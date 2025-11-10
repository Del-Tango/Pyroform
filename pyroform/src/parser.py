"""
Pyro Configuration Parser
"""

import json
import yaml
from pathlib import Path
from typing import List, Dict, Any
import glob

from .models import PyroConfig, User, Group, Device


class PyroParser:
    """
    Parser for Pyro configuration files (JSON and YAML)
    """

    def parse(self, input_path: Path) -> List[PyroConfig]:
        """
        Parse Pyro files from file or directory

        Args:
            input_path: Path to Pyro file or directory containing Pyro files

        Returns:
            List of PyroConfig objects

        Raises:
            FileNotFoundError: If input_path doesn't exist
            ValueError: If file format is invalid
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input path does not exist: {input_path}")

        if input_path.is_file():
            return [self._parse_single_file(input_path)]
        elif input_path.is_dir():
            return self._parse_directory(input_path)
        else:
            raise ValueError(f"Input path is neither file nor directory: {input_path}")

    def _parse_single_file(self, file_path: Path) -> PyroConfig:
        """
        Parse single JSON/YAML file

        Args:
            file_path: Path to Pyro file

        Returns:
            PyroConfig object

        Raises:
            ValueError: If file format is invalid or unsupported
        """
        if file_path.suffix.lower() in [".json"]:
            with open(file_path, "r") as f:
                data = json.load(f)
        elif file_path.suffix.lower() in [".yaml", ".yml"]:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        return self._parse_single_file_data(data)

    def _parse_single_file_data(self, data: Dict[str, Any]) -> PyroConfig:
        """
        Parse configuration data from a single file

        Args:
            data: Dictionary containing Pyro configuration

        Returns:
            PyroConfig object
        """
        # Extract basic configuration
        label = data.get("Label", "Unnamed Configuration")

        # Parse users
        users = []
        for user_data in data.get("Users", []):
            try:
                user = User(
                    label=user_data.get("label", ""),
                    name=user_data.get("Name", ""),
                    password=user_data.get("Password", ""),
                    groups=user_data.get("Groups", []),
                )
                users.append(user)
            except (KeyError, TypeError) as e:
                raise ValueError(f"Invalid user data: {user_data}") from e

        # Parse groups
        groups = []
        for group_data in data.get("Groups", []):
            try:
                group = Group(
                    label=group_data.get("label", ""),
                    name=group_data.get("Name", ""),
                    users=group_data.get("Users", []),
                )
                groups.append(group)
            except (KeyError, TypeError) as e:
                raise ValueError(f"Invalid group data: {group_data}") from e

        # Parse devices
        devices = []
        for device_data in data.get("Devices", []):
            try:
                device = Device(
                    label=device_data.get("label", ""),
                    path=device_data.get("Path", ""),
                    partition=device_data.get("Partition", 0),
                    mountpoint=device_data.get("Mountpoint", ""),
                    state=device_data.get("State", []),
                )
                devices.append(device)
            except (KeyError, TypeError) as e:
                raise ValueError(f"Invalid device data: {device_data}") from e

        return PyroConfig(label=label, users=users, groups=groups, devices=devices)

    def _parse_directory(self, directory_path: Path) -> List[PyroConfig]:
        """
        Parse all Pyro files in a directory

        Args:
            directory_path: Path to directory containing Pyro files

        Returns:
            List of PyroConfig objects
        """
        configs = []

        # Look for JSON files with pyro_ prefix
        json_patterns = [
            "pyro_*.json",
            "*.json",  # Also accept any JSON file for flexibility
        ]

        # Look for YAML files with pyro_ prefix
        yaml_patterns = [
            "pyro_*.yaml",
            "pyro_*.yml",
            "*.yaml",
            "*.yml",  # Also accept any YAML file for flexibility
        ]

        all_files = []

        # Collect all matching files
        for pattern in json_patterns + yaml_patterns:
            matches = glob.glob(str(directory_path / pattern))
            all_files.extend([Path(m) for m in matches])

        # Remove duplicates and sort for consistent ordering
        all_files = sorted(set(all_files))

        # Parse each file
        for file_path in all_files:
            if file_path.is_file():
                try:
                    config = self._parse_single_file(file_path)
                    configs.append(config)
                except (json.JSONDecodeError, yaml.YAMLError, ValueError) as e:
                    raise ValueError(f"Error parsing file {file_path}: {e}") from e

        return configs


# CODE DUMP

