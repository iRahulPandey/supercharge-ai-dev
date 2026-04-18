# GitFlow Strategy — Supercharge AI Dev

This document describes the Git branching and deployment workflow for the Supercharge AI Dev project.

## Branch Structure

```
master (production)
  ↑
  |── stg (staging)
        ↑
        |── dev (development)
              ↑
              |── feature/* (feature branches)
```

## Branches

### `master` — Production
- **Stability:** Highest (all commits are tested and reviewed)
- **Deployment Target:** PROD Databricks workspace
- **Protection:** Requires PR review, all CI checks must pass
- **Source:** Merges from `dev` or `stg`
- **Note:** This is the primary branch (not `main`)

### `stg` — Staging
- **Stability:** High (tested, reflects production-like environment)
- **Deployment Target:** STG Databricks workspace
- **Protection:** Requires PR review, all CI checks must pass
- **Source:** Merges from `dev`
- **Purpose:** Final validation before production deployment

### `dev` — Development
- **Stability:** Medium (all commits tested, may contain experimental features)
- **Deployment Target:** DEV Databricks workspace
- **Protection:** Requires PR review, all CI checks must pass
- **Source:** Merges from feature branches
- **Purpose:** Main integration branch for active development

### `feature/*` — Feature Branches
- **Naming:** `feature/short-description` or `feat/short-description`
- **Source:** Created from `dev`
- **Destination:** PR back to `dev`
- **Lifetime:** Short-lived (1-2 weeks typical)
- **Examples:**
  - `feature/add-vector-search-integration`
  - `feat/improve-config-validation`
  - `fix/resolve-logging-issue`

## Workflow

### 1. Start a Feature

```bash
# Create feature branch from dev
git checkout dev
git pull origin dev
git checkout -b feat/your-feature-name
```

### 2. Develop Locally

- Write tests first (TDD)
- Implement feature
- Run linting and tests:
  ```bash
  uv run pytest
  uv run ruff check . --fix
  uv run pre-commit run --all-files
  ```

### 3. Push and Create PR

```bash
git push origin feat/your-feature-name
# Then create PR on GitHub targeting 'dev' branch
```

**PR must include:**
- Descriptive title and description
- Link to related issues (if any)
- Test coverage summary
- Any special deployment notes

### 4. Merge to Dev

Once approved and all checks pass:
```bash
# Can squash or regular merge
git checkout dev
git merge feat/your-feature-name
git push origin dev
```

**Automatically triggers:**
- `test.yml` workflow (lint, test, security)
- `deploy-dev.yml` on merge completion (deploys to DEV workspace)

### 5. Promote to Staging

When ready to test in staging environment:

```bash
# Create PR from dev to stg
git checkout stg
git pull origin stg
git merge origin/dev
git push origin stg
```

Or use GitHub UI to create PR from `dev` → `stg`

**Automatically triggers:**
- `test.yml` workflow
- `deploy-stg.yml` on merge completion (deploys to STG workspace)

### 6. Promote to Production

When staging validation is complete and ready for production:

```bash
# Create PR from dev to master
git checkout master
git pull origin master
git merge origin/dev
git push origin master
```

Or use GitHub UI to create PR from `dev` → `master`

**Automatically triggers:**
- `test.yml` workflow
- `deploy-prod.yml` on merge completion (deploys to PROD workspace)

## CI/CD Pipeline

### Test Workflow (`test.yml`)
- **Trigger:** On all branches for push and PR
- **Jobs:**
  - Lint: Ruff linting and formatting
  - Test: Pytest with coverage
  - Security: Pip-audit vulnerability scan
- **Duration:** ~5-10 minutes
- **Must Pass:** Before allowing merge

### Deploy Workflow (`deploy-dev.yml`, `deploy-stg.yml`, `deploy-prod.yml`)
- **Trigger:** On push to respective branch
- **Conditions:**
  - Only runs if tests passed (via branch protection)
  - Each job conditional on correct branch (`if: github.ref == 'refs/heads/dev'`)
- **Steps:**
  1. Checkout code
  2. Setup Python 3.12 and uv
  3. Install Databricks CLI
  4. Build wheel package
  5. Authenticate with Databricks (environment-specific)
  6. Deploy bundle: `databricks bundle deploy --target {dev|stg|prod}`
  7. Validate deployment: Run `hello_world_job` to ensure success
- **Duration:** ~10-15 minutes per environment
- **Secrets Required:**
  - `DATABRICKS_DEV_HOST` / `DATABRICKS_DEV_TOKEN`
  - `DATABRICKS_STG_HOST` / `DATABRICKS_STG_TOKEN`
  - `DATABRICKS_PROD_HOST` / `DATABRICKS_PROD_TOKEN`

## Commit Message Convention

All commits must follow Conventional Commits:

```
<type>(<scope>): <description>

Types:
  feat     — New feature
  fix      — Bug fix
  refactor — Code restructuring (no behavior change)
  docs     — Documentation only
  test     — Test files or testing utilities
  chore    — Tooling, config, dependencies
  perf     — Performance improvement
  ci       — CI/CD changes
```

**Examples:**
```bash
git commit -m "feat(config): add support for dynamic endpoint resolution"
git commit -m "fix(logger): handle async operations correctly"
git commit -m "test(vector_search): add integration tests"
git commit -m "docs: update deployment documentation"
```

## Environment Configuration

Each environment (`dev`, `stg`, `prod`) has:

1. **Databricks Workspace** — Separate workspace instance
2. **Catalog** — `dev`, `stg`, or `prod` (in project_config.yml)
3. **Schema** — `supercharge_ai` (consistent across all)
4. **DAB Target** — Configured in databricks.yml
5. **Secrets** — Environment-specific credentials in GitHub

### Example: Deploying a Job

The same job definition in `resources/` is deployed to all three environments:

```yaml
# resources/hello_world_job.yml (same file for all environments)
resources:
  jobs:
    hello_world_job:
      name: hello_world_{{.bundle.target}}
      tasks:
        - task_key: main
          notebook_task:
            notebook_path: {{.workspace.file_path}}/notebooks/1_hello_world
```

When deployed:
- `dev` target → job name: `hello_world_dev` in `dev` workspace, `dev` catalog
- `stg` target → job name: `hello_world_stg` in `stg` workspace, `stg` catalog
- `prod` target → job name: `hello_world_prod` in `prod` workspace, `prod` catalog

## Troubleshooting

### Feature branch won't merge to dev
- **Cause:** CI tests failing or merge conflicts
- **Solution:**
  1. Check GitHub Actions logs
  2. Fix failing tests locally
  3. Resolve any merge conflicts
  4. Re-push to feature branch

### Staging deployment failed
- **Cause:** Bundle validation or Databricks API error
- **Solution:**
  1. Check workflow logs: `.github/workflows/deploy-stg.yml`
  2. Run `databricks bundle validate -t stg` locally
  3. Verify `DATABRICKS_STG_HOST` and `DATABRICKS_STG_TOKEN` are set
  4. Check Databricks workspace for resource conflicts

### Production deployment blocked
- **Cause:** Branch protection rules, missing approvals, or CI failure
- **Solution:**
  1. Ensure all required approvals given
  2. All CI checks passing
  3. No outstanding review requests
  4. Contact team lead if additional approval needed

## Best Practices

1. **Keep feature branches short-lived** — Merge within 1-2 weeks
2. **Rebase before merge** — Keeps history clean:
   ```bash
   git fetch origin
   git rebase origin/dev
   git push origin feat/your-feature --force-with-lease
   ```
3. **Squash commits for feature** — Use GitHub's "Squash and merge" option
4. **Sync dev regularly** — Prevents large merge conflicts:
   ```bash
   git checkout feat/your-feature
   git merge origin/dev
   ```
5. **Write clear PR descriptions** — Helps reviewers understand context
6. **Test in staging first** — Always validate in STG before PROD
7. **Monitor deployments** — Check Databricks job runs after deployment
8. **Document deployment notes** — Add any manual steps in PR description

## Example Workflow Timeline

```
Monday:
  ├─ 10:00 — Create feat/new-feature from dev
  ├─ 14:00 — Push code and create PR
  └─ 15:30 — PR approved and merged to dev
             → test.yml triggers (5 min)
             → deploy-dev.yml triggers (10 min)
             → Feature now in DEV workspace

Tuesday:
  ├─ 09:00 — Validate feature in dev workspace
  ├─ 14:00 — Create PR: dev → stg
  └─ 15:00 — PR approved and merged to stg
             → test.yml triggers (5 min)
             → deploy-stg.yml triggers (10 min)
             → Feature now in STG workspace

Wednesday:
  ├─ 09:00 — QA validates in staging
  ├─ 13:00 — Create PR: dev → master (for release)
  └─ 14:00 — PR approved and merged to master
             → test.yml triggers (5 min)
             → deploy-prod.yml triggers (10 min)
             → Feature now in PROD workspace ✓
```

## References

- [Databricks Asset Bundles Docs](https://docs.databricks.com/en/dev-tools/bundles/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow Documentation](https://guides.github.com/introduction/flow/)
