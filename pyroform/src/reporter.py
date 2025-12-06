"""
Report Generation for Pyroform
"""
import json
import yaml
import pysnooper

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from .logging import STDOUTMsg


# TODO
@pysnooper.snoop()
class ReportGenerator:
    """
    Generates comprehensive reports for Pyroform actions
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, stdout: STDOUTMsg | None = None, **kwargs) -> None:
        self.config = config or {}
        self.stdout = stdout or STDOUTMsg(
            debug_mode=kwargs.get('debug', self.config.get('debug', False)),
            timestamp=kwargs.get('log_timestamp', self.config.get('log_timestamp', False)),
        )

        self.stdout.debug(f'Reporter conf: {self.config}')

    @pysnooper.snoop()
    def generate_action_report(
        self,
        action: str,
        result: Any,
        config_files: List[str],
        start_time: str,
        end_time: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate detailed action report
        """
        # Calculate duration
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            duration_seconds = (end_dt - start_dt).total_seconds()
        except (ValueError, TypeError):
            duration_seconds = 0

        # Base report structure
        report = {
            "action": action,
            "timestamp": end_time,
            "start_time": start_time,
            "end_time": end_time,
            "duration": self.seconds_to_hms_timedelta(str(duration_seconds)),  # Add duration field for test compatibility
            "duration_seconds": duration_seconds,
            "config_files": config_files,
            "success": getattr(result, "success", False),
            "summary": self._generate_summary(action, result),
            "details": self._generate_details(action, result),
            "metadata": kwargs,
        }

        self.stdout.debug(f'Base Report Structure: {report}')

        return report

    # TODO
    @pysnooper.snoop()
    def _generate_summary(self, action: str, result: Any) -> Dict[str, Any]:
        """
        Generate summary section of report
        """
        summary = {
            "action": action,
            "status": "success" if getattr(result, "success", False) else "failed",
            "timestamp": datetime.now().isoformat(),
            "errors": len(getattr(result, "errors", [])),
        }

        # Action-specific summary fields
        if hasattr(result, "__class__") and result.__class__.__name__ == "ScorchResult":
            summary.update(
                {
                    "resources_removed": len(getattr(result, "resources_removed", [])),
                    "resources_failed": len(getattr(result, "resources_failed", [])),
                    "dry_run": getattr(result, "dry_run", False),
                }
            )
        elif hasattr(result, "__class__") and result.__class__.__name__ == "ValidationResult":
            summary.update(
                {
                    "is_valid": getattr(result, "is_valid", False),
                    "total_issues": getattr(result, "summary", {}).get(
                        "total_issues", 0
                    ),
                    "critical_issues": getattr(result, "summary", {}).get(
                        "critical_issues", 0
                    ),
                }
            )
        elif hasattr(result, "__class__") and result.__class__.__name__ == "ConfigureResult":
            pass
        elif hasattr(result, "__class__") and result.__class__.__name__ == "MountResult":
            pass
        elif hasattr(result, "__class__") and result.__class__.__name__ == "SnapshotResult":
            pass
        else:
            # Generic result handling
            summary.update(
                {
                    "execution_time": getattr(result, "execution_time", 0),
                    "resources_processed": getattr(result, "resources_processed", 0),
                    "errors": len(getattr(result, "errors", [])),
                }
            )

        self.stdout.debug(f'Action report summary: {summary}')

        return summary

    # TODO
    @pysnooper.snoop()
    def _generate_details(self, action: str, result: Any) -> Dict[str, Any]:
        """
        Generate details section of report
        """
        details = {}

        if hasattr(result, "__class__") and result.__class__.__name__ == "ScorchResult":
            details_found = getattr(result, "details", {})
            if details_found:
                details.update({k: v for k, v in details_found.items() if v})
            details.update({"errors": getattr(result, "errors", {}),})
        elif (
            hasattr(result, "__class__")
            and result.__class__.__name__ == "ValidationResult"
        ):
            details.update(
                {
                    "discrepancies": getattr(result, "discrepancies", []),
                    "summary": getattr(result, "summary", {}),
                }
            )
        else:
            # Generic result handling
            details.update(
                {
                    "execution_time": getattr(result, "execution_time", 0),
                    "resources_processed": getattr(result, "resources_processed", 0),
                    "errors": getattr(result, "errors", []),
                }
            )

        self.stdout.debug(f'Action report details: {details}')

        return details

    @pysnooper.snoop()
    def save_report(
        self, report: Dict[str, Any], output_path: Path, format: str = "json"
    ) -> bool:
        """
        Save report to file
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if format.lower() == "yaml":
                with open(output_path, "w") as f:
                    yaml.dump(report, f, default_flow_style=False)
            else:  # Default to JSON
                with open(output_path, "w") as f:
                    json.dump(report, f, indent=2)

            return True

        except (IOError, TypeError, yaml.YAMLError) as e:
            self.stdout.err(f"Could not save report to {output_path}! Details: {e}")
            return False

    @pysnooper.snoop()
    def generate_combined_report(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a combined report from multiple action reports
        """
        combined = {
            "type": "combined",
            "timestamp": datetime.now().isoformat(),
            "total_actions": len(reports),
            "successful_actions": len([r for r in reports if r.get("success", False)]),
            "failed_actions": len([r for r in reports if not r.get("success", False)]),
            "actions": reports,
            "summary": self._generate_combined_summary(reports),
        }

        return combined

    @pysnooper.snoop()
    def _generate_combined_summary(
        self, reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate summary for combined report

        Args:
            reports: List of action reports

        Returns:
            Combined summary dictionary
        """
        total_duration = sum(r.get("duration_seconds", 0) for r in reports)

        return {
            "total_duration_seconds": total_duration,
            "actions_performed": [r.get("action", "unknown") for r in reports],
            "overall_success": all(r.get("success", False) for r in reports),
        }

    def seconds_to_hms_timedelta(self, seconds_str: str) -> str:
        try:
            seconds = float(seconds_str)
            td = timedelta(seconds=seconds)

            # Extract components
            total_seconds = td.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds_remainder = total_seconds % 60

            return f"{hours:02d}:{minutes:02d}:{seconds_remainder:06.3f}"
        except ValueError:
            return "Invalid input"

# CODE DUMP


    # TODO - ? Required ?
    @pysnooper.snoop()
    def generate_validation_report(self, validation_result: Any) -> Dict[str, Any]:
        """
        Generate validation-specific report

        Args:
            validation_result: ValidationResult object

        Returns:
            Validation report dictionary
        """
        report = {
            "type": "validation",
            "timestamp": datetime.now().isoformat(),
            "is_valid": getattr(validation_result, "is_valid", False),
            "summary": getattr(validation_result, "summary", {}),
            "discrepancies": getattr(validation_result, "discrepancies", []),
            "total_checks": len(getattr(validation_result, "discrepancies", [])),
            "passed": 0,  # Will be calculated
            "failed": 0,  # Will be calculated
            "warnings": 0,  # Will be calculated
        }

        # Calculate metrics
        discrepancies = report["discrepancies"]
        report["failed"] = len(discrepancies)
        report["passed"] = report["total_checks"] - report["failed"]
        report["warnings"] = len(
            [d for d in discrepancies if not d.get("critical", False)]
        )

        return report

