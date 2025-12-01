"""
FlowCTRL Sketch Generator for Pyroform

Generates executable FlowCTRL sketch files from Pyro configuration objects.
Supports multiple action types including configuration, mounting, cleanup, and snapshot generation.

Author: Pyroform Team
Version: 1.0.0
"""

import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .models import PyroConfig, User, Group, Device, Exclude, ActionType
from .logging import STDOUTMsg
from .splitter import ListSplitter
from .validator import SystemValidator


class CommandGenerator:
    """
    Generates individual FlowCTRL commands for different system operations.

    Separates command generation logic from sketch assembly for better testability.
    """

    def __init__(self, dry_run: bool = False, stdout: Optional[STDOUTMsg] = None):
        self.dry_run = dry_run
        self.cmd_prefix = '' if not dry_run else '# '
        self.stdout = stdout or STDOUTMsg(debug_mode=False, timestamp=False)

    def generate_user_command(self, user: User) -> Dict[str, Any]:
        """Generate user creation command."""
        group_membership = [str(grp) for grp in user.groups]
        csv_groups = ','.join(group_membership)
        groups = " ".join(group_membership)

        return {
            "name": f"Creating System User {user.name}",
            "cmd": f"{self.cmd_prefix}for group in {groups}; do groupadd -f $group; done && "
                   f"useradd -m -p '{user.password}' -G '{csv_groups}' '{user.name}' || exit 0",
            "setup-cmd": f"id {user.name} && echo 'User {user.name} already exists' || exit 0",
            "teardown-cmd": "",
            "on-ok-cmd": f"echo 'User {user.name} exists or created successfully'",
            "on-nok-cmd": f"echo 'Failed to create user {user.name}'",
            "fatal-nok": False,
        }

    def generate_group_command(self, group: Group) -> Dict[str, Any]:
        """Generate group creation command."""
        member_users = [str(usr) for usr in group.users]
        users = " ".join(member_users)

        return {
            "name": f"Creating System Group {group.name}",
            "cmd": f"{self.cmd_prefix}groupadd -f '{group.name}' && "
                   f"for user in {users}; do id $user || useradd -m $user; "
                   f"usermod -a -G '{group.name}' $user; done",
            "setup-cmd": f"getent group {group.name} && echo 'Group {group.name} already exists' || exit 0",
            "teardown-cmd": "",
            "on-ok-cmd": f"echo 'Group {group.name} exists'",
            "on-nok-cmd": f"echo 'Failed to create group {group.name}'",
            "fatal-nok": False,
        }

    def generate_mountpoint_command(self, device: Device) -> Dict[str, Any]:
        """Generate mountpoint directory creation command."""
        return {
            "name": f"Creating System Mountpoint Directory {device.mountpoint}",
            "cmd": f"{self.cmd_prefix}mkdir -p '{device.mountpoint}'",
            "setup-cmd": f"test -d {device.mountpoint}",
            "teardown-cmd": "",
            "on-ok-cmd": f"echo 'Mountpoint {device.mountpoint} exists'",
            "on-nok-cmd": f"echo 'Creating mountpoint {device.mountpoint}'",
            "fatal-nok": True,
        }

    def generate_mount_command(self, device: Device) -> Dict[str, Any]:
        """Generate device mounting command."""
        partition_suffix = device.partition if device.partition else ""

        return {
            "name": f"Mounting Block Device {device.label}",
            "cmd": f"{self.cmd_prefix}mount '{device.path}{partition_suffix}' '{device.mountpoint}'",
            "setup-cmd": f"mount | grep -q '{device.path} on {device.mountpoint}'",
            "teardown-cmd": f"umount {device.mountpoint}",
            "on-ok-cmd": f"echo 'Device {device.path} already mounted to {device.mountpoint}'",
            "on-nok-cmd": f"echo 'Mounting {device.path} to {device.mountpoint}'",
            "fatal-nok": True,
        }

    def generate_directory_command(self, path: str) -> Dict[str, Any]:
        """Generate directory creation command."""
        return {
            "name": f"Creating Directory {path}",
            "cmd": f"{self.cmd_prefix}mkdir -p {path}",
            "setup-cmd": f"test -d {path}",
            "teardown-cmd": "",
            "on-ok-cmd": f"echo 'Directory {path} exists'",
            "on-nok-cmd": f"echo 'Creating directory {path}'",
            "fatal-nok": True,
        }

    def generate_file_command(self, path: str) -> Dict[str, Any]:
        """Generate file creation command."""
        return {
            "name": f"Creating Regular File {path}",
            "cmd": f"{self.cmd_prefix}touch {path}",
            "setup-cmd": f"test -f {path}",
            "teardown-cmd": "",
            "on-ok-cmd": f"echo 'File {path} exists'",
            "on-nok-cmd": f"echo 'Creating file {path}'",
            "fatal-nok": True,
        }

    def generate_symlink_command(self, path: str, target: str) -> Dict[str, Any]:
        """Generate symbolic link creation command."""
        return {
            "name": f"Creating Symbolic Link {path}",
            "cmd": f"{self.cmd_prefix}ln -s {target} {path}",
            "setup-cmd": f"test -L {path}",
            "teardown-cmd": "",
            "on-ok-cmd": f"echo 'File {path} exists'",
            "on-nok-cmd": f"echo 'Creating file {path}'",
            "fatal-nok": True,
        }

    def generate_permission_command(self, path: str, owner: str, group: str, permissions: str) -> Dict[str, Any]:
        """Generate permission setting command."""
        return {
            "name": f"Setting Permissions For {path}",
            "cmd": f"{self.cmd_prefix}chown {owner}:{group} {path} && chmod {permissions} {path}",
            "setup-cmd": f"stat -c '%U:%G %a' {path} | grep -q '{owner}:{group} {permissions}'",
            "teardown-cmd": "",
            "on-ok-cmd": f"echo 'Permissions for {path} are correct'",
            "on-nok-cmd": f"echo 'Setting permissions for {path}'",
            "fatal-nok": True,
        }

    def generate_cleanup_user_command(self, usernames: str) -> Dict[str, Any]:
        """Generate user cleanup command."""
        return {
            "name": "Cleanup extra users",
            "cmd": f"{self.cmd_prefix}for user in {usernames}; do userdel -f -r $user; done",
            "setup-cmd": "",
            "on-ok-cmd": f"echo 'Eliminated: {usernames}'",
            "on-nok-cmd": f"echo 'Could not scorch extra system users! Details: {usernames}'",
            "fatal-nok": False,
        }

    def generate_cleanup_group_command(self, groups: str) -> Dict[str, Any]:
        """Generate group cleanup command."""
        return {
            "name": "Cleanup extra groups",
            "cmd": f"{self.cmd_prefix}for group in {groups}; do groupdel $group; done",
            "setup-cmd": "",
            "on-ok-cmd": f"echo 'Eliminated: {groups}'",
            "on-nok-cmd": f"echo 'Could not scorch extra system groups! Details: {groups}'",
            "fatal-nok": False,
        }

    def generate_cleanup_directories_command(self, directories: str) -> Dict[str, Any]:
        """Generate directory cleanup command."""
        return {
            "name": "Cleanup extra directories",
            "cmd": f"{self.cmd_prefix}rm -rf {directories}",
            "setup-cmd": "",
            "on-ok-cmd": f"echo 'Eliminated: {directories}'",
            "on-nok-cmd": f"echo 'Could not scorch extra directories! Details: {directories}'",
            "fatal-nok": False,
        }

    def generate_cleanup_files_command(self, files: str) -> Dict[str, Any]:
        """Generate file cleanup command."""
        return {
            "name": "Cleanup extra files and links",
            "cmd": f"{self.cmd_prefix}rm -f {files}",
            "setup-cmd": "",
            "on-ok-cmd": f"echo 'Eliminated: {files}'",
            "on-nok-cmd": f"echo 'Could not scorch extra files and links! Details: {files}'",
            "fatal-nok": False,
        }


class ExclusionChecker:
    """
    Handles exclusion logic for system resources.

    Determines whether specific resources should be excluded from processing
    based on configuration exclusions.
    """

    def __init__(self, stdout: Optional[STDOUTMsg] = None):
        self.stdout = stdout or STDOUTMsg(debug_mode=False, timestamp=False)

    def should_exclude_user(self, username: str, excludes: List[str]) -> bool:
        """Check if a user should be excluded."""
        if excludes and username in excludes:
            self.stdout.info(f'Excluding system user: {username}')
            return True
        return False

    def should_exclude_group(self, groupname: str, excludes: List[str]) -> bool:
        """Check if a group should be excluded."""
        if excludes and groupname in excludes:
            self.stdout.info(f'Excluding system group: {groupname}')
            return True
        return False

    def should_exclude_device(self, device_path: str, excludes: List[str]) -> bool:
        """Check if a device should be excluded."""
        if excludes and device_path in excludes:
            self.stdout.info(f'Excluding block storage device: {device_path}')
            return True
        return False

    def should_exclude_path(self, path: str, excludes: List[str]) -> bool:
        """Check if a filesystem path should be excluded."""
        if excludes and path in excludes:
            self.stdout.info(f'Excluding path: {path}')
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


class StateEntryParser:
    """Parses and validates state entries from device configuration."""

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
            'type': obj_type,
            'path': path,
            'owner': owner,
            'group': group,
            'permissions': permissions
        }

        # Handle symlink target
        if obj_type in ('l', 'ln', 'link') and len(parts) >= 6:
            result['target'] = parts[5]

        return result

    @staticmethod
    def is_valid_state_entry(parsed_entry: Dict[str, str]) -> bool:
        """Validate parsed state entry."""
        required_fields = ['type', 'path', 'owner', 'group', 'permissions']
        return all(field in parsed_entry for field in required_fields)

    @staticmethod
    def get_entry_type_category(obj_type: str) -> str:
        """Categorize state entry type."""
        type_mapping = {
            'd': 'directory', 'dir': 'directory', 'directory': 'directory',
            'f': 'file', 'fl': 'file', 'file': 'file',
            'l': 'symlink', 'ln': 'symlink', 'link': 'symlink'
        }
        return type_mapping.get(obj_type, 'unknown')


class SketchGenerator:
    """
    Generates FlowCTRL sketch files from PyroConfig objects.

    Coordinates the generation of executable sketches for different system
    operations including configuration, mounting, cleanup, and snapshots.
    """

    def __init__(
        self,
        stdout: Optional[STDOUTMsg] = None,
        dry_run: bool = False,
        config: Optional[dict] = None,
        chunk_size: int = 500
    ):
        """
        Initialize SketchGenerator.

        Args:
            stdout: STDOUTMsg instance for logging
            dry_run: Whether to generate dry-run commands
            config: Configuration dictionary
            chunk_size: Size for splitting large command lists
        """
        self.dry_run = dry_run
        self.chunk_size = chunk_size
        self.stdout = stdout or STDOUTMsg(debug_mode=False, timestamp=False)

        # Initialize components
        self.command_generator = CommandGenerator(dry_run=dry_run, stdout=stdout)
        self.exclusion_checker = ExclusionChecker(stdout=stdout)
        self.state_parser = StateEntryParser()
        self.list_splitter = ListSplitter(chunk_size=chunk_size)
        self.validator = SystemValidator(stdout=stdout, config=config)

    def generate_sketch(self, config: PyroConfig, action: ActionType) -> Dict[str, Any]:
        """
        Generate FlowCTRL sketch based on action type.

        Args:
            config: PyroConfig object containing system configuration
            action: Type of action to generate sketch for

        Returns:
            FlowCTRL sketch dictionary ready for execution

        Raises:
            ValueError: For unsupported action types
        """
        action_handlers = {
            ActionType.CONFIGURE: self.generate_configure_sketch,
            ActionType.MOUNT: self.generate_mount_sketch,
            ActionType.SCORCH: self.generate_scorch_sketch,
            ActionType.SNAPSHOT: self.generate_snapshot_pyro_config,
        }

        if action == ActionType.VALIDATE:
            raise ValueError("Validate action does not generate sketches")

        if action not in action_handlers:
            raise ValueError(f"Unsupported action type: {action}")

        return action_handlers[action](config)

    def generate_snapshot_pyro_config(self, config: PyroConfig) -> Dict[str, Any]:
        """
        Generate snapshot configuration from current system state.

        Args:
            config: PyroConfig object for exclusion filtering

        Returns:
            Snapshot configuration dictionary
        """
        system_state = self.validator.get_system_state(
            pyro_config=config, max_depth=100, include_hidden=True
        )

        timestamp = datetime.datetime.now()
        snapshot = {
            'Label': f'Pyroform Snapshot {timestamp}',
            'Users': self._build_user_snapshot(system_state),
            'Groups': self._build_group_snapshot(system_state),
            'Devices': self._build_device_snapshot(system_state),
        }

        return snapshot

    def _build_user_snapshot(self, system_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build user snapshot from system state."""
        users_snapshot = []

        for user in system_state.get('users', []):
            user_record = {
                'label': 'Snapshot of ' + user.get('username', ''),
                'Name': user.get('username', ''),
                'Password': '',  # Passwords are not stored in snapshots
                'Groups': user.get('groups', []),
            }
            users_snapshot.append(user_record)

        return users_snapshot

    def _build_group_snapshot(self, system_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build group snapshot from system state."""
        groups_snapshot = []

        for group in system_state.get('groups', []):
            group_record = {
                'label': 'Snapshot of ' + group.get('groupname', ''),
                'Name': group.get('groupname', ''),
                'Users': group.get('members', []),
            }
            groups_snapshot.append(group_record)

        return groups_snapshot

    def _build_device_snapshot(self, system_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build device snapshot from system state."""
        devices_snapshot = []

        for device in system_state.get('mounted_devices', []):
            device_record = {
                'label': 'Snapshot of ' + device.get('device_path', ''),
                'Path': device.get('device_path', ''),
                'Partition': device.get('partition', ''),
                'Mountpoint': device.get('mountpoint', ''),
                'State': self._build_device_state_snapshot(device)
            }
            devices_snapshot.append(device_record)

        return devices_snapshot

    def _build_device_state_snapshot(self, device: Dict[str, Any]) -> List[str]:
        """Build device state snapshot entries."""
        state_entries = []

        # Add directories
        for directory in device.get('directories', []):
            dir_record = ','.join([
                'dir', directory['path'], directory['owner'],
                directory['group'], directory['permissions']
            ])
            state_entries.append(dir_record)

        # Add files
        for file in device.get('files', []):
            file_record = ','.join([
                'fl', file['path'], file['owner'],
                file['group'], file['permissions']
            ])
            state_entries.append(file_record)

        # Add symlinks
        for link in device.get('symlinks', []):
            link_record = ','.join([
                'ln', link['path'], link['owner'], link['group'],
                link['permissions'], link.get('target', '')
            ])
            state_entries.append(link_record)

        return state_entries

    def generate_scorch_sketch(self, config: PyroConfig) -> Dict[str, Any]:
        """
        Generate sketch for scorch action (cleanup).

        Removes system resources that are not defined in the configuration.

        Args:
            config: PyroConfig object

        Returns:
            FlowCTRL sketch dictionary for cleanup operations
        """
        system_state = self.validator.get_system_state(
            pyro_config=config, max_depth=100, include_hidden=True
        )
        compared = self.validator.compare_system_state_with_pyro_file(system_state, config)

        sketch = {
            "name": f"Pyroform Auto-Generated Sketch {config.label}",
            "Cleanup": self._generate_cleanup_commands(config, compared),
        }

        # Remove empty sections
        return {k: v for k, v in sketch.items() if v}

    def _generate_cleanup_commands(self, config: PyroConfig, compared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate cleanup commands for scorch action.

        Args:
            config: PyroConfig object
            compared: Comparison results from validator

        Returns:
            List of cleanup commands
        """
        commands = []

        # Clean up extra users
        user_commands = self._generate_user_cleanup_commands(config, compared)
        commands.extend(user_commands)

        # Clean up extra groups
        group_commands = self._generate_group_cleanup_commands(config, compared)
        commands.extend(group_commands)

        # Clean up extra filesystem items
        fs_commands = self._generate_filesystem_cleanup_commands(config, compared)
        commands.extend(fs_commands)

        return commands

    def _generate_user_cleanup_commands(self, config: PyroConfig, compared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate user cleanup commands."""
        extra_usernames = [
            user['username'] for user in compared.get('extra_users', [])
            if user.get('username')
            and not self.exclusion_checker.should_exclude_user(user['username'], config.excludes.users)
        ]

        if not extra_usernames:
            return []

        username_chunks = self.list_splitter.split(extra_usernames) if len(extra_usernames) > self.chunk_size else [extra_usernames]
        commands = []

        for chunk in username_chunks:
            usernames_str = " ".join(chunk)
            if usernames_str.strip():
                command = self.command_generator.generate_cleanup_user_command(usernames_str)
                commands.append(command)

        return commands

    def _generate_group_cleanup_commands(self, config: PyroConfig, compared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate group cleanup commands."""
        extra_groups = [
            group['groupname'] for group in compared.get('extra_groups', [])
            if group.get('groupname')
            and not self.exclusion_checker.should_exclude_group(group['groupname'], config.excludes.groups)
        ]

        if not extra_groups:
            return []

        group_chunks = self.list_splitter.split(extra_groups) if len(extra_groups) > self.chunk_size else [extra_groups]
        commands = []

        for chunk in group_chunks:
            groups_str = " ".join(chunk)
            if groups_str.strip():
                command = self.command_generator.generate_cleanup_group_command(groups_str)
                commands.append(command)

        return commands

    def _generate_filesystem_cleanup_commands(self, config: PyroConfig, compared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate filesystem cleanup commands."""
        commands = []

        # Clean up extra directories
        dir_commands = self._generate_directory_cleanup_commands(config, compared)
        commands.extend(dir_commands)

        # Clean up extra files and symlinks
        file_commands = self._generate_file_cleanup_commands(config, compared)
        commands.extend(file_commands)

        return commands

    def _generate_directory_cleanup_commands(self, config: PyroConfig, compared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate directory cleanup commands."""
        extra_directories = [
            directory['path'] for directory in compared.get('extra_directories', [])
            if directory.get('path')
            and not self.exclusion_checker.should_exclude_path(directory['path'], config.excludes.directories)
            and not self.exclusion_checker.has_excluded_parent(directory['path'], config.excludes.directories)
        ]

        if not extra_directories:
            return []

        dir_chunks = self.list_splitter.split(extra_directories) if len(extra_directories) > self.chunk_size else [extra_directories]
        commands = []

        for chunk in dir_chunks:
            directories_str = " ".join(chunk)
            if directories_str.strip():
                command = self.command_generator.generate_cleanup_directories_command(directories_str)
                commands.append(command)

        return commands

    def _generate_file_cleanup_commands(self, config: PyroConfig, compared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate file and symlink cleanup commands."""
        extra_files_and_links = [
            file['path'] for file in compared.get('extra_files', [])
            if file.get('path')
            and not self.exclusion_checker.should_exclude_path(file['path'], config.excludes.files)
            and not self.exclusion_checker.has_excluded_parent(file['path'], config.excludes.directories)
        ] + [
            link['path'] for link in compared.get('extra_symlinks', [])
            if link.get('path')
            and not self.exclusion_checker.should_exclude_path(link['path'], config.excludes.links)
            and not self.exclusion_checker.has_excluded_parent(link['path'], config.excludes.directories)
        ]

        if not extra_files_and_links:
            return []

        file_chunks = self.list_splitter.split(extra_files_and_links) if len(extra_files_and_links) > self.chunk_size else [extra_files_and_links]
        commands = []

        for chunk in file_chunks:
            files_str = " ".join(chunk)
            if files_str.strip():
                command = self.command_generator.generate_cleanup_files_command(files_str)
                commands.append(command)

        return commands

    def generate_configure_sketch(self, config: PyroConfig) -> Dict[str, Any]:
        """
        Generate sketch for configure action (users, groups, file permissions).

        Args:
            config: PyroConfig object

        Returns:
            FlowCTRL sketch dictionary for configuration operations
        """
        sketch = {
            "name": f"Pyroform Auto-Generated Sketch {config.label}",
            "Users": self._generate_user_commands(config.users, config.excludes.users),
            "Groups": self._generate_group_commands(config.groups, config.excludes.groups),
            "Devices": self._generate_device_commands(config.devices, config.excludes),
        }

        # Remove empty sections
        sketch = {k: v for k, v in sketch.items() if v}
        self.stdout.info(f'FlowCTRL Sketch: {json.dumps(sketch, indent=4)}')
        return sketch

    def generate_mount_sketch(self, config: PyroConfig) -> Dict[str, Any]:
        """
        Generate sketch for mount action (device mounting only).

        Args:
            config: PyroConfig object

        Returns:
            FlowCTRL sketch dictionary for mounting operations
        """
        sketch = {
            "name": f"Pyroform Auto-Generated Sketch {config.label}",
            "Devices": self._generate_mount_commands(config.devices, config.excludes.devices),
        }

        return {k: v for k, v in sketch.items() if v}

    def _generate_user_commands(self, users: List[User], excludes: List[str]) -> List[Dict[str, Any]]:
        """Generate user management commands."""
        commands = []

        for user in users:
            if self.exclusion_checker.should_exclude_user(user.name, excludes):
                continue

            command = self.command_generator.generate_user_command(user)
            commands.append(command)

        return commands

    def _generate_group_commands(self, groups: List[Group], excludes: List[str]) -> List[Dict[str, Any]]:
        """Generate group management commands."""
        commands = []

        for group in groups:
            if self.exclusion_checker.should_exclude_group(group.name, excludes):
                continue

            command = self.command_generator.generate_group_command(group)
            commands.append(command)

        return commands

    def _generate_mount_commands(self, devices: List[Device], excludes: List[str]) -> List[Dict[str, Any]]:
        """
        Generate device mounting commands only.

        For mount action, we only handle the actual device mounting,
        not the directory structure creation.
        """
        commands = []

        for device in devices:
            if self.exclusion_checker.should_exclude_device(device.path, excludes):
                continue

            # Create mountpoint directory
            if device.mountpoint:
                mountpoint_cmd = self.command_generator.generate_mountpoint_command(device)
                commands.append(mountpoint_cmd)

            # Mount device
            if device.path and device.mountpoint:
                mount_cmd = self.command_generator.generate_mount_command(device)
                commands.append(mount_cmd)

        return commands

    def _generate_device_commands(self, devices: List[Device], excludes: Exclude) -> List[Dict[str, Any]]:
        """
        Generate complete device commands including directory structure.

        Used for configure action to set up full filesystem hierarchy.
        """
        commands = []

        for device in devices:
            if self.exclusion_checker.should_exclude_device(device.path, excludes.devices):
                continue

            # Generate mount-related commands
            mount_commands = self._generate_mount_commands([device], excludes.devices)
            commands.extend(mount_commands)

            # Generate filesystem structure commands
            if device.state:
                structure_commands = self._generate_filesystem_structure_commands(device, excludes)
                commands.extend(structure_commands)

        return commands

    def _generate_filesystem_structure_commands(self, device: Device, excludes: Exclude) -> List[Dict[str, Any]]:
        """Generate filesystem structure creation commands."""
        commands = []

        for state_entry in device.state:
            parsed_entry = self.state_parser.parse_state_entry(state_entry)
            if not parsed_entry or not self.state_parser.is_valid_state_entry(parsed_entry):
                self.stdout.err(f'Invalid file state entry for device {device.label}! Details: {state_entry}')
                continue

            path = parsed_entry['path']
            obj_type = parsed_entry['type']

            # Check exclusions
            if self._should_exclude_filesystem_entry(path, obj_type, excludes):
                continue

            # Generate creation command based on type
            creation_command = self._generate_creation_command(parsed_entry)
            if creation_command:
                commands.append(creation_command)

            # Generate permission command
            perm_command = self.command_generator.generate_permission_command(
                path, parsed_entry['owner'], parsed_entry['group'], parsed_entry['permissions']
            )
            commands.append(perm_command)

        return commands

    def _should_exclude_filesystem_entry(self, path: str, obj_type: str, excludes: Exclude) -> bool:
        """Check if a filesystem entry should be excluded."""
        exclusion_mapping = {
            'directory': excludes.directories,
            'file': excludes.files,
            'symlink': excludes.links
        }

        entry_category = self.state_parser.get_entry_type_category(obj_type)
        exclude_list = exclusion_mapping.get(entry_category, [])

        if self.exclusion_checker.should_exclude_path(path, exclude_list):
            return True

        return self.exclusion_checker.has_excluded_parent(path, excludes.directories)

    def _generate_creation_command(self, parsed_entry: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Generate appropriate creation command based on entry type."""
        path = parsed_entry['path']
        obj_type = parsed_entry['type']

        if obj_type in ('d', 'dir', 'directory'):
            return self.command_generator.generate_directory_command(path)
        elif obj_type in ('f', 'fl', 'file'):
            return self.command_generator.generate_file_command(path)
        elif obj_type in ('l', 'ln', 'link'):
            target = parsed_entry.get('target', '')
            return self.command_generator.generate_symlink_command(path, target)

        return None

    def save_sketch(self, sketch: Dict[str, Any], output_path: Path) -> bool:
        """
        Save sketch to JSON file.

        Args:
            sketch: FlowCTRL sketch dictionary
            output_path: Path to save the sketch file

        Returns:
            True if successful, False otherwise
        """
        try:
            self.stdout.info(f'Saving FlowCTRL Sketch file to {output_path}...')

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w") as f:
                json.dump(sketch, f, indent=4)

            self.stdout.info(f'Successfully saved sketch to {output_path}')
            return True

        except (IOError, TypeError, OSError) as e:
            self.stdout.err(f"Error saving sketch to {output_path}: {e}")
            return False

# CODE DUMP

