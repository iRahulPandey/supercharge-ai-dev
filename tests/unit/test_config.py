"""Tests for configuration management."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from supercharge_ai.config import (
    DatasetConfig,
    ProjectConfig,
    TableRef,
    load_dataset,
)

# --- ProjectConfig ---------------------------------------------------------


def test_project_config_from_dict():
    """Creating ProjectConfig from dict with just catalog works."""
    config = ProjectConfig(catalog="dev", volume="data")
    assert config.catalog == "dev"
    assert config.volume == "data"


def test_project_config_missing_catalog_raises():
    """ProjectConfig requires catalog."""
    with pytest.raises(ValidationError):
        ProjectConfig(volume="data")


def test_load_config_from_yaml():
    """Per-env config loads via ProjectConfig.from_yaml."""
    yaml_content = """
dev:
  catalog: dev
  volume: data

stg:
  catalog: stg
  volume: data
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yml"
        config_path.write_text(yaml_content)

        dev = ProjectConfig.from_yaml(str(config_path), env="dev")
        assert dev.catalog == "dev"

        stg = ProjectConfig.from_yaml(str(config_path), env="stg")
        assert stg.catalog == "stg"


def test_load_config_invalid_environment():
    """Invalid env name raises ValueError."""
    yaml_content = "dev:\n  catalog: dev\n"
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yml"
        config_path.write_text(yaml_content)

        with pytest.raises(ValueError, match="Invalid environment"):
            ProjectConfig.from_yaml(str(config_path), env="invalid")


# --- TableRef --------------------------------------------------------------


def test_tableref_fqn_with_explicit_catalog():
    """TableRef with catalog set produces a fully qualified name."""
    ref = TableRef(catalog="samples", schema="bakehouse", table="media_customer_reviews")
    assert ref.fqn() == "samples.bakehouse.media_customer_reviews"


def test_tableref_fqn_falls_back_to_default_catalog():
    """When catalog is omitted, fqn() uses the default_catalog argument."""
    ref = TableRef(schema="bakehouse", table="media_customer_reviews")
    assert ref.fqn(default_catalog="dev") == "dev.bakehouse.media_customer_reviews"
    assert ref.fqn(default_catalog="prd") == "prd.bakehouse.media_customer_reviews"


def test_tableref_fqn_without_any_catalog_raises():
    """No catalog set AND no default_catalog → error."""
    ref = TableRef(schema="bakehouse", table="media_customer_reviews")
    with pytest.raises(ValueError, match="No catalog available"):
        ref.fqn()


# --- DatasetConfig + load_dataset -----------------------------------------


def test_dataset_config_from_dict():
    """DatasetConfig builds from input/output dicts."""
    ds = DatasetConfig(
        input={
            "catalog": "samples",
            "schema": "bakehouse",
            "table": "media_customer_reviews",
        },
        output={"schema": "bakehouse", "table": "media_customer_reviews"},
    )
    assert ds.input.fqn() == "samples.bakehouse.media_customer_reviews"
    assert ds.output.fqn("dev") == "dev.bakehouse.media_customer_reviews"


def test_load_dataset_from_yaml():
    """load_dataset reads the datasets section of the config file."""
    yaml_content = """
dev:
  catalog: dev
  volume: data

datasets:
  media_customer_reviews:
    input:
      catalog: samples
      schema: bakehouse
      table: media_customer_reviews
    output:
      schema: bakehouse
      table: media_customer_reviews
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yml"
        config_path.write_text(yaml_content)

        ds = load_dataset("media_customer_reviews", str(config_path))
        assert ds.input.fqn() == "samples.bakehouse.media_customer_reviews"
        assert ds.output.catalog is None
        assert ds.output.fqn("dev") == "dev.bakehouse.media_customer_reviews"
        assert ds.output.fqn("prd") == "prd.bakehouse.media_customer_reviews"


def test_load_dataset_missing_key_raises():
    """load_dataset raises a clear error when the dataset key is absent."""
    yaml_content = """
datasets:
  media_customer_reviews:
    input:
      catalog: samples
      schema: bakehouse
      table: media_customer_reviews
    output:
      schema: bakehouse
      table: media_customer_reviews
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yml"
        config_path.write_text(yaml_content)

        with pytest.raises(ValueError, match="Dataset 'nonexistent' not found"):
            load_dataset("nonexistent", str(config_path))
