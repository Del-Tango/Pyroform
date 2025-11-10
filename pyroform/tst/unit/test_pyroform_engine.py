"""
Comprehensive Unit Tests for PyroformEngine
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

# Import the classes to test
from pyroform.src.models import PyroConfig, User, Group, Device, ActionType
from pyroform.src.parser import PyroParser
from pyroform.src.sketch_generator import SketchGenerator
from pyroform.src.validator import SystemValidator, ValidationResult
from pyroform.src.scorch_engine import ScorchResult
from pyroform.src.reporter import ReportGenerator
from pyroform.pyroform import PyroformEngine


class TestPyroformEngine(unittest.TestCase):
    """Test cases for PyroformEngine class"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.config = {
            "safety_checks": True,
            "default_output_dir": "/tmp/pyroform_test",
            "log_level": "INFO",
            "auto_confirm": False,
            "dry_run": False,
        }

        # Create test configuration data
        self.test_users = [
            User(
                label="test_user",
                name="testuser",
                password="testpass",
                groups=["testgroup"],
            )
        ]
        self.test_groups = [
            Group(label="test_group", name="testgroup", users=["testuser"])
        ]
        self.test_devices = [
            Device(
                label="test_device",
                path="/dev/sdb1",
                partition=1,
                mountpoint="/mnt/test",
                state=["dir,/mnt/test/data,root,root,755"],
            )
        ]
        self.test_config = PyroConfig(
            label="test_config",
            users=self.test_users,
            groups=self.test_groups,
            devices=self.test_devices,
        )

        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()

        # Create test JSON configuration file
        self.test_json_file = Path(self.temp_dir) / "test_config.json"
        test_config_data = {
            "Label": "test_config",
            "Users": [
                {
                    "label": "test_user",
                    "Name": "testuser",
                    "Password": "testpass",
                    "Groups": ["testgroup"],
                }
            ],
            "Groups": [
                {"label": "test_group", "Name": "testgroup", "Users": ["testuser"]}
            ],
            "Devices": [
                {
                    "label": "test_device",
                    "Path": "/dev/sdb1",
                    "Partition": 1,
                    "Mountpoint": "/mnt/test",
                    "State": ["dir,/mnt/test/data,root,root,755"],
                }
            ],
        }
        with open(self.test_json_file, "w") as f:
            json.dump(test_config_data, f)

    def tearDown(self):
        """Clean up after each test method"""
        # Remove temporary directory and files
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test PyroformEngine initialization"""
        engine = PyroformEngine(self.config)

        self.assertIsInstance(engine.parser, PyroParser)
        self.assertIsInstance(engine.sketch_generator, SketchGenerator)
        self.assertIsInstance(engine.validator, SystemValidator)
        self.assertIsInstance(engine.reporter, ReportGenerator)
        self.assertEqual(engine.config, self.config)

    def test_initialization_default_config(self):
        """Test PyroformEngine initialization with default config"""
        engine = PyroformEngine()

        self.assertIsNotNone(engine.config)
        self.assertIn("safety_checks", engine.config)
        self.assertIn("default_output_dir", engine.config)
        self.assertIn("log_level", engine.config)

    @patch("pyroform.pyroform.PyroParser")
    def test_configure_action_no_configs(self, mock_parser):
        """Test configure action when no configurations are found"""
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse.return_value = []

        engine = PyroformEngine(self.config)
        engine.parser = mock_parser_instance

        result = engine.configure(str(self.test_json_file))

        self.assertFalse(result)

    @patch("pyroform.pyroform.PyroParser")
    def test_configure_action_parser_exception(self, mock_parser):
        """Test configure action when parser raises exception"""
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse.side_effect = Exception("Parser error")

        engine = PyroformEngine(self.config)
        engine.parser = mock_parser_instance

        result = engine.configure(str(self.test_json_file))

        self.assertFalse(result)

    @patch("pyroform.pyroform.PyroParser")
    @patch("pyroform.pyroform.ScorchEngine")
    def test_scorch_action_success(self, mock_scorch_engine, mock_parser):
        """Test scorch action with successful execution"""
        # Setup mocks
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse.return_value = [self.test_config]

        mock_scorch_instance = mock_scorch_engine.return_value
        expected_result = ScorchResult(
            resources_removed=["user:testuser"],
            resources_failed=[],
            dry_run=False,
            success=True,
        )
        mock_scorch_instance.execute_scorch.return_value = expected_result

        # Create engine and execute
        engine = PyroformEngine(self.config)
        engine.parser = mock_parser_instance

        result = engine.scorch(str(self.test_json_file))

        # Assertions
        self.assertEqual(result, expected_result)
        mock_parser_instance.parse.assert_called_once()
        mock_scorch_instance.execute_scorch.assert_called_once_with(
            self.test_config, dry_run=False
        )

    @patch("pyroform.pyroform.PyroParser")
    def test_scorch_action_no_configs(self, mock_parser):
        """Test scorch action when no configurations are found"""
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse.return_value = []

        engine = PyroformEngine(self.config)
        engine.parser = mock_parser_instance

        result = engine.scorch(str(self.test_json_file))

        self.assertFalse(result.success)
        self.assertEqual(len(result.resources_removed), 0)

    @patch("pyroform.pyroform.PyroParser")
    def test_scorch_action_with_dry_run(self, mock_parser):
        """Test scorch action with dry_run parameter"""
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse.return_value = [self.test_config]

        engine = PyroformEngine(self.config)
        engine.parser = mock_parser_instance

        with patch("pyroform.pyroform.ScorchEngine") as mock_scorch_engine:
            mock_scorch_instance = mock_scorch_engine.return_value
            mock_scorch_instance.execute_scorch.return_value = ScorchResult(
                resources_removed=[], resources_failed=[], dry_run=True, success=True
            )

            result = engine.scorch(str(self.test_json_file), dry_run=True)

            mock_scorch_instance.execute_scorch.assert_called_once_with(
                self.test_config, dry_run=True
            )

    @patch("pyroform.pyroform.PyroParser")
    @patch("pyroform.pyroform.SystemValidator")
    def test_validate_action_success(self, mock_validator, mock_parser):
        """Test validate action with successful validation"""
        # Setup mocks
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse.return_value = [self.test_config]

        mock_validator_instance = mock_validator.return_value
        expected_result = ValidationResult(
            is_valid=True,
            discrepancies=[],
            summary={"total_issues": 0, "critical_issues": 0},
        )
        mock_validator_instance.validate_configuration.return_value = expected_result

        # Create engine and execute
        engine = PyroformEngine(self.config)
        engine.parser = mock_parser_instance
        engine.validator = mock_validator_instance

        result = engine.validate(str(self.test_json_file))

        # Assertions
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.discrepancies), 0)
        mock_parser_instance.parse.assert_called_once()
        mock_validator_instance.validate_configuration.assert_called_once_with(
            self.test_config
        )

    @patch("pyroform.pyroform.PyroParser")
    @patch("pyroform.pyroform.SystemValidator")
    def test_validate_action_with_discrepancies(self, mock_validator, mock_parser):
        """Test validate action with validation discrepancies"""
        # Setup mocks
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse.return_value = [self.test_config]

        mock_validator_instance = mock_validator.return_value
        discrepancies = [
            {
                "type": "user",
                "name": "missinguser",
                "issue": "User does not exist",
                "critical": True,
            },
            {
                "type": "mount",
                "device": "/dev/sdb1",
                "issue": "Device not mounted",
                "critical": False,
            },
        ]
        expected_result = ValidationResult(
            is_valid=False,
            discrepancies=discrepancies,
            summary={"total_issues": 2, "critical_issues": 1},
        )
        mock_validator_instance.validate_configuration.return_value = expected_result

        # Create engine and execute
        engine = PyroformEngine(self.config)
        engine.parser = mock_parser_instance
        engine.validator = mock_validator_instance

        result = engine.validate(str(self.test_json_file))

        # Assertions
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.discrepancies), 2)
        self.assertEqual(result.summary["total_issues"], 2)
        self.assertEqual(result.summary["critical_issues"], 1)

    @patch("pyroform.pyroform.PyroParser")
    def test_validate_action_no_configs(self, mock_parser):
        """Test validate action when no configurations are found"""
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse.return_value = []

        engine = PyroformEngine(self.config)
        engine.parser = mock_parser_instance

        result = engine.validate(str(self.test_json_file))

        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.discrepancies), 1)
        self.assertIn("error", result.discrepancies[0])

    def test_default_config(self):
        """Test default configuration generation"""
        engine = PyroformEngine()
        config = engine._default_config()

        expected_keys = [
            "safety_checks",
            "default_output_dir",
            "log_level",
            "auto_confirm",
            "dry_run",
        ]
        for key in expected_keys:
            self.assertIn(key, config)

        self.assertTrue(config["safety_checks"])
        self.assertEqual(config["log_level"], "INFO")
        self.assertFalse(config["auto_confirm"])

    def test_mock_flow_engine_creation(self):
        """Test mock flow engine creation for testing"""
        engine = PyroformEngine()

        # The flow engine should be a mock
        self.assertTrue(hasattr(engine.flow_engine, "execute_sketch"))
        self.assertTrue(hasattr(engine.flow_engine, "pause_execution"))
        self.assertTrue(hasattr(engine.flow_engine, "resume_execution"))
        self.assertTrue(hasattr(engine.flow_engine, "stop_execution"))
        self.assertTrue(hasattr(engine.flow_engine, "send_command"))
        self.assertTrue(hasattr(engine.flow_engine, "purge_data"))

    @patch("pyroform.pyroform.PyroParser")
    def test_scorch_action_with_auto_confirm(self, mock_parser):
        """Test scorch action with auto_confirm parameter"""
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse.return_value = [self.test_config]

        engine = PyroformEngine(self.config)
        engine.parser = mock_parser_instance

        with patch("pyroform.pyroform.ScorchEngine") as mock_scorch_engine:
            mock_scorch_instance = mock_scorch_engine.return_value
            mock_scorch_instance.execute_scorch.return_value = ScorchResult(
                resources_removed=["user:testuser"],
                resources_failed=[],
                dry_run=False,
                success=True,
            )

            result = engine.scorch(str(self.test_json_file), auto_confirm=True)

            # Verify ScorchEngine was created with safety_check=False when auto_confirm=True
            mock_scorch_engine.assert_called_once_with(safety_check=False)
            mock_scorch_instance.execute_scorch.assert_called_once()

    @patch("pyroform.pyroform.PyroParser")
    def test_scorch_action_exception_handling(self, mock_parser):
        """Test scorch action exception handling"""
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse.side_effect = Exception("Test exception")

        engine = PyroformEngine(self.config)
        engine.parser = mock_parser_instance

        result = engine.scorch(str(self.test_json_file))

        self.assertFalse(result.success)
        self.assertEqual(len(result.resources_failed), 1)
        self.assertIn("error", result.resources_failed[0])

    @patch("pyroform.pyroform.PyroParser")
    @patch("pyroform.pyroform.SystemValidator")
    def test_validate_action_exception_handling(self, mock_validator, mock_parser):
        """Test validate action exception handling"""
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse.side_effect = Exception("Test exception")

        engine = PyroformEngine(self.config)
        engine.parser = mock_parser_instance

        result = engine.validate(str(self.test_json_file))

        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.discrepancies), 1)
        self.assertIn("error", result.discrepancies[0])


class TestPyroformEngineIntegration(unittest.TestCase):
    """Integration tests for PyroformEngine with real components"""

    def setUp(self):
        """Set up integration test fixtures"""
        self.config = {
            "safety_checks": False,  # Disable safety checks for testing
            "default_output_dir": "/tmp/pyroform_test",
            "log_level": "INFO",
            "auto_confirm": True,  # Auto-confirm for testing
            "dry_run": True,  # Use dry-run to avoid actual system changes
        }

        # Create test data directory
        self.test_dir = tempfile.mkdtemp()
        self.test_config_file = Path(self.test_dir) / "test_config.json"

        # Create a simple test configuration
        test_config = {
            "Label": "integration_test",
            "Users": [
                {
                    "label": "test_user",
                    "Name": "testuser",
                    "Password": "testpass123",
                    "Groups": ["testgroup"],
                }
            ],
            "Groups": [
                {"label": "test_group", "Name": "testgroup", "Users": ["testuser"]}
            ],
            "Devices": [
                {
                    "label": "test_device",
                    "Path": "/dev/sdb1",
                    "Partition": 1,
                    "Mountpoint": "/mnt/test",
                    "State": ["dir,/mnt/test/data,root,root,755"],
                }
            ],
        }

        with open(self.test_config_file, "w") as f:
            json.dump(test_config, f)

    def tearDown(self):
        """Clean up integration test fixtures"""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_parser_integration(self):
        """Test integration with PyroParser"""
        engine = PyroformEngine(self.config)

        # Test that parser can read the test configuration
        configs = engine.parser.parse(self.test_config_file)

        self.assertEqual(len(configs), 1)
        self.assertEqual(configs[0].label, "integration_test")
        self.assertEqual(len(configs[0].users), 1)
        self.assertEqual(len(configs[0].groups), 1)
        self.assertEqual(len(configs[0].devices), 1)

    def test_sketch_generator_integration(self):
        """Test integration with SketchGenerator"""
        engine = PyroformEngine(self.config)

        # Parse configuration
        configs = engine.parser.parse(self.test_config_file)
        config = configs[0]

        # Test sketch generation for different actions
        configure_sketch = engine.sketch_generator.generate_configure_sketch(config)
        mount_sketch = engine.sketch_generator.generate_mount_sketch(config)
        scorch_sketch = engine.sketch_generator.generate_scorch_sketch(config)

        # Verify sketch structures
        self.assertIn("name", configure_sketch)
        self.assertIn("name", mount_sketch)
        self.assertIn("name", scorch_sketch)

        # Configure sketch should have Users, Groups, Files sections
        self.assertIn("Users", configure_sketch)
        self.assertIn("Groups", configure_sketch)

        # Mount sketch should have Devices section
        self.assertIn("Devices", mount_sketch)

        # Scorch sketch should have Cleanup section
        self.assertIn("Cleanup", scorch_sketch)

    def test_validate_action_integration(self):
        """Test integration of validate action with real components"""
        engine = PyroformEngine(self.config)

        # This will use the real validator (though it will check actual system state)
        result = engine.validate(str(self.test_config_file))

        # We can't predict the actual validation result, but we can check the structure
        self.assertIn(result.is_valid, [True, False])
        self.assertIsInstance(result.discrepancies, list)
        self.assertIsInstance(result.summary, dict)
        self.assertIn("total_issues", result.summary)
        self.assertIn("critical_issues", result.summary)

    @patch("pyroform.pyroform.ScorchEngine")
    def test_scorch_action_integration_dry_run(self, mock_scorch_engine):
        """Test integration of scorch action in dry-run mode"""
        # Mock the scorch engine to avoid actual system changes
        mock_scorch_instance = mock_scorch_engine.return_value
        mock_scorch_instance.execute_scorch.return_value = ScorchResult(
            resources_removed=["user:testuser", "group:testgroup"],
            resources_failed=[],
            dry_run=True,
            success=True,
        )

        engine = PyroformEngine(self.config)

        result = engine.scorch(str(self.test_config_file), dry_run=True)

        # Verify the scorch engine was called with dry_run=True
        mock_scorch_instance.execute_scorch.assert_called_once()
        call_args = mock_scorch_instance.execute_scorch.call_args[1]
        self.assertTrue(call_args["dry_run"])

        # Verify the result structure
        self.assertTrue(result.success)
        self.assertTrue(result.dry_run)
        self.assertEqual(len(result.resources_removed), 2)


class TestPyroformEngineEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for PyroformEngine"""

    def setUp(self):
        """Set up edge case test fixtures"""
        self.config = {
            "safety_checks": True,
            "default_output_dir": "/tmp/pyroform_test",
            "log_level": "INFO",
            "auto_confirm": False,
            "dry_run": False,
        }

    def test_nonexistent_input_path(self):
        """Test behavior with nonexistent input path"""
        engine = PyroformEngine(self.config)

        # Test with nonexistent file
        nonexistent_path = "/nonexistent/path/config.json"

        # All actions should handle nonexistent paths gracefully
        configure_result = engine.configure(nonexistent_path)
        self.assertFalse(configure_result)

        scorch_result = engine.scorch(nonexistent_path)
        self.assertFalse(scorch_result.success)

        mount_result = engine.mount(nonexistent_path)
        self.assertFalse(mount_result)

        validate_result = engine.validate(nonexistent_path)
        self.assertFalse(validate_result.is_valid)

    def test_invalid_configuration_data(self):
        """Test behavior with invalid configuration data"""
        engine = PyroformEngine(self.config)

        # Create a temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"invalid": "json", "missing": "closing brace"')
            invalid_json_file = f.name

        try:
            # Parser should raise an exception with invalid JSON
            with self.assertRaises(Exception):
                engine.parser.parse(Path(invalid_json_file))

        finally:
            # Clean up
            if os.path.exists(invalid_json_file):
                os.unlink(invalid_json_file)

    def test_mock_flow_engine_methods(self):
        """Test that mock flow engine methods work correctly"""
        engine = PyroformEngine(self.config)

        # Test all flow engine methods
        self.assertTrue(engine.flow_engine.execute_sketch({}, ActionType.CONFIGURE))
        self.assertTrue(engine.flow_engine.pause_execution())
        self.assertTrue(engine.flow_engine.resume_execution())
        self.assertTrue(engine.flow_engine.stop_execution())
        self.assertTrue(engine.flow_engine.send_command("test_command"))
        self.assertTrue(engine.flow_engine.purge_data())
        self.assertIsNone(engine.flow_engine.current_sketch)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)

# CODE DUMP

# TODO
#   @patch('pyroform.pyroform.PyroParser')
#   @patch('pyroform.pyroform.SketchGenerator')
#   @patch('pyroform.pyroform.PyroflowEngine')
#   def test_mount_action_success(self, mock_flow_engine, mock_sketch_gen, mock_parser):
#       """Test mount action with successful execution"""
#       # Setup mocks
#       mock_parser_instance = mock_parser.return_value
#       mock_parser_instance.parse.return_value = [self.test_config]

#       mock_sketch_instance = mock_sketch_gen.return_value
#       mock_sketch_instance.generate_mount_sketch.return_value = {"name": "mount_sketch"}

#       mock_flow_instance = mock_flow_engine.return_value
#       mock_flow_instance.execute_sketch.return_value = True

#       # Create engine and execute
#       engine = PyroformEngine(self.config)
#       engine.parser = mock_parser_instance
#       engine.sketch_generator = mock_sketch_instance
#       engine.flow_engine = mock_flow_instance

#       result = engine.mount(str(self.test_json_file))

#       # Assertions
#       self.assertTrue(result)
#       mock_parser_instance.parse.assert_called_once()
#       mock_sketch_instance.generate_mount_sketch.assert_called_once_with(self.test_config)
#       mock_flow_instance.execute_sketch.assert_called_once()

# TODO
#   @patch('pyroform.pyroform.PyroParser')
#   def test_validate_action_multiple_configs(self, mock_parser):
#       """Test validate action with multiple configurations"""
#       # Create multiple test configs
#       config1 = PyroConfig(label="config1", users=[], groups=[], devices=[])
#       config2 = PyroConfig(label="config2", users=[], groups=[], devices=[])

#       mock_parser_instance = mock_parser.return_value
#       mock_parser_instance.parse.return_value = [config1, config2]

#       engine = PyroformEngine(self.config)
#       engine.parser = mock_parser_instance

#       with patch('pyroform.pyroform.SystemValidator') as mock_validator:
#           mock_validator_instance = mock_validator.return_value

#           # First config has issues, second is valid
#           result1 = ValidationResult(
#               is_valid=False,
#               discrepancies=[{"type": "user", "issue": "User missing", "critical": True}],
#               summary={"total_issues": 1, "critical_issues": 1}
#           )
#           result2 = ValidationResult(
#               is_valid=True,
#               discrepancies=[],
#               summary={"total_issues": 0, "critical_issues": 0}
#           )
#           mock_validator_instance.validate_configuration.side_effect = [result1, result2]

#           result = engine.validate(str(self.test_json_file))

#           # Combined result should be invalid (one config has issues)
#           self.assertFalse(result.is_valid)
#           self.assertEqual(len(result.discrepancies), 1)
#           self.assertEqual(result.summary["total_issues"], 1)

# TODO
#   def test_empty_configuration(self):
#       """Test behavior with empty configuration"""
#       engine = PyroformEngine(self.config)

#       # Create an empty configuration
#       empty_config = PyroConfig(label="empty", users=[], groups=[], devices=[])

#       with patch('pyroform.pyroform.PyroParser') as mock_parser:
#           mock_parser_instance = mock_parser.return_value
#           mock_parser_instance.parse.return_value = [empty_config]

#           engine.parser = mock_parser_instance

#           # All actions should handle empty configurations
#           configure_result = engine.configure("dummy_path")
#           # configure should return False since no actual work is done
#           self.assertFalse(configure_result)

#           # scorch with empty config should find no resources to remove
#           scorch_result = engine.scorch("dummy_path")
#           # In dry_run mode, this would be successful with no resources removed
#           # In actual mode, it depends on system state

#           # mount with empty config should return True (no mounts to process)
#           with patch('pyroform.pyroform.SketchGenerator') as mock_sketch:
#               with patch('pyroform.pyroform.PyroflowEngine') as mock_flow:
#                   mock_sketch_instance = mock_sketch.return_value
#                   mock_sketch_instance.generate_mount_sketch.return_value = {}
#                   mock_flow_instance = mock_flow.return_value
#                   mock_flow_instance.execute_sketch.return_value = True

#                   engine.sketch_generator = mock_sketch_instance
#                   engine.flow_engine = mock_flow_instance

#                   mount_result = engine.mount("dummy_path")
#                   self.assertTrue(mount_result)

#           # validate with empty config should be valid (no requirements to check)
#           with patch('pyroform.pyroform.SystemValidator') as mock_validator:
#               mock_validator_instance = mock_validator.return_value
#               mock_validator_instance.validate_configuration.return_value = ValidationResult(
#                   is_valid=True, discrepancies=[], summary={"total_issues": 0, "critical_issues": 0}
#               )

#               engine.validator = mock_validator_instance
#               validate_result = engine.validate("dummy_path")
#               self.assertTrue(validate_result.is_valid)

# TODO
#   @patch('pyroform.pyroform.PyroParser')
#   @patch('pyroform.pyroform.SketchGenerator')
#   @patch('pyroform.pyroform.PyroflowEngine')
#   def test_configure_action_success(self, mock_flow_engine, mock_sketch_gen, mock_parser):
#       """Test configure action with successful execution"""
#       # Setup mocks
#       mock_parser_instance = mock_parser.return_value
#       mock_parser_instance.parse.return_value = [self.test_config]

#       mock_sketch_instance = mock_sketch_gen.return_value
#       mock_sketch_instance.generate_configure_sketch.return_value = {"name": "test_sketch"}

#       mock_flow_instance = mock_flow_engine.return_value
#       mock_flow_instance.execute_sketch.return_value = True

#       # Create engine and execute
#       engine = PyroformEngine(self.config)
#       engine.parser = mock_parser_instance
#       engine.sketch_generator = mock_sketch_instance
#       engine.flow_engine = mock_flow_instance

#       result = engine.configure(str(self.test_json_file))

#       # Assertions
#       self.assertTrue(result)
#       mock_parser_instance.parse.assert_called_once()
#       mock_sketch_instance.generate_configure_sketch.assert_called_once_with(self.test_config)
#       mock_flow_instance.execute_sketch.assert_called_once()
