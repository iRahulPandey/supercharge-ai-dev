# Supercharge AI Dev

Declarative AI/data workflows on Databricks, shipped to production via **Databricks Asset Bundles (DAB)** with a disciplined GitFlow-driven CI/CD pipeline. Every change — an ingestion, an enrichment, a Genie space — is a notebook + a YAML job, deployed the same way to the same path shape across every environment.

> **Working on this repo with Claude or another AI assistant?** Read [`CLAUDE.md`](./CLAUDE.md) first — it documents the workflow rules, naming conventions, and established feature patterns every change must follow.

---

## Why This Project Exists

Data / AI work on Databricks tends to drift into ad-hoc notebooks, hand-clicked jobs, and manual promotions between workspaces. That works for one person, but it breaks down fast: no rollback, no audit trail, no reproducibility, no way to tell "who deployed this" or "what catalog is this job writing to."

This project is a reference implementation of the opposite: **everything ships through DAB**, CI/CD is the only path into `dev`/`stg`/`prod`, and every resource is tagged with its origin (local vs cicd, which environment, who deployed). Local-vs-remote never gets confused.

## Table of Contents

1. [The CI/CD Philosophy](#the-cicd-philosophy)
2. [GitFlow → Environment Mapping](#gitflow--environment-mapping)
3. [DAB Architecture — Four Targets, One Pattern](#dab-architecture--four-targets-one-pattern)
4. [The CI/CD Pipeline](#the-cicd-pipeline)
5. [Best Practices We Follow](#best-practices-we-follow)
6. [Example: Product Insights Use Case](#example-product-insights-use-case)
7. [Deploying to Production — Step by Step](#deploying-to-production--step-by-step)
8. [Quick Start](#quick-start)
9. [Project Structure](#project-structure)
10. [Documentation Index](#documentation-index)

---

## The CI/CD Philosophy

Three ideas drive every design decision:

### 1. Declarative over imperative

Resources (jobs, tables, Genie spaces, eventually pipelines/endpoints) are defined as **YAML + small notebooks**, not as hand-crafted API calls from a developer's laptop. The bundle describes the intended state; DAB reconciles reality to match. Re-applying the same bundle is a no-op — no duplicates, no drift.

### 2. Config-driven, single source of truth

Everything that varies between environments (catalogs, warehouse IDs, endpoint names) lives in `project_config.yml`. Everything that varies between features (source table, destination table, Genie prompts) also lives in `project_config.yml`. One file; two top-level sections:

- **Env sections** (`local` / `dev` / `stg` / `prod`) — per-environment values.
- **Feature sections** (`datasets:`, `genie_spaces:`) — per-feature declarative metadata.

Notebooks receive `env` + `<feature_key>` as job parameters, load from the config file, and do the work. Same notebook runs locally (against `dev` catalog) and in prod (against `prd` catalog) with zero code changes.

### 3. Local-vs-remote must be visible

A deploy from your laptop and a deploy from CI must be telldapart in the Databricks UI. We inject three tags on every resource:

| Tag | Values | Why |
|---|---|---|
| `deployed_by` | username or service principal | Audit "who last deployed this" |
| `source` | `local` / `cicd` | Tell one-off personal deploys from promoted, reviewed code |
| `environment` | `local` / `dev` / `stg` / `prod` | Catalog-independent identity |

Combined with per-target deployment paths, there's no ambiguity: a job tagged `source=local, deployed_by=rpandey1901@gmail.com` is someone's experiment; a job tagged `source=cicd, deployed_by=ci-bot-prod` is the audited production artifact.

---

## GitFlow → Environment Mapping

```
                                    ┌─── CI deploys to ───┐
                                    │                     │
feature/<name>   ──▶  dev branch   ═╪══▶ /Workspace/supercharge-ai/dev/
                       │            │
                       └───▶ stg    ═╪══▶ /Workspace/supercharge-ai/stg/
                             │      │
                             └───▶ master
                                    ═══▶ /Workspace/supercharge-ai/prod/  (catalog: prd)
```

**Rules:**

- All work happens on `feature/<name>` branches cut from `dev`.
- PRs default to `--base dev`. Never PR directly into `master`.
- Each branch merge triggers CI to deploy to the matching DAB target.
- Promoting a change = merging dev → stg → master. No direct commits anywhere except feature branches.

Branch protection is set up via [`scripts/setup-branch-protection.sh`](./scripts/setup-branch-protection.sh). Full strategy lives in [`docs/GITFLOW.md`](./docs/GITFLOW.md).

---

## DAB Architecture — Four Targets, One Pattern

All four targets share the **same bundle definition, same resources, same notebooks**. They differ only in *where* they deploy and *what catalog* their jobs read/write.

| Target | DAB mode | Workspace path | Catalog | Who triggers it |
|---|---|---|---|---|
| `local` (default) | `development` | `/Users/{you}/.bundle/supercharge-ai/local/` | `dev` | You, from your laptop |
| `dev` | `production` | `/Workspace/supercharge-ai/dev/` | `dev` | CI on push to `dev` |
| `stg` | `production` | `/Workspace/supercharge-ai/stg/` | `stg` | CI on push to `stg` |
| `prod` | `production` | `/Workspace/supercharge-ai/prod/` | `prd` | CI on push to `master` |

**Why `development` mode for `local`:** deploys auto-scope to your personal folder, schedules auto-pause, and job names get `[dev yourname]` prefixes — so your test runs can't corrupt a shared environment.

**Why `production` mode for `dev`/`stg`/`prod`:** requires explicit non-user `root_path`, enforces auditable shared paths, runs schedules as configured. These are the managed, shared-by-the-team environments.

Full workspace permissions, service principal setup, and secret management: [`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md) and [`.github/SECRETS.md`](./.github/SECRETS.md).

---

## The CI/CD Pipeline

Three workflows under `.github/workflows/`:

### `deploy.yml` — per-environment deployment

```yaml
on:
  push:
    branches: [dev, stg, master]
    paths:                         # Skip deploys on docs/test-only changes
      - databricks.yml
      - resources/**
      - notebooks/**
      - src/**
      - pyproject.toml

concurrency:                       # Prevent racing deploys on the same branch
  group: deploy-${{ github.ref }}
  cancel-in-progress: false
```

Each of `deploy-dev` / `deploy-stg` / `deploy-prod` runs this sequence against its own OAuth service principal:

1. `uv build` — produces `dist/supercharge_ai-<version>-py3-none-any.whl`
2. `databricks bundle validate --target <env>` — YAML parse + resource check
3. `databricks bundle deploy --target <env>` — idempotent upload: wheel + notebooks + config + job definitions
4. Deployment summary written to `$GITHUB_STEP_SUMMARY` (commit SHA, deployer, target path, `bundle summary` output for audit)
5. `prod` only: a `databricks bundle deploy --dry-run` is run **before** the real deploy so the plan shows up in the Actions run before any change lands

**Key choice: jobs are deployed but NOT triggered on `stg`/`prod`.** CI's job ends at "deploy was successful." Running the actual data job is either manual (from the Databricks UI) or scheduled. This keeps CI fast, avoids wasting compute, and prevents unintended data movement.

### `pr-preview.yml` — validation before merge

On PRs targeting `dev`/`stg`/`master`, `pr-preview.yml`:

1. Figures out the target matching the PR's base branch (`dev` → `dev`, `master` → `prod`)
2. Runs `databricks bundle validate --target <target>`
3. Runs `databricks bundle deploy --target <target> --dry-run` to show the plan
4. Posts the result as a PR comment (requires `pull-requests: write` permission, hence the explicit `permissions:` block in the workflow)

Reviewers see "what would change" before approving.

### `ci.yml` — tests + linting

Standard pytest + ruff on every PR, decoupled from DAB. Protects against regressions in `src/supercharge_ai/`.

---

## Best Practices We Follow

### Idempotency everywhere

- **DAB itself is idempotent** — resources are tracked by their **logical key** in the bundle (e.g., `ingest_media_customer_reviews_job`), not by display name. `job_id` stays constant across redeploys. No duplicates ever.
- **Notebooks use `CREATE OR REPLACE TABLE … AS SELECT …`** — safe to re-run, no surprise side-effects.
- **Genie Space deployment is idempotent by title match** — list spaces, find the one whose title matches `"<title> (<env>)"`, and `updatespace` if found, otherwise create. Re-running never creates duplicates.

### Secrets never leave GitHub environments

- OAuth service principals (`ci-bot-dev` / `ci-bot-stg` / `ci-bot-prod`), **not PAT tokens**. Scoped per environment, rotatable without code change.
- Each environment's secrets are attached to a GitHub Environment (`dev`/`stg`/`prod`). Workflow jobs declare `environment:` to access them — protection rules can gate with required reviewers for prod.
- No secret ever appears in config files or logs. Workflow injection attacks are mitigated by passing `github.*` context through `env:` blocks, never inlined into `run:` strings.

### Safe-by-default changes

- **Path filters** on `deploy.yml` — README-only commits don't trigger 15-minute deploys.
- **Concurrency groups** (`deploy-${{ github.ref }}`, `cancel-in-progress: false`) — two merges in quick succession queue rather than race, so the second deploy doesn't trample the first's in-flight sync.
- **Prod dry-run** — the plan is printed to the Actions step summary before the real apply.
- **Env-scoped workspace folders** — service principals have `CAN_MANAGE` only on their own `/Workspace/supercharge-ai/<env>/` folder. A compromised dev SP can't touch prod paths.

### Testing discipline

- TDD for anything in `src/supercharge_ai/` (config loaders, Genie helpers). 30 unit tests currently, all pass in <100 ms.
- Notebooks aren't unit-tested — they're validated by running the job against the `local` target end-to-end before the commit.
- `uv run pre-commit run --all-files` runs ruff check/format + mypy + YAML validation + secret detection before every commit.

### When something breaks, research before iterating

Databricks has a lot of moving parts and sharp edges (DAB path resolution, serverless env deps, Genie API's silent proto constraints). The `.claude/skills/databricks-*` skills and `.ai-dev-kit/` are curated references — **consult them before guessing**. The [`CLAUDE.md`](./CLAUDE.md) documents every pitfall this project has hit so far so they don't get re-discovered the hard way.

---

## Example: Product Insights Use Case

This is the end-to-end walkthrough of what's currently in the repo. It's the canonical template for all future features.

**User journey:** A business user wants to explore customer feedback about bakery franchises in plain English — "which franchise has the most positive reviews?", "what topics do detractors complain about?". They open a **Genie Space**, ask questions, get SQL-backed answers. Everything behind the Genie Space — the data, the enrichment, the space itself — was built, tested, and promoted through the pipeline.

### Three stages, three jobs

```
samples.bakehouse.media_customer_reviews        ← Databricks sample data
                │
                │   Stage 1: Ingestion (CTAS)
                │   notebooks/01_ingest_media_customer_reviews.py
                │   resources/ingest_media_customer_reviews_job.yml
                ▼
<env>.bakehouse.media_customer_reviews          ← our copy, per env
                │
                │   Stage 2: AI Enrichment (ai_analyze_sentiment,
                │            ai_classify, ai_extract)
                │   notebooks/02_extract_media_customer_review_insights.py
                │   resources/extract_media_customer_review_insights_job.yml
                ▼
<env>.bakehouse.media_customer_review_insights  ← sentiment + nps + topics per review
                │
                │   Stage 3: Genie Space deployment
                │   notebooks/03_deploy_media_customer_insights_genie_space.py
                │   resources/deploy_media_customer_insights_genie_space_job.yml
                ▼
"Media Customer Review Insights (<env>)"        ← Genie Space in the workspace UI
```

### Stage 1 — Ingestion

A single notebook + a single job YAML, plus a config entry:

**`project_config.yml`** — `datasets.media_customer_reviews` entry:
```yaml
datasets:
  media_customer_reviews:
    input:
      catalog: samples          # explicit — sample data is in Databricks' `samples` catalog
      schema: bakehouse
      table: media_customer_reviews
    output:
      # catalog omitted → inherits env.catalog (dev / stg / prd) at runtime
      schema: bakehouse
      table: media_customer_reviews
```

Note the **symmetric shape**: both `input` and `output` use `{catalog, schema, table}`. `catalog` is optional on `output` — when omitted it falls back to the current env's catalog, so one entry serves all three environments.

**`notebooks/01_ingest_media_customer_reviews.py`** — reads widgets (`env`, `dataset`, `config_path`), uses `supercharge_ai.config.load_dataset()` to resolve FQNs, runs `CREATE SCHEMA IF NOT EXISTS` + `CREATE OR REPLACE TABLE … AS SELECT …`. Logs row count, exits with a structured result string.

**`resources/ingest_media_customer_reviews_job.yml`** — serverless env v4, installs the project wheel (`dependencies: [../dist/*.whl]` — DAB uploads it and rewrites the path), passes `env = ${bundle.target}` as a notebook parameter, tags the job with `deployed_by` / `source` / `environment`.

### Stage 2 — AI enrichment

Same pattern, different notebook. The interesting part is the SQL: no model endpoint setup, no API keys — task-specific Databricks AI functions:

```sql
CREATE OR REPLACE TABLE {output_fqn} AS
SELECT
    new_id,
    franchiseID                                             AS franchise_id,
    review_date,
    review,
    ai_analyze_sentiment(review)                            AS sentiment,
    ai_classify(review, ARRAY('promoter', 'passive', 'detractor'))  AS nps_category,
    ai_extract(review, ARRAY('taste', 'quality', 'service',
                              'price', 'ambience', 'variety'))      AS topics,
    current_timestamp()                                     AS processed_at
FROM {input_fqn}
```

Why task-specific functions (`ai_analyze_sentiment`, `ai_classify`, `ai_extract`) instead of a generic `ai_query(model, prompt)`: they're pre-tuned for the task, cheaper, and produce consistent outputs. The [`databricks-ai-functions`](./.claude/skills/databricks-ai-functions/SKILL.md) skill has the full selection rubric.

**The config entry again follows the symmetric `input` / `output` shape** — input catalog inherits from env (we're reading our own ingested copy):

```yaml
datasets:
  media_customer_review_insights:
    input:
      schema: bakehouse
      table: media_customer_reviews
    output:
      schema: bakehouse
      table: media_customer_review_insights
```

### Stage 3 — Genie Space deployment

The Genie Space is a natural-language interface to the enriched table. Config lives in a new top-level section:

```yaml
genie_spaces:
  media_customer_insights:
    title: "Media Customer Review Insights"
    description: |
      Natural-language exploration of media customer reviews enriched with
      sentiment, NPS category, and topic extraction ...
    instructions:
      - "`sentiment` is one of: positive, negative, neutral, mixed."
      - "`nps_category` is one of: promoter, passive, detractor. ..."
      - "`topics` is a struct with fields taste, quality, service, price, ambience, variety. ..."
      - ...
    sample_questions:
      - "Which franchise has the most positive reviews?"
      - "Show me detractors grouped by franchise ..."
      - ...
    tables:
      - schema: bakehouse
        table: media_customer_review_insights
        description: "Customer reviews enriched with sentiment, NPS category, and topics."
```

The deploy notebook:
1. Loads config + env's catalog + warehouse
2. Suffixes the title with `(<env>)` — so `dev` / `stg` / `prod` spaces coexist without collision
3. Calls `GET /api/2.0/genie/spaces`, looks for a space whose title matches (idempotent upsert by title)
4. `POST /api/2.0/genie/spaces/{id}/updatespace` if found, `POST /api/2.0/genie/spaces` if not
5. Logs the space URL for the user to click

Three non-obvious Genie API quirks we learned and documented:

- `config` / `data_sources` / `instructions` are **top-level siblings**, not nested inside `config`. Nesting → API rejection.
- `instructions.text_instructions` is **`max_items=1`**. All user instruction strings go inside that single entry's `content` array, not as separate entries.
- The Databricks SDK doesn't expose `create_space` — use `WorkspaceClient.api_client.do("POST", "/api/2.0/genie/spaces", body=...)` directly.

These are captured in `src/supercharge_ai/genie.py` (with regression tests) so the next Genie feature doesn't re-discover them.

---

## Deploying to Production — Step by Step

Here's what happens when a change in this repo reaches production. Say we just finished the insights feature on `feature/product-insights`.

### 1. Local verification (before any PR)

```bash
uv build
databricks bundle deploy --target local
databricks bundle run ingest_media_customer_reviews_job --target local
databricks bundle run extract_media_customer_review_insights_job --target local
databricks bundle run deploy_media_customer_insights_genie_space_job --target local
```

Everything deploys to `/Users/{you}/.bundle/supercharge-ai/local/` and writes to the `dev` catalog under your service principal. Tagged `source=local`.

Verify the output:
```sql
SELECT sentiment, count(*) FROM dev.bakehouse.media_customer_review_insights GROUP BY sentiment;
```

Open the `"Media Customer Review Insights (local)"` Genie space in the Databricks UI and ask a question.

### 2. Raise the PR to `dev`

```bash
git push -u origin feature/product-insights
gh pr create --base dev --title "feat(product-insights): …"
```

- `pr-preview.yml` runs automatically: validates the bundle, runs a dry-run deploy, posts the plan as a PR comment.
- Team reviews the code + the dry-run plan.
- Tests and linting gates (`ci.yml`) must pass.

### 3. Merge to `dev` → auto-deploy to dev env

```bash
gh pr merge --squash
```

- `deploy.yml` fires on push to `dev`.
- CI authenticates as `ci-bot-dev`, deploys to `/Workspace/supercharge-ai/dev/`, and tags every resource with `source=cicd deployed_by=ci-bot-dev environment=dev`.
- Deployment summary is posted to the Actions run (commit SHA, target path, resource URLs).
- Jobs are deployed but **not triggered** — a dev team member runs `ingest → extract → deploy_genie_space` from the Databricks UI (or on schedule) to smoke-test against the shared dev catalog.

### 4. Promote to `stg`

```bash
git checkout stg && git merge dev && git push
```

- Same deploy flow, `ci-bot-stg`, writes to `stg` catalog via `/Workspace/supercharge-ai/stg/`.
- The `"Media Customer Review Insights (stg)"` Genie Space is now available for business stakeholders to try against staging data.

### 5. Promote to `prod`

```bash
git checkout master && git merge stg && git push
```

- Before the real deploy, the `prod` job runs `databricks bundle deploy --target prod --dry-run` — the plan is in the Actions step summary.
- Then the real deploy runs as `ci-bot-prod` → `/Workspace/supercharge-ai/prod/` → `prd` catalog.
- Tags: `source=cicd deployed_by=ci-bot-prod environment=prod`.
- Production Genie Space: `"Media Customer Review Insights (prod)"`.

No step in this process involves a developer's laptop touching prod. The OAuth service principals are the only things that can; their access is scoped to their folder; every action is in Git + Actions logs.

---

## Quick Start

### Prerequisites

- Python **3.12** (matches Databricks Serverless Environment 4)
- `uv` — [install guide](https://docs.astral.sh/uv/getting-started/installation/)
- Databricks CLI v0.218+ — `curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh`
- An OAuth profile in `~/.databrickscfg` pointing at your workspace

### Setup

```bash
git clone <repo-url>
cd supercharge-ai-dev
uv sync                                         # install deps
uv run pre-commit install                       # enable git hooks
uv run pytest                                   # verify setup (should pass)
databricks bundle validate --target local       # verify DAB auth + config
```

### Build + deploy locally

```bash
uv build                                          # build the project wheel
databricks bundle deploy --target local           # upload bundle + wheel
databricks bundle summary --target local          # list deployed jobs with URLs
databricks bundle run ingest_media_customer_reviews_job --target local
databricks bundle destroy --target local          # clean up when you're done
```

### Common commands

```bash
# Development
uv run pytest                          # run unit tests
uv run ruff check . --fix              # lint + autofix
uv run ruff format .                   # format
uv run pre-commit run --all-files      # run all hooks

# DAB
databricks bundle validate --target <target>
databricks bundle deploy --target <target>
databricks bundle run <job_name> --target <target>
databricks bundle summary --target <target>
databricks bundle destroy --target <target>
```

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
├── notebooks/
│   ├── 01_ingest_media_customer_reviews.py
│   ├── 02_extract_media_customer_review_insights.py
│   └── 03_deploy_media_customer_insights_genie_space.py
├── resources/
│   ├── ingest_media_customer_reviews_job.yml
│   ├── extract_media_customer_review_insights_job.yml
│   └── deploy_media_customer_insights_genie_space_job.yml
├── scripts/                # infra scripts (branch protection, etc.)
├── src/supercharge_ai/
│   ├── config.py           # ProjectConfig, TableRef, DatasetConfig, GenieSpaceConfig, loaders
│   ├── genie.py            # build_serialized_space, upsert_space, warehouse resolution
│   ├── logger.py           # loguru setup
│   └── utils.py
├── tests/                  # pytest — 30 tests for config + genie helpers
├── databricks.yml          # DAB bundle config (4 targets: local/dev/stg/prod)
├── project_config.yml      # per-env settings + datasets + genie_spaces
├── pyproject.toml          # pinned deps
└── version.txt             # package version
```

---

## Documentation Index

| Doc | Purpose |
|---|---|
| [`CLAUDE.md`](./CLAUDE.md) | Workflow rules for AI assistants — ship-to-env, simple vs complex asks, naming, debugging pitfalls |
| [`docs/SETUP.md`](./docs/SETUP.md) | Detailed local setup |
| [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) | System architecture |
| [`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md) | Local + CI/CD deployment guide with tag verification |
| [`docs/GITFLOW.md`](./docs/GITFLOW.md) | Branching strategy + PR workflow |
| [`docs/CI-CD-STANDARDS.md`](./docs/CI-CD-STANDARDS.md) | GitHub Actions conventions |
| [`docs/DAB_FILE_SYNC.md`](./docs/DAB_FILE_SYNC.md) | How DAB syncs notebooks, wheels, and artifacts |
| [`.github/SECRETS.md`](./.github/SECRETS.md) | OAuth service principal setup per environment |
| [`.claude/skills/databricks-*/`](./.claude/skills/) | Curated Databricks knowledge (AI functions, Genie, SDK, bundles, etc.) |
