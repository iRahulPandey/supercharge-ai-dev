# Supercharge AI Dev — Project Guidelines

## Core Principles

1. **Ship-to-env mindset.** Every feature you build must be deployable via Databricks Asset Bundles (DAB). Don't write ad-hoc scripts that bypass DAB. Work is a notebook + a DAB job definition, deployed to the `local` target for personal testing and to `dev`/`stg`/`prod` via CI/CD.
2. **Consult `.ai-dev-kit/` and Databricks MCP first.** For any Databricks question — SDK usage, serverless, Unity Catalog, DLT, vector search, Genie, agents — check the curated skills in `.ai-dev-kit/` (and the mirrors in `.agents/`, `.claude/`, `.github/skills/`) and the Databricks MCP tools before relying on training data. Training data lags; those references are authoritative.
3. **Security + simplicity > cleverness.** Lean, Databricks-native patterns win. No hardcoded secrets. Validate inputs. Prefer serverless over clusters, Unity Catalog over legacy permissions. Don't add frameworks or abstractions without a reason.
4. **Idempotent, declarative, tagged.** Deployments must be safe to re-run. Every resource carries `deployed_by`, `source` (local vs cicd), and `environment` tags via DAB variables.

## Task Workflow

### Simple requests

A "simple" request is one that fits cleanly into the existing patterns — e.g., "create a table in `catalog.schema`", "add a daily job that refreshes X". For these:

1. **Create a notebook** in `notebooks/NN_<snake_case>.py` using Databricks notebook format (see conventions below).
2. **Create a job YAML** in `resources/<name>_job.yml` with:
   - Serverless environment (`environment_version: "4"`)
   - Wheel installed via `dependencies: [../dist/*.whl]` if the notebook imports from `supercharge_ai`
   - Standard tags (`deployed_by`, `source`, `environment`)
   - Notebook path as `../notebooks/NN_<snake_case>.py` (relative to `resources/`, with `.py` extension)
3. **Deploy and run locally** against the `local` target: `databricks bundle deploy` then `databricks bundle run <job_name>`. Verify it works.
4. **Ask the user** before committing or raising a PR. Don't auto-commit.

### Complex requests

A "complex" request touches multiple subsystems, introduces new patterns, or has unclear scope. For these, **do not start building**:

1. Present an implementation plan: files to create/modify, task breakdown, risks, open questions.
2. Wait for user feedback.
3. Only proceed after alignment.

When in doubt, treat it as complex.

## DAB Architecture (Four Targets)

| Target | Mode | Where it deploys | Used by |
|---|---|---|---|
| `local` (default) | `development` | `/Users/{you}/.bundle/supercharge-ai/local/` | Your feature-branch development |
| `dev` | `production` | `/Workspace/supercharge-ai/dev/` | CI from `dev` branch |
| `stg` | `production` | `/Workspace/supercharge-ai/stg/` | CI from `stg` branch |
| `prod` | `production` | `/Workspace/supercharge-ai/prod/` | CI from `master` branch |

Never deploy to `dev`/`stg`/`prod` from a developer machine. Those targets are for CI only.

**GitFlow:** `feature/*` → `dev` → `stg` → `master`. PRs default to `--base dev`.

## Naming Conventions

**Notebooks** (`notebooks/`)
- `NN_snake_case.py` — two-digit numeric prefix for ordering, snake_case description
- Example: `01_ingest_products.py`, `02_compute_insights.py`
- First line must be `# Databricks notebook source`
- Cell separator: `# COMMAND ----------`
- No shebang (`#!/usr/bin/env python`)

**Jobs** (`resources/`)
- File: `<purpose>_job.yml` (e.g., `ingest_products_job.yml`)
- Logical key (top-level map key in the YAML): `<purpose>_job` — matches filename stem
- Display name: `Title Case` (e.g., `name: Ingest Products Job`)

**Unity Catalog objects**
- Tables: `snake_case`, singular (e.g., `product`, `order_item`, not `products`)
- Views: `snake_case` with `_v` suffix (e.g., `product_enriched_v`)
- Schemas: `snake_case`, function-scoped (e.g., `raw`, `curated`, `insights`)
- Volumes: `snake_case` (e.g., `landing`, `artifacts`)

**Python (PEP 8)**
- Files/functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `SCREAMING_SNAKE_CASE`
- Private: `_leading_underscore`

**Git**
- Branches: `feature/<description>` or `fix/<description>`
- Commits: Conventional Commits (`feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`)

## Development Environment

Python **3.12** is required (matches Databricks Serverless Environment 4). Use `uv` for dependency management.

**Always prefix commands with `uv run`:**

```bash
uv run pytest                          # tests
uv run ruff check . --fix              # lint + autofix
uv run ruff format .                   # format
uv run pre-commit run --all-files      # all hooks
uv build                               # build wheel (artifacts.default uses this)
```

**Databricks CLI commands** (auth via OAuth profile `DEFAULT` configured locally):

```bash
databricks bundle validate --target local      # parse + resource check
databricks bundle deploy --target local        # upload to your user workspace
databricks bundle run <job_name> --target local
databricks bundle summary --target local       # list deployed resources with URLs
databricks bundle destroy --target local       # clean up your personal deploy
```

## Project Structure

```
supercharge-ai-dev/
├── .ai-dev-kit/            # curated Databricks skills — consult FIRST
├── .claude/                # Claude Code commands + mirrored skills
├── .github/
│   └── workflows/          # CI/CD (deploy.yml, pr-preview.yml, ci.yml)
├── docs/                   # architecture, setup, DAB notes, specs, plans
├── notebooks/              # Databricks notebooks (NN_snake_case.py)
├── resources/              # DAB job definitions (*_job.yml)
├── scripts/                # infra scripts (branch protection, etc.)
├── src/supercharge_ai/     # shared Python utilities (config loader, logger)
├── tests/                  # pytest unit tests
├── databricks.yml          # DAB bundle config (4 targets: local/dev/stg/prod)
├── project_config.yml      # per-environment settings (catalog, schema, endpoints)
├── pyproject.toml          # pinned deps
└── version.txt             # package version
```

## Dependency Management

- **Regular dependencies** (`[project.dependencies]`): pin to exact version (e.g., `loguru==0.7.3`)
- **Optional/dev dependencies**: `>=X.Y.Z,<NEXT_MAJOR`
- When a notebook needs a new runtime dep, add it to `pyproject.toml` — the wheel picks it up, and jobs install it via `dependencies: [../dist/*.whl]`.

## Security Checklist (Pre-Commit)

- No hardcoded secrets, tokens, or PATs
- OAuth service principals, never PAT tokens
- Validate all user input at boundaries
- Parameterized SQL only (no string concatenation)
- No `print(config)` / `print(secret)`
- Dependencies scanned (`uv run pip-audit` if available)

## Testing Requirements

- TDD for new `src/supercharge_ai/` utilities (RED → GREEN → REFACTOR)
- 80% coverage minimum, 100% for auth/security/core business logic
- Run `uv run pytest` locally before every commit
- Notebooks themselves aren't unit-tested — validate them by running the job against `local` target

## When Something Breaks (DAB Debugging)

Don't guess. Step back:

1. Read the actual error in the CI log or local CLI output.
2. Check `.ai-dev-kit/` or use Context7 (`mcp__plugin_context7_context7__query-docs` on `/websites/databricks`) for authoritative DAB/Databricks docs.
3. Explain the root cause to the user before making a fix.
4. Iterate only after you understand what's happening.

Common pitfalls already encountered on this project:
- Notebook paths in resource YAMLs are resolved **relative to the YAML file location** (`resources/`), not the bundle root. Use `../notebooks/X.py` with the `.py` extension.
- Serverless env v4 has a narrow base library set. Install the project wheel via `dependencies: [../dist/*.whl]` in the environment spec — that's how runtime deps reach the notebook.
- `mode: production` requires an explicit non-user `root_path`. `mode: development` auto-scopes paths to `/Users/{you}/.bundle/...` and pauses schedules.
