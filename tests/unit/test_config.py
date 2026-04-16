"""Tests for configuration management."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from supercharge_ai.config import ProjectConfig, load_config


def test_project_config_from_dict():
    """Test creating ProjectConfig from dictionary."""
    config_data = {
        "catalog": "dev",
        "schema": "supercharge_ai",
        "volume": "data",
        "llm_endpoint": "databricks-llama",
        "embedding_endpoint": "databricks-gte",
        "warehouse_id": "test-warehouse-id",
        "vector_search_endpoint": "test-vs-endpoint",
    }
    config = ProjectConfig(**config_data)

    assert config.catalog == "dev"
    assert config.schema == "supercharge_ai"
    assert config.full_schema_name == "dev.supercharge_ai"
    assert config.full_volume_path == "/Volumes/dev/supercharge_ai/data"


def test_project_config_missing_required_field():
    """Test that ProjectConfig raises error for missing required field."""
    config_data = {
        "catalog": "dev",
        # Missing 'schema'
        "volume": "data",
    }
    with pytest.raises(ValidationError):
        ProjectConfig(**config_data)


def test_load_config_from_yaml():
    """Test loading config from YAML file."""
    yaml_content = """
dev:
  catalog: dev
  schema: supercharge_ai
  volume: data
  llm_endpoint: databricks-llama
  embedding_endpoint: databricks-gte
  warehouse_id: test-warehouse
  vector_search_endpoint: test-vs

acc:
  catalog: acc
  schema: supercharge_ai
  volume: data
  llm_endpoint: databricks-llama
  embedding_endpoint: databricks-gte
  warehouse_id: test-warehouse
  vector_search_endpoint: test-vs
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yml"
        config_path.write_text(yaml_content)

        config = ProjectConfig.from_yaml(str(config_path), env="dev")
        assert config.catalog == "dev"
        assert config.schema == "supercharge_ai"


def test_load_config_invalid_environment():
    """Test that invalid environment raises error."""
    yaml_content = """
dev:
  catalog: dev
  schema: supercharge_ai
  volume: data
  llm_endpoint: databricks-llama
  embedding_endpoint: databricks-gte
  warehouse_id: test-warehouse
  vector_search_endpoint: test-vs
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yml"
        config_path.write_text(yaml_content)

        with pytest.raises(ValueError, match="Invalid environment"):
            ProjectConfig.from_yaml(str(config_path), env="invalid")
