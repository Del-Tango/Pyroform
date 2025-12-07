"""
Report Generation for Pyroform
"""

import json
import yaml

# import pysnooper

from datetime import datetime, timedelta
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any, List, Optional

from .logging import STDOUTMsg


# @pysnooper.snoop()
class ReportGenerator:
    """
    Generates comprehensive reports for Pyroform actions
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        stdout: STDOUTMsg | None = None,
        **kwargs,
    ) -> None:
        self.config = config or {}
        self.stdout = stdout or STDOUTMsg(
            debug_mode=kwargs.get("debug", self.config.get("debug", False)),
            timestamp=kwargs.get(
                "log_timestamp", self.config.get("log_timestamp", False)
            ),
        )

        self.stdout.debug(f"Reporter conf: {self.config}")

    # @pysnooper.snoop()
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
            "duration": self.seconds_to_hms_timedelta(
                str(duration_seconds)
            ),  # Add duration field for test compatibility
            "duration_seconds": duration_seconds,
            "config_files": config_files,
        }
        report.update(asdict(result))

        self.stdout.debug(f"Base Report Structure: {report}")

        return report

    # @pysnooper.snoop()
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
