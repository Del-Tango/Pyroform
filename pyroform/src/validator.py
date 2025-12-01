"""
System Validation for Pyroform
"""

import os
import pwd
import grp
import stat
import json
import subprocess
import pysnooper

from typing import Dict, List, Any, Tuple, Set, Optional
from dataclasses import dataclass
from pathlib import Path

from .models import PyroConfig, User, Group, Device, Exclude
from .logging import STDOUTMsg


@dataclass
class ValidationResult:
    """Result of system validation"""

    is_valid: bool
    system_state: Dict[str, list]
    discrepancies: Dict[str, list]
    summary: Dict[str, Any]


class SystemValidator:
    """
    Validates current system state against desired Pyro configuration
    """

    #@pysnooper.snoop()
    def __init__(self, stdout: STDOUTMsg | None = None, config: dict | None = None) -> None:
        self._last_result: ValidationResult = None
        self.config = config or {}
        self.stdout = stdout or STDOUTMsg(
            debug_mode=self.config.get('debug', False),
            timestamp=self.config.get('log_timestamp') or self.config.get('debug', False),
        )

    #@pysnooper.snoop()
    def validate_configuration(self, config: PyroConfig) -> ValidationResult:
        """
        Compare current system state with desired configuration

        Args:
            config: Desired Pyro configuration

        Returns:
            ValidationResult with discrepancies and summary
        """

        current_state = self.get_system_state(
            pyro_config=config, max_depth=100, include_hidden=True
        )
        differences = self.compare_system_state_with_pyro_file(current_state, config)

        self.stdout.debug('Current State: ' + json.dumps(current_state, indent=4))
        self.stdout.debug('Discrepancies: ' + json.dumps(differences, indent=4))

        critical_issues = sum([len(item) for item in differences if 'mismatch' not in item])
        total_issues = sum([len(item) for item in differences])

        summary = {
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "is_valid": total_issues == 0,
        }

        self.stdout.debug('Summary: ' + json.dumps(summary, indent=4))

        self._last_result = ValidationResult(
            is_valid=summary["is_valid"],
            discrepancies=differences,
            system_state=current_state,
            summary=summary
        )

        return self._last_result

    #@pysnooper.snoop()
    def get_validation_report(self) -> Dict[str, Any]:
        """
        Generate detailed validation report

        Returns:
            Comprehensive validation report
        """
        if self._last_result is None:
            return {
                "summary": {"total_checks": 0, "passed": 0, "failed": 0, "warnings": 0},
                "discrepancies": [],
                "timestamp": self._get_timestamp(),
            }

        # Use the last validation result
        discrepancies = self._last_result.discrepancies
        total_checks = len(discrepancies)
        failed = len(discrepancies)
        passed = (
            total_checks - failed
        )  # This is simplified - in reality we'd count actual checks
        warnings = len([d for d in discrepancies if not d.get("critical", False)])

        return {
            "summary": {
                "total_checks": total_checks,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "total_issues": self._last_result.summary.get("total_issues", 0),
                "critical_issues": self._last_result.summary.get("critical_issues", 0),
            },
            "discrepancies": discrepancies,
            "timestamp": self._get_timestamp(),
            "is_valid": self._last_result.is_valid,
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp for reports"""
        from datetime import datetime

        return datetime.now().isoformat()

    # SCANNER

    #@pysnooper.snoop()
    def get_system_state(
        self,
        scan_paths: Optional[List[str]] = None,
        pyro_config: Optional[PyroConfig] = None,
        max_depth: int = 10,
        include_hidden: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch Linux system state information.

        Args:
            scan_paths: List of paths to scan for files/directories (default: all mountpoints)
            max_depth: Maximum directory depth to scan
            include_hidden: Whether to include hidden files (starting with .)

        Returns:
            Dictionary with system state organized by users, groups, and mounted devices
        """

        self.stdout.info('Scanning current machine state (users, groups, filesystem)...')
        self.stdout.debug(f'Max directory depth: {max_depth}')
        self.stdout.debug(f'Include hidden files: {include_hidden}')

        system_state = {
            'users': self.get_users_info(pyro_config=pyro_config),
            'groups': self.get_groups_info(pyro_config=pyro_config),
            'mounted_devices': self.get_mounted_devices_info(scan_paths, max_depth, include_hidden, pyro_config=pyro_config)
        }

        self.stdout.debug(f'System State:' + json.dumps(system_state, indent=4))

        return system_state

    #@pysnooper.snoop()
    def get_users_info(self, pyro_config: Optional[PyroConfig] = None) -> List[Dict[str, Any]]:
        """Get information about all system users."""
        users = []
        try:
            if pyro_config and not pyro_config.users:
                return users
            for user in pwd.getpwall():
                if pyro_config.excludes and user in pyro_config.excludes.users:
                    self.stdout.warn(f'Excluding user {user}')
                    continue
                try:
                    groups = self.get_user_groups(user.pw_name)
                    users.append({
                        'username': user.pw_name,
                        'uid': user.pw_uid,
                        'gid': user.pw_gid,
                        'home_directory': user.pw_dir,
                        'shell': user.pw_shell,
                        'gecos': user.pw_gecos,
                        'groups': groups
                    })
                except Exception as e:
                    print(f"Error processing user {user.pw_name}: {e}")
                    continue
        except Exception as e:
            print(f"Error fetching users: {e}")

        return users

    ##@pysnooper.snoop()
    def get_user_groups(self, username: str) -> List[str]:
        """Get all groups a user belongs to."""
        try:
            result = subprocess.run(
                ['groups', username],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split(': ')[1].split()
        except (subprocess.CalledProcessError, IndexError, FileNotFoundError):
            return []

    ##@pysnooper.snoop()
    def get_groups_info(self, pyro_config: Optional[PyroConfig] = None) -> List[Dict[str, Any]]:
        """Get information about all system groups."""
        groups = []
        try:
            if pyro_config and not pyro_config.groups:
                return groups
            for group in grp.getgrall():
                if pyro_config.excludes and group in pyro_config.excludes.groups:
                    self.stdout.warn(f'Excluding group {group}')
                    continue
                try:
                    groups.append({
                        'groupname': group.gr_name,
                        'gid': group.gr_gid,
                        'members': group.gr_mem
                    })
                except Exception as e:
                    print(f"Error processing group {group.gr_name}: {e}")
                    continue
        except Exception as e:
            print(f"Error fetching groups: {e}")

        return groups

    #@pysnooper.snoop()
    def get_mounted_devices_info(
        self,
        scan_paths: Optional[List[str]],
        max_depth: int,
        include_hidden: bool,
        pyro_config: Optional[PyroConfig] = None,
    ) -> List[Dict[str, Any]]:
        """Get information about mounted devices and their contents."""
        mounted_devices = []

        try:

            if pyro_config and not pyro_config.devices:
                return mounted_devices

            # Get mount information using multiple methods
            mounts = []

            # Method 1: /proc/mounts
            if os.path.exists('/proc/mounts'):
                with open('/proc/mounts', 'r') as f:
                    mounts.extend(f.readlines())

            # Method 2: df command
            try:
                result = subprocess.run(
                    ['df', '-h', '-x', 'tmpfs', '-x', 'devtmpfs'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                # Skip header line
                df_lines = result.stdout.strip().split('\n')[1:]
                mounts.extend(df_lines)
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

            # Method 3: mount command
            try:
                result = subprocess.run(
                    ['mount'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                mount_lines = result.stdout.strip().split('\n')
                mounts.extend(mount_lines)
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

            processed_mountpoints = set()

            for mount in mounts:
                try:
                    parts = mount.strip().split()
                    if not parts:
                        continue

                    # Parse different mount output formats
                    device = None
                    mountpoint = None
                    fstype = None
                    options = ""

                    if len(parts) >= 6 and parts[0] != 'Filesystem':
                        # /proc/mounts format: device mountpoint fstype options dump pass
                        device = parts[0]
                        mountpoint = parts[1]
                        fstype = parts[2]
                        options = parts[3]
                    elif len(parts) >= 6 and ' on ' in mount:
                        # mount command format: device on mountpoint type fstype (options)
                        device_index = parts.index('on') - 1
                        mountpoint_index = parts.index('on') + 1
                        type_index = parts.index('type') + 1

                        if device_index >= 0 and mountpoint_index < len(parts) and type_index < len(parts):
                            device = parts[device_index]
                            mountpoint = parts[mountpoint_index]
                            fstype = parts[type_index]
                            # Extract options from parentheses
                            options_start = mount.find('(')
                            options_end = mount.find(')')
                            if options_start != -1 and options_end != -1:
                                options = mount[options_start+1:options_end]
                    elif len(parts) >= 6:
                        # df command format: Filesystem Size Used Avail Use% Mounted on
                        device = parts[0]
                        mountpoint = parts[-1]
                        fstype = "unknown"

                    if not device or not mountpoint:
                        continue

                    # Skip if we've already processed this mountpoint
                    if mountpoint in processed_mountpoints:
                        continue

                    if pyro_config.excludes and device in pyro_config.excludes.devices:
                        self.stdout.warn(f'Excluding device {device}')
                        continue

                    processed_mountpoints.add(mountpoint)

                    # If specific scan paths are provided, only include those
                    if scan_paths:
                        if not any(mountpoint.startswith(path) for path in scan_paths):
                            continue

                    partitions = self.get_device_partitions(device)
                    mounted_partition = [part['name'] for part in partitions if part['mountpoint'] == mountpoint]

                    device_info = {
                        'device_path': device,
                        'mountpoint': mountpoint,
                        'filesystem_type': fstype or 'unknown',
                        'mount_options': options,
                        'partition': '' if not mounted_partition else mounted_partition[0],
                        'partitions': partitions,
                        'files': [],
                        'directories': [],
                        'symlinks': []
                    }

                    self.stdout.debug(f"Scanning mountpoint: {mountpoint}")

                    # Scan filesystem contents
                    if os.path.exists(mountpoint) and os.path.isdir(mountpoint):
                        try:
                            self.scan_filesystem(
                                mountpoint,
                                device_info,
                                max_depth,
                                include_hidden,
                                current_depth=0,
                                pyro_config=pyro_config,
                            )
                            self.stdout.debug(f"  Found {len(device_info['files'])} files, {len(device_info['directories'])} directories, {len(device_info['symlinks'])} symlinks")
                        except Exception as e:
                            self.stdout.err(f"  Error scanning {mountpoint}: {e}")

                    mounted_devices.append(device_info)

                except Exception as e:
                    self.stdout.err(f"Error processing mount line '{mount}': {e}")
                    continue

        except Exception as e:
            self.stdout.err(f"Error reading mounts: {e}")

        return mounted_devices

    #@pysnooper.snoop()
    def get_device_partitions(self, device: str) -> List[Dict[str, str]]:
        """Get partition information for a device."""
        partitions = []
        try:
            result = subprocess.run(
                ['lsblk', '-J', device],
                capture_output=True,
                text=True,
                check=True
            )
            lsblk_data = json.loads(result.stdout)

            def extract_partitions(device_data):
                for device in device_data.get('blockdevices', []):
                    if 'children' in device:
                        for child in device['children']:
                            partitions.append({
                                'name': child['name'],
                                'size': child.get('size', ''),
                                'mountpoint': child.get('mountpoint', ''),
                                'fstype': child.get('fstype', '')
                            })

            extract_partitions(lsblk_data)

        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, FileNotFoundError):
            # Fallback to basic partition detection
            try:
                device_name = Path(device).name
                for entry in os.listdir('/dev'):
                    if entry.startswith(device_name) and entry != device_name:
                        partitions.append({'name': entry, 'size': 'unknown'})
            except OSError:
                pass

        return partitions

    ##@pysnooper.snoop()
    def get_numeric_permissions(self, mode: int) -> str:
        """
        Convert file mode to numeric (octal) permissions notation.

        Args:
            mode: File mode from os.stat()

        Returns:
            String representation of octal permissions (e.g., '0644', '0755')
        """
        # Extract the permission bits (last 12 bits)
        permissions = mode & 0o7777
        # Format as 4-digit octal string
        return oct(permissions)[2:].zfill(4)

    ##@pysnooper.snoop()
    def scan_filesystem(
        self,
        path: str,
        device_info: Dict[str, Any],
        max_depth: int,
        include_hidden: bool,
        current_depth: int = 0,
        pyro_config: Optional[PyroConfig] = None,
    ) -> None:
        """Recursively scan filesystem and categorize files, directories, and symlinks."""
        if current_depth > max_depth:
            return

        try:
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)

                # Skip hidden files if not included
                if not include_hidden and entry.startswith('.'):
                    continue

                try:
                    stat_info = os.lstat(full_path)

                    # Get owner and group
                    try:
                        owner = pwd.getpwuid(stat_info.st_uid).pw_name
                    except KeyError:
                        owner = str(stat_info.st_uid)

                    try:
                        group = grp.getgrgid(stat_info.st_gid).gr_name
                    except KeyError:
                        group = str(stat_info.st_gid)

                    # Get permissions in NUMERICAL (octal) notation
                    permissions = self.get_numeric_permissions(stat_info.st_mode)

                    file_info = {
                        'path': full_path,
                        'owner': owner,
                        'group': group,
                        'permissions': permissions,
                        'permissions_symbolic': stat.filemode(stat_info.st_mode)  # Keep both for reference
                    }

                    # Categorize by type
                    if stat.S_ISREG(stat_info.st_mode):
                        if pyro_config.excludes and full_path in pyro_config.excludes.files:
                            self.stdout.warn(f'Excluding file {full_path}')
                            continue
                        device_info['files'].append(file_info)
                    elif stat.S_ISDIR(stat_info.st_mode):
                        if pyro_config.excludes and full_path in pyro_config.excludes.directories:
                            self.stdout.warn(f'Excluding directory {full_path}')
                            continue
                        device_info['directories'].append(file_info)
                        # Recursively scan directories
                        if current_depth < max_depth:
                            self.scan_filesystem(
                                full_path,
                                device_info,
                                max_depth,
                                include_hidden,
                                current_depth + 1,
                                pyro_config=pyro_config,
                            )
                    elif stat.S_ISLNK(stat_info.st_mode):
                        if pyro_config.excludes and full_path in pyro_config.excludes.links:
                            self.stdout.warn(f'Excluding link {full_path}')
                            continue
                        try:
                            target = os.readlink(full_path)
                            file_info['target'] = target
                            device_info['symlinks'].append(file_info)
                        except OSError:
                            file_info['target'] = 'broken'
                            device_info['symlinks'].append(file_info)

                except (OSError, PermissionError) as e:
                    # Skip files we can't access
                    continue

        except (OSError, PermissionError) as e:
            # Skip directories we can't access
            pass

    # DIFERENCES

    #@pysnooper.snoop()
    def compare_system_state_with_pyro_file(self, system_state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare current system state with configuration and generate difference report.

        Args:
            system_state: The system state dictionary from get_linux_system_state()
            config: Configuration dictionary with desired state

        Returns:
            Dictionary containing differences organized by category
        """

        self.stdout.info('Comparing current system state with Pyro file...')

        differences = {
            'missing_users': [],
            'extra_users': [],
            'user_mismatches': [],
            'missing_groups': [],
            'extra_groups': [],
            'group_mismatches': [],
            'missing_directories': [],
            'extra_directories': [],
            'directory_mismatches': [],
            'missing_files': [],
            'extra_files': [],
            'file_mismatches': [],
            'missing_symlinks': [],
            'extra_symlinks': [],
            'symlink_mismatches': [],
            'missing_mountpoints': [],
            'mountpoint_mismatches': []
        }

        # Extract current state for easier comparison
        current_users = {user['username']: user for user in system_state['users']}
        current_groups = {group['groupname']: group for group in system_state['groups']}
        # Build current filesystem state
        current_fs_state = self.build_filesystem_state(system_state)
        # Compare users
        if config.users:
            self.stdout.debug(f'config.users - {config.users}')
            self.compare_users(config.users, current_users, differences, config.excludes)
        # Compare groups
        if config.groups:
            self.stdout.debug(f'config.groups - {config.groups}')
            self.compare_groups(config.groups, current_groups, differences, config.excludes)
        # Compare filesystem state
        if config.devices:
            self.stdout.debug(f'config.devices - {config.devices}')
            self.compare_filesystem(config.devices, current_fs_state, differences, config.excludes)
        sanitized = {k: v for k, v in differences.items() if v}
        self.stdout.debug("Differences: " + json.dumps(sanitized, indent=4))
        return sanitized

    def build_filesystem_state(self, system_state: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Build a unified filesystem state from system state."""
        fs_state = {}

        for device in system_state['mounted_devices']:
            mountpoint = device['mountpoint']

            # Add directories
            for dir_info in device['directories']:
                path = dir_info['path']
                fs_state[path] = {
                    'type': 'directory',
                    'owner': dir_info['owner'],
                    'group': dir_info['group'],
                    'permissions': dir_info['permissions'],
                    'mountpoint': mountpoint
                }

            # Add files
            for file_info in device['files']:
                path = file_info['path']
                fs_state[path] = {
                    'type': 'file',
                    'owner': file_info['owner'],
                    'group': file_info['group'],
                    'permissions': file_info['permissions'],
                    'mountpoint': mountpoint
                }

            # Add symlinks
            for link_info in device['symlinks']:
                path = link_info['path']
                fs_state[path] = {
                    'type': 'symlink',
                    'owner': link_info['owner'],
                    'group': link_info['group'],
                    'permissions': link_info['permissions'],
                    'target': link_info.get('target', 'broken'),
                    'mountpoint': mountpoint
                }

        return fs_state

    ##@pysnooper.snoop()
    def compare_users(self, config_users: List[User], current_users: Dict, differences: Dict[str, Any], excludes: Exclude | None = None) -> None:
        """Compare configured users with current system users."""
        config_user_names = set()

        for config_user in config_users:
            username = config_user.name
            if excludes and username in excludes.users:
                continue
            config_user_names.add(username)

            if username not in current_users:
                differences['missing_users'].append({
                    'label': config_user.label,
                    'username': username,
                    'password': config_user.password,
                    'groups': config_user.groups
                })
            else:
                # Check user properties
                current_user = current_users[username]
                mismatches = []

                # Check group membership
                expected_groups = set(config_user.groups)
                current_groups = set(current_user.get('groups', []))

                missing_groups = expected_groups - current_groups
                extra_groups = current_groups - expected_groups

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
                        'username': username,
                        'mismatches': mismatches
                    })

        # Find extra users (in system but not in config)
        current_user_names = set(current_users.keys())
        extra_users = current_user_names - config_user_names

        for username in extra_users:
            if excludes and username in excludes.users:
                continue
            user = current_users[username]
    #       if user['uid'] >= 1000:  # Typically non-system users
            differences['extra_users'].append({
                'username': username,
                'uid': user['uid'],
                'home_directory': user['home_directory']
            })

    ##@pysnooper.snoop()
    def compare_groups(self, config_groups: List[Group], current_groups: Dict, differences: Dict[str, Any], excludes: Exclude | None = None) -> None:
        """Compare configured groups with current system groups."""
        config_group_names = set()

        for config_group in config_groups:
            groupname = config_group.name
            if excludes and groupname in excludes.groups:
                continue
            config_group_names.add(groupname)

            if groupname not in current_groups:
                differences['missing_groups'].append({
                    'label': config_group.label,
                    'groupname': groupname,
                    'members': config_group.users,
                })
            else:
                # Check group properties
                current_group = current_groups[groupname]
                mismatches = []

                # Check group membership
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
                        'groupname': groupname,
                        'mismatches': mismatches
                    })

        # Find extra groups (in system but not in config)
        current_group_names = set(current_groups.keys())
        extra_groups = current_group_names - config_group_names

        for groupname in extra_groups:
            if excludes and groupname in excludes.groups:
                continue
            group = current_groups[groupname]
#           if group['gid'] >= 1000:  # Typically non-system groups
            differences['extra_groups'].append({
                'groupname': groupname,
                'gid': group['gid'],
                'members': group['members']
            })

    def parse_config_state_entry(self, entry: str) -> Dict[str, Any]:
        """Parse configuration state entries like 'dir,/path,owner,group,permissions'."""
        parts = entry.split(',')
        if len(parts) < 5:
            return None

        entry_type = parts[0]
        path = parts[1]
        owner = parts[2]
        group = parts[3]
        permissions = parts[4]

        result = {
            'type': entry_type,
            'path': path,
            'owner': owner,
            'group': group,
            'permissions': permissions
        }

        if entry_type == 'ln' and len(parts) >= 6:
            result['target'] = parts[5]

        return result

    def compare_filesystem(self, config_devices: List[Device], current_fs_state: Dict, differences: Dict[str, Any], excludes: Exclude | None = None) -> None:
        """Compare configured filesystem state with current state."""
        config_paths = set()

        for device in config_devices:
            if excludes and device in excludes.devices:
                continue
            mountpoint = device.mountpoint
            config_states = device.state

            # Check if mountpoint exists
            mountpoint_exists = any(
                mp == mountpoint
                for mp in {
                    mp for item in current_fs_state.values() for mp in [item.get('mountpoint')] if mp
                })

            if not mountpoint_exists and mountpoint:
                differences['missing_mountpoints'].append({
                    'label': device.label,
                    'mountpoint': mountpoint
                })

            for state_entry in config_states:
                config_item = self.parse_config_state_entry(state_entry)
                if not config_item:
                    continue

                path = config_item['path']
                if excludes and path in excludes.directories or path in excludes.files or path in excludes.links:
                    continue
                config_paths.add(path)

                if path not in current_fs_state:
                    # Item is missing from system
                    if config_item['type'] == 'dir':
                        differences['missing_directories'].append(config_item)
                    elif config_item['type'] == 'fl':
                        differences['missing_files'].append(config_item)
                    elif config_item['type'] == 'ln':
                        differences['missing_symlinks'].append(config_item)
                else:
                    # Item exists, check properties
                    current_item = current_fs_state[path]
                    mismatches = []

                    # Check type
                    type_map = {'dir': 'directory', 'fl': 'file', 'ln': 'symlink'}
                    expected_type = type_map.get(config_item['type'])
                    if current_item['type'] != expected_type:
                        mismatches.append({
                            'property': 'type',
                            'expected': expected_type,
                            'actual': current_item['type']
                        })

                    # Check owner
                    if config_item['owner'] != current_item['owner']:
                        mismatches.append({
                            'property': 'owner',
                            'expected': config_item['owner'],
                            'actual': current_item['owner']
                        })

                    # Check group
                    if config_item['group'] != current_item['group']:
                        mismatches.append({
                            'property': 'group',
                            'expected': config_item['group'],
                            'actual': current_item['group']
                        })

                    # Check permissions
                    if config_item['permissions'] != current_item['permissions']:
                        mismatches.append({
                            'property': 'permissions',
                            'expected': config_item['permissions'],
                            'actual': current_item['permissions']
                        })

                    # Check symlink target
                    if (config_item['type'] == 'ln' and
                        current_item['type'] == 'symlink' and
                        'target' in config_item and
                        config_item['target'] != current_item.get('target')):
                        mismatches.append({
                            'property': 'target',
                            'expected': config_item['target'],
                            'actual': current_item.get('target', 'missing')
                        })

                    if mismatches:
                        mismatch_entry = {
                            'path': path,
                            'mismatches': mismatches,
                            'expected': config_item,
                            'actual': current_item
                        }

                        if config_item['type'] == 'dir':
                            differences['directory_mismatches'].append(mismatch_entry)
                        elif config_item['type'] == 'fl':
                            differences['file_mismatches'].append(mismatch_entry)
                        elif config_item['type'] == 'ln':
                            differences['symlink_mismatches'].append(mismatch_entry)

        # Find extra items (in system but not in config)
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

            if item['type'] == 'directory':
                differences['extra_directories'].append(extra_entry)
            elif item['type'] == 'file':
                differences['extra_files'].append(extra_entry)
            elif item['type'] == 'symlink':
                extra_entry['target'] = item.get('target', 'broken')
                differences['extra_symlinks'].append(extra_entry)


# CODE DUMP

