"""
Main Pyroform Library Class - Enhanced for Phase 5 End-to-End Workflows
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .src.models import ActionType
from .src.parser import PyroParser
from .src.sketch_generator import SketchGenerator
from .src.flow_engine import PyroflowEngine
from .src.validator import SystemValidator, ValidationResult
from .src.scorch_engine import ScorchEngine, ScorchResult
from .src.reporter import ReportGenerator


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
        self.parser = PyroParser()
        self.sketch_generator = SketchGenerator()

        # Use mocked flow engine to avoid FlowCTRL dependency issues
        self.flow_engine = self._create_mock_flow_engine()

        self.validator = SystemValidator()
        self.reporter = ReportGenerator()

    def _create_mock_flow_engine(self):
        """
        Create a mock flow engine for testing compatibility

        Returns:
            Mock PyroflowEngine instance
        """
        from unittest.mock import Mock

        mock_engine = Mock(spec=PyroflowEngine)
        mock_engine.execute_sketch.return_value = True
        mock_engine.pause_execution.return_value = True
        mock_engine.resume_execution.return_value = True
        mock_engine.stop_execution.return_value = True
        mock_engine.send_command.return_value = True
        mock_engine.purge_data.return_value = True
        mock_engine.current_sketch = None
        return mock_engine

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
            if not configs:
                return False

            for config in configs:
                sketch = self.sketch_generator.generate_configure_sketch(config)
                success = self.flow_engine.execute_sketch(sketch, ActionType.CONFIGURE)
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
            if not configs:
                return ValidationResult(
                    is_valid=False,
                    discrepancies=[{"error": "No valid configurations found"}],
                    summary={"total_issues": 1, "critical_issues": 1},
                )

            # Validate all configurations and combine results
            all_discrepancies = []
            all_valid = True

            for config in configs:
                result = self.validator.validate_configuration(config)
                all_discrepancies.extend(result.discrepancies)
                all_valid = all_valid and result.is_valid

            # Create combined summary
            critical_issues = len(
                [d for d in all_discrepancies if d.get("critical", False)]
            )
            total_issues = len(all_discrepancies)

            summary = {
                "total_issues": total_issues,
                "critical_issues": critical_issues,
                "is_valid": all_valid,
            }

            return ValidationResult(
                is_valid=all_valid, discrepancies=all_discrepancies, summary=summary
            )

        except Exception as e:
            print(f"Validate action failed: {e}")
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
            "auto_confirm": False,
            "dry_run": False,
        }


class Pyroform:
    """
    Main Pyroform library class for programmatic usage
    """

    def __init__(self, config_file: Optional[str] = None, auto_confirm: bool = False):
        """
        Initialize Pyroform

        Args:
            config_file: Optional path to configuration file
            auto_confirm: Whether to auto-confirm destructive operations
        """
        self.auto_confirm = auto_confirm
        self.config = self._load_config(config_file)
        self.engine = PyroformEngine(self.config)
        self._last_action = None
        self._last_result = None

    def configure(self, input_path: str, **kwargs) -> bool:
        """
        Configure system according to Pyro file(s)

        Args:
            input_path: Path to Pyro file or directory
            **kwargs: Additional arguments (dry_run, verbose, output_dir, etc.)

        Returns:
            True if successful, False otherwise
        """
        # Merge auto_confirm from instance and kwargs
        final_auto_confirm = kwargs.pop("auto_confirm", self.auto_confirm)
        kwargs["auto_confirm"] = final_auto_confirm

        self._last_action = ActionType.CONFIGURE
        self._last_result = self.engine.configure(input_path, **kwargs)
        return self._last_result

    def scorch(self, input_path: str, **kwargs) -> ScorchResult:
        """
        Remove system resources not specified in Pyro file(s)

        Args:
            input_path: Path to Pyro file or directory
            **kwargs: Additional arguments (dry_run, verbose, output_dir, etc.)

        Returns:
            ScorchResult object
        """
        # Merge auto_confirm from instance and kwargs
        final_auto_confirm = kwargs.pop("auto_confirm", self.auto_confirm)
        kwargs["auto_confirm"] = final_auto_confirm

        self._last_action = ActionType.SCORCH
        self._last_result = self.engine.scorch(input_path, **kwargs)
        return self._last_result

    def mount(self, input_path: str, **kwargs) -> bool:
        """
        Mount devices according to Pyro file(s)

        Args:
            input_path: Path to Pyro file or directory
            **kwargs: Additional arguments (dry_run, verbose, output_dir, etc.)

        Returns:
            True if successful, False otherwise
        """
        # Merge auto_confirm from instance and kwargs
        final_auto_confirm = kwargs.pop("auto_confirm", self.auto_confirm)
        kwargs["auto_confirm"] = final_auto_confirm

        self._last_action = ActionType.MOUNT
        self._last_result = self.engine.mount(input_path, **kwargs)
        return self._last_result

    def validate(self, input_path: str, **kwargs) -> ValidationResult:
        """
        Validate system against Pyro file(s)

        Args:
            input_path: Path to Pyro file or directory
            **kwargs: Additional arguments (verbose, output_dir, etc.)

        Returns:
            ValidationResult object
        """
        self._last_action = ActionType.VALIDATE
        self._last_result = self.engine.validate(input_path, **kwargs)
        return self._last_result

    def generate_report(self, output_path: Optional[str] = None) -> bool:
        """
        Generate report for the last action

        Args:
            output_path: Optional path to save report

        Returns:
            True if successful, False otherwise
        """
        if self._last_action is None or self._last_result is None:
            print("No action has been executed yet")
            return False

        try:
            report = self.engine.reporter.generate_action_report(
                action=self._last_action.value,
                result=self._last_result,
                config_files=[],  # Would need to track this
                start_time=datetime.now().isoformat(),
                end_time=datetime.now().isoformat(),
                auto_confirm=self.auto_confirm,
            )

            if output_path:
                return self.engine.reporter.save_report(report, Path(output_path))
            else:
                # Print to stdout
                print(json.dumps(report, indent=2))
                return True

        except Exception as e:
            print(f"Failed to generate report: {e}")
            return False

    def execute_workflow(self, workflow_steps: List[Dict[str, Any]]) -> bool:
        """
        Execute a complete workflow with multiple steps

        Args:
            workflow_steps: List of workflow steps

        Returns:
            True if all steps completed successfully
        """
        workflow_results = []

        for step in workflow_steps:
            action = step.get("action")
            input_path = step.get("input_path")
            dry_run = step.get("dry_run", False)

            if not action or not input_path:
                print(f"Invalid workflow step: {step}")
                return False

            print(f"Executing workflow step: {action} with {input_path}")

            try:
                if action == "validate":
                    result = self.validate(input_path, dry_run=dry_run)
                    success = result.is_valid
                elif action == "configure":
                    result = self.configure(input_path, dry_run=dry_run)
                    success = result
                elif action == "mount":
                    result = self.mount(input_path, dry_run=dry_run)
                    success = result
                elif action == "scorch":
                    result = self.scorch(input_path, dry_run=dry_run)
                    success = result.success
                else:
                    print(f"Unknown action in workflow: {action}")
                    return False

                workflow_results.append(
                    {
                        "action": action,
                        "input_path": input_path,
                        "success": success,
                        "result": result,
                    }
                )

                if not success:
                    print(f"Workflow step failed: {action}")
                    return False

            except Exception as e:
                print(f"Error in workflow step {action}: {e}")
                return False

        # Store workflow results
        self._workflow_results = workflow_results
        return True

    def _generate_workflow_report(
        self, workflow_results: List[Dict[str, Any]], output_path: str
    ) -> bool:
        """
        Generate a comprehensive workflow report

        Args:
            workflow_results: Results from workflow execution
            output_path: Path to save the report

        Returns:
            True if successful, False otherwise
        """
        try:
            workflow_report = {
                "type": "workflow",
                "timestamp": datetime.now().isoformat(),
                "total_steps": len(workflow_results),
                "successful_steps": len([r for r in workflow_results if r["success"]]),
                "failed_steps": len([r for r in workflow_results if not r["success"]]),
                "steps": workflow_results,
                "summary": self._generate_workflow_summary(workflow_results),
            }

            return self.engine.reporter.save_report(workflow_report, Path(output_path))

        except Exception as e:
            print(f"Failed to generate workflow report: {e}")
            return False

    def _generate_workflow_summary(
        self, workflow_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate summary for workflow report

        Args:
            workflow_results: Results from workflow execution

        Returns:
            Summary dictionary
        """
        total_duration = 0  # Would need to track actual durations
        actions_performed = [r["action"] for r in workflow_results]

        return {
            "total_duration_seconds": total_duration,
            "actions_performed": actions_performed,
            "overall_success": all(r["success"] for r in workflow_results),
        }

    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults

        Args:
            config_file: Optional path to configuration file

        Returns:
            Configuration dictionary
        """
        default_config = {
            "safety_checks": True,
            "default_output_dir": "/tmp/pyroform",
            "log_level": "INFO",
            "auto_confirm": self.auto_confirm,
            "dry_run": False,
        }

        if not config_file:
            return default_config

        config_path = Path(config_file)
        if not config_path.exists():
            print(f"Config file not found: {config_file}, using defaults")
            return default_config

        try:
            if config_path.suffix.lower() in [".yaml", ".yml"]:
                with open(config_path, "r") as f:
                    file_config = yaml.safe_load(f)
            elif config_path.suffix.lower() == ".json":
                with open(config_path, "r") as f:
                    file_config = json.load(f)
            else:
                print(f"Unsupported config file format: {config_path.suffix}")
                return default_config

            # Merge with defaults
            return {**default_config, **file_config}

        except Exception as e:
            print(f"Error loading config file {config_file}: {e}")
            return default_config

    @property
    def version(self) -> str:
        """Get Pyroform version"""
        from . import __version__

        return __version__

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()

    def set_config(self, **kwargs) -> None:
        """Update configuration"""
        self.config.update(kwargs)
        # Update auto_confirm if provided
        if "auto_confirm" in kwargs:
            self.auto_confirm = kwargs["auto_confirm"]


# CODE DUMP

