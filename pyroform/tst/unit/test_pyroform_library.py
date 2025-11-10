import unittest
from unittest.mock import Mock, patch

# Import the modules to test
from pyroform.src.models import ActionType
from pyroform.src.validator import ValidationResult
from pyroform.src.scorch_engine import ScorchResult
from pyroform.pyroform import Pyroform


class TestPyroformLibrary(unittest.TestCase):
    """Test main Pyroform library class"""

    def setUp(self):
        self.pyroform = Pyroform(auto_confirm=True)

    @patch("pyroform.pyroform.PyroformEngine.configure")
    def test_configure_method(self, mock_engine_configure):
        """Test library configure method"""
        mock_engine_configure.return_value = True

        success = self.pyroform.configure("/path/to/config", dry_run=True)

        self.assertTrue(success)
        mock_engine_configure.assert_called_once_with(
            "/path/to/config", dry_run=True, auto_confirm=True
        )

    @patch("pyroform.pyroform.PyroformEngine.scorch")
    def test_scorch_method(self, mock_engine_scorch):
        """Test library scorch method"""
        mock_result = ScorchResult([], [], False, True)
        mock_engine_scorch.return_value = mock_result

        result = self.pyroform.scorch("/path/to/config", dry_run=True)

        self.assertEqual(result, mock_result)
        mock_engine_scorch.assert_called_once_with(
            "/path/to/config", dry_run=True, auto_confirm=True
        )

    @patch("pyroform.pyroform.PyroformEngine.validate")
    def test_validate_method(self, mock_engine_validate):
        """Test library validate method"""
        mock_result = ValidationResult(True, [], {})
        mock_engine_validate.return_value = mock_result

        result = self.pyroform.validate("/path/to/config")

        self.assertEqual(result, mock_result)
        mock_engine_validate.assert_called_once_with("/path/to/config")

    @patch("pyroform.pyroform.ReportGenerator.generate_action_report")
    @patch("pyroform.pyroform.ReportGenerator.save_report")
    def test_generate_report(self, mock_save_report, mock_generate_report):
        """Test report generation"""
        # Set up last action and result
        self.pyroform._last_action = ActionType.CONFIGURE
        self.pyroform._last_result = Mock(success=True)

        mock_generate_report.return_value = {"action": "configure", "success": True}
        mock_save_report.return_value = True

        success = self.pyroform.generate_report("/path/to/report.json")

        self.assertTrue(success)
        mock_generate_report.assert_called_once()
        mock_save_report.assert_called_once()

    def test_config_management(self):
        """Test configuration management methods"""
        original_config = self.pyroform.get_config()

        # Update configuration
        self.pyroform.set_config(log_level="DEBUG", dry_run=True)
        updated_config = self.pyroform.get_config()

        self.assertEqual(updated_config["log_level"], "DEBUG")
        self.assertTrue(updated_config["dry_run"])
        # Original config should not be modified
        self.assertNotEqual(original_config, updated_config)
