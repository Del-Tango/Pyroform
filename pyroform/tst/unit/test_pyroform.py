"""
Unit Test Suite for Pyroform Class

This module contains unit tests for the Pyroform main library interface class.
"""

import pytest
import json
import yaml
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime

from pyroform.src.models import ActionType
from pyroform.pyroform import Pyroform


class TestPyroformInitialization:
    """Test Pyroform class initialization and basic properties"""

#   # TODO
#   def test_initialization_with_config_file(self):
#       """Test Pyroform initialization with config file"""
#       pass
#   # TODO
#   def test_initialization_with_nonexistent_config_file(self):
#       """Test Pyroform initialization with nonexistent config file"""
#       pass
#   # TODO
#   def test_initialization_with_invalid_config_format(self):
#       """Test Pyroform initialization with invalid config file format"""
#       pass
#   # TODO
#   def test_initialization_with_malformed_yaml(self):
#       """Test Pyroform initialization with malformed YAML config"""
#       pass

    def test_initialization_without_config_file(self):
        """Test Pyroform initialization without config file"""
        # When no config file provided, should use defaults
        pf = Pyroform()

        assert pf.auto_confirm is False
        assert pf.config is not None
        assert "safety_checks" in pf.config
        assert "default_output_dir" in pf.config
        assert "log_level" in pf.config
        assert pf.engine is not None
        assert pf._last_action is None
        assert pf._last_result is None

    def test_initialization_with_auto_confirm(self):
        """Test Pyroform initialization with auto_confirm"""
        pf = Pyroform(auto_confirm=True)
        assert pf.auto_confirm is True
        assert pf.config["auto_confirm"] is True

    def test_initialization_with_dry_run(self):
        """Test Pyroform initialization with dry_run"""
        pf = Pyroform(dry_run=True)
        assert pf.config["dry_run"] is True

    def test_initialization_with_debug(self):
        """Test Pyroform initialization with debug mode"""
        pf = Pyroform(debug=True)
        assert pf.config["debug"] is True

    def test_initialization_with_json_config_file(self):
        """Test Pyroform initialization with JSON config file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                "safety_checks": False,
                "log_level": "WARNING"
            }
            json.dump(config_data, f)
            config_path = f.name

        try:
            pf = Pyroform(config_file=config_path)

            # Should use JSON config values and merge with defaults
            assert pf.config["safety_checks"] is False
            assert pf.config["log_level"] == "WARNING"
            # Defaults should still be present
            assert "default_output_dir" in pf.config
        finally:
            Path(config_path).unlink()


class TestPyroformConfigurationManagement:
    """Test configuration management methods"""

#   # TODO
#   def test_version_property(self):
#       """Test version property returns version string"""
#       pass

    @pytest.fixture
    def pyroform_instance(self):
        """Create a Pyroform instance for testing"""
        return Pyroform(auto_confirm=True, dry_run=False, debug=False)

    def test_get_config(self, pyroform_instance):
        """Test get_config returns a copy of configuration"""
        config = pyroform_instance.get_config()

        assert isinstance(config, dict)
        assert config["auto_confirm"] is True
        assert config["dry_run"] is False
        assert config["debug"] is False

        # Should be a copy, not the same object
        config["test_key"] = "test_value"
        assert "test_key" not in pyroform_instance.config

    def test_set_config(self, pyroform_instance):
        """Test set_config updates configuration"""
        original_config = pyroform_instance.get_config().copy()

        # Update configuration
        pyroform_instance.set_config(
            log_level="DEBUG",
            dry_run=True,
            new_key="new_value"
        )

        # Verify updates
        assert pyroform_instance.config["log_level"] == "DEBUG"
        assert pyroform_instance.config["dry_run"] is True
        assert pyroform_instance.config["new_key"] == "new_value"

        # Verify auto_confirm property is updated
        pyroform_instance.set_config(auto_confirm=False)
        assert pyroform_instance.auto_confirm is False

        # Verify other values unchanged
        assert pyroform_instance.config["safety_checks"] == original_config["safety_checks"]
        assert pyroform_instance.config["default_output_dir"] == original_config["default_output_dir"]


class TestPyroformActionMethods:
    """Test main action methods (configure, scorch, mount, validate, snapshot)"""

    @pytest.fixture
    def pyroform_with_mocked_engine(self):
        """Create Pyroform instance with mocked engine"""
        with patch('pyroform.pyroform.PyroformEngine') as MockEngine:
            mock_engine = Mock()
            mock_engine.configure = Mock(return_value=True)
            mock_engine.scorch = Mock(return_value={'success': True, 'resources_removed': []})
            mock_engine.mount = Mock(return_value=True)
            mock_engine.validate = Mock(return_value={'is_valid': True, 'discrepancies': []})
            mock_engine.snapshot = Mock(return_value={'success': True, 'output_path': '/tmp/snapshot.yaml'})
            mock_engine.reporter = Mock()
            mock_engine.reporter.generate_action_report = Mock(return_value={'action': 'test', 'success': True})
            mock_engine.reporter.save_report = Mock(return_value=True)

            MockEngine.return_value = mock_engine
            pf = Pyroform(auto_confirm=True)

            return pf, mock_engine

    def test_configure_success(self, pyroform_with_mocked_engine):
        """Test configure method success"""
        pf, mock_engine = pyroform_with_mocked_engine

        result = pf.configure("/path/to/config.yaml", dry_run=True, verbose=True)

        assert result is True
        mock_engine.configure.assert_called_once_with(
            "/path/to/config.yaml",
            auto_confirm=True,  # From instance initialization
            dry_run=True,
            verbose=True
        )
        assert pf._last_action == ActionType.CONFIGURE
        assert pf._last_result is True

    def test_configure_with_kwargs_merging(self, pyroform_with_mocked_engine):
        """Test configure method merges kwargs correctly"""
        pf, mock_engine = pyroform_with_mocked_engine

        # Create instance without auto_confirm
        pf.auto_confirm = False

        # Call with auto_confirm in kwargs
        pf.configure("/path/to/config.yaml", auto_confirm=True, dry_run=True)

        mock_engine.configure.assert_called_once_with(
            "/path/to/config.yaml",
            auto_confirm=True,  # From kwargs (overrides instance)
            dry_run=True
        )

    def test_configure_failure(self, pyroform_with_mocked_engine):
        """Test configure method failure"""
        pf, mock_engine = pyroform_with_mocked_engine
        mock_engine.configure.return_value = False

        result = pf.configure("/path/to/config.yaml")

        assert result is False
        assert pf._last_action == ActionType.CONFIGURE
        assert pf._last_result is False

    def test_scorch_success(self, pyroform_with_mocked_engine):
        """Test scorch method success"""
        pf, mock_engine = pyroform_with_mocked_engine
        mock_result = {'success': True, 'resources_removed': ['user1', 'group1']}
        mock_engine.scorch.return_value = mock_result

        result = pf.scorch("/path/to/config.yaml", dry_run=True)

        assert result == mock_result
        mock_engine.scorch.assert_called_once_with(
            "/path/to/config.yaml",
            auto_confirm=True,
            dry_run=True
        )
        assert pf._last_action == ActionType.SCORCH
        assert pf._last_result == mock_result

    def test_scorch_kwargs_merging(self):
        """Test scorch method properly merges auto_confirm"""
        with patch('pyroform.pyroform.PyroformEngine') as MockEngine:
            mock_engine = Mock()
            mock_engine.scorch = Mock(return_value={'success': True})
            MockEngine.return_value = mock_engine

            # Instance with auto_confirm=False
            pf = Pyroform(auto_confirm=False)

            # Call scorch with auto_confirm in kwargs
            pf.scorch("/path/to/config.yaml", auto_confirm=True, dry_run=False)

            # Should use kwargs auto_confirm
            mock_engine.scorch.assert_called_once_with(
                "/path/to/config.yaml",
                auto_confirm=True,  # From kwargs
                dry_run=False
            )

    def test_mount_success(self, pyroform_with_mocked_engine):
        """Test mount method success"""
        pf, mock_engine = pyroform_with_mocked_engine

        result = pf.mount("/path/to/config.yaml", verbose=True)

        assert result is True
        mock_engine.mount.assert_called_once_with(
            "/path/to/config.yaml",
            auto_confirm=True,
            verbose=True
        )
        assert pf._last_action == ActionType.MOUNT
        assert pf._last_result is True

    def test_mount_failure(self, pyroform_with_mocked_engine):
        """Test mount method failure"""
        pf, mock_engine = pyroform_with_mocked_engine
        mock_engine.mount.return_value = False

        result = pf.mount("/path/to/config.yaml")

        assert result is False
        assert pf._last_action == ActionType.MOUNT
        assert pf._last_result is False

    def test_validate_success(self, pyroform_with_mocked_engine):
        """Test validate method success"""
        pf, mock_engine = pyroform_with_mocked_engine
        mock_result = {'is_valid': True, 'discrepancies': [], 'summary': {'total_issues': 0}}
        mock_engine.validate.return_value = mock_result

        result = pf.validate("/path/to/config.yaml", verbose=True)

        assert result == mock_result
        mock_engine.validate.assert_called_once_with(
            "/path/to/config.yaml",
            verbose=True
        )
        assert pf._last_action == ActionType.VALIDATE
        assert pf._last_result == mock_result

    def test_validate_failure(self, pyroform_with_mocked_engine):
        """Test validate method with validation failure"""
        pf, mock_engine = pyroform_with_mocked_engine
        mock_result = {
            'is_valid': False,
            'discrepancies': [{'type': 'user', 'issue': 'User missing'}],
            'summary': {'total_issues': 1}
        }
        mock_engine.validate.return_value = mock_result

        result = pf.validate("/path/to/config.yaml")

        assert result == mock_result
        assert pf._last_action == ActionType.VALIDATE
        assert pf._last_result == mock_result

    def test_snapshot_success(self, pyroform_with_mocked_engine):
        """Test snapshot method success"""
        pf, mock_engine = pyroform_with_mocked_engine

        result = pf.snapshot(output_path="/tmp/snapshot.yaml", max_depth=5)

        assert result == {'success': True, 'output_path': '/tmp/snapshot.yaml'}
        mock_engine.snapshot.assert_called_once_with(
            "/tmp/snapshot.yaml",
            max_depth=5
        )
        assert pf._last_action == ActionType.SNAPSHOT
        assert pf._last_result == {'success': True, 'output_path': '/tmp/snapshot.yaml'}

    def test_snapshot_with_input_path(self, pyroform_with_mocked_engine):
        """Test snapshot method with input path (even though it's not used in the method)"""
        pf, mock_engine = pyroform_with_mocked_engine
        result = pf.snapshot(
            input_path="/path/to/config.yaml",
            output_path="/tmp/snapshot.yaml"
        )
        mock_engine.snapshot.assert_called_once_with("/tmp/snapshot.yaml")

    def test_snapshot_failure(self, pyroform_with_mocked_engine):
        """Test snapshot method failure"""
        pf, mock_engine = pyroform_with_mocked_engine
        mock_engine.snapshot.return_value = {'success': False, 'error': 'Failed to create snapshot'}

        result = pf.snapshot(output_path="/tmp/snapshot.yaml")

        assert result == {'success': False, 'error': 'Failed to create snapshot'}
        assert pf._last_action == ActionType.SNAPSHOT
        assert pf._last_result == {'success': False, 'error': 'Failed to create snapshot'}


class TestPyroformGenerateReport:
    """Test generate_report method"""

#   # TODO
#   def test_generate_report_with_output_path(self, pyroform_with_mocked_engine_and_last_action):
#       """Test generate_report with output path"""
#       pass

    @pytest.fixture
    def pyroform_with_mocked_engine_and_last_action(self):
        """Create Pyroform with mocked engine and last action set"""
        with patch('pyroform.pyroform.PyroformEngine') as MockEngine, \
             patch('pyroform.pyroform.datetime') as mock_datetime, \
             patch('builtins.print'):

            # Mock datetime
            mock_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.fromisoformat = datetime.fromisoformat

            # Mock engine
            mock_engine = Mock()
            mock_reporter = Mock()
            mock_engine.reporter = mock_reporter
            MockEngine.return_value = mock_engine

            pf = Pyroform(auto_confirm=True)
            pf._last_action = ActionType.CONFIGURE
            pf._last_result = {'success': True, 'processed_configs': ['test_config']}

            return pf, mock_reporter, mock_now

    def test_generate_report_without_output_path(self, pyroform_with_mocked_engine_and_last_action):
        """Test generate_report without output path (prints to stdout)"""
        pf, mock_reporter, mock_now = pyroform_with_mocked_engine_and_last_action

        mock_report = {'action': 'configure', 'success': True}
        mock_reporter.generate_action_report.return_value = mock_report

        with patch('builtins.print') as mock_print:
            result = pf.generate_report()

            assert result is True
            mock_print.assert_called_once()
            # Should print JSON
            call_args = mock_print.call_args[0][0]
            assert 'configure' in call_args
            mock_reporter.save_report.assert_not_called()

    def test_generate_report_no_last_action(self):
        """Test generate_report when no action has been executed"""
        pf = Pyroform()

        with patch('builtins.print') as mock_print:
            result = pf.generate_report("/tmp/report.json")

            assert result is False
            mock_print.assert_called_once_with("No action has been executed yet")

    def test_generate_report_exception_handling(self, pyroform_with_mocked_engine_and_last_action):
        """Test generate_report exception handling"""
        pf, mock_reporter, _ = pyroform_with_mocked_engine_and_last_action

        mock_reporter.generate_action_report.side_effect = Exception("Test error")

        with patch('builtins.print') as mock_print:
            result = pf.generate_report("/tmp/report.json")

            assert result is False
            mock_print.assert_called_once_with("Failed to generate report: Test error")


class TestPyroformWorkflowExecution:
    """Test execute_workflow method"""

#   # TODO
#   def test_execute_workflow_success(self, pyroform_for_workflow):
#       """Test successful workflow execution"""
#       pass
#   # TODO
#   def test_execute_workflow_with_scorch(self, pyroform_for_workflow):
#       """Test workflow execution with scorch action"""
#       pass
#   # TODO
#   def test_execute_workflow_with_snapshot(self, pyroform_for_workflow):
#       """Test workflow execution with snapshot action"""
#       pass
#   # TODO
#   def test_execute_workflow_unknown_action(self, pyroform_for_workflow):
#       """Test workflow execution with unknown action"""
#       pass
#   # TODO
#   def test_execute_workflow_step_failure(self, pyroform_for_workflow):
#       """Test workflow execution when a step fails"""
#       pass
#   # TODO
#   def test_execute_workflow_step_exception(self, pyroform_for_workflow):
#       """Test workflow execution when a step raises an exception"""
#       pass
#   # TODO
#   def test_execute_workflow_with_report_generation(self):
#       """Test workflow execution with report generation"""
#       pass

    @pytest.fixture
    def pyroform_for_workflow(self):
        """Create Pyroform instance for workflow testing"""
        with patch('pyroform.pyroform.PyroformEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine

            pf = Pyroform(auto_confirm=True)

            # Mock the action methods
            pf.validate = Mock(return_value={'is_valid': True})
            pf.configure = Mock(return_value=True)
            pf.mount = Mock(return_value=True)
            pf.scorch = Mock(return_value={'success': True})
            pf.snapshot = Mock(return_value={'success': True})
            pf._generate_workflow_report = Mock(return_value=True)

            return pf

    def test_execute_workflow_invalid_step(self, pyroform_for_workflow):
        """Test workflow execution with invalid step"""
        pf = pyroform_for_workflow

        # Missing input_path
        workflow_steps = [
            {"action": "validate"}
        ]

        with patch('builtins.print') as mock_print:
            result = pf.execute_workflow(workflow_steps)

            assert result is False
            mock_print.assert_called_once_with("Invalid workflow step: {'action': 'validate'}")

    def test_generate_workflow_summary(self):
        """Test _generate_workflow_summary method"""
        pf = Pyroform()

        workflow_results = [
            {"action": "validate", "success": True},
            {"action": "configure", "success": True},
            {"action": "mount", "success": False}
        ]

        summary = pf._generate_workflow_summary(workflow_results)

        assert summary["total_duration_seconds"] == 0  # Not tracking duration
        assert summary["actions_performed"] == ["validate", "configure", "mount"]
        assert summary["overall_success"] is False  # One step failed

    def test_generate_workflow_report_success(self):
        """Test _generate_workflow_report method success"""
        with patch('pyroform.pyroform.PyroformEngine') as MockEngine, \
             patch('pyroform.pyroform.datetime') as mock_datetime:

            mock_engine = Mock()
            mock_reporter = Mock()
            mock_engine.reporter = mock_reporter
            MockEngine.return_value = mock_engine

            mock_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            pf = Pyroform()

            workflow_results = [
                {"action": "validate", "success": True, "result": {'is_valid': True}},
                {"action": "configure", "success": False, "result": False}
            ]

            mock_reporter.save_report.return_value = True

            result = pf._generate_workflow_report(workflow_results, "/tmp/report.json")

            assert result is True
            mock_reporter.save_report.assert_called_once()

            # Verify report structure
            call_args = mock_reporter.save_report.call_args[0]
            report = call_args[0]
            assert report["type"] == "workflow"
            assert report["total_steps"] == 2
            assert report["successful_steps"] == 1
            assert report["failed_steps"] == 1
            assert report["steps"] == workflow_results

    def test_generate_workflow_report_failure(self):
        """Test _generate_workflow_report method failure"""
        with patch('pyroform.pyroform.PyroformEngine') as MockEngine, \
             patch('builtins.print'):

            mock_engine = Mock()
            mock_reporter = Mock()
            mock_engine.reporter = mock_reporter
            MockEngine.return_value = mock_engine

            pf = Pyroform()

            workflow_results = []

            mock_reporter.save_report.side_effect = Exception("Save failed")

            with patch('builtins.print') as mock_print:
                result = pf._generate_workflow_report(workflow_results, "/tmp/report.json")

                assert result is False
                mock_print.assert_called_once_with("Failed to generate workflow report: Save failed")


class TestPyroformLoadConfig:
    """Test _load_config method"""

    def test_load_config_defaults(self):
        """Test _load_config returns defaults when no config file"""
        pf = Pyroform()

        # Call _load_config directly
        config = pf._load_config(None, auto_confirm=True, dry_run=False, debug=True)

        assert config["safety_checks"] is True
        assert config["default_output_dir"] == "/tmp/pyroform"
        assert config["log_level"] == "INFO"
        assert config["log_timestamp"] is False
        assert config["auto_confirm"] is True
        assert config["dry_run"] is False
        assert config["debug"] is True

    def test_load_config_with_yaml_file(self):
        """Test _load_config with YAML config file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                "safety_checks": False,
                "log_level": "DEBUG",
                "custom_setting": "custom_value"
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            pf = Pyroform()
            config = pf._load_config(config_path, auto_confirm=False)

            # Should merge with defaults
            assert config["safety_checks"] is False  # From file
            assert config["log_level"] == "DEBUG"  # From file
            assert config["auto_confirm"] is False  # From kwargs
            assert config["custom_setting"] == "custom_value"  # From file
            assert config["default_output_dir"] == "/tmp/pyroform"  # Default
        finally:
            Path(config_path).unlink()

    def test_load_config_with_json_file(self):
        """Test _load_config with JSON config file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                "log_level": "WARNING",
                "dry_run": True
            }
            json.dump(config_data, f)
            config_path = f.name

        try:
            pf = Pyroform()
            config = pf._load_config(config_path, debug=True)

            assert config["log_level"] == "WARNING"  # From file
            assert config["dry_run"] is True  # From file
            assert config["debug"] is True  # From kwargs
            assert config["safety_checks"] is True  # Default
        finally:
            Path(config_path).unlink()

    def test_load_config_nonexistent_file(self):
        """Test _load_config with nonexistent config file"""
        pf = Pyroform()

        with patch('builtins.print') as mock_print:
            config = pf._load_config("/nonexistent/config.yaml", auto_confirm=True)

            mock_print.assert_called_once_with(
                "Config file not found: /nonexistent/config.yaml, using defaults"
            )
            # Should return defaults
            assert config["auto_confirm"] is True
            assert config["log_level"] == "INFO"

    def test_load_config_unsupported_format(self):
        """Test _load_config with unsupported file format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test config")
            config_path = f.name

        try:
            pf = Pyroform()

            with patch('builtins.print') as mock_print:
                config = pf._load_config(config_path)

                mock_print.assert_called_once_with(
                    f"Unsupported config file format: .txt"
                )
                # Should return defaults
                assert config["log_level"] == "INFO"
        finally:
            Path(config_path).unlink()

    def test_load_config_yaml_parse_error(self):
        """Test _load_config with YAML parse error"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: : : :")
            config_path = f.name

        try:
            pf = Pyroform()

            with patch('builtins.print') as mock_print:
                config = pf._load_config(config_path)

                mock_print.assert_called_once()
                assert "Error loading config file" in mock_print.call_args[0][0]
                # Should return defaults
                assert config["log_level"] == "INFO"
        finally:
            Path(config_path).unlink()

    def test_load_config_json_parse_error(self):
        """Test _load_config with JSON parse error"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json")
            config_path = f.name

        try:
            pf = Pyroform()

            with patch('builtins.print') as mock_print:
                config = pf._load_config(config_path)

                mock_print.assert_called_once()
                assert "Error loading config file" in mock_print.call_args[0][0]
                # Should return defaults
                assert config["log_level"] == "INFO"
        finally:
            Path(config_path).unlink()


class TestPyroformEdgeCases:
    """Test edge cases and error scenarios"""

#   # TODO
#   def test_workflow_with_missing_success_field(self):
#       """Test workflow execution when result doesn't have success field"""
#       pass

    def test_action_methods_with_engine_exception(self):
        """Test action methods when engine raises exception"""
        with patch('pyroform.pyroform.PyroformEngine') as MockEngine:
            mock_engine = Mock()
            mock_engine.configure = Mock(side_effect=Exception("Engine error"))
            MockEngine.return_value = mock_engine

            pf = Pyroform()

            # Method should propagate the exception
            with pytest.raises(Exception, match="Engine error"):
                pf.configure("/path/to/config.yaml")

    def test_concurrent_action_execution(self):
        """Test that last_action and last_result are properly tracked"""
        with patch('pyroform.pyroform.PyroformEngine') as MockEngine:
            mock_engine = Mock()
            mock_engine.configure = Mock(return_value=True)
            mock_engine.validate = Mock(return_value={'is_valid': False})
            MockEngine.return_value = mock_engine

            pf = Pyroform()

            # Execute configure
            pf.configure("/path/to/config1.yaml")
            assert pf._last_action == ActionType.CONFIGURE
            assert pf._last_result is True

            # Execute validate
            pf.validate("/path/to/config2.yaml")
            assert pf._last_action == ActionType.VALIDATE
            assert pf._last_result == {'is_valid': False}

    def test_empty_workflow(self):
        """Test execute_workflow with empty steps list"""
        pf = Pyroform()

        result = pf.execute_workflow([])

        assert result is True
        assert pf._workflow_results == []


# Main test execution
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
