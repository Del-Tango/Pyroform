"""
Integration Tests: Library API & Integration
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

from pyroform import Pyroform
from pyroform.src.models import ActionType


class TestLibraryAPI:
    """Test library API and integration capabilities"""

    @pytest.fixture
    def sample_pyro_file(self):
        """Create a sample Pyro file for library testing"""
        config = {
            "Label": "Library Test Config",
            "Users": [
                {
                    "label": "lib_user",
                    "Name": "libuser",
                    "Password": "libpass123",
                    "Groups": ["libgroup"],
                }
            ],
            "Groups": [
                {"label": "lib_group", "Name": "libgroup", "Users": ["libuser"]}
            ],
            "Devices": [],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            yield Path(f.name)

        # Cleanup
        if Path(f.name).exists():
            Path(f.name).unlink()

    @pytest.fixture
    def mock_pyroform_engine(self):
        """Mock the internal Pyroform engine"""
        with patch("pyroform.pyroform.PyroformEngine") as mock_engine_class:
            mock_engine = Mock()
            mock_engine.configure.return_value = True
            mock_engine.scorch.return_value = Mock(
                resources_removed=[], resources_failed=[], dry_run=False, success=True
            )
            mock_engine.mount.return_value = True
            mock_engine.validate.return_value = Mock(
                is_valid=True,
                discrepancies=[],
                summary={"total_issues": 0, "critical_issues": 0},
            )
            mock_engine_class.return_value = mock_engine
            yield mock_engine

    def test_library_initialization(self):
        """Test Pyroform library can be initialized"""
        # Test default initialization
        pf = Pyroform()
        assert pf.auto_confirm is False

        # Test with auto-confirm
        pf_auto = Pyroform(auto_confirm=True)
        assert pf_auto.auto_confirm is True

        # Test with config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as f:
            f.write("defaults:\n  safety_checks: true\n")
            pf_config = Pyroform(config_file=f.name)
            assert pf_config.engine is not None

    def test_library_action_methods(self, sample_pyro_file, mock_pyroform_engine):
        """Test all library action methods"""
        pf = Pyroform(auto_confirm=True)

        # Test configure action
        result = pf.configure(str(sample_pyro_file))
        assert result is True
        pf.engine.configure.assert_called_once()

        # Test scorch action
        result = pf.scorch(str(sample_pyro_file))
        assert isinstance(result, Mock)  # Our mock ScorchResult
        pf.engine.scorch.assert_called_once()

        # Test mount action
        result = pf.mount(str(sample_pyro_file))
        assert result is True
        pf.engine.mount.assert_called_once()

        # Test validate action
        result = pf.validate(str(sample_pyro_file))
        assert result.is_valid is True
        pf.engine.validate.assert_called_once()

    def test_library_error_handling(self, sample_pyro_file, mock_pyroform_engine):
        """Test library error handling and propagation"""
        pf = Pyroform(auto_confirm=True)

        # Test engine failure
        pf.engine.configure.return_value = False
        result = pf.configure(str(sample_pyro_file))
        assert result is False

        # Test exception handling
        pf.engine.mount.side_effect = Exception("Mount failed")
        with pytest.raises(Exception, match="Mount failed"):
            pf.mount(str(sample_pyro_file))

    def test_library_with_kwargs(self, sample_pyro_file, mock_pyroform_engine):
        """Test library methods accept and pass kwargs"""
        pf = Pyroform(auto_confirm=True)

        kwargs = {"dry_run": True, "verbose": True, "output_dir": "/tmp/output"}

        pf.configure(str(sample_pyro_file), **kwargs)

        # The call should include both our kwargs and auto_confirm
        expected_kwargs = kwargs.copy()
        expected_kwargs["auto_confirm"] = True
        pf.engine.configure.assert_called_with(str(sample_pyro_file), **expected_kwargs)

    def test_module_level_imports(self):
        """Test that module-level imports work correctly"""
        # Test core classes are importable
        from pyroform import Pyroform
        from pyroform.src.models import PyroConfig

        assert Pyroform is not None
        assert PyroConfig is not None
        assert ActionType is not None

    def test_library_in_other_context(self):
        """Test library can be used in different contexts"""
        # Simulate usage in another script
        with patch("pyroform.pyroform.PyroformEngine") as mock_engine:
            mock_engine.return_value.configure.return_value = True

            # This simulates how users would import and use Pyroform
            from pyroform import Pyroform

            pf = Pyroform(auto_confirm=True)
            result = pf.configure("/path/to/config.yaml")

            assert result is True

    def test_configuration_persistence(self, tmp_path):
        """Test configuration persists across library instances"""
        config_content = {
            "safety_checks": True,
            "default_output_dir": str(tmp_path),
            "log_level": "INFO",
        }

        config_file = tmp_path / "pyroform_config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_content, f)

        # Create multiple instances with same config
        pf1 = Pyroform(config_file=str(config_file))
        pf2 = Pyroform(config_file=str(config_file))

        # Both should use the same configuration
        assert pf1.config["safety_checks"] is True
        assert pf2.config["safety_checks"] is True

    def test_concurrent_library_usage(self):
        """Test library can be used concurrently (basic thread safety)"""
        import threading

        results = []

        def worker(worker_id, results_list):
            """Worker function for concurrent testing"""
            try:
                # Mock the PyroformEngine to avoid FlowCTRL dependency issues
                with patch("pyroform.pyroform.PyroformEngine") as MockEngine:
                    mock_engine = Mock()
                    mock_engine.configure.return_value = True
                    MockEngine.return_value = mock_engine

                    pf = Pyroform(auto_confirm=True)
                    result = pf.configure(f"/fake/config_{worker_id}.yaml")
                    results_list.append((worker_id, result))
            except Exception as e:
                results_list.append((worker_id, str(e)))

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i, results))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all workers completed successfully
        assert len(results) == 5
        for worker_id, result in results:
            assert result is True, f"Worker {worker_id} failed with: {result}"

    def test_library_with_different_file_formats(self, tmp_path):
        """Test library works with different input file formats"""
        # Mock the PyroformEngine to avoid FlowCTRL dependency issues
        with patch("pyroform.pyroform.PyroformEngine") as MockEngine:
            mock_engine = Mock()
            mock_engine.configure.return_value = True
            MockEngine.return_value = mock_engine

            pf = Pyroform(auto_confirm=True)

            # Test JSON format
            json_config = tmp_path / "test.json"
            with open(json_config, "w") as f:
                json.dump(
                    {"Label": "JSON Test", "Users": [], "Groups": [], "Devices": []}, f
                )

            result = pf.configure(str(json_config))
            assert result is True

            # Test YAML format
            yaml_config = tmp_path / "test.yaml"
            with open(yaml_config, "w") as f:
                f.write("Label: YAML Test\nUsers: []\nGroups: []\nDevices: []\n")

            result = pf.configure(str(yaml_config))
            assert result is True

    def test_library_method_chaining(self):
        """Test that library methods can be chained (if designed that way)"""
        # Mock the PyroformEngine to avoid FlowCTRL dependency issues
        with patch("pyroform.pyroform.PyroformEngine") as MockEngine:
            mock_engine = Mock()
            mock_engine.configure.return_value = True
            mock_engine.mount.return_value = True
            MockEngine.return_value = mock_engine

            pf = Pyroform(auto_confirm=True)

            # Example of potential method chaining
            result1 = pf.configure("/path/config.yaml")
            result2 = pf.mount("/path/config.yaml")

            # For now, just verify both methods were called
            assert pf.engine.configure.called
            assert pf.engine.mount.called


# CODE DUMP

