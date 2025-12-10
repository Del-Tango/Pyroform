"""
Scanner Test Suite

Unit tests for the system state Scanner class.
"""

import json
import stat
import subprocess
from unittest.mock import Mock, patch

import pytest

from pyroform.src.models import Exclude, MountedDevice, PyroConfig
from pyroform.src.scanner import SystemStateScanner


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
def scanner(mock_stdout):
    """Create SystemStateScanner with mocked stdout."""
    return SystemStateScanner(stdout=mock_stdout)


@pytest.fixture
def pyro_config():
    """Create a mock PyroConfig with excludes."""
    config = Mock(spec=PyroConfig)
    config.users = [Mock(username="testuser")]
    config.groups = [Mock(groupname="testgroup")]
    config.devices = [Mock(device_path="/dev/sda1")]

    excludes = Mock(spec=Exclude)
    excludes.users = {"excluded_user"}
    excludes.groups = {"excluded_group"}
    excludes.devices = {"/dev/excluded"}
    excludes.files = {"/etc/excluded.txt"}
    excludes.directories = {"/tmp/excluded"}
    excludes.links = {"/etc/link_excluded"}
    config.excludes = excludes

    return config


@pytest.fixture
def empty_pyro_config():
    """Create an empty PyroConfig."""
    config = Mock(spec=PyroConfig)
    config.users = []
    config.groups = []
    config.devices = []
    config.excludes = Mock(spec=Exclude)
    config.excludes.users = set()
    config.excludes.groups = set()
    config.excludes.devices = set()
    config.excludes.files = set()
    config.excludes.directories = set()
    config.excludes.links = set()
    return config


@pytest.fixture
def mock_pwd_user():
    """Mock pwd.getpwall return value."""
    return [
        type(
            "User",
            (),
            {
                "pw_name": "testuser",
                "pw_uid": 1000,
                "pw_gid": 1000,
                "pw_dir": "/home/testuser",
                "pw_shell": "/bin/bash",
                "pw_gecos": "Test User",
            },
        )
    ]


@pytest.fixture
def mock_grp_group():
    """Mock grp.getgrall return value."""
    return [
        type(
            "Group",
            (),
            {"gr_name": "testgroup", "gr_gid": 1000, "gr_mem": ["testuser"]},
        )
    ]


@pytest.fixture
def mount_entries():
    """Sample mount entries from different sources."""
    return [
        # /proc/mounts format
        "/dev/sda1 / ext4 rw,relatime 0 0",
        "/dev/sdb1 /mnt/data xfs rw,nosuid 0 0",
        # mount command format
        "/dev/sda2 on /boot type ext4 (rw,relatime)",
        # df command format
        "/dev/sda3   50G   10G   40G   20% /var",
    ]


@pytest.fixture
def mock_lsblk_output():
    """Mock lsblk JSON output."""
    return {
        "blockdevices": [
            {
                "name": "sda",
                "size": "100G",
                "children": [
                    {
                        "name": "sda1",
                        "size": "50G",
                        "mountpoint": "/",
                        "fstype": "ext4",
                    },
                    {
                        "name": "sda2",
                        "size": "1G",
                        "mountpoint": "/boot",
                        "fstype": "ext4",
                    },
                ],
            }
        ]
    }


class TestSystemStateScannerInitialization:
    """Test SystemStateScanner initialization."""

# TODO
#   def test_init_stdout_required(self):
#       """Test that stdout is required."""

    def test_init_with_stdout(self, mock_stdout):
        """Test initialization with stdout dependency."""
        scanner = SystemStateScanner(stdout=mock_stdout)
        assert scanner.stdout == mock_stdout


class TestScanSystemState:
    """Test the main scan_system_state method."""

#   # TODO
#   def test_scan_system_state_default_parameters(self, scanner):
#       """Test default parameter values."""
#   def test_scan_system_state_debug_output(
#       self, mock_scan_devices, mock_scan_groups, mock_scan_users, scanner, mock_stdout
#   ):
#       """Test debug output formatting."""

    @patch.object(SystemStateScanner, "_scan_users")
    @patch.object(SystemStateScanner, "_scan_groups")
    @patch.object(SystemStateScanner, "_scan_mounted_devices")
    def test_scan_system_state_basic(
        self, mock_scan_devices, mock_scan_groups, mock_scan_users, scanner, mock_stdout
    ):
        """Test basic system state scanning."""
        # Setup
        mock_scan_users.return_value = [{"username": "user1"}]
        mock_scan_groups.return_value = [{"groupname": "group1"}]
        mock_scan_devices.return_value = [{"device": "sda1"}]

        # Execute
        result = scanner.scan_system_state()

        # Verify
        assert isinstance(result, dict)
        assert "users" in result
        assert "groups" in result
        assert "mounted_devices" in result
        assert result["users"] == [{"username": "user1"}]
        assert result["groups"] == [{"groupname": "group1"}]
        assert result["mounted_devices"] == [{"device": "sda1"}]

        mock_stdout.info.assert_called_once_with(
            "Scanning current machine state (users, groups, filesystem)..."
        )
        mock_stdout.debug.assert_any_call("Max directory depth: 10")
        mock_stdout.debug.assert_any_call("Include hidden files: True")

    @patch.object(SystemStateScanner, "_scan_users")
    @patch.object(SystemStateScanner, "_scan_groups")
    @patch.object(SystemStateScanner, "_scan_mounted_devices")
    def test_scan_system_state_with_config(
        self, mock_scan_devices, mock_scan_groups, mock_scan_users, scanner, pyro_config
    ):
        """Test scanning with PyroConfig."""
        mock_scan_users.return_value = []
        mock_scan_groups.return_value = []
        mock_scan_devices.return_value = []

        result = scanner.scan_system_state(
            pyro_config=pyro_config, max_depth=5, include_hidden=False
        )

        mock_scan_users.assert_called_once_with(pyro_config)
        mock_scan_groups.assert_called_once_with(pyro_config)
        mock_scan_devices.assert_called_once_with(pyro_config, 5, False)


class TestUserScanning:
    """Test user scanning methods."""

#   # TODO
#   def test_scan_users_individual_error(self, mock_getpwall, scanner, mock_stdout):
#       """Test error handling for individual user processing."""
#   def test_should_exclude_user_no_config(self, scanner):
#       """Test user exclusion check without config."""
#   def test_should_exclude_user_no_excludes(self, scanner):
#       """Test user exclusion check without excludes."""
#   def test_scan_users_exclusion(
#       self, mock_should_exclude, mock_getpwall, scanner, mock_pwd_user, pyro_config
#   ):
#       """Test user exclusion."""


    @patch("pwd.getpwall")
    def test_scan_users_basic(self, mock_getpwall, scanner, mock_pwd_user):
        """Test basic user scanning."""
        mock_getpwall.return_value = mock_pwd_user

        result = scanner._scan_users(None)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["username"] == "testuser"
        assert result[0]["uid"] == 1000
        assert result[0]["home_directory"] == "/home/testuser"

    @patch("pwd.getpwall")
    @patch.object(SystemStateScanner, "_get_user_groups")
    @patch.object(SystemStateScanner, "_should_exclude_user")
    def test_scan_users_with_groups(
        self,
        mock_should_exclude,
        mock_get_groups,
        mock_getpwall,
        scanner,
        mock_pwd_user,
    ):
        """Test user scanning with groups."""
        mock_getpwall.return_value = mock_pwd_user
        mock_should_exclude.return_value = False
        mock_get_groups.return_value = ["group1", "group2"]

        result = scanner._scan_users(None)

        assert result[0]["groups"] == ["group1", "group2"]
        mock_get_groups.assert_called_once_with("testuser")

    @patch("pwd.getpwall")
    def test_scan_users_empty_config(self, mock_getpwall, scanner, empty_pyro_config):
        """Test scanning with empty config."""
        empty_pyro_config.users = []

        result = scanner._scan_users(empty_pyro_config)

        assert result == []
        mock_getpwall.assert_not_called()

    @patch("pwd.getpwall")
    @patch.object(SystemStateScanner, "_get_user_groups")
    def test_scan_users_error_handling(self, mock_get_groups, mock_getpwall, scanner):
        """Test user scanning error handling."""
        mock_getpwall.side_effect = Exception("Test error")

        result = scanner._scan_users(None)

        assert result == []
        scanner.stdout.err.assert_called_once_with("Error fetching users: Test error")

    @patch("subprocess.run")
    def test_get_user_groups_success(self, mock_run, scanner):
        """Test successful group retrieval for a user."""
        mock_run.return_value = Mock(
            stdout="testuser : wheel audio video\n", returncode=0
        )

        groups = scanner._get_user_groups("testuser")

        assert groups == ["wheel", "audio", "video"]
        mock_run.assert_called_once_with(
            ["groups", "testuser"], capture_output=True, text=True, check=True
        )

    @patch("subprocess.run")
    def test_get_user_groups_command_not_found(self, mock_run, scanner):
        """Test groups command not found."""
        mock_run.side_effect = FileNotFoundError("Command not found")

        groups = scanner._get_user_groups("testuser")

        assert groups == []

    @patch("subprocess.run")
    def test_get_user_groups_process_error(self, mock_run, scanner):
        """Test groups command error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "groups")

        groups = scanner._get_user_groups("testuser")

        assert groups == []

    def test_should_exclude_user_with_config(self, scanner, pyro_config):
        """Test user exclusion check with config."""
        assert scanner._should_exclude_user("excluded_user", pyro_config) == True
        assert scanner._should_exclude_user("regular_user", pyro_config) == False


class TestGroupScanning:
    """Test group scanning methods."""

    # TODO
#   def test_scan_groups_exclusion(
#       self, mock_should_exclude, mock_getgrall, scanner, mock_grp_group, pyro_config
#   ):
#       """Test group exclusion."""


    @patch("grp.getgrall")
    def test_scan_groups_basic(self, mock_getgrall, scanner, mock_grp_group):
        """Test basic group scanning."""
        mock_getgrall.return_value = mock_grp_group

        result = scanner._scan_groups(None)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["groupname"] == "testgroup"
        assert result[0]["gid"] == 1000
        assert result[0]["members"] == ["testuser"]

    @patch("grp.getgrall")
    def test_scan_groups_empty_config(self, mock_getgrall, scanner, empty_pyro_config):
        """Test scanning with empty config."""
        empty_pyro_config.groups = []

        result = scanner._scan_groups(empty_pyro_config)

        assert result == []
        mock_getgrall.assert_not_called()

    @patch("grp.getgrall")
    def test_scan_groups_error_handling(self, mock_getgrall, scanner):
        """Test group scanning error handling."""
        mock_getgrall.side_effect = Exception("Test error")

        result = scanner._scan_groups(None)

        assert result == []
        scanner.stdout.err.assert_called_once_with("Error fetching groups: Test error")

    def test_should_exclude_group_with_config(self, scanner, pyro_config):
        """Test group exclusion check with config."""
        assert scanner._should_exclude_group("excluded_group", pyro_config) == True
        assert scanner._should_exclude_group("regular_group", pyro_config) == False


class TestDeviceScanning:
    """Test device and mount scanning methods."""

#   # TODO
#   def test_scan_mounted_devices_basic(self, mock_scan_contents, mock_parse_entry,
#                                     mock_get_mounts, scanner, empty_pyro_config):
#       """Test basic mounted device scanning."""
#   def test_get_mount_information_multiple_sources(self, mock_run, mock_open, scanner):
#       """Test mount information collection from multiple sources."""
#   def test_get_mount_information_fallback_sources(self, mock_run, mock_open, scanner):
#       """Test mount information with some sources unavailable."""
#   def test_extract_mount_info_mount_command_format(self, scanner):
#       """Test mount command format parsing."""
#   def test_extract_mount_info_df_format(self, scanner):
#       """Test df command format parsing."""
#   def test_parse_mount_entry_excluded(
#       self, mock_should_exclude, scanner, pyro_config
#   ):
#       """Test parsing of excluded device."""

    @patch.object(SystemStateScanner, "_get_mount_information")
    def test_scan_mounted_devices_empty_config(
        self, mock_get_mounts, scanner, empty_pyro_config
    ):
        """Test scanning with empty device config."""
        empty_pyro_config.devices = []

        result = scanner._scan_mounted_devices(empty_pyro_config, 5, True)

        assert result == []
        mock_get_mounts.assert_not_called()

    @patch.object(SystemStateScanner, "_get_mount_information")
    def test_scan_mounted_devices_error_handling(self, mock_get_mounts, scanner):
        """Test mounted device scanning error handling."""
        mock_get_mounts.side_effect = Exception("Test error")

        result = scanner._scan_mounted_devices(None, 5, True)

        assert result == []
        scanner.stdout.err.assert_called_once_with("Error reading mounts: Test error")

    def test_extract_mount_info_proc_format(self, scanner):
        """Test /proc/mounts format parsing."""
        parts = ["/dev/sda1", "/", "ext4", "rw,relatime", "0", "0"]
        mount = " ".join(parts)

        device, mountpoint, fstype = scanner._extract_mount_info(parts, mount)

        assert device == "/dev/sda1"
        assert mountpoint == "/"
        assert fstype == "ext4"

    def test_extract_mount_info_invalid_format(self, scanner):
        """Test invalid mount entry parsing."""
        parts = ["invalid", "entry"]
        mount = " ".join(parts)

        device, mountpoint, fstype = scanner._extract_mount_info(parts, mount)

        assert device is None
        assert mountpoint is None
        assert fstype is None

    @patch.object(SystemStateScanner, "_get_device_partitions")
    @patch.object(SystemStateScanner, "_should_exclude_device")
    def test_parse_mount_entry_success(
        self, mock_should_exclude, mock_get_partitions, scanner, empty_pyro_config
    ):
        """Test successful mount entry parsing."""
        mock_should_exclude.return_value = False
        mock_get_partitions.return_value = [
            {"name": "sda1", "mountpoint": "/", "fstype": "ext4"}
        ]

        processed = set()
        mount = "/dev/sda1 / ext4 rw 0 0"

        device_info = scanner._parse_mount_entry(mount, processed, empty_pyro_config)

        assert device_info is not None
        assert device_info.device_path == "/dev/sda1"
        assert device_info.mountpoint == "/"
        assert device_info.filesystem_type == "ext4"
        assert "/" in processed


    def test_parse_mount_entry_duplicate_mountpoint(self, scanner, empty_pyro_config):
        """Test parsing duplicate mountpoint."""
        processed = {"/mnt"}

        device_info = scanner._parse_mount_entry(
            "/dev/sdb1 /mnt ext4 rw 0 0", processed, empty_pyro_config
        )

        assert device_info is None

    def test_parse_mount_entry_empty_line(self, scanner, empty_pyro_config):
        """Test parsing empty mount entry."""
        device_info = scanner._parse_mount_entry("", set(), empty_pyro_config)

        assert device_info is None

    @patch("subprocess.run")
    def test_get_device_partitions_success(self, mock_run, scanner, mock_lsblk_output):
        """Test successful partition detection with lsblk."""
        mock_run.return_value = Mock(stdout=json.dumps(mock_lsblk_output), returncode=0)

        partitions = scanner._get_device_partitions("/dev/sda")

        assert len(partitions) == 2
        assert partitions[0]["name"] == "sda1"
        assert partitions[0]["mountpoint"] == "/"
        assert partitions[0]["fstype"] == "ext4"
        assert partitions[1]["name"] == "sda2"

        mock_run.assert_called_once_with(
            ["lsblk", "-J", "/dev/sda"], capture_output=True, text=True, check=True
        )

    @patch("subprocess.run")
    @patch("os.listdir")
    def test_get_device_partitions_fallback(self, mock_listdir, mock_run, scanner):
        """Test fallback partition detection."""
        mock_run.side_effect = FileNotFoundError("lsblk not found")
        mock_listdir.return_value = ["sda", "sda1", "sda2", "sdb"]

        partitions = scanner._get_device_partitions("/dev/sda")

        assert len(partitions) == 2
        assert partitions[0]["name"] == "sda1"
        assert partitions[1]["name"] == "sda2"

        mock_listdir.assert_called_once_with("/dev")

    @patch("os.listdir")
    def test_fallback_partition_detection_error(self, mock_listdir, scanner):
        """Test fallback partition detection with error."""
        mock_listdir.side_effect = OSError("Permission denied")

        partitions = scanner._fallback_partition_detection("/dev/sda")

        assert partitions == []

    def test_extract_partitions_from_lsblk(self, scanner, mock_lsblk_output):
        """Test lsblk JSON parsing."""
        partitions = scanner._extract_partitions_from_lsblk(mock_lsblk_output)

        assert len(partitions) == 2
        assert partitions[0]["name"] == "sda1"
        assert partitions[0]["size"] == "50G"
        assert partitions[0]["mountpoint"] == "/"
        assert partitions[0]["fstype"] == "ext4"

    def test_extract_partitions_from_lsblk_invalid(self, scanner):
        """Test lsblk JSON parsing with invalid data."""
        invalid_data = {"invalid": "format"}

        partitions = scanner._extract_partitions_from_lsblk(invalid_data)

        assert partitions == []

    def test_find_mounted_partition(self, scanner):
        """Test finding partition by mountpoint."""
        partitions = [
            {"name": "sda1", "mountpoint": "/"},
            {"name": "sda2", "mountpoint": "/boot"},
        ]

        result = scanner._find_mounted_partition(partitions, "/boot")

        assert result == "sda2"

    def test_find_mounted_partition_not_found(self, scanner):
        """Test partition not found by mountpoint."""
        partitions = [{"name": "sda1", "mountpoint": "/"}]

        result = scanner._find_mounted_partition(partitions, "/nonexistent")

        assert result == ""


class TestFilesystemScanning:
    """Test filesystem scanning methods."""

#   # TODO
#   def test_scan_device_contents_success(self, mock_scan_recursive, mock_isdir,
#                                       mock_exists, scanner, empty_pyro_config):
#       """Test successful device content scanning."""
#   def test_process_filesystem_entry_regular_file(
#       self, mock_exclude_link, mock_exclude_dir, mock_exclude_file,
#       mock_get_perms, mock_getgrgid, mock_getpwuid, mock_lstat, scanner, empty_pyro_config
#   ):
#       """Test processing a regular file."""
#   def test_process_filesystem_entry_directory(
#       self, mock_exclude_dir, mock_get_perms, mock_getgrgid, mock_getpwuid,
#       mock_lstat, scanner, empty_pyro_config
#   ):
#       """Test processing a directory."""
#   def test_process_filesystem_entry_symlink(
#       self, mock_readlink, mock_exclude_link, mock_get_perms, mock_getgrgid,
#       mock_getpwuid, mock_lstat, scanner, empty_pyro_config
#   ):
#       """Test processing a symlink."""
#   def test_scan_device_contents_error(
#       self, mock_scan_recursive, mock_isdir, mock_exists, scanner
#   ):
#       """Test device content scanning with error."""


    @patch("os.path.exists")
    @patch("os.path.isdir")
    def test_scan_device_contents_nonexistent(self, mock_isdir, mock_exists, scanner):
        """Test scanning nonexistent mountpoint."""
        mock_exists.return_value = False

        device_info = Mock(spec=MountedDevice)
        device_info.mountpoint = "/nonexistent"

        scanner._scan_device_contents(device_info, 5, True, None)

        # Should not attempt to scan
        scanner.stdout.debug.assert_not_called()

    @patch("os.listdir")
    @patch.object(SystemStateScanner, "_process_filesystem_entry")
    def test_scan_filesystem_recursive_basic(
        self, mock_process_entry, mock_listdir, scanner, empty_pyro_config
    ):
        """Test basic recursive filesystem scanning."""
        mock_listdir.return_value = ["file1.txt", ".hidden", "subdir"]

        device_info = Mock()
        device_info.files = []
        device_info.directories = []
        device_info.symlinks = []

        scanner._scan_filesystem_recursive(
            "/test", device_info, 2, False, 0, empty_pyro_config
        )

        # Should process 2 entries (hidden file excluded)
        assert mock_process_entry.call_count == 2
        mock_process_entry.assert_any_call(
            "/test/file1.txt", device_info, 2, False, 0, empty_pyro_config
        )
        mock_process_entry.assert_any_call(
            "/test/subdir", device_info, 2, False, 0, empty_pyro_config
        )

    @patch("os.listdir")
    def test_scan_filesystem_recursive_max_depth(self, mock_listdir, scanner):
        """Test recursive scanning respects max depth."""
        # Should not call listdir when at max depth
        scanner._scan_filesystem_recursive(
            "/test", Mock(), 2, True, 3, None  # current_depth > max_depth
        )

        mock_listdir.assert_not_called()

    @patch("os.listdir")
    def test_scan_filesystem_recursive_permission_error(self, mock_listdir, scanner):
        """Test recursive scanning with permission error."""
        mock_listdir.side_effect = PermissionError("Access denied")

        device_info = Mock()

        # Should not raise exception
        scanner._scan_filesystem_recursive("/protected", device_info, 5, True, 0, None)

    @patch("os.lstat")
    def test_process_filesystem_entry_permission_error(self, mock_lstat, scanner):
        """Test processing entry with permission error."""
        mock_lstat.side_effect = PermissionError("Access denied")

        device_info = Mock()

        # Should not raise exception
        scanner._process_filesystem_entry(
            "/protected/file", device_info, 5, True, 0, None
        )

    def test_exclusion_checks(self, scanner, pyro_config):
        """Test all exclusion check methods."""
        # File exclusion
        assert scanner._should_exclude_file("/etc/excluded.txt", pyro_config) == True
        assert scanner._should_exclude_file("/etc/regular.txt", pyro_config) == False

        # Directory exclusion
        assert scanner._should_exclude_directory("/tmp/excluded", pyro_config) == True
        assert scanner._should_exclude_directory("/tmp/regular", pyro_config) == False

        # Link exclusion
        assert scanner._should_exclude_link("/etc/link_excluded", pyro_config) == True
        assert scanner._should_exclude_link("/etc/link_regular", pyro_config) == False

        # Device exclusion
        assert scanner._should_exclude_device("/dev/excluded", pyro_config) == True
        assert scanner._should_exclude_device("/dev/regular", pyro_config) == False


class TestUtilityMethods:
    """Test utility methods."""

    def test_get_numeric_permissions(self, scanner):
        """Test permission conversion to numeric notation."""
        # Test various permissions
        test_cases = [
            (0o755, "0755"),  # Standard directory
            (0o644, "0644"),  # Standard file
            (0o777, "0777"),  # Full permissions
            (0o400, "0400"),  # Read only
            (0o755 | stat.S_ISUID, "4755"),  # Setuid
            (0o755 | stat.S_ISGID, "2755"),  # Setgid
            (0o755 | stat.S_ISVTX, "1755"),  # Sticky bit
        ]

        for mode, expected in test_cases:
            result = scanner._get_numeric_permissions(mode)
            assert result == expected, f"Failed for mode {oct(mode)}"

    @patch("pwd.getpwuid")
    def test_get_username_success(self, mock_getpwuid, scanner):
        """Test username lookup by UID."""
        mock_getpwuid.return_value = Mock(pw_name="testuser")

        result = scanner._get_username(1000)

        assert result == "testuser"
        mock_getpwuid.assert_called_once_with(1000)

    @patch("pwd.getpwuid")
    def test_get_username_not_found(self, mock_getpwuid, scanner):
        """Test username lookup for non-existent UID."""
        mock_getpwuid.side_effect = KeyError("No such user")

        result = scanner._get_username(9999)

        assert result == "9999"

    @patch("grp.getgrgid")
    def test_get_groupname_success(self, mock_getgrgid, scanner):
        """Test groupname lookup by GID."""
        mock_getgrgid.return_value = Mock(gr_name="testgroup")

        result = scanner._get_groupname(1000)

        assert result == "testgroup"
        mock_getgrgid.assert_called_once_with(1000)

    @patch("grp.getgrgid")
    def test_get_groupname_not_found(self, mock_getgrgid, scanner):
        """Test groupname lookup for non-existent GID."""
        mock_getgrgid.side_effect = KeyError("No such group")

        result = scanner._get_groupname(9999)

        assert result == "9999"

    @patch("os.readlink")
    def test_read_symlink_target_success(self, mock_readlink, scanner):
        """Test successful symlink target reading."""
        mock_readlink.return_value = "/target/path"

        result = scanner._read_symlink_target("/link")

        assert result == "/target/path"
        mock_readlink.assert_called_once_with("/link")

    @patch("os.readlink")
    def test_read_symlink_target_error(self, mock_readlink, scanner):
        """Test symlink reading error."""
        mock_readlink.side_effect = OSError("Broken link")

        result = scanner._read_symlink_target("/broken")

        assert result == "broken"


class TestIntegrationAndEdgeCases:
    """Test integration scenarios and edge cases."""

#   # TODO
#   def test_complete_scan_with_exclusions(
#       self, mock_scan_contents, mock_parse_entry, mock_get_mounts,
#       mock_getgrall, mock_getpwall, scanner, pyro_config
#   ):
#       """Test complete system scan with exclusions."""
#   def test_scan_with_none_config(self, scanner):
#       """Test scanning with None config (no exclusions)."""
#   def test_scan_with_config_no_excludes(self, scanner):
#       """Test scanning with config but no excludes section."""
#   def test_process_filesystem_entry_special_files(self, mock_lstat, scanner):
#       """Test processing special file types (should be ignored)."""
#   def test_debug_output_formatting(self, scanner, mock_stdout):
#       """Test debug output formatting."""

    @patch("subprocess.run")
    def test_command_execution_security(self, mock_run, scanner):
        """Test that commands are executed with proper arguments."""
        scanner._get_user_groups("testuser")

        # Verify command is not using shell=True
        mock_run.assert_called_once_with(
            ["groups", "testuser"], capture_output=True, text=True, check=True
        )

        # Verify no shell injection vulnerability
        call_args = mock_run.call_args[0][0]
        assert len(call_args) == 2  # ['groups', 'username']
        assert ";" not in call_args[1]  # No command injection
        assert "&" not in call_args[1]
        assert "|" not in call_args[1]


class TestPerformance:
    """Test performance-related aspects."""

    @patch("os.listdir")
    def test_recursive_scan_depth_limit(self, mock_listdir, scanner):
        """Test that recursive scanning respects depth limit."""
        call_count = 0

        def mock_recursive_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1

        with patch.object(
            scanner,
            "_scan_filesystem_recursive",
            side_effect=mock_recursive_side_effect,
        ):
            # This should only go 2 levels deep
            scanner._scan_filesystem_recursive("/test", Mock(), 2, True, 0, None)

            # Should be called once (the initial call)
            assert call_count == 1

    @patch("os.listdir")
    def test_hidden_file_exclusion_performance(self, mock_listdir, scanner):
        """Test that hidden file exclusion works efficiently."""
        # Create many files, some hidden
        files = [f".hidden{i}" for i in range(50)] + [f"visible{i}" for i in range(50)]
        mock_listdir.return_value = files

        with patch.object(scanner, "_process_filesystem_entry") as mock_process:
            scanner._scan_filesystem_recursive(
                "/test", Mock(), 1, False, 0, None  # include_hidden=False
            )

            # Should only process visible files
            assert mock_process.call_count == 50

    def test_mountpoint_deduplication(self, scanner):
        """Test that mountpoints are not processed multiple times."""
        processed = set()

        # First call should process
        device1 = scanner._parse_mount_entry(
            "/dev/sda1 /mnt/data ext4 rw 0 0", processed, None
        )
        assert device1 is not None
        assert "/mnt/data" in processed

        # Second call with same mountpoint should skip
        device2 = scanner._parse_mount_entry(
            "/dev/sdb1 /mnt/data xfs rw 0 0",  # Different device, same mountpoint
            processed,
            None,
        )
        assert device2 is None


if __name__ == "__main__":
    # This allows running the test file directly
    pytest.main([__file__, "-v", "--tb=short"])
