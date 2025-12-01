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
            "teardown-cmd": "",
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

