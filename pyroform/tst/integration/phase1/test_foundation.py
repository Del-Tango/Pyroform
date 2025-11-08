"""
Phase 1 Integration Tests: Foundation & Core Infrastructure
"""
import pytest
import json
import yaml
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from pyroform.src.models import PyroConfig, User, Group, Device, ActionType
from pyroform.src.parser import PyroParser
from pyroform.cli import main as cli_main


class TestPhase1Foundation:
    """Test foundation components work together"""

    @pytest.fixture
    def sample_pyro_config(self):
        """Sample Pyro configuration for testing"""
        return {
            "Label": "Test Configuration",
            "Users": [
                {
                    "label": "test_user",
                    "Name": "testuser",
                    "Password": "testpass123",
                    "Groups": ["testgroup"]
                }
            ],
            "Groups": [
                {
                    "label": "test_group",
                    "Name": "testgroup",
                    "Users": ["testuser"]
                }
            ],
            "Devices": [
                {
                    "label": "test_device",
                    "Path": "/dev/sdb1",
                    "Partition": 1,
                    "Mountpoint": "/mnt/test",
                    "State": [
                        "dir,/mnt/test/data,testuser,testgroup,755",
                        "fl,/mnt/test/data/file.txt,testuser,testgroup,644"
                    ]
                }
            ]
        }

    @pytest.fixture
    def temp_pyro_files(self, sample_pyro_config):
        """Create temporary Pyro files for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # JSON file
            json_file = Path(tmpdir) / "pyro_test.json"
            with open(json_file, 'w') as f:
                json.dump(sample_pyro_config, f)

            # YAML file
            yaml_file = Path(tmpdir) / "pyro_test.yaml"
            with open(yaml_file, 'w') as f:
                yaml.dump(sample_pyro_config, f)

            # Directory with multiple files
            multi_dir = Path(tmpdir) / "configs"
            multi_dir.mkdir()

            for i in range(3):
                multi_file = multi_dir / f"pyro_config_{i}.json"
                with open(multi_file, 'w') as f:
                    json.dump(sample_pyro_config, f)

            yield {
                'json_file': json_file,
                'yaml_file': yaml_file,
                'multi_dir': multi_dir,
                'tmpdir': tmpdir
            }

    def test_parser_integration(self, temp_pyro_files):
        """Test PyroParser can read various file formats"""
        parser = PyroParser()

        # Test single JSON file
        json_configs = parser.parse(temp_pyro_files['json_file'])
        assert len(json_configs) == 1
        assert json_configs[0].label == "Test Configuration"

        # Test single YAML file
        yaml_configs = parser.parse(temp_pyro_files['yaml_file'])
        assert len(yaml_configs) == 1
        assert yaml_configs[0].label == "Test Configuration"

        # Test directory with multiple files
        multi_configs = parser.parse(temp_pyro_files['multi_dir'])
        assert len(multi_configs) == 3
        for config in multi_configs:
            assert config.label == "Test Configuration"

    def test_data_model_validation(self, sample_pyro_config):
        """Test data models validate input correctly"""
        parser = PyroParser()

        # Test valid configuration - _parse_single_file_data returns a single PyroConfig
        config = parser._parse_single_file_data(sample_pyro_config)

        assert isinstance(config, PyroConfig)
        assert len(config.users) == 1
        assert len(config.groups) == 1
        assert len(config.devices) == 1

        user = config.users[0]
        assert user.name == "testuser"
        assert user.password == "testpass123"
        assert "testgroup" in user.groups

        device = config.devices[0]
        assert device.path == "/dev/sdb1"
        assert len(device.state) == 2

    def test_cli_argument_parsing(self):
        """Test CLI can parse all expected arguments"""
        # This test uses Click's test runner
        from click.testing import CliRunner

        runner = CliRunner()

        # Test help command
        result = runner.invoke(cli_main, ['--help'])
        assert result.exit_code == 0
        assert 'Pyroform Linux Configurator' in result.output

        # Test version command
        result = runner.invoke(cli_main, ['--version'])
        assert result.exit_code == 0
        assert 'pyroform' in result.output.lower()

    def test_invalid_file_handling(self, temp_pyro_files):
        """Test error handling for invalid files"""
        parser = PyroParser()

        # Test non-existent file
        with pytest.raises(FileNotFoundError):
            parser.parse(Path("/nonexistent/file.json"))

        # Test invalid JSON
        invalid_file = Path(temp_pyro_files['tmpdir']) / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("{ invalid json }")

        with pytest.raises((json.JSONDecodeError, ValueError)):
            parser.parse(invalid_file)

        # Test file with missing required fields
        incomplete_config = {"Label": "Incomplete"}
        incomplete_file = Path(temp_pyro_files['tmpdir']) / "incomplete.json"
        with open(incomplete_file, 'w') as f:
            json.dump(incomplete_config, f)

        # Should handle missing fields gracefully
        configs = parser.parse(incomplete_file)
        assert len(configs) == 1
        assert configs[0].users == []
        assert configs[0].groups == []
        assert configs[0].devices == []

    def test_multiple_config_merging(self, temp_pyro_files):
        """Test that multiple config files are merged correctly"""
        parser = PyroParser()

        # Create multiple configs with different content
        config1 = {
            "Label": "Config 1",
            "Users": [{"label": "u1", "Name": "user1", "Password": "pass1", "Groups": []}],
            "Groups": [],
            "Devices": []
        }

        config2 = {
            "Label": "Config 2",
            "Users": [{"label": "u2", "Name": "user2", "Password": "pass2", "Groups": []}],
            "Groups": [{"label": "g1", "Name": "group1", "Users": []}],
            "Devices": []
        }

        multi_dir = Path(temp_pyro_files['tmpdir']) / "merge_test"
        multi_dir.mkdir()

        file1 = multi_dir / "pyro_1.json"
        file2 = multi_dir / "pyro_2.json"

        with open(file1, 'w') as f:
            json.dump(config1, f)
        with open(file2, 'w') as f:
            json.dump(config2, f)

        configs = parser.parse(multi_dir)
        assert len(configs) == 2

        # Test that we can access all users from both configs
        all_users = []
        for config in configs:
            all_users.extend(config.users)

        user_names = [user.name for user in all_users]
        assert "user1" in user_names
        assert "user2" in user_names

# CODE DUMP

#   """
#   Phase 1 Integration Tests: Foundation & Core Infrastructure
#   """
#   import pytest
#   import json
#   import yaml
#   import tempfile
#   import os
#   from pathlib import Path
#   from unittest.mock import Mock, patch

#   from pyroform.src.models import PyroConfig, User, Group, Device, ActionType
#   from pyroform.src.parser import PyroParser
#   from pyroform.cli import main as cli_main


#   class TestPhase1Foundation:
#       """Test foundation components work together"""

#       @pytest.fixture
#       def sample_pyro_config(self):
#           """Sample Pyro configuration for testing"""
#           return {
#               "Label": "Test Configuration",
#               "Users": [
#                   {
#                       "label": "test_user",
#                       "Name": "testuser",
#                       "Password": "testpass123",
#                       "Groups": ["testgroup"]
#                   }
#               ],
#               "Groups": [
#                   {
#                       "label": "test_group",
#                       "Name": "testgroup",
#                       "Users": ["testuser"]
#                   }
#               ],
#               "Devices": [
#                   {
#                       "label": "test_device",
#                       "Path": "/dev/sdb1",
#                       "Partition": 1,
#                       "Mountpoint": "/mnt/test",
#                       "State": [
#                           "dir,/mnt/test/data,testuser,testgroup,755",
#                           "fl,/mnt/test/data/file.txt,testuser,testgroup,644"
#                       ]
#                   }
#               ]
#           }

#       @pytest.fixture
#       def temp_pyro_files(self, sample_pyro_config):
#           """Create temporary Pyro files for testing"""
#           with tempfile.TemporaryDirectory() as tmpdir:
#               # JSON file
#               json_file = Path(tmpdir) / "pyro_test.json"
#               with open(json_file, 'w') as f:
#                   json.dump(sample_pyro_config, f)

#               # YAML file
#               yaml_file = Path(tmpdir) / "pyro_test.yaml"
#               with open(yaml_file, 'w') as f:
#                   yaml.dump(sample_pyro_config, f)

#               # Directory with multiple files
#               multi_dir = Path(tmpdir) / "configs"
#               multi_dir.mkdir()

#               for i in range(3):
#                   multi_file = multi_dir / f"pyro_config_{i}.json"
#                   with open(multi_file, 'w') as f:
#                       json.dump(sample_pyro_config, f)

#               yield {
#                   'json_file': json_file,
#                   'yaml_file': yaml_file,
#                   'multi_dir': multi_dir,
#                   'tmpdir': tmpdir
#               }

#       def test_parser_integration(self, temp_pyro_files):
#           """Test PyroParser can read various file formats"""
#           parser = PyroParser()

#           # Test single JSON file
#           json_configs = parser.parse(temp_pyro_files['json_file'])
#           assert len(json_configs) == 1
#           assert json_configs[0].label == "Test Configuration"

#           # Test single YAML file
#           yaml_configs = parser.parse(temp_pyro_files['yaml_file'])
#           assert len(yaml_configs) == 1
#           assert yaml_configs[0].label == "Test Configuration"

#           # Test directory with multiple files
#           multi_configs = parser.parse(temp_pyro_files['multi_dir'])
#           assert len(multi_configs) == 3
#           for config in multi_configs:
#               assert config.label == "Test Configuration"

#       def test_data_model_validation(self, sample_pyro_config):
#           """Test data models validate input correctly"""
#           parser = PyroParser()

#           # Test valid configuration
#           configs = parser._parse_single_file_data(sample_pyro_config)
#           config = configs[0]

#           assert isinstance(config, PyroConfig)
#           assert len(config.users) == 1
#           assert len(config.groups) == 1
#           assert len(config.devices) == 1

#           user = config.users[0]
#           assert user.name == "testuser"
#           assert user.password == "testpass123"
#           assert "testgroup" in user.groups

#           device = config.devices[0]
#           assert device.path == "/dev/sdb1"
#           assert len(device.state) == 2

#       def test_cli_argument_parsing(self):
#           """Test CLI can parse all expected arguments"""
#           # This test uses Click's test runner
#           from click.testing import CliRunner

#           runner = CliRunner()

#           # Test help command
#           result = runner.invoke(cli_main, ['--help'])
#           assert result.exit_code == 0
#           assert 'Pyroform Linux Configurator' in result.output

#           # Test version command
#           result = runner.invoke(cli_main, ['--version'])
#           assert result.exit_code == 0
#           assert 'pyroform' in result.output.lower()

#       def test_invalid_file_handling(self, temp_pyro_files):
#           """Test error handling for invalid files"""
#           parser = PyroParser()

#           # Test non-existent file
#           with pytest.raises(FileNotFoundError):
#               parser.parse(Path("/nonexistent/file.json"))

#           # Test invalid JSON
#           invalid_file = Path(temp_pyro_files['tmpdir']) / "invalid.json"
#           with open(invalid_file, 'w') as f:
#               f.write("{ invalid json }")

#           with pytest.raises((json.JSONDecodeError, ValueError)):
#               parser.parse(invalid_file)

#           # Test file with missing required fields
#           incomplete_config = {"Label": "Incomplete"}
#           incomplete_file = Path(temp_pyro_files['tmpdir']) / "incomplete.json"
#           with open(incomplete_file, 'w') as f:
#               json.dump(incomplete_config, f)

#           # Should handle missing fields gracefully
#           configs = parser.parse(incomplete_file)
#           assert len(configs) == 1
#           assert configs[0].users == []
#           assert configs[0].groups == []
#           assert configs[0].devices == []

#       def test_multiple_config_merging(self, temp_pyro_files):
#           """Test that multiple config files are merged correctly"""
#           parser = PyroParser()

#           # Create multiple configs with different content
#           config1 = {
#               "Label": "Config 1",
#               "Users": [{"label": "u1", "Name": "user1", "Password": "pass1", "Groups": []}],
#               "Groups": [],
#               "Devices": []
#           }

#           config2 = {
#               "Label": "Config 2",
#               "Users": [{"label": "u2", "Name": "user2", "Password": "pass2", "Groups": []}],
#               "Groups": [{"label": "g1", "Name": "group1", "Users": []}],
#               "Devices": []
#           }

#           multi_dir = Path(temp_pyro_files['tmpdir']) / "merge_test"
#           multi_dir.mkdir()

#           file1 = multi_dir / "pyro_1.json"
#           file2 = multi_dir / "pyro_2.json"

#           with open(file1, 'w') as f:
#               json.dump(config1, f)
#           with open(file2, 'w') as f:
#               json.dump(config2, f)

#           configs = parser.parse(multi_dir)
#           assert len(configs) == 2

#           # Test that we can access all users from both configs
#           all_users = []
#           for config in configs:
#               all_users.extend(config.users)

#           user_names = [user.name for user in all_users]
#           assert "user1" in user_names
#           assert "user2" in user_names
