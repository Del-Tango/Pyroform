"""
PyroflowEngine Test Suite

Unit tests for the PyroflowEngine class.
"""

import pytest
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open, call
from typing import Dict, Any, Optional

from pyroform.src.flow_engine import PyroflowEngine
from pyroform.src.models import ActionType
from pyroform.src.logging import STDOUTMsg


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
def mock_flow_engine():
    """Mock FlowEngine instance."""
    mock = Mock()
    mock.load_procedure = Mock(return_value=True)
    mock.purge_data = Mock()
    mock.start_procedure = Mock()
    mock.pause_procedure = Mock()
    mock.resume_procedure = Mock()
    mock.stop_procedure = Mock()
    mock.send_external_command = Mock(return_value=True)
    return mock


@pytest.fixture
def mock_flow_config():
    """Mock FlowConfig class."""
    mock = Mock()
    mock.return_value = Mock()
    return mock


@pytest.fixture
def sample_sketch():
    """Create a sample FlowCTRL sketch."""
    return {
        "name": "Test Sketch",
        "steps": [
            {
                "name": "Test Step",
                "cmd": "echo 'test'"
            }
        ]
    }


@pytest.fixture
def default_config():
    """Get default configuration."""
    return {
        "project_dir": str(Path(__file__).parent.parent.parent),
        "log_dir": "log/pyroflow",
        "conf_dir": "conf/pyroflow",
        "state_file": ".pyroflow.state",
        "report_file": "pyroflow.report",
        "log_file": "pyroflow.log",
        "log_name": "PyroFlowCTRL",
        "silence": False,
        "debug": True,
        "log_format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        "timestamp_format": "%Y-%m-%d %H:%M:%S"
    }


class TestPyroflowEngineInitialization:
    """Test PyroflowEngine initialization."""

    def test_init_defaults(self, mock_stdout, mock_flow_config):
        """Test initialization with default parameters."""
        with patch('pyroform.src.flow_engine.STDOUTMsg', return_value=mock_stdout), \
             patch('pyroform.src.flow_engine.FlowConfig', mock_flow_config), \
             patch('pyroform.src.flow_engine.FlowEngine') as mock_flow_engine_cls:

            mock_flow_engine_instance = Mock()
            mock_flow_engine_cls.return_value = mock_flow_engine_instance

            engine = PyroflowEngine()

            # Verify STDOUTMsg was created with correct defaults
            assert engine.stdout == mock_stdout
            assert engine.config is not None

            # Verify FlowEngine was created
            mock_flow_engine_cls.assert_called_once()

            # Verify default attributes
            assert engine._current_sketch is None

            # Verify debug messages
            mock_stdout.debug.assert_called()

    def test_init_with_stdout(self, mock_stdout, mock_flow_config):
        """Test initialization with custom stdout."""
        with patch('pyroform.src.flow_engine.FlowConfig', mock_flow_config), \
             patch('pyroform.src.flow_engine.FlowEngine') as mock_flow_engine_cls:

            mock_flow_engine_cls.return_value = Mock()

            engine = PyroflowEngine(stdout=mock_stdout)

            assert engine.stdout == mock_stdout

    def test_init_with_config_path(self, mock_stdout, tmp_path):
        """Test initialization with config file path."""
        # Create a config file
        config_data = {
            "log_dir": "/custom/log/path",
            "debug": False,
            "silence": True
        }

        config_file = tmp_path / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        with patch('pyroform.src.flow_engine.STDOUTMsg', return_value=mock_stdout), \
             patch('pyroform.src.flow_engine.FlowConfig') as mock_flow_config_cls, \
             patch('pyroform.src.flow_engine.FlowEngine') as mock_flow_engine_cls:

            mock_flow_config_cls.return_value = Mock()
            mock_flow_engine_cls.return_value = Mock()

            engine = PyroflowEngine(config_path=str(config_file))

            # Config should be loaded from file
            # Note: _load_config is mocked by patch, but we can verify it was called
            # with the correct path

    def test_init_with_nonexistent_config_path(self, mock_stdout):
        """Test initialization with non-existent config file."""
        with patch('pyroform.src.flow_engine.STDOUTMsg', return_value=mock_stdout), \
             patch('pyroform.src.flow_engine.FlowConfig') as mock_flow_config_cls, \
             patch('pyroform.src.flow_engine.FlowEngine') as mock_flow_engine_cls:

            mock_flow_config_cls.return_value = Mock()
            mock_flow_engine_cls.return_value = Mock()

            # Should not raise exception
            engine = PyroflowEngine(config_path="/nonexistent/path/config.json")

            # Should use default config
            assert engine.config is not None

    def test_init_with_yaml_config(self, mock_stdout, tmp_path):
        """Test initialization with YAML config file."""
        config_data = {
            "log_dir": "/yaml/config/path",
            "debug": False
        }

        config_file = tmp_path / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        with patch('pyroform.src.flow_engine.STDOUTMsg', return_value=mock_stdout), \
             patch('pyroform.src.flow_engine.FlowConfig') as mock_flow_config_cls, \
             patch('pyroform.src.flow_engine.FlowEngine') as mock_flow_engine_cls:

            mock_flow_config_cls.return_value = Mock()
            mock_flow_engine_cls.return_value = Mock()

            engine = PyroflowEngine(config_path=str(config_file))

            # Should load YAML config
            # (actual loading is tested in _load_config tests)

    def test_init_flow_config_creation(self, mock_stdout):
        """Test that FlowConfig is created with correct parameters."""
        with patch('pyroform.src.flow_engine.STDOUTMsg', return_value=mock_stdout), \
             patch('pyroform.src.flow_engine.FlowConfig') as mock_flow_config_cls, \
             patch('pyroform.src.flow_engine.FlowEngine') as mock_flow_engine_cls:

            mock_flow_config_instance = Mock()
            mock_flow_config_cls.return_value = mock_flow_config_instance
            mock_flow_engine_cls.return_value = Mock()

            engine = PyroflowEngine()

            # FlowConfig should be created with config dict
            mock_flow_config_cls.assert_called_once_with(**engine.config)

            # Debug should show config
            mock_stdout.debug.assert_any_call(f'Config {engine.config}')

    def test_init_flow_engine_creation(self, mock_stdout):
        """Test that FlowEngine is created with FlowConfig."""
        with patch('pyroform.src.flow_engine.STDOUTMsg', return_value=mock_stdout), \
             patch('pyroform.src.flow_engine.FlowConfig') as mock_flow_config_cls, \
             patch('pyroform.src.flow_engine.FlowEngine') as mock_flow_engine_cls:

            mock_flow_config_instance = Mock()
            mock_flow_config_cls.return_value = mock_flow_config_instance
            mock_flow_engine_instance = Mock()
            mock_flow_engine_cls.return_value = mock_flow_engine_instance

            engine = PyroflowEngine()

            # FlowEngine should be created with FlowConfig
            mock_flow_engine_cls.assert_called_once_with(mock_flow_config_instance)

            # Engine should have flow_engine attribute
            assert engine.flow_engine == mock_flow_engine_instance

            # Debug should show engine
            mock_stdout.debug.assert_any_call(f'flow_engine - {mock_flow_engine_instance}')


class TestLoadConfig:
    """Test the _load_config method."""

#   # TODO
#   def test_load_config_unsupported_format(self, tmp_path):
#       """Test loading config with unsupported file format."""

    def test_load_config_json_file(self, tmp_path):
        """Test loading config from JSON file."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = Mock()

        # Create JSON config file
        config_data = {
            "log_dir": "/custom/json/path",
            "debug": False,
            "custom_field": "value"
        }

        config_file = tmp_path / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        result = engine._load_config(str(config_file))

        assert result["log_dir"] == "/custom/json/path"
        assert result["debug"] == False
        assert result["custom_field"] == "value"

    def test_load_config_yaml_file(self, tmp_path):
        """Test loading config from YAML file."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = Mock()

        # Create YAML config file
        config_data = {
            "log_dir": "/custom/yaml/path",
            "debug": True,
            "nested": {
                "field": "value"
            }
        }

        config_file = tmp_path / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        result = engine._load_config(str(config_file))

        assert result["log_dir"] == "/custom/yaml/path"
        assert result["debug"] == True
        assert result["nested"]["field"] == "value"

    def test_load_config_yml_extension(self, tmp_path):
        """Test loading config from .yml file."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = Mock()

        config_data = {"log_dir": "/yml/path"}

        config_file = tmp_path / "config.yml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        result = engine._load_config(str(config_file))

        assert result["log_dir"] == "/yml/path"

    def test_load_config_nonexistent_file(self):
        """Test loading config from non-existent file."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = Mock()

        result = engine._load_config("/nonexistent/path/config.json")

        # Should return default config
        assert "project_dir" in result
        assert "log_dir" in result

    def test_load_config_none_path(self):
        """Test loading config with None path."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = Mock()

        result = engine._load_config(None)

        # Should return default config
        assert "project_dir" in result

    def test_load_config_json_decode_error(self, tmp_path):
        """Test handling of JSON decode error."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = Mock()

        # Create invalid JSON file
        config_file = tmp_path / "invalid.json"
        with open(config_file, 'w') as f:
            f.write("{ invalid json")

        result = engine._load_config(str(config_file))

        # Should fall back to default config
        assert "project_dir" in result
        engine.stdout.err.assert_called_once()
        engine.stdout.info.assert_called_with("Using default configuration")

    def test_load_config_yaml_error(self, tmp_path):
        """Test handling of YAML parse error."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = Mock()

        # Create invalid YAML file
        config_file = tmp_path / "invalid.yaml"
        with open(config_file, 'w') as f:
            f.write("invalid: [unclosed list")

        result = engine._load_config(str(config_file))

        # Should fall back to default config
        assert "project_dir" in result
        engine.stdout.err.assert_called_once()

    def test_load_config_empty_file(self, tmp_path):
        """Test loading empty config file."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = Mock()

        config_file = tmp_path / "empty.json"
        config_file.touch()  # Create empty file

        result = engine._load_config(str(config_file))

        # Should return default config
        assert "project_dir" in result


class TestDefaultConfig:
    """Test the _default_config method."""

    def test_default_config_structure(self):
        """Test that default config has expected structure."""
        engine = PyroflowEngine.__new__(PyroflowEngine)

        config = engine._default_config()

        # Check required fields
        assert "project_dir" in config
        assert "log_dir" in config
        assert "conf_dir" in config
        assert "state_file" in config
        assert "report_file" in config
        assert "log_file" in config
        assert "log_name" in config
        assert "silence" in config
        assert "debug" in config
        assert "log_format" in config
        assert "timestamp_format" in config

        # Check values
        assert config["log_name"] == "PyroFlowCTRL"
        assert config["debug"] == True
        assert config["silence"] == False
        assert "%(asctime)s" in config["log_format"]
        assert "%Y-%m-%d" in config["timestamp_format"]

    def test_default_config_paths(self):
        """Test that default config paths are valid strings."""
        engine = PyroflowEngine.__new__(PyroflowEngine)

        config = engine._default_config()

        # All paths should be strings
        assert isinstance(config["project_dir"], str)
        assert isinstance(config["log_dir"], str)
        assert isinstance(config["conf_dir"], str)
        assert isinstance(config["state_file"], str)
        assert isinstance(config["report_file"], str)
        assert isinstance(config["log_file"], str)

    def test_default_config_immutable(self):
        """Test that modifying returned config doesn't affect future calls."""
        engine = PyroflowEngine.__new__(PyroflowEngine)

        config1 = engine._default_config()
        config1["custom_field"] = "value"

        config2 = engine._default_config()

        # config2 should not have the custom field
        assert "custom_field" not in config2
        assert config1["custom_field"] == "value"


class TestCreateFlowConfig:
    """Test the _create_flow_config method."""

#   # TODO
#   def test_create_flow_config(self, mock_stdout):
#       """Test FlowConfig creation."""

    def test_create_flow_config_empty(self, mock_stdout):
        """Test FlowConfig creation with empty config."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.config = {}

        with patch('pyroform.src.flow_engine.FlowConfig') as mock_flow_config_cls:
            mock_flow_config_instance = Mock()
            mock_flow_config_cls.return_value = mock_flow_config_instance

            result = engine._create_flow_config()

            # Should call FlowConfig with empty kwargs
            mock_flow_config_cls.assert_called_once_with()
            assert result == mock_flow_config_instance


class TestExecuteSketch:
    """Test the execute_sketch method."""

    def test_execute_sketch_success(self, mock_stdout, mock_flow_engine, sample_sketch):
        """Test successful sketch execution."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine
        engine.config = {}
        engine._current_sketch = None

        # Mock successful execution
        mock_result = Mock()
        mock_result.success = True
        mock_flow_engine.start_procedure.return_value = mock_result

        with patch('builtins.open', mock_open()) as mock_file, \
             patch('json.dump') as mock_json_dump, \
             patch('pyroform.src.flow_engine.Path') as mock_path_cls:

            mock_path = Mock()
            mock_path.__str__ = lambda x: "pyroflow.sketch.json"
            mock_path_cls.return_value = mock_path

            result = engine.execute_sketch(sample_sketch, ActionType.CONFIGURE)

            # Should save sketch to file
            mock_file.assert_called_with(mock_path, "w")
            mock_json_dump.assert_called_once_with(sample_sketch, mock_file(), indent=4)

            # Should purge data
            mock_flow_engine.purge_data.assert_called_once()

            # Should load procedure
            mock_flow_engine.load_procedure.assert_called_once_with("pyroflow.sketch.json")

            # Should start procedure
            mock_flow_engine.start_procedure.assert_called_once()

            # Should return success
            assert result == True

            # Should update current sketch
            assert engine._current_sketch == sample_sketch

            # Should log sketch
            mock_stdout.info.assert_called_once()
            info_call = mock_stdout.info.call_args[0][0]
            assert "FlowCTRL Sketch" in info_call

            # Should debug temp path
            mock_stdout.debug.assert_any_call(f'temp_sketch_path - {mock_path}')

    def test_execute_sketch_load_failure(self, mock_stdout, mock_flow_engine, sample_sketch):
        """Test sketch execution when loading fails."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        # Mock load failure
        mock_flow_engine.load_procedure.return_value = False

        with patch('builtins.open', mock_open()), \
             patch('json.dump'), \
             patch('pyroform.src.flow_engine.Path'):

            result = engine.execute_sketch(sample_sketch, ActionType.CONFIGURE)

            # Should return False
            assert result == False

            # Should log error
            mock_stdout.err.assert_called_once()
            err_call = mock_stdout.err.call_args[0][0]
            assert "Failed to load procedure" in err_call

    def test_execute_sketch_without_success_attribute(self, mock_stdout, mock_flow_engine, sample_sketch):
        """Test sketch execution when result doesn't have success attribute."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        # Mock result without success attribute
        mock_result = Mock()
        del mock_result.success  # Remove success attribute
        mock_flow_engine.start_procedure.return_value = mock_result

        with patch('builtins.open', mock_open()), \
             patch('json.dump'), \
             patch('pyroform.src.flow_engine.Path'):

            result = engine.execute_sketch(sample_sketch, ActionType.CONFIGURE)

            # Should return False when success attribute is missing
            assert result == False

    def test_execute_sketch_exception(self, mock_stdout, mock_flow_engine, sample_sketch):
        """Test sketch execution when exception occurs."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        # Mock exception during execution
        mock_flow_engine.start_procedure.side_effect = Exception("Test error")

        with patch('builtins.open', mock_open()), \
             patch('json.dump'), \
             patch('pyroform.src.flow_engine.Path'):

            result = engine.execute_sketch(sample_sketch, ActionType.CONFIGURE)

            # Should return False
            assert result == False

            # Should print error (not through stdout)
            # The actual code uses print() for exceptions

    def test_execute_sketch_different_actions(self, mock_stdout, mock_flow_engine, sample_sketch):
        """Test sketch execution with different action types."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_result = Mock()
        mock_result.success = True
        mock_flow_engine.start_procedure.return_value = mock_result

        with patch('builtins.open', mock_open()), \
             patch('json.dump'), \
             patch('pyroform.src.flow_engine.Path'):

            # Test all action types
            for action in [ActionType.CONFIGURE, ActionType.MOUNT, ActionType.SCORCH]:
                result = engine.execute_sketch(sample_sketch, action)
                assert result == True

    def test_execute_sketch_temp_file_cleanup_commented(self, mock_stdout, mock_flow_engine, sample_sketch):
        """Test that temp file cleanup is commented out in code."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_result = Mock()
        mock_result.success = True
        mock_flow_engine.start_procedure.return_value = mock_result

        mock_path = Mock()
        mock_path.unlink = Mock()

        with patch('builtins.open', mock_open()), \
             patch('json.dump'), \
             patch('pyroform.src.flow_engine.Path', return_value=mock_path):

            result = engine.execute_sketch(sample_sketch, ActionType.CONFIGURE)

            # Temp file cleanup is commented out in the actual code
            # So unlink should not be called
            mock_path.unlink.assert_not_called()

    def test_execute_sketch_empty_sketch(self, mock_stdout, mock_flow_engine):
        """Test sketch execution with empty sketch."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_result = Mock()
        mock_result.success = True
        mock_flow_engine.start_procedure.return_value = mock_result

        empty_sketch = {}

        with patch('builtins.open', mock_open()), \
             patch('json.dump'), \
             patch('pyroform.src.flow_engine.Path'):

            result = engine.execute_sketch(empty_sketch, ActionType.CONFIGURE)

            # Should still execute
            assert result == True
            mock_flow_engine.load_procedure.assert_called_once()


class TestControlMethods:
    """Test pause, resume, and stop methods."""

    def test_pause_execution_success(self, mock_stdout, mock_flow_engine):
        """Test successful pause execution."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_result = Mock()
        mock_result.success = True
        mock_flow_engine.pause_procedure.return_value = mock_result

        result = engine.pause_execution()

        mock_flow_engine.pause_procedure.assert_called_once()
        assert result == True

    def test_pause_execution_failure(self, mock_stdout, mock_flow_engine):
        """Test pause execution failure."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_result = Mock()
        mock_result.success = False
        mock_flow_engine.pause_procedure.return_value = mock_result

        result = engine.pause_execution()

        assert result == False

    def test_pause_execution_exception(self, mock_stdout, mock_flow_engine):
        """Test pause execution with exception."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_flow_engine.pause_procedure.side_effect = Exception("Pause error")

        result = engine.pause_execution()

        assert result == False
        # Should print error (code uses print, not stdout)

    def test_resume_execution_success(self, mock_stdout, mock_flow_engine):
        """Test successful resume execution."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_result = Mock()
        mock_result.success = True
        mock_flow_engine.resume_procedure.return_value = mock_result

        result = engine.resume_execution()

        mock_flow_engine.resume_procedure.assert_called_once()
        assert result == True

    def test_stop_execution_success(self, mock_stdout, mock_flow_engine):
        """Test successful stop execution."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_result = Mock()
        mock_result.success = True
        mock_flow_engine.stop_procedure.return_value = mock_result

        result = engine.stop_execution()

        mock_flow_engine.stop_procedure.assert_called_once()
        assert result == True

    def test_control_methods_without_success_attribute(self, mock_stdout, mock_flow_engine):
        """Test control methods when result doesn't have success attribute."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        # Create result without success attribute
        mock_result = Mock()
        del mock_result.success

        mock_flow_engine.pause_procedure.return_value = mock_result
        mock_flow_engine.resume_procedure.return_value = mock_result
        mock_flow_engine.stop_procedure.return_value = mock_result

        # All should return False
        assert engine.pause_execution() == False
        assert engine.resume_execution() == False
        assert engine.stop_execution() == False


class TestSendCommand:
    """Test the send_command method."""

    def test_send_command_success(self, mock_stdout, mock_flow_engine):
        """Test successful command sending."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_flow_engine.send_external_command.return_value = True

        result = engine.send_command("test_command")

        mock_flow_engine.send_external_command.assert_called_once_with("test_command")
        assert result == True

    def test_send_command_failure(self, mock_stdout, mock_flow_engine):
        """Test failed command sending."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_flow_engine.send_external_command.return_value = False

        result = engine.send_command("test_command")

        assert result == False

    def test_send_command_exception(self, mock_stdout, mock_flow_engine):
        """Test command sending with exception."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_flow_engine.send_external_command.side_effect = Exception("Command error")

        result = engine.send_command("test_command")

        assert result == False
        # Should print error

    def test_send_command_empty(self, mock_stdout, mock_flow_engine):
        """Test sending empty command."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        result = engine.send_command("")

        mock_flow_engine.send_external_command.assert_called_once_with("")
        # Return value depends on mock


class TestPurgeData:
    """Test the purge_data method."""

    def test_purge_data_success(self, mock_stdout, mock_flow_engine):
        """Test successful data purging."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_result = Mock()
        mock_result.success = True
        mock_flow_engine.purge_data.return_value = mock_result

        result = engine.purge_data()

        mock_flow_engine.purge_data.assert_called_once()
        assert result == True

    def test_purge_data_failure(self, mock_stdout, mock_flow_engine):
        """Test failed data purging."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_result = Mock()
        mock_result.success = False
        mock_flow_engine.purge_data.return_value = mock_result

        result = engine.purge_data()

        assert result == False

    def test_purge_data_exception(self, mock_stdout, mock_flow_engine):
        """Test data purging with exception."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_flow_engine.purge_data.side_effect = Exception("Purge error")

        result = engine.purge_data()

        assert result == False
        # Should print error

    def test_purge_data_in_execute_sketch(self, mock_stdout, mock_flow_engine, sample_sketch):
        """Test that purge_data is called in execute_sketch."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_result = Mock()
        mock_result.success = True
        mock_flow_engine.start_procedure.return_value = mock_result

        with patch('builtins.open', mock_open()), \
             patch('json.dump'), \
             patch('pyroform.src.flow_engine.Path'):

            engine.execute_sketch(sample_sketch, ActionType.CONFIGURE)

            # Should call purge_data before loading procedure
            mock_flow_engine.purge_data.assert_called_once()


class TestCurrentSketchProperty:
    """Test the current_sketch property."""

#   # TODO
#   def test_current_sketch_updates_on_execute(self, mock_stdout, mock_flow_engine, sample_sketch):
#       """Test that current_sketch updates after execute_sketch."""

    def test_current_sketch_none(self, mock_stdout):
        """Test current_sketch when no sketch has been executed."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine._current_sketch = None

        assert engine.current_sketch is None

    def test_current_sketch_after_execution(self, mock_stdout, mock_flow_engine, sample_sketch):
        """Test current_sketch after sketch execution."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine
        engine._current_sketch = sample_sketch

        assert engine.current_sketch == sample_sketch

    def test_current_sketch_readonly(self, mock_stdout, mock_flow_engine, sample_sketch):
        """Test that current_sketch is read-only."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        # Set initial sketch
        engine._current_sketch = sample_sketch

        # Try to assign to property (should fail or not change underlying)
        try:
            engine.current_sketch = {"new": "sketch"}
        except AttributeError:
            pass  # Expected if property is read-only

        # Original sketch should still be there
        assert engine.current_sketch == sample_sketch


class TestIntegrationScenarios:
    """Integration tests for complete workflows."""

#   # TODO
#   def test_error_recovery_workflow(self, mock_stdout, mock_flow_engine, sample_sketch):
#       """Test workflow with error recovery."""

    def test_complete_workflow(self, mock_stdout, mock_flow_engine, sample_sketch):
        """Test a complete PyroflowEngine workflow."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        # Mock successful results
        mock_result = Mock()
        mock_result.success = True

        mock_flow_engine.start_procedure.return_value = mock_result
        mock_flow_engine.pause_procedure.return_value = mock_result
        mock_flow_engine.resume_procedure.return_value = mock_result
        mock_flow_engine.stop_procedure.return_value = mock_result
        mock_flow_engine.purge_data.return_value = mock_result
        mock_flow_engine.send_external_command.return_value = True

        with patch('builtins.open', mock_open()), \
             patch('json.dump'), \
             patch('pyroform.src.flow_engine.Path'):

            # 1. Execute a sketch
            execute_result = engine.execute_sketch(sample_sketch, ActionType.CONFIGURE)
            assert execute_result == True
            assert engine.current_sketch == sample_sketch

            # 2. Pause execution
            pause_result = engine.pause_execution()
            assert pause_result == True

            # 3. Send a command
            command_result = engine.send_command("status")
            assert command_result == True

            # 4. Resume execution
            resume_result = engine.resume_execution()
            assert resume_result == True

            # 5. Stop execution
            stop_result = engine.stop_execution()
            assert stop_result == True

            # 6. Purge data
            purge_result = engine.purge_data()
            assert purge_result == True

            # Verify all methods were called
            mock_flow_engine.load_procedure.assert_called_once()
            mock_flow_engine.start_procedure.assert_called_once()
            mock_flow_engine.pause_procedure.assert_called_once()
            mock_flow_engine.resume_procedure.assert_called_once()
            mock_flow_engine.stop_procedure.assert_called_once()
            mock_flow_engine.purge_data.assert_called()  # Called at least once
            mock_flow_engine.send_external_command.assert_called_once_with("status")

    def test_sequential_sketch_execution(self, mock_stdout, mock_flow_engine):
        """Test executing multiple sketches sequentially."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        mock_result = Mock()
        mock_result.success = True
        mock_flow_engine.start_procedure.return_value = mock_result

        with patch('builtins.open', mock_open()), \
             patch('json.dump'), \
             patch('pyroform.src.flow_engine.Path'):

            sketch1 = {"name": "Sketch 1", "steps": []}
            sketch2 = {"name": "Sketch 2", "steps": []}

            # Execute first sketch
            result1 = engine.execute_sketch(sketch1, ActionType.CONFIGURE)
            assert result1 == True
            assert engine.current_sketch == sketch1

            # Execute second sketch (should replace first)
            result2 = engine.execute_sketch(sketch2, ActionType.MOUNT)
            assert result2 == True
            assert engine.current_sketch == sketch2  # Should be sketch2 now

            # purge_data should be called twice (once per execute_sketch)
            assert mock_flow_engine.purge_data.call_count == 2


class TestErrorHandling:
    """Test error handling and edge cases."""

#   # TODO
#   def test_execute_sketch_none_sketch(self, mock_stdout, mock_flow_engine):
#       """Test executing None sketch."""
#   def test_flow_engine_not_initialized(self, mock_stdout):
#       """Test methods when flow_engine is not initialized."""
#   def test_send_command_none_flow_engine(self, mock_stdout):
#       """Test send_command when flow_engine is None."""

    def test_execute_sketch_invalid_json(self, mock_stdout, mock_flow_engine):
        """Test executing sketch that can't be serialized to JSON."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        # Sketch with unserializable content
        invalid_sketch = {
            "name": "test",
            "data": object()  # Not JSON serializable
        }

        with patch('builtins.open', mock_open()), \
             patch('json.dump') as mock_json_dump:

            mock_json_dump.side_effect = TypeError("Object not serializable")

            result = engine.execute_sketch(invalid_sketch, ActionType.CONFIGURE)

            assert result == False

    def test_execute_sketch_file_write_error(self, mock_stdout, mock_flow_engine, sample_sketch):
        """Test sketch execution when file write fails."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        with patch('builtins.open') as mock_open_func:
            mock_open_func.side_effect = IOError("Permission denied")

            result = engine.execute_sketch(sample_sketch, ActionType.CONFIGURE)

            assert result == False

    def test_methods_with_none_flow_engine_result(self, mock_stdout, mock_flow_engine):
        """Test methods when flow_engine returns None."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        # Test each method with None return value
        mock_flow_engine.start_procedure.return_value = None
        mock_flow_engine.pause_procedure.return_value = None
        mock_flow_engine.resume_procedure.return_value = None
        mock_flow_engine.stop_procedure.return_value = None
        mock_flow_engine.purge_data.return_value = None

        with patch('builtins.open', mock_open()), \
             patch('json.dump'), \
             patch('pyroform.src.flow_engine.Path'):

            # All should return False when result is None
            assert engine.execute_sketch({}, ActionType.CONFIGURE) == False
            assert engine.pause_execution() == False
            assert engine.resume_execution() == False
            assert engine.stop_execution() == False
            assert engine.purge_data() == False


class TestRealWorldScenarios:
    """Real-world usage scenario tests."""

    def test_pyroform_integration_scenario(self, mock_stdout, mock_flow_engine):
        """Test a realistic Pyroform integration scenario."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        # Mock successful operations
        mock_result = Mock()
        mock_result.success = True

        mock_flow_engine.start_procedure.return_value = mock_result
        mock_flow_engine.pause_procedure.return_value = mock_result
        mock_flow_engine.resume_procedure.return_value = mock_result
        mock_flow_engine.stop_procedure.return_value = mock_result

        with patch('builtins.open', mock_open()), \
             patch('json.dump'), \
             patch('pyroform.src.flow_engine.Path'):

            # Simulate a configuration sketch
            config_sketch = {
                "name": "Configure System",
                "Users": [
                    {
                        "name": "Create user 'webapp'",
                        "cmd": "useradd -m webapp"
                    }
                ],
                "Groups": [
                    {
                        "name": "Create group 'www-data'",
                        "cmd": "groupadd www-data"
                    }
                ]
            }

            # 1. Configure system
            config_result = engine.execute_sketch(config_sketch, ActionType.CONFIGURE)
            assert config_result == True

            # 2. Pause to inspect
            pause_result = engine.pause_execution()
            assert pause_result == True

            # 3. Check status
            status_result = engine.send_command("status")
            assert status_result == True

            # 4. Resume
            resume_result = engine.resume_execution()
            assert resume_result == True

            # 5. Stop when done
            stop_result = engine.stop_execution()
            assert stop_result == True

            # Simulate a mount sketch
            mount_sketch = {
                "name": "Mount Devices",
                "Devices": [
                    {
                        "name": "Mount /dev/sdb1",
                        "cmd": "mount /dev/sdb1 /mnt/data"
                    }
                ]
            }

            # 6. Mount devices (new sketch)
            mount_result = engine.execute_sketch(mount_sketch, ActionType.MOUNT)
            assert mount_result == True

            # Current sketch should be mount sketch
            assert engine.current_sketch == mount_sketch

    def test_error_scenario_with_recovery(self, mock_stdout, mock_flow_engine):
        """Test error scenario with recovery steps."""
        engine = PyroflowEngine.__new__(PyroflowEngine)
        engine.stdout = mock_stdout
        engine.flow_engine = mock_flow_engine

        with patch('builtins.open', mock_open()), \
             patch('json.dump'), \
             patch('pyroform.src.flow_engine.Path'):

            # First attempt fails
            mock_flow_engine.load_procedure.return_value = False

            sketch = {"name": "Failed Sketch"}
            result1 = engine.execute_sketch(sketch, ActionType.CONFIGURE)
            assert result1 == False
            mock_stdout.err.assert_called()  # Should log error

            # Reset mock
            mock_stdout.err.reset_mock()

            # Second attempt succeeds
            mock_flow_engine.load_procedure.return_value = True
            mock_result = Mock()
            mock_result.success = True
            mock_flow_engine.start_procedure.return_value = mock_result

            result2 = engine.execute_sketch(sketch, ActionType.CONFIGURE)
            assert result2 == True

            # During successful execution, error should not be logged
            mock_stdout.err.assert_not_called()

    def test_configuration_loading_scenarios(self, mock_stdout):
        """Test various configuration loading scenarios."""
        # Test 1: Default config
        with patch('pyroform.src.flow_engine.STDOUTMsg', return_value=mock_stdout), \
             patch('pyroform.src.flow_engine.FlowConfig') as mock_flow_config_cls, \
             patch('pyroform.src.flow_engine.FlowEngine') as mock_flow_engine_cls:

            mock_flow_config_cls.return_value = Mock()
            mock_flow_engine_cls.return_value = Mock()

            engine1 = PyroflowEngine()
            assert "project_dir" in engine1.config
            assert engine1.config["debug"] == True

        # Test 2: Config from JSON file
        with patch('pyroform.src.flow_engine.STDOUTMsg', return_value=mock_stdout), \
             patch('pyroform.src.flow_engine.FlowConfig') as mock_flow_config_cls, \
             patch('pyroform.src.flow_engine.FlowEngine') as mock_flow_engine_cls, \
             patch('pyroform.src.flow_engine.Path.exists', return_value=True):

            mock_flow_config_cls.return_value = Mock()
            mock_flow_engine_cls.return_value = Mock()

            json_config = '{"debug": false, "silence": true}'
            with patch('builtins.open', mock_open(read_data=json_config)):
                engine2 = PyroflowEngine(config_path="/test/config.json")
                # The mock will return our JSON data


if __name__ == "__main__":
    # This allows running the test file directly
    pytest.main([__file__, "-v", "--tb=short"])
