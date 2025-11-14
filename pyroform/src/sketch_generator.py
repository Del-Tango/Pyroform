"""
FlowCTRL Sketch Generator for Pyroform
"""

import json
import pysnooper

from typing import Dict, Any, List
from pathlib import Path

from .models import PyroConfig, User, Group, Device, ActionType
from .logging import STDOUTMsg


class SketchGenerator:
    """
    Generates FlowCTRL sketch files from PyroConfig objects
    """

    def __init__(self, *args, stdout=None, **kwargs):
        self.stdout = stdout or STDOUTMsg(
            debug_mode=False,
            timestamp=False,
        )

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
            "Files": self._generate_file_commands(config.devices),
            "summary": f"Configure system according to {config.label}",
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
            "Devices": self._generate_mount_commands(
                config.devices
            ),  # Only mount-related commands
            "summary": f"Mount devices according to {config.label}",
        }

        # Remove empty sections
        sketch = {k: v for k, v in sketch.items() if v}
        return sketch

    def generate_scorch_sketch(self, config: PyroConfig) -> Dict[str, Any]:
        """
        Generate sketch for scorch action (cleanup)

        Args:
            config: PyroConfig object

        Returns:
            FlowCTRL sketch dictionary
        """
        sketch = {
            "name": f"Pyroform Auto-Generated Sketch {config.label}",
            "Cleanup": self._generate_cleanup_commands(config),
            "summary": f"Scorch system according to {config.label}",
        }

        # Remove empty sections
        sketch = {k: v for k, v in sketch.items() if v}
        return sketch

    @pysnooper.snoop()
    def _generate_user_commands(self, users: List[User]) -> List[Dict[str, Any]]:
        """Generate user management commands"""
        commands = []

        for user in users:
            user_cmd = {
                "name": f"create_user_{user.name}",
                "cmd": f"useradd -m -p {user.password} {user.name}",
                "setup-cmd": f"id {user.name}",
                "teardown-cmd": f"userdel -r {user.name}",
                "on-ok-cmd": f"echo 'User {user.name} exists or created successfully'",
                "on-nok-cmd": f"echo 'Failed to create user {user.name}'",
                "fatal-nok": False,
            }
            commands.append(user_cmd)

            # Add user to groups
            for group_name in user.groups:
                group_cmd = {
                    "name": f"add_user_{user.name}_to_{group_name}",
                    "cmd": f"usermod -a -G {group_name} {user.name}",
                    "setup-cmd": f"id {user.name} | grep -q '{group_name}'",
                    "on-ok-cmd": f"echo 'User {user.name} already in group {group_name}'",
                    "on-nok-cmd": f"echo 'Adding user {user.name} to group {group_name}'",
                    "fatal-nok": False,
                }
                commands.append(group_cmd)

        return commands

    def _generate_group_commands(self, groups: List[Group]) -> List[Dict[str, Any]]:
        """Generate group management commands"""
        commands = []

        for group in groups:
            group_cmd = {
                "name": f"create_group_{group.name}",
                "cmd": f"groupadd {group.name}",
                "setup-cmd": f"getent group {group.name}",
                "teardown-cmd": f"groupdel {group.name}",
                "on-ok-cmd": f"echo 'Group {group.name} exists'",
                "on-nok-cmd": f"echo 'Creating group {group.name}'",
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

        for device in devices:
            # Create mountpoint directory
            mountpoint_cmd = {
                "name": f"create_mountpoint_{device.mountpoint.replace('/', '_')}",
                "cmd": f"mkdir -p {device.mountpoint}",
                "setup-cmd": f"test -d {device.mountpoint}",
                "on-ok-cmd": f"echo 'Mountpoint {device.mountpoint} exists'",
                "on-nok-cmd": f"echo 'Creating mountpoint {device.mountpoint}'",
                "fatal-nok": True,
            }
            commands.append(mountpoint_cmd)

            # Mount device
            device_cmd = {
                "name": f"mount_device_{device.label}",
                "cmd": f"mount {device.path} {device.mountpoint}",
                "setup-cmd": f"mount | grep -q '{device.path} on {device.mountpoint}'",
                "teardown-cmd": f"umount {device.mountpoint}",
                "on-ok-cmd": f"echo 'Device {device.path} already mounted to {device.mountpoint}'",
                "on-nok-cmd": f"echo 'Mounting {device.path} to {device.mountpoint}'",
                "fatal-nok": True,
            }
            commands.append(device_cmd)

        return commands

    def _generate_device_commands(self, devices: List[Device]) -> List[Dict[str, Any]]:
        """
        Generate complete device commands including directory structure
        Used for configure action
        """
        commands = []

        for device in devices:
            # Create mountpoint directory
            mountpoint_cmd = {
                "name": f"create_mountpoint_{device.mountpoint.replace('/', '_')}",
                "cmd": f"mkdir -p {device.mountpoint}",
                "setup-cmd": f"test -d {device.mountpoint}",
                "on-ok-cmd": f"echo 'Mountpoint {device.mountpoint} exists'",
                "on-nok-cmd": f"echo 'Creating mountpoint {device.mountpoint}'",
                "fatal-nok": True,
            }
            commands.append(mountpoint_cmd)

            # Mount device
            device_cmd = {
                "name": f"mount_device_{device.label}",
                "cmd": f"mount {device.path} {device.mountpoint}",
                "setup-cmd": f"mount | grep -q '{device.path} on {device.mountpoint}'",
                "teardown-cmd": f"umount {device.mountpoint}",
                "on-ok-cmd": f"echo 'Device {device.path} already mounted to {device.mountpoint}'",
                "on-nok-cmd": f"echo 'Mounting {device.path} to {device.mountpoint}'",
                "fatal-nok": True,
            }
            commands.append(device_cmd)

            # Create directory structure from state (for configure action)
            for state_entry in device.state:
                state_parts = state_entry.split(",")
                if len(state_parts) >= 5:
                    obj_type, path, owner, group, permissions = state_parts[:5]

                    if obj_type == "dir":
                        dir_cmd = {
                            "name": f"create_dir_{path.replace('/', '_')}",
                            "cmd": f"mkdir -p {path}",
                            "setup-cmd": f"test -d {path}",
                            "on-ok-cmd": f"echo 'Directory {path} exists'",
                            "on-nok-cmd": f"echo 'Creating directory {path}'",
                            "fatal-nok": False,
                        }
                        commands.append(dir_cmd)

                    # Set ownership and permissions
                    perm_cmd = {
                        "name": f"set_perms_{path.replace('/', '_')}",
                        "cmd": f"chown {owner}:{group} {path} && chmod {permissions} {path}",
                        "setup-cmd": f"stat -c '%U:%G %a' {path} | grep -q '{owner}:{group} {permissions}'",
                        "on-ok-cmd": f"echo 'Permissions for {path} are correct'",
                        "on-nok-cmd": f"echo 'Setting permissions for {path}'",
                        "fatal-nok": False,
                    }
                    commands.append(perm_cmd)

        return commands

    def _generate_file_commands(self, devices: List[Device]) -> List[Dict[str, Any]]:
        """Generate file and directory creation commands from device states"""
        commands = []

        for device in devices:
            for state_entry in device.state:
                state_parts = state_entry.split(",")
                if len(state_parts) >= 5:
                    obj_type, path, owner, group, permissions = state_parts[:5]

                    if obj_type == "fl":  # file
                        file_cmd = {
                            "name": f"create_file_{path.replace('/', '_')}",
                            "cmd": f"touch {path}",
                            "setup-cmd": f"test -f {path}",
                            "on-ok-cmd": f"echo 'File {path} exists'",
                            "on-nok-cmd": f"echo 'Creating file {path}'",
                            "fatal-nok": False,
                        }
                        commands.append(file_cmd)

        return commands

    def _generate_cleanup_commands(self, config: PyroConfig) -> List[Dict[str, Any]]:
        """
        Generate cleanup commands for scorch action

        Note: This is a simplified implementation. A real implementation would
        need to compare current system state with desired state.
        """
        commands = []

        # Clean up users not in config
        cleanup_user_cmd = {
            "name": "cleanup_orphaned_users",
            "cmd": "echo 'User cleanup would happen here'",
            "setup-cmd": "echo 'Checking for orphaned users'",
            "on-ok-cmd": "echo 'No orphaned users found'",
            "on-nok-cmd": "echo 'Cleaning up orphaned users'",
            "fatal-nok": False,
        }
        commands.append(cleanup_user_cmd)

        # Clean up groups not in config
        cleanup_group_cmd = {
            "name": "cleanup_orphaned_groups",
            "cmd": "echo 'Group cleanup would happen here'",
            "setup-cmd": "echo 'Checking for orphaned groups'",
            "on-ok-cmd": "echo 'No orphaned groups found'",
            "on-nok-cmd": "echo 'Cleaning up orphaned groups'",
            "fatal-nok": False,
        }
        commands.append(cleanup_group_cmd)

        return commands

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

