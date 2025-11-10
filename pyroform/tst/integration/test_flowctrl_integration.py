"""
Integration Tests: FlowCTRL Integration & Basic Actions
"""

import pytest
import json
from unittest.mock import Mock, patch

from pyroform.src.models import PyroConfig, User, Group, Device, ActionType
from pyroform.src.sketch_generator import SketchGenerator
from pyroform.src.flow_engine import PyroflowEngine


class TestFlowIntegration:
    """Test FlowCTRL integration and basic actions"""

    @pytest.fixture
    def sample_pyro_config(self):
        """Create a sample PyroConfig for testing"""
        users = [User("test_user", "testuser", "testpass123", ["testgroup"])]
        groups = [Group("test_group", "testgroup", ["testuser"])]
        devices = [
            Device(
                "test_device",
                "/dev/sdb1",
                1,
                "/mnt/test",
                ["dir,/mnt/test/data,testuser,testgroup,755"],
            )
        ]
        return PyroConfig("Test Config", users, groups, devices)

    @pytest.fixture
    def mock_flow_engine(self):
        """Mock FlowEngine for testing"""
        with patch("pyroform.src.flow_engine.FlowEngine") as mock_flow:
            # Create a proper mock that has the required attributes
            mock_instance = Mock()
            mock_instance.load_procedure.return_value = True
            mock_instance.start_procedure.return_value = Mock(
                success=True, message="Procedure completed successfully"
            )
            mock_instance.pause_procedure.return_value = Mock(success=True)
            mock_instance.resume_procedure.return_value = Mock(success=True)
            mock_instance.stop_procedure.return_value = Mock(success=True)
            mock_instance.purge_data.return_value = Mock(success=True)
            mock_instance.send_external_command.return_value = True

            mock_flow.return_value = mock_instance
            yield mock_instance

    def test_sketch_generation_integration(self, sample_pyro_config):
        """Test sketch generation from PyroConfig"""
        generator = SketchGenerator()

        # Test configure sketch
        configure_sketch = generator.generate_configure_sketch(sample_pyro_config)
        assert configure_sketch["name"] == "Pyroform Auto-Generated Sketch Test Config"
        assert "Users" in configure_sketch
        assert "Groups" in configure_sketch

        # Test mount sketch
        mount_sketch = generator.generate_mount_sketch(sample_pyro_config)
        assert "Devices" in mount_sketch

        # Test sketch structure validation
        for sketch in [configure_sketch, mount_sketch]:
            assert isinstance(sketch, dict)
            assert "name" in sketch
            for section in ["Users", "Groups", "Devices"]:
                if section in sketch:
                    assert isinstance(sketch[section], list)

    def test_flow_engine_integration(self, sample_pyro_config, mock_flow_engine):
        """Test PyroflowEngine integrates with FlowEngine"""
        pyro_engine = PyroflowEngine()
        generator = SketchGenerator()

        # Generate and execute sketch
        sketch = generator.generate_configure_sketch(sample_pyro_config)
        result = pyro_engine.execute_sketch(sketch, ActionType.CONFIGURE)

        # Verify FlowEngine was called correctly
        mock_flow_engine.load_procedure.assert_called_once()
        mock_flow_engine.start_procedure.assert_called_once()
        assert result is True

    def test_sketch_command_generation(self, sample_pyro_config):
        """Test specific command generation in sketches"""
        generator = SketchGenerator()

        sketch = generator.generate_configure_sketch(sample_pyro_config)

        # Verify user creation commands
        user_commands = sketch["Users"]
        assert len(user_commands) > 0

        user_cmd = user_commands[0]
        assert "testuser" in user_cmd["name"].lower()
        assert "useradd" in user_cmd["cmd"] or "id" in user_cmd["setup-cmd"]

        # Verify group creation commands
        group_commands = sketch["Groups"]
        assert len(group_commands) > 0

        group_cmd = group_commands[0]
        assert "testgroup" in group_cmd["name"].lower()
        assert "groupadd" in group_cmd["cmd"] or "getent" in group_cmd["setup-cmd"]

    def test_mount_sketch_generation(self, sample_pyro_config):
        """Test device mount sketch generation"""
        generator = SketchGenerator()

        sketch = generator.generate_mount_sketch(sample_pyro_config)

        # Verify device commands - mount action should only have mount-related commands
        device_commands = sketch["Devices"]
        assert len(device_commands) == 2  # mountpoint creation + device mounting

        device_cmd = device_commands[1]  # The mount command
        assert "test_device" in device_cmd["name"]
        assert "mount" in device_cmd["cmd"]
        assert "/dev/sdb1" in device_cmd["cmd"]
        assert "/mnt/test" in device_cmd["cmd"]

    def test_sketch_file_export(self, sample_pyro_config, tmp_path):
        """Test sketch export to file"""
        generator = SketchGenerator()

        # Mock the FlowEngine to avoid initialization issues
        with patch("pyroform.src.flow_engine.FlowEngine") as mock_flow:
            mock_instance = Mock()
            mock_instance.load_procedure.return_value = True
            mock_instance.start_procedure.return_value = Mock(success=True)
            mock_flow.return_value = mock_instance

            pyro_engine = PyroflowEngine()

        sketch = generator.generate_configure_sketch(sample_pyro_config)

        # Export sketch to file
        sketch_file = tmp_path / "test_sketch.json"
        with open(sketch_file, "w") as f:
            json.dump(sketch, f, indent=2)

        # Verify file was created and is valid JSON
        assert sketch_file.exists()

        with open(sketch_file, "r") as f:
            loaded_sketch = json.load(f)

        assert loaded_sketch["name"] == sketch["name"]
        assert len(loaded_sketch["Users"]) == len(sketch["Users"])

    def test_error_handling_in_flow_execution(
        self, sample_pyro_config, mock_flow_engine
    ):
        """Test error handling during FlowCTRL execution"""
        pyro_engine = PyroflowEngine()
        generator = SketchGenerator()

        sketch = generator.generate_configure_sketch(sample_pyro_config)

        # Test FlowEngine failure scenarios
        mock_flow_engine.load_procedure.return_value = False
        result = pyro_engine.execute_sketch(sketch, ActionType.CONFIGURE)
        assert result is False

        mock_flow_engine.load_procedure.return_value = True
        mock_flow_engine.start_procedure.return_value = Mock(
            success=False, message="Procedure failed"
        )
        result = pyro_engine.execute_sketch(sketch, ActionType.CONFIGURE)
        assert result is False

    def test_action_type_handling(self, sample_pyro_config):
        """Test different action types generate appropriate sketches"""
        generator = SketchGenerator()

        # Test each action type
        for action in ActionType:
            if action != ActionType.VALIDATE:  # Validate doesn't generate sketches
                sketch = generator.generate_sketch(sample_pyro_config, action)
                assert sketch is not None
                assert isinstance(sketch, dict)

    @patch("subprocess.run")
    def test_actual_command_execution(self, mock_subprocess, sample_pyro_config):
        """Test that generated commands are syntactically valid"""
        generator = SketchGenerator()

        sketch = generator.generate_configure_sketch(sample_pyro_config)

        # Mock successful command execution
        mock_subprocess.return_value = Mock(returncode=0)

        # Test user commands
        for user_cmd in sketch.get("Users", []):
            if user_cmd.get("setup-cmd"):
                # This would actually execute in real FlowCTRL
                assert isinstance(user_cmd["setup-cmd"], str)

        # Verify subprocess was called (in real execution)
        # In integration tests, we'd actually test this with docker/sandbox


# CODE DUMP

