import os
import pwd
import grp
import subprocess
import json
import stat

import pysnooper

from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .models import FileInfo, PyroConfig
from .logging import STDOUTMsg

# TODO - Configure from Pyroform interface (config file / CLI args)
stdout = STDOUTMsg(
    debug_mode=False,
    timestamp=False,
)


#@pysnooper.snoop()
def get_system_state(
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

    stdout.info('Scanning current machine state (users, groups, filesystem)...')
    stdout.debug(f'Max directory depth: {max_depth}')
    stdout.debug(f'Include hidden files: {include_hidden}')

    system_state = {
        'users': get_users_info(pyro_config=pyro_config),
        'groups': get_groups_info(pyro_config=pyro_config),
        'mounted_devices': get_mounted_devices_info(scan_paths, max_depth, include_hidden, pyro_config=pyro_config)
    }

    stdout.debug(f'System State:' + json.dumps(system_state, indent=4))

    return system_state

#@pysnooper.snoop()
def get_users_info(pyro_config: Optional[PyroConfig] = None) -> List[Dict[str, Any]]:
    """Get information about all system users."""
    users = []
    try:
        if not pyro_config.users:
            return users
        for user in pwd.getpwall():
            try:
                groups = get_user_groups(user.pw_name)
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
def get_user_groups(username: str) -> List[str]:
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
def get_groups_info(pyro_config: Optional[PyroConfig] = None) -> List[Dict[str, Any]]:
    """Get information about all system groups."""
    groups = []
    try:
        if not pyro_config.groups:
            return groups
        for group in grp.getgrall():
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

##@pysnooper.snoop()
def get_mounted_devices_info(
    scan_paths: Optional[List[str]],
    max_depth: int,
    include_hidden: bool,
    pyro_config: Optional[PyroConfig] = None,
) -> List[Dict[str, Any]]:
    """Get information about mounted devices and their contents."""
    mounted_devices = []

    try:

        if not pyro_config.devices:
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
                processed_mountpoints.add(mountpoint)

                # If specific scan paths are provided, only include those
                if scan_paths:
                    if not any(mountpoint.startswith(path) for path in scan_paths):
                        continue

                device_info = {
                    'device_path': device,
                    'mountpoint': mountpoint,
                    'filesystem_type': fstype or 'unknown',
                    'mount_options': options,
                    'partitions': get_device_partitions(device),
                    'files': [],
                    'directories': [],
                    'symlinks': []
                }

                stdout.debug(f"Scanning mountpoint: {mountpoint}")

                # Scan filesystem contents
                if os.path.exists(mountpoint) and os.path.isdir(mountpoint):
                    try:
                        scan_filesystem(
                            mountpoint,
                            device_info,
                            max_depth,
                            include_hidden,
                            current_depth=0
                        )
                        stdout.debug(f"  Found {len(device_info['files'])} files, {len(device_info['directories'])} directories, {len(device_info['symlinks'])} symlinks")
                    except Exception as e:
                        stdout.err(f"  Error scanning {mountpoint}: {e}")

                mounted_devices.append(device_info)

            except Exception as e:
                stdout.err(f"Error processing mount line '{mount}': {e}")
                continue

    except Exception as e:
        stdout.err(f"Error reading mounts: {e}")

    return mounted_devices

#@pysnooper.snoop()
def get_device_partitions(device: str) -> List[Dict[str, str]]:
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
def get_numeric_permissions(mode: int) -> str:
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
    path: str,
    device_info: Dict[str, Any],
    max_depth: int,
    include_hidden: bool,
    current_depth: int = 0
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
                permissions = get_numeric_permissions(stat_info.st_mode)

                file_info = {
                    'path': full_path,
                    'owner': owner,
                    'group': group,
                    'permissions': permissions,
                    'permissions_symbolic': stat.filemode(stat_info.st_mode)  # Keep both for reference
                }

                # Categorize by type
                if stat.S_ISREG(stat_info.st_mode):
                    device_info['files'].append(file_info)
                elif stat.S_ISDIR(stat_info.st_mode):
                    device_info['directories'].append(file_info)
                    # Recursively scan directories
                    if current_depth < max_depth:
                        scan_filesystem(
                            full_path,
                            device_info,
                            max_depth,
                            include_hidden,
                            current_depth + 1
                        )
                elif stat.S_ISLNK(stat_info.st_mode):
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

# CODE DUMP


