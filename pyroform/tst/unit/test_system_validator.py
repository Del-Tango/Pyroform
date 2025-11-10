import unittest

# Import the modules to test
from pyroform.src.models import PyroConfig, User, Group, Device
from pyroform.src.validator import SystemValidator


class TestSystemValidator(unittest.TestCase):
    """Test system validator"""

    def setUp(self):
        self.validator = SystemValidator()

        # Create test configuration
        self.users = [User("u1", "testuser", "pwd", [])]
        self.groups = [Group("g1", "testgroup", [])]
        self.devices = [Device("d1", "/dev/sda1", 1, "/mnt/test", [])]
        self.config = PyroConfig("test", self.users, self.groups, self.devices)

    def test_get_validation_report_no_validation(self):
        """Test getting report without prior validation"""
        report = self.validator.get_validation_report()

        self.assertEqual(report["summary"]["total_checks"], 0)
        self.assertEqual(report["summary"]["passed"], 0)
        self.assertEqual(report["summary"]["failed"], 0)


# CODE DUMP

# TODO
#   @patch('pyroform.src.validator.subprocess.run')
#   def test_validate_configuration(self, mock_subprocess):
#       """Test system validation"""
#       # Mock subprocess responses
#       mock_subprocess.return_value.stdout = "root\nbin\ntestuser\n"

#       result = self.validator.validate_configuration(self.config)

#       self.assertIsInstance(result, ValidationResult)
#       self.assertIn("is_valid", result.__dict__)
#       self.assertIn("discrepancies", result.__dict__)
#       self.assertIn("summary", result.__dict__)

# TODO
#   @patch('pyroform.src.validator.subprocess.run')
#   def test_get_validation_report(self, mock_subprocess):
#       """Test generating validation report"""
#       # First validate to set last_result
#       mock_subprocess.return_value.stdout = "root\nbin\ntestuser\n"
#       self.validator.validate_configuration(self.config)

#       report = self.validator.get_validation_report()

#       self.assertIn("summary", report)
#       self.assertIn("discrepancies", report)
#       self.assertIn("timestamp", report)
#       self.assertIn("total_checks", report["summary"])
