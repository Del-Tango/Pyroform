"""
FlowCTRL Engine Integration for Pyroform
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional

from flow_ctrl.src.core.engine import FlowEngine

from .models import ActionType


class PyroflowEngine:
    """
    Wrapper around FlowEngine for Pyroform operations
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize PyroflowEngine

        Args:
            config_path: Optional path to FlowCTRL config file
        """
        self.config = self._load_config(config_path)
        self.flow_engine = FlowEngine(self.config)
        self._current_sketch: Optional[Dict[str, Any]] = None

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
                with open(config_path, 'r') as f:
                    if config_path.endswith('.json'):
                        return json.load(f)
                    else:
                        import yaml
                        return yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading config from {config_path}: {e}")
                print("Using default configuration")

        return self._default_config()

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
            # Save sketch to temporary file
            temp_sketch_path = Path("/tmp/pyroform_sketch.json")
            with open(temp_sketch_path, 'w') as f:
                json.dump(sketch, f)

            # Load procedure into FlowEngine
            if not self.flow_engine.load_procedure(str(temp_sketch_path)):
                print(f"Failed to load procedure from {temp_sketch_path}")
                return False

            self._current_sketch = sketch

            # Start procedure execution
            result = self.flow_engine.start_procedure()

            # Clean up temporary file
            try:
                temp_sketch_path.unlink()
            except OSError:
                pass  # Ignore cleanup errors

            return result.success if hasattr(result, 'success') else False

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
            return result.success if hasattr(result, 'success') else False
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
            return result.success if hasattr(result, 'success') else False
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
            return result.success if hasattr(result, 'success') else False
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
            return result.success if hasattr(result, 'success') else False
        except Exception as e:
            print(f"Error purging data: {e}")
            return False

    def _default_config(self) -> Dict[str, Any]:
        """
        Generate default FlowCTRL configuration for Pyroform

        Returns:
            Default configuration dictionary
        """
        return {
            "state_file": "/tmp/pyroform_state.json",
            "logging": {
                "level": "INFO",
                "file": "/var/log/pyroform_flowctrl.log"
            },
            "execution": {
                "max_retries": 3,
                "timeout": 300,
                "continue_on_failure": False
            },
            "reporting": {
                "generate_reports": True,
                "report_dir": "/var/log/pyroform/reports"
            }
        }

    @property
    def current_sketch(self) -> Optional[Dict[str, Any]]:
        """Get the currently loaded sketch"""
        return self._current_sketch

# CODE DUMP

#   """
#   FlowCTRL Engine Integration for Pyroform
#   """
#   import json
#   from pathlib import Path
#   from typing import Dict, Any, Optional

#   from flow_ctrl.src.core.engine import FlowEngine

#   from .models import ActionType


#   class PyroflowEngine:
#       """
#       Wrapper around FlowEngine for Pyroform operations
#       """

#       def __init__(self, config_path: Optional[str] = None):
#           """
#           Initialize PyroflowEngine

#           Args:
#               config_path: Optional path to FlowCTRL config file
#           """
#           self.flow_engine = FlowEngine(config_path or self._default_config())
#           self._current_sketch: Optional[Dict[str, Any]] = None

#       def execute_sketch(self, sketch: Dict[str, Any], action: ActionType) -> bool:
#           """
#           Execute generated sketch through FlowCTRL

#           Args:
#               sketch: FlowCTRL sketch dictionary
#               action: Type of action being executed

#           Returns:
#               True if execution was successful, False otherwise
#           """
#           try:
#               # Save sketch to temporary file
#               temp_sketch_path = Path("/tmp/pyroform_sketch.json")
#               with open(temp_sketch_path, 'w') as f:
#                   json.dump(sketch, f)

#               # Load procedure into FlowEngine
#               if not self.flow_engine.load_procedure(str(temp_sketch_path)):
#                   print(f"Failed to load procedure from {temp_sketch_path}")
#                   return False

#               self._current_sketch = sketch

#               # Start procedure execution
#               result = self.flow_engine.start_procedure()

#               # Clean up temporary file
#               try:
#                   temp_sketch_path.unlink()
#               except OSError:
#                   pass  # Ignore cleanup errors

#               return result.success if hasattr(result, 'success') else False

#           except Exception as e:
#               print(f"Error executing sketch for {action.value}: {e}")
#               return False

#       def pause_execution(self) -> bool:
#           """
#           Pause current execution

#           Returns:
#               True if successful, False otherwise
#           """
#           try:
#               result = self.flow_engine.pause_procedure()
#               return result.success if hasattr(result, 'success') else False
#           except Exception as e:
#               print(f"Error pausing execution: {e}")
#               return False

#       def resume_execution(self) -> bool:
#           """
#           Resume paused execution

#           Returns:
#               True if successful, False otherwise
#           """
#           try:
#               result = self.flow_engine.resume_procedure()
#               return result.success if hasattr(result, 'success') else False
#           except Exception as e:
#               print(f"Error resuming execution: {e}")
#               return False

#       def stop_execution(self) -> bool:
#           """
#           Stop current execution

#           Returns:
#               True if successful, False otherwise
#           """
#           try:
#               result = self.flow_engine.stop_procedure()
#               return result.success if hasattr(result, 'success') else False
#           except Exception as e:
#               print(f"Error stopping execution: {e}")
#               return False

#       def send_command(self, command: str) -> bool:
#           """
#           Send external command to running FlowCTRL process

#           Args:
#               command: Command string to send

#           Returns:
#               True if successful, False otherwise
#           """
#           try:
#               return self.flow_engine.send_external_command(command)
#           except Exception as e:
#               print(f"Error sending command '{command}': {e}")
#               return False

#       def purge_data(self) -> bool:
#           """
#           Purge all state and report data

#           Returns:
#               True if successful, False otherwise
#           """
#           try:
#               result = self.flow_engine.purge_data()
#               return result.success if hasattr(result, 'success') else False
#           except Exception as e:
#               print(f"Error purging data: {e}")
#               return False

#       def _default_config(self) -> Dict[str, Any]:
#           """
#           Generate default FlowCTRL configuration for Pyroform

#           Returns:
#               Default configuration dictionary
#           """
#           return {
#               "logging": {
#                   "level": "INFO",
#                   "file": "/var/log/pyroform_flowctrl.log"
#               },
#               "execution": {
#                   "max_retries": 3,
#                   "timeout": 300,
#                   "continue_on_failure": False
#               },
#               "reporting": {
#                   "generate_reports": True,
#                   "report_dir": "/var/log/pyroform/reports"
#               }
#           }

#       @property
#       def current_sketch(self) -> Optional[Dict[str, Any]]:
#           """Get the currently loaded sketch"""
#           return self._current_sketch

# CODE DUMP

#   # pyroform/src/flow_engine.py
#   from flow_ctrl.src.core.engine import FlowEngine
#   from .models import ActionType

#   class PyroflowEngine:
#       def __init__(self, config_path: str = None):
#           self.flow_engine = FlowEngine(config_path or self._default_config())

#       def execute_sketch(self, sketch: Dict, action: ActionType) -> bool:
#           """Execute generated sketch through FlowCTRL"""
#           pass
