"""
Logging Test Suite

Unit tests for setup_logging function and STDOUTMsg classes.
"""

import pytest
import logging
import sys
import io
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, call
from typing import Optional

from pyroform.src.logging import setup_logging, STDOUTMsg


@pytest.fixture
def clean_logging():
    """Fixture to clean up logging configuration before and after tests."""
    # Store original state
    original_root = logging.getLogger()
    original_handlers = original_root.handlers.copy()
    original_level = original_root.level

    # Clear handlers for test
    for handler in original_root.handlers[:]:
        original_root.removeHandler(handler)

    yield

    # Restore original state
    for handler in original_root.handlers[:]:
        original_root.removeHandler(handler)

    for handler in original_handlers:
        original_root.addHandler(handler)

    original_root.setLevel(original_level)


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent timestamp testing."""
    with patch('pyroform.src.logging.datetime') as mock_dt:
        fixed_time = datetime(2023, 1, 1, 12, 0, 0)
        mock_dt.now.return_value = fixed_time
        mock_dt.strftime = lambda x, fmt: fixed_time.strftime(fmt)
        yield mock_dt


@pytest.fixture
def capture_output():
    """Fixture to capture stdout output."""
    captured = io.StringIO()

    with patch('sys.stdout', captured):
        yield captured


class TestSetupLogging:
    """Test the setup_logging function."""

#   # TODO
#   def test_setup_logging_removes_existing_handlers(self, clean_logging):
#       """Test that setup_logging removes existing handlers."""

    def test_setup_logging_defaults(self, clean_logging):
        """Test setup_logging with default parameters."""
        # Setup logging
        setup_logging()

        # Get root logger
        logger = logging.getLogger()

        # Verify log level
        assert logger.level == logging.INFO

        # Verify handlers
        assert len(logger.handlers) == 1  # Only console handler

        # Verify console handler
        console_handler = logger.handlers[0]
        assert isinstance(console_handler, logging.StreamHandler)
        assert console_handler.stream == sys.stdout
        assert console_handler.level == logging.INFO

        # Verify formatter
        formatter = console_handler.formatter
        assert formatter is not None
        assert '%(asctime)s' in formatter._fmt
        assert '%(name)s' in formatter._fmt
        assert '%(levelname)s' in formatter._fmt
        assert '%(message)s' in formatter._fmt

    def test_setup_logging_debug_mode(self, clean_logging):
        """Test setup_logging with debug=True."""
        setup_logging(debug=True)

        logger = logging.getLogger()

        # Should be DEBUG level
        assert logger.level == logging.DEBUG

        # Console handler should also be DEBUG
        console_handler = logger.handlers[0]
        assert console_handler.level == logging.DEBUG

    def test_setup_logging_with_log_file(self, clean_logging, tmp_path):
        """Test setup_logging with log file."""
        log_file = tmp_path / "test.log"

        setup_logging(log_file=log_file)

        logger = logging.getLogger()

        # Should have 2 handlers (console + file)
        assert len(logger.handlers) == 2

        # Find file handler
        file_handlers = [
            h for h in logger.handlers
            if isinstance(h, logging.FileHandler)
        ]
        assert len(file_handlers) == 1

        file_handler = file_handlers[0]
        assert file_handler.baseFilename == str(log_file)
        assert file_handler.level == logging.INFO

        # Log file should exist
        assert log_file.exists()

    def test_setup_logging_log_file_directory_creation(self, clean_logging, tmp_path):
        """Test that log file directory is created if it doesn't exist."""
        log_file = tmp_path / "deeply" / "nested" / "directory" / "test.log"

        # Directory doesn't exist yet
        assert not log_file.parent.exists()

        setup_logging(log_file=log_file)

        # Directory should be created
        assert log_file.parent.exists()

        # File should exist
        assert log_file.exists()

    def test_setup_logging_log_file_permission_error(self, clean_logging, tmp_path):
        """Test handling of log file permission error."""
        # Create a directory that we can't write to (simulate permission error)
        read_only_dir = tmp_path / "readonly"
        read_only_dir.mkdir()

        # On Unix-like systems, we can make it read-only
        import os
        os.chmod(read_only_dir, 0o444)

        log_file = read_only_dir / "test.log"

        # This should not raise exception
        setup_logging(log_file=log_file)

        # Should still have console handler
        logger = logging.getLogger()
        assert len(logger.handlers) >= 1  # At least console handler

        # Clean up
        os.chmod(read_only_dir, 0o755)

    def test_setup_logging_noisy_libraries_silenced(self, clean_logging):
        """Test that noisy libraries have their log level set to WARNING."""
        setup_logging()

        # Check urllib3 logger
        urllib3_logger = logging.getLogger('urllib3')
        assert urllib3_logger.level == logging.WARNING

        # Check requests logger
        requests_logger = logging.getLogger('requests')
        assert requests_logger.level == logging.WARNING

        # Other loggers should not be affected
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_setup_logging_debug_log_message(self, clean_logging, capture_output):
        """Test that debug message is logged after configuration."""
        # Capture logging output
        captured = io.StringIO()

        # Temporarily redirect logging
        with patch('sys.stdout', captured):
            setup_logging(debug=True)

        # Check that debug message was logged
        output = captured.getvalue()
        assert "Logging configured successfully" in output

    def test_setup_logging_multiple_calls(self, clean_logging):
        """Test that calling setup_logging multiple times works correctly."""
        # First call
        setup_logging()
        logger = logging.getLogger()
        handlers_count_1 = len(logger.handlers)

        # Second call with different parameters
        setup_logging(debug=True)
        handlers_count_2 = len(logger.handlers)

        # Should still have correct number of handlers (not duplicated)
        assert handlers_count_2 == handlers_count_1

        # Log level should be DEBUG now
        assert logger.level == logging.DEBUG

    def test_setup_logging_file_handler_log_message(self, clean_logging, tmp_path, capture_output):
        """Test that file handler creation is logged."""
        log_file = tmp_path / "test.log"
        captured = io.StringIO()

        with patch('sys.stdout', captured):
            setup_logging(log_file=log_file)

        output = captured.getvalue()
        assert f"Logging to file: {log_file}" in output

    def test_setup_logging_formatter_date_format(self, clean_logging):
        """Test that formatter has correct date format."""
        setup_logging()

        logger = logging.getLogger()
        console_handler = logger.handlers[0]
        formatter = console_handler.formatter

        # Check date format
        assert formatter.datefmt == '%Y-%m-%d %H:%M:%S'

        # Test format with a mock record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )

        formatted = formatter.format(record)
        # Should contain timestamp in expected format
        assert '2023' not in formatted  # Actual year depends on when test runs

    def test_setup_logging_none_log_file(self, clean_logging):
        """Test setup_logging with log_file=None."""
        setup_logging(log_file=None)

        logger = logging.getLogger()

        # Should only have console handler
        file_handlers = [
            h for h in logger.handlers
            if isinstance(h, logging.FileHandler)
        ]
        assert len(file_handlers) == 0
        assert len(logger.handlers) == 1


class TestSTDOUTMsgInitialization:
    """Test STDOUTMsg class initialization."""

    def test_init_defaults(self):
        """Test initialization with default parameters."""
        stdout = STDOUTMsg()

        assert stdout.debug_mode == False
        assert stdout.timestamp == False

    def test_init_debug_mode_true(self):
        """Test initialization with debug_mode=True."""
        stdout = STDOUTMsg(debug_mode=True)

        assert stdout.debug_mode == True
        assert stdout.timestamp == False

    def test_init_timestamp_true(self):
        """Test initialization with timestamp=True."""
        stdout = STDOUTMsg(timestamp=True)

        assert stdout.debug_mode == False
        assert stdout.timestamp == True

    def test_init_both_true(self):
        """Test initialization with both debug_mode and timestamp True."""
        stdout = STDOUTMsg(debug_mode=True, timestamp=True)

        assert stdout.debug_mode == True
        assert stdout.timestamp == True

    def test_colors_attribute(self):
        """Test that COLORS dictionary is accessible."""
        stdout = STDOUTMsg()

        assert isinstance(stdout.COLORS, dict)
        assert 'green' in stdout.COLORS
        assert 'red' in stdout.COLORS
        assert 'orange' in stdout.COLORS
        assert 'yellow' in stdout.COLORS
        assert 'reset' in stdout.COLORS
        assert 'bold' in stdout.COLORS

        # Check ANSI codes
        assert stdout.COLORS['green'] == '\033[92m'
        assert stdout.COLORS['red'] == '\033[91m'
        assert stdout.COLORS['reset'] == '\033[0m'


class TestSTDOUTMsgPrivateMethods:
    """Test STDOUTMsg private methods."""

#   # TODO
#   def test_print_method(self, capture_output):
#       """Test _print method flushes stdout."""

    def test_get_timestamp_disabled(self):
        """Test _get_timestamp when timestamp is False."""
        stdout = STDOUTMsg(timestamp=False)

        result = stdout._get_timestamp()

        assert result == ""

    @patch('pyroform.src.logging.datetime')
    def test_get_timestamp_enabled(self, mock_datetime):
        """Test _get_timestamp when timestamp is True."""
        fixed_time = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_time

        stdout = STDOUTMsg(timestamp=True)

        result = stdout._get_timestamp()

        assert result == "[2023-01-01 12:00:00] "
        mock_datetime.now.assert_called_once()

    def test_format_message_no_color(self):
        """Test _format_message without color."""
        stdout = STDOUTMsg(timestamp=False)

        result = stdout._format_message("TEST", "message")

        assert result == "[ TEST ]: message"

    def test_format_message_with_color(self):
        """Test _format_message with color."""
        stdout = STDOUTMsg(timestamp=False)

        result = stdout._format_message("TEST", "message", "green")

        # Should contain ANSI color codes
        assert '\033[92m' in result  # green
        assert '\033[0m' in result   # reset
        assert "TEST" in result
        assert "message" in result

    def test_format_message_with_timestamp(self, mock_datetime):
        """Test _format_message with timestamp enabled."""
        stdout = STDOUTMsg(timestamp=True)

        result = stdout._format_message("TEST", "message")

        assert "[2023-01-01 12:00:00]" in result
        assert "[ TEST ]: message" in result

    def test_format_message_invalid_color(self):
        """Test _format_message with invalid color."""
        stdout = STDOUTMsg(timestamp=False)

        result = stdout._format_message("TEST", "message", "invalid_color")

        # Should fall back to no color
        assert '\033[' not in result
        assert "[ TEST ]: message" in result

    def test_format_message_empty_tag(self):
        """Test _format_message with empty tag."""
        stdout = STDOUTMsg(timestamp=False)

        result = stdout._format_message("", "message")

        assert "[  ]: message" in result

    def test_format_message_empty_message(self):
        """Test _format_message with empty message."""
        stdout = STDOUTMsg(timestamp=False)

        result = stdout._format_message("TEST", "")

        assert "[ TEST ]: " in result


class TestSTDOUTMsgPublicMethods:
    """Test STDOUTMsg public methods."""

#   # TODO
#   def test_ok_method(self, capture_output):
#       """Test ok method."""
#   def test_nok_method(self, capture_output):
#       """Test nok method."""
#   def test_info_method(self, capture_output):
#       """Test info method."""
#   def test_warn_method(self, capture_output):
#       """Test warn method."""
#   def test_err_method(self, capture_output):
#       """Test err method."""
#   def test_debug_method_debug_enabled(self, capture_output):
#       """Test debug method when debug_mode is True."""
#   def test_custom_method(self, capture_output):
#       """Test custom method."""
#   def test_custom_method_no_color(self, capture_output):
#       """Test custom method without color."""
#   def test_custom_method_lowercase_tag(self, capture_output):
#       """Test custom method with lowercase tag (should be uppercased)."""
#   def test_methods_with_kwargs(self, capture_output):
#       """Test that methods accept and pass through kwargs to print()."""
#   def test_methods_with_timestamp(self, mock_datetime, capture_output):
#       """Test methods with timestamp enabled."""

    def test_debug_method_debug_disabled(self, capture_output):
        """Test debug method when debug_mode is False."""
        stdout = STDOUTMsg(debug_mode=False)

        stdout.debug("Debug message")

        captured = capture_output
        captured.seek(0)
        output = captured.read()

        # Should not print anything
        assert output == ""


class TestSTDOUTMsgSetterMethods:
    """Test STDOUTMsg setter methods."""

#   # TODO
#   def test_set_debug_mode_affects_debug_method(self, capture_output):
#       """Test that set_debug_mode affects debug method behavior."""
#   def test_set_timestamp_affects_all_methods(self, mock_datetime, capture_output):
#       """Test that set_timestamp affects all output methods."""

    def test_set_debug_mode(self):
        """Test set_debug_mode method."""
        stdout = STDOUTMsg(debug_mode=False)

        assert stdout.debug_mode == False

        stdout.set_debug_mode(True)
        assert stdout.debug_mode == True

        stdout.set_debug_mode(False)
        assert stdout.debug_mode == False

    def test_set_timestamp(self):
        """Test set_timestamp method."""
        stdout = STDOUTMsg(timestamp=False)

        assert stdout.timestamp == False

        stdout.set_timestamp(True)
        assert stdout.timestamp == True

        stdout.set_timestamp(False)
        assert stdout.timestamp == False


class TestIntegration:
    """Integration tests for logging module."""

#   # TODO
#   def test_logging_and_stdoutmsg_together(self, clean_logging, capture_output):
#       """Test that logging and STDOUTMsg can work together."""
#   def test_stdoutmsg_with_real_print_kwargs(self):
#       """Test STDOUTMsg with various print kwargs."""
#   def test_stdoutmsg_special_characters(self, capture_output):
#       """Test STDOUTMsg with special characters in messages."""
#   def test_stdoutmsg_long_messages(self, capture_output):
#       """Test STDOUTMsg with very long messages."""

    def test_stdoutmsg_color_disabled_environment(self):
        """Test STDOUTMsg when colors might be disabled (e.g., non-TTY)."""
        stdout = STDOUTMsg(timestamp=False)

        # Colors should still be in the format string
        # even if they won't display on non-TTY
        result = stdout._format_message("OK", "message", "green")
        assert '\033[92m' in result

    def test_stdoutmsg_multiple_instances(self):
        """Test that multiple STDOUTMsg instances don't interfere."""
        stdout1 = STDOUTMsg(debug_mode=False, timestamp=False)
        stdout2 = STDOUTMsg(debug_mode=True, timestamp=True)

        assert stdout1.debug_mode == False
        assert stdout2.debug_mode == True
        assert stdout1.timestamp == False
        assert stdout2.timestamp == True

        # Changing one shouldn't affect the other
        stdout1.set_debug_mode(True)
        assert stdout1.debug_mode == True
        assert stdout2.debug_mode == True  # Still True

        stdout1.set_timestamp(True)
        assert stdout1.timestamp == True
        assert stdout2.timestamp == True  # Still True


class TestErrorHandling:
    """Test error handling in logging module."""

#   # TODO
#   def test_stdoutmsg_none_message(self, capture_output):
#       """Test STDOUTMsg with None message."""
#   def test_stdoutmsg_non_string_message(self, capture_output):
#       """Test STDOUTMsg with non-string message."""

    def test_setup_logging_file_handler_error_recovery(self, clean_logging, tmp_path):
        """Test that file handler error doesn't prevent console logging."""
        # Create a path that will cause permission error
        # (trying to create file in non-existent parent directory we can't create)
        import os

        if os.name == 'posix':  # Unix-like systems
            # Try to write to root directory (usually requires root)
            log_file = Path("/proc/test.log")  # Usually not writable
        else:
            # On Windows, use a system directory
            log_file = Path("C:\\Windows\\test.log")

        # This should not raise exception
        setup_logging(log_file=log_file)

        # Should still have console handler
        logger = logging.getLogger()
        console_handlers = [
            h for h in logger.handlers
            if isinstance(h, logging.StreamHandler) and h.stream == sys.stdout
        ]
        assert len(console_handlers) == 1

        # Warning should be logged about file creation failure
        # (We can't easily test this without mocking the logger)

    def test_stdoutmsg_invalid_color_handling(self):
        """Test that invalid colors are handled gracefully."""
        stdout = STDOUTMsg(timestamp=False)

        # This should not raise exception
        result = stdout._format_message("TEST", "message", "invalid_color_name")

        # Should fall back to no color
        assert '\033[' not in result
        assert "[ TEST ]: message" in result

    def test_setup_logging_nonexistent_directory_chain(self, clean_logging, tmp_path):
        """Test creating log file in deeply nested nonexistent directory."""
        # Create a path with multiple nonexistent directories
        log_file = tmp_path / "level1" / "level2" / "level3" / "test.log"

        # Parent directories don't exist
        assert not log_file.parent.exists()

        setup_logging(log_file=log_file)

        # Directories should be created
        assert log_file.parent.exists()
        assert log_file.exists()


class TestPerformance:
    """Performance-related tests."""

#   # TODO
#   def test_stdoutmsg_rapid_calls(self, capture_output):
#       """Test making many rapid calls to STDOUTMsg methods."""

    def test_setup_logging_multiple_threads(self, clean_logging):
        """Test setup_logging called from multiple threads."""
        import threading

        errors = []

        def setup_logging_thread():
            try:
                setup_logging()
            except Exception as e:
                errors.append(e)

        # Create and start multiple threads
        threads = []
        for _ in range(10):
            t = threading.Thread(target=setup_logging_thread)
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Should not have any errors
        assert len(errors) == 0

        # Logger should be properly configured
        logger = logging.getLogger()
        assert len(logger.handlers) == 1  # Console handler

    def test_stdoutmsg_thread_safety(self):
        """Test that STDOUTMsg instances can be used from multiple threads."""
        import threading

        stdout = STDOUTMsg(timestamp=False)
        output_lines = []
        lock = threading.Lock()

        def print_message(thread_id):
            with lock:
                stdout.info(f"Thread {thread_id}")
                # Capture would be complex, so just ensure no exceptions

        # Create and start threads
        threads = []
        for i in range(20):
            t = threading.Thread(target=print_message, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # No assertions - just ensuring no exceptions are raised


class TestRealWorldScenarios:
    """Real-world usage scenario tests."""

#   # TODO
#   def test_typical_usage_pattern(self, clean_logging, capture_output):
#       """Test typical usage pattern of both logging and STDOUTMsg."""
#   def test_log_rotation_scenario(self, clean_logging, tmp_path):
#       """Test logging to a file that might be rotated."""

    def test_configuration_changes_during_runtime(self):
        """Test changing STDOUTMsg configuration during runtime."""
        stdout = STDOUTMsg(debug_mode=False, timestamp=False)

        # Start with defaults
        output1 = io.StringIO()
        stdout.debug("debug 1", file=output1)
        assert output1.getvalue() == ""  # Not printed

        # Enable debug
        stdout.set_debug_mode(True)
        output2 = io.StringIO()
        stdout.debug("debug 2", file=output2)
        assert "[ DEBUG ]: debug 2" in output2.getvalue()

        # Enable timestamp
        stdout.set_timestamp(True)
        output3 = io.StringIO()
        stdout.debug("debug 3", file=output3)
        assert "]: debug 3" in output3.getvalue()


if __name__ == "__main__":
    # This allows running the test file directly
    pytest.main([__file__, "-v", "--tb=short"])
