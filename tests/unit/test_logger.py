"""Tests for logging setup."""

from __future__ import annotations

import tempfile
from pathlib import Path

from supercharge_ai.logger import setup_logger


def test_setup_logger_returns_logger():
    """Test that setup_logger returns a logger instance."""
    logger = setup_logger(name="test")
    assert logger is not None


def test_setup_logger_with_file():
    """Test that setup_logger can write to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"
        logger = setup_logger(name="test", log_file=str(log_file))

        logger.info("test message")

        assert log_file.exists()
        assert "test message" in log_file.read_text()


def test_setup_logger_different_levels():
    """Test logger with different log levels."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"
        logger = setup_logger(name="test", log_file=str(log_file), level="DEBUG")

        logger.debug("debug message")
        logger.info("info message")

        content = log_file.read_text()
        assert "debug message" in content
        assert "info message" in content
