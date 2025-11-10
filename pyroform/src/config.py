
class PyroformConfig:
    def __init__(self, config_file: Path = None):
        self.settings = self._load_config(config_file)

    # TODO
    def _load_config(self, config_file: Path) -> Dict[str, Any]:
        """Load configuration from file with defaults"""
        pass
