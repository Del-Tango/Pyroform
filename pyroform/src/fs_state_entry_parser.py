"""
File System State Entry details for storage block device mountpoints
"""

import json
import datetime

from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .models import PyroConfig, User, Group, Device, Exclude, ActionType
from .logging import STDOUTMsg
from .splitter import ListSplitter
from .validator import SystemValidator


class StateEntryParser:
    """Parses and validates state entries from device configuration."""

    def __init__(
        self, config: dict | None = None, stdout: STDOUTMsg | None = None, **kwargs
    ) -> None:
        self.config = config or {}
        self.stdout = stdout or STDOUTMsg(
            debug_mode=kwargs.get("debug", self.config.get("debug", False)),
            timestamp=kwargs.get("log_timestamp", self.config.get("debug", False)),
        )

    @staticmethod
    def parse_state_entry(state_entry: str) -> Optional[Dict[str, str]]:
        """
        Parse configuration state entries like 'dir,/path,owner,group,permissions'.

        Args:
            state_entry: State entry string to parse

        Returns:
            Parsed state dictionary or None if invalid
        """
        parts = state_entry.split(",")
        if len(parts) < 5:
            return None

        obj_type = parts[0].lower()
        path = parts[1]
        owner = parts[2]
        group = parts[3]
        permissions = parts[4]

        result = {
            "type": obj_type,
            "path": path,
            "owner": owner,
            "group": group,
            "permissions": permissions,
        }

        # Handle symlink target
        if obj_type in ("l", "ln", "link") and len(parts) >= 6:
            result["target"] = parts[5]

        return result

    @staticmethod
    def is_valid_state_entry(parsed_entry: Dict[str, str]) -> bool:
        """Validate parsed state entry."""
        required_fields = ["type", "path", "owner", "group", "permissions"]
        return all(field in parsed_entry for field in required_fields)

    @staticmethod
    def get_entry_type_category(obj_type: str) -> str:
        """Categorize state entry type."""
        type_mapping = {
            "d": "directory",
            "dir": "directory",
            "directory": "directory",
            "f": "file",
            "fl": "file",
            "file": "file",
            "l": "symlink",
            "ln": "symlink",
            "link": "symlink",
        }
        return type_mapping.get(obj_type, "unknown")
