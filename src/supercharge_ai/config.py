"""Configuration management for Supercharge AI."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import yaml
from pydantic import BaseModel, ConfigDict, Field


class ProjectConfig(BaseModel):
    """Per-environment project settings (catalog + shared infra endpoints)."""

    catalog: str = Field(..., description="Unity Catalog name")
    volume: str = Field(default="", description="Default volume name")
    llm_endpoint: str = Field(default="", description="LLM endpoint name")
    embedding_endpoint: str = Field(default="", description="Embedding endpoint name")
    warehouse_id: str = Field(default="", description="Warehouse ID")
    vector_search_endpoint: str = Field(
        default="", description="Vector search endpoint name"
    )
    genie_space_id: str | None = Field(default=None, description="Genie Space ID")

    model_config = ConfigDict(populate_by_name=True)  # type: ignore[assignment]

    VALID_ENVS: ClassVar[tuple[str, ...]] = ("local", "dev", "stg", "prod")

    @classmethod
    def from_yaml(cls, config_path: str, env: str = "dev") -> ProjectConfig:
        """Load per-environment config from a YAML file.

        Args:
            config_path: Path to the YAML configuration file
            env: Environment name — one of local, dev, stg, prod (DAB target names)

        Returns:
            ProjectConfig instance

        Raises:
            ValueError: If env is invalid or absent from the config
        """
        if env not in cls.VALID_ENVS:
            raise ValueError(
                f"Invalid environment: {env}. Expected one of {cls.VALID_ENVS}"
            )

        with open(config_path, encoding="utf-8") as f:
            config_data: dict[str, Any] = yaml.safe_load(f)

        if env not in config_data:
            raise ValueError(f"Environment '{env}' not found in config file")

        return cls(**config_data[env])


class TableRef(BaseModel):
    """A three-part Unity Catalog table reference: catalog.schema.table.

    For `input`, all three parts are required. For `output`, `catalog` is
    optional — when omitted it's inherited from the current env's catalog.
    """

    catalog: str | None = Field(default=None, description="Unity Catalog name")
    schema_name: str = Field(..., alias="schema", description="Schema name")
    table: str = Field(..., description="Table name")

    model_config = ConfigDict(populate_by_name=True)  # type: ignore[assignment]

    def fqn(self, default_catalog: str | None = None) -> str:
        """Fully qualified name `catalog.schema.table`.

        Uses `self.catalog` when set; otherwise falls back to `default_catalog`
        (typically the current env's catalog).
        """
        catalog = self.catalog or default_catalog
        if not catalog:
            raise ValueError(
                f"No catalog available for table {self.schema_name}.{self.table}"
            )
        return f"{catalog}.{self.schema_name}.{self.table}"


class DatasetConfig(BaseModel):
    """Per-dataset ingestion config: input (source) + output (destination).

    Both use the same {catalog, schema, table} shape. Output catalog is
    optional and defaults to the current env's catalog at runtime.
    """

    input: TableRef = Field(..., description="Source table (fully qualified)")
    output: TableRef = Field(..., description="Destination table")

    model_config = ConfigDict(populate_by_name=True)  # type: ignore[assignment]


def load_config(
    config_path: str = "project_config.yml", env: str = "dev"
) -> ProjectConfig:
    """Load project configuration for an environment.

    Args:
        config_path: Path to configuration file
        env: Environment name — one of local, dev, stg, prod

    Returns:
        ProjectConfig instance
    """
    resolved = _resolve_config_path(config_path)
    return ProjectConfig.from_yaml(resolved, env)


def load_dataset(dataset: str, config_path: str = "project_config.yml") -> DatasetConfig:
    """Load per-dataset config from the `datasets` section of the config file.

    Args:
        dataset: Key under the top-level `datasets:` block
        config_path: Path to configuration file

    Returns:
        DatasetConfig instance

    Raises:
        ValueError: If dataset key is missing or `datasets` section is absent
    """
    resolved = _resolve_config_path(config_path)
    with open(resolved, encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f)

    datasets = raw.get("datasets") or {}
    if dataset not in datasets:
        available = sorted(datasets.keys())
        raise ValueError(
            f"Dataset '{dataset}' not found in {resolved}. "
            f"Available datasets: {available}"
        )

    return DatasetConfig(**datasets[dataset])


def _resolve_config_path(config_path: str) -> str:
    """Resolve a relative config path by walking up the tree looking for it."""
    if Path(config_path).is_absolute():
        return config_path

    current = Path.cwd()
    for _ in range(3):
        candidate = current / config_path
        if candidate.exists():
            return str(candidate)
        current = current.parent
    return config_path
