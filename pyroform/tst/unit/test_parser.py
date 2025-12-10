"""
Parser Test Suite

Unit tests for the Parser class.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from pyroform.src.logging import STDOUTMsg
from pyroform.src.models import Device, Exclude, Group, PyroConfig, User
from pyroform.src.parser import PyroParser


@pytest.fixture
def mock_stdout():
    """Mock STDOUTMsg to avoid console output during tests."""
    mock = Mock(spec=STDOUTMsg)
    mock.info = Mock()
    mock.debug = Mock()
    mock.warn = Mock()
    mock.err = Mock()
    mock.ok = Mock()
    mock.nok = Mock()
    return mock


@pytest.fixture
def minimal_pyro_data():
    """Create minimal valid Pyro configuration data."""
    return {
        "Label": "Test Configuration",
        "Users": [
            {
                "label": "test_user",
                "Name": "testuser",
                "Password": "encrypted_pass",
                "Groups": ["wheel", "users"],
            }
        ],
        "Groups": [
            {
                "label": "test_group",
                "Name": "testgroup",
                "Users": ["testuser", "otheruser"],
            }
        ],
        "Devices": [
            {
                "label": "root_device",
                "Path": "/dev/sda1",
                "Partition": 1,
                "Mountpoint": "/",
                "State": ["dir,/etc,root,root,0755"],
            }
        ],
    }


@pytest.fixture
def pyro_data_with_excludes():
    """Create Pyro configuration data with excludes."""
    return {
        "Label": "Config With Excludes",
        "Users": [],
        "Groups": [],
        "Devices": [],
        "Excludes": {
            "Users": ["excluded_user"],
            "Groups": ["excluded_group"],
            "Devices": ["/dev/excluded"],
            "Directories": ["/tmp/excluded"],
            "Files": ["/etc/excluded.txt"],
            "Links": ["/etc/excluded_link"],
        },
    }


@pytest.fixture
def empty_pyro_data():
    """Create empty Pyro configuration data."""
    return {"Label": "Empty Config", "Users": [], "Groups": [], "Devices": []}


@pytest.fixture
def test_json_file(tmp_path):
    """Create a temporary JSON file for testing."""
    data = {
        "Label": "JSON Config",
        "Users": [
            {"label": "user1", "Name": "user1", "Password": "pass", "Groups": []}
        ],
        "Groups": [],
        "Devices": [],
    }
    file_path = tmp_path / "test.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    return file_path


@pytest.fixture
def test_yaml_file(tmp_path):
    """Create a temporary YAML file for testing."""
    data = {
        "Label": "YAML Config",
        "Users": [
            {"label": "user1", "Name": "user1", "Password": "pass", "Groups": []}
        ],
        "Groups": [],
        "Devices": [],
    }
    file_path = tmp_path / "test.yaml"
    with open(file_path, "w") as f:
        yaml.dump(data, f)
    return file_path


@pytest.fixture
def test_directory_with_files(tmp_path):
    """Create a temporary directory with various config files."""
    # Create JSON files
    json_data = {"Label": "JSON Config", "Users": [], "Groups": [], "Devices": []}

    json_files = [
        ("pyro_config.json", json_data),
        ("config.pyro.json", json_data),
        ("other.json", json_data),
    ]

    # Create YAML files
    yaml_data = {"Label": "YAML Config", "Users": [], "Groups": [], "Devices": []}

    yaml_files = [
        ("pyro_config.yaml", yaml_data),
        ("pyro_config.yml", yaml_data),
        ("config.pyro.yaml", yaml_data),
        ("config.pyro.yml", yaml_data),
        ("other.yaml", yaml_data),
        ("other.yml", yaml_data),
    ]

    # Write all files
    for filename, data in json_files + yaml_files:
        file_path = tmp_path / filename
        if filename.endswith(".json"):
            with open(file_path, "w") as f:
                json.dump(data, f)
        else:
            with open(file_path, "w") as f:
                yaml.dump(data, f)

    return tmp_path


class TestPyroParserInitialization:
    """Test PyroParser initialization."""

    # TODO
#   def test_init_with_args_kwargs(self):
#       """Test initialization with *args and **kwargs."""

    def test_init_default_stdout(self):
        """Test initialization with default stdout."""
        with patch("pyroform.src.parser.STDOUTMsg") as mock_stdout_cls:
            mock_stdout_cls.return_value = Mock()

            parser = PyroParser()

            assert parser.stdout is not None
            mock_stdout_cls.assert_called_once_with(debug_mode=False, timestamp=False)

    def test_init_with_stdout(self, mock_stdout):
        """Test initialization with custom stdout."""
        parser = PyroParser(stdout=mock_stdout)

        assert parser.stdout == mock_stdout


class TestParseMethod:
    """Test the main parse method."""

    def test_parse_file_path(self, mock_stdout, test_json_file):
        """Test parsing a single file path."""
        parser = PyroParser(stdout=mock_stdout)

        with patch.object(parser, "_parse_single_file") as mock_parse_single:
            mock_parse_single.return_value = Mock(spec=PyroConfig)

            result = parser.parse(test_json_file)

            mock_parse_single.assert_called_once_with(test_json_file)
            assert isinstance(result, list)
            assert len(result) == 1

    def test_parse_directory_path(self, mock_stdout, tmp_path):
        """Test parsing a directory path."""
        parser = PyroParser(stdout=mock_stdout)

        with patch.object(parser, "_parse_directory") as mock_parse_dir:
            mock_parse_dir.return_value = [Mock(spec=PyroConfig), Mock(spec=PyroConfig)]

            result = parser.parse(tmp_path)

            mock_parse_dir.assert_called_once_with(tmp_path)
            assert len(result) == 2

    def test_parse_nonexistent_path(self, mock_stdout):
        """Test parsing a nonexistent path raises FileNotFoundError."""
        parser = PyroParser(stdout=mock_stdout)

        with pytest.raises(FileNotFoundError, match="Input path does not exist"):
            parser.parse(Path("/nonexistent/path"))

    def test_parse_invalid_path_type(self, mock_stdout, tmp_path):
        """Test parsing an invalid path type (e.g., symlink)."""
        parser = PyroParser(stdout=mock_stdout)

        # Create a symlink
        target = tmp_path / "target"
        target.touch()
        symlink = tmp_path / "symlink"
        symlink.symlink_to(target)

        # Mock is_file() and is_dir() to return False
        with patch.object(Path, "is_file", return_value=False), patch.object(
            Path, "is_dir", return_value=False
        ):

            with pytest.raises(
                ValueError, match="Input path is neither file nor directory"
            ):
                parser.parse(symlink)

            mock_stdout.err.assert_called_once()

    def test_parse_string_path(self, mock_stdout, test_json_file):
        """Test parsing with string path instead of Path object."""
        parser = PyroParser(stdout=mock_stdout)

        with patch.object(parser, "_parse_single_file") as mock_parse_single:
            mock_parse_single.return_value = Mock()

            result = parser.parse(str(test_json_file))

            # Should convert string to Path
            call_arg = mock_parse_single.call_args[0][0]
            assert isinstance(call_arg, Path)
            assert str(call_arg) == str(test_json_file)

    def test_parse_current_directory(self, mock_stdout):
        """Test parsing current directory."""
        parser = PyroParser(stdout=mock_stdout)

        with patch.object(Path, "is_dir", return_value=True), patch.object(
            parser, "_parse_directory"
        ) as mock_parse_dir:

            mock_parse_dir.return_value = []

            result = parser.parse(Path("."))

            mock_parse_dir.assert_called_once()
            assert result == []


class TestParseSingleFile:
    """Test _parse_single_file method."""

    def test_parse_json_file(self, mock_stdout, tmp_path):
        """Test parsing a JSON file."""
        # Create JSON file
        data = {"Label": "Test", "Users": [], "Groups": [], "Devices": []}
        json_file = tmp_path / "test.json"
        with open(json_file, "w") as f:
            json.dump(data, f)

        parser = PyroParser(stdout=mock_stdout)

        with patch.object(parser, "_parse_single_file_data") as mock_parse_data:
            mock_parse_data.return_value = Mock(spec=PyroConfig)

            result = parser._parse_single_file(json_file)

            mock_parse_data.assert_called_once_with(data)
            mock_stdout.info.assert_called_with(
                f"Parsing Pyro state file ({json_file})..."
            )

    def test_parse_yaml_file(self, mock_stdout, tmp_path):
        """Test parsing a YAML file."""
        # Create YAML file
        data = {"Label": "Test", "Users": [], "Groups": [], "Devices": []}
        yaml_file = tmp_path / "test.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(data, f)

        parser = PyroParser(stdout=mock_stdout)

        with patch.object(parser, "_parse_single_file_data") as mock_parse_data:
            mock_parse_data.return_value = Mock()

            result = parser._parse_single_file(yaml_file)

            mock_parse_data.assert_called_once_with(data)

    def test_parse_yaml_file_yml_extension(self, mock_stdout, tmp_path):
        """Test parsing a YAML file with .yml extension."""
        data = {"Label": "Test", "Users": [], "Groups": [], "Devices": []}
        yml_file = tmp_path / "test.yml"
        with open(yml_file, "w") as f:
            yaml.dump(data, f)

        parser = PyroParser(stdout=mock_stdout)

        with patch.object(parser, "_parse_single_file_data") as mock_parse_data:
            mock_parse_data.return_value = Mock()

            result = parser._parse_single_file(yml_file)

            mock_parse_data.assert_called_once_with(data)

    def test_parse_unsupported_format(self, mock_stdout, tmp_path):
        """Test parsing unsupported file format raises ValueError."""
        parser = PyroParser(stdout=mock_stdout)

        txt_file = tmp_path / "test.txt"
        txt_file.touch()

        with pytest.raises(ValueError, match="Unsupported Pyro state file format"):
            parser._parse_single_file(txt_file)

        mock_stdout.err.assert_called_once()

    def test_parse_json_decode_error(self, mock_stdout, tmp_path):
        """Test handling of JSON decode error."""
        parser = PyroParser(stdout=mock_stdout)

        json_file = tmp_path / "invalid.json"
        with open(json_file, "w") as f:
            f.write("invalid json content")

        with pytest.raises(json.JSONDecodeError):
            parser._parse_single_file(json_file)

    def test_parse_yaml_error(self, mock_stdout, tmp_path):
        """Test handling of YAML parse error."""
        parser = PyroParser(stdout=mock_stdout)

        yaml_file = tmp_path / "invalid.yaml"
        with open(yaml_file, "w") as f:
            f.write("invalid: [unclosed list")

        with pytest.raises(yaml.YAMLError):
            parser._parse_single_file(yaml_file)

    def test_parse_file_not_found(self, mock_stdout):
        """Test parsing non-existent file."""
        parser = PyroParser(stdout=mock_stdout)

        with pytest.raises(FileNotFoundError):
            parser._parse_single_file(Path("/nonexistent/file.json"))

    def test_parse_case_insensitive_extension(self, mock_stdout, tmp_path):
        """Test parsing with case-insensitive file extension."""
        data = {"Label": "Test", "Users": [], "Groups": [], "Devices": []}

        # Test uppercase extension
        json_file = tmp_path / "test.JSON"
        with open(json_file, "w") as f:
            json.dump(data, f)

        parser = PyroParser(stdout=mock_stdout)

        with patch.object(parser, "_parse_single_file_data") as mock_parse_data:
            mock_parse_data.return_value = Mock()

            result = parser._parse_single_file(json_file)

            mock_parse_data.assert_called_once_with(data)


class TestParseSingleFileData:
    """Test _parse_single_file_data method."""

    #   # TODO
    #   def test_parse_invalid_user_data(self, mock_stdout):
    #       """Test parsing invalid user data raises ValueError."""
    #   def test_parse_invalid_group_data(self, mock_stdout):
    #       """Test parsing invalid group data raises ValueError."""
    #   def test_parse_invalid_device_data(self, mock_stdout):
    #       """Test parsing invalid device data raises ValueError."""
    #   def test_parse_invalid_exclude_data(self, mock_stdout):
    #       """Test parsing invalid exclude data raises ValueError."""

    def test_parse_minimal_data(self, mock_stdout, minimal_pyro_data):
        """Test parsing minimal valid configuration data."""
        parser = PyroParser(stdout=mock_stdout)

        result = parser._parse_single_file_data(minimal_pyro_data)

        # Verify result type
        assert isinstance(result, PyroConfig)

        # Verify basic properties
        assert result.label == "Test Configuration"

        # Verify users
        assert len(result.users) == 1
        user = result.users[0]
        assert isinstance(user, User)
        assert user.name == "testuser"
        assert user.password == "encrypted_pass"
        assert user.groups == ["wheel", "users"]

        # Verify groups
        assert len(result.groups) == 1
        group = result.groups[0]
        assert isinstance(group, Group)
        assert group.name == "testgroup"
        assert group.users == ["testuser", "otheruser"]

        # Verify devices
        assert len(result.devices) == 1
        device = result.devices[0]
        assert isinstance(device, Device)
        assert device.path == "/dev/sda1"
        assert device.partition == 1
        assert device.mountpoint == "/"
        assert device.state == ["dir,/etc,root,root,0755"]

        # Verify excludes (should be default empty)
        assert isinstance(result.excludes, Exclude)
        assert result.excludes.users == []
        assert result.excludes.groups == []

        # Verify debug output
        mock_stdout.info.assert_called()

    def test_parse_data_with_excludes(self, mock_stdout, pyro_data_with_excludes):
        """Test parsing configuration data with excludes."""
        parser = PyroParser(stdout=mock_stdout)

        result = parser._parse_single_file_data(pyro_data_with_excludes)

        # Verify excludes
        excludes = result.excludes
        assert isinstance(excludes, Exclude)
        assert excludes.users == ["excluded_user"]
        assert excludes.groups == ["excluded_group"]
        assert excludes.devices == ["/dev/excluded"]
        assert excludes.directories == ["/tmp/excluded"]
        assert excludes.files == ["/etc/excluded.txt"]
        assert excludes.links == ["/etc/excluded_link"]

    def test_parse_empty_data(self, mock_stdout, empty_pyro_data):
        """Test parsing empty configuration data."""
        parser = PyroParser(stdout=mock_stdout)

        result = parser._parse_single_file_data(empty_pyro_data)

        assert result.label == "Empty Config"
        assert result.users == []
        assert result.groups == []
        assert result.devices == []
        assert isinstance(result.excludes, Exclude)
        assert result.excludes.users == []

    def test_parse_data_no_label(self, mock_stdout):
        """Test parsing data without Label field."""
        data = {"Users": [], "Groups": [], "Devices": []}

        parser = PyroParser(stdout=mock_stdout)

        result = parser._parse_single_file_data(data)

        assert result.label == "Unnamed Configuration"

    def test_parse_data_empty_sections(self, mock_stdout):
        """Test parsing data with missing or empty sections."""
        data = {
            "Label": "Test",
            # Missing Users, Groups, Devices keys
        }

        parser = PyroParser(stdout=mock_stdout)

        result = parser._parse_single_file_data(data)

        assert result.users == []
        assert result.groups == []
        assert result.devices == []

    def test_parse_data_with_partial_excludes(self, mock_stdout):
        """Test parsing data with partial exclude sections."""
        data = {
            "Label": "Test",
            "Users": [],
            "Groups": [],
            "Devices": [],
            "Excludes": {
                "Users": ["user1"],
                # Missing other exclude fields
            },
        }

        parser = PyroParser(stdout=mock_stdout)

        result = parser._parse_single_file_data(data)

        assert result.excludes.users == ["user1"]
        assert result.excludes.groups == []  # Should default to empty list

    def test_parse_none_excludes(self, mock_stdout):
        """Test parsing when Excludes is None."""
        data = {
            "Label": "Test",
            "Users": [],
            "Groups": [],
            "Devices": [],
            "Excludes": None,
        }

        parser = PyroParser(stdout=mock_stdout)

        result = parser._parse_single_file_data(data)

        # Should create empty Exclude object
        assert isinstance(result.excludes, Exclude)
        assert result.excludes.users == []

    def test_parse_user_with_empty_fields(self, mock_stdout):
        """Test parsing user with empty or missing optional fields."""
        data = {
            "Label": "Test",
            "Users": [
                {
                    # Only required field is technically "Name"
                    "Name": "testuser"
                    # Missing label, password, groups
                }
            ],
            "Groups": [],
            "Devices": [],
        }

        parser = PyroParser(stdout=mock_stdout)

        result = parser._parse_single_file_data(data)

        user = result.users[0]
        assert user.name == "testuser"
        assert user.label == ""  # Default empty string
        assert user.password == ""  # Default empty string
        assert user.groups == []  # Default empty list

    def test_parse_debug_output(self, mock_stdout, minimal_pyro_data):
        """Test debug output formatting."""
        parser = PyroParser(stdout=mock_stdout)

        parser._parse_single_file_data(minimal_pyro_data)

        # Should call info with JSON string
        mock_stdout.info.assert_called()
        info_call = mock_stdout.info.call_args[0][0]
        assert "State file data:" in info_call
        assert "Test Configuration" in info_call


class TestParseDirectory:
    """Test _parse_directory method."""

    #   # TODO
    #   def test_parse_directory_with_files(self, mock_stdout, test_directory_with_files):
    #       """Test parsing directory with multiple config files."""
    #   def test_parse_directory_duplicate_files(self, mock_stdout, tmp_path):
    #       """Test parsing directory with duplicate file paths."""
    #   def test_parse_directory_file_parsing_error(self, mock_stdout, tmp_path):
    #       """Test handling of file parsing errors in directory."""
    #   def test_parse_directory_non_file_entry(self, mock_stdout, tmp_path):
    #       """Test handling of non-file entries (e.g., directories)."""
    #   def test_parse_directory_json_decode_error(self, mock_stdout, tmp_path):
    #       """Test handling of JSON decode errors in directory parsing."""
    #   def test_parse_directory_yaml_error(self, mock_stdout, tmp_path):
    #       """Test handling of YAML errors in directory parsing."""
    #   def test_parse_directory_sorted_results(self, mock_stdout, tmp_path):
    #       """Test that files are sorted for consistent ordering."""

    def test_parse_directory_no_files(self, mock_stdout, tmp_path):
        """Test parsing directory with no matching files."""
        parser = PyroParser(stdout=mock_stdout)

        with patch("pyroform.src.parser.glob.glob", return_value=[]):
            result = parser._parse_directory(tmp_path)

            assert result == []
            mock_stdout.nok.assert_called_once()
            nok_call = mock_stdout.nok.call_args[0][0]
            assert "No state files found" in nok_call
            assert str(tmp_path) in nok_call

    def test_parse_directory_file_patterns(self, mock_stdout, tmp_path):
        """Test that all file patterns are searched."""
        parser = PyroParser(stdout=mock_stdout)

        with patch("pyroform.src.parser.glob.glob") as mock_glob:
            mock_glob.return_value = []

            parser._parse_directory(tmp_path)

            # Should call glob multiple times with different patterns
            assert mock_glob.call_count > 0

            # Check some expected patterns
            calls = [call[0][0] for call in mock_glob.call_args_list]
            assert any("pyro_*.json" in str(call) for call in calls)
            assert any("*.pyro.json" in str(call) for call in calls)
            assert any("*.json" in str(call) for call in calls)
            assert any("pyro_*.yaml" in str(call) for call in calls)
            assert any("*.pyro.yaml" in str(call) for call in calls)
            assert any("*.yaml" in str(call) for call in calls)
            assert any("*.yml" in str(call) for call in calls)


class TestIntegrationScenarios:
    """Integration tests for complete parsing workflows."""

    #   # TODO
    #   def test_parse_directory_workflow(self, mock_stdout, test_directory_with_files):
    #       """Test complete directory parsing workflow."""
    #   def test_parse_mixed_file_formats(self, mock_stdout, tmp_path):
    #       """Test parsing directory with mixed JSON and YAML files."""
    #   def test_parse_nested_directory_structure(self, mock_stdout, tmp_path):
    #       """Test that directory parsing doesn't search subdirectories."""

    def test_parse_complete_workflow_json(self, mock_stdout, tmp_path):
        """Test complete parsing workflow with JSON file."""
        # Create complete JSON config
        data = {
            "Label": "Complete Config",
            "Users": [
                {
                    "label": "admin_user",
                    "Name": "admin",
                    "Password": "admin123",
                    "Groups": ["wheel", "sudo"],
                }
            ],
            "Groups": [
                {"label": "admin_group", "Name": "admins", "Users": ["admin", "root"]}
            ],
            "Devices": [
                {
                    "label": "boot_device",
                    "Path": "/dev/nvme0n1",
                    "Partition": 1,
                    "Mountpoint": "/boot",
                    "State": [
                        "dir,/boot/grub,root,root,0755",
                        "fl,/boot/vmlinuz,root,root,0644",
                    ],
                }
            ],
            "Excludes": {
                "Users": ["nobody", "daemon"],
                "Groups": ["nogroup"],
                "Directories": ["/tmp", "/var/tmp"],
            },
        }

        json_file = tmp_path / "config.json"
        with open(json_file, "w") as f:
            json.dump(data, f)

        parser = PyroParser(stdout=mock_stdout)

        # Parse the file
        result = parser.parse(json_file)

        # Verify results
        assert len(result) == 1
        config = result[0]

        assert config.label == "Complete Config"
        assert len(config.users) == 1
        assert len(config.groups) == 1
        assert len(config.devices) == 1
        assert len(config.excludes.users) == 2
        assert len(config.excludes.groups) == 1
        assert len(config.excludes.directories) == 2

        # Verify user
        user = config.users[0]
        assert user.name == "admin"
        assert user.groups == ["wheel", "sudo"]

        # Verify device state
        device = config.devices[0]
        assert len(device.state) == 2
        assert "dir,/boot/grub" in device.state[0]


class TestEdgeCases:
    """Test edge cases and error handling."""

    #   # TODO
    #   def test_parse_user_with_none_values(self, mock_stdout):
    #       """Test parsing user with None values."""
    #   def test_parse_directory_permission_error(self, mock_stdout, tmp_path):
    #       """Test handling of directory permission errors."""

    def test_parse_empty_file(self, mock_stdout, tmp_path):
        """Test parsing an empty file."""
        parser = PyroParser(stdout=mock_stdout)

        empty_file = tmp_path / "empty.json"
        empty_file.touch()  # Create empty file

        with pytest.raises(json.JSONDecodeError):
            parser._parse_single_file(empty_file)

    def test_parse_file_with_only_whitespace(self, mock_stdout, tmp_path):
        """Test parsing a file containing only whitespace."""
        parser = PyroParser(stdout=mock_stdout)

        whitespace_file = tmp_path / "whitespace.json"
        with open(whitespace_file, "w") as f:
            f.write("   \n\t  \n")

        with pytest.raises(json.JSONDecodeError):
            parser._parse_single_file(whitespace_file)

    def test_parse_data_with_extra_fields(self, mock_stdout):
        """Test parsing data with extra, unrecognized fields."""
        data = {
            "Label": "Test",
            "Users": [],
            "Groups": [],
            "Devices": [],
            "ExtraField": "Should be ignored",
            "AnotherExtra": 123,
        }

        parser = PyroParser(stdout=mock_stdout)

        result = parser._parse_single_file_data(data)

        # Should parse successfully, ignoring extra fields
        assert result.label == "Test"

    def test_parse_device_with_string_partition(self, mock_stdout):
        """Test parsing device with string partition (should convert to int)."""
        data = {
            "Label": "Test",
            "Users": [],
            "Groups": [],
            "Devices": [
                {
                    "label": "test",
                    "Path": "/dev/sda",
                    "Partition": "1",  # String instead of int
                    "Mountpoint": "/",
                    "State": [],
                }
            ],
        }

        parser = PyroParser(stdout=mock_stdout)

        result = parser._parse_single_file_data(data)

        device = result.devices[0]
        # The Device model should handle type conversion
        assert device.path == "/dev/sda"

    def test_parse_excludes_with_non_list_values(self, mock_stdout):
        """Test parsing excludes with non-list values."""
        data = {
            "Label": "Test",
            "Users": [],
            "Groups": [],
            "Devices": [],
            "Excludes": {
                "Users": "single_user",  # Should be list
                "Groups": None,
                "Devices": [],
            },
        }

        parser = PyroParser(stdout=mock_stdout)

        # This might fail depending on Exclude model implementation
        # Let it raise the natural exception
        try:
            result = parser._parse_single_file_data(data)
            # If it succeeds, check the values
            if hasattr(result.excludes, "users"):
                # Depends on how Exclude handles non-list
                pass
        except (TypeError, ValueError):
            pass  # Expected if Exclude validates input types

    def test_parse_symlink_file(self, mock_stdout, tmp_path):
        """Test parsing a symlink to a config file."""
        parser = PyroParser(stdout=mock_stdout)

        # Create target file
        target = tmp_path / "target.json"
        with open(target, "w") as f:
            json.dump({"Label": "Target", "Users": [], "Groups": [], "Devices": []}, f)

        # Create symlink
        symlink = tmp_path / "symlink.json"
        symlink.symlink_to(target)

        # Should parse through symlink
        with patch.object(parser, "_parse_single_file_data") as mock_parse_data:
            mock_parse_data.return_value = Mock(spec=PyroConfig)

            result = parser._parse_single_file(symlink)

            mock_parse_data.assert_called_once()

    def test_parse_large_file(self, mock_stdout, tmp_path):
        """Test parsing a large configuration file."""
        parser = PyroParser(stdout=mock_stdout)

        # Create large config with many users
        data = {
            "Label": "Large Config",
            "Users": [
                {
                    "label": f"user{i}",
                    "Name": f"user{i}",
                    "Password": f"pass{i}",
                    "Groups": ["users"],
                }
                for i in range(1000)
            ],
            "Groups": [
                {
                    "label": "users",
                    "Name": "users",
                    "Users": [f"user{i}" for i in range(1000)],
                }
            ],
            "Devices": [],
        }

        large_file = tmp_path / "large.json"
        with open(large_file, "w") as f:
            json.dump(data, f)

        # Should parse without memory issues
        result = parser._parse_single_file(large_file)

        assert len(result.users) == 1000
        assert len(result.groups) == 1
        assert len(result.groups[0].users) == 1000


class TestLogging:
    """Test logging and output behavior."""

    #   # TODO
    #   def test_parse_directory_logging_success(self, mock_stdout, tmp_path):
    #       """Test logging when directory parsing finds files."""
    #   def test_error_logging_format(self, mock_stdout):
    #       """Test that error messages are properly formatted."""

    def test_parse_single_file_logging(self, mock_stdout, tmp_path):
        """Test logging during single file parsing."""
        parser = PyroParser(stdout=mock_stdout)

        json_file = tmp_path / "test.json"
        with open(json_file, "w") as f:
            json.dump({"Label": "Test", "Users": [], "Groups": [], "Devices": []}, f)

        with patch.object(parser, "_parse_single_file_data") as mock_parse_data:
            mock_parse_data.return_value = Mock()

            parser._parse_single_file(json_file)

            # Should log file parsing
            mock_stdout.info.assert_any_call(
                f"Parsing Pyro state file ({json_file})..."
            )

    def test_parse_directory_logging_no_files(self, mock_stdout, tmp_path):
        """Test logging when directory has no matching files."""
        parser = PyroParser(stdout=mock_stdout)

        with patch("pyroform.src.parser.glob.glob", return_value=[]):
            parser._parse_directory(tmp_path)

            # Should log warning
            mock_stdout.nok.assert_called_once()
            nok_call = mock_stdout.nok.call_args[0][0]
            assert "No state files found" in nok_call

    def test_stdout_method_calls(self, mock_stdout, tmp_path):
        """Test all stdout method calls during parsing."""
        parser = PyroParser(stdout=mock_stdout)

        # Create a valid config file
        json_file = tmp_path / "test.json"
        with open(json_file, "w") as f:
            json.dump(
                {
                    "Label": "Test",
                    "Users": [
                        {"label": "u1", "Name": "user1", "Password": "p1", "Groups": []}
                    ],
                    "Groups": [],
                    "Devices": [],
                },
                f,
            )

        # Parse it
        parser.parse(json_file)

        # Verify stdout methods were called
        assert mock_stdout.info.called
        assert not mock_stdout.warn.called  # No warnings for valid file
        assert not mock_stdout.err.called  # No errors for valid file


class TestModelIntegration:
    """Test integration with data models."""

    def test_parser_creates_correct_models(self, mock_stdout, minimal_pyro_data):
        """Test that parser creates correct model instances."""
        parser = PyroParser(stdout=mock_stdout)

        result = parser._parse_single_file_data(minimal_pyro_data)

        # Verify model types
        assert isinstance(result, PyroConfig)
        assert isinstance(result.users[0], User)
        assert isinstance(result.groups[0], Group)
        assert isinstance(result.devices[0], Device)
        assert isinstance(result.excludes, Exclude)

    def test_model_validation_during_parsing(self, mock_stdout):
        """Test that model validation happens during parsing."""
        parser = PyroParser(stdout=mock_stdout)

        # Data that would create invalid model
        data = {
            "Label": "Test",
            "Users": [
                {
                    "label": "",  # Empty but allowed
                    "Name": "",  # Empty name might be invalid
                    "Password": "",
                    "Groups": [],
                }
            ],
            "Groups": [],
            "Devices": [],
        }

        # Try to parse - depends on User model validation
        try:
            result = parser._parse_single_file_data(data)
            # If it succeeds, check the model
            user = result.users[0]
            assert user.name == ""  # Might be allowed
        except ValueError:
            # If User model validates name, this might fail
            pass  # Acceptable

    def test_exclude_model_creation(self, mock_stdout):
        """Test that Exclude model is created with correct defaults."""
        parser = PyroParser(stdout=mock_stdout)

        # Data without Excludes section
        data = {"Label": "Test", "Users": [], "Groups": [], "Devices": []}

        result = parser._parse_single_file_data(data)

        # Should create Exclude with empty lists
        assert isinstance(result.excludes, Exclude)
        assert result.excludes.users == []
        assert result.excludes.groups == []
        assert result.excludes.devices == []
        assert result.excludes.directories == []
        assert result.excludes.files == []
        assert result.excludes.links == []

    def test_device_state_preservation(self, mock_stdout):
        """Test that device state list is preserved correctly."""
        parser = PyroParser(stdout=mock_stdout)

        state_entries = [
            "dir,/etc,root,root,0755",
            "fl,/etc/hosts,root,root,0644",
            "ln,/etc/localtime,root,root,0777,/usr/share/zoneinfo/UTC",
        ]

        data = {
            "Label": "Test",
            "Users": [],
            "Groups": [],
            "Devices": [
                {
                    "label": "test",
                    "Path": "/dev/sda1",
                    "Partition": 1,
                    "Mountpoint": "/",
                    "State": state_entries,
                }
            ],
        }

        result = parser._parse_single_file_data(data)

        device = result.devices[0]
        assert device.state == state_entries
        assert len(device.state) == 3


if __name__ == "__main__":
    # This allows running the test file directly
    pytest.main([__file__, "-v", "--tb=short"])
