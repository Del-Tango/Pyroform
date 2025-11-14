"""
Main Pyroform Engine Library Class
"""

import yaml
import json

import pysnooper

from pathlib import Path
from typing import Dict, Any, Optional
# List
# from datetime import datetime

from .models import ActionType
from .parser import PyroParser
from .sketch_generator import SketchGenerator
from .flow_engine import PyroflowEngine
from .validator import SystemValidator, ValidationResult
from .scorch_engine import ScorchEngine, ScorchResult
from .reporter import ReportGenerator

from .logging import STDOUTMsg


class PyroformEngine:
    """
    Internal engine that coordinates all Pyroform operations
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize PyroformEngine

        Args:
            config: Configuration dictionary
        """
        self.config = config or self._default_config()
        self.stdout = STDOUTMsg(
            debug_mode=self.config['debug'],
            timestamp=self.config['log_timestamp'] or self.config['debug'],
        )

        self.parser = PyroParser(stdout=self.stdout)
        self.sketch_generator = SketchGenerator(stdout=self.stdout)

        self.flow_engine = PyroflowEngine(stdout=self.stdout)

        # Use mocked flow engine to avoid FlowCTRL dependency issues
        # self._create_mock_flow_engine(stdout=self.stdout)

        self.validator = SystemValidator()
        self.reporter = ReportGenerator()

    # TODO - Make verbose logging
    @pysnooper.snoop()
    def configure(self, input_path: str, **kwargs) -> bool:
        """
        Execute configure action

        Args:
            input_path: Path to Pyro file or directory
            **kwargs: Additional arguments

        Returns:
            True if successful, False otherwise
        """
        try:
            configs = self.parser.parse(Path(input_path))
            self.stdout.debug(f'Configs ({configs})')
            if not configs:
                self.stdout.err('No valid Pyro state files found at specified location! Details: {input_path}')
                return False

            for config in configs:
                self.stdout.debug(f'Config {config}')
                sketch = self.sketch_generator.generate_configure_sketch(config)
                self.stdout.debug(f'Sketch {sketch}')
                success = self.flow_engine.execute_sketch(sketch, ActionType.CONFIGURE)
                self.stdout.debug(f'Success {success}')
                if not success:
                    return False

            return True
        except Exception as e:
            print(f"Configure action failed: {e}")
            return False

    def scorch(self, input_path: str, **kwargs) -> ScorchResult:
        """
        Execute scorch action

        Args:
            input_path: Path to Pyro file or directory
            **kwargs: Additional arguments

        Returns:
            ScorchResult object
        """
        try:
            configs = self.parser.parse(Path(input_path))
            if not configs:
                return ScorchResult(
                    resources_removed=[],
                    resources_failed=[],
                    dry_run=kwargs.get("dry_run", False),
                    success=False,
                )

            # Use the first configuration for scorch
            config = configs[0]
            safety_check = not kwargs.get("auto_confirm", False)
            dry_run = kwargs.get("dry_run", False)

            scorch_engine = ScorchEngine(safety_check=safety_check)
            return scorch_engine.execute_scorch(config, dry_run=dry_run)

        except Exception as e:
            print(f"Scorch action failed: {e}")
            return ScorchResult(
                resources_removed=[],
                resources_failed=[{"error": str(e)}],
                dry_run=kwargs.get("dry_run", False),
                success=False,
            )

    def mount(self, input_path: str, **kwargs) -> bool:
        """
        Execute mount action

        Args:
            input_path: Path to Pyro file or directory
            **kwargs: Additional arguments

        Returns:
            True if successful, False otherwise
        """
        try:
            configs = self.parser.parse(Path(input_path))
            if not configs:
                return False

            for config in configs:
                sketch = self.sketch_generator.generate_mount_sketch(config)
                success = self.flow_engine.execute_sketch(sketch, ActionType.MOUNT)
                if not success:
                    return False

            return True
        except Exception as e:
            print(f"Mount action failed: {e}")
            return False

    @pysnooper.snoop()
    def validate(self, input_path: str, **kwargs) -> ValidationResult:
        """
        Execute validate action

        Args:
            input_path: Path to Pyro file or directory
            **kwargs: Additional arguments

        Returns:
            ValidationResult object
        """
        try:
            configs = self.parser.parse(Path(input_path))
            self.stdout.debug(f'Configs ({configs})')
            if not configs:
                self.stdout.err('No valid Pyro state files found at specified location! Details: {input_path}')
                return ValidationResult(
                    is_valid=False,
                    discrepancies=[{"error": "No valid Pyro files found"}],
                    summary={"total_issues": 1, "critical_issues": 1},
                )

            # Validate all configurations and combine results
            all_discrepancies = []
            all_valid = True

            for config in configs:
#               self.stdout.info(f'Processing Pyro config {config.label}... Details: {config.__dict__}') #$ % str(json.dumps(config.__dict__, indent=4)))
                result = self.validator.validate_configuration(config)
                self.stdout.debug(f'Result {result}')
                if result.discrepancies:
                    self.stdout.nok(f'Discrepancies %s' % str(json.dumps(result.discrepancies, indent=4)))
                all_discrepancies.extend(result.discrepancies)
                all_valid = all_valid and result.is_valid
                if result.is_valid:
                    self.stdout.ok(f'Machine state corresponds with Pyro config {config.label}')
                else:
                    self.stdout.nok(f'Machine state does not correspond with Pyro config {config.label}')

            # Create combined summary
            critical_issues = len(
                [d for d in all_discrepancies if d.get("critical", False)]
            )
            total_issues = len(all_discrepancies)

            if critical_issues:
                self.stdout.nok(f'({critical_issues}) critical issues identified')
                self.stdout.nok(f'({total_issues}) total issues identified')
            elif total_issues and not critical_issues:
                self.stdout.warn(f'({total_issues}) non critical issues identified')

            if all_valid:
                self.stdout.ok('Machine state corresponds!')
            else:
                self.stdout.nok('Machine state does not correspond!')

            summary = {
                "total_issues": total_issues,
                "critical_issues": critical_issues,
                "is_valid": all_valid,
            }

            return ValidationResult(
                is_valid=all_valid, discrepancies=all_discrepancies, summary=summary
            )

        except Exception as e:
            self.stdout.err(f"Validate action failed! Details: {e}")
            return ValidationResult(
                is_valid=False,
                discrepancies=[{"error": str(e)}],
                summary={"total_issues": 1, "critical_issues": 1},
            )

    def _default_config(self) -> Dict[str, Any]:
        """
        Get default configuration

        Returns:
            Default configuration dictionary
        """
        return {
            "safety_checks": True,
            "default_output_dir": "/tmp/pyroform",
            "log_level": "INFO",
            "log_timestamp": False,
            "auto_confirm": False,
            "dry_run": False,
            "debug": False,
        }

# CODE DUMP

#   # TODO - DEPRECATED
#   def _create_mock_flow_engine(self):
#       """
#       Create a mock flow engine for testing compatibility

#       Returns:
#           Mock PyroflowEngine instance
#       """
#       from unittest.mock import Mock

#       mock_engine = Mock(spec=PyroflowEngine)
#       mock_engine.execute_sketch.return_value = True
#       mock_engine.pause_execution.return_value = True
#       mock_engine.resume_execution.return_value = True
#       mock_engine.stop_execution.return_value = True
#       mock_engine.send_command.return_value = True
#       mock_engine.purge_data.return_value = True
#       mock_engine.current_sketch = None
#       return mock_engine

