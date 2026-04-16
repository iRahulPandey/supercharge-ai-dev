# Supercharge AI Dev — Project Guidelines

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
supercharge-ai-dev/
├── .claude/                   # Claude Code commands
├── .github/
│   └── workflows/             # GitHub Actions CI/CD
├── docs/                      # Documentation
├── notebooks/                 # Databricks notebooks
├── src/
│   └── supercharge_ai/        # Python package
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
- **Optional/dev dependencies**: use `>=X.Y.Z,<NEXT_MAJOR`

## Notebook File Format

All Python files in `notebooks/` must be Databricks notebooks:
- **First line**: `# Databricks notebook source`
- **Cell separator**: `# COMMAND ----------`

**NEVER** use `#!/usr/bin/env python` shebangs.

## Git Conventions

- **Branch naming**: `feature/description` or `fix/description`
- **Commits**: Conventional Commits (feat, fix, refactor, docs, test, chore, perf, ci)
- **PR workflow**: Feature branch → PR → review → merge to main
- **No direct commits to main**
