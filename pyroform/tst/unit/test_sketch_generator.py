"""
FlowCTRL Sketch Generator Test Suite

Unit tests for Sketch Generator
"""

from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from pyroform.src.logging import STDOUTMsg
from pyroform.src.models import ActionType, Device, Exclude, Group, PyroConfig, User
from pyroform.src.sketch_generator import (
    CommandGenerator,
    ExclusionChecker,
    SketchGenerator,
    StateEntryParser,
)
from pyroform.src.splitter import ListSplitter
from pyroform.src.validator import SystemValidator


@pytest.fixture
def mock_stdout():
    """Mock STDOUTMsg to avoid console output during tests."""
    mock = Mock(spec=STDOUTMsg)
    mock.info = Mock()
    mock.debug = Mock()
    mock.warn = Mock()
    mock.err = Mock()
    return mock


@pytest.fixture
def mock_user():
    """Create a mock User."""
    user = Mock(spec=User)
    user.name = "testuser"
    user.label = "testuser_label"
    user.password = "encrypted_password"
    user.groups = ["wheel", "audio"]
    return user


@pytest.fixture
def mock_group():
    """Create a mock Group."""
    group = Mock(spec=Group)
    group.name = "testgroup"
    group.label = "testgroup_label"
    group.users = ["user1", "user2"]
    return group


@pytest.fixture
def mock_device():
    """Create a mock Device."""
    device = Mock(spec=Device)
    device.label = "test_device"
    device.path = "/dev/sda1"
    device.mountpoint = "/mnt/data"
    device.partition = "1"
    device.state = [
        "dir,/mnt/data/dir1,root,root,0755",
        "fl,/mnt/data/file.txt,root,root,0644",
        "ln,/mnt/data/link,target,root,root,0777",
    ]
    return device


@pytest.fixture
def mock_pyro_config(mock_user, mock_group, mock_device):
    """Create a mock PyroConfig."""
    config = Mock(spec=PyroConfig)
    config.label = "test_config"
    config.users = [mock_user]
    config.groups = [mock_group]
    config.devices = [mock_device]

    excludes = Mock(spec=Exclude)
    excludes.users = ["excluded_user"]
    excludes.groups = ["excluded_group"]
    excludes.devices = ["/dev/excluded"]
    excludes.directories = ["/excluded/dir"]
    excludes.files = ["/excluded/file.txt"]
    excludes.links = ["/excluded/link"]
    config.excludes = excludes

    return config


@pytest.fixture
def empty_pyro_config():
    """Create an empty PyroConfig."""
    config = Mock(spec=PyroConfig)
    config.label = "empty_config"
    config.users = []
    config.groups = []
    config.devices = []
    config.excludes = Mock(spec=Exclude)
    config.excludes.users = []
    config.excludes.groups = []
    config.excludes.devices = []
    config.excludes.directories = []
    config.excludes.files = []
    config.excludes.links = []
    return config


@pytest.fixture
def system_state():
    """Create a sample system state."""
    return {
        "users": [
            {
                "username": "existing_user",
                "groups": ["wheel"],
                "uid": 1000,
                "gid": 1000,
                "home_directory": "/home/existing",
                "shell": "/bin/bash",
                "gecos": "Existing User",
            }
        ],
        "groups": [
            {"groupname": "existing_group", "gid": 1000, "members": ["existing_user"]}
        ],
        "mounted_devices": [
            {
                "device_path": "/dev/sda1",
                "mountpoint": "/",
                "filesystem_type": "ext4",
                "partition": "sda1",
                "files": [
                    {
                        "path": "/etc/hosts",
                        "owner": "root",
                        "group": "root",
                        "permissions": "0644",
                    }
                ],
                "directories": [
                    {
                        "path": "/etc",
                        "owner": "root",
                        "group": "root",
                        "permissions": "0755",
                    }
                ],
                "symlinks": [
                    {
                        "path": "/etc/localtime",
                        "owner": "root",
                        "group": "root",
                        "permissions": "0777",
                        "target": "/usr/share/zoneinfo/UTC",
                    }
                ],
            }
        ],
    }


class TestCommandGenerator:
    """Test CommandGenerator class."""

#   # TODO
#   def test_generate_mount_command_no_partition(self, mock_device):
#       """Test mount command generation without partition."""
#   def test_init(self, mock_stdout):
#       """Test initialization."""

    def test_init_default_stdout(self):
        """Test initialization with default stdout."""
        generator = CommandGenerator()

        assert generator.stdout is not None
        assert isinstance(generator.stdout, STDOUTMsg)
        assert generator.cmd_prefix == ""  # Not dry run by default

    def test_init_dry_run_false(self):
        """Test initialization with dry_run=False."""
        generator = CommandGenerator(dry_run=False)

        assert generator.cmd_prefix == ""

    def test_generate_user_command(self, mock_stdout, mock_user):
        """Test user command generation."""
        generator = CommandGenerator(dry_run=False, stdout=mock_stdout)

        command = generator.generate_user_command(mock_user)

        assert isinstance(command, dict)
        assert command["name"] == "Creating System User testuser"
        assert "useradd" in command["cmd"]
        assert "wheel" in command["cmd"]  # Should include groups
        assert "testuser" in command["cmd"]
        assert "setup-cmd" in command
        assert "on-ok-cmd" in command
        assert "on-nok-cmd" in command
        assert "fatal-nok" in command
        assert command["fatal-nok"] == False

    def test_generate_user_command_dry_run(self, mock_user):
        """Test user command generation in dry-run mode."""
        generator = CommandGenerator(dry_run=True)

        command = generator.generate_user_command(mock_user)

        assert command["cmd"].startswith("# ")

    def test_generate_user_command_no_groups(self, mock_user):
        """Test user command generation with empty groups."""
        mock_user.groups = []
        generator = CommandGenerator()

        command = generator.generate_user_command(mock_user)

        # Should still generate valid command
        assert "useradd" in command["cmd"]

    def test_generate_group_command(self, mock_group):
        """Test group command generation."""
        generator = CommandGenerator()

        command = generator.generate_group_command(mock_group)

        assert isinstance(command, dict)
        assert command["name"] == "Creating System Group testgroup"
        assert "groupadd" in command["cmd"]
        assert "testgroup" in command["cmd"]
        assert command["fatal-nok"] == False

    def test_generate_group_command_no_members(self, mock_group):
        """Test group command generation with empty members."""
        mock_group.users = []
        generator = CommandGenerator()

        command = generator.generate_group_command(mock_group)

        # Should still generate valid command
        assert "groupadd" in command["cmd"]

    def test_generate_mountpoint_command(self, mock_device):
        """Test mountpoint command generation."""
        generator = CommandGenerator()

        command = generator.generate_mountpoint_command(mock_device)

        assert (
            command["name"]
            == f"Creating System Mountpoint Directory {mock_device.mountpoint}"
        )
        assert "mkdir" in command["cmd"]
        assert mock_device.mountpoint in command["cmd"]
        assert command["fatal-nok"] == True

    def test_generate_mount_command(self, mock_device):
        """Test mount command generation."""
        generator = CommandGenerator()

        command = generator.generate_mount_command(mock_device)

        assert command["name"] == f"Mounting Block Device {mock_device.label}"
        assert "mount" in command["cmd"]
        assert mock_device.path in command["cmd"]
        assert mock_device.mountpoint in command["cmd"]
        assert command["fatal-nok"] == True

    def test_generate_directory_command(self):
        """Test directory command generation."""
        generator = CommandGenerator()

        command = generator.generate_directory_command("/test/dir")

        assert command["name"] == "Creating Directory /test/dir"
        assert "mkdir" in command["cmd"]
        assert "/test/dir" in command["cmd"]
        assert command["fatal-nok"] == True

    def test_generate_file_command(self):
        """Test file command generation."""
        generator = CommandGenerator()

        command = generator.generate_file_command("/test/file.txt")

        assert command["name"] == "Creating Regular File /test/file.txt"
        assert "touch" in command["cmd"]
        assert "/test/file.txt" in command["cmd"]
        assert command["fatal-nok"] == True

    def test_generate_symlink_command(self):
        """Test symlink command generation."""
        generator = CommandGenerator()

        command = generator.generate_symlink_command("/link", "/target")

        assert command["name"] == "Creating Symbolic Link /link"
        assert "ln -s" in command["cmd"]
        assert "/target" in command["cmd"]
        assert "/link" in command["cmd"]
        assert command["fatal-nok"] == True

    def test_generate_permission_command(self):
        """Test permission command generation."""
        generator = CommandGenerator()

        command = generator.generate_permission_command("/test", "root", "root", "0755")

        assert command["name"] == "Setting Permissions For /test"
        assert "chown" in command["cmd"]
        assert "chmod" in command["cmd"]
        assert "root:root" in command["cmd"]
        assert "0755" in command["cmd"]
        assert command["fatal-nok"] == True

    def test_generate_cleanup_user_command(self):
        """Test user cleanup command generation."""
        generator = CommandGenerator()

        command = generator.generate_cleanup_user_command("user1 user2 user3")

        assert command["name"] == "Cleanup extra users"
        assert "userdel" in command["cmd"]
        assert "user1 user2 user3" in command["cmd"]
        assert "Eliminated:" in command["on-ok-cmd"]
        assert command["fatal-nok"] == False

    def test_generate_cleanup_user_command_dry_run(self):
        """Test user cleanup command generation in dry-run mode."""
        generator = CommandGenerator(dry_run=True)

        command = generator.generate_cleanup_user_command("user1")

        assert command["cmd"].startswith("# ")

    def test_generate_cleanup_group_command(self):
        """Test group cleanup command generation."""
        generator = CommandGenerator()

        command = generator.generate_cleanup_group_command("group1 group2")

        assert command["name"] == "Cleanup extra groups"
        assert "groupdel" in command["cmd"]
        assert command["fatal-nok"] == False

    def test_generate_cleanup_directories_command(self):
        """Test directory cleanup command generation."""
        generator = CommandGenerator()

        command = generator.generate_cleanup_directories_command("/dir1 /dir2")

        assert command["name"] == "Cleanup extra directories"
        assert "rm -rf" in command["cmd"]
        assert command["fatal-nok"] == False

    def test_generate_cleanup_files_command(self):
        """Test file cleanup command generation."""
        generator = CommandGenerator()

        command = generator.generate_cleanup_files_command("/file1 /file2")

        assert command["name"] == "Cleanup extra files and links"
        assert "rm -f" in command["cmd"]
        assert command["fatal-nok"] == False

    def test_command_structure_consistency(self, mock_user):
        """Test that all commands have consistent structure."""
        generator = CommandGenerator()

        command = generator.generate_user_command(mock_user)

        # Check required fields
        required_fields = [
            "name",
            "cmd",
            "setup-cmd",
            "on-ok-cmd",
            "on-nok-cmd",
            "fatal-nok",
        ]
        for field in required_fields:
            assert field in command

        # Check field types
        assert isinstance(command["name"], str)
        assert isinstance(command["cmd"], str)
        assert isinstance(command["setup-cmd"], str)
        assert isinstance(command["on-ok-cmd"], str)
        assert isinstance(command["on-nok-cmd"], str)
        assert isinstance(command["fatal-nok"], bool)


class TestExclusionChecker:
    """Test ExclusionChecker class."""

    # TODO
#   def test_should_exclude_user(self, mock_stdout):
#       """Test user exclusion check."""
#   def test_should_exclude_group(self, mock_stdout):
#       """Test group exclusion check."""
#   def test_should_exclude_device(self, mock_stdout):
#       """Test device exclusion check."""
#   def test_should_exclude_path(self, mock_stdout):
#       """Test path exclusion check."""


    def test_init(self, mock_stdout):
        """Test initialization."""
        checker = ExclusionChecker(stdout=mock_stdout)

        assert checker.stdout == mock_stdout

    def test_init_default_stdout(self):
        """Test initialization with default stdout."""
        checker = ExclusionChecker()

        assert checker.stdout is not None
        assert isinstance(checker.stdout, STDOUTMsg)

    def test_should_exclude_user_empty_excludes(self, mock_stdout):
        """Test user exclusion with empty exclude list."""
        checker = ExclusionChecker(stdout=mock_stdout)

        assert checker.should_exclude_user("any_user", []) == False
        assert checker.should_exclude_user("any_user", None) == False

    def test_has_excluded_parent_direct_parent(self, mock_stdout):
        """Test parent exclusion check with direct parent."""
        checker = ExclusionChecker(stdout=mock_stdout)

        excluded_paths = ["/excluded"]

        # Direct child
        assert checker.has_excluded_parent("/excluded/child", excluded_paths) == True
        mock_stdout.debug.assert_called_with("Excluding: /excluded/child")

        # Not a child
        mock_stdout.debug.reset_mock()
        assert checker.has_excluded_parent("/other/child", excluded_paths) == False
        mock_stdout.debug.assert_not_called()

    def test_has_excluded_parent_nested(self, mock_stdout):
        """Test parent exclusion check with nested paths."""
        checker = ExclusionChecker(stdout=mock_stdout)

        excluded_paths = ["/excluded"]

        assert (
            checker.has_excluded_parent("/excluded/nested/deep", excluded_paths) == True
        )

    def test_has_excluded_parent_same_path(self, mock_stdout):
        """Test parent exclusion check with same path."""
        checker = ExclusionChecker(stdout=mock_stdout)

        excluded_paths = ["/excluded"]

        # Same path should be considered a parent
        assert checker.has_excluded_parent("/excluded", excluded_paths) == True

    def test_has_excluded_parent_multiple_excludes(self, mock_stdout):
        """Test parent exclusion check with multiple excluded paths."""
        checker = ExclusionChecker(stdout=mock_stdout)

        excluded_paths = ["/excluded1", "/excluded2"]

        assert checker.has_excluded_parent("/excluded1/child", excluded_paths) == True
        assert checker.has_excluded_parent("/excluded2/child", excluded_paths) == True
        assert checker.has_excluded_parent("/other/child", excluded_paths) == False

    def test_has_excluded_parent_with_path_objects(self, mock_stdout):
        """Test parent exclusion check with Path objects."""
        checker = ExclusionChecker(stdout=mock_stdout)

        excluded_paths = [Path("/excluded")]

        assert checker.has_excluded_parent("/excluded/child", excluded_paths) == True
        assert (
            checker.has_excluded_parent(Path("/excluded/child"), excluded_paths) == True
        )

    def test_has_excluded_parent_resolution(self, mock_stdout):
        """Test parent exclusion with path resolution."""
        checker = ExclusionChecker(stdout=mock_stdout)

        excluded_paths = ["/excluded"]

        # Should resolve paths before comparison
        with patch.object(Path, "resolve") as mock_resolve:
            mock_resolve.return_value = Path("/excluded")
            assert (
                checker.has_excluded_parent("/excluded/child", excluded_paths) == True
            )


class TestStateEntryParser:
    """Test StateEntryParser class."""

    #   # TODO
    #   def test_get_entry_type_category_case_insensitive(self):
    #       """Test type categorization is case insensitive."""

    def test_parse_state_entry_directory(self):
        """Test parsing directory entry."""
        entry = "dir,/test/dir,root,root,0755"

        result = StateEntryParser.parse_state_entry(entry)

        assert result is not None
        assert result["type"] == "dir"
        assert result["path"] == "/test/dir"
        assert result["owner"] == "root"
        assert result["group"] == "root"
        assert result["permissions"] == "0755"

    def test_parse_state_entry_file(self):
        """Test parsing file entry."""
        entry = "fl,/test/file.txt,root,root,0644"

        result = StateEntryParser.parse_state_entry(entry)

        assert result["type"] == "fl"
        assert result["path"] == "/test/file.txt"

    def test_parse_state_entry_symlink(self):
        """Test parsing symlink entry."""
        entry = "ln,/test/link,root,root,0777,/target"

        result = StateEntryParser.parse_state_entry(entry)

        assert result["type"] == "ln"
        assert result["path"] == "/test/link"
        assert result["target"] == "/target"

    def test_parse_state_entry_various_types(self):
        """Test parsing various type notations."""
        test_cases = [
            ("d,/test,root,root,0755", "d"),
            ("dir,/test,root,root,0755", "dir"),
            ("directory,/test,root,root,0755", "directory"),
            ("f,/test,root,root,0644", "f"),
            ("fl,/test,root,root,0644", "fl"),
            ("file,/test,root,root,0644", "file"),
            ("l,/test,root,root,0777,/target", "l"),
            ("ln,/test,root,root,0777,/target", "ln"),
            ("link,/test,root,root,0777,/target", "link"),
        ]

        for entry, expected_type in test_cases:
            result = StateEntryParser.parse_state_entry(entry)
            assert result is not None
            assert result["type"] == expected_type

    def test_parse_state_entry_invalid(self):
        """Test parsing invalid entries."""
        # Too few parts
        assert StateEntryParser.parse_state_entry("dir,/test,root") is None
        # Empty
        assert StateEntryParser.parse_state_entry("") is None
        # Invalid format
        assert StateEntryParser.parse_state_entry("invalid") is None

    def test_parse_state_entry_case_insensitive(self):
        """Test parsing is case insensitive."""
        entry = "DIR,/test,root,root,0755"

        result = StateEntryParser.parse_state_entry(entry)

        assert result is not None
        assert result["type"] == "dir"  # Should be lowercased

    def test_is_valid_state_entry_valid(self):
        """Test validation of valid entry."""
        entry = {
            "type": "dir",
            "path": "/test",
            "owner": "root",
            "group": "root",
            "permissions": "0755",
        }

        assert StateEntryParser.is_valid_state_entry(entry) == True

    def test_is_valid_state_entry_missing_field(self):
        """Test validation of entry with missing field."""
        entry = {
            "type": "dir",
            "path": "/test",
            "owner": "root",
            # Missing group and permissions
        }

        assert StateEntryParser.is_valid_state_entry(entry) == False

    def test_is_valid_state_entry_empty(self):
        """Test validation of empty entry."""
        assert StateEntryParser.is_valid_state_entry({}) == False

    def test_get_entry_type_category(self):
        """Test entry type categorization."""
        test_cases = [
            ("d", "directory"),
            ("dir", "directory"),
            ("directory", "directory"),
            ("f", "file"),
            ("fl", "file"),
            ("file", "file"),
            ("l", "symlink"),
            ("ln", "symlink"),
            ("link", "symlink"),
            ("unknown", "unknown"),  # Unknown type
            ("", "unknown"),  # Empty type
        ]

        for obj_type, expected in test_cases:
            result = StateEntryParser.get_entry_type_category(obj_type)
            assert result == expected

# TODO
#   class TestSketchGeneratorInitialization:
#       """Test SketchGenerator initialization."""
#       def test_init_defaults(self, mock_stdout):
#           """Test initialization with defaults."""
#       def test_init_custom_params(self, mock_stdout):
#           """Test initialization with custom parameters."""
#       def test_init_components(self, mock_stdout):
#           """Test that components are initialized properly."""
#       def test_init_dry_run_propagated(self, mock_stdout):
#           """Test that dry_run is propagated to CommandGenerator."""


class TestGenerateSketch:
    """Test the main generate_sketch method."""

    def test_generate_sketch_configure(self, mock_stdout, mock_pyro_config):
        """Test generate_sketch for CONFIGURE action."""
        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(generator, "generate_configure_sketch") as mock_configure:
            mock_configure.return_value = {"test": "sketch"}

            result = generator.generate_sketch(mock_pyro_config, ActionType.CONFIGURE)

            mock_configure.assert_called_once_with(mock_pyro_config)
            assert result == {"test": "sketch"}

    def test_generate_sketch_mount(self, mock_stdout, mock_pyro_config):
        """Test generate_sketch for MOUNT action."""
        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(generator, "generate_mount_sketch") as mock_mount:
            mock_mount.return_value = {"test": "mount_sketch"}

            result = generator.generate_sketch(mock_pyro_config, ActionType.MOUNT)

            mock_mount.assert_called_once_with(mock_pyro_config)
            assert result == {"test": "mount_sketch"}

    def test_generate_sketch_scorch(self, mock_stdout, mock_pyro_config):
        """Test generate_sketch for SCORCH action."""
        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(generator, "generate_scorch_sketch") as mock_scorch:
            mock_scorch.return_value = {"test": "scorch_sketch"}

            result = generator.generate_sketch(mock_pyro_config, ActionType.SCORCH)

            mock_scorch.assert_called_once_with(mock_pyro_config)
            assert result == {"test": "scorch_sketch"}

    def test_generate_sketch_snapshot(self, mock_stdout, mock_pyro_config):
        """Test generate_sketch for SNAPSHOT action."""
        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(generator, "generate_snapshot_pyro_config") as mock_snapshot:
            mock_snapshot.return_value = {"test": "snapshot"}

            result = generator.generate_sketch(mock_pyro_config, ActionType.SNAPSHOT)

            mock_snapshot.assert_called_once_with(mock_pyro_config)
            assert result == {"test": "snapshot"}

    def test_generate_sketch_validate_error(self, mock_stdout, mock_pyro_config):
        """Test generate_sketch for VALIDATE action raises error."""
        generator = SketchGenerator(stdout=mock_stdout)

        with pytest.raises(
            ValueError, match="Validate action does not generate sketches"
        ):
            generator.generate_sketch(mock_pyro_config, ActionType.VALIDATE)

    def test_generate_sketch_unsupported_action(self, mock_stdout, mock_pyro_config):
        """Test generate_sketch for unsupported action raises error."""
        generator = SketchGenerator(stdout=mock_stdout)

        unsupported_action = Mock()
        unsupported_action.value = "UNSUPPORTED"

        with pytest.raises(ValueError, match="Unsupported action type"):
            generator.generate_sketch(mock_pyro_config, unsupported_action)

    def test_generate_sketch_none_config(self, mock_stdout):
        """Test generate_sketch with None config."""
        generator = SketchGenerator(stdout=mock_stdout)

        # Should handle gracefully based on action
        with patch.object(generator, "generate_snapshot_pyro_config") as mock_snapshot:
            mock_snapshot.return_value = {}

            result = generator.generate_sketch(None, ActionType.SNAPSHOT)

            mock_snapshot.assert_called_once_with(None)
            assert result == {}


class TestSnapshotGeneration:
    """Test snapshot generation methods."""

#   # TODO
#   def test_generate_snapshot_pyro_config(self, mock_get_state, mock_stdout, system_state):
#       """Test snapshot generation."""
#   def test_build_device_state_snapshot_missing_fields(self, mock_stdout):
#       """Test device state snapshot building with missing fields."""
#   def test_build_device_snapshot(self, mock_stdout, system_state):
#       """Test device snapshot building."""
#   def test_build_device_state_snapshot(self, mock_stdout, system_state):
#       """Test device state snapshot building."""


    def test_build_user_snapshot(self, mock_stdout, system_state):
        """Test user snapshot building."""
        generator = SketchGenerator(stdout=mock_stdout)

        result = generator._build_user_snapshot(system_state)

        assert isinstance(result, list)
        assert len(result) == 1
        user_snapshot = result[0]
        assert user_snapshot["label"] == "Snapshot of existing_user"
        assert user_snapshot["Name"] == "existing_user"
        assert user_snapshot["Password"] == ""  # Passwords not stored
        assert user_snapshot["Groups"] == ["wheel"]

    def test_build_user_snapshot_empty(self, mock_stdout):
        """Test user snapshot building with empty state."""
        generator = SketchGenerator(stdout=mock_stdout)

        result = generator._build_user_snapshot({})

        assert result == []

    def test_build_group_snapshot(self, mock_stdout, system_state):
        """Test group snapshot building."""
        generator = SketchGenerator(stdout=mock_stdout)

        result = generator._build_group_snapshot(system_state)

        assert isinstance(result, list)
        assert len(result) == 1
        group_snapshot = result[0]
        assert group_snapshot["label"] == "Snapshot of existing_group"
        assert group_snapshot["Name"] == "existing_group"
        assert group_snapshot["Users"] == ["existing_user"]

    def test_build_device_state_snapshot_empty(self, mock_stdout):
        """Test device state snapshot building with empty device."""
        generator = SketchGenerator(stdout=mock_stdout)

        device = {"files": [], "directories": [], "symlinks": []}

        result = generator._build_device_state_snapshot(device)

        assert result == []


class TestScorchSketchGeneration:
    """Test scorch sketch generation."""

    #   # TODO
    #   def test_generate_scorch_sketch(
    #       self, mock_compare, mock_get_state, mock_stdout, mock_pyro_config, system_state
    #   ):
    #       """Test scorch sketch generation."""

    def test_generate_cleanup_commands(self, mock_stdout, mock_pyro_config):
        """Test cleanup command generation."""
        generator = SketchGenerator(stdout=mock_stdout)

        compared = {
            "extra_users": [{"username": "user1"}],
            "extra_groups": [{"groupname": "group1"}],
            "extra_directories": [{"path": "/dir1"}],
            "extra_files": [{"path": "/file1"}],
            "extra_symlinks": [{"path": "/link1"}],
        }

        with patch.object(
            generator, "_generate_user_cleanup_commands"
        ) as mock_users, patch.object(
            generator, "_generate_group_cleanup_commands"
        ) as mock_groups, patch.object(
            generator, "_generate_filesystem_cleanup_commands"
        ) as mock_fs:

            mock_users.return_value = [{"user": "cleanup"}]
            mock_groups.return_value = [{"group": "cleanup"}]
            mock_fs.return_value = [{"fs": "cleanup"}]

            result = generator._generate_cleanup_commands(mock_pyro_config, compared)

            assert len(result) == 3
            mock_users.assert_called_once_with(mock_pyro_config, compared)
            mock_groups.assert_called_once_with(mock_pyro_config, compared)
            mock_fs.assert_called_once_with(mock_pyro_config, compared)

    def test_generate_user_cleanup_commands_no_extra(
        self, mock_stdout, mock_pyro_config
    ):
        """Test user cleanup with no extra users."""
        generator = SketchGenerator(stdout=mock_stdout)

        compared = {"extra_users": []}

        result = generator._generate_user_cleanup_commands(mock_pyro_config, compared)

        assert result == []

    def test_generate_user_cleanup_commands_with_exclusions(
        self, mock_stdout, mock_pyro_config
    ):
        """Test user cleanup with exclusions."""
        generator = SketchGenerator(stdout=mock_stdout)

        compared = {
            "extra_users": [{"username": "excluded_user"}, {"username": "regular_user"}]
        }

        with patch.object(
            generator.exclusion_checker, "should_exclude_user"
        ) as mock_exclude:
            mock_exclude.side_effect = [True, False]  # First excluded, second not

            with patch.object(generator.list_splitter, "split") as mock_split:
                mock_split.return_value = [["regular_user"]]

                with patch.object(
                    generator.command_generator, "generate_cleanup_user_command"
                ) as mock_cmd:
                    mock_cmd.return_value = {"cmd": "cleanup"}

                    result = generator._generate_user_cleanup_commands(
                        mock_pyro_config, compared
                    )

                    assert len(result) == 1
                    mock_exclude.assert_any_call(
                        "excluded_user", mock_pyro_config.excludes.users
                    )
                    mock_exclude.assert_any_call(
                        "regular_user", mock_pyro_config.excludes.users
                    )

    def test_generate_user_cleanup_commands_chunking(
        self, mock_stdout, mock_pyro_config
    ):
        """Test user cleanup command chunking."""
        generator = SketchGenerator(stdout=mock_stdout, chunk_size=2)

        compared = {
            "extra_users": [
                {"username": "user1"},
                {"username": "user2"},
                {"username": "user3"},
            ]
        }

        with patch.object(
            generator.exclusion_checker, "should_exclude_user", return_value=False
        ):
            with patch.object(
                generator.command_generator, "generate_cleanup_user_command"
            ) as mock_cmd:
                mock_cmd.return_value = {"cmd": "cleanup"}

                result = generator._generate_user_cleanup_commands(
                    mock_pyro_config, compared
                )

                # Should create 2 chunks (2 + 1 users with chunk_size=2)
                assert len(result) == 2
                assert mock_cmd.call_count == 2

    def test_generate_group_cleanup_commands(self, mock_stdout, mock_pyro_config):
        """Test group cleanup command generation."""
        generator = SketchGenerator(stdout=mock_stdout)

        compared = {"extra_groups": [{"groupname": "group1"}]}

        with patch.object(
            generator.exclusion_checker, "should_exclude_group", return_value=False
        ):
            with patch.object(
                generator.command_generator, "generate_cleanup_group_command"
            ) as mock_cmd:
                mock_cmd.return_value = {"cmd": "cleanup group"}

                result = generator._generate_group_cleanup_commands(
                    mock_pyro_config, compared
                )

                assert len(result) == 1
                mock_cmd.assert_called_once()

    def test_generate_directory_cleanup_commands(self, mock_stdout, mock_pyro_config):
        """Test directory cleanup command generation."""
        generator = SketchGenerator(stdout=mock_stdout)

        compared = {"extra_directories": [{"path": "/dir1"}]}

        with patch.object(
            generator.exclusion_checker, "should_exclude_path", return_value=False
        ), patch.object(
            generator.exclusion_checker, "has_excluded_parent", return_value=False
        ), patch.object(
            generator.command_generator, "generate_cleanup_directories_command"
        ) as mock_cmd:

            mock_cmd.return_value = {"cmd": "cleanup dir"}

            result = generator._generate_directory_cleanup_commands(
                mock_pyro_config, compared
            )

            assert len(result) == 1
            mock_cmd.assert_called_once()

    def test_generate_directory_cleanup_commands_excluded_parent(
        self, mock_stdout, mock_pyro_config
    ):
        """Test directory cleanup with excluded parent."""
        generator = SketchGenerator(stdout=mock_stdout)

        compared = {"extra_directories": [{"path": "/excluded/dir1"}]}

        with patch.object(
            generator.exclusion_checker, "should_exclude_path", return_value=False
        ), patch.object(
            generator.exclusion_checker, "has_excluded_parent", return_value=True
        ):

            result = generator._generate_directory_cleanup_commands(
                mock_pyro_config, compared
            )

            # Should be excluded due to parent
            assert result == []

    def test_generate_file_cleanup_commands(self, mock_stdout, mock_pyro_config):
        """Test file and symlink cleanup command generation."""
        generator = SketchGenerator(stdout=mock_stdout)

        compared = {
            "extra_files": [{"path": "/file1"}],
            "extra_symlinks": [{"path": "/link1"}],
        }

        with patch.object(
            generator.exclusion_checker, "should_exclude_path", return_value=False
        ), patch.object(
            generator.exclusion_checker, "has_excluded_parent", return_value=False
        ), patch.object(
            generator.command_generator, "generate_cleanup_files_command"
        ) as mock_cmd:

            mock_cmd.return_value = {"cmd": "cleanup files"}

            result = generator._generate_file_cleanup_commands(
                mock_pyro_config, compared
            )

            assert len(result) == 1
            # Should combine files and symlinks
            mock_cmd.assert_called_once()

    def test_generate_filesystem_cleanup_commands(self, mock_stdout, mock_pyro_config):
        """Test complete filesystem cleanup command generation."""
        generator = SketchGenerator(stdout=mock_stdout)

        compared = {}

        with patch.object(
            generator, "_generate_directory_cleanup_commands"
        ) as mock_dirs, patch.object(
            generator, "_generate_file_cleanup_commands"
        ) as mock_files:

            mock_dirs.return_value = [{"dir": "cleanup"}]
            mock_files.return_value = [{"file": "cleanup"}]

            result = generator._generate_filesystem_cleanup_commands(
                mock_pyro_config, compared
            )

            assert len(result) == 2
            mock_dirs.assert_called_once_with(mock_pyro_config, compared)
            mock_files.assert_called_once_with(mock_pyro_config, compared)


class TestConfigureSketchGeneration:
    """Test configure sketch generation."""

    #   # TODO
    #   def test_generate_device_commands(self, mock_stdout, mock_device):
    #       """Test device command generation."""
    #   def test_generate_filesystem_structure_commands(self, mock_stdout, mock_device):
    #       """Test filesystem structure command generation."""
    #   def test_generate_filesystem_structure_commands_invalid_entry(self, mock_stdout, mock_device):
    #       """Test filesystem structure with invalid entry."""
    #   def test_generate_filesystem_structure_commands_excluded(self, mock_stdout, mock_device):
    #       """Test filesystem structure with excluded entry."""
    #   def test_should_exclude_filesystem_entry(self, mock_stdout):
    #       """Test filesystem entry exclusion."""
    #   def test_should_exclude_filesystem_entry_excluded(self, mock_stdout):
    #       """Test filesystem entry that should be excluded."""

    def test_generate_configure_sketch(self, mock_stdout, mock_pyro_config):
        """Test configure sketch generation."""
        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(
            generator, "_generate_user_commands"
        ) as mock_users, patch.object(
            generator, "_generate_group_commands"
        ) as mock_groups, patch.object(
            generator, "_generate_device_commands"
        ) as mock_devices:

            mock_users.return_value = [{"user": "command"}]
            mock_groups.return_value = [{"group": "command"}]
            mock_devices.return_value = [{"device": "command"}]

            result = generator.generate_configure_sketch(mock_pyro_config)

            assert "name" in result
            assert (
                result["name"]
                == f"Pyroform Auto-Generated Sketch {mock_pyro_config.label}"
            )
            assert "Users" in result
            assert "Groups" in result
            assert "Devices" in result

            mock_stdout.info.assert_called_once()

    def test_generate_configure_sketch_empty_sections(
        self, mock_stdout, empty_pyro_config
    ):
        """Test configure sketch with empty sections."""
        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(
            generator, "_generate_user_commands", return_value=[]
        ), patch.object(
            generator, "_generate_group_commands", return_value=[]
        ), patch.object(
            generator, "_generate_device_commands", return_value=[]
        ):

            result = generator.generate_configure_sketch(empty_pyro_config)

            # Should only have name field
            assert list(result.keys()) == ["name"]

    def test_generate_user_commands(self, mock_stdout, mock_user):
        """Test user command generation."""
        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(
            generator.exclusion_checker, "should_exclude_user", return_value=False
        ), patch.object(
            generator.command_generator, "generate_user_command"
        ) as mock_cmd:

            mock_cmd.return_value = {"cmd": "useradd"}

            result = generator._generate_user_commands([mock_user], ["excluded_user"])

            assert len(result) == 1
            generator.exclusion_checker.should_exclude_user.assert_called_once_with(
                mock_user.name, ["excluded_user"]
            )
            mock_cmd.assert_called_once_with(mock_user)

    def test_generate_user_commands_excluded(self, mock_stdout, mock_user):
        """Test user command generation with excluded user."""
        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(
            generator.exclusion_checker, "should_exclude_user", return_value=True
        ):
            result = generator._generate_user_commands([mock_user], ["excluded_user"])

            assert result == []

    def test_generate_group_commands(self, mock_stdout, mock_group):
        """Test group command generation."""
        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(
            generator.exclusion_checker, "should_exclude_group", return_value=False
        ), patch.object(
            generator.command_generator, "generate_group_command"
        ) as mock_cmd:

            mock_cmd.return_value = {"cmd": "groupadd"}

            result = generator._generate_group_commands(
                [mock_group], ["excluded_group"]
            )

            assert len(result) == 1

    def test_generate_mount_commands(self, mock_stdout, mock_device):
        """Test mount command generation."""
        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(
            generator.exclusion_checker, "should_exclude_device", return_value=False
        ), patch.object(
            generator.command_generator, "generate_mountpoint_command"
        ) as mock_mountpoint, patch.object(
            generator.command_generator, "generate_mount_command"
        ) as mock_mount:

            mock_mountpoint.return_value = {"cmd": "mkdir"}
            mock_mount.return_value = {"cmd": "mount"}

            result = generator._generate_mount_commands(
                [mock_device], ["/dev/excluded"]
            )

            assert len(result) == 2  # mountpoint + mount
            mock_mountpoint.assert_called_once_with(mock_device)
            mock_mount.assert_called_once_with(mock_device)

    def test_generate_mount_commands_no_mountpoint(self, mock_stdout, mock_device):
        """Test mount command generation without mountpoint."""
        mock_device.mountpoint = None
        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(
            generator.exclusion_checker, "should_exclude_device", return_value=False
        ):
            result = generator._generate_mount_commands([mock_device], [])

            # Should not generate mountpoint or mount commands
            assert result == []

    def test_generate_mount_commands_excluded(self, mock_stdout, mock_device):
        """Test mount command generation with excluded device."""
        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(
            generator.exclusion_checker, "should_exclude_device", return_value=True
        ):
            result = generator._generate_mount_commands(
                [mock_device], ["/dev/excluded"]
            )

            assert result == []

    def test_generate_device_commands_excluded(
        self, mock_stdout, mock_device, mock_pyro_config
    ):
        """Test device command generation with excluded device."""
        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(
            generator.exclusion_checker, "should_exclude_device", return_value=True
        ):
            result = generator._generate_device_commands(
                [mock_device], mock_pyro_config.excludes
            )

            assert result == []

    def test_generate_creation_command_directory(self, mock_stdout):
        """Test creation command generation for directory."""
        generator = SketchGenerator(stdout=mock_stdout)

        parsed_entry = {"type": "dir", "path": "/test"}

        with patch.object(
            generator.command_generator, "generate_directory_command"
        ) as mock_cmd:
            mock_cmd.return_value = {"cmd": "mkdir"}

            result = generator._generate_creation_command(parsed_entry)

            assert result == {"cmd": "mkdir"}
            mock_cmd.assert_called_once_with("/test")

    def test_generate_creation_command_file(self, mock_stdout):
        """Test creation command generation for file."""
        generator = SketchGenerator(stdout=mock_stdout)

        parsed_entry = {"type": "fl", "path": "/test.txt"}

        with patch.object(
            generator.command_generator, "generate_file_command"
        ) as mock_cmd:
            mock_cmd.return_value = {"cmd": "touch"}

            result = generator._generate_creation_command(parsed_entry)

            mock_cmd.assert_called_once_with("/test.txt")

    def test_generate_creation_command_symlink(self, mock_stdout):
        """Test creation command generation for symlink."""
        parsed_entry = {"type": "ln", "path": "/link", "target": "/target"}

        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(
            generator.command_generator, "generate_symlink_command"
        ) as mock_cmd:
            mock_cmd.return_value = {"cmd": "ln -s"}

            result = generator._generate_creation_command(parsed_entry)

            mock_cmd.assert_called_once_with("/link", "/target")

    def test_generate_creation_command_unknown_type(self, mock_stdout):
        """Test creation command generation for unknown type."""
        generator = SketchGenerator(stdout=mock_stdout)

        parsed_entry = {"type": "unknown", "path": "/test"}

        result = generator._generate_creation_command(parsed_entry)

        assert result is None


class TestMountSketchGeneration:
    """Test mount sketch generation."""

    def test_generate_mount_sketch(self, mock_stdout, mock_pyro_config):
        """Test mount sketch generation."""
        generator = SketchGenerator(stdout=mock_stdout)

        with patch.object(generator, "_generate_mount_commands") as mock_mount:
            mock_mount.return_value = [{"mount": "cmd"}]

            result = generator.generate_mount_sketch(mock_pyro_config)

            assert "name" in result
            assert "Devices" in result
            assert result["Devices"] == [{"mount": "cmd"}]
            mock_mount.assert_called_once_with(
                mock_pyro_config.devices, mock_pyro_config.excludes.devices
            )

    def test_generate_mount_sketch_no_devices(self, mock_stdout, empty_pyro_config):
        """Test mount sketch generation with no devices."""
        generator = SketchGenerator(stdout=mock_stdout)

        result = generator.generate_mount_sketch(empty_pyro_config)

        assert result == {"name": "Pyroform Auto-Generated Sketch empty_config"}


class TestSaveSketch:
    """Test the save_sketch method."""

    #   # TODO
    #   def test_save_sketch_success(self, mock_json_dump, mock_file, mock_stdout):
    #       """Test successful sketch saving."""

    @patch("builtins.open")
    def test_save_sketch_io_error(self, mock_open, mock_stdout):
        """Test sketch saving with IO error."""
        mock_open.side_effect = IOError("Permission denied")
        generator = SketchGenerator(stdout=mock_stdout)

        result = generator.save_sketch({}, Path("/protected/path.json"))

        assert result == False
        mock_stdout.err.assert_called_once()

    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_sketch_type_error(self, mock_file, mock_json_dump, mock_stdout):
        """Test sketch saving with type error."""
        mock_json_dump.side_effect = TypeError("Invalid JSON")
        generator = SketchGenerator(stdout=mock_stdout)

        result = generator.save_sketch({"invalid": object()}, Path("/tmp/test.json"))

        assert result == False
        mock_stdout.err.assert_called_once()

    def test_save_sketch_none_path(self, mock_stdout):
        """Test sketch saving with None path."""
        generator = SketchGenerator(stdout=mock_stdout)

        with pytest.raises(AttributeError):
            generator.save_sketch({}, None)


class TestIntegration:
    """Integration tests for complete sketch generation scenarios."""

    #   # TODO
    #   def test_complete_scorch_workflow(self, mock_stdout, mock_pyro_config, system_state):
    #       """Test complete scorch sketch generation workflow."""
    #   def test_empty_config_handling(self, mock_stdout):
    #       """Test sketch generation with empty config."""

    def test_complete_configure_workflow(self, mock_stdout, mock_pyro_config):
        """Test complete configure sketch generation workflow."""
        generator = SketchGenerator(stdout=mock_stdout)

        # Mock all internal calls
        with patch.object(
            generator.command_generator, "generate_user_command"
        ) as mock_user_cmd, patch.object(
            generator.command_generator, "generate_group_command"
        ) as mock_group_cmd, patch.object(
            generator.command_generator, "generate_mountpoint_command"
        ) as mock_mountpoint, patch.object(
            generator.command_generator, "generate_mount_command"
        ) as mock_mount, patch.object(
            generator.command_generator, "generate_directory_command"
        ) as mock_dir, patch.object(
            generator.command_generator, "generate_file_command"
        ) as mock_file, patch.object(
            generator.command_generator, "generate_symlink_command"
        ) as mock_link, patch.object(
            generator.command_generator, "generate_permission_command"
        ) as mock_perm:

            # Setup mock returns
            mock_user_cmd.return_value = {"name": "Create user"}
            mock_group_cmd.return_value = {"name": "Create group"}
            mock_mountpoint.return_value = {"name": "Create mountpoint"}
            mock_mount.return_value = {"name": "Mount device"}
            mock_dir.return_value = {"name": "Create directory"}
            mock_file.return_value = {"name": "Create file"}
            mock_link.return_value = {"name": "Create symlink"}
            mock_perm.return_value = {"name": "Set permissions"}

            # Generate sketch
            sketch = generator.generate_configure_sketch(mock_pyro_config)

            # Verify sketch structure
            assert "name" in sketch
            assert "Users" in sketch
            assert "Groups" in sketch
            assert "Devices" in sketch

            # Should have debug output
            mock_stdout.info.assert_called()


class TestEdgeCases:
    """Test edge cases and error handling."""

    #   # TODO
    #   def test_has_excluded_parent_empty_path(self, mock_stdout):
    #       """Test parent exclusion with empty path."""
    #   def test_sketch_generator_empty_device_state(self, mock_stdout):
    #       """Test device command generation with empty state."""

    def test_generate_sketch_none_action(self, mock_stdout, mock_pyro_config):
        """Test generate_sketch with None action."""
        generator = SketchGenerator(stdout=mock_stdout)

        with pytest.raises(ValueError):
            generator.generate_sketch(mock_pyro_config, None)

    def test_empty_state_entry_parsing(self, mock_stdout):
        """Test parsing of empty or malformed state entries."""
        parser = StateEntryParser()

        assert parser.parse_state_entry("") is None
        assert parser.parse_state_entry(",") is None
        assert parser.parse_state_entry("dir") is None

    def test_exclusion_with_none_lists(self, mock_stdout):
        """Test exclusion checks with None exclude lists."""
        checker = ExclusionChecker(stdout=mock_stdout)

        # All should return False with None
        assert checker.should_exclude_user("test", None) == False
        assert checker.should_exclude_group("test", None) == False
        assert checker.should_exclude_device("/dev/test", None) == False
        assert checker.should_exclude_path("/test", None) == False

    def test_command_generator_empty_inputs(self):
        """Test command generation with empty inputs."""
        generator = CommandGenerator()

        # Test with empty strings
        user = Mock(spec=User)
        user.name = ""
        user.password = ""
        user.groups = []

        command = generator.generate_user_command(user)
        assert isinstance(command, dict)  # Should still generate command

        # Test cleanup with empty string
        command = generator.generate_cleanup_user_command("")
        assert isinstance(command, dict)

    def test_save_sketch_invalid_json(self, mock_stdout):
        """Test saving sketch with unserializable content."""
        generator = SketchGenerator(stdout=mock_stdout)

        # Create sketch with unserializable object
        sketch = {"name": "test", "data": object()}  # Not JSON serializable

        result = generator.save_sketch(sketch, Path("/tmp/test.json"))

        assert result == False
        mock_stdout.err.assert_called_once()


class TestDryRunMode:
    """Test dry run mode functionality."""

    # TODO
#   def test_dry_run_configure_sketch(self, mock_stdout, mock_pyro_config):
#       """Test configure sketch generation in dry run mode."""

    def test_dry_run_cleanup_commands(self, mock_stdout, mock_pyro_config):
        """Test cleanup command generation in dry run mode."""
        generator = SketchGenerator(stdout=mock_stdout, dry_run=True)

        compared = {"extra_users": [{"username": "test"}]}

        with patch.object(
            generator.exclusion_checker, "should_exclude_user", return_value=False
        ), patch.object(
            generator.command_generator, "generate_cleanup_user_command"
        ) as mock_cmd:

            mock_cmd.return_value = {"cmd": "# userdel"}  # Should have prefix

            commands = generator._generate_user_cleanup_commands(
                mock_pyro_config, compared
            )

            assert len(commands) == 1
            assert commands[0]["cmd"].startswith("# ")


class TestChunkSizeHandling:
    """Test chunk size handling in sketch generation."""

    def test_chunking_large_user_list(self, mock_stdout, mock_pyro_config):
        """Test chunking of large user lists."""
        generator = SketchGenerator(stdout=mock_stdout, chunk_size=2)

        compared = {
            "extra_users": [
                {"username": "user1"},
                {"username": "user2"},
                {"username": "user3"},
                {"username": "user4"},
            ]
        }

        with patch.object(
            generator.exclusion_checker, "should_exclude_user", return_value=False
        ), patch.object(generator.list_splitter, "split") as mock_split:

            mock_split.return_value = [["user1", "user2"], ["user3", "user4"]]

            commands = generator._generate_user_cleanup_commands(
                mock_pyro_config, compared
            )

            # Should split into 2 chunks
            mock_split.assert_called_once_with(["user1", "user2", "user3", "user4"])

    def test_no_chunking_small_list(self, mock_stdout, mock_pyro_config):
        """Test that small lists are not chunked."""
        generator = SketchGenerator(stdout=mock_stdout, chunk_size=500)

        compared = {"extra_users": [{"username": "user1"}, {"username": "user2"}]}

        with patch.object(
            generator.exclusion_checker, "should_exclude_user", return_value=False
        ):
            commands = generator._generate_user_cleanup_commands(
                mock_pyro_config, compared
            )

            # Should not use splitter for small list
            assert len(commands) > 0


if __name__ == "__main__":
    # This allows running the test file directly
    pytest.main([__file__, "-v", "--tb=short"])
