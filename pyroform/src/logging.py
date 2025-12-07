"""
Logging configuration for Pyroform
"""

import logging
import sys

import pysnooper

from pathlib import Path
from datetime import datetime
from typing import Optional, Any


# @pysnooper.snoop()
def setup_logging(
    log_file: Path = None, debug: bool = False, config: dict | None = None
) -> None:
    """
    Configure comprehensive logging for Pyroform
    """
    log_file_path = log_file or Path("./pyroform.log")

    # Determine log level
    log_level = (
        logging.DEBUG
        if debug
        else getattr(logging, config.get("log_level"), logging.INFO)
    )

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler
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

    logger.debug("Logging configured successfully")


class STDOUTMsg:
    """
    A class for standardized STDOUT messaging with color-coded prefixes.
    """

    # ANSI color codes
    COLORS = {
        "green": "\033[92m",
        "red": "\033[91m",
        "orange": "\033[93m",
        "yellow": "\033[93m",
        "reset": "\033[0m",
        "bold": "\033[1m",
    }

    def __init__(self, debug_mode: bool = False, timestamp: bool = False):
        """
        Initialize STDOUTMsg instance.

        Args:
            debug_mode: If True, debug messages will be printed
            timestamp: If True, messages will include timestamps
        """
        self.log = logging.getLogger(__name__)
        self.debug_mode = debug_mode
        self.timestamp = timestamp

    def _get_timestamp(self) -> str:
        """Get current timestamp if enabled."""
        if self.timestamp:
            return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
        return ""

    def _format_message(
        self, tag: str, message: str, color: Optional[str] = None
    ) -> str:
        """Format message with tag prefix and optional color."""
        timestamp = self._get_timestamp()
        if color and color in self.COLORS:
            return f"{timestamp}[ {self.COLORS[color]}{tag}{self.COLORS['reset']} ]: {message}"
        else:
            return f"{timestamp}[ {tag} ]: {message}"

    def _print(self, formatted_message: str, **kwargs) -> None:
        """Internal print method with flush."""
        print(formatted_message, **kwargs)
        sys.stdout.flush()

    def ok(self, message: str, **kwargs) -> None:
        """
        Print success message with green [ OK ] prefix.

        Args:
            message: The message to print
            **kwargs: Additional arguments to pass to print()
        """
        self.log.info(message)
        formatted = self._format_message("OK", message, "green")
        self._print(formatted, **kwargs)

    def nok(self, message: str, **kwargs) -> None:
        """
        Print not-ok message with red [ NOK ] prefix.

        Args:
            message: The message to print
            **kwargs: Additional arguments to pass to print()
        """
        self.log.info(message)
        formatted = self._format_message("NOK", message, "red")
        self._print(formatted, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """
        Print info message with [ INFO ] prefix (no color).

        Args:
            message: The message to print
            **kwargs: Additional arguments to pass to print()
        """
        self.log.info(message)
        formatted = self._format_message("INFO", message)
        self._print(formatted, **kwargs)

    def warn(self, message: str, **kwargs) -> None:
        """
        Print warning message with orange [ WARNING ] prefix.

        Args:
            message: The message to print
            **kwargs: Additional arguments to pass to print()
        """
        self.log.warning(message)
        formatted = self._format_message("WARNING", message, "orange")
        self._print(formatted, **kwargs)

    def err(self, message: str, **kwargs) -> None:
        """
        Print error message with red [ ERROR ] prefix.

        Args:
            message: The message to print
            **kwargs: Additional arguments to pass to print()
        """
        self.log.error(message)
        formatted = self._format_message("ERROR", message, "red")
        self._print(formatted, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """
        Print debug message with [ DEBUG ] prefix (no color) if debug_mode is True.

        Args:
            message: The message to print
            **kwargs: Additional arguments to pass to print()
        """
        self.log.debug(message)
        if self.debug_mode:
            formatted = self._format_message("DEBUG", message)
            self._print(formatted, **kwargs)

    def custom(
        self, tag: str, message: str, color: Optional[str] = None, **kwargs
    ) -> None:
        """
        Print custom message with [ <tag> ] prefix and optional color.

        Args:
            tag: Custom tag to display in brackets
            message: The message to print
            color: Optional color name ('green', 'red', 'orange', 'yellow')
            **kwargs: Additional arguments to pass to print()
        """
        self.log.info(message)
        formatted = self._format_message(tag.upper(), message, color)
        self._print(formatted, **kwargs)

    def set_debug_mode(self, debug_mode: bool) -> None:
        """Enable or disable debug message printing."""
        self.debug_mode = debug_mode

    def set_timestamp(self, timestamp: bool) -> None:
        """Enable or disable timestamp in messages."""
        self.timestamp = timestamp


# CODE DUMP
