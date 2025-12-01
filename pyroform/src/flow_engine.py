"""
FlowCTRL Engine Integration for Pyroform
"""

import json
import pysnooper

from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock

from flow_ctrl.src.core.engine import FlowEngine
from flow_ctrl.src.config.settings import FlowConfig

from .models import ActionType
from .logging import STDOUTMsg


class PyroflowEngine:
    """
    Wrapper around FlowEngine for Pyroform operations
    """

    stdout: STDOUTMsg

    #@pysnooper.snoop()
    def __init__(self, *args, stdout=None, config_path: Optional[str] = None, **kwargs):
        """
        Initialize PyroflowEngine

        Args:
            config_path: Optional path to FlowCTRL config file
        """
        self.config = self._load_config(config_path)
        self.stdout = stdout or STDOUTMsg(
            debug_mode=True,
            timestamp=True,
        )
        # Try to create a real FlowEngine with proper config object
        flow_config = self._create_flow_config()
        self.stdout.debug(f'flow_config - {flow_config}')
        self.stdout.debug(f'flow_config.__dict__ - {flow_config.__dict__}')

        self.flow_engine = FlowEngine(flow_config)
        self.stdout.debug(f'flow_engine - {self.flow_engine}')

        self._current_sketch: Optional[Dict[str, Any]] = None

    #@pysnooper.snoop()
    def _create_flow_config(self):
        """
        Create a FlowEngine compatible config object

        Returns:
            Config object with required attributes
        """
        self.stdout.debug(f'Config {self.config}')
        return FlowConfig(**self.config)


    #@pysnooper.snoop()
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults

        Args:
            config_path: Optional path to config file

        Returns:
            Configuration dictionary
        """
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, "r") as f:
                    if config_path.endswith(".json"):
                        return json.load(f)
                    else:
                        import yaml

                        return yaml.safe_load(f)
            except Exception as e:
                self.stdout.err(f"Error loading config from {config_path}: {e}")
                self.stdout.info("Using default configuration")

        return self._default_config()

    #@pysnooper.snoop()
    def execute_sketch(self, sketch: Dict[str, Any], action: ActionType) -> bool:
        """
        Execute generated sketch through FlowCTRL

        Args:
            sketch: FlowCTRL sketch dictionary
            action: Type of action being executed

        Returns:
            True if execution was successful, False otherwise
        """
        try:

            # TODO - Remove,duplication
#           self.stdout.info('FlowCTRL Sketch - %s' % str(json.dumps(sketch, indent=4)))

            # TODO - Set --output path from config / cli args
            # Save sketch to temporary file
            temp_sketch_path = Path("pyroflow.sketch.json")

            self.stdout.debug(f'temp_sketch_path - {temp_sketch_path}')

            with open(temp_sketch_path, "w") as f:
                json.dump(sketch, f, indent=4)

            # Purging previous session data
            self.flow_engine.purge_data()

            # Load procedure into FlowEngine
            if not self.flow_engine.load_procedure(str(temp_sketch_path)):
                self.stdout.err(f"Failed to load procedure from {temp_sketch_path}")
                return False

            self._current_sketch = sketch

            # Start procedure execution
            result = self.flow_engine.start_procedure()

            # TODO - Make configurable from CLI args
#           # Clean up temporary file
#           try:
#               temp_sketch_path.unlink()
#           except OSError:
#               pass  # Ignore cleanup errors

            return result.success if hasattr(result, "success") else False

        except Exception as e:
            print(f"Error executing sketch for {action.value}: {e}")
            return False

    def pause_execution(self) -> bool:
        """
        Pause current execution

        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.flow_engine.pause_procedure()
            return result.success if hasattr(result, "success") else False
        except Exception as e:
            print(f"Error pausing execution: {e}")
            return False

    def resume_execution(self) -> bool:
        """
        Resume paused execution

        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.flow_engine.resume_procedure()
            return result.success if hasattr(result, "success") else False
        except Exception as e:
            print(f"Error resuming execution: {e}")
            return False

    def stop_execution(self) -> bool:
        """
        Stop current execution

        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.flow_engine.stop_procedure()
            return result.success if hasattr(result, "success") else False
        except Exception as e:
            print(f"Error stopping execution: {e}")
            return False

    def send_command(self, command: str) -> bool:
        """
        Send external command to running FlowCTRL process

        Args:
            command: Command string to send

        Returns:
            True if successful, False otherwise
        """
        try:
            return self.flow_engine.send_external_command(command)
        except Exception as e:
            print(f"Error sending command '{command}': {e}")
            return False

    def purge_data(self) -> bool:
        """
        Purge all state and report data

        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.flow_engine.purge_data()
            return result.success if hasattr(result, "success") else False
        except Exception as e:
            print(f"Error purging data: {e}")
            return False

    #@pysnooper.snoop()
    def _default_config(self) -> Dict[str, Any]:
        """
        Generate default FlowCTRL configuration for Pyroform

        Returns:
            Default configuration dictionary
        """
        flow_ctrl_config = {
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
        return flow_ctrl_config


    @property
    def current_sketch(self) -> Optional[Dict[str, Any]]:
        """Get the currently loaded sketch"""
        return self._current_sketch


# CODE DUMP

