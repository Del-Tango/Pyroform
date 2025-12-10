"""
Unit Test Suite for Pyroform Class

This module contains unit tests for the Pyroform main library interface class.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from pyroform.pyroform import Pyroform
from pyroform.src.models import ActionType


class TestPyroformInitialization:
    """Test Pyroform class initialization and basic properties"""

#   # TODO
#   def test_initialization_with_config_file(self):
#       """Test Pyroform initialization with config file"""
#   def test_initialization_with_nonexistent_config_file(self):
#       """Test Pyroform initialization with nonexistent config file"""
#   def test_initialization_with_invalid_config_format(self):
#       """Test Pyroform initialization with invalid config file format"""
#   def test_initialization_with_malformed_yaml(self):
#       """Test Pyroform initialization with malformed YAML config"""
#   def test_initialization_without_config_file(self):
#       """Test Pyroform initialization without config file"""
#   def test_initialization_with_auto_confirm(self):
#       """Test Pyroform initialization with auto_confirm"""
#   def test_initialization_with_json_config_file(self):
#       """Test Pyroform initialization with JSON config file"""

    def test_initialization_with_dry_run(self):
        """Test Pyroform initialization with dry_run"""
        pf = Pyroform(dry_run=True)
        assert pf.config["dry_run"] is True

    def test_initialization_with_debug(self):
        """Test Pyroform initialization with debug mode"""
        pf = Pyroform(debug=True)
        assert pf.config["debug"] is True


class TestPyroformConfigurationManagement:
    """Test configuration management methods"""

#   # TODO
#   def test_version_property(self):
#       """Test version property returns version string"""
#   def test_set_config(self, pyroform_instance):
#       """Test set_config updates configuration"""

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


class TestPyroformActionMethods:
    """Test main action methods (configure, scorch, mount, validate, snapshot)"""

    # TODO
#   def test_configure_success(self, pyroform_with_mocked_engine):
#       """Test configure method success"""
#   def test_scorch_success(self, pyroform_with_mocked_engine):
#       """Test scorch method success"""
#   def test_mount_success(self, pyroform_with_mocked_engine):
#       """Test mount method success"""

    @pytest.fixture
    def pyroform_with_mocked_engine(self):
        """Create Pyroform instance with mocked engine"""
        with patch("pyroform.pyroform.PyroformEngine") as MockEngine:
            mock_engine = Mock()
            mock_engine.configure = Mock(return_value=True)
            mock_engine.scorch = Mock(
                return_value={"success": True, "resources_removed": []}
            )
            mock_engine.mount = Mock(return_value=True)
            mock_engine.validate = Mock(
                return_value={"is_valid": True, "discrepancies": []}
            )
            mock_engine.snapshot = Mock(
                return_value={"success": True, "output_path": "/tmp/snapshot.yaml"}
            )
            mock_engine.reporter = Mock()
            mock_engine.reporter.generate_action_report = Mock(
                return_value={"action": "test", "success": True}
            )
            mock_engine.reporter.save_report = Mock(return_value=True)

            MockEngine.return_value = mock_engine
            pf = Pyroform(auto_confirm=True)

            return pf, mock_engine

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
            dry_run=True,
        )

    def test_configure_failure(self, pyroform_with_mocked_engine):
        """Test configure method failure"""
        pf, mock_engine = pyroform_with_mocked_engine
        mock_engine.configure.return_value = False

        result = pf.configure("/path/to/config.yaml")

        assert result is False
        assert pf._last_action == ActionType.CONFIGURE
        assert pf._last_result is False

    def test_scorch_kwargs_merging(self):
        """Test scorch method properly merges auto_confirm"""
        with patch("pyroform.pyroform.PyroformEngine") as MockEngine:
            mock_engine = Mock()
            mock_engine.scorch = Mock(return_value={"success": True})
            MockEngine.return_value = mock_engine

            # Instance with auto_confirm=False
            pf = Pyroform(auto_confirm=False)

            # Call scorch with auto_confirm in kwargs
            pf.scorch("/path/to/config.yaml", auto_confirm=True, dry_run=False)

            # Should use kwargs auto_confirm
            mock_engine.scorch.assert_called_once_with(
                "/path/to/config.yaml", auto_confirm=True, dry_run=False  # From kwargs
            )

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
        mock_result = {
            "is_valid": True,
            "discrepancies": [],
            "summary": {"total_issues": 0},
        }
        mock_engine.validate.return_value = mock_result

        result = pf.validate("/path/to/config.yaml", verbose=True)

        assert result == mock_result
        mock_engine.validate.assert_called_once_with(
            "/path/to/config.yaml", verbose=True
        )
        assert pf._last_action == ActionType.VALIDATE
        assert pf._last_result == mock_result

    def test_validate_failure(self, pyroform_with_mocked_engine):
        """Test validate method with validation failure"""
        pf, mock_engine = pyroform_with_mocked_engine
        mock_result = {
            "is_valid": False,
            "discrepancies": [{"type": "user", "issue": "User missing"}],
            "summary": {"total_issues": 1},
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

        assert result == {"success": True, "output_path": "/tmp/snapshot.yaml"}
        mock_engine.snapshot.assert_called_once_with("/tmp/snapshot.yaml", max_depth=5)
        assert pf._last_action == ActionType.SNAPSHOT
        assert pf._last_result == {"success": True, "output_path": "/tmp/snapshot.yaml"}

    def test_snapshot_with_input_path(self, pyroform_with_mocked_engine):
        """Test snapshot method with input path (even though it's not used in the method)"""
        pf, mock_engine = pyroform_with_mocked_engine
        result = pf.snapshot(
            input_path="/path/to/config.yaml", output_path="/tmp/snapshot.yaml"
        )
        mock_engine.snapshot.assert_called_once_with("/tmp/snapshot.yaml")

    def test_snapshot_failure(self, pyroform_with_mocked_engine):
        """Test snapshot method failure"""
        pf, mock_engine = pyroform_with_mocked_engine
        mock_engine.snapshot.return_value = {
            "success": False,
            "error": "Failed to create snapshot",
        }

        result = pf.snapshot(output_path="/tmp/snapshot.yaml")

        assert result == {"success": False, "error": "Failed to create snapshot"}
        assert pf._last_action == ActionType.SNAPSHOT
        assert pf._last_result == {
            "success": False,
            "error": "Failed to create snapshot",
        }


class TestPyroformGenerateReport:
    """Test generate_report method"""

    # TODO
#   def test_generate_report_with_output_path(self, pyroform_with_mocked_engine_and_last_action):
#       """Test generate_report with output path"""
#   def test_generate_report_no_last_action(self):
#       """Test generate_report when no action has been executed"""

    @pytest.fixture
    def pyroform_with_mocked_engine_and_last_action(self):
        """Create Pyroform with mocked engine and last action set"""
        with patch("pyroform.pyroform.PyroformEngine") as MockEngine, patch(
            "pyroform.pyroform.datetime"
        ) as mock_datetime, patch("builtins.print"):

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
            pf._last_result = {"success": True, "processed_configs": ["test_config"]}

            return pf, mock_reporter, mock_now

    def test_generate_report_without_output_path(
        self, pyroform_with_mocked_engine_and_last_action
    ):
        """Test generate_report without output path (prints to stdout)"""
        pf, mock_reporter, mock_now = pyroform_with_mocked_engine_and_last_action

        mock_report = {"action": "configure", "success": True}
        mock_reporter.generate_action_report.return_value = mock_report

        with patch("builtins.print") as mock_print:
            result = pf.generate_report()

            assert result is True
            mock_print.assert_called_once()
            # Should print JSON
            call_args = mock_print.call_args[0][0]
            assert "configure" in call_args
            mock_reporter.save_report.assert_not_called()


class TestPyroformWorkflowExecution:
    """Test execute_workflow method"""

#   # TODO
#   def test_execute_workflow_success(self, pyroform_for_workflow):
#       """Test successful workflow execution"""
#   def test_execute_workflow_with_scorch(self, pyroform_for_workflow):
#       """Test workflow execution with scorch action"""
#   def test_execute_workflow_with_snapshot(self, pyroform_for_workflow):
#       """Test workflow execution with snapshot action"""
#   def test_execute_workflow_unknown_action(self, pyroform_for_workflow):
#       """Test workflow execution with unknown action"""
#   def test_execute_workflow_step_failure(self, pyroform_for_workflow):
#       """Test workflow execution when a step fails"""
#   def test_execute_workflow_step_exception(self, pyroform_for_workflow):
#       """Test workflow execution when a step raises an exception"""
#   def test_execute_workflow_with_report_generation(self):
#       """Test workflow execution with report generation"""
#   def test_execute_workflow_invalid_step(self, pyroform_for_workflow):
#       """Test workflow execution with invalid step"""
#   def test_generate_workflow_report_success(self):
#       """Test _generate_workflow_report method success"""
#   def test_generate_workflow_report_failure(self):
#       """Test _generate_workflow_report method failure"""

    @pytest.fixture
    def pyroform_for_workflow(self):
        """Create Pyroform instance for workflow testing"""
        with patch("pyroform.pyroform.PyroformEngine") as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine

            pf = Pyroform(auto_confirm=True)

            # Mock the action methods
            pf.validate = Mock(return_value={"is_valid": True})
            pf.configure = Mock(return_value=True)
            pf.mount = Mock(return_value=True)
            pf.scorch = Mock(return_value={"success": True})
            pf.snapshot = Mock(return_value={"success": True})
            pf._generate_workflow_report = Mock(return_value=True)

            return pf

    def test_generate_workflow_summary(self):
        """Test _generate_workflow_summary method"""
        pf = Pyroform()

        workflow_results = [
            {"action": "validate", "success": True},
            {"action": "configure", "success": True},
            {"action": "mount", "success": False},
        ]

        summary = pf._generate_workflow_summary(workflow_results)

        assert summary["total_duration_seconds"] == 0  # Not tracking duration
        assert summary["actions_performed"] == ["validate", "configure", "mount"]
        assert summary["overall_success"] is False  # One step failed

# TODO
#   class TestPyroformLoadConfig:
#       """Test _load_config method"""

#   def test_load_config_defaults(self):
#       """Test _load_config returns defaults when no config file"""
#   def test_load_config_with_yaml_file(self):
#       """Test _load_config with YAML config file"""
#   def test_load_config_with_json_file(self):
#       """Test _load_config with JSON config file"""
#   def test_load_config_nonexistent_file(self):
#       """Test _load_config with nonexistent config file"""
#   def test_load_config_unsupported_format(self):
#       """Test _load_config with unsupported file format"""
#   def test_load_config_yaml_parse_error(self):
#       """Test _load_config with YAML parse error"""
#   def test_load_config_json_parse_error(self):
#       """Test _load_config with JSON parse error"""


class TestPyroformEdgeCases:
    """Test edge cases and error scenarios"""

    # TODO
#   def test_workflow_with_missing_success_field(self):
#       """Test workflow execution when result doesn't have success field"""

    def test_action_methods_with_engine_exception(self):
        """Test action methods when engine raises exception"""
        with patch("pyroform.pyroform.PyroformEngine") as MockEngine:
            mock_engine = Mock()
            mock_engine.configure = Mock(side_effect=Exception("Engine error"))
            MockEngine.return_value = mock_engine

            pf = Pyroform()

            # Method should propagate the exception
            with pytest.raises(Exception, match="Engine error"):
                pf.configure("/path/to/config.yaml")

    def test_concurrent_action_execution(self):
        """Test that last_action and last_result are properly tracked"""
        with patch("pyroform.pyroform.PyroformEngine") as MockEngine:
            mock_engine = Mock()
            mock_engine.configure = Mock(return_value=True)
            mock_engine.validate = Mock(return_value={"is_valid": False})
            MockEngine.return_value = mock_engine

            pf = Pyroform()

            # Execute configure
            pf.configure("/path/to/config1.yaml")
            assert pf._last_action == ActionType.CONFIGURE
            assert pf._last_result is True

            # Execute validate
            pf.validate("/path/to/config2.yaml")
            assert pf._last_action == ActionType.VALIDATE
            assert pf._last_result == {"is_valid": False}

    def test_empty_workflow(self):
        """Test execute_workflow with empty steps list"""
        pf = Pyroform()

        result = pf.execute_workflow([])

        assert result is True
        assert pf._workflow_results == []


# Main test execution
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
