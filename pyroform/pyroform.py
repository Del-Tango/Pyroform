"""
: strMain Pyroform Library Interface Class
"""
import yaml
import json

import pysnooper

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .src.models import ActionType, ValidationResult # ScorchResult
from .src.pyroform_engine import PyroformEngine
from .src.logging import STDOUTMsg, setup_logging


class Pyroform:
    """
    Main Pyroform library class for programmatic usage
    """

    # @pysnooper.snoop()
    def __init__(self, config_file: Optional[str] = None, **kwargs):
        """
        Initialize Pyroform

        Args:
            config_file: Optional path to configuration file
            auto_confirm: Whether to auto-confirm destructive operations
        """
        self.stdout = STDOUTMsg(
            debug_mode=kwargs.get('debug', False),
            timestamp=kwargs.get('log_timestamp', False),
        )
        self.config = self._load_config(config_file, **kwargs)
        self.stdout.debug(f'Pyroform conf: {self.config}')

        self.reinit_logger(**self.config)
        self.engine = PyroformEngine(config=self.config, stdout=self.stdout)
        self._config_file = str(config_file)
        self._pyro_files = []
        self._last_action = None
        self._last_result = None

    # @pysnooper.snoop()
    def reinit_logger(self, **kwargs) -> STDOUTMsg:
        setup_logging(
            log_file=Path(self.config.get('log_file') or  './pyroform.log'),
            debug=self.config.get('debug', False),
            config=self.config
        )
        self.stdout = STDOUTMsg(
            debug_mode=kwargs.get('debug', False),
            timestamp=kwargs.get('log_timestamp', False),
        )
        return self.stdout

    # @pysnooper.snoop()
    def snapshot(self, input_path: str | None = None, output_path: str | None = None, **kwargs) -> bool:
        start_time = datetime.now().isoformat()
        self._pyro_files.append(input_path)
        self._last_action = ActionType.SNAPSHOT
        self._last_result = self.engine.snapshot(output_path, **kwargs)
        end_time = datetime.now().isoformat()
        if self.config.get('report'):
            self.generate_report(
                'report_' + str(self.config.get('output_path', str(ActionType.SNAPSHOT) + '.json')),
                start_time=start_time,
                end_time=end_time,
            )
        return self._last_result

    # @pysnooper.snoop()
    def configure(self, input_path: str, **kwargs) -> bool:
        """
        Configure system according to Pyro file(s)

        Args:
            input_path: Path to Pyro file or directory
            **kwargs: Additional arguments (dry_run, verbose, output_dir, etc.)

        Returns:
            True if successful, False otherwise
        """
        start_time = datetime.now().isoformat()
        self._pyro_files.append(input_path)
        self._last_action = ActionType.CONFIGURE
        self._last_result = self.engine.configure(input_path, **kwargs)
        end_time = datetime.now().isoformat()
        if self.config.get('report'):
            self.generate_report(
                'report_' + str(self.config.get('output_path', str(ActionType.CONFIGURE) + '.json')),
                start_time=start_time,
                end_time=end_time,
            )
        return self._last_result

    # @pysnooper.snoop()
    def scorch(self, input_path: str, **kwargs) -> dict:
        """
        Remove system resources not specified in Pyro file(s)

        Args:
            input_path: Path to Pyro file or directory
            **kwargs: Additional arguments (dry_run, verbose, output_dir, etc.)

        Returns:
            Dictionary object
        """
        start_time = datetime.now().isoformat()
        self._pyro_files.append(input_path)
        self._last_action = ActionType.SCORCH
        self._last_result = self.engine.scorch(input_path, **kwargs)

        self.stdout.debug(
            f'Last result: {self._last_result}'
        )

        end_time = datetime.now().isoformat()
        if self.config.get('report'):
            self.generate_report(
                'report_' + str(self.config.get('output_path', str(ActionType.SCORCH) + '.json')),
                start_time=start_time,
                end_time=end_time,
            )
        return self._last_result

    # @pysnooper.snoop()
    def mount(self, input_path: str, **kwargs) -> bool:
        """
        Mount devices according to Pyro file(s)

        Args:
            input_path: Path to Pyro file or directory
            **kwargs: Additional arguments (dry_run, verbose, output_dir, etc.)

        Returns:
            True if successful, False otherwise
        """
        start_time = datetime.now().isoformat()
        self._pyro_files.append(input_path)
        self._last_action = ActionType.MOUNT
        self._last_result = self.engine.mount(input_path, **kwargs)
        end_time = datetime.now().isoformat()
        if self.config.get('report'):
            self.generate_report(
                'report_' + str(self.config.get('output_path', str(ActionType.MOUNT) + '.json')),
                start_time=start_time,
                end_time=end_time,
            )
        return self._last_result

    # @pysnooper.snoop()
    def validate(self, input_path: str, **kwargs) -> dict:
        """
        Validate system against Pyro file(s)

        Args:
            input_path: Path to Pyro file or directory
            **kwargs: Additional arguments (verbose, output_dir, etc.)

        Returns:
            Dictionary object
        """
        start_time = datetime.now().isoformat()
        self._pyro_files.append(input_path)
        self._last_action = ActionType.VALIDATE
        self._last_result = self.engine.validate(input_path, **kwargs)
        end_time = datetime.now().isoformat()
        if self.config.get('report'):
            self.generate_report(
                'report_' + str(self.config.get('output_path', str(ActionType.VALIDATE) + '.json')),
                start_time=start_time,
                end_time=end_time,
            )
        return self._last_result

    # TODO
    # @pysnooper.snoop()
    def generate_report(self, output_path: Optional[str] = None, **kwargs) -> bool:
        """
        Generate report for the last action

        Args:
            output_path: Optional path to save report

        Returns:
            True if successful, False otherwise
        """
        if self._last_action is None or self._last_result is None:
            self.stdout.warn("No action has been executed yet")
            return False

        try:
            report = self.engine.reporter.generate_action_report(
                action=self._last_action.value,
                result=self._last_result,
                config_files=[self._config_file] + self._pyro_files,  # Would need to track this
                start_time=kwargs.get('start_time', datetime.now().isoformat()),
                end_time=kwargs.get('end_time', datetime.now().isoformat()),
                auto_confirm=self.config.get('auto_confirm', False),
            )

            self.stdout.custom('REPORT', json.dumps(report, indent=2))

            if output_path:
                return self.engine.reporter.save_report(report, Path(output_path))

            return True

        except Exception as e:
            self.stdout.err(f"Failed to generate report! Details: {e}")
            return False

    # @pysnooper.snoop()
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
            action = step.get('action')
            input_path = step.get('input_path')
            output_path = step.get('output_path')
            dry_run = step.get('dry_run', False)
            auto_confirm = step.get('auto_confirm') or self.config.get('auto_confirm')

            if not action or not input_path:
                self.stdout.err(f'Invalid workflow step: {step}')
                return False

            self.stdout.info(f'Executing workflow step: {action} with {input_path}')

            try:
                if action == 'validate':
                    result = self.validate(input_path, dry_run=dry_run)
                    success = result.is_valid
                elif action == 'configure':
                    result = self.configure(input_path, dry_run=dry_run)
                    success = result.get('success', False)
                elif action == 'mount':
                    result = self.mount(input_path, dry_run=dry_run)
                    success = result.get('success', False)
                elif action == 'scorch':
                    result = self.scorch(input_path, dry_run=dry_run)
                    success = result.get('success', False)
                elif action == 'snapshot':
                    result = self.snapshot(input_path, output_path)
                    success = result.get('success', False)
                else:
                    self.stdout.err(f'Unknown action in workflow: {action}')
                    return False

                workflow_results.append(
                    {
                        'action': action,
                        'input_path': input_path,
                        'success': success,
                        'result': result,
                    }
                )
                if not success:
                    if auto_confirm:
                        continue
                    print(f'[ WARNING ]: Previous step execution was not successful!')
                    print()
                    response = input('Continue with next workflow step? [Y/N]> ').strip().lower()
                    print()
                    if response.lower() not in ('n', 'no', 'nope', 'fuck no', 'fuck that'):
                        continue
                    return False

            except Exception as e:
                self.stdout.err(f"Error in workflow step {action}: {e}")
                return False

        # Store workflow results
        self._workflow_results = workflow_results

        # Generate workflow report
        if self.config.get("report", False):
            if os.path.isdir(output_path):
                report_file = output_path + "/pyroform_workflow.report.json"
            else:
                report_file = output_path
            self._generate_workflow_report(workflow_results, report_file)

        print(f"[ OK ]: Workflow completed successfully")
        return True

    # @pysnooper.snoop()
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
                'type': 'workflow',
                'timestamp': datetime.now().isoformat(),
                'total_steps': len(workflow_results),
                'successful_steps': len([r for r in workflow_results if r['success']]),
                'failed_steps': len([r for r in workflow_results if not r['success']]),
                'steps': workflow_results,
                'summary': self._generate_workflow_summary(workflow_results),
            }

            return self.engine.reporter.save_report(workflow_report, Path(output_path))

        except Exception as e:
            self.stdout.err(f'Failed to generate workflow report: {e}')
            return False

    # @pysnooper.snoop()
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

    # @pysnooper.snoop()
    def _load_config(self, config_file: Optional[str], **kwargs) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults

        Args:
            config_file: Optional path to configuration file

        Returns:
            Configuration dictionary
        """
        default_config = {
            'input_path': kwargs.get('input_path'),
            'output_path': kwargs.get('output_path'),
            'log_level': kwargs.get('log_level', 'INFO'),
            'log_timestamp': kwargs.get('log_timestamp', False),
            'log_file': kwargs.get('log_file', './pyroform.log'),
            'auto_confirm': kwargs.get('auto_confirm', False),
            'dry_run': kwargs.get('dry_run', False),
            'debug':  kwargs.get('debug', False),
            'cleanup': kwargs.get('cleanup', False),
            'report': kwargs.get('report', False),
        }
        self.stdout.debug(f'Default config: {default_config}')

        if not config_file:
            self.stdout.debug('No config file specified. Using defaults.')
            return default_config

        config_path = Path(config_file)
        if not config_path.exists():
            self.stdout.warn(f"Config file ({config_file}) not found!  Using defaults.")
            return default_config

        try:
            if config_path.suffix.lower() in [".yaml", ".yml"]:
                with open(config_path, "r") as f:
                    file_config = yaml.safe_load(f)
            elif config_path.suffix.lower() == ".json":
                with open(config_path, "r") as f:
                    file_config = json.load(f)
            else:
                self.stdout.warn(f"Unsupported config file format! Details: {config_path.suffix}")
                return default_config

            # Merge with defaults

            merged_config = {**default_config, **file_config}
            self.stdout.debug(f'Config merged with defaults: {merged_config}')
            return merged_config

        except Exception as e:
            self.stdout.err(f"Error loading config file {config_file}! Details: {e}")
            self.stdout.warn('Using defaults.')
            return default_config

    @property
    def version(self) -> str:
        """Get Pyroform version"""
        from . import __version__
        self.stdout.debug('Pyroform version: {__version__}')
        return __version__

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()

    def set_config(self, **kwargs) -> None:
        """Update configuration"""
        self.config.update(kwargs)


# CODE DUMP

