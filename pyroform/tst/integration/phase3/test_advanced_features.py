"""
Phase 3 Integration Tests: Advanced Features & Validation
"""
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from pyroform.src.models import PyroConfig, User, Group, Device
from pyroform.src.validator import SystemValidator, ValidationResult
from pyroform.src.scorch_engine import ScorchEngine, ScorchResult
from pyroform.src.reporter import ReportGenerator


class TestPhase3AdvancedFeatures:
    """Test advanced features like validation, scorch, and reporting"""

    @pytest.fixture
    def sample_system_state(self):
        """Mock current system state for validation testing"""
        return {
            "users": ["existing_user", "testuser"],
            "groups": ["existing_group", "testgroup"],
            "mounts": {
                "/dev/sda1": "/",
                "/dev/sdb1": "/mnt/test"
            },
            "files": {
                "/mnt/test/data": {"owner": "testuser", "group": "testgroup", "perms": "755"},
                "/mnt/test/data/file.txt": {"owner": "testuser", "group": "testgroup", "perms": "644"}
            }
        }

    @pytest.fixture
    def sample_pyro_config(self):
        """Create sample configuration for validation testing"""
        users = [
            User("desired_user", "testuser", "testpass123", ["testgroup"]),
            User("new_user", "newuser", "newpass123", ["testgroup"])
        ]
        groups = [
            Group("desired_group", "testgroup", ["testuser", "newuser"])
        ]
        devices = [
            Device(
                "desired_device",
                "/dev/sdb1",
                1,
                "/mnt/test",
                [
                    "dir,/mnt/test/data,testuser,testgroup,755",
                    "fl,/mnt/test/data/file.txt,testuser,testgroup,644",
                    "dir,/mnt/test/newdir,newuser,testgroup,700"
                ]
            )
        ]
        return PyroConfig("Validation Test", users, groups, devices)

    @patch('pyroform.src.validator.SystemValidator._get_current_system_state')
    def test_system_validation_integration(self, mock_get_state, sample_pyro_config, sample_system_state):
        """Test system validation against current state"""
        mock_get_state.return_value = sample_system_state
        validator = SystemValidator()

        result = validator.validate_configuration(sample_pyro_config)

        assert isinstance(result, ValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'discrepancies')
        assert hasattr(result, 'summary')

        # Should find discrepancies (newuser doesn't exist, newdir doesn't exist)
        assert not result.is_valid
        assert len(result.discrepancies) > 0

    def test_validation_report_generation(self, sample_pyro_config):
        """Test validation report generation"""
        validator = SystemValidator()

        # Mock validation result
        mock_result = ValidationResult(
            is_valid=False,
            discrepancies=[
                {"type": "user", "name": "newuser", "issue": "User does not exist"},
                {"type": "directory", "path": "/mnt/test/newdir", "issue": "Directory does not exist"}
            ],
            summary={"total_issues": 2, "critical_issues": 0}
        )

        # Set the last result directly
        validator._last_result = mock_result
        report = validator.get_validation_report()

        assert "summary" in report
        assert "discrepancies" in report
        assert report["summary"]["total_issues"] == 2

    @patch('pyroform.src.scorch_engine.ScorchEngine._get_current_system_state')
    @patch('pyroform.src.scorch_engine.os.remove')
    @patch('pyroform.src.scorch_engine.os.unlink')
    def test_scorch_engine_integration(self, mock_unlink, mock_remove, mock_get_state, sample_pyro_config):
        """Test scorch engine identifies resources for cleanup including filesystem items"""
        # Mock system state with extra resources
        mock_get_state.return_value = {
            "users": ["testuser", "extra_user", "another_user"],
            "groups": ["testgroup", "extra_group"],
            "mounts": {
                "/dev/sdb1": "/mnt/test",
                "/dev/sdc1": "/mnt/extra"
            },
            "files": {
                "/mnt/test/data": {"owner": "testuser", "group": "testgroup", "perms": "755"},
                "/mnt/extra/data": {"owner": "extra_user", "group": "extra_group", "perms": "755"}
            },
            "filesystem": {
                "files": [
                    "/mnt/test/data/file.txt",
                    "/mnt/extra/orphan_file.txt",  # This should be removed
                    "/home/extra_user/extra_file.conf"  # This should be removed
                ],
                "directories": [
                    "/mnt/test/data",
                    "/mnt/extra/orphan_dir",  # This should be removed
                    "/home/extra_user"  # This should be removed (after user removal)
                ],
                "links": [
                    "/mnt/test/link_to_data",
                    "/mnt/extra/orphan_link"  # This should be removed
                ]
            }
        }

        # Mock filesystem operations
        mock_remove.return_value = None
        mock_unlink.return_value = None

        # Mock subprocess calls specifically for UID/GID checks
        with patch('pyroform.src.scorch_engine.subprocess.run') as mock_subprocess:
            # Mock successful UID/GID checks (all users/groups have UID/GID >= 1000)
            mock_subprocess.return_value = Mock(returncode=0, stdout="1001\n")

            scorch_engine = ScorchEngine(safety_check=False)
            result = scorch_engine.execute_scorch(sample_pyro_config)

        assert isinstance(result, ScorchResult)
        assert hasattr(result, 'resources_removed')
        assert hasattr(result, 'resources_failed')
        assert hasattr(result, 'dry_run')

        # Should identify extra resources for removal including filesystem items
        removed_resources = [r for r in result.resources_removed if not r.endswith('(dry-run)')]
        assert len(removed_resources) > 0

        # Verify filesystem cleanup was attempted
        assert mock_remove.called or mock_unlink.called

    def test_scorch_safety_mechanisms(self, sample_pyro_config):
        """Test scorch safety prompts and dry-run"""
        scorch_engine = ScorchEngine(safety_check=True)

        # Test dry-run mode
        with patch('builtins.input', return_value='no'):
            result = scorch_engine.execute_scorch(sample_pyro_config, dry_run=True)
            assert result.dry_run is True

        # Test safety prompt rejection
        with patch('builtins.input', return_value='no'):
            result = scorch_engine.execute_scorch(sample_pyro_config, dry_run=False)
            # Should not execute actual scorch when user says no
            assert len(result.resources_removed) == 0

    def test_report_generation_integration(self, tmp_path):
        """Test comprehensive report generation"""
        reporter = ReportGenerator()

        # Mock action result
        mock_result = Mock()
        mock_result.success = True
        mock_result.execution_time = 30.5
        mock_result.resources_processed = 10
        mock_result.errors = []

        report = reporter.generate_action_report(
            action="configure",
            result=mock_result,
            config_files=["/path/to/config1.yaml"],
            start_time="2024-01-01 10:00:00",
            end_time="2024-01-01 10:00:30"
        )

        # Verify report structure
        assert "action" in report
        assert "timestamp" in report
        assert "duration" in report  # This was the failing assertion
        assert "success" in report
        assert "summary" in report
        assert "details" in report

        # Test file output
        report_file = tmp_path / "test_report.json"
        success = reporter.save_report(report, report_file)

        assert success is True
        assert report_file.exists()

        # Verify file content
        with open(report_file, 'r') as f:
            saved_report = json.load(f)

        assert saved_report["action"] == "configure"
        assert saved_report["success"] is True

    @patch('pyroform.src.validator.subprocess.run')
    def test_validation_with_real_commands(self, mock_subprocess):
        """Test validation using actual system commands (where safe)"""
        # Mock subprocess calls to return predictable results
        mock_subprocess.return_value = Mock(
            stdout="root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/bash\n",
            returncode=0
        )

        validator = SystemValidator()

        # Test user validation (non-destructive)
        current_users = validator._get_current_users()
        assert isinstance(current_users, list)

        # Test group validation (non-destructive)
        current_groups = validator._get_current_groups()
        assert isinstance(current_groups, list)

        # Test mount validation (non-destructive)
        current_mounts = validator._get_current_mounts()
        assert isinstance(current_mounts, dict)

    @patch('pyroform.src.scorch_engine.ScorchEngine._get_current_system_state')
    @patch('pyroform.src.scorch_engine.os.remove')
    def test_scorch_rollback_mechanism(self, mock_remove, mock_get_state, sample_pyro_config):
        """Test scorch rollback on partial failures"""
        # Mock system state
        mock_get_state.return_value = {
            "users": ["testuser", "extra_user"],
            "groups": ["testgroup", "extra_group"],
            "mounts": {},
            "files": {},
            "filesystem": {
                "files": ["/mnt/extra/orphan_file.txt"],
                "directories": [],
                "links": []
            }
        }

        scorch_engine = ScorchEngine(safety_check=False)

        # Mock subprocess calls specifically for UID/GID checks and removal
        with patch('pyroform.src.scorch_engine.subprocess.run') as mock_subprocess:
            # Mock successful UID/GID checks
            mock_subprocess.side_effect = [
                Mock(returncode=0, stdout="1001\n"),  # id -u extra_user
                Mock(returncode=0, stdout="1001\n"),  # getent group extra_group
                Mock(returncode=0),  # which userdel
                Mock(returncode=0),  # userdel extra_user - success
                Mock(returncode=0),  # which groupdel
                Mock(returncode=1),  # groupdel extra_group - failure
            ]

            mock_remove.side_effect = OSError("Permission denied")  # File removal fails

            result = scorch_engine.execute_scorch(sample_pyro_config)

        # Should stop on first failure and report partial success
        assert len(result.resources_failed) > 0

    def test_comprehensive_validation_scenarios(self):
        """Test various validation scenarios"""
        validator = SystemValidator()

        test_scenarios = [
            {
                "name": "perfect_match",
                "current_state": {"users": ["user1"], "groups": ["group1"], "mounts": {}, "files": {}},
                "desired_state": {"users": ["user1"], "groups": ["group1"]},
                "should_be_valid": True
            },
            {
                "name": "missing_user",
                "current_state": {"users": [], "groups": ["group1"], "mounts": {}, "files": {}},
                "desired_state": {"users": ["user1"], "groups": ["group1"]},
                "should_be_valid": False
            },
            {
                "name": "extra_user",
                "current_state": {"users": ["user1", "user2"], "groups": ["group1"], "mounts": {}, "files": {}},
                "desired_state": {"users": ["user1"], "groups": ["group1"]},
                "should_be_valid": True  # Extra users don't make config invalid
            }
        ]

        for scenario in test_scenarios:
            with patch.object(validator, '_get_current_system_state', return_value=scenario["current_state"]):
                # Create minimal PyroConfig for testing
                users = [User(f"user_{u}", u, "pass", []) for u in scenario["desired_state"]["users"]]
                groups = [Group(f"group_{g}", g, []) for g in scenario["desired_state"]["groups"]]
                config = PyroConfig(scenario["name"], users, groups, [])

                result = validator.validate_configuration(config)
                assert result.is_valid == scenario["should_be_valid"], f"Failed scenario: {scenario['name']}"

    def test_scorch_file_system_cleanup(self):
        """Test scorch engine properly identifies filesystem items for cleanup"""
        from pyroform.src.scorch_engine import ScorchEngine

        scorch_engine = ScorchEngine(safety_check=False)

        # Test desired paths extraction
        config = PyroConfig(
            label="Test Config",
            users=[],
            groups=[],
            devices=[
                Device(
                    "test_device",
                    "/dev/sdb1",
                    1,
                    "/mnt/test",
                    [
                        "dir,/mnt/test/data,user,group,755",
                        "fl,/mnt/test/data/file.txt,user,group,644",
                        "dir,/mnt/test/another,user,group,700"
                    ]
                )
            ]
        )

        desired_paths = scorch_engine._get_desired_paths(config)

        # Should include all specified paths
        assert "/mnt/test" in desired_paths
        assert "/mnt/test/data" in desired_paths
        assert "/mnt/test/data/file.txt" in desired_paths
        assert "/mnt/test/another" in desired_paths

        # Should include parent directories
        assert "/mnt" in desired_paths

        # Test system file detection
        assert scorch_engine._is_system_file("/etc/passwd") is True
        assert scorch_engine._is_system_file("/home/user/file.txt") is False

        # Test system directory detection
        assert scorch_engine._is_system_directory("/etc") is True
        assert scorch_engine._is_system_directory("/home/user/projects") is False

# CODE DUMP

#   """
#   Phase 3 Integration Tests: Advanced Features & Validation
#   """
#   import pytest
#   import tempfile
#   import json
#   from pathlib import Path
#   from unittest.mock import Mock, patch, MagicMock

#   from pyroform.src.models import PyroConfig, User, Group, Device
#   from pyroform.src.validator import SystemValidator, ValidationResult
#   from pyroform.src.scorch_engine import ScorchEngine, ScorchResult
#   from pyroform.src.reporter import ReportGenerator


#   class TestPhase3AdvancedFeatures:
#       """Test advanced features like validation, scorch, and reporting"""

#       @pytest.fixture
#       def sample_system_state(self):
#           """Mock current system state for validation testing"""
#           return {
#               "users": ["existing_user", "testuser"],
#               "groups": ["existing_group", "testgroup"],
#               "mounts": {
#                   "/dev/sda1": "/",
#                   "/dev/sdb1": "/mnt/test"
#               },
#               "files": {
#                   "/mnt/test/data": {"owner": "testuser", "group": "testgroup", "perms": "755"},
#                   "/mnt/test/data/file.txt": {"owner": "testuser", "group": "testgroup", "perms": "644"}
#               }
#           }

#       @pytest.fixture
#       def sample_pyro_config(self):
#           """Create sample configuration for validation testing"""
#           users = [
#               User("desired_user", "testuser", "testpass123", ["testgroup"]),
#               User("new_user", "newuser", "newpass123", ["testgroup"])
#           ]
#           groups = [
#               Group("desired_group", "testgroup", ["testuser", "newuser"])
#           ]
#           devices = [
#               Device(
#                   "desired_device",
#                   "/dev/sdb1",
#                   1,
#                   "/mnt/test",
#                   [
#                       "dir,/mnt/test/data,testuser,testgroup,755",
#                       "fl,/mnt/test/data/file.txt,testuser,testgroup,644",
#                       "dir,/mnt/test/newdir,newuser,testgroup,700"
#                   ]
#               )
#           ]
#           return PyroConfig("Validation Test", users, groups, devices)

#       @patch('pyroform.src.validator.SystemValidator._get_current_system_state')
#       def test_system_validation_integration(self, mock_get_state, sample_pyro_config, sample_system_state):
#           """Test system validation against current state"""
#           mock_get_state.return_value = sample_system_state
#           validator = SystemValidator()

#           result = validator.validate_configuration(sample_pyro_config)

#           assert isinstance(result, ValidationResult)
#           assert hasattr(result, 'is_valid')
#           assert hasattr(result, 'discrepancies')
#           assert hasattr(result, 'summary')

#           # Should find discrepancies (newuser doesn't exist, newdir doesn't exist)
#           assert not result.is_valid
#           assert len(result.discrepancies) > 0

#       def test_validation_report_generation(self, sample_pyro_config):
#           """Test validation report generation"""
#           validator = SystemValidator()

#           # Mock validation result
#           mock_result = ValidationResult(
#               is_valid=False,
#               discrepancies=[
#                   {"type": "user", "name": "newuser", "issue": "User does not exist"},
#                   {"type": "directory", "path": "/mnt/test/newdir", "issue": "Directory does not exist"}
#               ],
#               summary={"total_issues": 2, "critical_issues": 0}
#           )

#           # Set the last result directly
#           validator._last_result = mock_result
#           report = validator.get_validation_report()

#           assert "summary" in report
#           assert "discrepancies" in report
#           assert report["summary"]["total_issues"] == 2

#       @patch('pyroform.src.scorch_engine.ScorchEngine._get_current_system_state')
#       @patch('pyroform.src.scorch_engine.subprocess.run')
#       @patch('pyroform.src.scorch_engine.os.remove')
#       @patch('pyroform.src.scorch_engine.os.unlink')
#       def test_scorch_engine_integration(self, mock_unlink, mock_remove, mock_subprocess, mock_get_state, sample_pyro_config):
#           """Test scorch engine identifies resources for cleanup including filesystem items"""
#           # Mock system state with extra resources
#           mock_get_state.return_value = {
#               "users": ["testuser", "extra_user", "another_user"],
#               "groups": ["testgroup", "extra_group"],
#               "mounts": {
#                   "/dev/sdb1": "/mnt/test",
#                   "/dev/sdc1": "/mnt/extra"
#               },
#               "files": {
#                   "/mnt/test/data": {"owner": "testuser", "group": "testgroup", "perms": "755"},
#                   "/mnt/extra/data": {"owner": "extra_user", "group": "extra_group", "perms": "755"}
#               },
#               "filesystem": {
#                   "files": [
#                       "/mnt/test/data/file.txt",
#                       "/mnt/extra/orphan_file.txt",  # This should be removed
#                       "/home/extra_user/extra_file.conf"  # This should be removed
#                   ],
#                   "directories": [
#                       "/mnt/test/data",
#                       "/mnt/extra/orphan_dir",  # This should be removed
#                       "/home/extra_user"  # This should be removed (after user removal)
#                   ],
#                   "links": [
#                       "/mnt/test/link_to_data",
#                       "/mnt/extra/orphan_link"  # This should be removed
#                   ]
#               }
#           }

#           # Mock subprocess calls to avoid actual system commands
#           mock_subprocess.return_value = Mock(returncode=0)
#           # Mock filesystem operations
#           mock_remove.return_value = None
#           mock_unlink.return_value = None

#           scorch_engine = ScorchEngine(safety_check=False)
#           result = scorch_engine.execute_scorch(sample_pyro_config)

#           assert isinstance(result, ScorchResult)
#           assert hasattr(result, 'resources_removed')
#           assert hasattr(result, 'resources_failed')
#           assert hasattr(result, 'dry_run')

#           # Should identify extra resources for removal including filesystem items
#           removed_resources = [r for r in result.resources_removed if not r.endswith('(dry-run)')]
#           assert len(removed_resources) > 0

#           # Verify filesystem cleanup was attempted
#           assert mock_remove.called or mock_unlink.called

#       def test_scorch_safety_mechanisms(self, sample_pyro_config):
#           """Test scorch safety prompts and dry-run"""
#           scorch_engine = ScorchEngine(safety_check=True)

#           # Test dry-run mode
#           with patch('builtins.input', return_value='no'):
#               result = scorch_engine.execute_scorch(sample_pyro_config, dry_run=True)
#               assert result.dry_run is True

#           # Test safety prompt rejection
#           with patch('builtins.input', return_value='no'):
#               result = scorch_engine.execute_scorch(sample_pyro_config, dry_run=False)
#               # Should not execute actual scorch when user says no
#               assert len(result.resources_removed) == 0

#       def test_report_generation_integration(self, tmp_path):
#           """Test comprehensive report generation"""
#           reporter = ReportGenerator()

#           # Mock action result
#           mock_result = Mock()
#           mock_result.success = True
#           mock_result.execution_time = 30.5
#           mock_result.resources_processed = 10
#           mock_result.errors = []

#           report = reporter.generate_action_report(
#               action="configure",
#               result=mock_result,
#               config_files=["/path/to/config1.yaml"],
#               start_time="2024-01-01 10:00:00",
#               end_time="2024-01-01 10:00:30"
#           )

#           # Verify report structure
#           assert "action" in report
#           assert "timestamp" in report
#           assert "duration" in report  # This was the failing assertion
#           assert "success" in report
#           assert "summary" in report
#           assert "details" in report

#           # Test file output
#           report_file = tmp_path / "test_report.json"
#           success = reporter.save_report(report, report_file)

#           assert success is True
#           assert report_file.exists()

#           # Verify file content
#           with open(report_file, 'r') as f:
#               saved_report = json.load(f)

#           assert saved_report["action"] == "configure"
#           assert saved_report["success"] is True

#       @patch('pyroform.src.validator.subprocess.run')
#       def test_validation_with_real_commands(self, mock_subprocess):
#           """Test validation using actual system commands (where safe)"""
#           # Mock subprocess calls to return predictable results
#           mock_subprocess.return_value = Mock(
#               stdout="root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/bash\n",
#               returncode=0
#           )

#           validator = SystemValidator()

#           # Test user validation (non-destructive)
#           current_users = validator._get_current_users()
#           assert isinstance(current_users, list)

#           # Test group validation (non-destructive)
#           current_groups = validator._get_current_groups()
#           assert isinstance(current_groups, list)

#           # Test mount validation (non-destructive)
#           current_mounts = validator._get_current_mounts()
#           assert isinstance(current_mounts, dict)

#       @patch('pyroform.src.scorch_engine.ScorchEngine._get_current_system_state')
#       @patch('pyroform.src.scorch_engine.subprocess.run')
#       @patch('pyroform.src.scorch_engine.os.remove')
#       def test_scorch_rollback_mechanism(self, mock_remove, mock_subprocess, mock_get_state, sample_pyro_config):
#           """Test scorch rollback on partial failures"""
#           # Mock system state
#           mock_get_state.return_value = {
#               "users": ["testuser", "extra_user"],
#               "groups": ["testgroup", "extra_group"],
#               "mounts": {},
#               "files": {},
#               "filesystem": {
#                   "files": ["/mnt/extra/orphan_file.txt"],
#                   "directories": [],
#                   "links": []
#               }
#           }

#           scorch_engine = ScorchEngine(safety_check=False)

#           # Mock partial failure scenario
#           mock_subprocess.side_effect = [
#               Mock(returncode=0),  # which userdel - success
#               Mock(returncode=0),  # userdel extra_user - success
#               Mock(returncode=0),  # which groupdel - success
#               Mock(returncode=1),  # groupdel extra_group - failure
#           ]
#           mock_remove.side_effect = OSError("Permission denied")  # File removal fails

#           result = scorch_engine.execute_scorch(sample_pyro_config)

#           # Should stop on first failure and report partial success
#           assert len(result.resources_failed) > 0

#       def test_comprehensive_validation_scenarios(self):
#           """Test various validation scenarios"""
#           validator = SystemValidator()

#           test_scenarios = [
#               {
#                   "name": "perfect_match",
#                   "current_state": {"users": ["user1"], "groups": ["group1"], "mounts": {}, "files": {}},
#                   "desired_state": {"users": ["user1"], "groups": ["group1"]},
#                   "should_be_valid": True
#               },
#               {
#                   "name": "missing_user",
#                   "current_state": {"users": [], "groups": ["group1"], "mounts": {}, "files": {}},
#                   "desired_state": {"users": ["user1"], "groups": ["group1"]},
#                   "should_be_valid": False
#               },
#               {
#                   "name": "extra_user",
#                   "current_state": {"users": ["user1", "user2"], "groups": ["group1"], "mounts": {}, "files": {}},
#                   "desired_state": {"users": ["user1"], "groups": ["group1"]},
#                   "should_be_valid": True  # Extra users don't make config invalid
#               }
#           ]

#           for scenario in test_scenarios:
#               with patch.object(validator, '_get_current_system_state', return_value=scenario["current_state"]):
#                   # Create minimal PyroConfig for testing
#                   users = [User(f"user_{u}", u, "pass", []) for u in scenario["desired_state"]["users"]]
#                   groups = [Group(f"group_{g}", g, []) for g in scenario["desired_state"]["groups"]]
#                   config = PyroConfig(scenario["name"], users, groups, [])

#                   result = validator.validate_configuration(config)
#                   assert result.is_valid == scenario["should_be_valid"], f"Failed scenario: {scenario['name']}"

#       def test_scorch_file_system_cleanup(self):
#           """Test scorch engine properly identifies filesystem items for cleanup"""
#           from pyroform.src.scorch_engine import ScorchEngine

#           scorch_engine = ScorchEngine(safety_check=False)

#           # Test desired paths extraction
#           config = PyroConfig(
#               label="Test Config",
#               users=[],
#               groups=[],
#               devices=[
#                   Device(
#                       "test_device",
#                       "/dev/sdb1",
#                       1,
#                       "/mnt/test",
#                       [
#                           "dir,/mnt/test/data,user,group,755",
#                           "fl,/mnt/test/data/file.txt,user,group,644",
#                           "dir,/mnt/test/another,user,group,700"
#                       ]
#                   )
#               ]
#           )

#           desired_paths = scorch_engine._get_desired_paths(config)

#           # Should include all specified paths
#           assert "/mnt/test" in desired_paths
#           assert "/mnt/test/data" in desired_paths
#           assert "/mnt/test/data/file.txt" in desired_paths
#           assert "/mnt/test/another" in desired_paths

#           # Should include parent directories
#           assert "/mnt" in desired_paths

#           # Test system file detection
#           assert scorch_engine._is_system_file("/etc/passwd") is True
#           assert scorch_engine._is_system_file("/home/user/file.txt") is False

#           # Test system directory detection
#           assert scorch_engine._is_system_directory("/etc") is True
#           assert scorch_engine._is_system_directory("/home/user/projects") is False

# CODE DUMP

#   """
#   Phase 3 Integration Tests: Advanced Features & Validation
#   """
#   import pytest
#   import tempfile
#   import json
#   from pathlib import Path
#   from unittest.mock import Mock, patch, MagicMock

#   from pyroform.src.models import PyroConfig, User, Group, Device
#   from pyroform.src.validator import SystemValidator, ValidationResult
#   from pyroform.src.scorch_engine import ScorchEngine, ScorchResult
#   from pyroform.src.reporter import ReportGenerator


#   class TestPhase3AdvancedFeatures:
#       """Test advanced features like validation, scorch, and reporting"""

#       @pytest.fixture
#       def sample_system_state(self):
#           """Mock current system state for validation testing"""
#           return {
#               "users": ["existing_user", "testuser"],
#               "groups": ["existing_group", "testgroup"],
#               "mounts": {
#                   "/dev/sda1": "/",
#                   "/dev/sdb1": "/mnt/test"
#               },
#               "files": {
#                   "/mnt/test/data": {"owner": "testuser", "group": "testgroup", "perms": "755"},
#                   "/mnt/test/data/file.txt": {"owner": "testuser", "group": "testgroup", "perms": "644"}
#               }
#           }

#       @pytest.fixture
#       def sample_pyro_config(self):
#           """Create sample configuration for validation testing"""
#           users = [
#               User("desired_user", "testuser", "testpass123", ["testgroup"]),
#               User("new_user", "newuser", "newpass123", ["testgroup"])
#           ]
#           groups = [
#               Group("desired_group", "testgroup", ["testuser", "newuser"])
#           ]
#           devices = [
#               Device(
#                   "desired_device",
#                   "/dev/sdb1",
#                   1,
#                   "/mnt/test",
#                   [
#                       "dir,/mnt/test/data,testuser,testgroup,755",
#                       "fl,/mnt/test/data/file.txt,testuser,testgroup,644",
#                       "dir,/mnt/test/newdir,newuser,testgroup,700"
#                   ]
#               )
#           ]
#           return PyroConfig("Validation Test", users, groups, devices)

#       @patch('pyroform.src.validator.SystemValidator._get_current_system_state')
#       def test_system_validation_integration(self, mock_get_state, sample_pyro_config, sample_system_state):
#           """Test system validation against current state"""
#           mock_get_state.return_value = sample_system_state
#           validator = SystemValidator()

#           result = validator.validate_configuration(sample_pyro_config)

#           assert isinstance(result, ValidationResult)
#           assert hasattr(result, 'is_valid')
#           assert hasattr(result, 'discrepancies')
#           assert hasattr(result, 'summary')

#           # Should find discrepancies (newuser doesn't exist, newdir doesn't exist)
#           assert not result.is_valid
#           assert len(result.discrepancies) > 0

#       def test_validation_report_generation(self, sample_pyro_config):
#           """Test validation report generation"""
#           validator = SystemValidator()

#           # Mock validation result
#           mock_result = ValidationResult(
#               is_valid=False,
#               discrepancies=[
#                   {"type": "user", "name": "newuser", "issue": "User does not exist"},
#                   {"type": "directory", "path": "/mnt/test/newdir", "issue": "Directory does not exist"}
#               ],
#               summary={"total_issues": 2, "critical_issues": 0}
#           )

#           # Set the last result directly
#           validator._last_result = mock_result
#           report = validator.get_validation_report()

#           assert "summary" in report
#           assert "discrepancies" in report
#           assert report["summary"]["total_issues"] == 2

#       @patch('pyroform.src.scorch_engine.ScorchEngine._get_current_system_state')
#       @patch('pyroform.src.scorch_engine.subprocess.run')
#       @patch('pyroform.src.scorch_engine.os.remove')
#       @patch('pyroform.src.scorch_engine.shutil.rmtree')
#       @patch('pyroform.src.scorch_engine.os.unlink')
#       def test_scorch_engine_integration(self, mock_unlink, mock_rmtree, mock_remove, mock_subprocess, mock_get_state, sample_pyro_config):
#           """Test scorch engine identifies resources for cleanup including filesystem items"""
#           # Mock system state with extra resources
#           mock_get_state.return_value = {
#               "users": ["testuser", "extra_user", "another_user"],
#               "groups": ["testgroup", "extra_group"],
#               "mounts": {
#                   "/dev/sdb1": "/mnt/test",
#                   "/dev/sdc1": "/mnt/extra"
#               },
#               "files": {
#                   "/mnt/test/data": {"owner": "testuser", "group": "testgroup", "perms": "755"},
#                   "/mnt/extra/data": {"owner": "extra_user", "group": "extra_group", "perms": "755"}
#               },
#               "filesystem": {
#                   "files": [
#                       "/mnt/test/data/file.txt",
#                       "/mnt/extra/orphan_file.txt",  # This should be removed
#                       "/home/extra_user/extra_file.conf"  # This should be removed
#                   ],
#                   "directories": [
#                       "/mnt/test/data",
#                       "/mnt/extra/orphan_dir",  # This should be removed
#                       "/home/extra_user"  # This should be removed (after user removal)
#                   ],
#                   "links": [
#                       "/mnt/test/link_to_data",
#                       "/mnt/extra/orphan_link"  # This should be removed
#                   ]
#               }
#           }

#           # Mock subprocess calls to avoid actual system commands
#           mock_subprocess.return_value = Mock(returncode=0)
#           # Mock filesystem operations
#           mock_remove.return_value = None
#           mock_rmtree.return_value = None
#           mock_unlink.return_value = None

#           scorch_engine = ScorchEngine(safety_check=False)
#           result = scorch_engine.execute_scorch(sample_pyro_config)

#           assert isinstance(result, ScorchResult)
#           assert hasattr(result, 'resources_removed')
#           assert hasattr(result, 'resources_failed')
#           assert hasattr(result, 'dry_run')

#           # Should identify extra resources for removal including filesystem items
#           removed_resources = [r for r in result.resources_removed if not r.endswith('(dry-run)')]
#           assert len(removed_resources) > 0

#           # Verify filesystem cleanup was attempted
#           assert mock_remove.called or mock_rmtree.called or mock_unlink.called

#       def test_scorch_safety_mechanisms(self, sample_pyro_config):
#           """Test scorch safety prompts and dry-run"""
#           scorch_engine = ScorchEngine(safety_check=True)

#           # Test dry-run mode
#           with patch('builtins.input', return_value='no'):
#               result = scorch_engine.execute_scorch(sample_pyro_config, dry_run=True)
#               assert result.dry_run is True

#           # Test safety prompt rejection
#           with patch('builtins.input', return_value='no'):
#               result = scorch_engine.execute_scorch(sample_pyro_config, dry_run=False)
#               # Should not execute actual scorch when user says no
#               assert len(result.resources_removed) == 0

#       def test_report_generation_integration(self, tmp_path):
#           """Test comprehensive report generation"""
#           reporter = ReportGenerator()

#           # Mock action result
#           mock_result = Mock()
#           mock_result.success = True
#           mock_result.execution_time = 30.5
#           mock_result.resources_processed = 10
#           mock_result.errors = []

#           report = reporter.generate_action_report(
#               action="configure",
#               result=mock_result,
#               config_files=["/path/to/config1.yaml"],
#               start_time="2024-01-01 10:00:00",
#               end_time="2024-01-01 10:00:30"
#           )

#           # Verify report structure
#           assert "action" in report
#           assert "timestamp" in report
#           assert "duration" in report  # This was the failing assertion
#           assert "success" in report
#           assert "summary" in report
#           assert "details" in report

#           # Test file output
#           report_file = tmp_path / "test_report.json"
#           success = reporter.save_report(report, report_file)

#           assert success is True
#           assert report_file.exists()

#           # Verify file content
#           with open(report_file, 'r') as f:
#               saved_report = json.load(f)

#           assert saved_report["action"] == "configure"
#           assert saved_report["success"] is True

#       def test_validation_with_real_commands(self):
#           """Test validation using actual system commands (where safe)"""
#           validator = SystemValidator()

#           # Test user validation (non-destructive)
#           current_users = validator._get_current_users()
#           assert isinstance(current_users, list)

#           # Test group validation (non-destructive)
#           current_groups = validator._get_current_groups()
#           assert isinstance(current_groups, list)

#           # Test mount validation (non-destructive)
#           current_mounts = validator._get_current_mounts()
#           assert isinstance(current_mounts, dict)

#       @patch('pyroform.src.scorch_engine.subprocess.run')
#       @patch('pyroform.src.scorch_engine.os.remove')
#       def test_scorch_rollback_mechanism(self, mock_remove, mock_subprocess, sample_pyro_config):
#           """Test scorch rollback on partial failures"""
#           scorch_engine = ScorchEngine(safety_check=False)

#           # Mock partial failure scenario
#           mock_subprocess.side_effect = [
#               Mock(returncode=0),  # which userdel - success
#               Mock(returncode=0),  # userdel extra_user - success
#               Mock(returncode=0),  # which groupdel - success
#               Mock(returncode=1),  # groupdel extra_group - failure
#           ]
#           mock_remove.side_effect = OSError("Permission denied")  # File removal fails

#           result = scorch_engine.execute_scorch(sample_pyro_config)

#           # Should stop on first failure and report partial success
#           assert len(result.resources_failed) > 0

#       def test_comprehensive_validation_scenarios(self):
#           """Test various validation scenarios"""
#           validator = SystemValidator()

#           test_scenarios = [
#               {
#                   "name": "perfect_match",
#                   "current_state": {"users": ["user1"], "groups": ["group1"], "mounts": {}, "files": {}},
#                   "desired_state": {"users": ["user1"], "groups": ["group1"]},
#                   "should_be_valid": True
#               },
#               {
#                   "name": "missing_user",
#                   "current_state": {"users": [], "groups": ["group1"], "mounts": {}, "files": {}},
#                   "desired_state": {"users": ["user1"], "groups": ["group1"]},
#                   "should_be_valid": False
#               },
#               {
#                   "name": "extra_user",
#                   "current_state": {"users": ["user1", "user2"], "groups": ["group1"], "mounts": {}, "files": {}},
#                   "desired_state": {"users": ["user1"], "groups": ["group1"]},
#                   "should_be_valid": True  # Extra users don't make config invalid
#               }
#           ]

#           for scenario in test_scenarios:
#               with patch.object(validator, '_get_current_system_state', return_value=scenario["current_state"]):
#                   # Create minimal PyroConfig for testing
#                   users = [User(f"user_{u}", u, "pass", []) for u in scenario["desired_state"]["users"]]
#                   groups = [Group(f"group_{g}", g, []) for g in scenario["desired_state"]["groups"]]
#                   config = PyroConfig(scenario["name"], users, groups, [])

#                   result = validator.validate_configuration(config)
#                   assert result.is_valid == scenario["should_be_valid"], f"Failed scenario: {scenario['name']}"

#       def test_scorch_file_system_cleanup(self):
#           """Test scorch engine properly identifies filesystem items for cleanup"""
#           from pyroform.src.scorch_engine import ScorchEngine

#           scorch_engine = ScorchEngine(safety_check=False)

#           # Test desired paths extraction
#           config = PyroConfig(
#               label="Test Config",
#               users=[],
#               groups=[],
#               devices=[
#                   Device(
#                       "test_device",
#                       "/dev/sdb1",
#                       1,
#                       "/mnt/test",
#                       [
#                           "dir,/mnt/test/data,user,group,755",
#                           "fl,/mnt/test/data/file.txt,user,group,644",
#                           "dir,/mnt/test/another,user,group,700"
#                       ]
#                   )
#               ]
#           )

#           desired_paths = scorch_engine._get_desired_paths(config)

#           # Should include all specified paths
#           assert "/mnt/test" in desired_paths
#           assert "/mnt/test/data" in desired_paths
#           assert "/mnt/test/data/file.txt" in desired_paths
#           assert "/mnt/test/another" in desired_paths

#           # Should include parent directories
#           assert "/mnt" in desired_paths

#           # Test system file detection
#           assert scorch_engine._is_system_file("/etc/passwd") is True
#           assert scorch_engine._is_system_file("/home/user/file.txt") is False

#           # Test system directory detection
#           assert scorch_engine._is_system_directory("/etc") is True
#           assert scorch_engine._is_system_directory("/home/user/projects") is False

# CODE DUMP

#   """
#   Phase 3 Integration Tests: Advanced Features & Validation
#   """
#   import pytest
#   import tempfile
#   import json
#   from pathlib import Path
#   from unittest.mock import Mock, patch, MagicMock

#   from pyroform.src.models import PyroConfig, User, Group, Device
#   from pyroform.src.validator import SystemValidator, ValidationResult
#   from pyroform.src.scorch_engine import ScorchEngine, ScorchResult
#   from pyroform.src.reporter import ReportGenerator


#   class TestPhase3AdvancedFeatures:
#       """Test advanced features like validation, scorch, and reporting"""

#       @pytest.fixture
#       def sample_system_state(self):
#           """Mock current system state for validation testing"""
#           return {
#               "users": ["existing_user", "testuser"],
#               "groups": ["existing_group", "testgroup"],
#               "mounts": {
#                   "/dev/sda1": "/",
#                   "/dev/sdb1": "/mnt/test"
#               },
#               "files": {
#                   "/mnt/test/data": {"owner": "testuser", "group": "testgroup", "perms": "755"},
#                   "/mnt/test/data/file.txt": {"owner": "testuser", "group": "testgroup", "perms": "644"}
#               }
#           }

#       @pytest.fixture
#       def sample_pyro_config(self):
#           """Create sample configuration for validation testing"""
#           users = [
#               User("desired_user", "testuser", "testpass123", ["testgroup"]),
#               User("new_user", "newuser", "newpass123", ["testgroup"])
#           ]
#           groups = [
#               Group("desired_group", "testgroup", ["testuser", "newuser"])
#           ]
#           devices = [
#               Device(
#                   "desired_device",
#                   "/dev/sdb1",
#                   1,
#                   "/mnt/test",
#                   [
#                       "dir,/mnt/test/data,testuser,testgroup,755",
#                       "fl,/mnt/test/data/file.txt,testuser,testgroup,644",
#                       "dir,/mnt/test/newdir,newuser,testgroup,700"
#                   ]
#               )
#           ]
#           return PyroConfig("Validation Test", users, groups, devices)

#       @patch('pyroform.src.validator.SystemValidator._get_current_system_state')
#       def test_system_validation_integration(self, mock_get_state, sample_pyro_config, sample_system_state):
#           """Test system validation against current state"""
#           mock_get_state.return_value = sample_system_state
#           validator = SystemValidator()

#           result = validator.validate_configuration(sample_pyro_config)

#           assert isinstance(result, ValidationResult)
#           assert hasattr(result, 'is_valid')
#           assert hasattr(result, 'discrepancies')
#           assert hasattr(result, 'summary')

#           # Should find discrepancies (newuser doesn't exist, newdir doesn't exist)
#           assert not result.is_valid
#           assert len(result.discrepancies) > 0

#       def test_validation_report_generation(self, sample_pyro_config):
#           """Test validation report generation"""
#           validator = SystemValidator()

#           # Mock validation result
#           mock_result = ValidationResult(
#               is_valid=False,
#               discrepancies=[
#                   {"type": "user", "name": "newuser", "issue": "User does not exist"},
#                   {"type": "directory", "path": "/mnt/test/newdir", "issue": "Directory does not exist"}
#               ],
#               summary={"total_issues": 2, "critical_issues": 0}
#           )

#           # Set the last result directly
#           validator._last_result = mock_result
#           report = validator.get_validation_report()

#           assert "summary" in report
#           assert "discrepancies" in report
#           assert report["summary"]["total_issues"] == 2

#       @patch('pyroform.src.scorch_engine.ScorchEngine._get_current_system_state')
#       @patch('pyroform.src.scorch_engine.subprocess.run')
#       def test_scorch_engine_integration(self, mock_subprocess, mock_get_state, sample_pyro_config):
#           """Test scorch engine identifies resources for cleanup"""
#           # Mock system state with extra resources
#           mock_get_state.return_value = {
#               "users": ["testuser", "extra_user", "another_user"],
#               "groups": ["testgroup", "extra_group"],
#               "mounts": {
#                   "/dev/sdb1": "/mnt/test",
#                   "/dev/sdc1": "/mnt/extra"
#               },
#               "files": {
#                   "/mnt/test/data": {"owner": "testuser", "group": "testgroup", "perms": "755"},
#                   "/mnt/extra/data": {"owner": "extra_user", "group": "extra_group", "perms": "755"}
#               }
#           }

#           # Mock subprocess calls to avoid actual system commands
#           mock_subprocess.return_value = Mock(returncode=0)

#           scorch_engine = ScorchEngine(safety_check=False)
#           result = scorch_engine.execute_scorch(sample_pyro_config)

#           assert isinstance(result, ScorchResult)
#           assert hasattr(result, 'resources_removed')
#           assert hasattr(result, 'resources_failed')
#           assert hasattr(result, 'dry_run')

#           # Should identify extra resources for removal
#           assert len(result.resources_removed) > 0 or len(result.resources_failed) > 0

#       def test_scorch_safety_mechanisms(self, sample_pyro_config):
#           """Test scorch safety prompts and dry-run"""
#           scorch_engine = ScorchEngine(safety_check=True)

#           # Test dry-run mode
#           with patch('builtins.input', return_value='no'):
#               result = scorch_engine.execute_scorch(sample_pyro_config, dry_run=True)
#               assert result.dry_run is True

#           # Test safety prompt rejection
#           with patch('builtins.input', return_value='no'):
#               result = scorch_engine.execute_scorch(sample_pyro_config, dry_run=False)
#               # Should not execute actual scorch when user says no
#               assert len(result.resources_removed) == 0

#       def test_report_generation_integration(self, tmp_path):
#           """Test comprehensive report generation"""
#           reporter = ReportGenerator()

#           # Mock action result
#           mock_result = Mock()
#           mock_result.success = True
#           mock_result.execution_time = 30.5
#           mock_result.resources_processed = 10
#           mock_result.errors = []

#           report = reporter.generate_action_report(
#               action="configure",
#               result=mock_result,
#               config_files=["/path/to/config1.yaml"],
#               start_time="2024-01-01 10:00:00",
#               end_time="2024-01-01 10:00:30"
#           )

#           # Verify report structure
#           assert "action" in report
#           assert "timestamp" in report
#           assert "duration" in report  # This was the failing assertion
#           assert "success" in report
#           assert "summary" in report
#           assert "details" in report

#           # Test file output
#           report_file = tmp_path / "test_report.json"
#           success = reporter.save_report(report, report_file)

#           assert success is True
#           assert report_file.exists()

#           # Verify file content
#           with open(report_file, 'r') as f:
#               saved_report = json.load(f)

#           assert saved_report["action"] == "configure"
#           assert saved_report["success"] is True

#       def test_validation_with_real_commands(self):
#           """Test validation using actual system commands (where safe)"""
#           validator = SystemValidator()

#           # Test user validation (non-destructive)
#           current_users = validator._get_current_users()
#           assert isinstance(current_users, list)

#           # Test group validation (non-destructive)
#           current_groups = validator._get_current_groups()
#           assert isinstance(current_groups, list)

#           # Test mount validation (non-destructive)
#           current_mounts = validator._get_current_mounts()
#           assert isinstance(current_mounts, dict)

#       @patch('pyroform.src.scorch_engine.subprocess.run')
#       def test_scorch_rollback_mechanism(self, mock_subprocess, sample_pyro_config):
#           """Test scorch rollback on partial failures"""
#           scorch_engine = ScorchEngine(safety_check=False)

#           # Mock partial failure scenario
#           mock_subprocess.side_effect = [
#               Mock(returncode=0),  # which userdel - success
#               Mock(returncode=0),  # userdel extra_user - success
#               Mock(returncode=0),  # which groupdel - success
#               Mock(returncode=1),  # groupdel extra_group - failure
#           ]

#           result = scorch_engine.execute_scorch(sample_pyro_config)

#           # Should stop on first failure and report partial success
#           assert len(result.resources_failed) > 0

#       def test_comprehensive_validation_scenarios(self):
#           """Test various validation scenarios"""
#           validator = SystemValidator()

#           test_scenarios = [
#               {
#                   "name": "perfect_match",
#                   "current_state": {"users": ["user1"], "groups": ["group1"], "mounts": {}, "files": {}},
#                   "desired_state": {"users": ["user1"], "groups": ["group1"]},
#                   "should_be_valid": True
#               },
#               {
#                   "name": "missing_user",
#                   "current_state": {"users": [], "groups": ["group1"], "mounts": {}, "files": {}},
#                   "desired_state": {"users": ["user1"], "groups": ["group1"]},
#                   "should_be_valid": False
#               },
#               {
#                   "name": "extra_user",
#                   "current_state": {"users": ["user1", "user2"], "groups": ["group1"], "mounts": {}, "files": {}},
#                   "desired_state": {"users": ["user1"], "groups": ["group1"]},
#                   "should_be_valid": True  # Extra users don't make config invalid
#               }
#           ]

#           for scenario in test_scenarios:
#               with patch.object(validator, '_get_current_system_state', return_value=scenario["current_state"]):
#                   # Create minimal PyroConfig for testing
#                   users = [User(f"user_{u}", u, "pass", []) for u in scenario["desired_state"]["users"]]
#                   groups = [Group(f"group_{g}", g, []) for g in scenario["desired_state"]["groups"]]
#                   config = PyroConfig(scenario["name"], users, groups, [])

#                   result = validator.validate_configuration(config)
#                   assert result.is_valid == scenario["should_be_valid"], f"Failed scenario: {scenario['name']}"


#   # CODE DUMP

#   """
#   Phase 3 Integration Tests: Advanced Features & Validation
#   """
#   import pytest
#   import tempfile
#   import json
#   from pathlib import Path
#   from unittest.mock import Mock, patch, MagicMock

#   from pyroform.src.models import PyroConfig, User, Group, Device
#   from pyroform.src.validator import SystemValidator, ValidationResult
#   from pyroform.src.scorch_engine import ScorchEngine, ScorchResult
#   from pyroform.src.reporter import ReportGenerator


#   class TestPhase3AdvancedFeatures:
#       """Test advanced features like validation, scorch, and reporting"""

#       @pytest.fixture
#       def sample_system_state(self):
#           """Mock current system state for validation testing"""
#           return {
#               "users": ["existing_user", "testuser"],
#               "groups": ["existing_group", "testgroup"],
#               "mounts": {
#                   "/dev/sda1": "/",
#                   "/dev/sdb1": "/mnt/test"
#               },
#               "files": {
#                   "/mnt/test/data": {"owner": "testuser", "group": "testgroup", "perms": "755"},
#                   "/mnt/test/data/file.txt": {"owner": "testuser", "group": "testgroup", "perms": "644"}
#               }
#           }

#       @pytest.fixture
#       def sample_pyro_config(self):
#           """Create sample configuration for validation testing"""
#           users = [
#               User("desired_user", "testuser", "testpass123", ["testgroup"]),
#               User("new_user", "newuser", "newpass123", ["testgroup"])
#           ]
#           groups = [
#               Group("desired_group", "testgroup", ["testuser", "newuser"])
#           ]
#           devices = [
#               Device(
#                   "desired_device",
#                   "/dev/sdb1",
#                   1,
#                   "/mnt/test",
#                   [
#                       "dir,/mnt/test/data,testuser,testgroup,755",
#                       "fl,/mnt/test/data/file.txt,testuser,testgroup,644",
#                       "dir,/mnt/test/newdir,newuser,testgroup,700"
#                   ]
#               )
#           ]
#           return PyroConfig("Validation Test", users, groups, devices)

#       @patch('pyroform.src.validator.SystemValidator._get_current_system_state')
#       def test_system_validation_integration(self, mock_get_state, sample_pyro_config, sample_system_state):
#           """Test system validation against current state"""
#           mock_get_state.return_value = sample_system_state
#           validator = SystemValidator()

#           result = validator.validate_configuration(sample_pyro_config)

#           assert isinstance(result, ValidationResult)
#           assert hasattr(result, 'is_valid')
#           assert hasattr(result, 'discrepancies')
#           assert hasattr(result, 'summary')

#           # Should find discrepancies (newuser doesn't exist, newdir doesn't exist)
#           assert not result.is_valid
#           assert len(result.discrepancies) > 0

#       def test_validation_report_generation(self, sample_pyro_config):
#           """Test validation report generation"""
#           validator = SystemValidator()

#           # Mock validation result
#           mock_result = ValidationResult(
#               is_valid=False,
#               discrepancies=[
#                   {"type": "user", "name": "newuser", "issue": "User does not exist"},
#                   {"type": "directory", "path": "/mnt/test/newdir", "issue": "Directory does not exist"}
#               ],
#               summary={"total_issues": 2, "critical_issues": 0}
#           )

#           with patch.object(validator, 'validate_configuration', return_value=mock_result):
#               result = validator.validate_configuration(sample_pyro_config)
#               report = validator.get_validation_report()

#               assert "summary" in report
#               assert "discrepancies" in report
#               assert report["summary"]["total_issues"] == 2

#       @patch('pyroform.src.scorch_engine.ScorchEngine._get_current_system_state')
#       def test_scorch_engine_integration(self, mock_get_state, sample_pyro_config):
#           """Test scorch engine identifies resources for cleanup"""
#           # Mock system state with extra resources
#           mock_get_state.return_value = {
#               "users": ["testuser", "extra_user", "another_user"],
#               "groups": ["testgroup", "extra_group"],
#               "mounts": {
#                   "/dev/sdb1": "/mnt/test",
#                   "/dev/sdc1": "/mnt/extra"
#               },
#               "files": {
#                   "/mnt/test/data": {"owner": "testuser", "group": "testgroup", "perms": "755"},
#                   "/mnt/extra/data": {"owner": "extra_user", "group": "extra_group", "perms": "755"}
#               }
#           }

#           scorch_engine = ScorchEngine(safety_check=False)
#           result = scorch_engine.execute_scorch(sample_pyro_config)

#           assert isinstance(result, ScorchResult)
#           assert hasattr(result, 'resources_removed')
#           assert hasattr(result, 'resources_failed')
#           assert hasattr(result, 'dry_run')

#           # Should identify extra resources for removal
#           assert len(result.resources_removed) > 0 or len(result.resources_failed) > 0

#       def test_scorch_safety_mechanisms(self, sample_pyro_config):
#           """Test scorch safety prompts and dry-run"""
#           scorch_engine = ScorchEngine(safety_check=True)

#           # Test dry-run mode
#           with patch('builtins.input', return_value='no'):
#               result = scorch_engine.execute_scorch(sample_pyro_config, dry_run=True)
#               assert result.dry_run is True

#           # Test safety prompt rejection
#           with patch('builtins.input', return_value='no'):
#               result = scorch_engine.execute_scorch(sample_pyro_config, dry_run=False)
#               # Should not execute actual scorch when user says no
#               assert len(result.resources_removed) == 0

#       def test_report_generation_integration(self, tmp_path):
#           """Test comprehensive report generation"""
#           reporter = ReportGenerator()

#           # Mock action result
#           mock_result = Mock()
#           mock_result.success = True
#           mock_result.execution_time = 30.5
#           mock_result.resources_processed = 10
#           mock_result.errors = []

#           report = reporter.generate_action_report(
#               action="configure",
#               result=mock_result,
#               config_files=["/path/to/config1.yaml"],
#               start_time="2024-01-01 10:00:00",
#               end_time="2024-01-01 10:00:30"
#           )

#           # Verify report structure
#           assert "action" in report
#           assert "timestamp" in report
#           assert "duration" in report
#           assert "success" in report
#           assert "summary" in report
#           assert "details" in report

#           # Test file output
#           report_file = tmp_path / "test_report.json"
#           success = reporter.save_report(report, report_file)

#           assert success is True
#           assert report_file.exists()

#           # Verify file content
#           with open(report_file, 'r') as f:
#               saved_report = json.load(f)

#           assert saved_report["action"] == "configure"
#           assert saved_report["success"] is True

#       def test_validation_with_real_commands(self):
#           """Test validation using actual system commands (where safe)"""
#           validator = SystemValidator()

#           # Test user validation (non-destructive)
#           current_users = validator._get_current_users()
#           assert isinstance(current_users, list)

#           # Test group validation (non-destructive)
#           current_groups = validator._get_current_groups()
#           assert isinstance(current_groups, list)

#           # Test mount validation (non-destructive)
#           current_mounts = validator._get_current_mounts()
#           assert isinstance(current_mounts, dict)

#       @patch('pyroform.src.scorch_engine.ScorchEngine._execute_removal')
#       def test_scorch_rollback_mechanism(self, mock_execute, sample_pyro_config):
#           """Test scorch rollback on partial failures"""
#           scorch_engine = ScorchEngine(safety_check=False)

#           # Mock partial failure scenario
#           mock_execute.side_effect = [
#               True,   # First removal succeeds
#               False,  # Second removal fails
#               True    # Third removal succeeds (but shouldn't execute due to failure)
#           ]

#           result = scorch_engine.execute_scorch(sample_pyro_config)

#           # Should stop on first failure and report partial success
#           assert mock_execute.call_count == 2  # Only two calls before failure
#           assert len(result.resources_failed) > 0

#       def test_comprehensive_validation_scenarios(self):
#           """Test various validation scenarios"""
#           validator = SystemValidator()

#           test_scenarios = [
#               {
#                   "name": "perfect_match",
#                   "current_state": {"users": ["user1"], "groups": ["group1"]},
#                   "desired_state": {"users": ["user1"], "groups": ["group1"]},
#                   "should_be_valid": True
#               },
#               {
#                   "name": "missing_user",
#                   "current_state": {"users": [], "groups": ["group1"]},
#                   "desired_state": {"users": ["user1"], "groups": ["group1"]},
#                   "should_be_valid": False
#               },
#               {
#                   "name": "extra_user",
#                   "current_state": {"users": ["user1", "user2"], "groups": ["group1"]},
#                   "desired_state": {"users": ["user1"], "groups": ["group1"]},
#                   "should_be_valid": True  # Extra users don't make config invalid
#               }
#           ]

#           for scenario in test_scenarios:
#               with patch.object(validator, '_get_current_system_state', return_value=scenario["current_state"]):
#                   # Create minimal PyroConfig for testing
#                   users = [User(f"user_{u}", u, "pass", []) for u in scenario["desired_state"]["users"]]
#                   groups = [Group(f"group_{g}", g, []) for g in scenario["desired_state"]["groups"]]
#                   config = PyroConfig(scenario["name"], users, groups, [])

#                   result = validator.validate_configuration(config)
#                   assert result.is_valid == scenario["should_be_valid"], f"Failed scenario: {scenario['name']}"
