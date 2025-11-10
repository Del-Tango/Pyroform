import unittest
from unittest.mock import Mock, patch

# Import the modules to test
from pyroform.src.models import ActionType
from pyroform.src.flow_engine import PyroflowEngine


class TestPyroflowEngine(unittest.TestCase):
    """Test FlowCTRL engine integration"""

    def setUp(self):
        self.flow_engine = PyroflowEngine()

    def test_initialization(self):
        """Test engine initialization"""
        self.assertIsNotNone(self.flow_engine.flow_engine)
        self.assertIsNotNone(self.flow_engine.config)

    @patch("pyroform.src.flow_engine.PyroflowEngine._create_mock_flow_engine")
    def test_execute_sketch(self, mock_mock_engine):
        """Test sketch execution"""
        mock_engine = Mock()
        mock_engine.load_procedure.return_value = True
        mock_engine.start_procedure.return_value = Mock(success=True)
        mock_mock_engine.return_value = mock_engine

        self.flow_engine.flow_engine = mock_engine

        sketch = {"name": "test_sketch", "commands": []}
        success = self.flow_engine.execute_sketch(sketch, ActionType.CONFIGURE)

        self.assertTrue(success)
        mock_engine.load_procedure.assert_called_once()
        mock_engine.start_procedure.assert_called_once()

    def test_control_methods(self):
        """Test engine control methods (pause, resume, stop)"""
        # These should work with the mock engine
        self.assertTrue(self.flow_engine.pause_execution())
        self.assertTrue(self.flow_engine.resume_execution())
        self.assertTrue(self.flow_engine.stop_execution())
        self.assertTrue(self.flow_engine.send_command("test"))
        self.assertTrue(self.flow_engine.purge_data())
