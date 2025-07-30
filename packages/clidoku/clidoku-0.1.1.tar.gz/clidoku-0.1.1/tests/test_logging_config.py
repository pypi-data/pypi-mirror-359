"""Tests for logging configuration."""

import io
import logging

from src.clidoku.logging_config import get_logger, setup_logging


class TestLoggingConfig:
    """Test suite for logging configuration module."""

    def test_setup_logging_default_config(self):
        """Test that setup_logging configures logging with default settings."""
        # Capture output
        output_stream = io.StringIO()

        # Setup logging with custom stream
        setup_logging(output_stream=output_stream)

        # Get a logger and test it
        logger = get_logger("test_module")
        logger.info("Test message")

        # Check output
        output = output_stream.getvalue()
        assert "Test message" in output
        assert output.strip() == "Test message"  # Should be just the message, no formatting

    def test_setup_logging_custom_level(self):
        """Test that setup_logging respects custom log level."""
        output_stream = io.StringIO()

        # Setup with DEBUG level
        setup_logging(level=logging.DEBUG, output_stream=output_stream)

        logger = get_logger("test_module")
        logger.debug("Debug message")
        logger.info("Info message")

        output = output_stream.getvalue()
        assert "Debug message" in output
        assert "Info message" in output

    def test_setup_logging_filters_by_level(self):
        """Test that setup_logging filters messages below the set level."""
        output_stream = io.StringIO()

        # Setup with INFO level (should filter out DEBUG)
        setup_logging(level=logging.INFO, output_stream=output_stream)

        logger = get_logger("test_module")
        logger.debug("Debug message")  # Should be filtered out
        logger.info("Info message")  # Should appear

        output = output_stream.getvalue()
        assert "Debug message" not in output
        assert "Info message" in output

    def test_get_logger_returns_logger_instance(self):
        """Test that get_logger returns a proper Logger instance."""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_setup_logging_removes_existing_handlers(self):
        """Test that setup_logging removes existing handlers to avoid duplicates."""
        output_stream1 = io.StringIO()
        output_stream2 = io.StringIO()

        # Setup logging twice with different streams
        setup_logging(output_stream=output_stream1)
        setup_logging(output_stream=output_stream2)

        logger = get_logger("test_module")
        logger.info("Test message")

        # Only the second stream should have output
        assert output_stream1.getvalue() == ""
        assert "Test message" in output_stream2.getvalue()

    def test_logging_formatter_clean_output(self):
        """Test that the logging formatter produces clean output without timestamps or levels."""
        output_stream = io.StringIO()
        setup_logging(output_stream=output_stream)

        logger = get_logger("test_module")
        logger.info("Simple message")
        logger.warning("Warning message")
        logger.error("Error message")

        output_lines = output_stream.getvalue().strip().split("\n")

        # Each line should be just the message content
        assert output_lines[0] == "Simple message"
        assert output_lines[1] == "Warning message"
        assert output_lines[2] == "Error message"

        # No timestamps, log levels, or module names should appear
        for line in output_lines:
            assert "INFO" not in line
            assert "WARNING" not in line
            assert "ERROR" not in line
            assert "test_module" not in line
            assert ":" not in line  # No timestamp colons
