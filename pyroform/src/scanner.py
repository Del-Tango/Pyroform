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

from .models import FileInfo


def get_system_state(
    scan_paths: Optional[List[str]] = None,
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

    system_state = {
        'users': get_users_info(),
        'groups': get_groups_info(),
        'mounted_devices': get_mounted_devices_info(scan_paths, max_depth, include_hidden)
    }

    return system_state

def get_users_info() -> List[Dict[str, Any]]:
    """Get information about all system users."""
    users = []
    try:
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

def get_groups_info() -> List[Dict[str, Any]]:
    """Get information about all system groups."""
    groups = []
    try:
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

def get_mounted_devices_info(
    scan_paths: Optional[List[str]],
    max_depth: int,
    include_hidden: bool
) -> List[Dict[str, Any]]:
    """Get information about mounted devices and their contents."""
    mounted_devices = []

    try:
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

                # TODO - Configure from config file
                # Skip obviously virtual filesystems but be less restrictive
#               skip_patterns = ['/proc', '/sys', '/dev/pts', '/dev/shm', 'cgroup', 'mqueue', 'hugetlbfs']
                skip_patterns = ['/proc', '/sys', '/dev/pts', '/dev/shm']
                if any(pattern in mountpoint for pattern in skip_patterns):
                    continue

                # Skip tmpfs and devtmpfs
                if fstype in ['tmpfs', 'devtmpfs']:
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

                print(f"Scanning mountpoint: {mountpoint}")

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
                        print(f"  Found {len(device_info['files'])} files, {len(device_info['directories'])} directories, {len(device_info['symlinks'])} symlinks")
                    except Exception as e:
                        print(f"  Error scanning {mountpoint}: {e}")

                mounted_devices.append(device_info)

            except Exception as e:
                print(f"Error processing mount line '{mount}': {e}")
                continue

    except Exception as e:
        print(f"Error reading mounts: {e}")

    return mounted_devices

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

# Example usage and testing
if __name__ == "__main__":
    # Get complete system state
    system_state = get_system_state()

# CODE DUMP

#   @dataclass
#   class FileInfo:
#       path: str
#       owner: str
#       group: str
#       permissions: str
#       type: str


#   # Enhanced version that scans everything
#   def get_complete_system_state(max_depth=10, include_hidden=True) -> Dict[str, Any]:
#       """Get complete system state with all files, directories, and links."""
#       print("Fetching complete Linux system state...")

#       # Get all mountpoints
#       system_state = get_linux_system_state(
#           scan_paths=None,  # Scan all mountpoints
#           max_depth=10,     # Deeper scanning
#           include_hidden=True
#       )

#       return system_state



#   def get_system_state_summary(system_state: Dict[str, Any]) -> Dict[str, Any]:
#       """Generate a summary of the system state."""
#       summary = {
#           'total_users': len(system_state['users']),
#           'total_groups': len(system_state['groups']),
#           'total_mounted_devices': len(system_state['mounted_devices']),
#           'total_files': 0,
#           'total_directories': 0,
#           'total_symlinks': 0
#       }

#       for device in system_state['mounted_devices']:
#           summary['total_files'] += len(device['files'])
#           summary['total_directories'] += len(device['directories'])
#           summary['total_symlinks'] += len(device['symlinks'])

#       return summary




#   # Utility function to save state to JSON
#   def save_system_state_to_json(system_state: Dict[str, Any], filename: str) -> None:
#       """Save system state to JSON file."""
#       try:
#           with open(filename, 'w') as f:
#               json.dump(system_state, f, indent=2, default=str)
#           print(f"System state saved to {filename}")
#       except Exception as e:
#           print(f"Error saving to JSON: {e}")


# Display permissions in a more readable format
#   def display_permission_legend():
#       """Display a legend for numeric permissions."""
#       print("\nPermission Legend (Octal Notation):")
#       print("  First digit: Special permissions (setuid/setgid/sticky)")
#       print("  Second digit: Owner permissions")
#       print("  Third digit: Group permissions")
#       print("  Fourth digit: Other permissions")
#       print("\nPermission Values:")
#       print("  4 = read (r), 2 = write (w), 1 = execute (x)")
#       print("  Examples: 0644 = rw-r--r--, 0755 = rwxr-xr-x")
#       print("  Special: 4000 = setuid, 2000 = setgid, 1000 = sticky bit")
#       print("-" * 60)



#   # Generate summary
#   summary = get_system_state_summary(system_state)
#   print("\nSystem State Summary:")
#   for key, value in summary.items():
#       print(f"  {key}: {value}")

#   # Display permission legend
#   display_permission_legend()

#   # Display detailed information with NUMERICAL permissions
#   print(f"\nUsers ({len(system_state['users'])} total):")
#   for user in system_state['users']:
#       print(f"  - {user['username']} (UID: {user['uid']}, GID: {user['gid']}, Home: {user['home_directory']})")
#       print(f"    Groups: {', '.join(user['groups'])}")
#       print(f"    Shell: {user['shell']}")

#   print(f"\nGroups ({len(system_state['groups'])} total):")
#   for group in system_state['groups']:
#       print(f"  - {group['groupname']} (GID: {group['gid']})")
#       if group['members']:
#           print(f"    Members: {', '.join(group['members'])}")

#   print(f"\nMounted Devices ({len(system_state['mounted_devices'])} total):")
#   for device in system_state['mounted_devices']:
#       print(f"  - {device['device_path']} mounted at {device['mountpoint']} ({device['filesystem_type']})")
#       print(f"    Files: {len(device['files'])}")
#       print(f"    Directories: {len(device['directories'])}")
#       print(f"    Symlinks: {len(device['symlinks'])}")

#       # Show some samples with NUMERICAL permissions
#       if device['files']:
#           print("    Sample files:")
#           for file in device['files']:
#               print(f"      {file['path']} ({file['owner']}:{file['group']} {file['permissions']})")

#       if device['directories']:
#           print("    Sample directories:")
#           for dir in device['directories']:
#               print(f"      {dir['path']} ({dir['owner']}:{dir['group']} {dir['permissions']})")

#       if device['symlinks']:
#           print("    Sample symlinks:")
#           for link in device['symlinks']:
#               print(f"      {link['path']} -> {link.get('target', 'broken')} ({link['owner']}:{link['group']} {link['permissions']})")

#   # Save to file (still includes both numerical and symbolic for reference)
#   save_system_state_to_json(system_state, "complete_system_state.json")
#   print(f"\nComplete system state saved to complete_system_state.json")

#   # Show some common permission examples
#   print("\nCommon Permission Examples Found:")
#   common_perms = {}
#   for device in system_state['mounted_devices']:
#       for item in device['files'] + device['directories'] + device['symlinks']:
#           perm = item['permissions']
#           common_perms[perm] = common_perms.get(perm, 0) + 1

#   # Show top 10 most common permissions
#   print("Top 10 most common permissions:")
#   for perm, count in sorted(common_perms.items(), key=lambda x: x[1], reverse=True)[:10]:
#       symbolic = None
#       # Convert back to symbolic for display
#       try:
#           # This is a simplified conversion for common cases
#           perm_int = int(perm, 8)
#           symbolic = stat.filemode(perm_int)
#       except:
#           symbolic = "N/A"
#       print(f"  {perm} ({symbolic}): {count} occurrences")


