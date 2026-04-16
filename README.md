# Supercharge AI Dev

A comprehensive Python framework for building AI applications on Databricks with declarative infrastructure automation, integrated configuration management, and production-grade tooling.

**Supercharge AI Dev** combines the Databricks AI Dev Kit with Databricks Asset Bundles (DAB) to simplify development, testing, and deployment of AI workflows across development, staging, and production environments.

## Features

- ✅ **Multi-environment configuration** — Dev, staging, production with environment-specific overrides
- ✅ **Databricks Asset Bundles integration** — Declarative job and resource definitions via YAML
- ✅ **AI/LLM ready** — Built-in support for LLM endpoints, embedding models, and vector search
- ✅ **Production logging** — Loguru integration with structured logging
- ✅ **Type-safe configuration** — Pydantic validation for all configuration
- ✅ **Databricks SDK** — Pre-configured authentication and workspace access
- ✅ **Development tooling** — Pre-commit hooks, linting, formatting, type checking
- ✅ **Comprehensive testing** — Unit tests, pytest fixtures, test coverage tracking
- ✅ **Databricks notebooks support** — Notebook development with proper cell handling
- ✅ **CI/CD ready** — GitHub Actions workflows for automated testing and deployment

## Quick Start

### Prerequisites

- **Python 3.12+** (check `.python-version` for pinned version)
- **Git**
- **Databricks CLI** (for workspace authentication)
- **VS Code** (recommended, with Databricks extension)

### 1. Clone Repository

```bash
git clone <repository-url>
cd supercharge-ai-dev
```

### 2. Python 3.12 Installation

**macOS (using Homebrew):**
```bash
brew install python@3.12
/usr/local/opt/python@3.12/bin/python3.12 -m venv venv
source venv/bin/activate
```

**macOS (using pyenv):**
```bash
brew install pyenv
pyenv install 3.12.x
pyenv local 3.12.x
python -m venv venv
source venv/bin/activate
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3.12 python3.12-venv
python3.12 -m venv venv
source venv/bin/activate
```

**Windows (using python.org installer):**
```cmd
# Download from https://www.python.org/downloads/
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

We recommend **uv** for fast, reliable dependency management:

**Install uv:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# Windows: use the MSI installer or `pip install uv`
```

**Install project dependencies:**
```bash
uv sync --extra dev     # Install all dependencies including dev tools
```

Or use traditional pip:
```bash
pip install -e ".[dev]"  # Install with dev dependencies
```

### 4. Databricks Authentication

Choose one of three authentication methods:

**Option A: Databricks CLI (Recommended)**
```bash
databricks configure --token
# Enter workspace URL and personal access token when prompted
```

**Option B: Environment Variables**
```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."
```

**Option C: VS Code Extension**
- Install "Databricks" extension
- Authenticate through the extension UI
- Configuration is automatically picked up

### 5. Verify Installation

```bash
uv run pytest                      # Run test suite (should pass)
uv run ruff check .                # Lint check
uv run python main.py              # Run entry point
```

## Project Structure

```
supercharge-ai-dev/
├── .claude/                       # Claude Code custom commands
│   └── commands/
├── .github/
│   └── workflows/                 # GitHub Actions CI/CD
│       ├── tests.yml              # Automated test runs
│       └── deploy.yml             # Deployment workflow (manual)
├── docs/                          # Documentation
│   ├── SETUP.md                   # Detailed setup guide
│   ├── ARCHITECTURE.md            # System design and patterns
│   └── superpowers/               # Claude Code superpowers config
├── notebooks/                     # Databricks notebooks
│   ├── 1_hello_world.py           # Hello world example
│   └── 2_config_usage.py          # Configuration examples
├── resources/                     # Databricks Asset Bundle definitions
│   ├── hello_world_job.yml        # Hello world job
│   └── config_demo_job.yml        # Configuration demo job
├── src/supercharge_ai/            # Main Python package
│   ├── __init__.py                # Package exports
│   ├── config.py                  # Configuration management
│   ├── logger.py                  # Logging setup
│   └── utils.py                   # Utility functions
├── tests/                         # Test suite
│   ├── conftest.py                # Pytest fixtures
│   ├── test_imports.py            # Import validation tests
│   └── unit/                      # Unit tests by feature
│       ├── test_config.py
│       └── test_logger.py
├── .pre-commit-config.yaml        # Pre-commit hooks
├── databricks.yml                 # DAB bundle configuration
├── project_config.yml             # Per-environment configuration
├── pyproject.toml                 # Project metadata, dependencies, tool config
├── CLAUDE.md                      # Claude Code guidelines
├── version.txt                    # Version string
└── uv.lock                        # Dependency lock file
```

## Development Workflow

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_config.py

# Run tests matching pattern
uv run pytest -k test_config
```

### Code Quality

```bash
# Run linter
uv run ruff check .

# Auto-fix lint issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# Type checking
uv run python -m mypy src/ --ignore-missing-imports

# All checks in one command
uv run ruff check . && uv run ruff format . --check
```

### Pre-commit Hooks

Install local pre-commit hooks:
```bash
uv run pre-commit install
```

Run all hooks manually:
```bash
uv run pre-commit run --all-files
```

### Databricks Asset Bundles

**Validate bundle configuration:**
```bash
databricks bundle validate -t dev
```

**Deploy to dev environment:**
```bash
databricks bundle deploy -t dev
```

**Run a job in the bundle:**
```bash
databricks bundle run -t dev hello_world_job
```

**View deployment status:**
```bash
databricks bundle list -t dev
```

## Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Runtime** | Python | 3.12+ | Application runtime |
| **Config** | Pydantic | 2.11+ | Type-safe configuration |
| **Workspace SDK** | databricks-sdk | 0.85+ | Databricks API client |
| **Logging** | Loguru | 0.7+ | Structured logging |
| **Secrets** | python-dotenv | 1.1+ | Environment variable loading |
| **YAML** | PyYAML | 6.0+ | Configuration file parsing |
| **Testing** | pytest | 8.3+ | Test framework |
| **Coverage** | pytest-cov | 6.0+ | Coverage reporting |
| **Linting** | Ruff | 0.15+ | Fast Python linter |
| **Pre-commit** | pre-commit | 4.1+ | Git hook management |
| **Async** | pytest-asyncio | 0.23+ | Async test support |
| **Remote Exec** | databricks-connect | 17.0+ | Remote code execution |
| **Notebooks** | ipykernel | 6.29+ | Interactive notebook support |

## Environment Variables

Create a `.env` file in the project root (not committed to git):

```bash
# Databricks Workspace
DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
DATABRICKS_TOKEN="dapi..."

# Optional: Specific endpoint IDs
LLM_ENDPOINT="databricks-llama-4-maverick"
EMBEDDING_ENDPOINT="databricks-gte-large-en"
VECTOR_SEARCH_ENDPOINT="supercharge_vs_endpoint"

# Optional: Catalog configuration
CATALOG="dev"
SCHEMA="supercharge_ai"
VOLUME="data"

# Optional: Logging level
LOG_LEVEL="INFO"
```

The `.env` file is loaded automatically via `python-dotenv`. See `src/supercharge_ai/config.py` for configuration details.

## Git Workflow

We follow Conventional Commits for clear, semantic commit messages:

```bash
<type>(<scope>): <description>

# Types:
# feat     - New feature
# fix      - Bug fix
# refactor - Code restructuring
# docs     - Documentation only
# test     - Tests or test utilities
# chore    - Tooling, dependencies
# perf     - Performance improvement
# ci       - CI/CD changes
```

### Examples

```bash
git commit -m "feat(config): add support for dynamic environment loading"
git commit -m "fix(logger): handle async logging properly"
git commit -m "docs: update README with setup instructions"
git commit -m "test(config): add edge case tests for validation"
```

### Branch Naming

```bash
git checkout -b feat/new-feature-name
git checkout -b fix/issue-number-description
git checkout -b refactor/cleanup-description
```

### Workflow

1. Create feature branch: `git checkout -b feat/description`
2. Write tests (TDD)
3. Implement feature
4. Run tests and linting: `uv run pytest && uv run ruff check . --fix`
5. Commit with conventional message
6. Create pull request for review
7. Merge to main after approval

## Configuration

### Project Configuration (project_config.yml)

```yaml
dev:
  catalog: dev
  schema: supercharge_ai
  volume: data
  llm_endpoint: databricks-llama-4-maverick
  embedding_endpoint: databricks-gte-large-en
  warehouse_id: ""
  vector_search_endpoint: supercharge_vs_endpoint
  genie_space_id: ""
```

Configuration is loaded based on the `ENVIRONMENT` variable (defaults to `dev`). See `src/supercharge_ai/config.py` for implementation.

### Databricks Asset Bundle (databricks.yml)

```yaml
bundle:
  name: supercharge-ai

targets:
  dev:
    mode: development
    workspace:
      host: https://your-dev-workspace.cloud.databricks.com
  stg:
    workspace:
      host: https://your-stg-workspace.cloud.databricks.com
  prod:
    workspace:
      host: https://your-prod-workspace.cloud.databricks.com
```

## Troubleshooting

### Python Version Mismatch

**Error:** `ModuleNotFoundError: No module named 'supercharge_ai'`

**Solution:**
```bash
python --version  # Should be 3.12+
uv venv --python 3.12  # Create venv with specific Python
source venv/bin/activate
uv sync --extra dev
```

### Databricks Authentication Failed

**Error:** `No Databricks credentials found`

**Solution:**
```bash
# Option 1: Configure via CLI
databricks configure --token

# Option 2: Set environment variables
export DATABRICKS_HOST="https://workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."

# Option 3: Check existing config
cat ~/.databrickscfg
```

### Import Errors in IDE

**Solution:**
```bash
# Ensure package is installed in editable mode
pip install -e "."

# Rebuild virtual environment if issues persist
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
uv sync --extra dev
```

### Pre-commit Hooks Failing

**Solution:**
```bash
# Run hooks manually to see errors
uv run pre-commit run --all-files

# Auto-fix common issues
uv run ruff check . --fix
uv run ruff format .

# Then retry hooks
git add .
git commit -m "fix: address pre-commit issues"
```

### Tests Failing After Changes

**Solution:**
```bash
# Run tests with verbose output
uv run pytest -vv

# Run specific failing test
uv run pytest tests/unit/test_config.py::test_name -vv

# Check test coverage
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Bundle Deployment Issues

**Error:** `Workspace not found` or authentication error

**Solution:**
```bash
# Verify Databricks credentials
databricks workspace list

# Check bundle configuration
cat databricks.yml

# Validate bundle before deploy
databricks bundle validate -t dev

# Deploy with verbose output
databricks bundle deploy -t dev --verbose
```

## Resources

### Official Documentation
- [Databricks Asset Bundles](https://docs.databricks.com/en/dev-tools/bundles/)
- [Databricks Python SDK](https://databricks-py.readthedocs.io/)
- [Databricks AI Dev Kit](https://docs.databricks.com/en/ai-dev-kit/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### Project Documentation
- [Setup Guide](docs/SETUP.md) — Detailed installation and configuration
- [Architecture](docs/ARCHITECTURE.md) — System design and patterns
- [CLAUDE.md](CLAUDE.md) — Development guidelines and conventions

### Helpful Commands

```bash
# Check Databricks connection
databricks workspace get-status /

# List workspaces
databricks workspace list

# List jobs in bundle
databricks bundle list -t dev

# View job runs
databricks jobs list-runs --job-id <job_id>

# Get job output
databricks jobs get-run --run-id <run_id>

# Direct workspace access
databricks workspace export --source-path /Shared/file.txt --format AUTO --output-file file.txt
```

## Contributing

1. Follow TDD workflow: RED → GREEN → REFACTOR
2. Write tests before code
3. Target 80%+ test coverage
4. Follow code style rules (enforced by pre-commit hooks)
5. Use Conventional Commits
6. Create pull requests for review before merging

## License

This project is proprietary and confidential.

## Author

Rahul Pandey (rpandey1901@gmail.com)

---

**Last Updated:** April 2026

For detailed setup instructions, see [docs/SETUP.md](docs/SETUP.md).
For architecture and design details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
