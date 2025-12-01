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


class SystemStateScanner:
    """
    Scans and collects current system state information.

    Responsible for gathering information about users, groups, mounted devices,
    and filesystem entries from the live system.
    """

    def __init__(self, stdout: STDOUTMsg):
        self.stdout = stdout

    def scan_system_state(
        self,
        pyro_config: Optional[PyroConfig] = None,
        max_depth: int = 10,
        include_hidden: bool = True
    ) -> Dict[str, Any]:
        """
        Scan and collect comprehensive system state information.

        Args:
            pyro_config: Pyro configuration for exclusion filtering
            max_depth: Maximum directory depth to scan
            include_hidden: Whether to include hidden files

        Returns:
            Dictionary containing system state organized by category
        """
        self.stdout.info('Scanning current machine state (users, groups, filesystem)...')
        self.stdout.debug(f'Max directory depth: {max_depth}')
        self.stdout.debug(f'Include hidden files: {include_hidden}')

        system_state = {
            'users': self._scan_users(pyro_config),
            'groups': self._scan_groups(pyro_config),
            'mounted_devices': self._scan_mounted_devices(
                pyro_config, max_depth, include_hidden
            )
        }

        self.stdout.debug(f'System State: {json.dumps(system_state, indent=4)}')
        return system_state

    def _scan_users(self, pyro_config: Optional[PyroConfig]) -> List[Dict[str, Any]]:
        """Scan system users information."""
        users = []
        try:
            if pyro_config and not pyro_config.users:
                return users

            for user in pwd.getpwall():
                if self._should_exclude_user(user.pw_name, pyro_config):
                    self.stdout.warn(f'Excluding user {user.pw_name}')
                    continue

                try:
                    groups = self._get_user_groups(user.pw_name)
                    users.append(SystemUser(
                        username=user.pw_name,
                        uid=user.pw_uid,
                        gid=user.pw_gid,
                        home_directory=user.pw_dir,
                        shell=user.pw_shell,
                        gecos=user.pw_gecos,
                        groups=groups
                    ).__dict__)
                except Exception as e:
                    self.stdout.err(f"Error processing user {user.pw_name}: {e}")

        except Exception as e:
            self.stdout.err(f"Error fetching users: {e}")

        return users

    def _scan_groups(self, pyro_config: Optional[PyroConfig]) -> List[Dict[str, Any]]:
        """Scan system groups information."""
        groups = []
        try:
            if pyro_config and not pyro_config.groups:
                return groups

            for group in grp.getgrall():
                if self._should_exclude_group(group.gr_name, pyro_config):
                    self.stdout.warn(f'Excluding group {group.gr_name}')
                    continue

                try:
                    groups.append(SystemGroup(
                        groupname=group.gr_name,
                        gid=group.gr_gid,
                        members=group.gr_mem
                    ).__dict__)
                except Exception as e:
                    self.stdout.err(f"Error processing group {group.gr_name}: {e}")

        except Exception as e:
            self.stdout.err(f"Error fetching groups: {e}")

        return groups

    def _scan_mounted_devices(
        self,
        pyro_config: Optional[PyroConfig],
        max_depth: int,
        include_hidden: bool
    ) -> List[Dict[str, Any]]:
        """Scan mounted devices and their contents."""
        mounted_devices = []

        try:
            if pyro_config and not pyro_config.devices:
                return mounted_devices

            mounts = self._get_mount_information()
            processed_mountpoints = set()

            for mount in mounts:
                device_info = self._parse_mount_entry(mount, processed_mountpoints, pyro_config)
                if device_info:
                    self._scan_device_contents(device_info, max_depth, include_hidden, pyro_config)
                    mounted_devices.append(device_info.__dict__)

        except Exception as e:
            self.stdout.err(f"Error reading mounts: {e}")

        return mounted_devices

    def _get_mount_information(self) -> List[str]:
        """Collect mount information from multiple sources."""
        mounts = []

        # Method 1: /proc/mounts
        if os.path.exists('/proc/mounts'):
            with open('/proc/mounts', 'r') as f:
                mounts.extend(f.readlines())

        # Method 2: df command
        try:
            result = subprocess.run(
                ['df', '-h', '-x', 'tmpfs', '-x', 'devtmpfs'],
                capture_output=True, text=True, check=True
            )
            df_lines = result.stdout.strip().split('\n')[1:]  # Skip header
            mounts.extend(df_lines)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Method 3: mount command
        try:
            result = subprocess.run(['mount'], capture_output=True, text=True, check=True)
            mounts.extend(result.stdout.strip().split('\n'))
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        return mounts

    def _parse_mount_entry(
        self,
        mount: str,
        processed_mountpoints: Set[str],
        pyro_config: Optional[PyroConfig]
    ) -> Optional[MountedDevice]:
        """Parse a single mount entry."""
        parts = mount.strip().split()
        if not parts:
            return None

        device, mountpoint, fstype = self._extract_mount_info(parts, mount)
        if not device or not mountpoint or mountpoint in processed_mountpoints:
            return None

        if self._should_exclude_device(device, pyro_config):
            self.stdout.warn(f'Excluding device {device}')
            return None

        processed_mountpoints.add(mountpoint)
        partitions = self._get_device_partitions(device)
        mounted_partition = self._find_mounted_partition(partitions, mountpoint)

        return MountedDevice(
            device_path=device,
            mountpoint=mountpoint,
            filesystem_type=fstype or 'unknown',
            mount_options="",
            partition=mounted_partition,
            partitions=partitions,
            files=[],
            directories=[],
            symlinks=[]
        )

    def _extract_mount_info(self, parts: List[str], mount: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract device, mountpoint, and filesystem type from mount entry."""
        # /proc/mounts format: device mountpoint fstype options dump pass
        if len(parts) >= 6 and parts[0] != 'Filesystem':
            return parts[0], parts[1], parts[2]

        # mount command format: device on mountpoint type fstype (options)
        if ' on ' in mount:
            try:
                device_index = parts.index('on') - 1
                mountpoint_index = parts.index('on') + 1
                type_index = parts.index('type') + 1

                if all(0 <= i < len(parts) for i in [device_index, mountpoint_index, type_index]):
                    return parts[device_index], parts[mountpoint_index], parts[type_index]
            except ValueError:
                pass

        # df command format: Filesystem Size Used Avail Use% Mounted on
        if len(parts) >= 6:
            return parts[0], parts[-1], "unknown"

        return None, None, None

    def _scan_device_contents(
        self,
        device_info: MountedDevice,
        max_depth: int,
        include_hidden: bool,
        pyro_config: Optional[PyroConfig]
    ) -> None:
        """Scan filesystem contents of a mounted device."""
        mountpoint = device_info.mountpoint

        if not os.path.exists(mountpoint) or not os.path.isdir(mountpoint):
            return

        self.stdout.debug(f"Scanning mountpoint: {mountpoint}")

        try:
            self._scan_filesystem_recursive(
                mountpoint,
                device_info,
                max_depth,
                include_hidden,
                current_depth=0,
                pyro_config=pyro_config
            )

            self.stdout.debug(
                f"  Found {len(device_info.files)} files, "
                f"{len(device_info.directories)} directories, "
                f"{len(device_info.symlinks)} symlinks"
            )
        except Exception as e:
            self.stdout.err(f"  Error scanning {mountpoint}: {e}")

    def _scan_filesystem_recursive(
        self,
        path: str,
        device_info: MountedDevice,
        max_depth: int,
        include_hidden: bool,
        current_depth: int,
        pyro_config: Optional[PyroConfig]
    ) -> None:
        """Recursively scan filesystem directory."""
        if current_depth > max_depth:
            return

        try:
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)

                if not include_hidden and entry.startswith('.'):
                    continue

                self._process_filesystem_entry(
                    full_path, device_info, max_depth, include_hidden,
                    current_depth, pyro_config
                )

        except (OSError, PermissionError):
            pass  # Skip directories we can't access

    def _process_filesystem_entry(
        self,
        full_path: str,
        device_info: MountedDevice,
        max_depth: int,
        include_hidden: bool,
        current_depth: int,
        pyro_config: Optional[PyroConfig]
    ) -> None:
        """Process a single filesystem entry."""
        try:
            stat_info = os.lstat(full_path)
            owner = self._get_username(stat_info.st_uid)
            group = self._get_groupname(stat_info.st_gid)
            permissions = self._get_numeric_permissions(stat_info.st_mode)

            file_info = FileSystemEntry(
                path=full_path,
                owner=owner,
                group=group,
                permissions=permissions,
                mountpoint=device_info.mountpoint
            )

            if stat.S_ISREG(stat_info.st_mode):
                if not self._should_exclude_file(full_path, pyro_config):
                    device_info.files.append(file_info)
            elif stat.S_ISDIR(stat_info.st_mode):
                if not self._should_exclude_directory(full_path, pyro_config):
                    device_info.directories.append(file_info)
                    if current_depth < max_depth:
                        self._scan_filesystem_recursive(
                            full_path, device_info, max_depth, include_hidden,
                            current_depth + 1, pyro_config
                        )
            elif stat.S_ISLNK(stat_info.st_mode):
                if not self._should_exclude_link(full_path, pyro_config):
                    file_info.target = self._read_symlink_target(full_path)
                    device_info.symlinks.append(file_info)

        except (OSError, PermissionError):
            pass  # Skip files we can't access

    def _get_user_groups(self, username: str) -> List[str]:
        """Get all groups a user belongs to."""
        try:
            result = subprocess.run(
                ['groups', username], capture_output=True, text=True, check=True
            )
            return result.stdout.strip().split(': ')[1].split()
        except (subprocess.CalledProcessError, IndexError, FileNotFoundError):
            return []

    def _get_device_partitions(self, device: str) -> List[Dict[str, str]]:
        """Get partition information for a device."""
        try:
            result = subprocess.run(
                ['lsblk', '-J', device], capture_output=True, text=True, check=True
            )
            lsblk_data = json.loads(result.stdout)
            return self._extract_partitions_from_lsblk(lsblk_data)
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, FileNotFoundError):
            return self._fallback_partition_detection(device)

    def _extract_partitions_from_lsblk(self, lsblk_data: Dict) -> List[Dict[str, str]]:
        """Extract partition information from lsblk JSON output."""
        partitions = []

        def _recurse_devices(devices):
            for device in devices.get('blockdevices', []):
                if 'children' in device:
                    for child in device['children']:
                        partitions.append({
                            'name': child['name'],
                            'size': child.get('size', ''),
                            'mountpoint': child.get('mountpoint', ''),
                            'fstype': child.get('fstype', '')
                        })

        _recurse_devices(lsblk_data)
        return partitions

    def _fallback_partition_detection(self, device: str) -> List[Dict[str, str]]:
        """Fallback method for partition detection."""
        partitions = []
        try:
            device_name = Path(device).name
            for entry in os.listdir('/dev'):
                if entry.startswith(device_name) and entry != device_name:
                    partitions.append({'name': entry, 'size': 'unknown'})
        except OSError:
            pass
        return partitions

    def _get_numeric_permissions(self, mode: int) -> str:
        """Convert file mode to numeric (octal) permissions notation."""
        permissions = mode & 0o7777
        return oct(permissions)[2:].zfill(4)

    def _get_username(self, uid: int) -> str:
        """Get username from UID."""
        try:
            return pwd.getpwuid(uid).pw_name
        except KeyError:
            return str(uid)

    def _get_groupname(self, gid: int) -> str:
        """Get group name from GID."""
        try:
            return grp.getgrgid(gid).gr_name
        except KeyError:
            return str(gid)

    def _read_symlink_target(self, path: str) -> str:
        """Read symlink target."""
        try:
            return os.readlink(path)
        except OSError:
            return 'broken'

    def _find_mounted_partition(self, partitions: List[Dict[str, str]], mountpoint: str) -> str:
        """Find partition name for a mountpoint."""
        for part in partitions:
            if part.get('mountpoint') == mountpoint:
                return part['name']
        return ''

    # Exclusion check methods
    def _should_exclude_user(self, username: str, pyro_config: Optional[PyroConfig]) -> bool:
        return (pyro_config and pyro_config.excludes and
                username in pyro_config.excludes.users)

    def _should_exclude_group(self, groupname: str, pyro_config: Optional[PyroConfig]) -> bool:
        return (pyro_config and pyro_config.excludes and
                groupname in pyro_config.excludes.groups)

    def _should_exclude_device(self, device: str, pyro_config: Optional[PyroConfig]) -> bool:
        return (pyro_config and pyro_config.excludes and
                device in pyro_config.excludes.devices)

    def _should_exclude_file(self, filepath: str, pyro_config: Optional[PyroConfig]) -> bool:
        return (pyro_config and pyro_config.excludes and
                filepath in pyro_config.excludes.files)

    def _should_exclude_directory(self, dirpath: str, pyro_config: Optional[PyroConfig]) -> bool:
        return (pyro_config and pyro_config.excludes and
                dirpath in pyro_config.excludes.directories)

    def _should_exclude_link(self, linkpath: str, pyro_config: Optional[PyroConfig]) -> bool:
        return (pyro_config and pyro_config.excludes and
                linkpath in pyro_config.excludes.links)

