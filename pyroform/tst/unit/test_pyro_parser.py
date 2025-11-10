import unittest
import json
import yaml
import tempfile
from pathlib import Path

# Import the modules to test
from pyroform.src.parser import PyroParser


class TestPyroParser(unittest.TestCase):
    """Test configuration parser"""

    def setUp(self):
        self.parser = PyroParser()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_parse_single_json_file(self):
        """Test parsing single JSON configuration file"""
        config_data = {
            "Label": "Test Configuration",
            "Users": [
                {
                    "label": "user1",
                    "Name": "testuser",
                    "Password": "testpass",
                    "Groups": ["admin"],
                }
            ],
            "Groups": [{"label": "group1", "Name": "testgroup", "Users": ["testuser"]}],
            "Devices": [
                {
                    "label": "device1",
                    "Path": "/dev/sda1",
                    "Partition": 1,
                    "Mountpoint": "/mnt/test",
                    "State": ["dir,/mnt/test/data,root,root,755"],
                }
            ],
        }

        config_file = Path(self.temp_dir) / "test.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        configs = self.parser.parse(config_file)

        self.assertEqual(len(configs), 1)
        config = configs[0]
        self.assertEqual(config.label, "Test Configuration")
        self.assertEqual(len(config.users), 1)
        self.assertEqual(len(config.groups), 1)
        self.assertEqual(len(config.devices), 1)

    def test_parse_single_yaml_file(self):
        """Test parsing single YAML configuration file"""
        config_data = {
            "Label": "Test Configuration",
            "Users": [
                {
                    "label": "user1",
                    "Name": "testuser",
                    "Password": "testpass",
                    "Groups": ["admin"],
                }
            ],
        }

        config_file = Path(self.temp_dir) / "test.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        configs = self.parser.parse(config_file)

        self.assertEqual(len(configs), 1)
        config = configs[0]
        self.assertEqual(config.label, "Test Configuration")
        self.assertEqual(len(config.users), 1)

    def test_parse_directory(self):
        """Test parsing multiple configuration files in directory"""
        # Create multiple config files
        config_data1 = {
            "Label": "Config 1",
            "Users": [{"label": "u1", "Name": "user1", "Password": "p1", "Groups": []}],
        }
        config_data2 = {
            "Label": "Config 2",
            "Users": [{"label": "u2", "Name": "user2", "Password": "p2", "Groups": []}],
        }

        config_file1 = Path(self.temp_dir) / "pyro_config1.json"
        config_file2 = Path(self.temp_dir) / "pyro_config2.json"

        with open(config_file1, "w") as f:
            json.dump(config_data1, f)
        with open(config_file2, "w") as f:
            json.dump(config_data2, f)

        configs = self.parser.parse(Path(self.temp_dir))

        self.assertEqual(len(configs), 2)
        self.assertEqual(configs[0].label, "Config 1")
        self.assertEqual(configs[1].label, "Config 2")

    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file raises FileNotFoundError"""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse(Path("/nonexistent/file.json"))

    def test_parse_invalid_format(self):
        """Test parsing file with invalid format raises ValueError"""
        invalid_file = Path(self.temp_dir) / "test.txt"
        invalid_file.write_text("invalid content")

        with self.assertRaises(ValueError):
            self.parser.parse(invalid_file)
