"""Shared pytest fixtures and configuration."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_config_dict() -> dict:
    """Sample configuration dictionary for testing."""
    return {
        "catalog": "dev",
        "schema": "supercharge_ai",
        "volume": "data",
        "llm_endpoint": "databricks-llama",
        "embedding_endpoint": "databricks-gte",
        "warehouse_id": "test-warehouse-id",
        "vector_search_endpoint": "test-vs-endpoint",
    }
