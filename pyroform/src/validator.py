"""
System Validation for Pyroform
"""

import subprocess
import json
import pysnooper

from dataclasses import dataclass
from typing import List, Dict, Any
from pathlib import Path

from .models import PyroConfig
from .logging import STDOUTMsg
from .scanner import get_system_state
from .difference import compare_system_state_with_pyro_file


@dataclass
class ValidationResult:
    """Result of system validation"""

    is_valid: bool
    discrepancies: List[Dict[str, Any]]
    summary: Dict[str, Any]


class SystemValidator:
    """
    Validates current system state against desired Pyro configuration
    """

    @pysnooper.snoop()
    def __init__(self, stdout: STDOUTMsg | None = None, config: dict | None = None) -> None:
        self._last_result: ValidationResult = None
        self.config = config or {}
        self.stdout = stdout or STDOUTMsg(
            debug_mode=self.config.get('debug', False),
            timestamp=self.config.get('log_timestamp') or self.config.get('debug', False),
        )

    # TODO - Refactor - use scanner and difference
    @pysnooper.snoop()
    def validate_configuration(self, config: PyroConfig) -> ValidationResult:
        """
        Compare current system state with desired configuration

        Args:
            config: Desired Pyro configuration

        Returns:
            ValidationResult with discrepancies and summary
        """

        # TODO - Move to validator and use in sketch generator from here
#       system_state = get_system_state(
#           pyro_config=config, max_depth=100, include_hidden=True
#       )
#       compared = compare_system_state_with_pyro_file(system_state, config)


        # TODO - DEPRECATED 2 down
        current_state = self._get_current_system_state()
        discrepancies = self._compare_states(config, current_state)

        self.stdout.debug('Current State: ' + json.dumps(current_state, indent=4))
        self.stdout.debug('Discrepancies: ' + json.dumps(discrepancies, indent=4))

        # Calculate summary
        critical_issues = len([d for d in discrepancies if d.get("critical", False)])
        total_issues = len(discrepancies)

        summary = {
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "is_valid": total_issues == 0,
        }

        self._last_result = ValidationResult(
            is_valid=summary["is_valid"], discrepancies=discrepancies, summary=summary
        )

        return self._last_result

    @pysnooper.snoop()
    def get_validation_report(self) -> Dict[str, Any]:
        """
        Generate detailed validation report

        Returns:
            Comprehensive validation report
        """
        if self._last_result is None:
            return {
                "summary": {"total_checks": 0, "passed": 0, "failed": 0, "warnings": 0},
                "discrepancies": [],
                "timestamp": self._get_timestamp(),
            }

        # Use the last validation result
        discrepancies = self._last_result.discrepancies
        total_checks = len(discrepancies)
        failed = len(discrepancies)
        passed = (
            total_checks - failed
        )  # This is simplified - in reality we'd count actual checks
        warnings = len([d for d in discrepancies if not d.get("critical", False)])

        return {
            "summary": {
                "total_checks": total_checks,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "total_issues": self._last_result.summary.get("total_issues", 0),
                "critical_issues": self._last_result.summary.get("critical_issues", 0),
            },
            "discrepancies": discrepancies,
            "timestamp": self._get_timestamp(),
            "is_valid": self._last_result.is_valid,
        }

    @pysnooper.snoop()
    def _get_current_system_state(self) -> Dict[str, Any]:
        """
        Get current system state

        Returns:
            Dictionary containing current system state
        """
        return {
            "users": self._get_current_users(),
            "groups": self._get_current_groups(),
            "mounts": self._get_current_mounts(),
            "files": self._get_current_file_state(),
        }

    @pysnooper.snoop()
    def _get_current_users(self) -> List[str]:
        """Get list of current system users"""
        try:
            result = subprocess.run(
                ["getent", "passwd"], capture_output=True, text=True, check=True
            )
            users = []
            for line in result.stdout.splitlines():
                if ":" in line:
                    users.append(line.split(":")[0])
            return users
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

    @pysnooper.snoop()
    def _get_current_groups(self) -> List[str]:
        """Get list of current system groups"""
        try:
            result = subprocess.run(
                ["getent", "group"], capture_output=True, text=True, check=True
            )
            groups = []
            for line in result.stdout.splitlines():
                if ":" in line:
                    groups.append(line.split(":")[0])
            return groups
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

    @pysnooper.snoop()
    def _get_current_mounts(self) -> Dict[str, str]:
        """Get current mount points"""
        try:
            result = subprocess.run(
                ["mount"], capture_output=True, text=True, check=True
            )
            mounts = {}
            for line in result.stdout.splitlines():
                if " on " in line and " type " in line:
                    parts = line.split(" on ")
                    if len(parts) >= 2:
                        device = parts[0].split()[-1]  # Get the device part
                        mountpoint = parts[1].split(" type ")[0]
                        mounts[device] = mountpoint
            return mounts
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {}

    # TODO - Move implementation from scanner
    @pysnooper.snoop()
    def _get_current_file_state(self) -> Dict[str, Dict[str, str]]:
        """
        Get current file and directory states

        Returns:
            Dictionary mapping paths to their ownership and permissions
        """
        # This is a simplified implementation
        # In a real system, we'd need to traverse directories and check permissions
        file_state = {}

        # Check some common directories
        common_paths = ["/home", "/etc", "/var", "/opt", "/mnt"]

        for base_path in common_paths:
            if Path(base_path).exists():
                try:
                    stat_result = subprocess.run(
                        ["stat", "-c", "%U:%G %a", base_path],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    owner_group, perms = stat_result.stdout.strip().split()
                    file_state[base_path] = {
                        "owner": owner_group.split(":")[0],
                        "group": owner_group.split(":")[1],
                        "perms": perms,
                    }
                except (subprocess.CalledProcessError, IndexError):
                    continue

        return file_state

    # TODO - REFACTOR - Import differences from .difference
    @pysnooper.snoop()
    def _compare_states(
        self, config: PyroConfig, current_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Compare desired configuration with current state

        Args:
            config: Desired configuration
            current_state: Current system state

        Returns:
            List of discrepancies
        """
        discrepancies = []

        # Check users
        desired_users = {user.name for user in config.users}
        current_users = set(current_state.get("users", []))

        for user in config.users:
            if user.name not in current_users:
                discrepancies.append(
                    {
                        "type": "user",
                        "name": user.name,
                        "issue": "User does not exist",
                        "critical": True,
                    }
                )

        # Check groups
        desired_groups = {group.name for group in config.groups}
        current_groups = set(current_state.get("groups", []))

        for group in config.groups:
            if group.name not in current_groups:
                discrepancies.append(
                    {
                        "type": "group",
                        "name": group.name,
                        "issue": "Group does not exist",
                        "critical": True,
                    }
                )

        # Check mounts - only if we have devices to check
        current_mounts = current_state.get("mounts", {})
        for device in config.devices:
            if device.path not in current_mounts:
                discrepancies.append(
                    {
                        "type": "mount",
                        "device": device.path,
                        "mountpoint": device.mountpoint,
                        "issue": "Device not mounted",
                        "critical": False,
                    }
                )
            elif current_mounts.get(device.path) != device.mountpoint:
                discrepancies.append(
                    {
                        "type": "mount",
                        "device": device.path,
                        "expected_mountpoint": device.mountpoint,
                        "actual_mountpoint": current_mounts[device.path],
                        "issue": "Device mounted at wrong location",
                        "critical": False,
                    }
                )

        # Check file and directory states from device configurations
        current_files = current_state.get("files", {})
        for device in config.devices:
            for state_entry in device.state:
                state_parts = state_entry.split(",")
                if len(state_parts) >= 5:
                    obj_type, path, expected_owner, expected_group, expected_perms = (
                        state_parts[:5]
                    )

                    if path not in current_files:
                        discrepancies.append(
                            {
                                "type": obj_type,
                                "path": path,
                                "issue": f"{obj_type.capitalize()} does not exist",
                                "critical": obj_type
                                == "dir",  # Missing dir is critical, missing file is not
                            }
                        )
                    else:
                        current_info = current_files[path]
                        if current_info["owner"] != expected_owner:
                            discrepancies.append(
                                {
                                    "type": "ownership",
                                    "path": path,
                                    "expected_owner": expected_owner,
                                    "actual_owner": current_info["owner"],
                                    "issue": "Incorrect owner",
                                    "critical": False,
                                }
                            )

                        if current_info["group"] != expected_group:
                            discrepancies.append(
                                {
                                    "type": "group_ownership",
                                    "path": path,
                                    "expected_group": expected_group,
                                    "actual_group": current_info["group"],
                                    "issue": "Incorrect group",
                                    "critical": False,
                                }
                            )

                        if current_info["perms"] != expected_perms:
                            discrepancies.append(
                                {
                                    "type": "permissions",
                                    "path": path,
                                    "expected_perms": expected_perms,
                                    "actual_perms": current_info["perms"],
                                    "issue": "Incorrect permissions",
                                    "critical": False,
                                }
                            )

        return discrepancies

    def _get_timestamp(self) -> str:
        """Get current timestamp for reports"""
        from datetime import datetime

        return datetime.now().isoformat()


# CODE DUMP

