# eops/worker.py
"""
The operational entrypoint for managing strategy instances within a Docker container.
This script is designed to be called by an external orchestrator via `docker exec`.
It manages strategy instances as separate OS processes and tracks their PIDs.
"""
import typer
import json
import os
import signal
import fcntl
from pathlib import Path
from multiprocessing import Process, current_process
from contextlib import contextmanager
from typing import Dict, Any

# --- Add project root to path to allow eops imports ---
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from eops.core.backtester import BacktestEngine
from eops.core.engine import LiveEngine
from eops.utils.config_loader import load_config_from_dict
from eops.utils.logger import setup_logger

# --- Constants ---
PID_DIR = Path("/tmp/eops_pids")
PID_FILE = PID_DIR / "pids.json"
app = typer.Typer(help="Eops Worker: Manages strategy instances as processes.")
log = setup_logger("worker")

# --- PID File Management with Locking ---

@contextmanager
def pid_file_lock():
    """A context manager to safely read/write the PID file."""
    PID_DIR.mkdir(exist_ok=True)
    try:
        with open(PID_FILE, 'a+') as f: # 'a+' creates if not exists, and allows reading
            fcntl.flock(f, fcntl.LOCK_EX)
            f.seek(0)
            yield f
            fcntl.flock(f, fcntl.LOCK_UN)
    except IOError as e:
        log.error(f"Could not access PID file {PID_FILE}: {e}")
        raise

def read_pids() -> Dict[str, int]:
    """Reads the PID file and returns a dictionary of instance_id -> pid."""
    with pid_file_lock() as f:
        content = f.read()
        if not content:
            return {}
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            log.warning("PID file is corrupted. Returning empty dictionary.")
            return {}

def write_pids(pids: Dict[str, int]):
    """Writes the given dictionary to the PID file."""
    with pid_file_lock() as f:
        f.seek(0)
        f.truncate()
        json.dump(pids, f, indent=4)

# --- Eops Instance Runner (The function that runs in a new process) ---

def run_eops_instance(instance_id: str, config_dict: Dict[str, Any], backtest_mode: bool):
    """
    This function is the target for the new process. It sets up and runs a single
    eops Engine instance.
    """
    # Give the process a descriptive name
    current_process().name = f"eops-inst-{instance_id}"
    
    # Each process gets its own logger
    instance_log = setup_logger(instance_id)
    
    try:
        instance_log.info(f"Process {os.getpid()} starting up for instance.")
        config = load_config_from_dict(config_dict)
        
        if backtest_mode:
            # Backtesting is not a typical use case for the worker, but supported for consistency.
            instance_log.info("Mode: Backtesting")
            engine = BacktestEngine(config)
        else:
            instance_log.info("Mode: Live Trading")
            # In a real scenario, we might need a more specific LiveEngine.
            engine = LiveEngine(config)
        
        # The engine's run method now blocks until a SIGTERM is received.
        engine.run()

    except Exception as e:
        instance_log.error(f"FATAL ERROR in instance process: {e}", exc_info=True)
    finally:
        instance_log.info(f"Process {os.getpid()} for instance is shutting down.")

# --- Typer CLI Commands ---

@app.command()
def start(
    instance_id: str = typer.Argument(..., help="A unique UUID for the strategy instance."),
    config_json: str = typer.Argument(..., help="A JSON string containing the strategy configuration."),
    backtest: bool = typer.Option(False, "--backtest", help="Run in backtesting mode (for testing)."),
):
    """
    Starts a new strategy instance as a background OS process.
    """
    log.info(f"Received 'start' command for instance: {instance_id}")
    pids = read_pids()
    if instance_id in pids:
        log.error(f"Instance '{instance_id}' is already running with PID {pids[instance_id]}. Aborting.")
        raise typer.Exit(code=1)

    try:
        config = json.loads(config_json)
    except json.JSONDecodeError as e:
        log.error(f"Invalid configuration JSON for instance '{instance_id}': {e}")
        raise typer.Exit(code=1)

    process = Process(
        target=run_eops_instance,
        args=(instance_id, config, backtest),
    )
    process.daemon = False # Let it be an independent process
    process.start()

    pids[instance_id] = process.pid
    write_pids(pids)
    
    log.info(f"✅ Successfully started instance '{instance_id}' with PID: {process.pid}")
    typer.echo(f"OK: Started instance {instance_id} with PID {process.pid}")

@app.command()
def stop(instance_id: str = typer.Argument(..., help="The unique ID of the instance to stop.")):
    """
    Stops a running strategy instance by sending it a SIGTERM signal.
    """
    log.info(f"Received 'stop' command for instance: {instance_id}")
    pids = read_pids()
    pid = pids.get(instance_id)

    if not pid:
        log.error(f"Instance '{instance_id}' not found in PID file. Cannot stop.")
        raise typer.Exit(code=1)

    try:
        os.kill(pid, signal.SIGTERM)
        log.info(f"Sent SIGTERM to process {pid} for instance '{instance_id}'.")
    except ProcessLookupError:
        log.warning(f"Process {pid} for instance '{instance_id}' was not found. It may have already exited.")
    except Exception as e:
        log.error(f"Failed to kill process {pid}: {e}")
        raise typer.Exit(code=1)

    # Clean up PID file
    pids.pop(instance_id, None)
    write_pids(pids)
    log.info(f"✅ Successfully stopped and removed instance '{instance_id}' from tracking.")
    typer.echo(f"OK: Stop signal sent to instance {instance_id}")

@app.command(name="status")
def get_status():
    """
    Checks the status of all managed instances by checking if their PIDs are active.
    """
    log.info("Received 'status' command.")
    pids = read_pids()
    if not pids:
        typer.echo("No instances are currently managed.")
        return
        
    typer.echo(f"{'INSTANCE ID':<40} {'PID':<10} {'STATUS':<10}")
    typer.echo("-" * 62)
    
    dead_instances = []
    for instance_id, pid in pids.items():
        try:
            os.kill(pid, 0) # Check if process exists without killing it
            status = typer.style("RUNNING", fg=typer.colors.GREEN)
        except OSError:
            status = typer.style("DEAD", fg=typer.colors.RED)
            dead_instances.append(instance_id)
            
        typer.echo(f"{instance_id:<40} {pid:<10} {status:<10}")

    # Clean up dead instances from the PID file
    if dead_instances:
        log.warning(f"Found dead instances: {dead_instances}. Cleaning up PID file.")
        for inst_id in dead_instances:
            pids.pop(inst_id, None)
        write_pids(pids)

if __name__ == "__main__":
    app()