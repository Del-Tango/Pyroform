# pyroform/src/scorch_engine.py
class ScorchEngine:
    def __init__(self, safety_check: bool = True):
        self.safety_check = safety_check

    def execute_scorch(self, config: PyroConfig) -> ScorchResult:
        """Remove resources not specified in configuration"""
        pass

    def _calculate_cleanup_set(self) -> Set[str]:
        """Calculate resources to be removed"""
        pass
