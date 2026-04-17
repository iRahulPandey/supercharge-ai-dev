"""Supercharge AI Dev — AI-Dev-Kit + Databricks Asset Bundles Integration."""

from __future__ import annotations

from supercharge_ai.config import (
    DatasetConfig,
    ProjectConfig,
    TableRef,
    load_config,
    load_dataset,
)
from supercharge_ai.logger import setup_logger

__version__ = "0.0.1"
__author__ = "Rahul Pandey"
__email__ = "rpandey1901@gmail.com"

__all__ = [
    "__version__",
    "DatasetConfig",
    "ProjectConfig",
    "TableRef",
    "load_config",
    "load_dataset",
    "setup_logger",
]
