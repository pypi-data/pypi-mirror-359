# eops/utils/config_loader.py
import importlib.util
from pathlib import Path
from typing import Dict, Any

def load_config_from_dict(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and prepares a configuration dictionary.
    """
    try:
        # STRATEGY_CLASS is the only required key in all modes
        strategy_class = config_dict["STRATEGY_CLASS"]

        config = {
            "exchange_class": config_dict.get("EXCHANGE_CLASS"),
            "exchange_params": config_dict.get("EXCHANGE_PARAMS", {}),
            "strategy_class": strategy_class,  # Required
            "strategy_params": config_dict.get("STRATEGY_PARAMS", {}),
            "engine_params": config_dict.get("ENGINE_PARAMS", {}),
            "backtest_data_path": config_dict.get("BACKTEST_DATA_PATH"),
        }
        return config
    except KeyError:
        raise AttributeError("Missing required configuration key 'STRATEGY_CLASS' in the provided config.")

def load_config_from_file(config_path: Path) -> Dict[str, Any]:
    """
    Dynamically loads a Python configuration file as a module and converts it to a dictionary.
    """
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    spec = importlib.util.spec_from_file_location(name="eops_config", location=str(config_path))
    if spec is None:
        raise ImportError(f"Could not load spec for module at {config_path}")
    
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    # Convert module attributes to a dictionary
    config_dict = {
        key: getattr(config_module, key)
        for key in dir(config_module)
        if not key.startswith("__")
    }
    
    # Use the new dictionary-based loader for validation and preparation
    return load_config_from_dict(config_dict)