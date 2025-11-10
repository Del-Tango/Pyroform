import unittest

# Import the modules to test
from pyroform.src.models import PyroConfig, User, Group, Device, ActionType


class TestModels(unittest.TestCase):
    """Test data models"""

    def test_user_creation(self):
        """Test User model creation"""
        user = User(
            label="test_user",
            name="testuser",
            password="testpass",
            groups=["admin", "users"],
        )
        self.assertEqual(user.name, "testuser")
        self.assertEqual(user.password, "testpass")
        self.assertEqual(user.groups, ["admin", "users"])

    def test_group_creation(self):
        """Test Group model creation"""
        group = Group(label="test_group", name="testgroup", users=["user1", "user2"])
        self.assertEqual(group.name, "testgroup")
        self.assertEqual(group.users, ["user1", "user2"])

    def test_device_creation(self):
        """Test Device model creation"""
        device = Device(
            label="test_device",
            path="/dev/sda1",
            partition=1,
            mountpoint="/mnt/test",
            state=["dir,/mnt/test/data,root,root,755"],
        )
        self.assertEqual(device.path, "/dev/sda1")
        self.assertEqual(device.mountpoint, "/mnt/test")
        self.assertEqual(device.state, ["dir,/mnt/test/data,root,root,755"])

    def test_pyroconfig_creation(self):
        """Test PyroConfig model creation"""
        users = [User("u1", "user1", "pass1", ["group1"])]
        groups = [Group("g1", "group1", ["user1"])]
        devices = [Device("d1", "/dev/sda1", 1, "/mnt/test", [])]

        config = PyroConfig(
            label="test_config", users=users, groups=groups, devices=devices
        )

        self.assertEqual(config.label, "test_config")
        self.assertEqual(len(config.users), 1)
        self.assertEqual(len(config.groups), 1)
        self.assertEqual(len(config.devices), 1)

    def test_pyroconfig_empty_lists(self):
        """Test PyroConfig handles empty lists correctly"""
        config = PyroConfig(label="test", users=None, groups=None, devices=None)
        self.assertEqual(config.users, [])
        self.assertEqual(config.groups, [])
        self.assertEqual(config.devices, [])

    def test_action_type_enum(self):
        """Test ActionType enum values"""
        self.assertEqual(ActionType.CONFIGURE.value, "configure")
        self.assertEqual(ActionType.SCORCH.value, "scorch")
        self.assertEqual(ActionType.MOUNT.value, "mount")
        self.assertEqual(ActionType.VALIDATE.value, "validate")
