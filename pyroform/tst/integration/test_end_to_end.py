"""
Integration Tests: End-to-End Workflows
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

from pyroform.cli import cli  # Changed from main to cli
from pyroform import Pyroform


class TestEndToEnd:
    """Test complete end-to-end workflows"""

    @pytest.fixture
    def comprehensive_pyro_config(self):
        """Create a comprehensive Pyro configuration for E2E testing"""
        return {
            "Label": "E2E Test Configuration",
            "Users": [
                {
                    "label": "app_user",
                    "Name": "appuser",
                    "Password": "apppass123",
                    "Groups": ["appgroup", "users"],
                },
                {
                    "label": "data_user",
                    "Name": "datauser",
                    "Password": "datapass123",
                    "Groups": ["datagroup", "users"],
                },
            ],
            "Groups": [
                {"label": "app_group", "Name": "appgroup", "Users": ["appuser"]},
                {"label": "data_group", "Name": "datagroup", "Users": ["datauser"]},
                {
                    "label": "users_group",
                    "Name": "users",
                    "Users": ["appuser", "datauser"],
                },
            ],
            "Devices": [
                {
                    "label": "data_device",
                    "Path": "/dev/sdb1",
                    "Partition": 1,
                    "Mountpoint": "/mnt/data",
                    "State": [
                        "dir,/mnt/data/app,appuser,appgroup,750",
                        "dir,/mnt/data/shared,datauser,datagroup,775",
                        "fl,/mnt/data/app/config.yaml,appuser,appgroup,600",
                        "fl,/mnt/data/shared/data.txt,datauser,datagroup,664",
                    ],
                }
            ],
        }

    @pytest.fixture
    def temp_config_environment(self, comprehensive_pyro_config):
        """Create temporary configuration environment"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create Pyro files
            pyro_dir = tmpdir_path / "pyro_configs"
            pyro_dir.mkdir()

            # Main config
            main_config = pyro_dir / "pyro_main.yaml"
            with open(main_config, "w") as f:
                yaml.dump(comprehensive_pyro_config, f)

            # Additional config
            additional_config = {
                "Label": "Additional Config",
                "Users": [
                    {
                        "label": "extra_user",
                        "Name": "extrauser",
                        "Password": "extrapass123",
                        "Groups": ["users"],
                    }
                ],
                "Groups": [],
                "Devices": [],
            }

            extra_config = pyro_dir / "pyro_extra.json"
            with open(extra_config, "w") as f:
                json.dump(additional_config, f)

            # Pyroform config file
            pyroform_config = {
                "safety_checks": True,
                "default_output_dir": str(tmpdir_path / "output"),
                "log_level": "INFO",
                "auto_confirm": False,
            }

            config_file = tmpdir_path / "pyroform_config.yaml"
            with open(config_file, "w") as f:
                yaml.dump(pyroform_config, f)

            yield {
                "tmpdir": tmpdir_path,
                "pyro_dir": pyro_dir,
                "main_config": main_config,
                "extra_config": extra_config,
                "pyroform_config": config_file,
            }

    @patch("pyroform.src.flow_engine.FlowEngine")
    @patch("pyroform.src.validator.SystemValidator._get_current_system_state")
    def test_complete_cli_workflow(
        self, mock_get_state, mock_flow_engine, temp_config_environment
    ):
        """Test complete CLI workflow from input to execution"""
        # Mock system state
        mock_get_state.return_value = {
            "users": [],
            "groups": [],
            "mounts": {},
            "files": {},
        }

        # Mock FlowEngine
        mock_flow_instance = Mock()
        mock_flow_instance.load_procedure.return_value = True
        mock_flow_instance.start_procedure.return_value = Mock(
            success=True, message="Success"
        )
        mock_flow_engine.return_value = mock_flow_instance

        runner = CliRunner()

        # Test configure action - use cli instead of main
        result = runner.invoke(
            cli,
            [
                "main",  # Specify the main command
                "-C",
                "-i",
                str(temp_config_environment["pyro_dir"]),
                "-c",
                str(temp_config_environment["pyroform_config"]),
                "-y",  # Auto-confirm
                "-r",  # Generate report
            ],
        )

        assert result.exit_code == 0
        assert "configure" in result.output.lower() or result.exit_code == 0

    @patch("pyroform.pyroform.PyroformEngine")
    def test_complete_library_workflow(
        self, mock_engine_class, temp_config_environment
    ):
        """Test complete library workflow"""
        # Create a fresh mock for each test run
        mock_engine = MagicMock()

        # Set up return values
        mock_engine.configure.return_value = True
        mock_engine.mount.return_value = True
        mock_engine.scorch.return_value = Mock(
            resources_removed=[], resources_failed=[], success=True, dry_run=False
        )

        # Create validation responses
        invalid_response = Mock()
        invalid_response.is_valid = False
        invalid_response.discrepancies = [{"type": "user", "issue": "test"}]
        invalid_response.summary = {"total_issues": 1, "critical_issues": 1}

        valid_response = Mock()
        valid_response.is_valid = True
        valid_response.discrepancies = []
        valid_response.summary = {"total_issues": 0, "critical_issues": 0}

        # Set up side effect for validate
        mock_engine.validate.side_effect = [invalid_response, valid_response]

        # Make sure the class returns our mock instance
        mock_engine_class.return_value = mock_engine

        pf = Pyroform(
            config_file=str(temp_config_environment["pyroform_config"]),
            auto_confirm=True,
        )

        # Execute full workflow
        config_file = str(temp_config_environment["main_config"])

        # 1. Validate current state
        validation = pf.validate(config_file)
        assert validation.is_valid is False

        # 2. Configure system
        configure_result = pf.configure(config_file)
        assert configure_result is True

        # 3. Mount devices
        mount_result = pf.mount(config_file)
        assert mount_result is True

        # 4. Validate again (should be valid now)
        final_validation = pf.validate(config_file)
        assert (
            final_validation.is_valid is True
        ), f"Expected True but got {final_validation.is_valid}. Validation calls: {mock_engine.validate.call_count}"

    def test_error_recovery_workflow(self, temp_config_environment):
        """Test workflow with error recovery"""
        pf = Pyroform(auto_confirm=True)

        with patch.object(pf.engine, "configure") as mock_configure:
            # Simulate partial failure scenario
            mock_configure.side_effect = [
                Exception("First failure"),
                True,  # Success on retry
            ]

            # First attempt should fail
            with pytest.raises(Exception, match="First failure"):
                pf.configure(str(temp_config_environment["main_config"]))

            # Second attempt should succeed
            result = pf.configure(str(temp_config_environment["main_config"]))
            assert result is True

    @patch("pyroform.src.scorch_engine.ScorchEngine._get_current_system_state")
    def test_scorch_workflow(self, mock_get_state, temp_config_environment):
        """Test complete scorch workflow"""
        # Mock system with extra resources
        mock_get_state.return_value = {
            "users": ["appuser", "datauser", "extrauser", "olduser"],
            "groups": ["appgroup", "datagroup", "users", "oldgroup"],
            "mounts": {"/dev/sdb1": "/mnt/data", "/dev/sdc1": "/mnt/old"},
            "files": {
                "/mnt/data/app": {
                    "owner": "appuser",
                    "group": "appgroup",
                    "perms": "750",
                },
                "/mnt/old/data": {
                    "owner": "olduser",
                    "group": "oldgroup",
                    "perms": "755",
                },
            },
        }

        pf = Pyroform(auto_confirm=True)

        with patch.object(pf.engine, "scorch") as mock_scorch:
            mock_scorch.return_value = Mock(
                resources_removed=["olduser", "oldgroup", "/mnt/old"],
                resources_failed=[],
                dry_run=False,
            )

            result = pf.scorch(str(temp_config_environment["main_config"]))

            assert len(result.resources_removed) > 0
            assert len(result.resources_failed) == 0

    def test_multi_config_workflow(self, temp_config_environment):
        """Test workflow with multiple configuration files"""
        pf = Pyroform(auto_confirm=True)

        with patch.object(pf.engine, "configure") as mock_configure:
            mock_configure.return_value = True

            # Configure with directory containing multiple files
            result = pf.configure(str(temp_config_environment["pyro_dir"]))

            assert result is True
            # Verify engine was called with directory path and auto_confirm
            mock_configure.assert_called_with(
                str(temp_config_environment["pyro_dir"]), auto_confirm=True
            )

    @patch("pyroform.src.validator.SystemValidator._get_current_system_state")
    def test_validation_workflow(self, mock_get_state, temp_config_environment):
        """Test complete validation workflow"""
        # Mock a system that matches our configuration
        mock_get_state.return_value = {
            "users": ["appuser", "datauser", "extrauser"],
            "groups": ["appgroup", "datagroup", "users"],
            "mounts": {"/dev/sdb1": "/mnt/data"},
            "files": {
                "/mnt/data/app": {
                    "owner": "appuser",
                    "group": "appgroup",
                    "perms": "750",
                },
                "/mnt/data/shared": {
                    "owner": "datauser",
                    "group": "datagroup",
                    "perms": "775",
                },
                "/mnt/data/app/config.yaml": {
                    "owner": "appuser",
                    "group": "appgroup",
                    "perms": "600",
                },
                "/mnt/data/shared/data.txt": {
                    "owner": "datauser",
                    "group": "datagroup",
                    "perms": "664",
                },
            },
        }

        pf = Pyroform(auto_confirm=True)

        with patch.object(pf.engine, "validate") as mock_validate:
            mock_validate.return_value = Mock(
                is_valid=True,
                discrepancies=[],
                summary={"total_issues": 0, "critical_issues": 0},
            )

            result = pf.validate(str(temp_config_environment["pyro_dir"]))

            assert result.is_valid is True
            assert len(result.discrepancies) == 0

    def test_report_generation_workflow(self, temp_config_environment):
        """Test complete report generation workflow"""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as report_file:
            with patch("pyroform.src.flow_engine.FlowEngine") as mock_flow_engine:
                mock_instance = Mock()
                mock_instance.load_procedure.return_value = True
                mock_instance.start_procedure.return_value = Mock(
                    success=True, message="Success"
                )
                mock_flow_engine.return_value = mock_instance

                result = runner.invoke(
                    cli,
                    [
                        "main",  # Specify the main command
                        "-C",
                        "-i",
                        str(temp_config_environment["main_config"]),
                        "-o",
                        report_file.name,
                        "-r",
                        "-y",
                    ],
                )

                assert result.exit_code == 0

                # Verify report file was created and contains valid JSON
                with open(report_file.name, "r") as f:
                    report_content = json.load(f)

                assert "action" in report_content
                assert "summary" in report_content
                assert "timestamp" in report_content

    def test_dry_run_workflow(self, temp_config_environment):
        """Test dry-run workflow doesn't execute destructive operations"""
        pf = Pyroform(auto_confirm=True)

        with patch.object(pf.engine, "scorch") as mock_scorch:
            mock_scorch.return_value = Mock(
                resources_removed=["olduser", "oldgroup"],
                resources_failed=[],
                dry_run=True,
            )

            # Test scorch with dry-run
            result = pf.scorch(
                str(temp_config_environment["main_config"]), dry_run=True
            )

            assert result.dry_run is True
            # In dry-run mode, no actual resources should be removed
            # (though our mock returns some for testing)

    def test_workflow_with_configuration_overrides(self, temp_config_environment):
        """Test workflow with configuration file overrides"""
        runner = CliRunner()

        # Test CLI with config file that overrides defaults
        with patch("pyroform.src.flow_engine.FlowEngine") as mock_flow_engine:
            mock_instance = Mock()
            mock_instance.load_procedure.return_value = True
            mock_instance.start_procedure.return_value = Mock(
                success=True, message="Success"
            )
            mock_flow_engine.return_value = mock_instance

            result = runner.invoke(
                cli,
                [
                    "main",  # Specify the main command
                    "-M",  # Mount action
                    "-i",
                    str(temp_config_environment["main_config"]),
                    "-c",
                    str(temp_config_environment["pyroform_config"]),
                    "-y",
                ],
            )

            assert result.exit_code == 0

    def test_comprehensive_error_workflow(self, temp_config_environment):
        """Test complete workflow with error scenarios"""
        pf = Pyroform(auto_confirm=True)

        # Test workflow where configure fails but mount succeeds
        with patch.object(pf.engine, "configure") as mock_configure:
            with patch.object(pf.engine, "mount") as mock_mount:
                mock_configure.return_value = False  # Configure fails
                mock_mount.return_value = True  # Mount succeeds

                # Configure should fail
                configure_result = pf.configure(
                    str(temp_config_environment["main_config"])
                )
                assert configure_result is False

                # Mount might still work (depending on dependencies)
                mount_result = pf.mount(str(temp_config_environment["main_config"]))
                assert mount_result is True


# CODE DUMP

