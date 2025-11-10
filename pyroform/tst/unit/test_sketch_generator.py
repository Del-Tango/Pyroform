import unittest
import json
import tempfile
from pathlib import Path

# Import the modules to test
from pyroform.src.models import PyroConfig, User, Group, Device, ActionType
from pyroform.src.sketch_generator import SketchGenerator


class TestSketchGenerator(unittest.TestCase):
    """Test sketch generator"""

    def setUp(self):
        self.generator = SketchGenerator()

        # Create test configuration
        self.users = [User("user1", "testuser", "password123", ["admin", "users"])]
        self.groups = [Group("group1", "testgroup", ["testuser"])]
        self.devices = [
            Device(
                "device1",
                "/dev/sda1",
                1,
                "/mnt/data",
                [
                    "dir,/mnt/data/subdir,root,root,755",
                    "fl,/mnt/data/file.txt,user,users,644",
                ],
            )
        ]

        self.config = PyroConfig(
            label="test_config",
            users=self.users,
            groups=self.groups,
            devices=self.devices,
        )

    def test_generate_configure_sketch(self):
        """Test generating configure sketch"""
        sketch = self.generator.generate_configure_sketch(self.config)

        self.assertIn("name", sketch)
        self.assertIn("Users", sketch)
        self.assertIn("Groups", sketch)
        self.assertIn("Files", sketch)
        self.assertIn("summary", sketch)

        # Check user commands
        self.assertTrue(
            any(
                "create_user_testuser" in cmd.get("name", "") for cmd in sketch["Users"]
            )
        )

        # Check group commands
        self.assertTrue(
            any(
                "create_group_testgroup" in cmd.get("name", "")
                for cmd in sketch["Groups"]
            )
        )

    def test_generate_mount_sketch(self):
        """Test generating mount sketch"""
        sketch = self.generator.generate_mount_sketch(self.config)

        self.assertIn("name", sketch)
        self.assertIn("Devices", sketch)
        self.assertIn("summary", sketch)

        # Check mount commands
        self.assertTrue(
            any("create_mountpoint" in cmd.get("name", "") for cmd in sketch["Devices"])
        )
        self.assertTrue(
            any("mount_device" in cmd.get("name", "") for cmd in sketch["Devices"])
        )

    def test_generate_scorch_sketch(self):
        """Test generating scorch sketch"""
        sketch = self.generator.generate_scorch_sketch(self.config)

        self.assertIn("name", sketch)
        self.assertIn("Cleanup", sketch)
        self.assertIn("summary", sketch)

        # Check cleanup commands
        self.assertTrue(
            any("cleanup_orphaned" in cmd.get("name", "") for cmd in sketch["Cleanup"])
        )

    def test_generate_sketch_validation_action(self):
        """Test generating sketch for validate action raises ValueError"""
        with self.assertRaises(ValueError):
            self.generator.generate_sketch(self.config, ActionType.VALIDATE)

    def test_save_sketch(self):
        """Test saving sketch to file"""
        sketch = {"name": "test_sketch", "commands": []}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            success = self.generator.save_sketch(sketch, temp_path)
            self.assertTrue(success)

            # Verify file content
            with open(temp_path, "r") as f:
                saved_sketch = json.load(f)
            self.assertEqual(saved_sketch["name"], "test_sketch")
        finally:
            if temp_path.exists():
                temp_path.unlink()
