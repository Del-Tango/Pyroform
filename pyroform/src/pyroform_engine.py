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

from .models import ActionType, PyroConfig
# from .models import PyroConfig, ScorchResult
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

    #@pysnooper.snoop()
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize PyroformEngine

        Args:
            config: Configuration dictionary
        """
        self.config = config or self._default_config()
        self.stdout = STDOUTMsg(
            debug_mode=False, #self.config['debug'],
            timestamp=self.config['log_timestamp'] or self.config['debug'],
        )
        self.parser = PyroParser(stdout=self.stdout)
        self.sketch_generator = SketchGenerator(
            stdout=self.stdout,
            config=config,
            dry_run=self.config['dry_run']
        )

        self.flow_engine = PyroflowEngine(stdout=self.stdout)

        # Use mocked flow engine to avoid FlowCTRL dependency issues
        # self._create_mock_flow_engine(stdout=self.stdout)

        self.validator = SystemValidator(stdout=self.stdout, config=self.config)
        self.reporter = ReportGenerator()

    #@pysnooper.snoop()
    def snapshot(self, output_path: str, **kwargs) -> dict:
        """
        """
        try:
            system_state = self.validator.get_system_state(
                max_depth=100, include_hidden=True
            )
            self.stdout.debug(f'system_state {system_state}')
            pyro_conf = self.sketch_generator.generate_sketch(None, ActionType.SNAPSHOT)
            self.stdout.debug(f'pyro_conf {pyro_conf}')
            with open(output_path, 'w') as fl:
                yaml.dump(pyro_conf, fl)
            self.stdout.ok(f'Machine state snapshot written to Pyro config {output_path}')
        except Exception as e:
            self.stdout.err(f'Error encountered while snapshotting system state! Details: {e}')
            self.stdout.nok(f'Could not snapshot system state to Pyro config {output_path}')
            return False
        return True

    #@pysnooper.snoop()
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
                if len(sketch) <= 1:
                    self.stdout.info(f'Nothing to configure! Skipping Pyro config ({config.label})')
                    continue
                success = self.flow_engine.execute_sketch(sketch, ActionType.CONFIGURE)
                self.stdout.debug(f'Success {success}')
                if not success:
                    return False

            return True
        except Exception as e:
            print(f"Configure action failed: {e}")
            return False

    def _confirm_scorch(self, config: PyroConfig) -> bool:
        """
        Confirm scorch operation with user

        Args:
            config: Configuration that will be used to determine what to keep

        Returns:
            True if confirmed, False if cancelled
        """
        self.stdout.warn(
            f"Scorch action will remove system resources not specified in '{config.label}'."
        )

        self.stdout.warn("This is a destructive operation that cannot be undone!")
        print()
        response = input("Are you sure about this? [Y/N]: ")
        print()
        return response.lower() in ["yes", "y"]


    #@pysnooper.snoop()
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

            safety_check = not kwargs.get("auto_confirm", False)
            dry_run = kwargs.get("dry_run", False)

            for config in configs:
                self.stdout.debug(f'Config {config}')
                sketch = self.sketch_generator.generate_scorch_sketch(config)
                self.stdout.debug(f'Sketch {sketch}')
                if len(sketch) <= 1:
                    self.stdout.info(f'Nothing to scorch! Skipping Pyro config ({config.label})')
                    continue
                if safety_check and not self._confirm_scorch(config):
                    self.stdout.warn(f'Scorch action aborted! Pyro config ({config.label}) not applied.\n')
                    continue

                success = self.flow_engine.execute_sketch(sketch, ActionType.SCORCH)
                self.stdout.debug(f'Success {success}')
                if not success:
                    return False

            return True
        except Exception as e:
            print(f"Scorch action failed: {e}")
            return False

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
                if len(sketch) <= 1:
                    self.stdout.info(f'Nothing to mount! Skipping Pyro config ({config.label})')
                    continue
                success = self.flow_engine.execute_sketch(sketch, ActionType.MOUNT)
                if not success:
                    return False

            return True
        except Exception as e:
            print(f"Mount action failed: {e}")
            return False

    #@pysnooper.snoop()
    def validate(self, input_path: str, **kwargs) -> ValidationResult:
        """
        Execute validate action

        Args:
            input_path: Path to Pyro file or directory
            **kwargs: Additional arguments

        Returns:
            ValidationResult object
        """
        system_state = {}
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
                result = self.validator.validate_configuration(config)
                self.stdout.debug(f'Result {result}')

                # TODO - Remove 2 down
                with open('validation.dummy', 'w') as fl:
                    fl.write(json.dumps(result.discrepancies, indent=4))

                if result.discrepancies:
                    self.stdout.nok(f'Discrepancies %s' % str(json.dumps(result.discrepancies, indent=4)))

                # TODO - FIX ME
#               all_discrepancies.extend(result.discrepancies)
                all_discrepancies.append(result.discrepancies)

                all_valid = all_valid and result.is_valid
                if result.is_valid:
                    self.stdout.ok(f'Machine state corresponds with Pyro config {config.label}')
                else:
                    self.stdout.nok(f'Machine state does not correspond with Pyro config {config.label}')
                system_state = self.validator._last_result.system_state





#           self.stdout.info(f'[ DEBUG ]: all_discrepancies - {all_discrepancies}')
#           critical_list = [len(v) for item in all_discrepancies for k, v in item.items() if 'mismatch' not in k]
#           self.stdout.info(f'[ DEBUG ]: critical_list - {critical_list}')
#           all_list = [len(v) for item in all_discrepancies for k, v in item.items()]
#           self.stdout.info(f'[ DEBUG ]: all_list - {all_list}')

            # TODO - FIX ME

            critical_issues = sum([len(v) for item in all_discrepancies for k, v in item.items() if 'mismatch' not in k])
            total_issues = sum([len(v) for item in all_discrepancies for k, v in item.items()])

            if critical_issues:
                self.stdout.nok(f'({critical_issues}) critical issues identified, ({total_issues}) total issues identified!')
            elif total_issues and not critical_issues:
                self.stdout.warn(f'({total_issues}) non critical issues identified')

            if all_valid:
                self.stdout.ok('No further action required!')
            else:
                self.stdout.nok('Run action "Configure" to apply Pyro config!')

            # TODO - Remove 2 down
            with open('discrepancies.dummy', 'w') as fl:
                fl.write(json.dumps(all_discrepancies, indent=4))

            summary = {
                "total_issues": total_issues,
                "critical_issues": critical_issues,
                "is_valid": all_valid,
            }

            return ValidationResult(
                is_valid=all_valid,
                discrepancies=all_discrepancies,
                summary=summary,
                system_state=system_state,
            )

        except Exception as e:
            self.stdout.err(f"Validate action failed! Details: {e}")
            return ValidationResult(
                is_valid=False,
                discrepancies=[{"error": str(e)}],
                summary={"total_issues": 1, "critical_issues": 1},
                system_state=system_state,
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

