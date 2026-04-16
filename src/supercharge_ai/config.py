"""Configuration management for Supercharge AI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field


class ProjectConfig(BaseModel):
    """Project configuration model."""

    catalog: str = Field(..., description="Unity Catalog name")
    schema_name: str = Field(..., alias="schema", description="Schema name")
    volume: str = Field(..., description="Volume name")
    llm_endpoint: str = Field(default="", description="LLM endpoint name")
    embedding_endpoint: str = Field(default="", description="Embedding endpoint name")
    warehouse_id: str = Field(default="", description="Warehouse ID")
    vector_search_endpoint: str = Field(
        default="", description="Vector search endpoint name"
    )
    genie_space_id: str | None = Field(default=None, description="Genie Space ID")

    model_config = ConfigDict(populate_by_name=True)  # type: ignore[assignment]

    @classmethod
    def from_yaml(cls, config_path: str, env: str = "dev") -> ProjectConfig:
        """Load configuration from YAML file.

        Args:
            config_path: Path to the YAML configuration file
            env: Environment name (dev, acc, prd)

        Returns:
            ProjectConfig instance

        Raises:
            ValueError: If environment is invalid or not found
        """
        if env not in ["prd", "acc", "dev"]:
            raise ValueError(
                f"Invalid environment: {env}. Expected 'prd', 'acc', or 'dev'"
            )

        with open(config_path) as f:
            config_data: dict[str, Any] = yaml.safe_load(f)

        if env not in config_data:
            raise ValueError(f"Environment '{env}' not found in config file")

        return cls(**config_data[env])

    @property
    def full_schema_name(self) -> str:
        """Get fully qualified schema name."""
        return f"{self.catalog}.{self.schema_name}"

    @property
    def full_volume_path(self) -> str:
        """Get fully qualified volume path as filesystem path."""
        return f"/Volumes/{self.catalog}/{self.schema_name}/{self.volume}"


def load_config(
    config_path: str = "project_config.yml", env: str = "dev"
) -> ProjectConfig:
    """Load project configuration.

    Args:
        config_path: Path to configuration file
        env: Environment name (dev, acc, prd)

    Returns:
        ProjectConfig instance
    """
    if not Path(config_path).is_absolute():
        current = Path.cwd()
        for _ in range(3):
            candidate = current / config_path
            if candidate.exists():
                config_path = str(candidate)
                break
            current = current.parent

    return ProjectConfig.from_yaml(config_path, env)
