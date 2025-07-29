# eops/cli.py
import typer
from pathlib import Path
from .utils.config_loader import load_config_from_file
from .core.backtester import BacktestEngine
from .data.downloader import download_ohlcv_data, fix_ohlcv_data
from .utils.logger import log as framework_log
from . import __version__
import sys
sys.path.insert(0, str(Path.cwd()))

main_app = typer.Typer(help="Eops - A quantitative trading framework.")
data_app = typer.Typer(name="data", help="Tools for managing historical data.")
main_app.add_typer(data_app)

@main_app.command()
def run(
    config_file: Path = typer.Argument(..., help="Path to the Python configuration file.", exists=True),
    backtest: bool = typer.Option(False, "--backtest", "-b", help="Run in backtesting mode."),
    report_path: Path = typer.Option(None, "--report", "-r", help="Path to save the backtest report HTML file."),
):
    """
    Run a trading strategy from a configuration file.
    This CLI is intended for local development and debugging.
    """
    framework_log.info(f"🚀 Starting Eops runner via CLI...")
    framework_log.info(f"⚙️  Config file: {config_file}")

    try:
        config = load_config_from_file(config_file)
        
        if backtest:
            typer.secho("MODE: Backtesting", fg=typer.colors.YELLOW)
            engine = BacktestEngine(config, report_path=report_path)
            engine.run()
        else:
            typer.secho("MODE: Live Trading (Not fully implemented)", fg=typer.colors.GREEN)
            # This part will need a LiveEngine implementation
            # from .core.engine import LiveEngine
            # engine = LiveEngine(config)
            # engine.run()
            framework_log.warning("Live trading from CLI is not fully implemented yet.")
            
    except (FileNotFoundError, AttributeError, ImportError, ValueError) as e:
        framework_log.error(f"🔥 Error loading configuration: {e}")
        typer.secho(f"🔥 Error loading configuration: {e}", fg=typer.colors.RED, err=True)
    except Exception as e:
        framework_log.error(f"🔥 An unexpected application error occurred: {e}", exc_info=True)
        typer.secho(f"🔥 An unexpected application error occurred: {e}", fg=typer.colors.RED, err=True)


@data_app.command("download")
def download_data_command(
    exchange: str = typer.Option("binance", "--exchange", "-e", help="Exchange ID (e.g., 'binance', 'okx')."),
    symbol: str = typer.Option("BTC/USDT", "--symbol", "-s", help="Trading symbol (e.g., 'BTC/USDT')."),
    timeframe: str = typer.Option("1h", "--timeframe", "-t", help="Timeframe (e.g., '1m', '5m', '1h', '1d')."),
    since: str = typer.Option(..., "--since", help="Start date in YYYY-MM-DD format."),
    until: str = typer.Option(None, "--until", help="End date in YYYY-MM-DD format (optional)."),
    output: Path = typer.Option(None, "--output", "-o", help="Output file path (CSV). Defaults to './data/EXCHANGE_SYMBOL_TF.csv'.")
):
    """
    Download historical OHLCV data from an exchange.
    """
    if not output:
        safe_symbol = symbol.replace("/", "_")
        output = Path(f"./data/{exchange}_{safe_symbol}_{timeframe}.csv")

    typer.echo(f"📥 Starting data download...")
    typer.echo(f"   - Exchange: {exchange}")
    typer.echo(f"   - Symbol: {symbol}")
    typer.echo(f"   - Timeframe: {timeframe}")
    typer.echo(f"   - Since: {since}")
    if until:
        typer.echo(f"   - Until: {until}")
    typer.echo(f"   - Output file: {output}")

    download_ohlcv_data(
        exchange_id=exchange,
        symbol=symbol,
        timeframe=timeframe,
        since=since,
        output_path=output,
        until=until
    )

@data_app.command("fix")
def fix_data_command(
    file: Path = typer.Argument(..., help="Path to the CSV data file to fix.", exists=True, readable=True, writable=True)
):
    """
    Checks for missing data points in a CSV file and fetches them.
    The filename must be in 'exchange_symbol_timeframe.csv' format.
    Example: binance_BTC_USDT_1h.csv
    """
    typer.echo(f"🛠️  Attempting to fix data file: {file}")
    fix_ohlcv_data(file)

@main_app.command()
def info():
    """Displays information about eops."""
    typer.echo(f"Eops Quant Trading Library v{__version__}")

if __name__ == "__main__":
    main_app()