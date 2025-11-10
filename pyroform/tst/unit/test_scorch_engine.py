import unittest
from unittest.mock import patch

# Import the modules to test
from pyroform.src.models import PyroConfig, User, Group, Device
from pyroform.src.scorch_engine import ScorchEngine, ScorchResult


class TestScorchEngine(unittest.TestCase):
    """Test scorch engine"""

    def setUp(self):
        self.scorch_engine = ScorchEngine(safety_check=False)

        # Create test configuration
        self.users = [User("u1", "testuser", "pwd", [])]
        self.groups = [Group("g1", "testgroup", [])]
        self.devices = [Device("d1", "/dev/sda1", 1, "/mnt/test", [])]
        self.config = PyroConfig("test", self.users, self.groups, self.devices)

    @patch("pyroform.src.scorch_engine.ScorchEngine._get_current_system_state")
    @patch("pyroform.src.scorch_engine.subprocess.run")
    def test_execute_scorch_dry_run(self, mock_subprocess, mock_get_state):
        """Test scorch execution in dry-run mode"""
        # Mock system state
        mock_get_state.return_value = {
            "users": ["testuser", "orphanuser"],
            "groups": ["testgroup", "orphangroup"],
            "mounts": {"/dev/sda1": "/mnt/test"},
            "filesystem": {"files": [], "directories": [], "links": []},
        }

        # Mock subprocess for UID/GID checks
        mock_subprocess.return_value.stdout = "1001\n"
        mock_subprocess.return_value.returncode = 0

        result = self.scorch_engine.execute_scorch(self.config, dry_run=True)

        self.assertIsInstance(result, ScorchResult)
        self.assertTrue(result.dry_run)
        # In dry-run mode, resources should be marked for removal but not actually removed
        self.assertGreater(len(result.resources_removed), 0)

    @patch("pyroform.src.scorch_engine.ScorchEngine._get_current_system_state")
    @patch("pyroform.src.scorch_engine.subprocess.run")
    def test_execute_scorch_actual_run(self, mock_subprocess, mock_get_state):
        """Test scorch execution in actual mode"""
        # Mock system state with orphaned resources
        mock_get_state.return_value = {
            "users": ["testuser", "orphanuser"],
            "groups": ["testgroup", "orphangroup"],
            "mounts": {"/dev/sda1": "/mnt/test"},
            "filesystem": {"files": [], "directories": [], "links": []},
        }

        # Mock successful removal commands
        mock_subprocess.return_value.returncode = 0

        result = self.scorch_engine.execute_scorch(self.config, dry_run=False)

        self.assertIsInstance(result, ScorchResult)
        self.assertFalse(result.dry_run)
        self.assertTrue(result.success)

    def test_confirm_scorch(self):
        """Test scorch confirmation (mocked for automation)"""
        # With safety_check=False, confirmation should be bypassed
        self.scorch_engine.safety_check = False
        confirmed = self.scorch_engine._confirm_scorch(self.config)
        self.assertTrue(confirmed)
