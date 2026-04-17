# Supercharge AI Dev

AI/data workflows on Databricks, deployed declaratively via Databricks Asset Bundles (DAB). Python 3.12, serverless compute, Unity Catalog, OAuth service principals, GitFlow CI/CD.

> **Working on this repo with Claude or another AI assistant?** Read [`CLAUDE.md`](./CLAUDE.md) first — it documents the required workflow, naming conventions, and ship-to-env rules every feature must follow.

---

## Quick Start

### Prerequisites

- Python **3.12** (matches Databricks Serverless Environment 4)
- `uv` — [install guide](https://docs.astral.sh/uv/getting-started/installation/)
- Databricks CLI v0.218+ — `curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh`
- An OAuth profile in `~/.databrickscfg` pointing at `https://dbc-8943fe10-4fbf.cloud.databricks.com`

### Setup

```bash
git clone <repo-url>
cd supercharge-ai-dev
uv sync                          # install deps
uv run pre-commit install        # enable git hooks
uv run pytest                    # verify setup (should pass)
databricks bundle validate --target local    # verify DAB auth + config
```

### Your first local deploy

```bash
uv build                                          # build the project wheel
databricks bundle deploy --target local           # upload to /Users/you/.bundle/supercharge-ai/local/
databricks bundle summary --target local          # list deployed jobs with URLs
databricks bundle destroy --target local          # clean up when you're done
```

---

## DAB Architecture

Four targets cleanly separate local dev from managed envs:

| Target | Mode | Workspace path | Who deploys |
|---|---|---|---|
| `local` *(default)* | `development` | `/Users/{you}/.bundle/supercharge-ai/local/` | You, from your machine |
| `dev` | `production` | `/Workspace/supercharge-ai/dev/` | CI on `dev` branch |
| `stg` | `production` | `/Workspace/supercharge-ai/stg/` | CI on `stg` branch |
| `prod` | `production` | `/Workspace/supercharge-ai/prod/` | CI on `master` branch |

Every resource is tagged with `deployed_by`, `source` (`local` vs `cicd`), and `environment` so you can tell deployments apart in the Databricks UI / audit logs.

Deployment details and folder permissions: [`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md).

---

## GitFlow

```
feature/<name>  →  dev  →  stg  →  master
                   ↓        ↓        ↓
                   CI deploys to matching DAB target
```

- Start every change from a `feature/*` branch cut off `dev`.
- PRs default to `--base dev`. Never PR straight into `master`.
- `pr-preview.yml` runs `databricks bundle validate` and a dry-run against the PR's target branch.
- Full strategy: [`docs/GITFLOW.md`](./docs/GITFLOW.md).

---

## CI/CD Pipelines

`.github/workflows/`:

- **`deploy.yml`** — on push to `dev`/`stg`/`master`, deploys to the matching DAB target using OAuth service principals.
  - Path filters skip deploys on docs/test-only changes.
  - Concurrency groups prevent parallel deploys on the same branch.
  - Post-deploy summary writes commit SHA, deployer, and `bundle summary` output to the Actions run.
  - Jobs are **deployed but not triggered** on `stg`/`prod` (they wait for manual trigger or schedule).
- **`pr-preview.yml`** — on PRs, validates and dry-runs against the correct target; posts results as a PR comment.
- **`ci.yml`** — tests + linting on every PR.

Service principal and secret setup: [`.github/SECRETS.md`](./.github/SECRETS.md). CI/CD conventions: [`docs/CI-CD-STANDARDS.md`](./docs/CI-CD-STANDARDS.md).

---

## Building a Feature (High Level)

The detailed workflow (and rules for simple vs complex asks) lives in [`CLAUDE.md`](./CLAUDE.md). Short version:

1. `git checkout -b feature/<name>` off `dev`
2. Add a notebook: `notebooks/NN_snake_case.py` (Databricks notebook format — `# Databricks notebook source` at top, `# COMMAND ----------` between cells)
3. Add a job YAML: `resources/<name>_job.yml` — serverless env, installs the wheel via `dependencies: [../dist/*.whl]`, tags injected from DAB variables
4. `uv build && databricks bundle deploy --target local && databricks bundle run <job_name> --target local`
5. When green, raise a PR to `dev`

---

## Project Structure

```
supercharge-ai-dev/
├── .ai-dev-kit/            # curated Databricks skills — consult first for Databricks Qs
├── .claude/                # Claude Code commands + mirrored skills
├── .github/
│   ├── workflows/          # deploy.yml, pr-preview.yml, ci.yml
│   └── SECRETS.md          # service principal + OAuth setup
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SETUP.md
│   ├── DEPLOYMENT.md
│   ├── GITFLOW.md
│   ├── CI-CD-STANDARDS.md
│   └── DAB_FILE_SYNC.md
├── notebooks/              # Databricks notebooks (NN_snake_case.py)
├── resources/              # DAB job definitions (*_job.yml)
├── scripts/                # infra scripts (branch protection, etc.)
├── src/supercharge_ai/     # shared Python utilities (config, logger)
├── tests/                  # pytest unit tests
├── databricks.yml          # DAB bundle config (4 targets)
├── project_config.yml      # per-env config (catalog, schema, endpoints)
├── pyproject.toml          # pinned deps
└── version.txt             # package version
```

---

## Common Commands

```bash
# Development
uv run pytest                          # run unit tests
uv run ruff check . --fix              # lint + autofix
uv run ruff format .                   # format
uv run pre-commit run --all-files      # run all hooks
uv build                               # build wheel (artifacts.default)

# DAB (replace <target> and <job_name>)
databricks bundle validate --target <target>
databricks bundle deploy --target <target>
databricks bundle run <job_name> --target <target>
databricks bundle summary --target <target>
databricks bundle destroy --target <target>
```

---

## Documentation Index

| Doc | Purpose |
|---|---|
| [`CLAUDE.md`](./CLAUDE.md) | Workflow rules for AI assistants — ship-to-env, simple vs complex asks, naming |
| [`docs/SETUP.md`](./docs/SETUP.md) | Detailed local setup |
| [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) | System architecture |
| [`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md) | Local + CI/CD deployment guide |
| [`docs/GITFLOW.md`](./docs/GITFLOW.md) | Branching strategy + PR workflow |
| [`docs/CI-CD-STANDARDS.md`](./docs/CI-CD-STANDARDS.md) | GitHub Actions conventions |
| [`docs/DAB_FILE_SYNC.md`](./docs/DAB_FILE_SYNC.md) | How DAB syncs notebooks, wheels, and artifacts |
| [`.github/SECRETS.md`](./.github/SECRETS.md) | OAuth service principal setup per environment |
