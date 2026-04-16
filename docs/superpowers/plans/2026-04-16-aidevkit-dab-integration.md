# AI-Dev-Kit + Databricks Asset Bundles Integration Project

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a reusable, production-grade project template that demonstrates ai-dev-kit integration with Databricks Asset Bundles, with multi-environment deployment (dev/acc/prd) and GitHub Actions CI/CD.

**Architecture:** The project follows a modular structure where ai-dev-kit orchestrates the creation and deployment of Databricks resources via DAB. A Python package provides reusable components (config management, logging, utilities), notebooks demonstrate workflows, and DAB manages deployment across three isolated environments. GitHub Actions handles CI/CD: linting, testing on PR, and promotion through environments on merge to main.

**Tech Stack:**
- **ai-dev-kit**: Orchestration framework
- **Databricks Asset Bundles (DAB)**: Infrastructure-as-code for Databricks
- **Python 3.12**: Core language (matches Databricks Serverless v4)
- **UV**: Dependency management
- **Pydantic**: Configuration management
- **pytest + pytest-cov**: Testing
- **Ruff**: Linting/formatting
- **pre-commit**: Local validation
- **GitHub Actions**: CI/CD pipeline
- **Loguru**: Structured logging

---

## File Structure Overview

```
supercharge-ai-template/
├── .github/
│   └── workflows/
│       ├── test.yml                    # Run tests on PR
│       └── deploy.yml                  # Deploy on merge to main
├── .claude/
│   └── commands/
│       ├── fix-deps.md                 # Skill: update pyproject.toml
│       ├── run-notebook.md             # Skill: run notebook on DAB
│       └── ship.md                     # Skill: commit + push
├── notebooks/
│   ├── 1_hello_world.py                # Basic Hello World example
│   └── 2_config_usage.py                # Demonstrate config loading
├── src/
│   └── ai_template/
│       ├── __init__.py                 # Package init
│       ├── config.py                   # Pydantic config + env resolution
│       ├── logger.py                   # Loguru setup
│       └── utils.py                    # Helper functions
├── resources/
│   ├── hello_world_job.yml             # DAB job definition
│   └── config_demo_job.yml             # DAB job definition
├── tests/
│   ├── conftest.py                     # Fixtures, mocks
│   ├── test_imports.py                 # Smoke test
│   └── unit/
│       ├── test_config.py              # Config loading tests
│       └── test_logger.py              # Logger tests
├── .pre-commit-config.yaml             # Pre-commit hooks
├── .gitignore                          # Git ignore rules
├── CLAUDE.md                           # Project guidelines
├── README.md                           # Setup + usage
├── databricks.yml                      # DAB bundle config
├── project_config.yml                  # Per-environment config
├── pyproject.toml                      # Dependencies + build
├── uv.lock                             # Locked dependencies
└── version.txt                         # Version number
```

---

## Task Breakdown

### Task 1: Initialize Git Repository & Basic Project Structure

**Files:**
- Create: `.gitignore`
- Create: `README.md` (stub)
- Create: `CLAUDE.md` (project guidelines)
- Create: `version.txt`
- Create: `pyproject.toml`
- Create: `databricks.yml`
- Create: `project_config.yml`

**Context:** Set up the basic skeleton. No code yet—just configuration and documentation.

- [ ] **Step 1: Initialize git repository**

```bash
cd /Users/rahulpandey/Projects
mkdir supercharge-ai-template
cd supercharge-ai-template
git init
git config user.name "RAHUL PANDEY"
git config user.email "rpandey1901@gmail.com"
```

- [ ] **Step 2: Create .gitignore**

Create file: `.gitignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
ENV/
env/

# IDEs
.vscode/
.cursor/
.idea/
*.swp
*.swo
*~

# Databricks
.databricks

# DAB
.bundle/
.databricks/

# Environment files
.env
.env.local

# Development artifacts
.agents/
.ai-dev-kit/
.claude/
.mcp.json

# Test artifacts
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 3: Create README.md (stub)**

Create file: `README.md`

```markdown
# AI-Dev-Kit + Databricks Asset Bundles Template

A production-ready project template demonstrating integration of ai-dev-kit with Databricks Asset Bundles (DAB) for multi-environment deployment and CI/CD.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
uv sync --extra dev
```

## Project Structure

- `src/ai_template/` — Python package (config, logging, utilities)
- `notebooks/` — Databricks notebooks (week-by-week lessons)
- `resources/` — DAB job definitions (.yml files)
- `tests/` — Unit tests (no cluster required)

## Development

```bash
# Run tests
uv run pytest

# Lint + format
uv run ruff check . --fix && uv run ruff format .

# Deploy to dev
databricks bundle deploy

# Run a job
databricks bundle run hello_world_job
```

## Environments

Three isolated environments via Unity Catalog:
- `dev` — Development (default)
- `acc` — Acceptance/Staging
- `prd` — Production

See `project_config.yml` for environment-specific settings.
```

- [ ] **Step 4: Create CLAUDE.md**

Create file: `CLAUDE.md`

```markdown
# AI-Dev-Kit + DAB Template — Project Guidelines

## Development Environment

This project uses `uv` for dependency management. Python **3.12** is required (matches Databricks Serverless Environment 4).

### Running Commands

**ALWAYS use `uv run` prefix:**

```bash
uv run pytest                          # Run tests
uv run ruff check . --fix              # Lint + auto-fix
uv run ruff format .                   # Format
uv run pre-commit run --all-files      # Run all pre-commit hooks
```

## Project Structure

```
supercharge-ai-template/
├── .claude/commands/          # Claude Code slash commands
├── .github/workflows/         # GitHub Actions CI/CD
├── notebooks/                 # Databricks notebooks
├── src/ai_template/           # Python package
├── resources/                 # DAB job definitions
├── tests/                     # Unit tests
├── databricks.yml             # DAB bundle config
├── project_config.yml         # Per-environment config
├── pyproject.toml             # Dependencies
└── version.txt                # Version
```

## Dependency Management

**Pinning Rules:**
- **Regular dependencies** (`[project] dependencies`): pin to exact version
  ```toml
  "pydantic==2.11.7"
  "databricks-sdk==0.85.0"
  ```
- **Optional/dev dependencies**: use `>=X.Y.Z,<NEXT_MAJOR`
  ```toml
  "pytest>=8.3.4,<9"
  "pre-commit>=4.1.0,<5"
  ```

## Notebook File Format

All Python files in `notebooks/` must be formatted as Databricks notebooks:
- **First line**: `# Databricks notebook source`
- **Cell separator**: `# COMMAND ----------` between logical sections

```python
# Databricks notebook source
"""
Notebook description.
"""

import os

# COMMAND ----------

print("Hello, world!")
```

**NEVER** use `#!/usr/bin/env python` shebangs.

## Git Conventions

- **Branch naming**: `feature/short-description` or `fix/issue-number-description`
- **Commits**: Conventional Commits format
  ```
  feat(scope): description
  fix(scope): description
  ```
- **PR workflow**: Feature branch → PR → review → merge to main
- **No direct commits to main**

## Skills

Custom slash commands in `.claude/commands/`:
- `/fix-deps` — Update dependencies via `/fix-deps` skill
- `/run-notebook <path>` — Deploy and run notebook on Databricks
- `/ship` — Commit with conventional format + push
```

- [ ] **Step 5: Create version.txt**

Create file: `version.txt`

```
0.0.1
```

- [ ] **Step 6: Create pyproject.toml**

Create file: `pyproject.toml`

```toml
[project]
name = "ai-template"
dynamic = ["version"]
description = "AI-Dev-Kit + Databricks Asset Bundles integration template"
requires-python = ">=3.12, <3.13"
dependencies = [
    "pydantic==2.11.7",
    "databricks-sdk==0.85.0",
    "loguru==0.7.3",
    "python-dotenv==1.1.1",
]

[project.optional-dependencies]
dev = [
    "databricks-connect>=17.0, <18",
    "ipykernel>=6.29.5, <7",
    "pip>=25.0.1, <26",
    "pre-commit>=4.1.0, <5",
    "ruff>=0.15.1, <1",
]

ci = [
    "pre-commit>=4.1.0, <5",
    "pytest>=8.3.4, <9",
    "pytest-cov>=6.0.0, <7",
]

[build-system]
requires = ["setuptools>=72.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
include = ["ai_template*"]

[tool.setuptools.dynamic]
version = { file = "version.txt" }

[tool.pytest.ini_options]
addopts = "-s --no-header --no-summary"
testpaths = ["tests"]
pythonpath = ["."]

[tool.ruff]
line-length = 90

[tool.ruff.lint]
select = [
    "F",    # pyflakes
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "B",    # flake8-bugbear
    "I",    # isort
    "UP",   # pyupgrade
    "SIM",  # flake8-simplify
    "ANN",  # flake8-annotations
]

ignore = [
    "ANN204",  # Missing return type annotation for __init__
]

[tool.ruff.lint.per-file-ignores]
"notebooks/*.py" = ["E501", "E402"]  # Line too long, module level import not at top
"tests/**/*.py" = ["ANN"]             # No annotations in tests

[tool.ruff.format]
indent-style = "space"
```

- [ ] **Step 7: Create databricks.yml (DAB configuration)**

Create file: `databricks.yml`

```yaml
bundle:
  name: ai-template

include:
  - resources/*.yml

variables:
  git_sha:
    description: "Git SHA of the deployed commit"
    default: "local"
  schedule_pause_status:
    description: "Schedule pause status"
    default: PAUSED

artifacts:
  default:
    type: whl
    build: uv build
    path: .

targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://your-dev-workspace.cloud.databricks.com
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}

  acc:
    workspace:
      host: https://your-acc-workspace.cloud.databricks.com
      root_path: /Shared/.bundle/${bundle.name}/${bundle.target}
    variables:
      schedule_pause_status: PAUSED

  prd:
    workspace:
      host: https://your-prd-workspace.cloud.databricks.com
      root_path: /Shared/.bundle/${bundle.name}/${bundle.target}
    variables:
      schedule_pause_status: UNPAUSED
```

- [ ] **Step 8: Create project_config.yml**

Create file: `project_config.yml`

```yaml
# Project Configuration for AI Template — Dev, Acceptance, Production

dev:
  catalog: dev
  schema: ai_template
  volume: data
  llm_endpoint: databricks-llama-4-maverick
  embedding_endpoint: databricks-gte-large-en
  warehouse_id: ""
  vector_search_endpoint: ai_template_vs_endpoint
  genie_space_id: ""

acc:
  catalog: acc
  schema: ai_template
  volume: data
  llm_endpoint: databricks-llama-4-maverick
  embedding_endpoint: databricks-gte-large-en
  warehouse_id: ""
  vector_search_endpoint: ai_template_vs_endpoint
  genie_space_id: ""

prd:
  catalog: prd
  schema: ai_template
  volume: data
  llm_endpoint: databricks-llama-4-maverick
  embedding_endpoint: databricks-gte-large-en
  warehouse_id: ""
  vector_search_endpoint: ai_template_vs_endpoint
  genie_space_id: ""
```

- [ ] **Step 9: Commit initial setup**

```bash
git add .gitignore README.md CLAUDE.md version.txt pyproject.toml databricks.yml project_config.yml
git commit -m "chore: initialize project structure and configuration"
```

---

### Task 2: Create Python Package Structure & Config Module

**Files:**
- Create: `src/ai_template/__init__.py`
- Create: `src/ai_template/config.py`
- Create: `tests/conftest.py`
- Create: `tests/test_imports.py`
- Create: `tests/unit/test_config.py`

**Context:** Build the core Python package with Pydantic-based configuration management. Test-driven: write tests first, then implement.

- [ ] **Step 1: Create package init file**

Create file: `src/ai_template/__init__.py`

```python
"""AI Template — AI-Dev-Kit + Databricks Asset Bundles Integration."""

from __future__ import annotations

__version__ = "0.0.1"
__author__ = "Rahul Pandey"
__email__ = "rpandey1901@gmail.com"

__all__ = ["__version__"]
```

- [ ] **Step 2: Write test for config import**

Create file: `tests/test_imports.py`

```python
"""Smoke tests for package imports."""


def test_package_imports():
    """Test that ai_template package imports without error."""
    import ai_template
    assert ai_template.__version__ == "0.0.1"


def test_config_module_imports():
    """Test that config module imports without error."""
    from ai_template.config import ProjectConfig, load_config
    assert ProjectConfig is not None
    assert load_config is not None
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd /Users/rahulpandey/Projects/supercharge-ai-template
uv run pytest tests/test_imports.py -v
```

Expected output:
```
FAILED tests/test_imports.py::test_config_module_imports - ImportError: cannot import name 'ProjectConfig'
```

- [ ] **Step 4: Write test for config loading**

Create file: `tests/unit/test_config.py`

```python
"""Tests for configuration management."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_template.config import ProjectConfig, load_config


def test_project_config_from_dict():
    """Test creating ProjectConfig from dictionary."""
    config_data = {
        "catalog": "dev",
        "schema": "ai_template",
        "volume": "data",
        "llm_endpoint": "databricks-llama",
        "embedding_endpoint": "databricks-gte",
        "warehouse_id": "test-warehouse-id",
        "vector_search_endpoint": "test-vs-endpoint",
    }
    config = ProjectConfig(**config_data)

    assert config.catalog == "dev"
    assert config.schema == "ai_template"
    assert config.full_schema_name == "dev.ai_template"
    assert config.full_volume_path == "/Volumes/dev/ai_template/data"


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
  schema: ai_template
  volume: data
  llm_endpoint: databricks-llama
  embedding_endpoint: databricks-gte
  warehouse_id: test-warehouse
  vector_search_endpoint: test-vs

acc:
  catalog: acc
  schema: ai_template
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
        assert config.schema == "ai_template"


def test_load_config_invalid_environment():
    """Test that invalid environment raises error."""
    yaml_content = """
dev:
  catalog: dev
  schema: ai_template
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
```

- [ ] **Step 5: Create conftest.py for fixtures**

Create file: `tests/conftest.py`

```python
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
        "schema": "ai_template",
        "volume": "data",
        "llm_endpoint": "databricks-llama",
        "embedding_endpoint": "databricks-gte",
        "warehouse_id": "test-warehouse-id",
        "vector_search_endpoint": "test-vs-endpoint",
    }
```

- [ ] **Step 6: Implement ProjectConfig class**

Create file: `src/ai_template/config.py`

```python
"""Configuration management for AI Template."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    """Project configuration model."""

    catalog: str = Field(..., description="Unity Catalog name")
    schema: str = Field(..., description="Schema name")
    volume: str = Field(..., description="Volume name")
    llm_endpoint: str = Field(default="", description="LLM endpoint name")
    embedding_endpoint: str = Field(default="", description="Embedding endpoint name")
    warehouse_id: str = Field(default="", description="Warehouse ID")
    vector_search_endpoint: str = Field(
        default="", description="Vector search endpoint name"
    )
    genie_space_id: str | None = Field(
        default=None, description="Genie Space ID"
    )

    model_config = {"populate_by_name": True}

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
        return f"{self.catalog}.{self.schema}"

    @property
    def full_volume_path(self) -> str:
        """Get fully qualified volume path as filesystem path."""
        return f"/Volumes/{self.catalog}/{self.schema}/{self.volume}"


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
```

- [ ] **Step 7: Run config tests to verify they pass**

```bash
uv run pytest tests/unit/test_config.py -v
```

Expected output:
```
tests/unit/test_config.py::test_project_config_from_dict PASSED
tests/unit/test_config.py::test_project_config_missing_required_field PASSED
tests/unit/test_config.py::test_load_config_from_yaml PASSED
tests/unit/test_config.py::test_load_config_invalid_environment PASSED
```

- [ ] **Step 8: Run all import tests**

```bash
uv run pytest tests/test_imports.py -v
```

Expected output:
```
tests/test_imports.py::test_package_imports PASSED
tests/test_imports.py::test_config_module_imports PASSED
```

- [ ] **Step 9: Commit package and tests**

```bash
git add src/ai_template/ tests/
git commit -m "feat: add config module with pydantic-based configuration management"
```

---

### Task 3: Create Logging Module & Utilities

**Files:**
- Create: `src/ai_template/logger.py`
- Create: `src/ai_template/utils.py`
- Create: `tests/unit/test_logger.py`

**Context:** Add structured logging and common utility functions. Simple, focused modules.

- [ ] **Step 1: Write tests for logger module**

Create file: `tests/unit/test_logger.py`

```python
"""Tests for logging setup."""

from __future__ import annotations

import tempfile
from pathlib import Path

from loguru import logger as loguru_logger

from ai_template.logger import setup_logger


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
```

- [ ] **Step 2: Run logger tests (should fail)**

```bash
uv run pytest tests/unit/test_logger.py -v
```

Expected output:
```
FAILED tests/unit/test_logger.py::test_setup_logger_returns_logger - ImportError: cannot import name 'setup_logger'
```

- [ ] **Step 3: Implement logger module**

Create file: `src/ai_template/logger.py`

```python
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
    loguru_logger.add(
        sys.stderr,
        level=level,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    # Add file handler if specified
    if log_file:
        loguru_logger.add(
            log_file,
            level=level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="7 days",
        )

    return loguru_logger
```

- [ ] **Step 4: Run logger tests (should pass)**

```bash
uv run pytest tests/unit/test_logger.py -v
```

Expected output:
```
tests/unit/test_logger.py::test_setup_logger_returns_logger PASSED
tests/unit/test_logger.py::test_setup_logger_with_file PASSED
tests/unit/test_logger.py::test_setup_logger_different_levels PASSED
```

- [ ] **Step 5: Create utils module**

Create file: `src/ai_template/utils.py`

```python
"""Utility functions for AI Template."""

from __future__ import annotations

import os
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory.

    Returns:
        Path to project root
    """
    current = Path.cwd()
    for _ in range(5):
        if (current / "databricks.yml").exists():
            return current
        current = current.parent
    return Path.cwd()


def get_notebook_path() -> str | None:
    """Get the current notebook path if running in Databricks.

    Returns:
        Notebook path or None if not in a notebook
    """
    try:
        from pyspark.sql import SparkSession

        spark = SparkSession.getActiveSession()
        if spark:
            # In Databricks notebook
            dbutils = spark.sparkContext._jvm.com.databricks.service.DBUtils  # type: ignore
            return dbutils.notebook.getContext().notebookPath().get()  # type: ignore
    except Exception:
        pass
    return None


def ensure_dir_exists(path: Path | str) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj
```

- [ ] **Step 6: Update __init__.py to export main classes**

Edit file: `src/ai_template/__init__.py`

```python
"""AI Template — AI-Dev-Kit + Databricks Asset Bundles Integration."""

from __future__ import annotations

from ai_template.config import ProjectConfig, load_config
from ai_template.logger import setup_logger

__version__ = "0.0.1"
__author__ = "Rahul Pandey"
__email__ = "rpandey1901@gmail.com"

__all__ = [
    "__version__",
    "ProjectConfig",
    "load_config",
    "setup_logger",
]
```

- [ ] **Step 7: Commit logger and utils**

```bash
git add src/ai_template/logger.py src/ai_template/utils.py tests/unit/test_logger.py
git commit -m "feat: add structured logging and utility functions"
```

---

### Task 4: Set Up Pre-commit Hooks & Linting

**Files:**
- Create: `.pre-commit-config.yaml`
- Create: `tests/unit/__init__.py`

**Context:** Configure pre-commit hooks for automated code quality checks (linting, formatting, type checking).

- [ ] **Step 1: Create .pre-commit-config.yaml**

Create file: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.1
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies:
          - pydantic
          - types-PyYAML
        args: [--ignore-missing-imports]
        exclude: ^notebooks/
```

- [ ] **Step 2: Create tests/unit/__init__.py**

Create file: `tests/unit/__init__.py`

```python
"""Unit tests for AI Template."""
```

- [ ] **Step 3: Create tests/__init__.py**

Create file: `tests/__init__.py`

```python
"""Tests for AI Template."""
```

- [ ] **Step 4: Install and run pre-commit hooks**

```bash
uv sync --extra dev
uv run pre-commit install
uv run pre-commit run --all-files
```

Expected: All checks pass or auto-fix issues.

- [ ] **Step 5: Run all tests to ensure nothing broke**

```bash
uv run pytest -v
```

Expected output:
```
tests/test_imports.py::test_package_imports PASSED
tests/test_imports.py::test_config_module_imports PASSED
tests/unit/test_config.py::test_project_config_from_dict PASSED
...
7 passed
```

- [ ] **Step 6: Commit pre-commit configuration**

```bash
git add .pre-commit-config.yaml tests/__init__.py tests/unit/__init__.py
git commit -m "chore: add pre-commit hooks for code quality"
```

---

### Task 5: Create Databricks Notebooks

**Files:**
- Create: `notebooks/1_hello_world.py`
- Create: `notebooks/2_config_usage.py`

**Context:** Create two simple example notebooks demonstrating basic usage and config loading on Databricks.

- [ ] **Step 1: Create hello_world notebook**

Create file: `notebooks/1_hello_world.py`

```python
# Databricks notebook source
"""
Hello World Notebook

This notebook demonstrates:
- Databricks notebook format
- Cell structure (using # COMMAND ----------)
- Basic Databricks operations
"""

# COMMAND ----------

print("Welcome to AI Template!")
print("This is a simple Hello World notebook running on Databricks.")

# COMMAND ----------

# Get the workspace client
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
current_user = w.current_user.me()

print(f"\nLogged in as: {current_user.display_name}")
print(f"Email: {current_user.emails[0].value if current_user.emails else 'N/A'}")

# COMMAND ----------

print("\n✓ Hello World notebook completed successfully!")
```

- [ ] **Step 2: Create config_usage notebook**

Create file: `notebooks/2_config_usage.py`

```python
# Databricks notebook source
"""
Configuration Usage Example

This notebook demonstrates:
- Loading project configuration
- Accessing environment-specific settings
- Using the configuration in Databricks context
"""

# COMMAND ----------

# Import the config loader
from ai_template.config import load_config
from loguru import logger

# COMMAND ----------

# Load configuration for current environment
config = load_config("project_config.yml", env="dev")

print("Loaded Configuration:")
print(f"  Catalog: {config.catalog}")
print(f"  Schema: {config.schema}")
print(f"  Volume: {config.volume}")
print(f"  Full Schema Name: {config.full_schema_name}")
print(f"  Full Volume Path: {config.full_volume_path}")

# COMMAND ----------

# Log some information
logger.info(f"Using catalog: {config.catalog}")
logger.info(f"Using schema: {config.schema}")
logger.info(f"LLM Endpoint: {config.llm_endpoint}")

# COMMAND ----------

print("\n✓ Configuration usage example completed successfully!")
```

- [ ] **Step 3: Commit notebooks**

```bash
git add notebooks/
git commit -m "feat: add hello world and config usage example notebooks"
```

---

### Task 6: Create DAB Job Definitions

**Files:**
- Create: `resources/hello_world_job.yml`
- Create: `resources/config_demo_job.yml`

**Context:** Define two DAB jobs that run the notebooks as scheduled or on-demand tasks.

- [ ] **Step 1: Create hello_world_job.yml**

Create file: `resources/hello_world_job.yml`

```yaml
resources:
  jobs:
    hello_world_job:
      name: Hello World Job
      description: Demonstrates basic notebook execution via DAB
      tasks:
        - task_key: hello_world
          notebook_task:
            notebook_path: ${workspace.root_path}/notebooks/1_hello_world
          existing_cluster_id: null
          new_cluster:
            spark_version: 15.4.x-scala2.12
            node_type_id: i3.xlarge
            num_workers: 1
            spark_conf:
              spark.databricks.cluster.profile: singleNode
      max_concurrent_runs: 1
```

- [ ] **Step 2: Create config_demo_job.yml**

Create file: `resources/config_demo_job.yml`

```yaml
resources:
  jobs:
    config_demo_job:
      name: Config Demo Job
      description: Demonstrates configuration loading and usage
      tasks:
        - task_key: config_demo
          notebook_task:
            notebook_path: ${workspace.root_path}/notebooks/2_config_usage
          existing_cluster_id: null
          new_cluster:
            spark_version: 15.4.x-scala2.12
            node_type_id: i3.xlarge
            num_workers: 1
            spark_conf:
              spark.databricks.cluster.profile: singleNode
      max_concurrent_runs: 1
```

- [ ] **Step 3: Verify DAB configuration is valid**

```bash
databricks bundle validate
```

Expected output:
```
Validating resources in bundle at /path/to/supercharge-ai-template...
✓ Validation succeeded
```

- [ ] **Step 4: Commit DAB job definitions**

```bash
git add resources/
git commit -m "feat: add DAB job definitions for notebooks"
```

---

### Task 7: Create GitHub Actions CI/CD Workflow

**Files:**
- Create: `.github/workflows/test.yml`
- Create: `.github/workflows/deploy.yml`

**Context:** Set up GitHub Actions for running tests on PR and deploying on merge to main.

- [ ] **Step 1: Create test workflow**

Create file: `.github/workflows/test.yml`

```yaml
name: Tests & Linting

on:
  pull_request:
    branches:
      - main
  push:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: .venv
          key: ${{ runner.os }}-venv-${{ hashFiles('**/uv.lock') }}
          restore-keys: |
            ${{ runner.os }}-venv-

      - name: Install dependencies
        run: uv sync --extra ci

      - name: Lint with Ruff
        run: uv run ruff check .

      - name: Format check with Ruff
        run: uv run ruff format . --check

      - name: Run tests
        run: uv run pytest -v --cov=src --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: false
```

- [ ] **Step 2: Create deploy workflow**

Create file: `.github/workflows/deploy.yml`

```yaml
name: Deploy via DAB

on:
  push:
    branches:
      - main

jobs:
  deploy-dev:
    runs-on: ubuntu-latest
    environment:
      name: dev
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Install Databricks CLI
        run: pip install databricks-cli

      - name: Build wheel
        run: uv build

      - name: Authenticate with Databricks
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_DEV_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_DEV_TOKEN }}
        run: |
          mkdir -p ~/.databricks
          cat > ~/.databricks/DEFAULT << EOF
          host = ${{ secrets.DATABRICKS_DEV_HOST }}
          token = ${{ secrets.DATABRICKS_DEV_TOKEN }}
          EOF

      - name: Deploy to dev
        run: databricks bundle deploy --target dev

      - name: Run validation job
        run: databricks bundle run hello_world_job --target dev

  deploy-acc:
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment:
      name: acc
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Install Databricks CLI
        run: pip install databricks-cli

      - name: Build wheel
        run: uv build

      - name: Authenticate with Databricks
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_ACC_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_ACC_TOKEN }}
        run: |
          mkdir -p ~/.databricks
          cat > ~/.databricks/DEFAULT << EOF
          host = ${{ secrets.DATABRICKS_ACC_HOST }}
          token = ${{ secrets.DATABRICKS_ACC_TOKEN }}
          EOF

      - name: Deploy to acc
        run: databricks bundle deploy --target acc

  deploy-prd:
    needs: deploy-acc
    runs-on: ubuntu-latest
    environment:
      name: prd
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Install Databricks CLI
        run: pip install databricks-cli

      - name: Build wheel
        run: uv build

      - name: Authenticate with Databricks
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_PRD_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_PRD_TOKEN }}
        run: |
          mkdir -p ~/.databricks
          cat > ~/.databricks/DEFAULT << EOF
          host = ${{ secrets.DATABRICKS_PRD_HOST }}
          token = ${{ secrets.DATABRICKS_PRD_TOKEN }}
          EOF

      - name: Deploy to prd
        run: databricks bundle deploy --target prd
```

- [ ] **Step 3: Create GitHub environment secrets documentation**

Create file: `.github/SECRETS.md`

```markdown
# GitHub Secrets Setup

Configure these secrets in your GitHub repository for CI/CD:

## Development Environment (env:dev)
- `DATABRICKS_DEV_HOST` — Databricks workspace URL (e.g., https://your-workspace.cloud.databricks.com)
- `DATABRICKS_DEV_TOKEN` — Databricks PAT (Personal Access Token)

## Acceptance Environment (env:acc)
- `DATABRICKS_ACC_HOST` — Databricks workspace URL
- `DATABRICKS_ACC_TOKEN` — Databricks PAT

## Production Environment (env:prd)
- `DATABRICKS_PRD_HOST` — Databricks workspace URL
- `DATABRICKS_PRD_TOKEN` — Databricks PAT

### How to Create Databricks PAT

1. Log into your Databricks workspace
2. Click on your user profile (top right)
3. Select "User Settings"
4. Click "Generate new token"
5. Copy the token and add to GitHub Secrets

### How to Add GitHub Secrets

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret name and value
4. Also create GitHub Environments:
   - Settings → Environments → New environment
   - Create `dev`, `acc`, `prd` environments
   - Add the corresponding secrets to each environment
```

- [ ] **Step 4: Commit CI/CD workflows**

```bash
git add .github/
git commit -m "chore: add GitHub Actions CI/CD workflows"
```

---

### Task 8: Create Documentation & Setup Guide

**Files:**
- Modify: `README.md` (expand with full content)
- Create: `docs/SETUP.md`
- Create: `docs/ARCHITECTURE.md`

**Context:** Document the project thoroughly for developers and operators.

- [ ] **Step 1: Expand README.md**

Edit file: `README.md`

```markdown
# AI-Dev-Kit + Databricks Asset Bundles Template

A production-ready project template demonstrating integration of ai-dev-kit with Databricks Asset Bundles (DAB) for multi-environment deployment and CI/CD.

## Features

✅ **Multi-environment support** (dev, acc, prd) via Unity Catalog
✅ **Databricks Asset Bundles** for infrastructure-as-code
✅ **Python 3.12** with UV dependency management
✅ **Pydantic-based configuration** for environment-specific settings
✅ **Structured logging** via Loguru
✅ **Comprehensive testing** (pytest, fixtures, mocks)
✅ **Pre-commit hooks** (Ruff, formatting, type checking)
✅ **GitHub Actions CI/CD** (test on PR, deploy on merge to main)
✅ **Databricks notebooks** with cell structure
✅ **Professional git workflow** (conventional commits, PRs)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/supercharge-ai-template.git
cd supercharge-ai-template
```

### 2. Install Dependencies

```bash
# Install Python 3.12 (required)
python --version  # Should be 3.12.x

# Install uv
pip install uv

# Install project with dev dependencies
uv sync --extra dev
```

### 3. Set Up Pre-commit Hooks

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

### 4. Configure Databricks

```bash
# Authenticate with Databricks
databricks configure --host https://your-workspace.cloud.databricks.com

# Or use VS Code Databricks extension (recommended)
```

### 5. Update Configuration

Edit `project_config.yml` to match your Databricks workspace:

```yaml
dev:
  catalog: dev
  schema: ai_template
  warehouse_id: "your-warehouse-id"
  vector_search_endpoint: "your-vs-endpoint"
  # ... other fields
```

Also update `databricks.yml` with your workspace URLs:

```yaml
targets:
  dev:
    workspace:
      host: https://your-dev-workspace.cloud.databricks.com
  acc:
    workspace:
      host: https://your-acc-workspace.cloud.databricks.com
  prd:
    workspace:
      host: https://your-prd-workspace.cloud.databricks.com
```

## Development Workflow

### Running Tests

```bash
# All tests
uv run pytest

# With verbose output
uv run pytest -v

# With coverage
uv run pytest --cov=src --cov-report=html

# Specific test file
uv run pytest tests/unit/test_config.py -v
```

### Linting & Formatting

```bash
# Check and auto-fix
uv run ruff check . --fix

# Format code
uv run ruff format .

# Both in one
uv run ruff check . --fix && uv run ruff format .
```

### Running Pre-commit Hooks

```bash
# Install hooks (one-time)
uv run pre-commit install

# Run on all files
uv run pre-commit run --all-files

# Run on staged files only
uv run pre-commit run
```

## Deployment

### Deploy to Development

```bash
# Validate bundle
databricks bundle validate

# Deploy
databricks bundle deploy

# Run a job
databricks bundle run hello_world_job
```

### Deploy to Acceptance

```bash
databricks bundle deploy --target acc
databricks bundle run hello_world_job --target acc
```

### Deploy to Production

```bash
databricks bundle deploy --target prd
databricks bundle run hello_world_job --target prd
```

### Via GitHub Actions

1. Push to main branch
2. GitHub Actions automatically:
   - Runs tests (on PR)
   - Deploys to dev (on merge)
   - Deploys to acc (after dev succeeds)
   - Deploys to prd (after acc succeeds)

## Project Structure

```
supercharge-ai-template/
├── .github/
│   ├── workflows/
│   │   ├── test.yml                # PR & push tests
│   │   └── deploy.yml              # Deploy on merge to main
│   └── SECRETS.md                  # GitHub Secrets setup
├── .claude/
│   └── commands/                   # Claude Code skills
├── notebooks/
│   ├── 1_hello_world.py            # Basic example
│   └── 2_config_usage.py           # Config loading example
├── src/
│   └── ai_template/
│       ├── __init__.py             # Package init
│       ├── config.py               # Pydantic configuration
│       ├── logger.py               # Loguru setup
│       └── utils.py                # Helper functions
├── resources/
│   ├── hello_world_job.yml         # DAB job definition
│   └── config_demo_job.yml         # DAB job definition
├── tests/
│   ├── conftest.py                 # Fixtures
│   ├── test_imports.py             # Smoke tests
│   └── unit/
│       ├── test_config.py          # Config tests
│       └── test_logger.py          # Logger tests
├── docs/
│   ├── SETUP.md                    # Setup guide
│   └── ARCHITECTURE.md             # Architecture overview
├── .pre-commit-config.yaml         # Pre-commit hooks
├── CLAUDE.md                       # Project guidelines
├── README.md                       # This file
├── databricks.yml                  # DAB bundle config
├── project_config.yml              # Per-environment config
├── pyproject.toml                  # Dependencies
├── uv.lock                         # Locked versions
└── version.txt                     # Version
```

## Technologies

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.12 |
| **Dependency Management** | UV |
| **Configuration** | Pydantic + YAML |
| **Logging** | Loguru |
| **Testing** | pytest + pytest-cov |
| **Linting** | Ruff |
| **Code Quality** | Pre-commit hooks |
| **Deployment** | Databricks Asset Bundles |
| **CI/CD** | GitHub Actions |
| **Platform** | Databricks (Serverless Compute v4) |

## Git Workflow

1. Create feature branch: `git checkout -b feature/short-description`
2. Make changes and commit: `git commit -m "feat(scope): description"`
3. Push to GitHub: `git push origin feature/short-description`
4. Open Pull Request against `main`
5. GitHub Actions runs tests automatically
6. After approval, merge to `main`
7. GitHub Actions automatically deploys to dev, acc, and prd

### Commit Format (Conventional Commits)

```
feat(config): add new configuration option
fix(logger): handle file rotation correctly
refactor(utils): simplify directory creation
docs: update README with examples
test: add tests for config loading
chore: update dependencies
```

## Environment Variables

Create `.env` file for local development (not committed):

```bash
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-personal-access-token
```

## Troubleshooting

### Import Errors

Ensure `src/` is in PYTHONPATH. The `pyproject.toml` configures this automatically.

```bash
# Verify imports work
python -c "from ai_template import ProjectConfig, load_config; print('✓ Imports OK')"
```

### Configuration Not Found

The `load_config()` function searches parent directories up to 3 levels. Ensure `project_config.yml` is in the project root.

```bash
# Find project root
find . -name "project_config.yml"
```

### DAB Validation Fails

```bash
# Validate bundle
databricks bundle validate

# Check workspace connectivity
databricks workspace list /
```

## Contributing

1. Follow git workflow above
2. Write tests for new features (TDD)
3. Ensure all tests pass: `uv run pytest`
4. Ensure code passes linting: `uv run ruff check . --fix`
5. Pre-commit hooks run automatically on commit

## Resources

- [Databricks Asset Bundles Documentation](https://docs.databricks.com/en/dev-tools/bundles/)
- [Databricks SDK for Python](https://databricks-sdk-py.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

## License

MIT

## Author

Rahul Pandey — rpandey1901@gmail.com
```

- [ ] **Step 2: Create SETUP.md**

Create file: `docs/SETUP.md`

```markdown
# Setup Guide

## Prerequisites

- Python 3.12.x
- Git
- Databricks workspace (dev, acc, prd)
- GitHub repository
- Databricks CLI

## Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/supercharge-ai-template.git
cd supercharge-ai-template
```

## Step 2: Install Python 3.12

Check your current Python version:

```bash
python --version
```

If not 3.12, install it:

```bash
# macOS (using Homebrew)
brew install python@3.12

# Or use pyenv
pyenv install 3.12.0
pyenv local 3.12.0

# Linux (Ubuntu/Debian)
sudo apt-get install python3.12 python3.12-venv

# Windows
# Download from https://www.python.org/downloads/
```

## Step 3: Install UV

UV is a fast dependency resolver and installer written in Rust.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Windows (via pip)
pip install uv

# Verify installation
uv --version
```

## Step 4: Install Dependencies

```bash
cd supercharge-ai-template

# Create virtual environment and install dependencies
uv sync --extra dev

# If you only need production dependencies
uv sync

# If you need CI dependencies
uv sync --extra ci
```

## Step 5: Configure Databricks Authentication

### Option A: Databricks CLI

```bash
# Configure
databricks configure --host https://your-workspace.cloud.databricks.com

# You'll be prompted for:
# - Host URL
# - Token (paste your PAT)

# Verify
databricks workspace list /
```

### Option B: Environment Variables

Create `.env` file (not committed):

```bash
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi...
```

### Option C: VS Code Databricks Extension

1. Install [Databricks extension for VS Code](https://marketplace.visualstudio.com/items?itemName=databricks.databricks)
2. Click Databricks icon in sidebar
3. Sign in with your Databricks credentials
4. Select workspace

## Step 6: Create Unity Catalog Objects

For each environment (dev, acc, prd), create the required objects in your Databricks workspace:

```sql
-- Development
CREATE CATALOG IF NOT EXISTS dev;
CREATE SCHEMA IF NOT EXISTS dev.ai_template;
CREATE VOLUME IF NOT EXISTS dev.ai_template.data;

-- Acceptance
CREATE CATALOG IF NOT EXISTS acc;
CREATE SCHEMA IF NOT EXISTS acc.ai_template;
CREATE VOLUME IF NOT EXISTS acc.ai_template.data;

-- Production
CREATE CATALOG IF NOT EXISTS prd;
CREATE SCHEMA IF NOT EXISTS prd.ai_template;
CREATE VOLUME IF NOT EXISTS prd.ai_template.data;
```

You can run this SQL in your Databricks workspace SQL editor.

## Step 7: Update Configuration

Edit `project_config.yml` with your actual workspace details:

```yaml
dev:
  catalog: dev
  schema: ai_template
  volume: data
  warehouse_id: "your-dev-warehouse-id"  # Find in Databricks workspace
  llm_endpoint: "databricks-llama-4-maverick"
  embedding_endpoint: "databricks-gte-large-en"
  vector_search_endpoint: "your-vs-endpoint"

# ... repeat for acc and prd
```

To find your warehouse ID:
1. Go to Databricks workspace → SQL → Warehouses
2. Click on your warehouse
3. Copy the ID from the URL (or click Details)

Edit `databricks.yml` with your workspace URLs:

```yaml
targets:
  dev:
    workspace:
      host: https://your-dev-workspace.cloud.databricks.com

  acc:
    workspace:
      host: https://your-acc-workspace.cloud.databricks.com

  prd:
    workspace:
      host: https://your-prd-workspace.cloud.databricks.com
```

## Step 8: Install Pre-commit Hooks

```bash
# Install git hooks
uv run pre-commit install

# Run on all files to check
uv run pre-commit run --all-files

# If any issues, fix them and retry
```

## Step 9: Run Tests

```bash
# Run all tests
uv run pytest -v

# With coverage
uv run pytest --cov=src --cov-report=html

# Check coverage report
open htmlcov/index.html
```

## Step 10: Validate DAB Configuration

```bash
# Validate bundle configuration
databricks bundle validate

# Should output: ✓ Validation succeeded
```

## Step 11: Deploy to Development

```bash
# Deploy the bundle to dev workspace
databricks bundle deploy

# Run a test job
databricks bundle run hello_world_job

# Check job results in Databricks workspace → Workflows → Jobs
```

## Step 12: Set Up GitHub Secrets (for CI/CD)

1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Add repository secrets:
   - `DATABRICKS_DEV_HOST` — your dev workspace URL
   - `DATABRICKS_DEV_TOKEN` — your dev PAT token
   - `DATABRICKS_ACC_HOST` — your acc workspace URL
   - `DATABRICKS_ACC_TOKEN` — your acc PAT token
   - `DATABRICKS_PRD_HOST` — your prd workspace URL
   - `DATABRICKS_PRD_TOKEN` — your prd PAT token

3. Create GitHub Environments:
   - Settings → Environments → New environment
   - Create `dev`, `acc`, `prd` environments
   - Add the corresponding secrets to each environment

4. Update environment protection rules (optional):
   - For `acc` and `prd`: require reviews before deployment
   - This adds a manual approval step

## Verification Checklist

- [ ] Python 3.12 installed
- [ ] UV installed and working
- [ ] Dependencies installed (`uv sync --extra dev`)
- [ ] Pre-commit hooks installed (`uv run pre-commit install`)
- [ ] Databricks authentication configured
- [ ] `project_config.yml` updated with your workspace details
- [ ] `databricks.yml` updated with your workspace URLs
- [ ] Unity Catalog objects created (catalog, schema, volume)
- [ ] All tests passing (`uv run pytest -v`)
- [ ] DAB validation passes (`databricks bundle validate`)
- [ ] Dev deployment works (`databricks bundle deploy`)
- [ ] GitHub Secrets configured
- [ ] Ready to develop!

## Troubleshooting

### Python 3.12 Not Found

```bash
# Check available Python versions
ls /usr/bin/python*

# Or with pyenv
pyenv versions
```

### UV Installation Failed

```bash
# Alternative: install via pip
pip install uv

# Or via conda
conda install -c conda-forge uv
```

### Databricks Authentication Failed

```bash
# Check configuration
cat ~/.databrickscfg

# Re-configure
databricks configure --token
```

### DAB Validation Fails

```bash
# Check for syntax errors
databricks bundle validate --verbose

# Check workspace connectivity
databricks workspace list /
```

### Tests Failing

```bash
# Check imports
python -c "from ai_template import ProjectConfig; print('OK')"

# Run with verbose output
uv run pytest -vv

# Check for missing dependencies
uv sync --extra dev
```

## Next Steps

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes to the code
3. Write tests for new features
4. Run tests: `uv run pytest`
5. Commit with conventional message: `git commit -m "feat(scope): description"`
6. Push and open a PR: `git push origin feature/my-feature`
7. GitHub Actions will run tests automatically
8. After approval, merge to main
9. GitHub Actions will deploy automatically to dev → acc → prd

Happy coding! 🚀
```

- [ ] **Step 3: Create ARCHITECTURE.md**

Create file: `docs/ARCHITECTURE.md`

```markdown
# Architecture Overview

## High-Level Design

```
GitHub → Push/PR → GitHub Actions
                        ↓
                    Tests (pytest)
                        ↓
                    Linting (Ruff)
                        ↓
                    Deploy via DAB
                        ↓
            Databricks Workspace (dev/acc/prd)
                        ↓
         Unity Catalog + Asset Bundles Jobs
```

## Components

### 1. Python Package (`src/ai_template/`)

The core package providing reusable functionality:

- **`config.py`** — Pydantic model for environment-specific configuration
  - Loads from `project_config.yml`
  - Supports dev/acc/prd environments
  - Properties for fully qualified names
  
- **`logger.py`** — Structured logging via Loguru
  - Console and file handlers
  - Log rotation and retention
  - Different log levels per environment

- **`utils.py`** — Helper functions
  - Project root detection
  - Notebook context detection
  - Directory creation helpers

### 2. Databricks Notebooks (`notebooks/`)

Interactive notebooks for Databricks workspace:

- Formatted as Python files with cell separators (`# COMMAND ----------`)
- Can be run locally via Jupyter or on Databricks
- Demonstrate configuration usage and Databricks APIs

### 3. DAB Resources (`resources/`)

Databricks Asset Bundle job definitions in YAML:

- Reference notebooks from workspace
- Define cluster specs, timeouts, alerts
- Support environment variables and parameters
- Deployed via `databricks bundle` CLI

### 4. Tests (`tests/`)

Unit tests with comprehensive coverage:

- **Unit tests** — No Databricks cluster required
- **Fixtures** — Shared test data and mocks
- **Coverage** — Pytest with coverage reporting

### 5. Configuration Files

- **`databricks.yml`** — DAB bundle definition
  - Targets for dev/acc/prd
  - Artifact build configuration
  - Variables and environment-specific settings

- **`project_config.yml`** — Application configuration
  - Per-environment: catalog, schema, volume, endpoints
  - Loaded at runtime via `ProjectConfig.from_yaml()`

- **`pyproject.toml`** — Python packaging
  - Dependencies (exact versions)
  - Optional dependencies (dev, ci)
  - Tool configurations (pytest, ruff, setuptools)

### 6. GitHub Actions CI/CD

Two workflows:

- **`test.yml`** — On PR or push to main
  - Install dependencies (uv)
  - Lint with Ruff
  - Run tests with coverage
  - Upload coverage to Codecov

- **`deploy.yml`** — On merge to main
  - Build wheel package
  - Authenticate with Databricks (three workspaces)
  - Deploy via `databricks bundle deploy`
  - Sequential promotion: dev → acc → prd

## Data & Configuration Flow

```
┌─────────────────────────────────────────────────────────┐
│ GitHub Repository                                       │
│  ├─ notebooks/                                          │
│  ├─ src/ai_template/                                    │
│  ├─ resources/                                          │
│  ├─ databricks.yml                                      │
│  └─ project_config.yml                                  │
└────────────────────────┬────────────────────────────────┘
                         │
                    On merge to main
                         │
                         ↓
          ┌──────────────────────────────┐
          │ GitHub Actions CI/CD          │
          │  1. Build wheel               │
          │  2. Deploy (dev)              │
          │  3. Deploy (acc)              │
          │  4. Deploy (prd)              │
          └──────────────────┬────────────┘
                             │
                             ↓
     ┌───────────────────────┼───────────────────────┐
     ↓                       ↓                       ↓
┌─────────────┐      ┌─────────────────┐      ┌────────────┐
│ Dev         │      │ Acceptance      │      │ Production │
│ Workspace   │      │ Workspace       │      │ Workspace  │
└─────────────┘      └─────────────────┘      └────────────┘
     │                       │                        │
     ├─ Catalog: dev         ├─ Catalog: acc         ├─ Catalog: prd
     ├─ Schema: ai_template  ├─ Schema: ai_template  ├─ Schema: ai_template
     ├─ Volume: data         ├─ Volume: data         ├─ Volume: data
     └─ Jobs via DAB         └─ Jobs via DAB         └─ Jobs via DAB
```

## Environment Promotion Strategy

```
Feature Branch
    │
    ├─ PR → GitHub Actions Tests (pytest, ruff)
    │
    ├─ Review & Approval
    │
    └─ Merge to main
        │
        ├─ Deploy to Dev
        │   ├─ Build wheel
        │   ├─ Run validation job (hello_world_job)
        │   └─ Success → proceed
        │
        ├─ Deploy to Acceptance
        │   ├─ Build wheel
        │   ├─ Run validation job
        │   └─ Success → proceed
        │
        └─ Deploy to Production
            ├─ Build wheel
            ├─ Requires approval (optional)
            └─ Deploy
```

## Dependency Management

**Pinning Strategy:**

- **Production dependencies** (`[project] dependencies`) — pinned to exact versions
  - Example: `pydantic==2.11.7`
  - Ensures reproducible builds

- **Optional/Dev dependencies** — pinned to range
  - Example: `pytest>=8.3.4,<9`
  - Allows patch updates without changing major/minor version

**Locked Dependencies:**

- `uv.lock` — generated by UV, committed to git
- Ensures all environments have identical package versions
- Automatically updated when `pyproject.toml` changes

## Testing Strategy

**Unit Tests**
- Test individual functions and classes
- Mock external dependencies (Databricks, config files)
- Fast (< 1 second per test)
- Run locally without cluster

**Integration Tests** (future)
- Test against real Databricks workspace
- Run in CI/CD after unit tests pass
- ~30 seconds per test

**E2E Tests** (future)
- Test complete workflows
- Run in CI/CD after integration tests
- Can require manual approval

## Code Quality

**Pre-commit Hooks**
- Trailing whitespace
- File formatting
- YAML syntax
- Large files detection
- Ruff linting and formatting
- Mypy type checking

**CI/CD Checks**
- Ruff linting (`ruff check .`)
- Ruff formatting (`ruff format . --check`)
- Pytest unit tests
- Coverage reporting (can fail if <80%)

## Configuration Resolution at Runtime

```python
# In a notebook or script
from ai_template.config import load_config, get_env
from pyspark.sql import SparkSession

# Get current environment
spark = SparkSession.getActiveSession()
env = get_env(spark)  # returns 'dev', 'acc', or 'prd'

# Load environment-specific config
config = load_config("project_config.yml", env=env)

# Now use config
print(config.catalog)  # e.g., 'dev'
print(config.full_schema_name)  # e.g., 'dev.ai_template'
```

## Security & Secrets Management

- **No hardcoded secrets** in code
- **Environment variables** for sensitive data
  - `DATABRICKS_HOST`
  - `DATABRICKS_TOKEN`
- **GitHub Secrets** for CI/CD
  - Three sets (dev, acc, prd)
  - Accessed via `${{ secrets.DATABRICKS_DEV_TOKEN }}`
- **Pre-commit hook** detects private keys and prevents commits

## Scaling Considerations

**For Larger Projects:**

1. **Split notebooks into multiple files** — one per domain
2. **Create feature-specific DAB jobs** — keep resources/ organized
3. **Add integration tests** — test against real Databricks
4. **Implement approval gates** — require review before prod deploy
5. **Add monitoring** — integrate with Databricks' monitoring/MLflow
6. **Version the package** — use semantic versioning, tag releases

**Example scaled structure:**

```
notebooks/
  ├── module_1/
  │   ├── 1_ingest.py
  │   └── 2_process.py
  └── module_2/
      ├── 1_feature_engineering.py
      └── 2_model_training.py

resources/
  ├── ingestion_jobs.yml
  ├── processing_jobs.yml
  └── model_jobs.yml

src/ai_template/
  ├── pipelines/
  │   ├── ingest.py
  │   └── process.py
  └── features/
      └── engineering.py
```

## Key Patterns

### Configuration Pattern
```python
from ai_template.config import load_config
config = load_config("project_config.yml", env="dev")
catalog = config.catalog
```

### Logging Pattern
```python
from ai_template.logger import setup_logger
logger = setup_logger(__name__)
logger.info("Processing started")
```

### Testing Pattern
```python
import pytest
from ai_template.config import ProjectConfig

def test_feature(sample_config_dict):
    config = ProjectConfig(**sample_config_dict)
    assert config.full_schema_name == "dev.ai_template"
```

## Future Enhancements

1. **MLflow Integration** — experiment tracking and model versioning
2. **Delta Lake Workflows** — batch processing pipelines
3. **Vector Search** — similarity search capabilities
4. **Prompt Management** — LLM prompt versioning via MLflow
5. **Observability** — metrics, alerts, dashboards
6. **Multi-workspace Sync** — replicate configs across workspaces
```

- [ ] **Step 5: Commit documentation**

```bash
git add docs/ README.md
git commit -m "docs: add comprehensive documentation and setup guides"
```

---

### Task 9: Final Testing & Git Cleanup

**Files:**
- Verify: all tests pass
- Verify: git history clean

**Context:** Ensure everything works end-to-end before declaring the template ready.

- [ ] **Step 1: Run all tests**

```bash
uv run pytest -v --cov=src --cov-report=term-missing
```

Expected output:
```
tests/test_imports.py::test_package_imports PASSED
tests/test_imports.py::test_config_module_imports PASSED
tests/unit/test_config.py::test_project_config_from_dict PASSED
...
======================== 8 passed in 0.42s ========================
```

- [ ] **Step 2: Run pre-commit checks**

```bash
uv run pre-commit run --all-files
```

Expected output:
```
trailing-whitespace.............................................................Passed
end-of-file-fixer...............................................................Passed
check-yaml.....................................................................Passed
ruff.........................................................................Passed
ruff-format...................................................................Passed
mypy.........................................................................Passed
```

- [ ] **Step 3: Validate DAB configuration**

```bash
databricks bundle validate
```

Expected output:
```
Validating resources in bundle at /path/to/supercharge-ai-template...
✓ Validation succeeded
```

- [ ] **Step 4: Check git log**

```bash
git log --oneline
```

Expected output:
```
<commit> docs: add comprehensive documentation and setup guides
<commit> chore: add GitHub Actions CI/CD workflows
<commit> feat: add DAB job definitions for notebooks
<commit> feat: add hello world and config usage example notebooks
<commit> chore: add pre-commit hooks for code quality
<commit> feat: add structured logging and utility functions
<commit> feat: add config module with pydantic-based configuration management
<commit> chore: initialize project structure and configuration
```

- [ ] **Step 5: Create final commit summary**

```bash
git log --oneline | wc -l
# Should show ~8 commits

git log --stat | head -50
# Review the file changes
```

- [ ] **Step 6: Verify README and docs are complete**

```bash
# Check that key files exist
ls -la README.md CLAUDE.md docs/SETUP.md docs/ARCHITECTURE.md

# Spot check content
head -20 README.md
head -20 docs/SETUP.md
```

- [ ] **Step 7: Create a final git tag**

```bash
git tag -a v0.0.1 -m "Initial template release with DAB integration and GitHub Actions CI/CD"
git log --oneline --graph --all | head -15
```

---

## Success Criteria

✅ **All Tests Pass**
- Unit tests run without errors
- Coverage >= 80%
- Pre-commit checks pass

✅ **DAB Configuration Valid**
- `databricks bundle validate` succeeds
- Resources include both hello_world_job and config_demo_job
- Targets are configured for dev, acc, prd

✅ **Documentation Complete**
- README.md covers features, quick start, workflow
- docs/SETUP.md has step-by-step instructions
- docs/ARCHITECTURE.md explains design and patterns
- CLAUDE.md provides project guidelines

✅ **CI/CD Ready**
- GitHub Actions workflows are valid YAML
- test.yml runs on PR and push
- deploy.yml runs on merge to main
- Workflows deploy to dev, acc, prd sequentially

✅ **Git History Clean**
- 8-10 logical commits with conventional messages
- No merge commits (rebase workflow)
- All changes staged and committed

---

## Execution Plan Summary

This plan creates a production-ready template in **9 tasks**:

1. **Initialize project** — Git, config, documentation stubs
2. **Core Python package** — Config module, tests
3. **Logging & utilities** — Structured logging, helpers
4. **Code quality** — Pre-commit, linting, type checking
5. **Example notebooks** — Hello world, config usage
6. **DAB jobs** — Job definitions for notebooks
7. **CI/CD workflows** — GitHub Actions for testing and deployment
8. **Complete documentation** — Setup guide, architecture, README
9. **Final verification** — Tests, validation, git cleanup

**Estimated time:** 45-60 minutes for experienced developers, 2-3 hours for first-time setup.

**Output:** A reusable, professional template ready for new projects.

---
