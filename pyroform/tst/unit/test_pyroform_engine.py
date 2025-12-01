"""
Pyroform Engine Test Suite

Unit tests for the PyroformEngine class.
"""

import pytest
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call, mock_open
from typing import Dict, Any, List
import tempfile
import sys

from pyroform.src.pyroform_engine import PyroformEngine, OperationResult
from pyroform.src.models import ActionType, PyroConfig
from pyroform.src.validator import ValidationResult


@pytest.fixture
def mock_stdout():
    """Mock STDOUTMsg to avoid console output during tests."""
    mock = Mock()
    mock.debug = Mock()
    mock.ok = Mock()
    mock.err = Mock()
    mock.info = Mock()
    mock.warn = Mock()
    mock.nok = Mock()
    return mock


@pytest.fixture
def mock_parser():
    """Mock PyroParser."""
    mock = Mock()
    mock.parse = Mock()
    return mock


@pytest.fixture
def mock_sketch_generator():
    """Mock SketchGenerator."""
    mock = Mock()
    mock.generate_sketch = Mock()
    mock.generate_scorch_sketch = Mock()
    return mock


@pytest.fixture
def mock_flow_engine():
    """Mock PyroflowEngine."""
    mock = Mock()
    mock.execute_sketch = Mock(return_value=True)
    return mock


@pytest.fixture
def mock_validator():
    """Mock SystemValidator."""
    mock = Mock()
    mock.get_system_state = Mock()
    mock.validate_configuration = Mock()
    mock._last_result = Mock(system_state={})
    return mock


@pytest.fixture
def mock_reporter():
    """Mock ReportGenerator."""
    return Mock()


@pytest.fixture
def pyro_config():
    """Create a mock PyroConfig instance."""
    config = Mock(spec=PyroConfig)
    config.label = "test_config"
    return config


@pytest.fixture
def engine_with_mocks(mock_stdout, mock_parser, mock_sketch_generator,
                      mock_flow_engine, mock_validator, mock_reporter):
    """Create PyroformEngine with mocked dependencies."""
    with patch('pyroform.src.pyroform_engine.STDOUTMsg', return_value=mock_stdout), \
         patch('pyroform.src.pyroform_engine.PyroParser', return_value=mock_parser), \
         patch('pyroform.src.pyroform_engine.SketchGenerator', return_value=mock_sketch_generator), \
         patch('pyroform.src.pyroform_engine.PyroflowEngine', return_value=mock_flow_engine), \
         patch('pyroform.src.pyroform_engine.SystemValidator', return_value=mock_validator), \
         patch('pyroform.src.pyroform_engine.ReportGenerator', return_value=mock_reporter):

        engine = PyroformEngine()
        engine.stdout = mock_stdout
        engine.parser = mock_parser
        engine.sketch_generator = mock_sketch_generator
        engine.flow_engine = mock_flow_engine
        engine.validator = mock_validator
        engine.reporter = mock_reporter

        return engine


@pytest.fixture
def default_config():
    """Return default configuration."""
    return {
        "safety_checks": True,
        "default_output_dir": "/tmp/pyroform",
        "log_level": "INFO",
        "log_timestamp": False,
        "auto_confirm": False,
        "dry_run": False,
        "debug": True,
    }


class TestPyroformEngineInitialization:
    """Test PyroformEngine initialization."""

#   # TODO
#   def test_init_with_custom_config(self):
#       """Test initialization with custom config."""
#       pass

    def test_init_with_default_config(self):
        """Test initialization with no config provided."""
        with patch('pyroform.src.pyroform_engine.STDOUTMsg') as mock_stdout_cls, \
             patch('pyroform.src.pyroform_engine.PyroParser') as mock_parser_cls, \
             patch('pyroform.src.pyroform_engine.SketchGenerator') as mock_sketch_cls, \
             patch('pyroform.src.pyroform_engine.PyroflowEngine') as mock_flow_cls, \
             patch('pyroform.src.pyroform_engine.SystemValidator') as mock_validator_cls, \
             patch('pyroform.src.pyroform_engine.ReportGenerator') as mock_reporter_cls:

            engine = PyroformEngine()

            # Verify default config was used
            assert engine.config["safety_checks"] == True
            assert engine.config["default_output_dir"] == "/tmp/pyroform"

            # Verify components initialized
            mock_stdout_cls.assert_called_once()
            mock_parser_cls.assert_called_once()
            mock_sketch_cls.assert_called_once()
            mock_flow_cls.assert_called_once()
            mock_validator_cls.assert_called_once()
            mock_reporter_cls.assert_called_once()

    def test_init_with_invalid_config_path(self):
        """Test initialization with invalid config path raises ValueError."""
        invalid_config = {
            "default_output_dir": "/non/existent/parent/path"
        }

        with pytest.raises(ValueError, match="parent does not exist"):
            PyroformEngine(config=invalid_config)

    def test_validate_config_method(self):
        """Test _validate_config method."""
        engine = PyroformEngine()

        # Valid config should not raise
        valid_config = {
            "default_output_dir": str(Path.home())  # Parent exists
        }
        engine.config = valid_config
        engine._validate_config()  # Should not raise

        # Invalid config should raise
        invalid_config = {
            "default_output_dir": "/this/path/does/not/exist/123"
        }
        engine.config = invalid_config
        with pytest.raises(ValueError):
            engine._validate_config()

    def test_get_default_config(self):
        """Test _get_default_config method."""
        engine = PyroformEngine()
        default_config = engine._get_default_config()

        assert isinstance(default_config, dict)
        assert "safety_checks" in default_config
        assert "default_output_dir" in default_config
        assert "log_level" in default_config
        assert default_config["safety_checks"] == True
        assert default_config["dry_run"] == False


class TestSnapshotMethod:
    """Test the snapshot method."""

    def test_snapshot_success(self, engine_with_mocks, mock_validator):
        """Test successful snapshot creation."""
        # Setup
        mock_system_state = {"files": ["/etc/hosts"], "dirs": ["/tmp"]}
        mock_validator.get_system_state.return_value = mock_system_state

        mock_sketch = {"actions": ["snapshot_action"]}
        engine_with_mocks.sketch_generator.generate_sketch.return_value = mock_sketch

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "snapshot.yaml"
            result = engine_with_mocks.snapshot(str(output_path))

            # Verify
            assert result["success"] == True
            assert result["output_path"] == str(output_path)
            assert result["system_state"] == mock_system_state

            mock_validator.get_system_state.assert_called_once_with(
                max_depth=100,
                include_hidden=True
            )

            engine_with_mocks.sketch_generator.generate_sketch.assert_called_once_with(
                None,
                ActionType.SNAPSHOT
            )

            engine_with_mocks.stdout.ok.assert_called_once_with(
                f'System snapshot written to: {output_path}'
            )

    def test_snapshot_with_custom_parameters(self, engine_with_mocks):
        """Test snapshot with custom parameters."""
        engine_with_mocks.snapshot(
            "/tmp/test.yaml",
            max_depth=5,
            include_hidden=False
        )

        engine_with_mocks.validator.get_system_state.assert_called_once_with(
            max_depth=5,
            include_hidden=False
        )

    def test_snapshot_directory_creation(self, engine_with_mocks, mock_validator):
        """Test that output directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = Path(tmpdir) / "deeply" / "nested" / "snapshot.yaml"

            # Mock system state
            mock_validator.get_system_state.return_value = {}
            engine_with_mocks.sketch_generator.generate_sketch.return_value = {}

            result = engine_with_mocks.snapshot(str(nested_path))

            # Verify parent directory was created
            assert nested_path.parent.exists()
            assert result["success"] == True

    def test_snapshot_exception_handling(self, engine_with_mocks, mock_validator):
        """Test snapshot exception handling."""
        # Setup exception
        mock_validator.get_system_state.side_effect = Exception("Test error")

        # Execute
        result = engine_with_mocks.snapshot("/tmp/test.yaml")

        # Verify
        assert result["success"] == False
        assert "error" in result
        assert result["error"] == "Test error"
        engine_with_mocks.stdout.err.assert_called_once()

    @patch('pyroform.src.pyroform_engine.Path')
    @patch('builtins.open', new_callable=mock_open)
    def test_snapshot_file_writing(self, mock_file, mock_path_cls, engine_with_mocks, mock_validator):
        """Test snapshot YAML file writing."""
        # Setup
        mock_validator.get_system_state.return_value = {}
        mock_sketch = {"key": "value", "list": [1, 2, 3]}
        engine_with_mocks.sketch_generator.generate_sketch.return_value = mock_sketch

        # Mock Path behavior
        mock_path = Mock()
        mock_path.parent = Mock()
        mock_path.parent.mkdir = Mock()
        mock_path.open = Mock(return_value=mock_file())
        mock_path_cls.return_value = mock_path

        # Execute
        result = engine_with_mocks.snapshot("/test/path.yaml")

        # Verify YAML was written correctly
        mock_file().write.assert_called()
        # Can't easily verify YAML content due to mock, but we can verify the call happened


class TestConfigureMethod:
    """Test the configure method."""

#   # TODO
#   def test_configure_multiple_configs(self, engine_with_mocks, mock_parser):
#       """Test configuration with multiple configs."""
#       pass

    def test_configure_success(self, engine_with_mocks, mock_parser, pyro_config):
        """Test successful configuration."""
        # Setup
        mock_parser.parse.return_value = [pyro_config]
        mock_sketch = {"actions": ["configure_action1", "configure_action2"]}
        engine_with_mocks.sketch_generator.generate_sketch.return_value = mock_sketch
        engine_with_mocks.flow_engine.execute_sketch.return_value = True

        # Execute
        result = engine_with_mocks.configure("/path/to/configs")

        # Verify
        assert result["success"] == True
        assert result["processed_configs"] == ["test_config"]
        assert len(result["results"]) == 1

        mock_parser.parse.assert_called_once_with(Path("/path/to/configs"))
        engine_with_mocks.sketch_generator.generate_sketch.assert_called_once_with(
            pyro_config,
            ActionType.CONFIGURE
        )

    def test_configure_no_valid_files(self, engine_with_mocks, mock_parser):
        """Test configure with no valid Pyro files."""
        mock_parser.parse.return_value = []

        result = engine_with_mocks.configure("/invalid/path")

        assert result["success"] == False
        assert result["processed_configs"] == []
        engine_with_mocks.stdout.err.assert_called_once_with(
            'No valid Pyro files found at: /invalid/path'
        )

    def test_configure_skipped_config(self, engine_with_mocks, mock_parser, pyro_config):
        """Test configure with empty sketch (skipped config)."""
        mock_parser.parse.return_value = [pyro_config]
        engine_with_mocks.sketch_generator.generate_sketch.return_value = {"empty": True}

        result = engine_with_mocks.configure("/path")

        # Verify skipped result
        config_result = result["results"][0]
        assert config_result["success"] == True
        assert config_result["skipped"] == True
        assert engine_with_mocks.flow_engine.execute_sketch.call_count == 0

    def test_configure_exception_handling(self, engine_with_mocks, mock_parser):
        """Test configure exception handling."""
        mock_parser.parse.side_effect = Exception("Parse error")

        result = engine_with_mocks.configure("/path")

        assert result["success"] == False
        assert "error" in result
        assert result["error"] == "Parse error"


class TestScorchMethod:
    """Test the scorch method."""

#   # TODO
#   def test_scorch_with_dry_run(self, engine_with_mocks, mock_parser, pyro_config):
#       """Test scorch with dry_run=True."""
#       pass
#   # TODO
#   def test_scorch_user_cancellation(self, engine_with_mocks, mock_parser, pyro_config):
#       """Test scorch when user cancels."""
#       pass
#   # TODO
#   def test_scorch_empty_sketch(self, engine_with_mocks, mock_parser, pyro_config):
#       """Test scorch with empty sketch (nothing to remove)."""
#       pass
#   # TODO
#   def test_scorch_multiple_configs(self, engine_with_mocks, mock_parser):
#       """Test scorch with multiple configs."""
#       pass

    def test_scorch_success(self, engine_with_mocks, mock_parser, pyro_config):
        """Test successful scorch operation."""
        # Setup
        mock_parser.parse.return_value = [pyro_config]
        mock_sketch = {"actions": ["remove_action1", "remove_action2"]}
        engine_with_mocks.sketch_generator.generate_scorch_sketch.return_value = mock_sketch

        # Mock user confirmation
        with patch.object(engine_with_mocks, '_confirm_scorch', return_value=True):
            result = engine_with_mocks.scorch("/path/to/configs", auto_confirm=False)

        # Verify
        assert result["success"] == True
        assert result["dry_run"] == False
        assert "resources_removed" in result
        assert "resources_failed" in result

        engine_with_mocks.sketch_generator.generate_scorch_sketch.assert_called_once_with(
            pyro_config
        )

    def test_scorch_with_auto_confirm(self, engine_with_mocks, mock_parser, pyro_config):
        """Test scorch with auto_confirm=True."""
        mock_parser.parse.return_value = [pyro_config]
        engine_with_mocks.sketch_generator.generate_scorch_sketch.return_value = {"actions": []}

        # Should not ask for confirmation
        with patch.object(engine_with_mocks, '_confirm_scorch') as mock_confirm:
            result = engine_with_mocks.scorch("/path", auto_confirm=True)

            mock_confirm.assert_not_called()
            assert result["success"] == True

    def test_scorch_exception_handling(self, engine_with_mocks, mock_parser):
        """Test scorch exception handling."""
        mock_parser.parse.side_effect = Exception("Test error")

        result = engine_with_mocks.scorch("/path")

        assert result["success"] == False
        assert "error" in result
        assert result["error"] == "Test error"


class TestValidateMethod:
    """Test the validate method."""

#   # TODO
#   def test_validate_success(self, engine_with_mocks, mock_parser, pyro_config):
#       """Test successful validation."""
#       pass
#   # TODO
#   def test_validate_with_discrepancies(self, engine_with_mocks, mock_parser, pyro_config):
#       """Test validation with discrepancies."""
#       pass
#   # TODO
#   def test_validate_multiple_configs(self, engine_with_mocks, mock_parser):
#       """Test validation with multiple configs."""
#       pass
#   # TODO
#   def test_validate_no_valid_files(self, engine_with_mocks, mock_parser):
#       """Test validate with no valid Pyro files."""
#       pass
#   # TODO
#   def test_validate_exception_handling(self, engine_with_mocks, mock_parser):
#       """Test validate exception handling."""
#       pass
#   # TODO
#   def test_log_validation_methods(self, engine_with_mocks):
#       """Test the validation logging helper methods."""
#       pass

class TestMountMethod:
    """Test the mount method."""

    def test_mount_success(self, engine_with_mocks, mock_parser, pyro_config):
        """Test successful mount operation."""
        # Mock _execute_config_action since mount delegates to it
        expected_result = {
            "success": True,
            "processed_configs": ["test_config"],
            "results": [{"success": True}]
        }

        with patch.object(engine_with_mocks, '_execute_config_action',
                         return_value=expected_result) as mock_execute:
            result = engine_with_mocks.mount("/path/to/mounts.yaml")

            mock_execute.assert_called_once_with(
                "/path/to/mounts.yaml",
                ActionType.MOUNT
            )
            assert result == expected_result

    def test_mount_with_kwargs(self, engine_with_mocks):
        """Test mount passes kwargs to _execute_config_action."""
        kwargs = {"option1": "value1", "option2": "value2"}

        with patch.object(engine_with_mocks, '_execute_config_action') as mock_execute:
            engine_with_mocks.mount("/path", **kwargs)

            mock_execute.assert_called_once_with(
                "/path",
                ActionType.MOUNT,
                option1="value1",
                option2="value2"
            )


class TestInternalHelperMethods:
    """Test internal helper methods."""

#   # TODO
#   def test_process_configuration_success(self, engine_with_mocks, pyro_config):
#       """Test _process_configuration success."""
#       pass
#   # TODO
#   def test_execute_scorch_config_success(self, engine_with_mocks, pyro_config):
#       """Test _execute_scorch_config success."""
#       pass
#   # TODO
#   def test_execute_scorch_config_needs_confirmation(self, engine_with_mocks, pyro_config):
#       """Test _execute_scorch_config with user confirmation."""
#       pass

    def test_process_configuration_skipped(self, engine_with_mocks, pyro_config):
        """Test _process_configuration with empty sketch."""
        engine_with_mocks.sketch_generator.generate_sketch.return_value = {"empty": True}

        result = engine_with_mocks._process_configuration(
            pyro_config,
            ActionType.CONFIGURE
        )

        assert result["success"] == True
        assert result["skipped"] == True
        assert engine_with_mocks.flow_engine.execute_sketch.call_count == 0
        engine_with_mocks.stdout.info.assert_called_once_with(
            'No actions required for test_config, skipping'
        )

    def test_process_configuration_exception(self, engine_with_mocks, pyro_config):
        """Test _process_configuration exception handling."""
        engine_with_mocks.sketch_generator.generate_sketch.side_effect = Exception("Test error")

        result = engine_with_mocks._process_configuration(
            pyro_config,
            ActionType.CONFIGURE
        )

        assert result["success"] == False
        assert "error" in result
        assert result["error"] == "Test error"
        engine_with_mocks.stdout.err.assert_called_once_with(
            "Failed to process test_config: Test error"
        )

    def test_execute_config_action_success(self, engine_with_mocks, mock_parser, pyro_config):
        """Test _execute_config_action success."""
        mock_parser.parse.return_value = [pyro_config]

        # Mock _process_configuration
        process_result = {"success": True, "config_label": "test_config"}
        with patch.object(engine_with_mocks, '_process_configuration',
                         return_value=process_result):
            result = engine_with_mocks._execute_config_action(
                "/path",
                ActionType.MOUNT
            )

            assert result["success"] == True
            assert result["processed_configs"] == ["test_config"]
            mock_parser.parse.assert_called_once_with(Path("/path"))

    def test_execute_config_action_no_configs(self, engine_with_mocks, mock_parser):
        """Test _execute_config_action with no configs found."""
        mock_parser.parse.return_value = []

        result = engine_with_mocks._execute_config_action(
            "/path",
            ActionType.MOUNT
        )

        assert result["success"] == False
        assert result["error"] == "No configurations found"

    def test_execute_config_action_exception(self, engine_with_mocks, mock_parser):
        """Test _execute_config_action exception handling."""
        mock_parser.parse.side_effect = Exception("Parse error")

        result = engine_with_mocks._execute_config_action(
            "/path",
            ActionType.MOUNT
        )

        assert result["success"] == False
        assert result["error"] == "Parse error"
        engine_with_mocks.stdout.err.assert_called_once_with(
            'mount operation failed: Parse error'
        )

    @patch('builtins.input')
    def test_confirm_scorch_yes(self, mock_input, engine_with_mocks, pyro_config):
        """Test _confirm_scorch with yes response."""
        mock_input.return_value = "yes"

        result = engine_with_mocks._confirm_scorch(pyro_config)

        assert result == True
        engine_with_mocks.stdout.warn.assert_called()
        mock_input.assert_called_once_with("Are you sure about this? [Y/N]> ")

    @patch('builtins.input')
    def test_confirm_scorch_no(self, mock_input, engine_with_mocks, pyro_config):
        """Test _confirm_scorch with no response."""
        mock_input.return_value = "no"

        result = engine_with_mocks._confirm_scorch(pyro_config)

        assert result == False
        engine_with_mocks.stdout.warn.assert_called()

    @patch('builtins.input')
    def test_confirm_scorch_variations(self, mock_input, engine_with_mocks, pyro_config):
        """Test _confirm_scorch with various yes responses."""
        for response in ["y", "Y", "yes", "YES", "Yes"]:
            mock_input.reset_mock()
            mock_input.return_value = response

            result = engine_with_mocks._confirm_scorch(pyro_config)

            assert result == True

    @patch('builtins.input')
    def test_confirm_scorch_no_response(self, mock_input, engine_with_mocks, pyro_config):
        """Test _confirm_scorch with empty/whitespace response."""
        mock_input.return_value = "   "

        result = engine_with_mocks._confirm_scorch(pyro_config)

        assert result == False


class TestEdgeCases:
    """Test edge cases and error conditions."""

#   # TODO
#   def test_none_input_path(self, engine_with_mocks):
#       """Test methods with None input path."""
#       pass
#   # TODO
#   def test_snapshot_without_write_permission(self, engine_with_mocks, mock_validator):
#       """Test snapshot when cannot write to output path."""
#       pass
#   # TODO
#   def test_configure_with_invalid_config_content(self, engine_with_mocks, mock_parser):
#       """Test configure with invalid config file content."""
#       pass
#   # TODO
#   def test_scorch_with_failed_removal(self, engine_with_mocks, mock_parser, pyro_config):
#       """Test scorch when some resources fail to remove."""
#       pass
#   # TODO
#   def test_validate_with_large_number_of_discrepancies(self, engine_with_mocks, mock_parser):
#       """Test validate with many discrepancies."""
#       pass

    def test_empty_string_input_path(self, engine_with_mocks, mock_parser):
        """Test methods with empty string input path."""
        mock_parser.parse.return_value = []

        result = engine_with_mocks.configure("")

        assert result["success"] == False
        mock_parser.parse.assert_called_once_with(Path(""))

    def test_non_existent_input_path(self, engine_with_mocks, mock_parser):
        """Test methods with non-existent path."""
        mock_parser.parse.return_value = []  # Simulate no files found

        result = engine_with_mocks.configure("/non/existent/path")

        assert result["success"] == False
        engine_with_mocks.stdout.err.assert_called_once()


class TestIntegrationScenarios:
    """Test integration-like scenarios."""

#   # TODO
#   def test_full_workflow_simulation(self, mock_reporter_cls, mock_validator_cls,
#                                   mock_flow_cls, mock_sketch_cls, mock_parser_cls,
#                                   mock_stdout_cls):
#       pass
#   # TODO
#   def test_chained_operations(self, engine_with_mocks, mock_parser, mock_validator):
#       """Test a sequence of operations."""
#       pass


class TestOperationResultEnum:
    """Test the OperationResult enumeration."""

    def test_enum_values(self):
        """Test that OperationResult has correct values."""
        assert OperationResult.SUCCESS.value == "success"
        assert OperationResult.FAILURE.value == "failure"
        assert OperationResult.CANCELLED.value == "cancelled"
        assert OperationResult.SKIPPED.value == "skipped"

    def test_enum_membership(self):
        """Test enum membership."""
        assert isinstance(OperationResult.SUCCESS, OperationResult)
        assert OperationResult.SUCCESS in OperationResult


if __name__ == "__main__":
    # This allows running the test file directly
    pytest.main([__file__, "-v"])
