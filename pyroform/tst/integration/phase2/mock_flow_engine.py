"""
Mock FlowEngine for testing
"""
from unittest.mock import Mock
from typing import Dict, Any


class MockFlowEngine:
    """Mock FlowEngine for testing purposes"""

    def __init__(self, config):
        self.config = config
        self.loaded_procedure = None
        self.procedure_started = False
        self.procedure_paused = False
        self.procedure_stopped = False

    def load_procedure(self, sketch_file: str) -> bool:
        """Mock load_procedure"""
        self.loaded_procedure = sketch_file
        return True

    def start_procedure(self) -> Mock:
        """Mock start_procedure"""
        self.procedure_started = True
        self.procedure_paused = False
        self.procedure_stopped = False
        return Mock(success=True, message="Procedure completed successfully")

    def pause_procedure(self) -> Mock:
        """Mock pause_procedure"""
        self.procedure_paused = True
        return Mock(success=True, message="Procedure paused")

    def resume_procedure(self) -> Mock:
        """Mock resume_procedure"""
        self.procedure_paused = False
        return Mock(success=True, message="Procedure resumed")

    def stop_procedure(self) -> Mock:
        """Mock stop_procedure"""
        self.procedure_stopped = True
        return Mock(success=True, message="Procedure stopped")

    def purge_data(self) -> Mock:
        """Mock purge_data"""
        return Mock(success=True, message="Data purged")

    def send_external_command(self, command: str) -> bool:
        """Mock send_external_command"""
        return True
