"""
Verify what resources should be excluded from action datasets
"""
import json
import datetime

from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .models import PyroConfig, User, Group, Device, Exclude, ActionType
from .logging import STDOUTMsg
from .splitter import ListSplitter


class ExclusionChecker:
    """
    Handles exclusion logic for system resources.

    Determines whether specific resources should be excluded from processing
    based on configuration exclusions.
    """

    def __init__(self, config: dict | None = None, stdout: Optional[STDOUTMsg] = None, **kwargs):
        self.config = config or {}
        self.stdout = stdout or STDOUTMsg(
            debug_mode=kwargs.get('debug', self.config.get('debug', False)),
            timestamp=kwargs.get('log_timestamp', self.config.get('log_timestamp', False))
        )
        self.stdout.debug(f'ExclusionChecker conf: {self.config}')

    def should_exclude_user(self, username: str, excludes: List[str]) -> bool:
        """Check if a user should be excluded."""
        if excludes and username in excludes:
            self.stdout.warn(f'Excluding system user: {username}')
            return True
        return False

    def should_exclude_group(self, groupname: str, excludes: List[str]) -> bool:
        """Check if a group should be excluded."""
        if excludes and groupname in excludes:
            self.stdout.warn(f'Excluding system group: {groupname}')
            return True
        return False

    def should_exclude_device(self, device_path: str, excludes: List[str]) -> bool:
        """Check if a device should be excluded."""
        if excludes and device_path in excludes:
            self.stdout.warn(f'Excluding block storage device: {device_path}')
            return True
        return False

    def should_exclude_path(self, path: str, excludes: List[str]) -> bool:
        """Check if a filesystem path should be excluded."""
        if excludes and path in excludes:
            self.stdout.warn(f'Excluding path: {path}')
            return True
        return False

    def has_excluded_parent(self, path: Union[str, Path], excluded_paths: List[Union[str, Path]]) -> bool:
        """
        Check if a path has any excluded path as its parent directory.

        Args:
            path: The path to check
            excluded_paths: List of paths that should not be parents

        Returns:
            True if any excluded path is a parent of the given path
        """
        path_obj = Path(path).resolve()

        for excluded in excluded_paths:
            excluded_obj = Path(excluded).resolve()
            try:
                # If path starts with excluded path, excluded is a parent
                path_obj.relative_to(excluded_obj)
                self.stdout.debug(f'Excluding: {path}')
                return True
            except ValueError:
                # excluded is not a parent of path
                continue
        return False

