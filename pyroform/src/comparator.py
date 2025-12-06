"""

"""
import json
import os
import pwd
import grp
import stat
import subprocess

import pysnooper

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Set, Optional, Tuple

from .models import (
    PyroConfig, User, Group, Device, Exclude, ValidationResult, FileSystemEntry,
    SystemUser, SystemGroup, MountedDevice, ValidationSummary
)
from .logging import STDOUTMsg


class SystemStateComparator:
    """
    Compares current system state with desired Pyro configuration.

    Identifies discrepancies between the live system state and the
    configuration defined in Pyro files.
    """

    def __init__(self, config: dict | None = None, stdout: STDOUTMsg | None = None, **kwargs):
        self.config = config or {}
        self.stdout = stdout or STDOUTMsg(
            debug_mode=kwargs.get('debug', self.config.get('debug', False)),
            timestamp=kwargs.get('log_timestamp', self.config.get('debug', False)),
        )

    # @pysnooper.snoop()
    def compare_states(
        self,
        system_state: Dict[str, Any],
        config: PyroConfig
    ) -> Dict[str, Any]:
        """
        Compare current system state with configuration.

        Args:
            system_state: Current system state from scanner
            config: Desired Pyro configuration

        Returns:
            Dictionary containing all identified discrepancies
        """
        self.stdout.info('Comparing current system state with Pyro file...')

        differences = self._initialize_differences_dict()

        if config.users:
            self._compare_users(config.users, system_state['users'], differences, config.excludes)

        if config.groups:
            self._compare_groups(config.groups, system_state['groups'], differences, config.excludes)

        if config.devices:
            current_fs_state = self._build_filesystem_state(system_state)
            self._compare_filesystem(config.devices, current_fs_state, differences, config.excludes)

        # Remove empty difference categories
        sanitized = {k: v for k, v in differences.items() if v}
        self.stdout.debug(f"Differences: {json.dumps(sanitized, indent=4)}")

        return sanitized

    def _initialize_differences_dict(self) -> Dict[str, List]:
        """Initialize the differences dictionary with all possible categories."""
        return {
            'missing_users': [], 'extra_users': [], 'user_mismatches': [],
            'missing_groups': [], 'extra_groups': [], 'group_mismatches': [],
            'missing_directories': [], 'extra_directories': [], 'directory_mismatches': [],
            'missing_files': [], 'extra_files': [], 'file_mismatches': [],
            'missing_symlinks': [], 'extra_symlinks': [], 'symlink_mismatches': [],
            'missing_mountpoints': [], 'mountpoint_mismatches': []
        }

    # @pysnooper.snoop()
    def _build_filesystem_state(self, system_state: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Build unified filesystem state from system state."""
        fs_state = {}

        for device in system_state['mounted_devices']:
            mountpoint = device['mountpoint']
            self._add_filesystem_entries(device['directories'], 'directory', mountpoint, fs_state)
            self._add_filesystem_entries(device['files'], 'file', mountpoint, fs_state)
            self._add_filesystem_entries(device['symlinks'], 'symlink', mountpoint, fs_state)

        return fs_state

    # @pysnooper.snoop()
    def _add_filesystem_entries(
        self,
        entries: List[Dict],
        entry_type: str,
        mountpoint: str,
        fs_state: Dict[str, Any]
    ) -> None:
        """Add filesystem entries to the unified state."""
        for entry in entries:
            fs_state[entry.path] = {
                'type': entry_type,
                'owner': entry.owner,
                'group': entry.group,
                'permissions': entry.permissions,
                'mountpoint': mountpoint
            }
            if entry_type == 'symlink':
                fs_state[entry.path]['target'] = entry.target or entry.broken

    def _compare_users(
        self,
        config_users: List[User],
        current_users: List[Dict],
        differences: Dict[str, Any],
        excludes: Optional[Exclude]
    ) -> None:
        """Compare configured users with current system users."""
        current_users_dict = {user['username']: user for user in current_users}
        config_user_names = set()

        for config_user in config_users:
            if self._should_exclude(config_user.name, excludes, 'users'):
                continue

            config_user_names.add(config_user.name)
            self._check_user_compliance(config_user, current_users_dict, differences)

        self._find_extra_users(config_user_names, current_users_dict, differences, excludes)

    # @pysnooper.snoop()
    def _check_user_compliance(
        self,
        config_user: User,
        current_users: Dict,
        differences: Dict[str, Any]
    ) -> None:
        """Check if a user complies with configuration."""
        username = config_user.name

        if username not in current_users:
            differences['missing_users'].append({
                'label': config_user.label,
                'username': username,
                'password': config_user.password,
                'groups': config_user.groups
            })
        else:
            self._check_user_properties(config_user, current_users[username], differences)

    # @pysnooper.snoop()
    def _check_user_properties(
        self,
        config_user: User,
        current_user: Dict,
        differences: Dict[str, Any]
    ) -> None:
        """Check user properties for mismatches."""
        mismatches = []
        expected_groups = set(config_user.groups)
        current_groups = set(current_user.get('groups', []))
        missing_groups = expected_groups - current_groups
        # Filter out users own default group
        extra_groups = [
            item for item in current_groups - expected_groups
            if item != config_user.name
        ]

        if missing_groups or extra_groups:
            mismatches.append({
                'property': 'groups',
                'expected': list(expected_groups),
                'actual': list(current_groups),
                'missing': list(missing_groups),
                'extra': list(extra_groups)
            })

        if mismatches:
            differences['user_mismatches'].append({
                'label': config_user.label,
                'username': config_user.name,
                'mismatches': mismatches
            })

    def _find_extra_users(
        self,
        config_user_names: Set[str],
        current_users: Dict,
        differences: Dict[str, Any],
        excludes: Optional[Exclude]
    ) -> None:
        """Find users present in system but not in configuration."""
        current_user_names = set(current_users.keys())
        extra_users = current_user_names - config_user_names

        for username in extra_users:
            if self._should_exclude(username, excludes, 'users'):
                continue

            user = current_users[username]
            differences['extra_users'].append({
                'username': username,
                'uid': user['uid'],
                'home_directory': user['home_directory']
            })

    def _compare_groups(
        self,
        config_groups: List[Group],
        current_groups: List[Dict],
        differences: Dict[str, Any],
        excludes: Optional[Exclude]
    ) -> None:
        """Compare configured groups with current system groups."""
        current_groups_dict = {group['groupname']: group for group in current_groups}
        config_group_names = set()

        for config_group in config_groups:
            if self._should_exclude(config_group.name, excludes, 'groups'):
                continue

            config_group_names.add(config_group.name)
            self._check_group_compliance(config_group, current_groups_dict, differences)

        self._find_extra_groups(config_group_names, current_groups_dict, differences, excludes)

    def _check_group_compliance(
        self,
        config_group: Group,
        current_groups: Dict,
        differences: Dict[str, Any]
    ) -> None:
        """Check if a group complies with configuration."""
        groupname = config_group.name

        if groupname not in current_groups:
            differences['missing_groups'].append({
                'label': config_group.label,
                'groupname': groupname,
                'members': config_group.users,
            })
        else:
            self._check_group_properties(config_group, current_groups[groupname], differences)

    def _check_group_properties(
        self,
        config_group: Group,
        current_group: Dict,
        differences: Dict[str, Any]
    ) -> None:
        """Check group properties for mismatches."""
        mismatches = []
        expected_members = set(config_group.users)
        current_members = set(current_group.get('members', []))

        missing_members = expected_members - current_members
        extra_members = current_members - expected_members

        if missing_members or extra_members:
            mismatches.append({
                'property': 'members',
                'expected': list(expected_members),
                'actual': list(current_members),
                'missing': list(missing_members),
                'extra': list(extra_members)
            })

        if mismatches:
            differences['group_mismatches'].append({
                'label': config_group.label,
                'groupname': config_group.name,
                'mismatches': mismatches
            })

    def _find_extra_groups(
        self,
        config_group_names: Set[str],
        current_groups: Dict,
        differences: Dict[str, Any],
        excludes: Optional[Exclude]
    ) -> None:
        """Find groups present in system but not in configuration."""
        current_group_names = set(current_groups.keys())
        extra_groups = current_group_names - config_group_names

        for groupname in extra_groups:
            if self._should_exclude(groupname, excludes, 'groups'):
                continue

            group = current_groups[groupname]
            differences['extra_groups'].append({
                'groupname': groupname,
                'gid': group['gid'],
                'members': group['members']
            })

    # @pysnooper.snoop()
    def _compare_filesystem(
        self,
        config_devices: List[Device],
        current_fs_state: Dict,
        differences: Dict[str, Any],
        excludes: Optional[Exclude]
    ) -> None:
        """Compare configured filesystem state with current state."""
        config_paths = set()

        for device in config_devices:
            if self._should_exclude(device.path, excludes, 'devices'):
                continue

            self._check_mountpoint(device, current_fs_state, differences)
            self._check_device_contents(device, current_fs_state, differences, config_paths, excludes)

        self._find_extra_filesystem_items(config_paths, current_fs_state, differences)

    # @pysnooper.snoop()
    def _check_mountpoint(
        self,
        device: Device,
        current_fs_state: Dict,
        differences: Dict[str, Any]
    ) -> None:
        """Check if mountpoint exists."""
        if not device.mountpoint:
            return

        mountpoint_exists = any(
            item.get('mountpoint') == device.mountpoint
            for item in current_fs_state.values()
        )

        if not mountpoint_exists:
            differences['missing_mountpoints'].append({
                'label': device.label,
                'mountpoint': device.mountpoint
            })

    # @pysnooper.snoop()
    def _check_device_contents(
        self,
        device: Device,
        current_fs_state: Dict,
        differences: Dict[str, Any],
        config_paths: Set[str],
        excludes: Optional[Exclude]
    ) -> None:
        """Check contents of a configured device."""
        for state_entry in device.state:
            config_item = self._parse_config_state_entry(state_entry)
            if not config_item:
                continue

            path = config_item['path']
            if self._should_exclude(path, excludes, config_item['type']):
                continue

            config_paths.add(path)
            self._check_filesystem_item_compliance(config_item, current_fs_state, differences)

    # @pysnooper.snoop()
    def _check_filesystem_item_compliance(
        self,
        config_item: Dict[str, Any],
        current_fs_state: Dict,
        differences: Dict[str, Any]
    ) -> None:
        """Check if a filesystem item complies with configuration."""
        path = config_item['path']

        if path not in current_fs_state:
            self._handle_missing_item(config_item, differences)
        else:
            self._check_item_properties(config_item, current_fs_state[path], differences)

    def _handle_missing_item(self, config_item: Dict[str, Any], differences: Dict[str, Any]) -> None:
        """Handle missing filesystem items."""
        item_type = config_item['type']
        if item_type == 'dir':
            differences['missing_directories'].append(config_item)
        elif item_type == 'fl':
            differences['missing_files'].append(config_item)
        elif item_type == 'ln':
            differences['missing_symlinks'].append(config_item)

    def _check_item_properties(
        self,
        config_item: Dict[str, Any],
        current_item: Dict[str, Any],
        differences: Dict[str, Any]
    ) -> None:
        """Check filesystem item properties for mismatches."""
        mismatches = self._find_property_mismatches(config_item, current_item)

        if mismatches:
            mismatch_entry = {
                'path': config_item['path'],
                'mismatches': mismatches,
                'expected': config_item,
                'actual': current_item
            }

            self._categorize_mismatch(config_item['type'], mismatch_entry, differences)

    def _find_property_mismatches(
        self,
        config_item: Dict[str, Any],
        current_item: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find all property mismatches between configured and current state."""
        mismatches = []
        type_map = {'dir': 'directory', 'fl': 'file', 'ln': 'symlink'}
        expected_type = type_map.get(config_item['type'])

        # Check type
        if current_item['type'] != expected_type:
            mismatches.append({
                'property': 'type',
                'expected': expected_type,
                'actual': current_item['type']
            })

        # Check owner, group, permissions
        for property_name in ['owner', 'group', 'permissions']:
            if config_item[property_name] != current_item[property_name]:
                mismatches.append({
                    'property': property_name,
                    'expected': config_item[property_name],
                    'actual': current_item[property_name]
                })

        # Check symlink target
        if (config_item['type'] == 'ln' and current_item['type'] == 'symlink' and
            'target' in config_item and config_item['target'] != current_item.get('target')):
            mismatches.append({
                'property': 'target',
                'expected': config_item['target'],
                'actual': current_item.get('target', 'missing')
            })

        return mismatches

    def _categorize_mismatch(
        self,
        item_type: str,
        mismatch_entry: Dict[str, Any],
        differences: Dict[str, Any]
    ) -> None:
        """Categorize mismatch by item type."""
        if item_type == 'dir':
            differences['directory_mismatches'].append(mismatch_entry)
        elif item_type == 'fl':
            differences['file_mismatches'].append(mismatch_entry)
        elif item_type == 'ln':
            differences['symlink_mismatches'].append(mismatch_entry)

    def _find_extra_filesystem_items(
        self,
        config_paths: Set[str],
        current_fs_state: Dict,
        differences: Dict[str, Any]
    ) -> None:
        """Find filesystem items present in system but not in configuration."""
        current_paths = set(current_fs_state.keys())
        extra_paths = current_paths - config_paths

        for path in extra_paths:
            item = current_fs_state[path]
            extra_entry = {
                'path': path,
                'owner': item['owner'],
                'group': item['group'],
                'permissions': item['permissions']
            }

            if item['type'] == 'symlink':
                extra_entry['target'] = item.get('target', 'broken')

            if item['type'] == 'directory':
                differences['extra_directories'].append(extra_entry)
            elif item['type'] == 'file':
                differences['extra_files'].append(extra_entry)
            elif item['type'] == 'symlink':
                differences['extra_symlinks'].append(extra_entry)

    def _parse_config_state_entry(self, entry: str) -> Optional[Dict[str, Any]]:
        """Parse configuration state entries like 'dir,/path,owner,group,permissions'."""
        parts = entry.split(',')
        if len(parts) < 5:
            return None

        entry_type = parts[0]
        result = {
            'type': entry_type,
            'path': parts[1],
            'owner': parts[2],
            'group': parts[3],
            'permissions': parts[4]
        }

        if entry_type == 'ln' and len(parts) >= 6:
            result['target'] = parts[5]

        return result

    def _should_exclude(
        self,
        item: str,
        excludes: Optional[Exclude],
        exclude_type: str
    ) -> bool:
        """Check if an item should be excluded from comparison."""
        if not excludes:
            return False

        exclude_mapping = {
            'users': excludes.users,
            'groups': excludes.groups,
            'devices': excludes.devices,
            'dir': excludes.directories,
            'fl': excludes.files,
            'ln': excludes.links
        }

        exclude_set = exclude_mapping.get(exclude_type, set())
        return item in exclude_set


