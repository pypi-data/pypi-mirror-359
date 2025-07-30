"""Logging configuration for clidoku."""

import logging
import sys
from typing import TextIO


def setup_logging(level: int = logging.INFO, output_stream: TextIO = sys.stdout) -> None:
    """
    Configure logging for clidoku with clean output formatting.

    Args:
        level: Logging level (default: INFO)
        output_stream: Output stream for log messages (default: stdout)
    """
    # Create a custom formatter that outputs just the message (no timestamp, level, etc.)
    formatter = logging.Formatter("%(message)s")

    # Create handler for the specified output stream
    handler = logging.StreamHandler(output_stream)
    handler.setFormatter(formatter)

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove any existing handlers to avoid duplicates
    for existing_handler in root_logger.handlers[:]:
        root_logger.removeHandler(existing_handler)

    # Add our handler
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified module."""
    return logging.getLogger(name)
