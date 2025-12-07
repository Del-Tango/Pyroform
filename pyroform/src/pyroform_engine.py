"""
Pyroform Engine - Main Library Class

This module contains the core Pyroform engine that coordinates all system
configuration operations including snapshotting, configuration application,
resource management (scorch), mounting, and validation.
"""

import json
import yaml

# import pysnooper

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from .flow_engine import PyroflowEngine
from .logging import STDOUTMsg
from .models import (
    ActionType,
    ConfigureResult,
    MountResult,
    PyroConfig,
    ScorchResult,
    SnapshotResult,
    ValidationResult,
)
from .parser import PyroParser
from .reporter import ReportGenerator
from .scanner import SystemStateScanner
from .sketch_generator import SketchGenerator
from .validator import SystemValidator


class OperationResult(Enum):
    """
    Enumeration of possible result statuses for engine operations.

    Attributes:
        SUCCESS: Operation completed successfully
        FAILURE: Operation failed
        CANCELLED: Operation was cancelled by user
        SKIPPED: Operation was skipped (no action required)
    """

    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class PyroformEngine:
    """
    Core engine that coordinates all Pyroform operations.

    This class serves as the central coordinator for all Pyroform functionality,
    managing the interaction between parsers, validators, sketch generators,
    and execution engines.
    """

    # @pysnooper.snoop()
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        stdout: STDOUTMsg | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Pyroform engine with configuration.

        Args:
            config: Optional configuration dictionary. If not provided,
                   default configuration will be used.
            stdout: Optional STDOUTMsg instance for logging. If not provided,
                   a default instance will be created.
            **kwargs: Additional keyword arguments for configuration.

        Raises:
            ValueError: If required configuration values are invalid
        """
        self.config = config or self._get_default_config()
        self.stdout = stdout or STDOUTMsg(
            debug_mode=kwargs.get("debug", self.config.get("debug", False)),
            timestamp=kwargs.get(
                "log_timestamp", self.config.get("log_timestamp", False)
            ),
        )
        self.stdout.debug(f"PyroformEngine conf: {self.config}")
        # Initialize core components
        self.parser = PyroParser(config=self.config, stdout=self.stdout)
        self.sketch_generator = SketchGenerator(
            stdout=self.stdout,
            config=self.config,
        )
        self.flow_engine = PyroflowEngine(stdout=self.stdout, pyro_config=self.config)
        self.validator = SystemValidator(stdout=self.stdout, config=self.config)
        self.scanner = SystemStateScanner(stdout=self.stdout, config=self.config)
        self.reporter = ReportGenerator(stdout=self.stdout, config=self.config)

    # @pysnooper.snoop()
    def snapshot(self, output_path: Path, **kwargs: Any) -> SnapshotResult:
        """
        Create a snapshot of current system state as Pyro configuration.

        Captures the current system state and generates a YAML configuration
        file that can be used to reproduce this state.

        Args:
            output_path: Path where the snapshot configuration will be saved
            **kwargs: Additional parameters:
                - max_depth: Maximum recursion depth for scanning (default: 100)
                - include_hidden: Whether to include hidden files/directories (default: True)

        Returns:
            SnapshotResult containing operation results and details
        """
        max_depth = kwargs.get("max_depth", 100)
        include_hidden = kwargs.get("include_hidden", True)
        details, errors = {"output_path": str(output_path), "metadata": kwargs}, []
        try:

            details["system_state"] = self.scanner.scan_system_state(
                max_depth=max_depth, include_hidden=include_hidden
            )
            self.stdout.debug(
                f'Captured system state: {len(details["system_state"])} items'
            )

            # Generate configuration from system state
            snapshot = self.sketch_generator.generate_sketch(
                None,
                ActionType.SNAPSHOT,
                system_state=details["system_state"],
                **kwargs,
            )
            self.stdout.debug(f"Generated pyro config with {len(snapshot)} elements")

            # Write configuration to file
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)

            with output_path_obj.open("w") as file:
                yaml.dump(snapshot, file, default_flow_style=False)

            details.update({"snapshot": snapshot})
            self.stdout.ok(f"System snapshot written to: {output_path}")
            return self._objectify_result(
                ActionType.SNAPSHOT,
                **{
                    "success": True,
                    "errors": errors,
                    "details": details,
                },
            )

        except Exception as e:
            msg = (
                f"Snapshot operation failed due to encountered exception! Details: {e}"
            )
            self.stdout.err(msg)
            errors.append(msg)
            return self._objectify_result(
                ActionType.SNAPSHOT,
                **{
                    "success": False,
                    "errors": str(errors),
                    "details": details,
                },
            )

    # @pysnooper.snoop()
    def configure(self, input_path: Path, **kwargs: Any) -> ConfigureResult:
        """
        Apply configuration from Pyro files to the system.

        Parses configuration files and executes the necessary actions
        to bring the system to the desired state.

        Args:
            input_path: Path to Pyro configuration file or directory
            **kwargs: Additional parameters:
                - dry_run: If True, only simulate changes without applying them

        Returns:
            ConfigureResult containing operation results and details
        """
        details, errors = {"input_path": str(input_path), "metadata": kwargs}, []
        dry_run = kwargs.get("dry_run", self.config.get("dry_run", False))
        results, processed_configs = [], []
        try:
            configs = self.parser.parse(Path(input_path))
            if not configs:
                msg = f"No valid Pyro files found at: {input_path}"
                self.stdout.err(msg)
                errors.append(msg)
                return self._objectify_result(
                    ActionType.CONFIGURE,
                    **{
                        "success": False,
                        "dry_run": dry_run,
                        "details": details,
                        "errors": errors,
                    },
                )

            self.stdout.debug(f"Found {len(configs)} configuration(s) to process")
            if dry_run:
                self.stdout.info(
                    "DRY RUN: No changes will be made. FlowCTRL sketch main commands will be commented."
                )

            for config in configs:
                config_result = self._process_configuration(
                    config, ActionType.CONFIGURE, **kwargs
                )
                results.append(config_result)
                if config_result["success"]:
                    processed_configs.append(config.label)
                else:
                    errors.append(
                        f"Failed to process Pyro file config! Details: {config}"
                    )

            overall_success = all(result["success"] for result in results)
            details.update(
                {
                    "processed_configs": processed_configs,
                    "results": results,
                }
            )

            return self._objectify_result(
                ActionType.CONFIGURE,
                **{
                    "success": overall_success,
                    "dry_run": dry_run,
                    "details": details,
                    "errors": errors,
                },
            )

        except Exception as error:
            msg = f"Configure operation failed: {error}"
            self.stdout.err(msg)
            errors.append(msg)
            return self._objectify_result(
                ActionType.CONFIGURE,
                **{
                    "success": False,
                    "dry_run": dry_run,
                    "details": details,
                    "errors": errors,
                },
            )

    # @pysnooper.snoop()
    def scorch(self, input_path: str, **kwargs: Any) -> ScorchResult:
        """
        Remove system resources not specified in Pyro configurations.

        This is a destructive operation that removes resources not defined
        in the provided configuration files. User confirmation is required
        unless auto_confirm is True.

        Args:
            input_path: Path to Pyro configuration file or directory
            **kwargs: Additional parameters:
                - dry_run: If True, only simulate changes without applying them
                - auto_confirm: If True, skip confirmation prompts

        Returns:
            ScorchResult containing operation results and details
        """
        details = {"input_path": input_path, "metadata": kwargs}
        processed_configs, all_comparisons, errors, results = [], [], [], []
        dry_run = kwargs.get("dry_run", self.config.get("dry_run", False))
        auto_confirm = kwargs.get(
            "auto_confirm", self.config.get("auto_confirm", False)
        )
        try:
            configs = self.parser.parse(Path(input_path))
            if not configs:
                errors.append("No valid configurations found")
                return self._objectify_result(
                    ActionType.SCORCH,
                    **{
                        "success": False,
                        "dry_run": dry_run,
                        "details": details,
                        "errors": errors,
                    },
                )
            if dry_run:
                self.stdout.info(
                    "DRY RUN: No changes will be made. FlowCTRL sketch main commands will be commented."
                )

            for config in configs:
                scorch = self._execute_scorch_config(config, errors=errors, **kwargs)
                results.append(scorch)
                if scorch["success"]:
                    all_comparisons.append(scorch.get("comparison", {}))
                    processed_configs.append(config.label)
                else:
                    errors.append(f"Failed to process Pyro config! Details: {config}")

            overall_success = all(result["success"] for result in results)
            details.update(
                {
                    "processed_configs": processed_configs,
                    "system_state": scorch.get("system_state", {}),
                    "results": results,
                }
            )

            return self._objectify_result(
                ActionType.SCORCH,
                **{
                    "success": len(errors) == 0,
                    "dry_run": dry_run,
                    "details": details,
                    "errors": errors,
                },
            )

        except Exception as e:
            msg = f"Scorch operation failed due to encountered exception! Details: {e}"
            self.stdout.err(msg)
            errors.append(msg)
            return self._objectify_result(
                ActionType.SCORCH,
                **{
                    "success": False,
                    "dry_run": dry_run,
                    "details": details,
                    "errors": errors,
                },
            )

    # @pysnooper.snoop()
    def _execute_scorch_config(
        self, config: PyroConfig, errors: list | None = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute scorch operation for a single configuration.

        Args:
            config: Pyro configuration to process
            errors: Optional list to append error messages to
            **kwargs: Additional parameters including auto_confirm

        Returns:
            Dictionary with scorch operation results for this configuration
        """
        try:
            sketch = self.sketch_generator.generate_scorch_sketch(config, **kwargs)
            system_state = self.sketch_generator._last_system_state
            comparison = self.sketch_generator._last_comparison

            if len(sketch) <= 1:
                self.stdout.info(f"Nothing to scorch for {config.label}, skipping")
                return {
                    "success": True,
                    "skipped": True,
                    "config_label": config.label,
                    "system_state": system_state,
                }

            if not kwargs.get(
                "auto_confirm", self.config.get("auto_confirm")
            ) and not self._confirm_scorch(config):
                msg = f"Scorch cancelled for {config.label}"
                self.stdout.warn(msg)
                if errors and isinstance(errors, list):
                    errors.append(msg)
                return {
                    "success": False,
                    "cancelled": True,
                    "config_label": config.label,
                    "system_state": system_state,
                    "comparison": comparison,
                }
            success = self.flow_engine.execute_sketch(
                sketch, ActionType.SCORCH, errors=errors, **kwargs
            )
            return {
                "success": success,
                "config_label": config.label,
                "system_state": system_state,
                "comparison": comparison,
                "sketch": sketch,
            }

        except Exception as e:
            self.stdout.err(f"Scorch failed for {config.label}! Details: {e}")
            return {"success": False, "error": str(e), "config_label": config.label}

    # @pysnooper.snoop()
    def mount(self, input_path: str, **kwargs: Any) -> MountResult:
        """
        Mount resources defined in Pyro configurations.

        Sets up mounts, volumes, and other mountable resources as defined
        in the configuration files.

        Args:
            input_path: Path to Pyro configuration file or directory
            **kwargs: Additional parameters:
                - dry_run: If True, only simulate changes without applying them
                - auto_confirm: If True, skip confirmation prompts

        Returns:
            MountResult containing operation results and details
        """
        details, errors = {"input_path": str(input_path), "metadata": kwargs}, []
        dry_run = kwargs.get("dry_run", self.config.get("dry_run", False))
        results, processed_configs = [], []
        try:
            configs = self.parser.parse(Path(input_path))
            if not configs:
                msg = f"No valid Pyro files found at: {input_path}"
                self.stdout.err(msg)
                errors.append(msg)
                return self._objectify_result(
                    ActionType.CONFIGURE,
                    **{
                        "success": False,
                        "dry_run": dry_run,
                        "details": details,
                        "errors": errors,
                    },
                )

            self.stdout.debug(f"Found {len(configs)} configuration(s) to process")
            if dry_run:
                self.stdout.info(
                    "DRY RUN: No changes will be made. FlowCTRL sketch main commands will be commented."
                )

            for config in configs:
                config_result = self._process_configuration(
                    config, ActionType.MOUNT, **kwargs
                )
                results.append(config_result)
                if config_result["success"]:
                    processed_configs.append(config.label)
                else:
                    errors.append(
                        f"Failed to process Pyro file config! Details: {config}"
                    )

            overall_success = all(result["success"] for result in results)
            details.update(
                {
                    "processed_configs": processed_configs,
                    "results": results,
                }
            )

            return self._objectify_result(
                ActionType.MOUNT,
                **{
                    "success": overall_success,
                    "dry_run": dry_run,
                    "details": details,
                    "errors": errors,
                },
            )

        except Exception as error:
            msg = f"Configure operation failed: {error}"
            self.stdout.err(msg)
            errors.append(msg)
            return self._objectify_result(
                ActionType.MOUNT,
                **{
                    "success": False,
                    "dry_run": dry_run,
                    "details": details,
                    "errors": errors,
                },
            )

    # @pysnooper.snoop()
    def validate(self, input_path: str, **kwargs: Any) -> ValidationResult:
        """
        Validate system state against Pyro configurations.

        Compares current system state with desired state defined in
        configuration files and reports discrepancies.

        Args:
            input_path: Path to Pyro configuration file or directory
            **kwargs: Additional parameters for validation

        Returns:
            ValidationResult containing validation results and details
        """
        details = {"input_path": input_path, "metadata": kwargs}
        processed_configs, all_comparisons, errors, results = [], [], [], []
        is_valid, success, all_discrepancies, system_state = False, True, [], {}
        summary = {"total_issues": 0, "critical_issues": 0}
        try:
            configs = self.parser.parse(Path(input_path))
            if not configs:
                msg = f"No valid Pyro files found at: {input_path}"
                self.stdout.err(msg)
                errors.append(msg)
                summary.update({"total_issues": 1, "critical_issues": 1})
                return self._objectify_result(
                    ActionType.VALIDATE,
                    **{
                        "is_valid": is_valid,
                        "success": success,
                        "system_state": system_state,
                        "discrepancies": all_discrepancies,
                        "summary": summary,
                        "errors": errors,
                        "details": details,
                    },
                )

            self.stdout.debug(f"Validating {len(configs)} configuration(s)")

            for config in configs:
                result = self.validator.validate_configuration(config, **kwargs)
                results.append(result)
                if result.discrepancies:
                    all_discrepancies.append({config.label: result.discrepancies})
                    self._log_validation_discrepancies(
                        config.label, result.discrepancies
                    )
                is_valid = is_valid and result.is_valid

                # Update issue counts
                config_critical = sum(
                    [
                        len(v)
                        for k, v in result.discrepancies.items()
                        if "mismatch" not in str(k).lower()
                    ]
                )
                config_total = sum([len(v) for k, v in result.discrepancies.items()])
                summary["critical_issues"] += config_critical
                summary["total_issues"] += config_total

                self._log_validation_result(
                    config.label, result.is_valid, config_critical, config_total
                )

            system_state = self.validator._last_result.system_state
            success = len(errors) == 0

            self._log_validation_summary(
                is_valid, summary["critical_issues"], summary["total_issues"]
            )

            return self._objectify_result(
                ActionType.VALIDATE,
                **{
                    "is_valid": is_valid,
                    "success": success,
                    "system_state": system_state,
                    "discrepancies": all_discrepancies,
                    "summary": summary,
                    "errors": errors,
                    "details": details,
                },
            )

        except Exception as e:
            msg = f"Validation failed due to encountered exception! Details: {e}"
            self.stdout.err(msg)
            errors.append(msg)
            summary["critical_issues"] += 1
            summary["total_issues"] += 1
            return self._objectify_result(
                ActionType.VALIDATE,
                **{
                    "is_valid": False,
                    "success": False,
                    "system_state": system_state,
                    "discrepancies": all_discrepancies,
                    "summary": summary,
                    "errors": errors,
                    "details": details,
                },
            )

    # @pysnooper.snoop()
    def _process_configuration(
        self, config: PyroConfig, action: ActionType, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Process a single configuration for the given action.

        Args:
            config: Configuration to process
            action: Type of action to perform
            **kwargs: Additional parameters for processing

        Returns:
            Dictionary with processing results including success status,
            configuration label, and any errors encountered
        """
        try:
            sketch = self.sketch_generator.generate_sketch(config, action)

            if len(sketch) <= 1:
                self.stdout.info(f"No actions required for {config.label}, skipping")
                return {"success": True, "skipped": True, "config_label": config.label}

            success = self.flow_engine.execute_sketch(sketch, action, **kwargs)

            return {
                "success": success,
                "skipped": False,
                "config_label": config.label,
                "actions_executed": len(sketch),
                "sketch": sketch,
            }

        except Exception as error:
            self.stdout.err(f"Failed to process {config.label}: {error}")
            return {"success": False, "error": str(error), "config_label": config.label}

    def _confirm_scorch(self, config: PyroConfig) -> bool:
        """
        Confirm destructive scorch operation with user.

        Args:
            config: Configuration that will determine what resources to keep

        Returns:
            True if confirmed, False if cancelled
        """
        self.stdout.warn(
            f"Scorch will remove system resources not specified in '{config.label}'"
        )
        self.stdout.warn("This is a DESTRUCTIVE operation that cannot be undone!")

        print()  # Add spacing
        response = input("Are you sure about this? [Y/N]> ").strip().lower()
        print()

        return response in ["y", "yes"]

    def _log_validation_discrepancies(
        self, config_label: str, discrepancies: List[Dict]
    ) -> None:
        """
        Log validation discrepancies in a structured format.

        Args:
            config_label: Label of the configuration being validated
            discrepancies: List of discrepancy dictionaries
        """
        self.stdout.nok(
            f"Validation discrepancies for Pyro config ({config_label}):\n"
            + json.dumps(discrepancies, indent=4)
        )

    def _log_validation_result(
        self, config_label: str, is_valid: bool, critical_issues: int, total_issues: int
    ) -> None:
        """
        Log individual configuration validation result.

        Args:
            config_label: Label of the configuration being validated
            is_valid: Whether the configuration is valid
            critical_issues: Number of critical issues found
            total_issues: Total number of issues found
        """
        if is_valid:
            self.stdout.ok(f"System state matches Pyro config: ({config_label})")
        else:
            issue_text = f"{critical_issues} critical, {total_issues} total"
            self.stdout.nok(
                f"System state mismatch for ({config_label}) ({issue_text} issues)"
            )

    def _log_validation_summary(
        self, all_valid: bool, critical_issues: int, total_issues: int
    ) -> None:
        """
        Log overall validation summary.

        Args:
            all_valid: Whether all configurations are valid
            critical_issues: Total number of critical issues
            total_issues: Total number of all issues
        """
        if critical_issues > 0:
            self.stdout.nok(
                f"Found {critical_issues} critical issues, {total_issues} total issues"
            )
        elif total_issues > 0:
            self.stdout.warn(f"Found {total_issues} non-critical issues")

        if all_valid:
            self.stdout.ok("System state validation passed - no action required")
        else:
            self.stdout.nok(
                'System state validation failed - run "configure" to apply changes'
            )

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get the default engine configuration.

        Returns:
            Dictionary with default configuration values
        """
        return {
            "input_path": "",
            "output_path": "",
            "log_level": "INFO",
            "log_timestamp": False,
            "auto_confirm": False,
            "dry_run": False,
            "debug": False,
            "report": False,
            "cleanup": False,
        }

    def _objectify_result(self, action_type: str, *args: Any, **kwargs: Any) -> Type:
        """
        Convert result dictionary to appropriate result object type.

        Args:
            action_type: Type of action performed
            **kwargs: Result data to pass to the result object constructor

        Returns:
            Appropriate result object (ConfigureResult, ScorchResult, etc.)

        Raises:
            ValueError: If action_type is not recognized
        """
        result = None
        match action_type:
            case ActionType.CONFIGURE:
                result = ConfigureResult(*args, **kwargs)
            case ActionType.SCORCH:
                result = ScorchResult(*args, **kwargs)
            case ActionType.MOUNT:
                result = MountResult(*args, **kwargs)
            case ActionType.VALIDATE:
                result = ValidationResult(*args, **kwargs)
            case ActionType.SNAPSHOT:
                result = SnapshotResult(*args, **kwargs)
            case _:
                self.stdout.err(f"Invalid action type! Details: {action_type}")
                return result
        return result


# CODE DUMP

#   """
#   Pyroform Engine - Main Library Class
#   """
#   import json
#   import yaml
#   import pysnooper

#   from pathlib import Path
#   from typing import Dict, Any, Optional, List, Type
#   from enum import Enum

#   from .models import (
#       ActionType, PyroConfig, ConfigureResult, ScorchResult, MountResult,
#       SnapshotResult, ValidationResult, ValidationSummary
#   )
#   from .parser import PyroParser
#   from .sketch_generator import SketchGenerator
#   from .flow_engine import PyroflowEngine
#   from .validator import SystemValidator
#   from .logging import STDOUTMsg
#   from .scanner import SystemStateScanner
#   from .reporter import ReportGenerator
