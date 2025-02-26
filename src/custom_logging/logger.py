import logging
from pathlib import Path

class LoggerSingleton:
    _instance = None

    def __new__(cls, config=None):
        if cls._instance is None:
            cls._instance = super(LoggerSingleton, cls).__new__(cls)
            if config:
                cls._setup_logging(config)
        return cls._instance

    @staticmethod
    def _setup_logging(config):
        """Configure logging based on config settings."""
        log_path = Path(config['logging']['file_path'])
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=config['logging']['level'],
            format=config['logging']['format'],
            handlers=[
                logging.FileHandler(config['logging']['file_path']),
                logging.StreamHandler()
            ]
        )

    @staticmethod
    def get_logger(name):
        return logging.getLogger(name) 