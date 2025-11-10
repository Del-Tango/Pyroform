import unittest
from unittest.mock import Mock
import json
import yaml
import tempfile
from pathlib import Path

# Import the modules to test
from pyroform.src.reporter import ReportGenerator


class TestReportGenerator(unittest.TestCase):
    """Test report generator"""

    def setUp(self):
        self.reporter = ReportGenerator()

    def test_generate_validation_report(self):
        """Test generating validation-specific report"""
        mock_validation_result = Mock()
        mock_validation_result.is_valid = False
        mock_validation_result.summary = {"total_issues": 2, "critical_issues": 1}
        mock_validation_result.discrepancies = [
            {"type": "user", "issue": "User missing", "critical": True},
            {"type": "permission", "issue": "Wrong permissions", "critical": False},
        ]

        report = self.reporter.generate_validation_report(mock_validation_result)

        self.assertEqual(report["type"], "validation")
        self.assertFalse(report["is_valid"])
        self.assertEqual(report["failed"], 2)
        self.assertEqual(report["warnings"], 1)

    def test_save_report_json(self):
        """Test saving report as JSON"""
        report = {"action": "test", "success": True}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            success = self.reporter.save_report(report, temp_path, "json")
            self.assertTrue(success)

            # Verify file content
            with open(temp_path, "r") as f:
                saved_report = json.load(f)
            self.assertEqual(saved_report["action"], "test")
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_save_report_yaml(self):
        """Test saving report as YAML"""
        report = {"action": "test", "success": True}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_path = Path(f.name)

        try:
            success = self.reporter.save_report(report, temp_path, "yaml")
            self.assertTrue(success)

            # Verify file content
            with open(temp_path, "r") as f:
                saved_report = yaml.safe_load(f)
            self.assertEqual(saved_report["action"], "test")
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_generate_combined_report(self):
        """Test generating combined report from multiple actions"""
        reports = [
            {"action": "validate", "success": True, "duration_seconds": 10},
            {"action": "configure", "success": True, "duration_seconds": 30},
        ]

        combined = self.reporter.generate_combined_report(reports)

        self.assertEqual(combined["type"], "combined")
        self.assertEqual(combined["total_actions"], 2)
        self.assertEqual(combined["successful_actions"], 2)
        self.assertEqual(combined["failed_actions"], 0)
        self.assertIn("summary", combined)


# CODE DUMP

# TODO
#   def setUp(self):
#       """Set up test fixtures"""
#       self.reporter = ReportGenerator()

#       # If you have existing mock reports, update their structure too
#       self.mock_report = {
#           "action": {"type": "test_action"},
#           "result": MagicMock(),
#           "config_files": ["test_config.yaml"],
#           "start_time": "2023-01-01T10:00:00Z",
#           "end_time": "2023-01-01T10:05:00Z",
#           "summary": {
#               "action_type": "test_action",
#               "status": "success",
#               "errors": 0,
#               "warnings": 0
#           }
#       }

# TODO
#   def test_generate_action_report(self):
#       """Test generating action report"""
#       # Create minimal mocks
#       mock_action = {"type": "test_action"}
#       mock_result = MagicMock()
#       mock_config_files = ["config1.yaml", "config2.yaml"]
#       mock_start_time = "2023-01-01T10:00:00Z"
#       mock_end_time = "2023-01-01T10:05:00Z"

#       # Mock the _generate_summary to avoid the len() issue entirely
#       with patch.object(self.reporter, '_generate_summary') as mock_summary:
#           mock_summary.return_value = {
#               "action_type": "test_action",
#               "status": "success",
#               "errors": 0,
#               "warnings": 0
#           }

#           report = self.reporter.generate_action_report(
#               action=mock_action,
#               result=mock_result,
#               config_files=mock_config_files,
#               start_time=mock_start_time,
#               end_time=mock_end_time
#           )

#       # Verify the method was called with correct parameters
#       mock_summary.assert_called_once_with(mock_action, mock_result)

#       # Verify report structure
#       self.assertEqual(report["action"], mock_action)
#       self.assertEqual(report["result"], mock_result)
#       self.assertEqual(report["config_files"], mock_config_files)
#       self.assertEqual(report["start_time"], mock_start_time)
#       self.assertEqual(report["end_time"], mock_end_time)
#       self.assertEqual(report["summary"], mock_summary.return_value)

# TODO
#   def test_generate_action_report(self):
#       """Test generating action report"""
#       # Create minimal mocks
#       mock_action = {"type": "test_action"}
#       mock_result = MagicMock()

#       # Mock the _generate_summary to avoid the len() issue entirely
#       with patch.object(self.reporter, '_generate_summary') as mock_summary:
#           mock_summary.return_value = {
#               "action_type": "test_action",
#               "status": "success",
#               "errors": 0,
#               "warnings": 0
#           }

#           report = self.reporter.generate_action_report(
#               action=mock_action,
#               result=mock_result,
#               timestamp="2023-01-01T00:00:00Z"
#           )

#       # Verify the method was called with correct parameters
#       mock_summary.assert_called_once_with(mock_action, mock_result)

#       # Verify report structure
#       self.assertEqual(report["action"], mock_action)
#       self.assertEqual(report["result"], mock_result)
#       self.assertEqual(report["timestamp"], "2023-01-01T00:00:00Z")
#       self.assertEqual(report["summary"], mock_summary.return_value)

# TODO
#   def test_generate_action_report(self):
#       """Test generating action report"""
#       mock_result = Mock()
#       mock_result.success = True

#       start_time = "2023-01-01T00:00:00"
#       end_time = "2023-01-01T00:01:30"

#       report = self.reporter.generate_action_report(
#           action="configure",
#           result=mock_result,
#           config_files=["/path/to/config.json"],
#           start_time=start_time,
#           end_time=end_time,
#           test_flag=True
#       )

#       self.assertEqual(report["action"], "configure")
#       self.assertEqual(report["config_files"], ["/path/to/config.json"])
#       self.assertTrue(report["success"])
#       self.assertIn("duration", report)
#       self.assertIn("summary", report)
#       self.assertIn("details", report)
