"""Structured logging setup using loguru."""

from __future__ import annotations

import sys
from typing import Literal

from loguru import logger as loguru_logger


def setup_logger(
    name: str,
    log_file: str | None = None,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
) -> object:
    """Set up a structured logger instance.

    Args:
        name: Logger name
        log_file: Optional path to log file
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    # Remove default handler
    loguru_logger.remove()

    # Add console handler
    console_fmt = (
        "<level>{level: <8}</level> | <cyan>{name}</cyan>:"
        "<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    loguru_logger.add(
        sys.stderr,
        level=level,
        format=console_fmt,
    )

    # Add file handler if specified
    if log_file:
        file_fmt = (
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} - {message}"
        )
        loguru_logger.add(
            log_file,
            level=level,
            format=file_fmt,
            rotation="10 MB",
            retention="7 days",
        )

    return loguru_logger
