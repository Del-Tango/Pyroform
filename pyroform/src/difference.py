import os
import json

import pysnooper

from typing import Dict, List, Any, Tuple, Set
from pathlib import Path

from .models import User, Group, Device


@pysnooper.snoop()
def compare_system_state_with_pyro_file(system_state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare current system state with configuration and generate difference report.

    Args:
        system_state: The system state dictionary from get_linux_system_state()
        config: Configuration dictionary with desired state

    Returns:
        Dictionary containing differences organized by category
    """

    differences = {
        'missing_users': [],
        'extra_users': [],              #
        'user_mismatches': [],          #?
        'missing_groups': [],
        'extra_groups': [],             #
        'group_mismatches': [],         #?
        'missing_directories': [],
        'extra_directories': [],        #
        'directory_mismatches': [],
        'missing_files': [],
        'extra_files': [],              #
        'file_mismatches': [],
        'missing_symlinks': [],
        'extra_symlinks': [],           #
        'symlink_mismatches': [],       #?
        'missing_mountpoints': [],
        'mountpoint_mismatches': []     #?
    }

    # Extract current state for easier comparison
    current_users = {user['username']: user for user in system_state['users']}
    current_groups = {group['groupname']: group for group in system_state['groups']}

    # Build current filesystem state
    current_fs_state = build_filesystem_state(system_state)


    # Compare users
    if config.users:

        print(f'[ DEBUG ]: config.users - {config.users}')

        compare_users(config.users, current_users, differences)

    # Compare groups
    if config.groups:
        compare_groups(config.groups, current_groups, differences)

    # Compare filesystem state
    if config.devices:
        compare_filesystem(config.devices, current_fs_state, differences)

    return differences

def build_filesystem_state(system_state: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
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

@pysnooper.snoop()
def compare_users(config_users: List[User], current_users: Dict, differences: Dict[str, Any]) -> None:
    """Compare configured users with current system users."""
    config_user_names = set()

    for config_user in config_users:
        username = config_user.name
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

    # Filter out system users (typically UID < 1000)
    for username in extra_users:
        user = current_users[username]
#       if user['uid'] >= 1000:  # Typically non-system users
        differences['extra_users'].append({
            'username': username,
            'uid': user['uid'],
            'home_directory': user['home_directory']
        })

@pysnooper.snoop()
def compare_groups(config_groups: List[Group], current_groups: Dict, differences: Dict[str, Any]) -> None:
    """Compare configured groups with current system groups."""
    config_group_names = set()

    for config_group in config_groups:
        groupname = config_group.name
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

    # Filter out system groups (typically GID < 1000)
    for groupname in extra_groups:
        group = current_groups[groupname]
        if group['gid'] >= 1000:  # Typically non-system groups
            differences['extra_groups'].append({
                'groupname': groupname,
                'gid': group['gid'],
                'members': group['members']
            })

def parse_config_state_entry(entry: str) -> Dict[str, Any]:
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

def compare_filesystem(config_devices: List[Device], current_fs_state: Dict, differences: Dict[str, Any]) -> None:
    """Compare configured filesystem state with current state."""
    config_paths = set()

    for device in config_devices:
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
            config_item = parse_config_state_entry(state_entry)
            if not config_item:
                continue

            path = config_item['path']
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

    # We might not want to list ALL extra items, so we can filter
    # For now, we'll include them all
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


# TODO - DEPRECATED
def generate_difference_report(differences: Dict[str, Any]) -> str:
    """Generate a human-readable difference report."""
    report = []

    # Summary
    total_issues = sum(len(items) for items in differences.values())
    report.append(f"SYSTEM STATE COMPARISON REPORT")
    report.append(f"Total issues found: {total_issues}")
    report.append("=" * 60)

    # Users section
    if differences['missing_users']:
        report.append("\n❌ MISSING USERS:")
        for user in differences['missing_users']:
            report.append(f"  - {user['username']} (label: {user['label']})")
            report.append(f"    Groups: {', '.join(user['groups'])}")

    if differences['extra_users']:
        report.append("\n⚠️  EXTRA USERS (in system but not in config):")
        for user in differences['extra_users']:
            report.append(f"  - {user['username']} (UID: {user['uid']}, Home: {user['home_directory']})")

    if differences['user_mismatches']:
        report.append("\n🔧 USER MISMATCHES:")
        for user in differences['user_mismatches']:
            report.append(f"  - {user['username']} (label: {user['label']})")
            for mismatch in user['mismatches']:
                if mismatch['property'] == 'groups':
                    report.append(f"    Groups mismatch:")
                    if mismatch['missing']:
                        report.append(f"      Missing: {', '.join(mismatch['missing'])}")
                    if mismatch['extra']:
                        report.append(f"      Extra: {', '.join(mismatch['extra'])}")

    # Groups section
    if differences['missing_groups']:
        report.append("\n❌ MISSING GROUPS:")
        for group in differences['missing_groups']:
            report.append(f"  - {group['groupname']} (label: {group['label']})")
            report.append(f"    Members: {', '.join(group['members'])}")

    if differences['extra_groups']:
        report.append("\n⚠️  EXTRA GROUPS (in system but not in config):")
        for group in differences['extra_groups']:
            report.append(f"  - {group['groupname']} (GID: {group['gid']})")
            if group['members']:
                report.append(f"    Members: {', '.join(group['members'])}")

    if differences['group_mismatches']:
        report.append("\n🔧 GROUP MISMATCHES:")
        for group in differences['group_mismatches']:
            report.append(f"  - {group['groupname']} (label: {group['label']})")
            for mismatch in group['mismatches']:
                if mismatch['property'] == 'members':
                    report.append(f"    Members mismatch:")
                    if mismatch['missing']:
                        report.append(f"      Missing: {', '.join(mismatch['missing'])}")
                    if mismatch['extra']:
                        report.append(f"      Extra: {', '.join(mismatch['extra'])}")

    # Filesystem section
    if differences['missing_mountpoints']:
        report.append("\n❌ MISSING MOUNTPOINTS:")
        for mountpoint in differences['missing_mountpoints']:
            report.append(f"  - {mountpoint['mountpoint']} (label: {mountpoint['label']})")

    def format_fs_item(item):
        return f"{item['path']} ({item['owner']}:{item['group']} {item['permissions']})"

    if differences['missing_directories']:
        report.append("\n❌ MISSING DIRECTORIES:")
        for dir in differences['missing_directories']:
            report.append(f"  - {format_fs_item(dir)}")

    if differences['missing_files']:
        report.append("\n❌ MISSING FILES:")
        for file in differences['missing_files']:
            report.append(f"  - {format_fs_item(file)}")

    if differences['missing_symlinks']:
        report.append("\n❌ MISSING SYMLINKS:")
        for link in differences['missing_symlinks']:
            target_info = f" -> {link['target']}" if 'target' in link else ""
            report.append(f"  - {format_fs_item(link)}{target_info}")

    # Mismatches
    if differences['directory_mismatches']:
        report.append("\n🔧 DIRECTORY MISMATCHES:")
        for dir in differences['directory_mismatches']:
            report.append(f"  - {dir['path']}")
            for mismatch in dir['mismatches']:
                report.append(f"    {mismatch['property']}: expected '{mismatch['expected']}', got '{mismatch['actual']}'")

    if differences['file_mismatches']:
        report.append("\n🔧 FILE MISMATCHES:")
        for file in differences['file_mismatches']:
            report.append(f"  - {file['path']}")
            for mismatch in file['mismatches']:
                report.append(f"    {mismatch['property']}: expected '{mismatch['expected']}', got '{mismatch['actual']}'")

    if differences['symlink_mismatches']:
        report.append("\n🔧 SYMLINK MISMATCHES:")
        for link in differences['symlink_mismatches']:
            report.append(f"  - {link['path']}")
            for mismatch in link['mismatches']:
                report.append(f"    {mismatch['property']}: expected '{mismatch['expected']}', got '{mismatch['actual']}'")

    return "\n".join(report)

# Example usage
if __name__ == "__main__":
    # Your configuration
    config = {
        "Label": "User Management Test",
        "Users": [
            {
                "label": "test_user_1",
                "Name": "pyrotest1",
                "Password": "testpass1",
                "Groups": [
                    "pyrogroup1"
                ]
            },
            {
                "label": "test_user_2",
                "Name": "pyrotest2",
                "Password": "testpass2",
                "Groups": [
                    "pyrogroup1",
                    "pyrogroup2"
                ]
            }
        ],
        "Groups": [
            {
                "label": "group_1",
                "Name": "pyrogroup1",
                "Users": [
                    "pyrotest1",
                    "pyrotest2"
                ]
            },
            {
                "label": "group_2",
                "Name": "pyrogroup2",
                "Users": [
                    "pyrotest2"
                ]
            }
        ],
        "Devices": [
            {
                "label": "test_fs",
                "Path": "",
                "Partition": 0,
                "Mountpoint": "/tmp/pyrotest",
                "State": [
                    "dir,/tmp/pyrotest,root,root,0755",
                    "dir,/tmp/pyrotest/data,pyrotest1,pyrogroup1,0750",
                    "dir,/tmp/pyrotest/logs,root,pyrogroup1,0775",
                    "fl,/tmp/pyrotest/README,pyrotest1,pyrogroup1,0644",
                    "ln,/tmp/pyrotest/readme_shortcut,pyrotest1,pyrogroup1,0777,/tmp/pyrotest/README"
                ]
            }
        ]
    }

    # Assuming you have a system_state from the previous script
    # system_state = get_complete_system_state()

    # For demonstration, create a mock system state
    system_state = {
        'users': [],
        'groups': [],
        'mounted_devices': []
    }

    # Compare and generate report
    differences = compare_system_state_with_pyro_file(system_state, config)
    report = generate_difference_report(differences)
    print(report)

    # Save detailed differences to JSON
    with open('system_state_differences.json', 'w') as f:
        json.dump(differences, f, indent=2, default=str)
    print("\nDetailed differences saved to system_state_differences.json")
