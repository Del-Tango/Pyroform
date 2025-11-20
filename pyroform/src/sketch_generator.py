"""
FlowCTRL Sketch Generator for Pyroform
"""

import json
import pysnooper

from typing import Dict, Any, List
from pathlib import Path

from .models import PyroConfig, User, Group, Device, ActionType
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

    @pysnooper.snoop()
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

    @pysnooper.snoop()
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


    # TODO
#   def _generate_correction_commands(self, config: PyroConfig, system_state: dict, compared: dict) -> List[Dict[str, Any]]:
#       commands = []

#       return commands

    # TODO - WIP
#   @pysnooper.snoop()
    def _generate_cleanup_commands(self, config: PyroConfig, system_state: dict, compared: dict) -> List[Dict[str, Any]]:
        """
        Generate cleanup commands for scorch action

        Note: This is a simplified implementation. A real implementation would
        need to compare current system state with desired state.
        """
        commands = []
        cmd_prefix = '' if not self.dry_run else '# '
        # TODO - Make configurable from config file
#       system_state = get_system_state(
#           pyro_config=config, max_depth=100, include_hidden=True
#       )
#       compared = compare_system_state_with_pyro_file(system_state, config)

        print(f'[ DEBUG ]: system_state - {system_state}')
#       print('[ DEBUG ]: system_state - ', json.dumps(system_state, indent=4))
        print(f'[ DEBUG ]: compared - {compared}')
#       print('[ DEBUG ]: compared - ', json.dumps(compared, indent=4))
        print(f'[ DEBUG ]: compared[extra_directories] - {compared["extra_directories"]}')

        extra_usernames = " ".join([user['username'] for user in compared.get('extra_users', []) if user.get('username')])
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

        extra_groups = " ".join([group['groupname'] for group in compared.get('extra_groups', []) if group.get('groupname')])
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



#       # TODO
#       extra_mounted_devices = " ".join([])
#       if extra_mounted_devices.strip():
#           # Clean up groups not in config
#           cleanup_devices_cmd = {
#               "name": "Cleanup extra mounted block storage devices",
#               "cmd": f"{self.cmd_prefix}for device in {extra_mounted_devices}; do umount -f $device; done",
#               "setup-cmd": "",
#               "on-ok-cmd": f"echo 'Eliminated: {extra_mounted_devices}'",
#               "on-nok-cmd": f"echo 'Could not scorch extra mounted devices! Details: {extra_mounted_devices}'",
#               "fatal-nok": False,
#           }
#           commands.append(cleanup_devices_cmd)

#       # TODO - Support chunks
#       extra_directory_list = []
#       if len(extra_directory_list) > self.chunk_size:
#           directory_chunks = self.list_splitter.split(extra_directory_list)

        extra_directory_list = [directory['path'] for directory in compared.get('extra_directories', []) if directory.get('path')]
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

        extra_files_and_linx_list = [file['path'] for file in compared.get('extra_files', []) if file.get('path')] \
            + [link['path'] for link in compared.get('extra_symlinks', []) if link.get('path')]
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

    @pysnooper.snoop()
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
            "Users": self._generate_user_commands(config.users),
            "Groups": self._generate_group_commands(config.groups),
            "Devices": self._generate_device_commands(config.devices),
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
            "Devices": self._generate_mount_commands(config.devices),  # Only mount-related commands
        }

        # Remove empty sections
        sketch = {k: v for k, v in sketch.items() if v}
        return sketch

    @pysnooper.snoop()
    def _generate_user_commands(self, users: List[User]) -> List[Dict[str, Any]]:
        """Generate user management commands"""
        commands = []
        cmd_prefix = '' if not self.dry_run else '# '

        for user in users:
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

    def _generate_group_commands(self, groups: List[Group]) -> List[Dict[str, Any]]:
        """Generate group management commands"""
        commands = []
        cmd_prefix = '' if not self.dry_run else '# '

        for group in groups:
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

    def _generate_mount_commands(self, devices: List[Device]) -> List[Dict[str, Any]]:
        """
        Generate device mounting commands only (no file/directory creation)

        For mount action, we only handle the actual device mounting,
        not the directory structure creation.
        """
        commands = []
        cmd_prefix = '' if not self.dry_run else '#'

        for device in devices:
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

    @pysnooper.snoop()
    def _generate_device_commands(self, devices: List[Device]) -> List[Dict[str, Any]]:
        """
        Generate complete device commands including directory structure
        Used for configure action
        """
        commands = []
        cmd_prefix = '' if not self.dry_run else '# '

        for device in devices:
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

    @pysnooper.snoop()
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

#   @pysnooper.snoop()
#   def _generate_file_commands(self, devices: List[Device]) -> List[Dict[str, Any]]:
#       """Generate file and directory creation commands from device states"""
#       commands = []

#       for device in devices:
#           for state_entry in device.state:
#               state_parts = state_entry.split(",")
#               if len(state_parts) >= 5:
#                   obj_type, path, owner, group, permissions = state_parts[:5]

#                   if obj_type == "fl":  # file
#                       file_cmd = {
#                           "name": f"create_file_{path.replace('/', '_')}",
#                           "cmd": f"touch {path}",
#                           "setup-cmd": f"test -f {path}",
#                           "on-ok-cmd": f"echo 'File {path} exists'",
#                           "on-nok-cmd": f"echo 'Creating file {path}'",
#                           "fatal-nok": False,
#                       }
#                       commands.append(file_cmd)

#       return commands


#           "summary": f"Scorch system according to {config.label}",

#           "Files": self._generate_file_commands(config.devices),
#           "summary": f"Configure system according to {config.label}",

#           "summary": f"Mount devices according to {config.label}",

        #f"getent group {group.name}",
        #groupdel {group.name}

#           csv_users = ','.join(member_users)


        # username="john"; groups="developers docker admin"; for group in $groups; do groupadd -f $group; done && useradd -m -G $(echo $groups | tr " " ",") $username
        # f"useradd -m -p {user.password} {user.name}",


#           # Add user to groups
#           for group_name in user.groups:
#               group_cmd = {
#                   "name": f"add_user_{user.name}_to_{group_name}",
#                   "cmd": f"usermod -a -G {group_name} {user.name}",
#                   "setup-cmd": f"id {user.name} | grep -q '{group_name}'",
#                   "on-ok-cmd": f"echo 'User {user.name} already in group {group_name}'",
#                   "on-nok-cmd": f"echo 'Adding user {user.name} to group {group_name}'",
#                   "fatal-nok": False,
#               }
#               commands.append(group_cmd)


