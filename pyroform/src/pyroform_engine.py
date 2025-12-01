"""
Pyroform Engine - Main Library Class

A configuration management engine that coordinates system state operations
including snapshotting, configuration, validation, and destructive operations.
"""

import json
import yaml
import pysnooper

from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum

from .models import ActionType, PyroConfig
from .parser import PyroParser
from .sketch_generator import SketchGenerator
from .flow_engine import PyroflowEngine
from .validator import SystemValidator, ValidationResult
from .reporter import ReportGenerator
from .logging import STDOUTMsg


class OperationResult(Enum):
    """Result status for engine operations."""
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class PyroformEngine:
    """
    Core engine that coordinates all Pyroform operations.

    The engine manages the complete lifecycle of system configuration management:
    - Parsing configuration files
    - Generating execution plans (sketches)
    - Validating system state
    - Executing configuration changes
    - Managing destructive operations

    Attributes:
        config: Engine configuration dictionary
        stdout: Standard output messaging handler
        parser: Configuration file parser
        sketch_generator: Execution plan generator
        flow_engine: Sketch execution engine
        validator: System state validator
        reporter: Report generation utility
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Pyroform engine with configuration.

        Args:
            config: Optional configuration dictionary. If not provided,
                   default configuration will be used.

        Raises:
            ValueError: If required configuration values are invalid
        """
        self.config = config or self._get_default_config()
        self._validate_config()

        self.stdout = STDOUTMsg(
            debug_mode=self.config.get('debug', False),
            timestamp=self.config.get('log_timestamp', False),
        )

        # Initialize core components
        self.parser = PyroParser(stdout=self.stdout)
        self.sketch_generator = SketchGenerator(
            stdout=self.stdout,
            config=config,
            dry_run=self.config.get('dry_run', False)
        )
        self.flow_engine = PyroflowEngine(stdout=self.stdout)
        self.validator = SystemValidator(stdout=self.stdout, config=self.config)
        self.reporter = ReportGenerator()

    def snapshot(self, output_path: str, **kwargs) -> Dict[str, Any]:
        """
        Create a snapshot of current system state as Pyro configuration.

        Captures the current system state and generates a YAML configuration
        file that can be used to reproduce this state.

        Args:
            output_path: File path where the snapshot will be saved
            **kwargs: Additional arguments:
                - max_depth: Maximum directory depth to scan (default: 100)
                - include_hidden: Whether to include hidden files (default: True)

        Returns:
            Dictionary containing:
                - success: Boolean indicating operation success
                - output_path: Path where snapshot was saved
                - system_state: Captured system state (on success)
                - error: Error message (on failure)

        Example:
            >>> engine.snapshot("/path/to/snapshot.yaml")
            {'success': True, 'output_path': '/path/to/snapshot.yaml'}
        """
        max_depth = kwargs.get('max_depth', 100)
        include_hidden = kwargs.get('include_hidden', True)

        try:
            # Capture current system state
            system_state = self.validator.get_system_state(
                max_depth=max_depth,
                include_hidden=include_hidden
            )
            self.stdout.debug(f'Captured system state: {len(system_state)} items')

            # Generate configuration from system state
            pyro_config = self.sketch_generator.generate_sketch(
                None,
                ActionType.SNAPSHOT
            )
            self.stdout.debug(f'Generated pyro config with {len(pyro_config)} elements')

            # Write configuration to file
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)

            with output_path_obj.open('w') as file:
                yaml.dump(pyro_config, file, default_flow_style=False)

            self.stdout.ok(f'System snapshot written to: {output_path}')

            return {
                'success': True,
                'output_path': output_path,
                'system_state': system_state
            }

        except Exception as error:
            self.stdout.err(f'Snapshot operation failed: {error}')
            return {
                'success': False,
                'error': str(error),
                'output_path': output_path
            }

    def configure(self, input_path: str, **kwargs) -> Dict[str, Any]:
        """
        Apply configuration from Pyro files to the system.

        Parses configuration files and executes the necessary actions
        to bring the system to the desired state.

        Args:
            input_path: Path to Pyro file or directory containing Pyro files
            **kwargs: Additional arguments for configuration

        Returns:
            Dictionary containing:
                - success: Overall operation success
                - processed_configs: List of processed configuration labels
                - results: Individual configuration results

        Example:
            >>> engine.configure("/path/to/configs/")
            {'success': True, 'processed_configs': ['web_server', 'database']}
        """
        try:
            configs = self.parser.parse(Path(input_path))
            if not configs:
                self.stdout.err(f'No valid Pyro files found at: {input_path}')
                return {'success': False, 'processed_configs': []}

            self.stdout.debug(f'Found {len(configs)} configuration(s) to process')

            results = []
            processed_configs = []

            for config in configs:
                config_result = self._process_configuration(config, ActionType.CONFIGURE)
                results.append(config_result)
                if config_result['success']:
                    processed_configs.append(config.label)

            overall_success = all(result['success'] for result in results)

            return {
                'success': overall_success,
                'processed_configs': processed_configs,
                'results': results
            }

        except Exception as error:
            self.stdout.err(f'Configure operation failed: {error}')
            return {'success': False, 'error': str(error)}

    def scorch(self, input_path: str, **kwargs) -> Dict[str, Any]:
        """
        Remove system resources not specified in Pyro configurations.

        This is a destructive operation that removes resources not defined
        in the provided configuration files. User confirmation is required
        unless auto_confirm is True.

        Args:
            input_path: Path to Pyro file or directory containing Pyro files
            **kwargs: Additional arguments:
                - auto_confirm: Skip confirmation prompt (default: False)
                - dry_run: Preview changes without executing (default: False)

        Returns:
            Dictionary containing:
                - success: Overall operation success
                - dry_run: Whether operation was a dry run
                - resources_removed: List of removed resources
                - resources_failed: List of resources that failed to remove
                - confirmed: Whether user confirmed the operation

        Example:
            >>> engine.scorch("/path/to/config.yaml", auto_confirm=True)
            {'success': True, 'resources_removed': ['/tmp/junk', '/old_logs']}
        """
        try:
            configs = self.parser.parse(Path(input_path))
            if not configs:
                return {
                    'success': False,
                    'resources_removed': [],
                    'resources_failed': [],
                    'error': 'No valid configurations found'
                }

            auto_confirm = kwargs.get('auto_confirm', False)
            dry_run = kwargs.get('dry_run', False)

            if dry_run:
                self.stdout.info('DRY RUN: No changes will be made')

            all_removed = []
            all_failed = []

            for config in configs:
                result = self._execute_scorch_config(config, auto_confirm, dry_run)
                if result['success']:
                    all_removed.extend(result.get('resources_removed', []))
                all_failed.extend(result.get('resources_failed', []))

            return {
                'success': len(all_failed) == 0,
                'dry_run': dry_run,
                'resources_removed': all_removed,
                'resources_failed': all_failed
            }

        except Exception as error:
            self.stdout.err(f'Scorch operation failed: {error}')
            return {
                'success': False,
                'resources_removed': [],
                'resources_failed': [],
                'error': str(error)
            }

    def mount(self, input_path: str, **kwargs) -> Dict[str, Any]:
        """
        Mount resources defined in Pyro configurations.

        Sets up mounts, volumes, and other mountable resources as defined
        in the configuration files.

        Args:
            input_path: Path to Pyro file or directory containing Pyro files
            **kwargs: Additional arguments for mount operations

        Returns:
            Dictionary containing operation results

        Example:
            >>> engine.mount("/path/to/mounts.yaml")
            {'success': True, 'mounts_created': ['/data', '/logs']}
        """
        return self._execute_config_action(input_path, ActionType.MOUNT, **kwargs)

    @pysnooper.snoop()
    def validate(self, input_path: str, **kwargs) -> ValidationResult:
        """
        Validate system state against Pyro configurations.

        Compares current system state with desired state defined in
        configuration files and reports discrepancies.

        Args:
            input_path: Path to Pyro file or directory containing Pyro files
            **kwargs: Additional arguments for validation

        Returns:
            ValidationResult object containing validation details

        Example:
            >>> result = engine.validate("/path/to/configs/")
            >>> result.is_valid
            False
            >>> result.discrepancies
            [{'resource': '/etc/nginx', 'issue': 'permissions mismatch'}]
        """
        try:
            configs = self.parser.parse(Path(input_path))
            if not configs:
                self.stdout.err(f'No valid Pyro files found at: {input_path}')
                return ValidationResult(
                    is_valid=False,
                    discrepancies=[{"error": f"No valid Pyro files found at {input_path}"}],
                    summary={"total_issues": 1, "critical_issues": 1},
                )

            self.stdout.debug(f'Validating {len(configs)} configuration(s)')

            all_discrepancies = []
            all_valid = True
            total_issues = 0
            critical_issues = 0

            for config in configs:
                result = self.validator.validate_configuration(config)
                if result.discrepancies:
                    self._log_validation_discrepancies(config.label, result.discrepancies)

                all_discrepancies.extend(result.discrepancies)
                all_valid = all_valid and result.is_valid

                # Update issue counts
                config_critical = sum(
                    1 for discrepancy in result.discrepancies
                    if 'mismatch' not in str(discrepancy).lower()
                )
                config_total = len(result.discrepancies)

                critical_issues += config_critical
                total_issues += config_total

                self._log_validation_result(config.label, result.is_valid, config_critical, config_total)

            self._log_validation_summary(all_valid, critical_issues, total_issues)

            summary = {
                "total_issues": total_issues,
                "critical_issues": critical_issues,
                "is_valid": all_valid,
            }

            return ValidationResult(
                is_valid=all_valid,
                discrepancies=all_discrepancies,
                summary=summary,
                system_state=self.validator._last_result.system_state
            )

        except Exception as error:
            self.stdout.err(f"Validation failed: {error}")
            return ValidationResult(
                is_valid=False,
                discrepancies=[{"error": str(error)}],
                summary={"total_issues": 1, "critical_issues": 1},
            )

    def _process_configuration(self, config: PyroConfig, action: ActionType) -> Dict[str, Any]:
        """
        Process a single configuration for the given action.

        Args:
            config: Configuration to process
            action: Type of action to perform

        Returns:
            Dictionary with processing results
        """
        try:
            sketch = self.sketch_generator.generate_sketch(config, action)

            if len(sketch) <= 1:
                self.stdout.info(f'No actions required for {config.label}, skipping')
                return {
                    'success': True,
                    'skipped': True,
                    'config_label': config.label
                }

            success = self.flow_engine.execute_sketch(sketch, action)

            return {
                'success': success,
                'skipped': False,
                'config_label': config.label,
                'actions_executed': len(sketch)
            }

        except Exception as error:
            self.stdout.err(f"Failed to process {config.label}: {error}")
            return {
                'success': False,
                'error': str(error),
                'config_label': config.label
            }

    def _execute_scorch_config(self, config: PyroConfig, auto_confirm: bool,
                             dry_run: bool) -> Dict[str, Any]:
        """
        Execute scorch operation for a single configuration.

        Args:
            config: Configuration to scorch against
            auto_confirm: Whether to skip confirmation
            dry_run: Whether to only simulate the operation

        Returns:
            Dictionary with scorch results
        """
        try:
            sketch = self.sketch_generator.generate_scorch_sketch(config)

            if len(sketch) <= 1:
                self.stdout.info(f'Nothing to scorch for {config.label}, skipping')
                return {
                    'success': True,
                    'skipped': True,
                    'config_label': config.label
                }

            if not auto_confirm and not self._confirm_scorch(config):
                self.stdout.warn(f'Scorch cancelled for {config.label}')
                return {
                    'success': False,
                    'cancelled': True,
                    'config_label': config.label
                }

            success = self.flow_engine.execute_sketch(sketch, ActionType.SCORCH)

            return {
                'success': success,
                'config_label': config.label,
                'actions_executed': len(sketch)
            }

        except Exception as error:
            self.stdout.err(f"Scorch failed for {config.label}: {error}")
            return {
                'success': False,
                'error': str(error),
                'config_label': config.label
            }

    def _execute_config_action(self, input_path: str, action: ActionType,
                             **kwargs) -> Dict[str, Any]:
        """
        Execute a configuration action (mount, configure, etc.).

        Args:
            input_path: Path to configuration files
            action: Action type to execute
            **kwargs: Additional arguments

        Returns:
            Dictionary with operation results
        """
        try:
            configs = self.parser.parse(Path(input_path))
            if not configs:
                return {'success': False, 'error': 'No configurations found'}

            results = []
            processed_configs = []

            for config in configs:
                result = self._process_configuration(config, action)
                results.append(result)
                if result.get('success'):
                    processed_configs.append(config.label)

            overall_success = all(result.get('success', False) for result in results)

            return {
                'success': overall_success,
                'processed_configs': processed_configs,
                'results': results
            }

        except Exception as error:
            self.stdout.err(f'{action.value} operation failed: {error}')
            return {'success': False, 'error': str(error)}

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

        return response in ['y', 'yes']

    def _log_validation_discrepancies(self, config_label: str, discrepancies: List[Dict]) -> None:
        """Log validation discrepancies in a structured format."""
        self.stdout.nok(f'Validation discrepancies for Pyro config ({config_label}):\n' + json.dumps(discrepancies, indent=4))

    def _log_validation_result(self, config_label: str, is_valid: bool,
                             critical_issues: int, total_issues: int) -> None:
        """Log individual configuration validation result."""
        if is_valid:
            self.stdout.ok(f'System state matches Pyro config: ({config_label})')
        else:
            issue_text = f"{critical_issues} critical, {total_issues} total"
            self.stdout.nok(f'System state mismatch for ({config_label}) ({issue_text} issues)')

    def _log_validation_summary(self, all_valid: bool, critical_issues: int,
                              total_issues: int) -> None:
        """Log overall validation summary."""
        if critical_issues > 0:
            self.stdout.nok(f'Found {critical_issues} critical issues, {total_issues} total issues')
        elif total_issues > 0:
            self.stdout.warn(f'Found {total_issues} non-critical issues')

        if all_valid:
            self.stdout.ok('System state validation passed - no action required')
        else:
            self.stdout.nok('System state validation failed - run "configure" to apply changes')

    def _validate_config(self) -> None:
        """
        Validate engine configuration.

        Raises:
            ValueError: If configuration contains invalid values
        """
        required_paths = ['default_output_dir']
        for path_key in required_paths:
            if path_key in self.config:
                path = Path(self.config[path_key])
                if not path.parent.exists():
                    raise ValueError(f"Configuration path {path_key} parent does not exist: {path.parent}")

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get the default engine configuration.

        Returns:
            Dictionary with default configuration values
        """
        return {
            "safety_checks": True,
            "default_output_dir": "/tmp/pyroform",
            "log_level": "INFO",
            "log_timestamp": False,
            "auto_confirm": False,
            "dry_run": False,
            "debug": True,
        }

# CODE DUMP
#from .scorch_engine import ScorchEngine, ScorchResult

