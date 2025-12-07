"""
Configuration management for Pyroform
"""

import json
import yaml

# import pysnooper

from pathlib import Path
from typing import Dict, Any, Optional


class PyroformConfig:
    """
    Configuration manager for Pyroform
    """

    def __init__(self, config_file: Path = None):
        """
        Initialize Pyroform configuration

        Args:
            config_file: Optional path to configuration file
        """
        self.settings = self._load_config(config_file)

    # @pysnooper.snoop()
    def _load_config(self, config_file: Optional[Path]) -> Dict[str, Any]:
        """
        Load configuration from file with defaults

        Args:
            config_file: Optional path to configuration file

        Returns:
            Configuration dictionary with defaults
        """
        # Default configuration
        default_config = {
            "log_level": "INFO",
            "log_timestamp": False,
            "auto_confirm": False,
            "dry_run": False,
            "debug": False,
        }

        # If no config file provided, return defaults
        if not config_file:
            return default_config

        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        try:
            # Load configuration from file based on extension
            if config_path.suffix.lower() in [".yaml", ".yml"]:
                with open(config_path, "r") as f:
                    file_config = yaml.safe_load(f) or {}
            elif config_path.suffix.lower() == ".json":
                with open(config_path, "r") as f:
                    file_config = json.load(f) or {}
            else:
                raise ValueError(
                    f"Unsupported configuration file format: {config_path.suffix}"
                )

            # Deep merge file configuration with defaults
            merged_config = self._deep_merge(default_config, file_config)
            return merged_config

        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Error parsing configuration file {config_file}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading configuration file {config_file}: {e}")

    def _deep_merge(
        self, base: Dict[str, Any], update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deep merge two dictionaries

        Args:
            base: Base dictionary
            update: Dictionary with updates

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in update.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                # Recursively merge dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Overwrite or add new value
                result[key] = value

        return result

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key

        Args:
            key: Configuration key (can be dot-separated for nested keys)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self.settings

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value

        Args:
            key: Configuration key (can be dot-separated for nested keys)
            value: Value to set
        """
        keys = key.split(".")
        config = self.settings

        # Navigate to the parent of the final key
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        # Set the final value
        config[keys[-1]] = value

    def save(self, config_file: Path) -> bool:
        """
        Save configuration to file

        Args:
            config_file: Path to save configuration

        Returns:
            True if successful, False otherwise
        """
        try:
            config_path = Path(config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            if config_path.suffix.lower() in [".yaml", ".yml"]:
                with open(config_path, "w") as f:
                    yaml.dump(self.settings, f, default_flow_style=False)
            elif config_path.suffix.lower() == ".json":
                with open(config_path, "w") as f:
                    json.dump(self.settings, f, indent=2)
            else:
                raise ValueError(
                    f"Unsupported configuration file format: {config_path.suffix}"
                )

            return True

        except Exception as e:
            print(f"Error saving configuration to {config_file}: {e}")
            return False


# CODE DUMP
