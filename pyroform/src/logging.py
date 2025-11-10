"""
Logging configuration for Pyroform
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(log_file: Path = None, debug: bool = False) -> None:
    """
    Configure comprehensive logging for Pyroform

    Args:
        log_file: Optional path to log file
        debug: Whether to enable debug logging
    """
    # Determine log level
    log_level = logging.DEBUG if debug else logging.INFO

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log file specified)
    if log_file:
        try:
            # Ensure log directory exists
            log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            logger.info(f"Logging to file: {log_file}")
        except (IOError, PermissionError) as e:
            logger.warning(f"Could not create log file {log_file}: {e}")

    # Set specific log levels for noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

    logger.debug("Logging configured successfully")

# CODE DUMP

