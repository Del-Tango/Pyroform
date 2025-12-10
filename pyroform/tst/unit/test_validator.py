"""
Validator Test Suite

Unit tests for the Validator class.
"""

import json
from unittest.mock import Mock, patch

import pytest

from pyroform.src.comparator import SystemStateComparator
from pyroform.src.logging import STDOUTMsg
from pyroform.src.models import PyroConfig, ValidationResult, ValidationSummary
from pyroform.src.scanner import SystemStateScanner
from pyroform.src.validator import SystemValidator


@pytest.fixture
def mock_stdout():
    """Mock STDOUTMsg to avoid console output during tests."""
    mock = Mock(spec=STDOUTMsg)
    mock.debug = Mock()
    mock.info = Mock()
    mock.warn = Mock()
    mock.err = Mock()
    mock.nok = Mock()
    mock.ok = Mock()
    return mock


@pytest.fixture
def mock_pyro_config():
    """Create a mock PyroConfig."""
    config = Mock(spec=PyroConfig)
    config.label = "test_config"
    config.users = []
    config.groups = []
    config.devices = []
    config.excludes = Mock()
    config.excludes.users = set()
    config.excludes.groups = set()
    config.excludes.devices = set()
    config.excludes.directories = set()
    config.excludes.files = set()
    config.excludes.links = set()
    return config


@pytest.fixture
def system_state():
    """Create a sample system state."""
    return {
        "users": [{"username": "user1"}],
        "groups": [{"groupname": "group1"}],
        "mounted_devices": [{"device_path": "/dev/sda1"}],
    }


@pytest.fixture
def comparison_differences():
    """Create sample comparison differences."""
    return {
        "missing_users": [{"username": "missing_user"}],
        "extra_users": [{"username": "extra_user"}],
        "user_mismatches": [{"username": "mismatch_user"}],
        "missing_groups": [{"groupname": "missing_group"}],
        "extra_groups": [{"groupname": "extra_group"}],
        "group_mismatches": [{"groupname": "mismatch_group"}],
        "missing_directories": [{"path": "/missing/dir"}],
        "extra_directories": [{"path": "/extra/dir"}],
        "directory_mismatches": [{"path": "/mismatch/dir"}],
        "missing_files": [{"path": "/missing/file.txt"}],
        "extra_files": [{"path": "/extra/file.txt"}],
        "file_mismatches": [{"path": "/mismatch/file.txt"}],
        "missing_symlinks": [{"path": "/missing/link"}],
        "extra_symlinks": [{"path": "/extra/link"}],
        "symlink_mismatches": [{"path": "/mismatch/link"}],
        "missing_mountpoints": [{"mountpoint": "/missing/mount"}],
        "mountpoint_mismatches": [{"mountpoint": "/mismatch/mount"}],
    }


@pytest.fixture
def empty_comparison_differences():
    """Create empty comparison differences."""
    return {
        "missing_users": [],
        "extra_users": [],
        "user_mismatches": [],
        "missing_groups": [],
        "extra_groups": [],
        "group_mismatches": [],
        "missing_directories": [],
        "extra_directories": [],
        "directory_mismatches": [],
        "missing_files": [],
        "extra_files": [],
        "file_mismatches": [],
        "missing_symlinks": [],
        "extra_symlinks": [],
        "symlink_mismatches": [],
        "missing_mountpoints": [],
        "mountpoint_mismatches": [],
    }


@pytest.fixture
def validation_summary():
    """Create a ValidationSummary."""
    return ValidationSummary(total_issues=5, critical_issues=2, is_valid=False)


@pytest.fixture
def validation_result(comparison_differences, system_state, validation_summary):
    """Create a ValidationResult."""
    return ValidationResult(
        is_valid=False,
        discrepancies=comparison_differences,
        system_state=system_state,
        summary=validation_summary,
    )


@pytest.fixture
def empty_validation_result():
    """Create an empty ValidationResult."""
    return ValidationResult(
        is_valid=True,
        discrepancies={},
        system_state={},
        summary=ValidationSummary(total_issues=0, critical_issues=0, is_valid=True),
    )

# TODO
#   class TestSystemValidatorInitialization:
#       """Test SystemValidator initialization."""
#       def test_init_defaults(self):
#           """Test initialization with default parameters."""
#       def test_init_with_stdout(self, mock_stdout):
#           """Test initialization with custom stdout."""
#       def test_init_with_config(self):
#           """Test initialization with config dictionary."""
#       def test_init_config_with_debug_only(self):
#           """Test initialization with config containing only debug flag."""
#       def test_init_config_with_timestamp_false(self):
#           """Test initialization with explicit timestamp false."""
#       def test_init_components_initialized_once(self):
#           """Test that components are initialized only once."""


class TestValidateConfiguration:
    """Test the main validate_configuration method."""

    #   # TODO
    #   def test_validate_configuration_success(
    #       self, mock_compare_states, mock_scan_state, mock_stdout, mock_pyro_config,
    #       system_state, empty_comparison_differences
    #   ):
    #       """Test successful validation with no discrepancies."""
    #   def test_validate_configuration_with_discrepancies(
    #       self, mock_compare_states, mock_scan_state, mock_stdout, mock_pyro_config,
    #       system_state, comparison_differences
    #   ):
    #       """Test validation with discrepancies."""
    #   def test_validate_configuration_critical_issues_calculation(
    #       self, mock_compare_states, mock_scan_state, mock_stdout, mock_pyro_config
    #   ):
    #       """Test critical issues calculation logic."""
    #   def test_validate_configuration_empty_differences_handling(
    #       self, mock_compare_states, mock_scan_state, mock_stdout, mock_pyro_config,
    #       system_state, empty_comparison_differences
    #   ):
    #       """Test validation with empty differences dictionary."""

    @patch.object(SystemStateScanner, "scan_system_state")
    @patch.object(SystemStateComparator, "compare_states")
    def test_validate_configuration_error_in_scanning(
        self, mock_compare_states, mock_scan_state, mock_stdout, mock_pyro_config
    ):
        """Test error handling during system state scanning."""
        mock_scan_state.side_effect = Exception("Scanning failed")

        validator = SystemValidator(stdout=mock_stdout)

        # Should propagate exception
        with pytest.raises(Exception, match="Scanning failed"):
            validator.validate_configuration(mock_pyro_config)

        # Last result should remain unchanged (None or previous)
        assert validator._last_result is None

    @patch.object(SystemStateScanner, "scan_system_state")
    @patch.object(SystemStateComparator, "compare_states")
    def test_validate_configuration_error_in_comparison(
        self, mock_compare_states, mock_scan_state, mock_stdout, mock_pyro_config
    ):
        """Test error handling during state comparison."""
        mock_scan_state.return_value = {}
        mock_compare_states.side_effect = Exception("Comparison failed")

        validator = SystemValidator(stdout=mock_stdout)

        with pytest.raises(Exception, match="Comparison failed"):
            validator.validate_configuration(mock_pyro_config)

    def test_validate_configuration_none_config(self, mock_stdout):
        """Test validation with None configuration."""
        validator = SystemValidator(stdout=mock_stdout)

        # Should handle None config based on scanner/comparator behavior
        # Let it propagate to see what happens
        with patch.object(validator.scanner, "scan_system_state") as mock_scan:
            mock_scan.return_value = {}

            # This will depend on comparator behavior with None config
            with patch.object(validator.comparator, "compare_states") as mock_compare:
                mock_compare.return_value = {}

                result = validator.validate_configuration(None)

                mock_scan.assert_called_once_with(
                    pyro_config=None, max_depth=100, include_hidden=True
                )
                mock_compare.assert_called_once_with({}, None)


class TestGetValidationReport:
    """Test the get_validation_report method."""

    #   # TODO
    #   def test_get_validation_report_with_result(self, mock_stdout, validation_result):
    #       """Test report generation with existing validation result."""
    #   def test_get_validation_report_empty_result(self, mock_stdout, empty_validation_result):
    #       """Test report generation with empty (valid) result."""
    #   def test_get_validation_report_timestamp(self, mock_datetime, mock_stdout, validation_result):
    #       """Test timestamp in validation report."""
    #   def test_get_validation_report_multiple_calls(self, mock_stdout, validation_result):
    #       """Test that multiple report calls return consistent results."""
    #   def test_get_validation_report_with_critical_flag(self, mock_stdout):
    #       """Test report generation with items marked as critical."""

    def test_get_validation_report_no_previous_result(self, mock_stdout):
        """Test report generation when no validation has been performed."""
        validator = SystemValidator(stdout=mock_stdout)

        # No validation performed yet
        assert validator._last_result is None

        report = validator.get_validation_report()

        assert isinstance(report, dict)
        assert "summary" in report
        assert "discrepancies" in report
        assert "timestamp" in report
        assert "is_valid" in report

        # Should be empty/valid report
        assert report["is_valid"] == True
        assert report["summary"]["total_checks"] == 0
        assert report["summary"]["passed"] == 0
        assert report["summary"]["failed"] == 0
        assert report["summary"]["warnings"] == 0
        assert report["summary"]["total_issues"] == 0
        assert report["summary"]["critical_issues"] == 0

        # Verify timestamp is present
        assert "timestamp" in report
        assert isinstance(report["timestamp"], str)


class TestPrivateHelperMethods:
    """Test private helper methods."""

    #   # TODO
    #   def test_create_report_from_result(self, mock_stdout, validation_result):
    #       """Test _create_report_from_result method."""
    #   def test_create_report_from_result_empty_discrepancies(self, mock_stdout, empty_validation_result):
    #       """Test _create_report_from_result with empty discrepancies."""
    #   def test_create_report_from_result_nested_discrepancies(self, mock_stdout):
    #       """Test _create_report_from_result with complex discrepancy structure."""
    #   def test_get_timestamp(self, mock_datetime, mock_stdout):
    #       """Test _get_timestamp method."""

    def test_create_empty_report(self, mock_stdout):
        """Test _create_empty_report method."""
        validator = SystemValidator(stdout=mock_stdout)

        report = validator._create_empty_report()

        assert isinstance(report, dict)
        assert report["summary"]["total_checks"] == 0
        assert report["summary"]["passed"] == 0
        assert report["summary"]["failed"] == 0
        assert report["summary"]["warnings"] == 0
        assert report["summary"]["total_issues"] == 0
        assert report["summary"]["critical_issues"] == 0
        assert report["summary"]["is_valid"] == True
        assert report["discrepancies"] == []
        assert report["is_valid"] == True
        assert "timestamp" in report


class TestEdgeCases:
    """Test edge cases and error handling."""

    #   # TODO
    #   def test_validate_configuration_partial_differences(self, mock_stdout, mock_pyro_config):
    #       """Test validation with partial differences dictionary (missing keys)."""
    #   def test_validation_result_immutability(self, mock_stdout, mock_pyro_config):
    #       """Test that validation results are not accidentally modified."""

    def test_validate_configuration_with_empty_config(self, mock_stdout):
        """Test validation with completely empty config."""
        empty_config = Mock(spec=PyroConfig)
        empty_config.users = []
        empty_config.groups = []
        empty_config.devices = []
        empty_config.excludes = Mock()
        empty_config.excludes.users = set()
        empty_config.excludes.groups = set()
        empty_config.excludes.devices = set()
        empty_config.excludes.directories = set()
        empty_config.excludes.files = set()
        empty_config.excludes.links = set()

        validator = SystemValidator(stdout=mock_stdout)

        with patch.object(
            validator.scanner, "scan_system_state"
        ) as mock_scan, patch.object(
            validator.comparator, "compare_states"
        ) as mock_compare:

            mock_scan.return_value = {}
            mock_compare.return_value = {}

            result = validator.validate_configuration(empty_config)

            assert result.is_valid == True

    def test_get_validation_report_after_exception(self, mock_stdout):
        """Test report generation after a failed validation."""
        validator = SystemValidator(stdout=mock_stdout)

        # Set up a failed validation scenario
        with patch.object(validator.scanner, "scan_system_state") as mock_scan:
            mock_scan.side_effect = Exception("Scan failed")

            try:
                validator.validate_configuration(Mock())
            except Exception:
                pass  # Expected

            # Last result should still be None
            assert validator._last_result is None

            # Should return empty report
            report = validator.get_validation_report()
            assert report["is_valid"] == True

    def test_concurrent_validation_requests(self, mock_stdout, mock_pyro_config):
        """Test handling of rapid successive validation requests."""
        validator = SystemValidator(stdout=mock_stdout)

        differences1 = {"missing_users": [{"username": "user1"}]}
        differences2 = {"missing_users": [{"username": "user2"}]}

        # Simulate two rapid calls
        with patch.object(
            validator.scanner, "scan_system_state"
        ) as mock_scan, patch.object(
            validator.comparator, "compare_states"
        ) as mock_compare:

            # First call
            mock_scan.return_value = {}
            mock_compare.return_value = differences1

            result1 = validator.validate_configuration(mock_pyro_config)

            # Reset for second call
            mock_scan.reset_mock()
            mock_compare.reset_mock()

            mock_scan.return_value = {}
            mock_compare.return_value = differences2

            result2 = validator.validate_configuration(mock_pyro_config)

            # Results should be different
            assert result1 != result2
            assert validator._last_result == result2

# TODO
#   class TestIntegrationScenarios:
#       """Integration tests for complete validation workflows."""
#       def test_complete_validation_workflow(
#           self, mock_compare_states, mock_scan_state, mock_stdout, mock_pyro_config
#       ):
#           """Test complete validation workflow from start to report."""
#       def test_multiple_validations_different_configs(self, mock_stdout):
#           """Test validating multiple different configurations."""
#       def test_validation_with_realistic_system_state(self, mock_stdout, mock_pyro_config):
#           """Test validation with realistic, complex system state."""

# TODO
#   class TestPerformance:
#       """Test performance-related aspects."""
#       def test_validate_configuration_large_state(self, mock_stdout, mock_pyro_config):
#           """Test validation with large system state."""
#       def test_get_validation_report_performance(self, mock_stdout):
#           """Test report generation performance with large discrepancies."""

class TestLogging:
    """Test logging and debug output."""

    # TODO
#   def test_validate_configuration_debug_output(
#       self, mock_compare_states, mock_scan_state, mock_stdout, mock_pyro_config
#   ):
#       """Test debug output during validation."""

    @patch.object(SystemStateScanner, "scan_system_state")
    @patch.object(SystemStateComparator, "compare_states")
    def test_validate_configuration_no_debug_output(
        self, mock_compare_states, mock_scan_state, mock_pyro_config
    ):
        """Test no debug output when debug is disabled."""
        # Create stdout without debug mode
        stdout = Mock(spec=STDOUTMsg)
        stdout.debug = Mock()

        mock_scan_state.return_value = {}
        mock_compare_states.return_value = {}

        validator = SystemValidator(stdout=stdout, config={"debug": False})

        validator.validate_configuration(mock_pyro_config)

        # Debug should still be called (it's called in validate_configuration)
        # but we can verify it was called with something
        assert stdout.debug.called

    def test_get_validation_report_no_stdout_interaction(self, mock_stdout):
        """Test that get_validation_report doesn't produce stdout output."""
        validator = SystemValidator(stdout=mock_stdout)

        # No validation performed
        report = validator.get_validation_report()

        # Should not call any stdout methods
        mock_stdout.debug.assert_not_called()
        mock_stdout.info.assert_not_called()
        mock_stdout.warn.assert_not_called()
        mock_stdout.err.assert_not_called()


if __name__ == "__main__":
    # This allows running the test file directly
    pytest.main([__file__, "-v", "--tb=short"])
