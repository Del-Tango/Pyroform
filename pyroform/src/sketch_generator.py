"""
FlowCTRL Sketch Generator for Pyroform
"""

import json
import pysnooper

from typing import Dict, Any, List, Union
from pathlib import Path

from .models import PyroConfig, User, Group, Device, Exclude, ActionType
from .logging import STDOUTMsg
from .splitter import ListSplitter

from .scanner import get_system_state
from .difference import compare_system_state_with_pyro_file


class SketchGenerator:
    """
    Generates FlowCTRL sketch files from PyroConfig objects
    """

    def __init__(self, *args, stdout: STDOUTMsg | None = None, dry_run: bool | None = False, **kwargs):
        self.chunk_size = 500
        self.dry_run = dry_run
        self.cmd_prefix = '' if not self.dry_run else '# '
        # TODO - Configure from config file
        self.stdout = stdout or STDOUTMsg(
            debug_mode=False,
            timestamp=False,
        )
        self.list_splitter = ListSplitter(chunk_size=self.chunk_size)

    #@pysnooper.snoop()
    def generate_sketch(self, config: PyroConfig, action: ActionType) -> Dict[str, Any]:
        """
        Generate FlowCTRL sketch based on action type

        Args:
            config: PyroConfig object
            action: Type of action to generate sketch for

        Returns:
            FlowCTRL sketch dictionary
        """
        self.cmd_prefix = '' if not self.dry_run else '# '
        if action == ActionType.CONFIGURE:
            return self.generate_configure_sketch(config)
        elif action == ActionType.MOUNT:
            return self.generate_mount_sketch(config)
        elif action == ActionType.SCORCH:
            return self.generate_scorch_sketch(config)
        elif action == ActionType.VALIDATE:
            raise ValueError("Validate action does not generate sketches")
        else:
            raise ValueError(f"Unsupported action type: {action}")

    #@pysnooper.snoop()
    def generate_scorch_sketch(self, config: PyroConfig) -> Dict[str, Any]:
        """
        Generate sketch for scorch action (cleanup)

        Args:
            config: PyroConfig object

        Returns:
            FlowCTRL sketch dictionary
        """
        system_state = get_system_state(
            pyro_config=config, max_depth=100, include_hidden=True
        )
        compared = compare_system_state_with_pyro_file(system_state, config)
        sketch = {
            "name": f"Pyroform Auto-Generated Sketch {config.label}",
            "Cleanup": self._generate_cleanup_commands(config, system_state, compared),
#           "Corrections": self._generate_correction_commands(config, system_state, compared),
        }

        # Remove empty sections
        sketch = {k: v for k, v in sketch.items() if v}
        return sketch

    # TODO - WIP
#   def _generate_correction_commands(self, config: PyroConfig, system_state: dict, compared: dict) -> List[Dict[str, Any]]:
#       commands = []
#       return commands

#   #@pysnooper.snoop()
    def has_excluded_parent(self, path: Union[str, Path], excluded_paths: List[Union[str, Path]]) -> bool:
        """
        Check if a path has any excluded path as its parent directory.

        Args:
            path: The path to check
            excluded_paths: List of paths that should not be parents

        Returns:
            bool: True if any excluded path is a parent of the given path
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

#   #@pysnooper.snoop()
    def _generate_cleanup_commands(self, config: PyroConfig, system_state: dict, compared: dict) -> List[Dict[str, Any]]:
        """
        Generate cleanup commands for scorch action

        Note: This is a simplified implementation. A real implementation would
        need to compare current system state with desired state.
        """
        commands = []

        extra_usernames = " ".join([
            user['username']
            for user in compared.get('extra_users', [])
            if user.get('username')
            and user['username'] not in config.excludes.users
        ])
        if extra_usernames.strip():
            # Clean up users not in config
            cleanup_user_cmd = {
                "name": "Cleanup extra users",
                "cmd": f"{self.cmd_prefix}for user in {extra_usernames}; do userdel -f -r $user; done",
                "setup-cmd": "",
                "on-ok-cmd": f"echo 'Eliminated: {extra_usernames}'",
                "on-nok-cmd": f"echo 'Could not scorch extra system users! Details: {extra_usernames}'",
                "fatal-nok": False,
            }
            commands.append(cleanup_user_cmd)

        extra_groups = " ".join([
            group['groupname']
            for group in compared.get('extra_groups', [])
            if group.get('groupname')
            and group['groupname'] not in config.excludes.groups
        ])
        if extra_groups.strip():
            # Clean up groups not in config
            cleanup_group_cmd = {
                "name": "Cleanup extra groups",
                "cmd": f"{self.cmd_prefix}for group in {extra_groups}; do groupdel $group; done",
                "setup-cmd": "",
                "on-ok-cmd": f"echo 'Eliminated: {extra_groups}'",
                "on-nok-cmd": f"echo 'Could not scorch extra system groups! Details: {extra_groups}'",
                "fatal-nok": False,
            }
            commands.append(cleanup_group_cmd)

        extra_directory_list = [
            directory['path']
            for directory in compared.get('extra_directories', [])
            if directory.get('path')
            and directory['path'] not in config.excludes.directories
            and not self.has_excluded_parent(directory['path'], config.excludes.directories)
        ]
        dir_chunks = self.list_splitter.split(extra_directory_list) if len(extra_directory_list) > self.chunk_size else [extra_directory_list]
        for chunk in dir_chunks:
            extra_directories = " ".join(chunk)
            if not extra_directories.strip():
                continue
            # Clean up groups not in config
            cleanup_directories_cmd = {
                "name": "Cleanup extra directories",
                "cmd": f"{self.cmd_prefix}rm -rf {extra_directories}",
                "setup-cmd": "",
                "on-ok-cmd": f"echo 'Eliminated: {extra_directories}'",
                "on-nok-cmd": f"echo 'Could not scorch extra directories! Details: {extra_directories}'",
                "fatal-nok": False,
            }
            commands.append(cleanup_directories_cmd)

        extra_files_and_linx_list = [
            file['path']
            for file in compared.get('extra_files', [])
            if file.get('path')
            and file['path'] not in config.excludes.files
            and not self.has_excluded_parent(file['path'], config.excludes.directories)
        ] + [
            link['path']
            for link in compared.get('extra_symlinks', [])
            if link.get('path')
            and link['path'] not in config.excludes.links
            and not self.has_excluded_parent(link['path'], config.excludes.directories)
        ]
        file_chunks = self.list_splitter.split(extra_files_and_linx_list) if len(extra_files_and_linx_list) > self.chunk_size else [extra_files_and_linx_list]
        for chunk in file_chunks:
            extra_files_and_links = " ".join(chunk)
            if not extra_files_and_links.strip():
                continue
            # Clean up groups not in config
            cleanup_files_and_links_cmd = {
                "name": "Cleanup extra files and links",
                "cmd": f"{self.cmd_prefix}rm -f {extra_files_and_links}",
                "setup-cmd": "",
                "on-ok-cmd": f"echo 'Eliminated: {extra_files_and_links}'",
                "on-nok-cmd": f"echo 'Could not scorch extra files and links! Details: {extra_files_and_links}'",
                "fatal-nok": False,
            }
            commands.append(cleanup_files_and_links_cmd)

        return commands

    #@pysnooper.snoop()
    def generate_configure_sketch(self, config: PyroConfig) -> Dict[str, Any]:
        """
        Generate sketch for configure action (users, groups, file permissions)

        Args:
            config: PyroConfig object

        Returns:
            FlowCTRL sketch dictionary
        """
        sketch = {
            "name": f"Pyroform Auto-Generated Sketch {config.label}",
            "Users": self._generate_user_commands(config.users, excludes=config.excludes.users),
            "Groups": self._generate_group_commands(config.groups, excludes=config.excludes.groups),
            "Devices": self._generate_device_commands(config.devices, excludes=config.excludes),
        }

        # Remove empty sections
        sketch = {k: v for k, v in sketch.items() if v}
        self.stdout.info('FlowCTRL Sketch %s' % str(json.dumps(sketch, indent=4)))
        return sketch

    def generate_mount_sketch(self, config: PyroConfig) -> Dict[str, Any]:
        """
        Generate sketch for mount action (device mounting only)

        Args:
            config: PyroConfig object

        Returns:
            FlowCTRL sketch dictionary
        """
        sketch = {
            "name": f"Pyroform Auto-Generated Sketch {config.label}",
            "Devices": self._generate_mount_commands(config.devices, excludes=config.excludes.devices),  # Only mount-related commands
        }

        # Remove empty sections
        sketch = {k: v for k, v in sketch.items() if v}
        return sketch

    #@pysnooper.snoop()
    def _generate_user_commands(self, users: List[User], excludes: Union[List[str], None] = None) -> List[Dict[str, Any]]:
        """Generate user management commands"""
        commands = []
        cmd_prefix = '' if not self.dry_run else '# '

        for user in users:
            if excludes and user.name in excludes:
                self.stdout.info(f'Excluding system user: {user.name}')
                continue
            group_membership = [str(grp) for grp in user.groups]
            csv_groups = ','.join(group_membership)
            groups = " ".join(group_membership)
            user_cmd = {
                "name": f"Creating System User {user.name}",
                "cmd": f"{self.cmd_prefix}for group in {groups}; do groupadd -f $group; done && useradd -m -p '{user.password}' -G '{csv_groups}' '{user.name}' || exit 0",
                "setup-cmd": f"id {user.name} && echo 'User {user.name} already exists' || exit 0",
                "teardown-cmd": "",
                "on-ok-cmd": f"echo 'User {user.name} exists or created successfully'",
                "on-nok-cmd": f"echo 'Failed to create user {user.name}'",
                "fatal-nok": False,
            }
            commands.append(user_cmd)

        return commands

    def _generate_group_commands(self, groups: List[Group], excludes: Union[List[str], None] = None) -> List[Dict[str, Any]]:
        """Generate group management commands"""
        commands = []
        cmd_prefix = '' if not self.dry_run else '# '

        for group in groups:
            if excludes and group.name in excludes:
                self.stdout.info(f'Excluding system group: {group.name}')
                continue
            member_users = [str(usr) for usr in group.users]
            users = " ".join(member_users)
            group_cmd = {
                "name": f"Creating System Group {group.name}",
                "cmd": f"{self.cmd_prefix}groupadd -f '{group.name}' && for user in {users}; do id $user || useradd -m $user; usermod -a -G '{group.name}' $user; done",
                "setup-cmd": f"getent group {group.name} && echo 'Group {group.name} already exists' || exit 0",
                "teardown-cmd": "",
                "on-ok-cmd": f"echo 'Group {group.name} exists'",
                "on-nok-cmd": f"echo 'Failed to create group {group.name}'",
                "fatal-nok": False,
            }
            commands.append(group_cmd)

        return commands

    # TODO
    def _generate_mount_commands(self, devices: List[Device], excludes: Union[List[str], None] = None) -> List[Dict[str, Any]]:
        """
        Generate device mounting commands only (no file/directory creation)

        For mount action, we only handle the actual device mounting,
        not the directory structure creation.
        """
        commands = []
        cmd_prefix = '' if not self.dry_run else '#'

        for device in devices:
            if excludes and device.path in excludes:
                self.stdout.info(f'Excluding block storage device: {device.label} - {device.path}')
                continue
            # Create mountpoint directory
            mountpoint_cmd = {
                "name": f"Creating System Mountpoint Directory {device.mountpoint}",
                "cmd": f"{self.cmd_prefix} mkdir -p '{device.mountpoint}' && sudo mount '{device.path}{device.partition}' '{device.mountpoint}'",  #f"mkdir -p {device.mountpoint}",
                "setup-cmd": f"test -d {device.mountpoint}",
                "teardown-cmd": "",
                "on-ok-cmd": f"echo 'Mountpoint {device.mountpoint} exists'",
                "on-nok-cmd": f"echo 'Creating mountpoint {device.mountpoint}'",
                "fatal-nok": True,
            }
            commands.append(mountpoint_cmd)

            # Mount device
            device_cmd = {
                "name": f"Mounting Block Device {device.label}",
                "cmd": f"{self.cmd_prefix} mount {device.path} {device.mountpoint}",
                "setup-cmd": f"mount | grep -q '{device.path} on {device.mountpoint}'",
                "teardown-cmd": f"umount {device.mountpoint}",
                "on-ok-cmd": f"echo 'Device {device.path} already mounted to {device.mountpoint}'",
                "on-nok-cmd": f"echo 'Mounting {device.path} to {device.mountpoint}'",
                "fatal-nok": True,
            }
            commands.append(device_cmd)

        return commands

    #@pysnooper.snoop()
    def _generate_device_commands(self, devices: List[Device], excludes: Union[Exclude, None] = None) -> List[Dict[str, Any]]:
        """
        Generate complete device commands including directory structure
        Used for configure action
        """
        commands = []
        cmd_prefix = '' if not self.dry_run else '# '

        for device in devices:
            if excludes and device.path in excludes.devices:
                self.stdout.info(f'Excluding block storage device: {device.label} - {device.path}')
                continue
            # Create mountpoint directory
            if device.mountpoint:
                mountpoint_cmd = {
                    "name": f"Creating System Mountpoint Directory {device.mountpoint}",
                    "cmd": f"{self.cmd_prefix}mkdir -p {device.mountpoint}",
                    "setup-cmd": f"test -d {device.mountpoint}",
                    "teardown-cmd": "",
                    "on-ok-cmd": f"echo 'Mountpoint {device.mountpoint} exists'",
                    "on-nok-cmd": f"echo 'Creating mountpoint {device.mountpoint}'",
                    "fatal-nok": True,
                }
                commands.append(mountpoint_cmd)

            # Mount device
            if device.path:
                device_cmd = {
                    "name": f"Mounting Block Device {device.label}",
                    "cmd": f"{self.cmd_prefix}mount {device.path} {device.mountpoint}",
                    "setup-cmd": f"mount | grep -q '{device.path} on {device.mountpoint}'",
                    "teardown-cmd": "",
                    "on-ok-cmd": f"echo 'Device {device.path} already mounted to {device.mountpoint}'",
                    "on-nok-cmd": f"echo 'Mounting {device.path} to {device.mountpoint}'",
                    "fatal-nok": True,
                }
                commands.append(device_cmd)

            # Create directory structure from state (for configure action)
            if device.state:
                for state_entry in device.state:
                    state_parts = state_entry.split(",")
                    if not len(state_parts) >= 5:
                        self.stdout.err(f'Invalid file state entry for device {device.label}! Details: {state_entry}')
                        continue

                    obj_type, path, owner, group, permissions = state_parts[:5]

                    if obj_type.lower() in ("d", "dir", "directory"):
                        if excludes and path in excludes.directories or self.has_excluded_parent(path, excludes.directories):
                            self.stdout.info(f'Excluding directory: {path}')
                            continue
                        dir_cmd = {
                            "name": f"Creating Directory {path}",
                            "cmd": f"{self.cmd_prefix}mkdir -p {path}",
                            "setup-cmd": f"test -d {path}",
                            "teardown-cmd": "",
                            "on-ok-cmd": f"echo 'Directory {path} exists'",
                            "on-nok-cmd": f"echo 'Creating directory {path}'",
                            "fatal-nok": True,
                        }
                        commands.append(dir_cmd)
                    elif obj_type.lower() in ("f", "fl", "file"):
                        if excludes and path in excludes.files or self.has_excluded_parent(path, excludes.directories):
                            self.stdout.info(f'Excluding file: {path}')
                            continue
                        dir_cmd = {
                            "name": f"Creating Regular File {path}",
                            "cmd": f"{self.cmd_prefix}touch {path}",
                            "setup-cmd": f"test -f {path}",
                            "teardown-cmd": "",
                            "on-ok-cmd": f"echo 'File {path} exists'",
                            "on-nok-cmd": f"echo 'Creating file {path}'",
                            "fatal-nok": True,
                        }
                        commands.append(dir_cmd)
                    elif obj_type.lower() in ("l", "ln", "link"):
                        if excludes and path in excludes.links or self.has_excluded_parent(path, excludes.directories):
                            self.stdout.info(f'Excluding link: {path}')
                            continue
                        dir_cmd = {
                            "name": f"Creating Symbolic Link {path}", #.replace('/', '_')
                            "cmd": f"{self.cmd_prefix}ln -s {state_parts[5]} {path}",
                            "setup-cmd": f"test -L {path}",
                            "teardown-cmd": "",
                            "on-ok-cmd": f"echo 'File {path} exists'",
                            "on-nok-cmd": f"echo 'Creating file {path}'",
                            "fatal-nok": True,
                        }
                        commands.append(dir_cmd)
                    # Set ownership and permissions
                    perm_cmd = {
                        "name": f"Setting Permissions For {path}", #.replace('/', '_')
                        "cmd": f"{self.cmd_prefix}chown {owner}:{group} {path} && chmod {permissions} {path}",
                        "setup-cmd": f"stat -c '%U:%G %a' {path} | grep -q '{owner}:{group} {permissions}'",
                        "teardown-cmd": "",
                        "on-ok-cmd": f"echo 'Permissions for {path} are correct'",
                        "on-nok-cmd": f"echo 'Setting permissions for {path}'",
                        "fatal-nok": True,
                    }
                    commands.append(perm_cmd)

        return commands

    #@pysnooper.snoop()
    def save_sketch(self, sketch: Dict[str, Any], output_path: Path) -> bool:
        """
        Save sketch to JSON file

        Args:
            sketch: FlowCTRL sketch dictionary
            output_path: Path to save the sketch file

        Returns:
            True if successful, False otherwise
        """
        try:
            self.stdout.info(f'Saving FlowCTRL Sketch file to {output_path}...')
            with open(output_path, "w") as f:
                json.dump(sketch, f, indent=4)
            return True
        except (IOError, TypeError) as e:
            self.stdout.err(f"Error saving sketch to {output_path}: {e}")
            return False

# CODE DUMP

