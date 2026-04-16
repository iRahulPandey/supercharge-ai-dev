# Architecture — Supercharge AI Dev

This document describes the system design, component architecture, and operational patterns of Supercharge AI Dev.

## System Overview

Supercharge AI Dev is built on three core pillars:

1. **Local Development** — Python package with type safety, testing, and tooling
2. **Databricks Infrastructure** — Asset Bundles for job orchestration and reproducibility
3. **Environment Promotion** — Seamless movement from dev → acc → prd with configuration management

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Developer's Machine                      │
├─────────────────────────────────────────────────────────────┤
│  Git Repo                                                   │
│  ├── src/supercharge_ai/          Python Package            │
│  ├── notebooks/                   Databricks Notebooks      │
│  ├── resources/                   Job Definitions (YAML)    │
│  ├── tests/                       Unit + Integration Tests  │
│  ├── databricks.yml               Bundle Configuration      │
│  └── project_config.yml           Per-Environment Config    │
├─────────────────────────────────────────────────────────────┤
│  Development Tools                                          │
│  ├── pytest                       Test framework            │
│  ├── ruff                         Linting & formatting      │
│  ├── pre-commit                   Automated checks          │
│  └── databricks-cli               Bundle deployment        │
└─────────────────────────────────────────────────────────────┘
                              ↓ git push
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Repository                        │
├─────────────────────────────────────────────────────────────┤
│  Workflows: Tests, Linting, Security Scans                │
└─────────────────────────────────────────────────────────────┘
                              ↓ deploy -t {dev|acc|prd}
┌──────────────┬──────────────┬──────────────────────────────┐
│   Dev Env    │   Acc Env    │   Production Env            │
├──────────────┼──────────────┼──────────────────────────────┤
│ Workspace    │ Workspace    │ Workspace                   │
│ Catalog: dev │ Catalog: acc │ Catalog: prd               │
│ Schema:      │ Schema:      │ Schema:                    │
│   superchg   │   superchg   │   superchg                 │
│ Jobs:        │ Jobs:        │ Jobs:                      │
│ - hello_...  │ - hello_...  │ - hello_...               │
│ - config_... │ - config_... │ - config_...              │
└──────────────┴──────────────┴──────────────────────────────┘
```

## Component Architecture

### 1. Python Package (`src/supercharge_ai/`)

The core application package providing reusable functionality:

```
supercharge_ai/
├── __init__.py              # Public API exports
├── config.py                # Configuration loading & management
├── logger.py                # Structured logging setup
└── utils.py                 # Utility functions
```

**Key responsibilities:**
- Load configuration from YAML and environment
- Initialize Databricks SDK connections
- Provide structured logging
- Utility functions for common operations

**Design patterns:**
- Pydantic for config validation
- Singleton pattern for logger initialization
- Factory pattern for SDK client creation

### 2. Notebooks (`notebooks/`)

Databricks notebooks for interactive development and job execution:

```
notebooks/
├── 1_hello_world.py         # Basic example
└── 2_config_usage.py        # Config loading example
```

**Format requirements:**
- First line: `# Databricks notebook source`
- Cell separators: `# COMMAND ----------`
- Use `/Workspace` paths for mounted data

### 3. Databricks Asset Bundles (`resources/`, `databricks.yml`)

Infrastructure-as-code for job orchestration:

```
resources/
├── hello_world_job.yml      # Hello world job definition
└── config_demo_job.yml      # Config usage job definition
```

**Bundle features:**
- Declarative job definitions
- Multi-target deployment (dev/acc/prd)
- Version control of infrastructure
- Reproducible deployments

### 4. Configuration System (`project_config.yml`)

Environment-specific settings:

```yaml
dev:
  catalog: dev
  schema: supercharge_ai
  llm_endpoint: databricks-llama-4-maverick
  embedding_endpoint: databricks-gte-large-en

acc:
  catalog: acc
  schema: supercharge_ai
  # Same structure as dev

prd:
  catalog: prd
  schema: supercharge_ai
  # Same structure as dev
```

**Resolution order:**
1. Environment variable (`ENVIRONMENT` env var)
2. Default environment (`dev`)
3. Configuration file (`project_config.yml`)
4. .env file (via python-dotenv)

### 5. Testing Infrastructure (`tests/`)

Comprehensive test suite:

```
tests/
├── conftest.py              # Shared fixtures
├── test_imports.py          # Import validation
└── unit/
    ├── test_config.py       # Config tests
    └── test_logger.py       # Logger tests
```

**Testing approach:**
- Unit tests for isolated functionality
- Integration tests for SDK interactions
- Fixtures for common test setup
- Coverage tracking via pytest-cov

## Data & Configuration Flow

### Configuration Resolution at Runtime

```
┌──────────────────────────────────────────────────────┐
│  1. Environment Variables (highest priority)        │
│     DATABRICKS_HOST, DATABRICKS_TOKEN               │
│     ENVIRONMENT="dev|acc|prd"                       │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│  2. .env File (python-dotenv)                       │
│     DATABRICKS_HOST=...                             │
│     LOG_LEVEL=INFO                                  │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│  3. YAML Configuration (project_config.yml)         │
│     [environment].catalog                           │
│     [environment].schema                            │
│     [environment].llm_endpoint                      │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│  4. Application Code (Config object)                │
│     config.catalog                                  │
│     config.schema                                   │
│     config.get_databricks_client()                  │
└──────────────────────────────────────────────────────┘
```

### Configuration Implementation Example

```python
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import yaml

# Load .env file
load_dotenv()

class EnvironmentConfig(BaseModel):
    catalog: str
    schema: str
    llm_endpoint: str
    embedding_endpoint: str

class Config:
    def __init__(self):
        env = os.getenv("ENVIRONMENT", "dev")

        # Load from YAML
        config_path = Path("project_config.yml")
        with open(config_path) as f:
            data = yaml.safe_load(f)

        # Load environment-specific config
        env_config = data[env]
        self.environment = EnvironmentConfig(**env_config)

        # Override with environment variables
        self.databricks_host = os.getenv("DATABRICKS_HOST")
        self.databricks_token = os.getenv("DATABRICKS_TOKEN")

    def get_databricks_client(self):
        from databricks.sdk import WorkspaceClient
        return WorkspaceClient(
            host=self.databricks_host,
            token=self.databricks_token
        )
```

## Environment Promotion Strategy

### Promotion Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. LOCAL DEVELOPMENT                                       │
│     Branch: feat/my-feature                                │
│     Tests: pytest (all passing)                            │
│     Quality: ruff check, format                            │
└─────────────────────────────────────────────────────────────┘
                        ↓ git push
┌─────────────────────────────────────────────────────────────┐
│  2. PULL REQUEST & REVIEW                                   │
│     GitHub Actions: Run full test suite                    │
│     Security: Check for secrets/vulnerabilities            │
│     Code Review: Peer approval required                    │
└─────────────────────────────────────────────────────────────┘
                        ↓ merge to main
┌─────────────────────────────────────────────────────────────┐
│  3. DEV DEPLOYMENT                                          │
│     Environment: dev workspace                             │
│     Command: databricks bundle deploy -t dev               │
│     Validation: All unit tests pass                        │
└─────────────────────────────────────────────────────────────┘
                        ↓ manual promotion
┌─────────────────────────────────────────────────────────────┐
│  4. ACCEPTANCE DEPLOYMENT                                   │
│     Environment: acc workspace                             │
│     Command: databricks bundle deploy -t acc               │
│     Testing: Integration & E2E tests                       │
│     Sign-off: Team lead approval                          │
└─────────────────────────────────────────────────────────────┘
                        ↓ manual promotion
┌─────────────────────────────────────────────────────────────┐
│  5. PRODUCTION DEPLOYMENT                                   │
│     Environment: prd workspace                             │
│     Command: databricks bundle deploy -t prd               │
│     Validation: Full test suite + manual QA               │
│     Monitoring: Job success rates, error logs              │
└─────────────────────────────────────────────────────────────┘
```

### Configuration Propagation

Each environment has its own configuration that flows through the system:

```
Development:  catalog=dev,   schema=supercharge_ai
Acceptance:   catalog=acc,   schema=supercharge_ai
Production:   catalog=prd,   schema=supercharge_ai
```

Jobs automatically use the target environment's configuration via the `ENVIRONMENT` variable set during bundle deployment.

## Dependency Management

### Dependency Categories

**Core Dependencies** (pinned to exact version):
- pydantic — Configuration validation
- databricks-sdk — Workspace access
- loguru — Structured logging
- python-dotenv — Environment variables
- pyyaml — Configuration files

**Development Dependencies** (>=X.Y.Z,<NEXT_MAJOR):
- pytest — Testing framework
- pytest-cov — Coverage reporting
- pytest-asyncio — Async test support
- ruff — Linting and formatting
- pre-commit — Git hooks

### Dependency Resolution

```
pyproject.toml (source of truth)
        ↓
uv.lock (frozen, committed to git)
        ↓
venv/ (local development environment)
        ↓
CI/CD environment (GitHub Actions, Databricks)
```

**Update strategy:**
1. Edit pyproject.toml
2. Run `uv sync` to regenerate uv.lock
3. Commit both files
4. Test thoroughly before merging

## Testing Strategy

### Testing Pyramid

```
        ▲
       │ E2E Tests
       │ (Critical workflows)
       │
      ╱ ╲
     ╱   ╲  Integration Tests
    ╱     ╲ (API, SDK, DB)
   ╱───────╲
  ╱         ╲ Unit Tests
 ╱___________╲ (Functions, Classes)
```

### Test Coverage Requirements

| Component | Coverage | Priority |
|-----------|----------|----------|
| Core logic | 100% | Critical |
| Config handling | 100% | Critical |
| SDK clients | 95%+ | High |
| Utilities | 85%+ | Medium |
| Integration | 80%+ | Medium |
| Overall | 80%+ | Minimum |

### Test Execution

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=term-missing

# Specific test file
pytest tests/unit/test_config.py

# Specific test
pytest tests/unit/test_config.py::test_load_config
```

## Code Quality Standards

### Linting & Formatting

**Ruff configuration** (pyproject.toml):

```toml
[tool.ruff]
line-length = 90

[tool.ruff.lint]
select = [
    "F",     # Pyflakes
    "E",     # Errors
    "W",     # Warnings
    "B",     # Bugbear
    "I",     # Isort
    "UP",    # Pyupgrade
    "SIM",   # Simplify
    "ANN",   # Annotations
]
```

**Pre-commit hooks** (enforced before commit):

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  hooks:
    - id: ruff
      args: [--fix]
    - id: ruff-format
```

### Type Checking

```bash
mypy src/ --ignore-missing-imports
```

Configuration ensures all function signatures are typed.

### Naming Conventions

- **Functions/Variables:** `snake_case`
- **Classes:** `PascalCase`
- **Constants:** `SCREAMING_SNAKE_CASE`
- **Private:** `_leading_underscore`
- **Booleans:** `is_*`, `has_*`, `can_*`

### Code Organization

- **Functions:** <50 lines (extract helpers if longer)
- **Files:** 200-400 lines typical, 800 max
- **Nesting:** <4 levels deep
- **Imports:** Stdlib → third-party → local

## Security & Secrets Management

### Secret Protection

```
┌────────────────────────────────────┐
│  Hardcoded in code                 │ ✗ FORBIDDEN
│  In .env file (local only)         │ ✓ OK
│  In GitHub Secrets                 │ ✓ OK
│  In Databricks workspace secrets   │ ✓ BEST
└────────────────────────────────────┘
```

### Implementation Pattern

```python
import os
from databricks.sdk import WorkspaceClient

# Get secrets from environment
token = os.getenv("DATABRICKS_TOKEN")
host = os.getenv("DATABRICKS_HOST")

# Initialize client
ws = WorkspaceClient(host=host, token=token)

# Use Databricks secrets for app secrets
secret_value = ws.secrets.get_secret(
    scope="my-scope",
    key="my-key"
)
```

### Secret Scanning

Pre-commit includes secret scanning:
```bash
uv run pre-commit run --all-files
# Detects and prevents hardcoded secrets
```

## Scaling Considerations

### Multi-Project Structure

As the project grows, organize by feature:

```
supercharge-ai-dev/
├── src/supercharge_ai/
│   ├── __init__.py
│   ├── config.py
│   ├── logger.py
│   ├── features/
│   │   ├── llm_client.py
│   │   ├── vector_search.py
│   │   └── data_pipeline.py
│   └── utils/
│       ├── databricks.py
│       ├── ml.py
│       └── validation.py
├── notebooks/
│   ├── 1_hello_world.py
│   ├── experiments/
│   │   ├── llm_experiments.py
│   │   └── embedding_tests.py
│   └── production/
│       ├── data_pipeline.py
│       └── inference_job.py
└── resources/
    ├── jobs/
    │   ├── data_pipeline_job.yml
    │   └── inference_job.yml
    └── pipelines/
        └── delta_live_tables.yml
```

### Larger Test Suite

```
tests/
├── conftest.py
├── unit/
│   ├── features/
│   │   ├── test_llm_client.py
│   │   ├── test_vector_search.py
│   │   └── test_data_pipeline.py
│   └── utils/
│       ├── test_databricks.py
│       └── test_ml.py
├── integration/
│   ├── test_databricks_api.py
│   └── test_vector_search_service.py
└── e2e/
    └── test_inference_pipeline.py
```

## Key Patterns

### Configuration Pattern

```python
from pydantic import BaseModel, Field
from typing import Optional

class DatabaseConfig(BaseModel):
    catalog: str = Field(..., description="Unity Catalog name")
    schema: str = Field(..., description="Schema name")
    volume: str = Field(default="data")

config = DatabaseConfig(
    catalog="dev",
    schema="supercharge_ai"
)
print(config.catalog)  # "dev"
```

### Logging Pattern

```python
from loguru import logger
import sys

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="{time} | {level} | {message}",
    level="INFO"
)

# Use in code
logger.info("Processing job", job_id="123")
logger.error("Failed to connect", host="...", error=str(e))
```

### Error Handling Pattern

```python
from typing import Optional
from dataclasses import dataclass

@dataclass
class Result:
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

def process_data() -> Result:
    try:
        # Processing logic
        return Result(success=True, data={"rows": 100})
    except Exception as e:
        return Result(success=False, error=str(e))

# Usage
result = process_data()
if result.success:
    print(f"Processed {result.data}")
else:
    print(f"Error: {result.error}")
```

## Future Enhancements

Planned improvements and extensions:

1. **Delta Live Tables Integration** — Declarative data pipelines
2. **MLflow Integration** — Model tracking and management
3. **Monitoring & Alerts** — Job health dashboards
4. **Advanced Configuration** — Multi-region support
5. **API Layer** — REST API for job submission
6. **Documentation** — Auto-generated API docs
7. **Performance Optimization** — Caching strategies
8. **Advanced Testing** — Property-based testing

## References

- [Project README](../README.md)
- [Setup Guide](SETUP.md)
- [Databricks Bundles Documentation](https://docs.databricks.com/en/dev-tools/bundles/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Design Patterns](https://python-patterns.guide/)

---

**Last Updated:** April 2026
