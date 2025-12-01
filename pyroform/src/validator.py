"""
System Validation Module for Pyroform

Provides comprehensive system state validation against Pyro configuration files.
Validates users, groups, filesystem permissions, mount points, and device configurations.

Author: Pyroform Team
Version: 1.0.0
"""
import json
import os
import pwd
import grp
import stat
import subprocess

import pysnooper

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Set, Optional, Tuple

from .models import (
    PyroConfig, User, Group, Device, Exclude, ValidationResult, FileSystemEntry,
    SystemUser, SystemGroup, MountedDevice, ValidationSummary
)
from .scanner import SystemStateScanner
from .comparator import SystemStateComparator
from .logging import STDOUTMsg


class SystemValidator:
    """
    Main system validation orchestrator.

    Coordinates system state scanning and comparison to validate
    current system state against desired Pyro configuration.
    """

    def __init__(self, stdout: STDOUTMsg | None = None, config: dict | None = None) -> None:
        """
        Initialize SystemValidator.

        Args:
            stdout: STDOUTMsg instance for logging
            config: Configuration dictionary
        """
        self._last_result: Optional[ValidationResult] = None
        self.config = config or {}
        self.stdout = stdout or STDOUTMsg(
            debug_mode=self.config.get('debug', False),
            timestamp=self.config.get('log_timestamp') or self.config.get('debug', False),
        )

        self.scanner = SystemStateScanner(self.stdout)
        self.comparator = SystemStateComparator(self.stdout)

#   @pysnooper.snoop()
    def validate_configuration(self, config: PyroConfig) -> ValidationResult:
        """
        Compare current system state with desired configuration.

        Args:
            config: Desired Pyro configuration

        Returns:
            ValidationResult with discrepancies and summary
        """
        current_state = self.scanner.scan_system_state(
            pyro_config=config, max_depth=100, include_hidden=True
        )

        differences = self.comparator.compare_states(current_state, config)

#       critical_issues = sum(len(item) for item in differences.values() if 'mismatch' not in item)
#       total_issues = sum(len(item) for item in differences.values())

        critical_issues = sum([len(v) for k, v in differences.items() if 'mismatch' not in str(k).lower()])
        total_issues = sum([len(v) for k, v in differences.items() ])

        summary = {
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "is_valid": total_issues == 0,
        }

        self.stdout.debug(f'Summary: {json.dumps(summary, indent=4)}')

        self._last_result = ValidationResult(
            is_valid=summary["is_valid"],
            discrepancies=differences,
            system_state=current_state,
            summary=summary
        )

        return self._last_result

    def get_validation_report(self) -> Dict[str, Any]:
        """
        Generate detailed validation report.

        Returns:
            Comprehensive validation report with summary and discrepancies
        """
        if self._last_result is None:
            return self._create_empty_report()

        return self._create_report_from_result()

    def _create_empty_report(self) -> Dict[str, Any]:
        """Create an empty validation report."""
        return {
            "summary": {
                "total_checks": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0,
                "total_issues": 0,
                "critical_issues": 0,
                "is_valid": True
            },
            "discrepancies": [],
            "timestamp": self._get_timestamp(),
            "is_valid": True,
        }

    def _create_report_from_result(self) -> Dict[str, Any]:
        """Create validation report from the last result."""
        discrepancies = self._last_result.discrepancies
        total_checks = len(discrepancies)
        failed = len(discrepancies)
        passed = total_checks - failed  # Simplified calculation
        warnings = len([d for d in discrepancies if not d.get("critical", False)])

        return {
            "summary": {
                "total_checks": total_checks,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "total_issues": self._last_result.summary.get("total_issues", 0),
                "critical_issues": self._last_result.summary.get("critical_issues", 0),
                "is_valid": self._last_result.is_valid,
            },
            "discrepancies": discrepancies,
            "timestamp": self._get_timestamp(),
            "is_valid": self._last_result.is_valid,
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp for reports."""
        from datetime import datetime
        return datetime.now().isoformat()


# CODE DUMP

