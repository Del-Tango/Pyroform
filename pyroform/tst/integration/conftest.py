import pytest
import tempfile
import json
from pathlib import Path


@pytest.fixture(scope="session")
def shared_temp_dir():
    """Shared temporary directory for integration tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def basic_pyro_config():
    """Basic Pyro configuration for multiple tests"""
    return {
        "Label": "Basic Test Config",
        "Users": [
            {
                "label": "test_user",
                "Name": "testuser",
                "Password": "testpass123",
                "Groups": ["testgroup"]
            }
        ],
        "Groups": [
            {
                "label": "test_group",
                "Name": "testgroup",
                "Users": ["testuser"]
            }
        ],
        "Devices": []
    }

