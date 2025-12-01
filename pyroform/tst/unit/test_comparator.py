"""
System State Comparator Test Suite

Unit tests for the system state Comparator class.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Optional

from pyroform.src.comparator import SystemStateComparator
from pyroform.src.models import (
    PyroConfig, User, Group, Device, Exclude,
    SystemUser, SystemGroup, MountedDevice, FileSystemEntry
)


@pytest.fixture
def mock_stdout():
    """Mock STDOUTMsg to avoid console output during tests."""
    mock = Mock()
    mock.info = Mock()
    mock.debug = Mock()
    mock.warn = Mock()
    mock.err = Mock()
    return mock


@pytest.fixture
def comparator(mock_stdout):
    """Create SystemStateComparator with mocked stdout."""
    return SystemStateComparator(stdout=mock_stdout)


@pytest.fixture
def pyro_config():
    """Create a mock PyroConfig."""
    config = Mock(spec=PyroConfig)
    config.users = []
    config.groups = []
    config.devices = []
    config.excludes = None
    return config


@pytest.fixture
def mock_excludes():
    """Create mock Exclude object."""
    excludes = Mock(spec=Exclude)
    excludes.users = {"excluded_user"}
    excludes.groups = {"excluded_group"}
    excludes.devices = {"/dev/excluded"}
    excludes.directories = {"/tmp/excluded"}
    excludes.files = {"/etc/excluded.txt"}
    excludes.links = {"/etc/link_excluded"}
    return excludes


@pytest.fixture
def system_state():
    """Create a sample system state dictionary."""
    return {
        'users': [
            {
                'username': 'existing_user',
                'uid': 1000,
                'gid': 1000,
                'home_directory': '/home/existing_user',
                'shell': '/bin/bash',
                'gecos': 'Existing User',
                'groups': ['wheel', 'audio']
            }
        ],
        'groups': [
            {
                'groupname': 'existing_group',
                'gid': 1000,
                'members': ['existing_user']
            }
        ],
        'mounted_devices': [
            {
                'device_path': '/dev/sda1',
                'mountpoint': '/',
                'filesystem_type': 'ext4',
                'mount_options': '',
                'partition': 'sda1',
                'partitions': [],
                'files': [
                    {
                        'path': '/etc/hosts',
                        'owner': 'root',
                        'group': 'root',
                        'permissions': '0644',
                        'mountpoint': '/'
                    }
                ],
                'directories': [
                    {
                        'path': '/etc',
                        'owner': 'root',
                        'group': 'root',
                        'permissions': '0755',
                        'mountpoint': '/'
                    }
                ],
                'symlinks': [
                    {
                        'path': '/etc/localtime',
                        'owner': 'root',
                        'group': 'root',
                        'permissions': '0777',
                        'mountpoint': '/',
                        'target': '/usr/share/zoneinfo/UTC'
                    }
                ]
            }
        ]
    }


@pytest.fixture
def minimal_system_state():
    """Create a minimal system state."""
    return {
        'users': [],
        'groups': [],
        'mounted_devices': []
    }


@pytest.fixture
def mock_user():
    """Create a mock User."""
    user = Mock(spec=User)
    user.name = "testuser"
    user.label = "testuser_label"
    user.password = "x"
    user.groups = ["wheel", "audio"]
    return user


@pytest.fixture
def mock_group():
    """Create a mock Group."""
    group = Mock(spec=Group)
    group.name = "testgroup"
    group.label = "testgroup_label"
    group.users = ["testuser"]
    return group


@pytest.fixture
def mock_device():
    """Create a mock Device."""
    device = Mock(spec=Device)
    device.label = "root_device"
    device.device_path = "/dev/sda1"
    device.mountpoint = "/"
    device.state = [
        "dir,/etc,root,root,0755",
        "fl,/etc/hosts,root,root,0644",
        "ln,/etc/localtime,root,root,0777,/usr/share/zoneinfo/UTC"
    ]
    return device


class TestSystemStateComparatorInitialization:
    """Test SystemStateComparator initialization."""

    def test_init_with_stdout(self, mock_stdout):
        """Test initialization with stdout dependency."""
        comparator = SystemStateComparator(stdout=mock_stdout)
        assert comparator.stdout == mock_stdout

    def test_init_stdout_required(self):
        """Test that stdout is required."""
        with pytest.raises(TypeError):
            SystemStateComparator()


class TestCompareStates:
    """Test the main compare_states method."""

    def test_compare_states_basic(self, comparator, pyro_config, minimal_system_state, mock_stdout):
        """Test basic comparison with empty config and state."""
        result = comparator.compare_states(minimal_system_state, pyro_config)

        assert isinstance(result, dict)
        assert len(result) == 0  # No differences
        mock_stdout.info.assert_called_once_with(
            'Comparing current system state with Pyro file...'
        )

    def test_compare_states_with_users(self, comparator, pyro_config, system_state):
        """Test comparison with user configuration."""
        user = Mock(spec=User)
        user.name = "new_user"
        user.label = "new_user_label"
        user.password = "x"
        user.groups = []
        pyro_config.users = [user]

        result = comparator.compare_states(system_state, pyro_config)

        assert 'missing_users' in result
        assert len(result['missing_users']) == 1
        assert result['missing_users'][0]['username'] == "new_user"

    def test_compare_states_with_groups(self, comparator, pyro_config, system_state):
        """Test comparison with group configuration."""
        group = Mock(spec=Group)
        group.name = "new_group"
        group.label = "new_group_label"
        group.users = []
        pyro_config.groups = [group]

        result = comparator.compare_states(system_state, pyro_config)

        assert 'missing_groups' in result
        assert len(result['missing_groups']) == 1
        assert result['missing_groups'][0]['groupname'] == "new_group"

    def test_compare_states_with_devices(self, comparator, pyro_config, system_state):
        """Test comparison with device configuration."""
        device = Mock(spec=Device)
        device.label = "test_device"
        device.device_path = "/dev/sdb1"
        device.mountpoint = "/mnt/data"
        device.state = ["dir,/mnt/data/test,root,root,0755"]
        pyro_config.devices = [device]

        result = comparator.compare_states(system_state, pyro_config)

        assert 'missing_mountpoints' in result
        assert len(result['missing_mountpoints']) == 1
        assert result['missing_mountpoints'][0]['mountpoint'] == "/mnt/data"

    def test_compare_states_empty_difference_categories_removed(self, comparator, mock_stdout):
        """Test that empty difference categories are removed from output."""
        system_state = {
            'users': [],
            'groups': [],
            'mounted_devices': []
        }

        config = Mock(spec=PyroConfig)
        config.users = []
        config.groups = []
        config.devices = []
        config.excludes = None

        result = comparator.compare_states(system_state, config)

        # Should not contain any empty lists
        for key, value in result.items():
            assert value != []

        # Verify debug output was called with sanitized dictionary
        mock_stdout.debug.assert_called_once()
        debug_call = mock_stdout.debug.call_args[0][0]
        assert "Differences:" in debug_call

    def test_compare_states_all_config_none(self, comparator, pyro_config, system_state):
        """Test comparison when all config sections are None."""
        pyro_config.users = None
        pyro_config.groups = None
        pyro_config.devices = None

        result = comparator.compare_states(system_state, pyro_config)

        # Should return empty dict
        assert result == {}

    def test_compare_states_debug_output(self, comparator, mock_stdout, system_state, pyro_config):
        """Test debug output formatting."""
        result = comparator.compare_states(system_state, pyro_config)

        # Verify debug output contains JSON
        mock_stdout.debug.assert_called_once()
        debug_arg = mock_stdout.debug.call_args[0][0]
        assert debug_arg.startswith("Differences: ")
        assert json.dumps(result) in debug_arg


class TestInitializeDifferencesDict:
    """Test the _initialize_differences_dict method."""

#   # TODO
#   def test_initialize_differences_dict(self, comparator):
#       """Test dictionary initialization."""


class TestBuildFilesystemState:
    """Test the _build_filesystem_state method."""

#   # TODO
#   def test_build_filesystem_state_multiple_mountpoints(self, comparator):
#       """Test building filesystem state with multiple mountpoints."""

    def test_build_filesystem_state_empty(self, comparator):
        """Test building filesystem state with empty system state."""
        system_state = {
            'mounted_devices': []
        }

        result = comparator._build_filesystem_state(system_state)

        assert result == {}

    def test_build_filesystem_state_with_entries(self, comparator):
        """Test building filesystem state with all entry types."""
        system_state = {
            'mounted_devices': [
                {
                    'mountpoint': '/',
                    'directories': [
                        {'path': '/etc', 'owner': 'root', 'group': 'root',
                         'permissions': '0755', 'mountpoint': '/'}
                    ],
                    'files': [
                        {'path': '/etc/hosts', 'owner': 'root', 'group': 'root',
                         'permissions': '0644', 'mountpoint': '/'}
                    ],
                    'symlinks': [
                        {'path': '/etc/localtime', 'owner': 'root', 'group': 'root',
                         'permissions': '0777', 'mountpoint': '/', 'target': 'UTC'}
                    ]
                }
            ]
        }

        result = comparator._build_filesystem_state(system_state)

        assert len(result) == 3
        assert '/etc' in result
        assert '/etc/hosts' in result
        assert '/etc/localtime' in result

        assert result['/etc']['type'] == 'directory'
        assert result['/etc/hosts']['type'] == 'file'
        assert result['/etc/localtime']['type'] == 'symlink'
        assert result['/etc/localtime']['target'] == 'UTC'

    def test_add_filesystem_entries(self, comparator):
        """Test _add_filesystem_entries helper method."""
        fs_state = {}

        entries = [
            {'path': '/test', 'owner': 'root', 'group': 'root',
             'permissions': '0755', 'mountpoint': '/'}
        ]

        comparator._add_filesystem_entries(entries, 'directory', '/', fs_state)

        assert '/test' in fs_state
        assert fs_state['/test']['type'] == 'directory'
        assert fs_state['/test']['owner'] == 'root'
        assert fs_state['/test']['group'] == 'root'
        assert fs_state['/test']['permissions'] == '0755'
        assert fs_state['/test']['mountpoint'] == '/'

    def test_add_filesystem_entries_symlink_with_target(self, comparator):
        """Test adding symlink entries with target."""
        fs_state = {}

        entries = [
            {'path': '/link', 'owner': 'root', 'group': 'root',
             'permissions': '0777', 'mountpoint': '/', 'target': '/target'}
        ]

        comparator._add_filesystem_entries(entries, 'symlink', '/', fs_state)

        assert fs_state['/link']['target'] == '/target'


class TestUserComparison:
    """Test user comparison methods."""

#   # TODO
#   def test_compare_users_no_config_users(self, comparator):
#       """Test comparison when config_users is None."""

    def test_compare_users_basic(self, comparator, mock_user):
        """Test basic user comparison."""
        config_users = [mock_user]
        current_users = []
        differences = comparator._initialize_differences_dict()

        comparator._compare_users(config_users, current_users, differences, None)

        assert len(differences['missing_users']) == 1
        assert differences['missing_users'][0]['username'] == "testuser"
        assert len(differences['extra_users']) == 0

    def test_compare_users_existing(self, comparator, mock_user):
        """Test comparison with existing user."""
        config_users = [mock_user]
        current_users = [
            {
                'username': 'testuser',
                'uid': 1000,
                'gid': 1000,
                'home_directory': '/home/testuser',
                'shell': '/bin/bash',
                'gecos': 'Test User',
                'groups': ['wheel', 'audio']
            }
        ]
        differences = comparator._initialize_differences_dict()

        comparator._compare_users(config_users, current_users, differences, None)

        # Should have no missing users
        assert len(differences['missing_users']) == 0
        # Should have no mismatches since groups match
        assert len(differences['user_mismatches']) == 0

    def test_compare_users_with_mismatch(self, comparator, mock_user):
        """Test comparison with user property mismatch."""
        config_users = [mock_user]
        # Current user has different groups
        current_users = [
            {
                'username': 'testuser',
                'uid': 1000,
                'gid': 1000,
                'home_directory': '/home/testuser',
                'shell': '/bin/bash',
                'gecos': 'Test User',
                'groups': ['wheel']  # Missing 'audio' group
            }
        ]
        differences = comparator._initialize_differences_dict()

        comparator._compare_users(config_users, current_users, differences, None)

        assert len(differences['user_mismatches']) == 1
        mismatch = differences['user_mismatches'][0]
        assert mismatch['username'] == 'testuser'
        assert len(mismatch['mismatches']) == 1
        assert mismatch['mismatches'][0]['property'] == 'groups'

    def test_compare_users_extra_user(self, comparator):
        """Test detection of extra users."""
        config_users = []
        current_users = [
            {
                'username': 'extra_user',
                'uid': 1001,
                'gid': 1001,
                'home_directory': '/home/extra'
            }
        ]
        differences = comparator._initialize_differences_dict()

        comparator._compare_users(config_users, current_users, differences, None)

        assert len(differences['extra_users']) == 1
        assert differences['extra_users'][0]['username'] == 'extra_user'

    def test_compare_users_with_excludes(self, comparator, mock_user, mock_excludes):
        """Test user comparison with excludes."""
        excluded_user = Mock(spec=User)
        excluded_user.name = "excluded_user"
        excluded_user.label = "excluded_label"
        excluded_user.password = "x"
        excluded_user.groups = []

        config_users = [excluded_user, mock_user]
        current_users = []
        differences = comparator._initialize_differences_dict()

        comparator._compare_users(config_users, current_users, differences, mock_excludes)

        # Only testuser should be in missing users (excluded_user should be skipped)
        assert len(differences['missing_users']) == 1
        assert differences['missing_users'][0]['username'] == "testuser"

    def test_check_user_compliance_missing(self, comparator, mock_user):
        """Test _check_user_compliance with missing user."""
        current_users = {}
        differences = comparator._initialize_differences_dict()

        comparator._check_user_compliance(mock_user, current_users, differences)

        assert len(differences['missing_users']) == 1
        missing = differences['missing_users'][0]
        assert missing['username'] == 'testuser'
        assert missing['label'] == 'testuser_label'

    def test_check_user_compliance_exists(self, comparator, mock_user):
        """Test _check_user_compliance with existing user."""
        current_users = {'testuser': {'username': 'testuser', 'groups': []}}
        differences = comparator._initialize_differences_dict()

        with patch.object(comparator, '_check_user_properties') as mock_check:
            comparator._check_user_compliance(mock_user, current_users, differences)

            mock_check.assert_called_once_with(mock_user, current_users['testuser'], differences)

    def test_check_user_properties_no_mismatch(self, comparator, mock_user):
        """Test _check_user_properties with no mismatches."""
        current_user = {'groups': ['wheel', 'audio']}
        differences = comparator._initialize_differences_dict()

        comparator._check_user_properties(mock_user, current_user, differences)

        assert len(differences['user_mismatches']) == 0

    def test_check_user_properties_with_mismatch(self, comparator, mock_user):
        """Test _check_user_properties with group mismatch."""
        current_user = {'groups': ['wheel']}  # Missing 'audio'
        differences = comparator._initialize_differences_dict()

        comparator._check_user_properties(mock_user, current_user, differences)

        assert len(differences['user_mismatches']) == 1
        mismatch = differences['user_mismatches'][0]
        assert mismatch['username'] == 'testuser'
        assert mismatch['mismatches'][0]['property'] == 'groups'
        assert 'audio' in mismatch['mismatches'][0]['missing']

    def test_find_extra_users(self, comparator):
        """Test _find_extra_users method."""
        config_user_names = {'user1', 'user2'}
        current_users = {
            'user1': {'username': 'user1', 'uid': 1000, 'home_directory': '/home/user1'},
            'user3': {'username': 'user3', 'uid': 1002, 'home_directory': '/home/user3'},
            'user4': {'username': 'user4', 'uid': 1003, 'home_directory': '/home/user4'}
        }
        differences = comparator._initialize_differences_dict()

        comparator._find_extra_users(config_user_names, current_users, differences, None)

        assert len(differences['extra_users']) == 2
        extra_usernames = {u['username'] for u in differences['extra_users']}
        assert 'user3' in extra_usernames
        assert 'user4' in extra_usernames

    def test_find_extra_users_with_excludes(self, comparator, mock_excludes):
        """Test _find_extra_users with excluded users."""
        config_user_names = {'user1'}
        current_users = {
            'user1': {'username': 'user1', 'uid': 1000},
            'excluded_user': {'username': 'excluded_user', 'uid': 1001}
        }
        differences = comparator._initialize_differences_dict()

        comparator._find_extra_users(config_user_names, current_users, differences, mock_excludes)

        # excluded_user should not be in extra_users
        assert len(differences['extra_users']) == 0


class TestGroupComparison:
    """Test group comparison methods."""

    def test_compare_groups_basic(self, comparator, mock_group):
        """Test basic group comparison."""
        config_groups = [mock_group]
        current_groups = []
        differences = comparator._initialize_differences_dict()

        comparator._compare_groups(config_groups, current_groups, differences, None)

        assert len(differences['missing_groups']) == 1
        assert differences['missing_groups'][0]['groupname'] == "testgroup"

    def test_compare_groups_existing(self, comparator, mock_group):
        """Test comparison with existing group."""
        config_groups = [mock_group]
        current_groups = [
            {'groupname': 'testgroup', 'gid': 1000, 'members': ['testuser']}
        ]
        differences = comparator._initialize_differences_dict()

        comparator._compare_groups(config_groups, current_groups, differences, None)

        assert len(differences['missing_groups']) == 0
        assert len(differences['group_mismatches']) == 0

    def test_compare_groups_with_mismatch(self, comparator, mock_group):
        """Test comparison with group property mismatch."""
        config_groups = [mock_group]
        # Current group has different members
        current_groups = [
            {'groupname': 'testgroup', 'gid': 1000, 'members': []}  # Missing 'testuser'
        ]
        differences = comparator._initialize_differences_dict()

        comparator._compare_groups(config_groups, current_groups, differences, None)

        assert len(differences['group_mismatches']) == 1
        mismatch = differences['group_mismatches'][0]
        assert mismatch['groupname'] == 'testgroup'
        assert mismatch['mismatches'][0]['property'] == 'members'

    def test_compare_groups_extra_group(self, comparator):
        """Test detection of extra groups."""
        config_groups = []
        current_groups = [
            {'groupname': 'extra_group', 'gid': 1001, 'members': []}
        ]
        differences = comparator._initialize_differences_dict()

        comparator._compare_groups(config_groups, current_groups, differences, None)

        assert len(differences['extra_groups']) == 1
        assert differences['extra_groups'][0]['groupname'] == 'extra_group'

    def test_compare_groups_with_excludes(self, comparator, mock_group, mock_excludes):
        """Test group comparison with excludes."""
        excluded_group = Mock(spec=Group)
        excluded_group.name = "excluded_group"
        excluded_group.label = "excluded_label"
        excluded_group.users = []

        config_groups = [excluded_group, mock_group]
        current_groups = []
        differences = comparator._initialize_differences_dict()

        comparator._compare_groups(config_groups, current_groups, differences, mock_excludes)

        # Only testgroup should be in missing groups
        assert len(differences['missing_groups']) == 1
        assert differences['missing_groups'][0]['groupname'] == "testgroup"

    def test_check_group_compliance_missing(self, comparator, mock_group):
        """Test _check_group_compliance with missing group."""
        current_groups = {}
        differences = comparator._initialize_differences_dict()

        comparator._check_group_compliance(mock_group, current_groups, differences)

        assert len(differences['missing_groups']) == 1
        missing = differences['missing_groups'][0]
        assert missing['groupname'] == 'testgroup'
        assert missing['label'] == 'testgroup_label'

    def test_check_group_properties_no_mismatch(self, comparator, mock_group):
        """Test _check_group_properties with no mismatches."""
        current_group = {'members': ['testuser']}
        differences = comparator._initialize_differences_dict()

        comparator._check_group_properties(mock_group, current_group, differences)

        assert len(differences['group_mismatches']) == 0

    def test_check_group_properties_with_mismatch(self, comparator, mock_group):
        """Test _check_group_properties with member mismatch."""
        current_group = {'members': []}  # Missing 'testuser'
        differences = comparator._initialize_differences_dict()

        comparator._check_group_properties(mock_group, current_group, differences)

        assert len(differences['group_mismatches']) == 1
        mismatch = differences['group_mismatches'][0]
        assert mismatch['groupname'] == 'testgroup'
        assert 'testuser' in mismatch['mismatches'][0]['missing']


class TestFilesystemComparison:
    """Test filesystem comparison methods."""

#   # TODO
#   def test_compare_filesystem_with_excludes(self, comparator, mock_device, mock_excludes):
#       """Test filesystem comparison with excluded device."""
#   def test_check_device_contents(self, comparator, mock_device):
#       """Test _check_device_contents."""
#   def test_check_item_properties_type_mismatch(self, comparator):
#       """Test _check_item_properties with type mismatch."""

    def test_compare_filesystem_basic(self, comparator, mock_device):
        """Test basic filesystem comparison."""
        config_devices = [mock_device]
        current_fs_state = {}
        differences = comparator._initialize_differences_dict()

        with patch.object(comparator, '_check_mountpoint') as mock_check_mount, \
             patch.object(comparator, '_check_device_contents') as mock_check_contents:
            comparator._compare_filesystem(config_devices, current_fs_state, differences, None)

            mock_check_mount.assert_called_once_with(mock_device, current_fs_state, differences)
            mock_check_contents.assert_called_once()

    def test_check_mountpoint_exists(self, comparator, mock_device):
        """Test _check_mountpoint when mountpoint exists."""
        current_fs_state = {
            '/path1': {'mountpoint': '/', 'type': 'directory'},
            '/path2': {'mountpoint': '/mnt', 'type': 'directory'}
        }
        mock_device.mountpoint = '/'
        differences = comparator._initialize_differences_dict()

        comparator._check_mountpoint(mock_device, current_fs_state, differences)

        assert len(differences['missing_mountpoints']) == 0

    def test_check_mountpoint_missing(self, comparator, mock_device):
        """Test _check_mountpoint when mountpoint is missing."""
        current_fs_state = {
            '/path1': {'mountpoint': '/', 'type': 'directory'}
        }
        mock_device.mountpoint = '/mnt/data'
        differences = comparator._initialize_differences_dict()

        comparator._check_mountpoint(mock_device, current_fs_state, differences)

        assert len(differences['missing_mountpoints']) == 1
        missing = differences['missing_mountpoints'][0]
        assert missing['mountpoint'] == '/mnt/data'
        assert missing['label'] == 'root_device'

    def test_check_mountpoint_none(self, comparator, mock_device):
        """Test _check_mountpoint when mountpoint is None."""
        mock_device.mountpoint = None
        differences = comparator._initialize_differences_dict()

        comparator._check_mountpoint(mock_device, {}, differences)

        # Should not add anything
        assert len(differences['missing_mountpoints']) == 0

    def test_check_device_contents_excluded(self, comparator, mock_device):
        """Test _check_device_contents with excluded item."""
        current_fs_state = {}
        differences = comparator._initialize_differences_dict()
        config_paths = set()

        with patch.object(comparator, '_parse_config_state_entry') as mock_parse, \
             patch.object(comparator, '_should_exclude') as mock_should_exclude:

            mock_parse.return_value = {'type': 'dir', 'path': '/test'}
            mock_should_exclude.return_value = True  # Excluded

            comparator._check_device_contents(
                mock_device, current_fs_state, differences, config_paths, None
            )

            # Should not add to config_paths or check compliance
            assert '/test' not in config_paths

    def test_check_device_contents_invalid_entry(self, comparator, mock_device):
        """Test _check_device_contents with invalid entry."""
        current_fs_state = {}
        differences = comparator._initialize_differences_dict()
        config_paths = set()

        with patch.object(comparator, '_parse_config_state_entry') as mock_parse:
            mock_parse.return_value = None  # Invalid entry

            comparator._check_device_contents(
                mock_device, current_fs_state, differences, config_paths, None
            )

            # Should not add anything
            assert len(config_paths) == 0

    def test_check_filesystem_item_compliance_missing(self, comparator):
        """Test _check_filesystem_item_compliance with missing item."""
        config_item = {'type': 'dir', 'path': '/missing'}
        current_fs_state = {}
        differences = comparator._initialize_differences_dict()

        with patch.object(comparator, '_handle_missing_item') as mock_handle:
            comparator._check_filesystem_item_compliance(
                config_item, current_fs_state, differences
            )

            mock_handle.assert_called_once_with(config_item, differences)

    def test_check_filesystem_item_compliance_exists(self, comparator):
        """Test _check_filesystem_item_compliance with existing item."""
        config_item = {'type': 'dir', 'path': '/existing'}
        current_fs_state = {'/existing': {'type': 'directory'}}
        differences = comparator._initialize_differences_dict()

        with patch.object(comparator, '_check_item_properties') as mock_check_props:
            comparator._check_filesystem_item_compliance(
                config_item, current_fs_state, differences
            )

            mock_check_props.assert_called_once_with(
                config_item, current_fs_state['/existing'], differences
            )

    def test_handle_missing_item_directory(self, comparator):
        """Test _handle_missing_item for directory."""
        config_item = {'type': 'dir', 'path': '/missing_dir'}
        differences = comparator._initialize_differences_dict()

        comparator._handle_missing_item(config_item, differences)

        assert len(differences['missing_directories']) == 1
        assert differences['missing_directories'][0]['path'] == '/missing_dir'

    def test_handle_missing_item_file(self, comparator):
        """Test _handle_missing_item for file."""
        config_item = {'type': 'fl', 'path': '/missing_file'}
        differences = comparator._initialize_differences_dict()

        comparator._handle_missing_item(config_item, differences)

        assert len(differences['missing_files']) == 1
        assert differences['missing_files'][0]['path'] == '/missing_file'

    def test_handle_missing_item_symlink(self, comparator):
        """Test _handle_missing_item for symlink."""
        config_item = {'type': 'ln', 'path': '/missing_link'}
        differences = comparator._initialize_differences_dict()

        comparator._handle_missing_item(config_item, differences)

        assert len(differences['missing_symlinks']) == 1
        assert differences['missing_symlinks'][0]['path'] == '/missing_link'

    def test_check_item_properties_no_mismatch(self, comparator):
        """Test _check_item_properties with no mismatches."""
        config_item = {
            'type': 'dir',
            'path': '/test',
            'owner': 'root',
            'group': 'root',
            'permissions': '0755'
        }
        current_item = {
            'type': 'directory',
            'owner': 'root',
            'group': 'root',
            'permissions': '0755'
        }
        differences = comparator._initialize_differences_dict()

        comparator._check_item_properties(config_item, current_item, differences)

        # Should have no mismatches
        assert len(differences['directory_mismatches']) == 0

    def test_check_item_properties_with_mismatches(self, comparator):
        """Test _check_item_properties with property mismatches."""
        config_item = {
            'type': 'fl',
            'path': '/test.txt',
            'owner': 'root',
            'group': 'root',
            'permissions': '0644'
        }
        current_item = {
            'type': 'file',
            'owner': 'user',  # Different owner
            'group': 'user',  # Different group
            'permissions': '0644'
        }
        differences = comparator._initialize_differences_dict()

        comparator._check_item_properties(config_item, current_item, differences)

        assert len(differences['file_mismatches']) == 1
        mismatch = differences['file_mismatches'][0]
        assert len(mismatch['mismatches']) == 2  # owner and group mismatches

    def test_check_item_properties_symlink_target_mismatch(self, comparator):
        """Test _check_item_properties with symlink target mismatch."""
        config_item = {
            'type': 'ln',
            'path': '/link',
            'owner': 'root',
            'group': 'root',
            'permissions': '0777',
            'target': '/target1'
        }
        current_item = {
            'type': 'symlink',
            'owner': 'root',
            'group': 'root',
            'permissions': '0777',
            'target': '/target2'  # Different target
        }
        differences = comparator._initialize_differences_dict()

        comparator._check_item_properties(config_item, current_item, differences)

        mismatch = differences['symlink_mismatches'][0]
        target_mismatch = next(
            m for m in mismatch['mismatches'] if m['property'] == 'target'
        )
        assert target_mismatch['expected'] == '/target1'
        assert target_mismatch['actual'] == '/target2'


class TestFindPropertyMismatches:
    """Test the _find_property_mismatches method."""

#   # TODO
#   def test_find_property_mismatches_type(self, comparator):
#       """Test type mismatch detection."""
#   def test_find_property_mismatches_owner(self, comparator):
#       """Test owner mismatch detection."""
#   def test_find_property_mismatches_group(self, comparator):
#       """Test group mismatch detection."""
#   def test_find_property_mismatches_permissions(self, comparator):
#       """Test permissions mismatch detection."""
#   def test_find_property_mismatches_unknown_type(self, comparator):
#       """Test with unknown type mapping."""


    def test_find_property_mismatches_none(self, comparator):
        """Test with no mismatches."""
        config_item = {
            'type': 'dir',
            'owner': 'root',
            'group': 'root',
            'permissions': '0755'
        }
        current_item = {
            'type': 'directory',
            'owner': 'root',
            'group': 'root',
            'permissions': '0755'
        }

        mismatches = comparator._find_property_mismatches(config_item, current_item)

        assert len(mismatches) == 0

    def test_find_property_mismatches_symlink_target(self, comparator):
        """Test symlink target mismatch detection."""
        config_item = {
            'type': 'ln',
            'owner': 'root',
            'group': 'root',
            'permissions': '0777',
            'target': '/target1'
        }
        current_item = {
            'type': 'symlink',
            'owner': 'root',
            'group': 'root',
            'permissions': '0777',
            'target': '/target2'
        }

        mismatches = comparator._find_property_mismatches(config_item, current_item)

        assert len(mismatches) == 1
        assert mismatches[0]['property'] == 'target'

    def test_find_property_mismatches_multiple(self, comparator):
        """Test multiple property mismatches."""
        config_item = {
            'type': 'fl',
            'owner': 'root',
            'group': 'root',
            'permissions': '0644'
        }
        current_item = {
            'type': 'file',
            'owner': 'user',
            'group': 'user',
            'permissions': '0755'
        }

        mismatches = comparator._find_property_mismatches(config_item, current_item)

        assert len(mismatches) == 3
        properties = {m['property'] for m in mismatches}
        assert properties == {'owner', 'group', 'permissions'}


class TestCategorizeMismatch:
    """Test the _categorize_mismatch method."""

    def test_categorize_mismatch_directory(self, comparator):
        """Test categorizing directory mismatch."""
        differences = comparator._initialize_differences_dict()
        mismatch_entry = {'path': '/test', 'mismatches': []}

        comparator._categorize_mismatch('dir', mismatch_entry, differences)

        assert len(differences['directory_mismatches']) == 1
        assert differences['directory_mismatches'][0]['path'] == '/test'

    def test_categorize_mismatch_file(self, comparator):
        """Test categorizing file mismatch."""
        differences = comparator._initialize_differences_dict()
        mismatch_entry = {'path': '/test.txt', 'mismatches': []}

        comparator._categorize_mismatch('fl', mismatch_entry, differences)

        assert len(differences['file_mismatches']) == 1
        assert differences['file_mismatches'][0]['path'] == '/test.txt'

    def test_categorize_mismatch_symlink(self, comparator):
        """Test categorizing symlink mismatch."""
        differences = comparator._initialize_differences_dict()
        mismatch_entry = {'path': '/link', 'mismatches': []}

        comparator._categorize_mismatch('ln', mismatch_entry, differences)

        assert len(differences['symlink_mismatches']) == 1
        assert differences['symlink_mismatches'][0]['path'] == '/link'

    def test_categorize_mismatch_unknown_type(self, comparator):
        """Test categorizing unknown type mismatch."""
        differences = comparator._initialize_differences_dict()

        # Should not raise error
        comparator._categorize_mismatch('unknown', {}, differences)

        # Should not add to any category
        for key in differences:
            if key.endswith('_mismatches'):
                assert len(differences[key]) == 0


class TestFindExtraFilesystemItems:
    """Test the _find_extra_filesystem_items method."""

    def test_find_extra_filesystem_items_empty(self, comparator):
        """Test with no extra items."""
        config_paths = {'/config1', '/config2'}
        current_fs_state = {
            '/config1': {'type': 'directory'},
            '/config2': {'type': 'file'}
        }
        differences = comparator._initialize_differences_dict()

        comparator._find_extra_filesystem_items(config_paths, current_fs_state, differences)

        # No extra items
        assert len(differences['extra_directories']) == 0
        assert len(differences['extra_files']) == 0
        assert len(differences['extra_symlinks']) == 0

    def test_find_extra_filesystem_items_directories(self, comparator):
        """Test finding extra directories."""
        config_paths = set()
        current_fs_state = {
            '/extra_dir': {
                'type': 'directory',
                'owner': 'user',
                'group': 'user',
                'permissions': '0755'
            }
        }
        differences = comparator._initialize_differences_dict()

        comparator._find_extra_filesystem_items(config_paths, current_fs_state, differences)

        assert len(differences['extra_directories']) == 1
        extra = differences['extra_directories'][0]
        assert extra['path'] == '/extra_dir'
        assert extra['owner'] == 'user'

    def test_find_extra_filesystem_items_files(self, comparator):
        """Test finding extra files."""
        config_paths = set()
        current_fs_state = {
            '/extra.txt': {
                'type': 'file',
                'owner': 'user',
                'group': 'user',
                'permissions': '0644'
            }
        }
        differences = comparator._initialize_differences_dict()

        comparator._find_extra_filesystem_items(config_paths, current_fs_state, differences)

        assert len(differences['extra_files']) == 1
        extra = differences['extra_files'][0]
        assert extra['path'] == '/extra.txt'

    def test_find_extra_filesystem_items_symlinks(self, comparator):
        """Test finding extra symlinks."""
        config_paths = set()
        current_fs_state = {
            '/extra_link': {
                'type': 'symlink',
                'owner': 'user',
                'group': 'user',
                'permissions': '0777',
                'target': '/target'
            }
        }
        differences = comparator._initialize_differences_dict()

        comparator._find_extra_filesystem_items(config_paths, current_fs_state, differences)

        assert len(differences['extra_symlinks']) == 1
        extra = differences['extra_symlinks'][0]
        assert extra['path'] == '/extra_link'
        assert extra['target'] == '/target'

    def test_find_extra_filesystem_items_broken_symlink(self, comparator):
        """Test finding extra broken symlinks."""
        config_paths = set()
        current_fs_state = {
            '/broken_link': {
                'type': 'symlink',
                'owner': 'user',
                'group': 'user',
                'permissions': '0777'
                # No target
            }
        }
        differences = comparator._initialize_differences_dict()

        comparator._find_extra_filesystem_items(config_paths, current_fs_state, differences)

        extra = differences['extra_symlinks'][0]
        assert 'target' not in extra or extra.get('target') == 'broken'


class TestParseConfigStateEntry:
    """Test the _parse_config_state_entry method."""

    def test_parse_config_state_entry_directory(self, comparator):
        """Test parsing directory entry."""
        entry = "dir,/etc,root,root,0755"

        result = comparator._parse_config_state_entry(entry)

        assert result is not None
        assert result['type'] == 'dir'
        assert result['path'] == '/etc'
        assert result['owner'] == 'root'
        assert result['group'] == 'root'
        assert result['permissions'] == '0755'

    def test_parse_config_state_entry_file(self, comparator):
        """Test parsing file entry."""
        entry = "fl,/etc/hosts,root,root,0644"

        result = comparator._parse_config_state_entry(entry)

        assert result['type'] == 'fl'
        assert result['path'] == '/etc/hosts'

    def test_parse_config_state_entry_symlink(self, comparator):
        """Test parsing symlink entry with target."""
        entry = "ln,/etc/localtime,root,root,0777,/usr/share/zoneinfo/UTC"

        result = comparator._parse_config_state_entry(entry)

        assert result['type'] == 'ln'
        assert result['path'] == '/etc/localtime'
        assert result['target'] == '/usr/share/zoneinfo/UTC'

    def test_parse_config_state_entry_invalid(self, comparator):
        """Test parsing invalid entry."""
        # Too few parts
        entry = "dir,/etc,root"

        result = comparator._parse_config_state_entry(entry)

        assert result is None

    def test_parse_config_state_entry_empty(self, comparator):
        """Test parsing empty entry."""
        result = comparator._parse_config_state_entry("")

        assert result is None

    def test_parse_config_state_entry_extra_parts(self, comparator):
        """Test parsing entry with extra parts."""
        entry = "dir,/etc,root,root,0755,extra,more"

        result = comparator._parse_config_state_entry(entry)

        # Should still parse first 5 parts
        assert result is not None
        assert result['type'] == 'dir'
        assert result['path'] == '/etc'


class TestShouldExclude:
    """Test the _should_exclude method."""

#   # TODO
#   def test_should_exclude_empty_exclude_set(self, comparator):
#       """Test when exclude set is empty."""

    def test_should_exclude_no_excludes(self, comparator):
        """Test when excludes is None."""
        assert comparator._should_exclude('item', None, 'users') == False

    def test_should_exclude_user(self, comparator, mock_excludes):
        """Test excluding users."""
        assert comparator._should_exclude('excluded_user', mock_excludes, 'users') == True
        assert comparator._should_exclude('regular_user', mock_excludes, 'users') == False

    def test_should_exclude_group(self, comparator, mock_excludes):
        """Test excluding groups."""
        assert comparator._should_exclude('excluded_group', mock_excludes, 'groups') == True
        assert comparator._should_exclude('regular_group', mock_excludes, 'groups') == False

    def test_should_exclude_device(self, comparator, mock_excludes):
        """Test excluding devices."""
        assert comparator._should_exclude('/dev/excluded', mock_excludes, 'devices') == True
        assert comparator._should_exclude('/dev/regular', mock_excludes, 'devices') == False

    def test_should_exclude_directory(self, comparator, mock_excludes):
        """Test excluding directories."""
        assert comparator._should_exclude('/tmp/excluded', mock_excludes, 'dir') == True
        assert comparator._should_exclude('/tmp/regular', mock_excludes, 'dir') == False

    def test_should_exclude_file(self, comparator, mock_excludes):
        """Test excluding files."""
        assert comparator._should_exclude('/etc/excluded.txt', mock_excludes, 'fl') == True
        assert comparator._should_exclude('/etc/regular.txt', mock_excludes, 'fl') == False

    def test_should_exclude_link(self, comparator, mock_excludes):
        """Test excluding links."""
        assert comparator._should_exclude('/etc/link_excluded', mock_excludes, 'ln') == True
        assert comparator._should_exclude('/etc/link_regular', mock_excludes, 'ln') == False

    def test_should_exclude_unknown_type(self, comparator, mock_excludes):
        """Test with unknown exclude type."""
        assert comparator._should_exclude('item', mock_excludes, 'unknown') == False


class TestIntegration:
    """Integration tests for complete comparison scenarios."""

#   # TODO
#   def test_complete_comparison_scenario(self, comparator, mock_stdout):
#       """Test a complete comparison scenario."""
#   def test_comparison_with_all_exclusions(self, comparator, mock_excludes):
#       """Test comparison where everything is excluded."""


class TestEdgeCases:
    """Test edge cases and error handling."""

#   # TODO
#   def test_build_filesystem_state_none_entries(self, comparator):
#       """Test building filesystem state with None entries."""

    def test_compare_states_empty_system_state(self, comparator, pyro_config):
        """Test comparison with empty system state."""
        system_state = {}

        # Should handle gracefully
        result = comparator.compare_states(system_state, pyro_config)

        assert isinstance(result, dict)

    def test_compare_states_missing_keys(self, comparator, pyro_config):
        """Test comparison with missing system state keys."""
        system_state = {
            'users': []  # Missing 'groups' and 'mounted_devices'
        }

        # Should handle gracefully
        result = comparator.compare_states(system_state, pyro_config)

        assert isinstance(result, dict)

    def test_compare_states_none_values(self, comparator, pyro_config):
        """Test comparison with None values in system state."""
        system_state = {
            'users': None,
            'groups': None,
            'mounted_devices': None
        }

        # Should handle gracefully
        result = comparator.compare_states(system_state, pyro_config)

        assert isinstance(result, dict)

    def test_parse_config_state_entry_with_commas_in_path(self, comparator):
        """Test parsing entry with commas in path (should handle gracefully)."""
        entry = "dir,/path,with,commas,root,root,0755"

        result = comparator._parse_config_state_entry(entry)

        # Should parse first 5 parts
        assert result is not None
        assert result['type'] == 'dir'
        # Path would be "/path" which is incorrect, but that's expected behavior


if __name__ == "__main__":
    # This allows running the test file directly
    pytest.main([__file__, "-v", "--tb=short"])
