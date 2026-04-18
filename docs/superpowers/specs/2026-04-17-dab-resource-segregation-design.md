# DAB Resource Segregation Strategy — Design Spec

**Date:** 2026-04-17
**Author:** Rahul Pandey
**Status:** Approved
**Scope:** Tag-based segregation of local vs CI/CD deployed resources in Databricks

---

## Problem Statement

When using Databricks Asset Bundles (DAB) to deploy resources to a shared workspace, there's currently no way to distinguish between:
- Resources deployed locally by developers (experimental, potentially incomplete)
- Resources deployed via CI/CD (vetted, from approved branches)

This creates governance and reliability issues:
1. **Reliability:** Cannot identify which resources are "official" vs experimental
2. **Safety:** No way to prevent accidental overwrites of prod resources from local machines
3. **Accountability:** Cannot track who deployed what or when
4. **Cleanup:** No mechanism to identify and remove stale local deployments

---

## Solution Overview

Implement a **tag-based segregation strategy** using DAB variables to automatically inject metadata tags on all deployed resources. Tags will include:
- `deployed_by` — username or service principal (for accountability)
- `source` — `local` or `cicd` (for segregation)
- `environment` — `dev`, `stg`, or `prod` (for environment tracking)

This approach is:
- ✅ **Declarative** — defined in `databricks.yml`, applies to all resources automatically
- ✅ **Low-friction** — minimal code changes, consistent across all resource types
- ✅ **Queryable** — tags enable filtering via Databricks API (for cleanup projects, dashboards)
- ✅ **Audit-friendly** — complete lineage of who deployed what, when

---

## Design Details

### Tag Structure

Three required tags on all resources:

| Tag | Local Value | CI/CD Value | Purpose |
|-----|-------------|-------------|---------|
| `deployed_by` | OS username (e.g., `rahul`) | `github-actions[bot]` | Accountability: who deployed |
| `source` | `local` | `cicd` | Segregation: where it came from |
| `environment` | `dev` (typically) | `dev` \| `stg` \| `prod` | Tracking: which environment |

### Tag Variables in databricks.yml

Add two new variables:

```yaml
variables:
  deployed_by:
    description: "User or service that deployed this bundle"
    default: "${env.USER}"  # Overridden in CI/CD

  deployment_source:
    description: "Source of deployment: local or cicd"
    default: "local"  # Overridden in CI/CD
```

**Local deployments:**
- `deployed_by` defaults to `${env.USER}` (automatically captures OS username)
- `deployment_source` defaults to `local`

**CI/CD deployments:**
- Workflow sets `DEPLOYED_BY=github-actions[bot]` before deploy
- Workflow sets `DEPLOYMENT_SOURCE=cicd` before deploy
- DAB picks up these env vars and uses them for variables

### Resource File Changes

Add tags section to all resources. Example for a job:

```yaml
resources:
  jobs:
    hello_world_job:
      name: Hello World Job
      tags:
        deployed_by: ${var.deployed_by}
        source: ${var.deployment_source}
        environment: ${bundle.target}
      tasks:
        # ... rest of job config
```

Tags use DAB variable interpolation: `${var.deployed_by}` resolves at deploy time.

### CI/CD Workflow Integration

In `.github/workflows/deploy.yml`, set environment variables before deployment:

```yaml
- name: Deploy to Databricks
  env:
    DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
    DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
    DEPLOYED_BY: "github-actions[bot]"
    DEPLOYMENT_SOURCE: "cicd"
  run: |
    databricks bundle deploy --target ${{ env.ENVIRONMENT }}
```

When DAB resolves `${var.deployed_by}`, it will use the `DEPLOYED_BY` env var if set, otherwise fall back to `${env.USER}`.

---

## Deployment Flows

### Local Deployment

```bash
# Developer runs from their machine:
$ databricks bundle deploy --target dev

# DAB resolves:
# - deployed_by = $(whoami)                  # e.g., "rahul"
# - deployment_source = "local"              # default value
# - environment = "dev"                      # from bundle.target

# Result in Databricks:
# Job tags: {deployed_by: "rahul", source: "local", environment: "dev"}
```

### CI/CD Deployment

```bash
# GitHub Actions workflow runs:
# 1. Sets env vars
export DEPLOYED_BY="github-actions[bot]"
export DEPLOYMENT_SOURCE="cicd"

# 2. Runs deploy
databricks bundle deploy --target prod

# DAB resolves:
# - deployed_by = "github-actions[bot]"      # from DEPLOYED_BY env var
# - deployment_source = "cicd"               # from DEPLOYMENT_SOURCE env var
# - environment = "prod"                     # from bundle.target

# Result in Databricks:
# Job tags: {deployed_by: "github-actions[bot]", source: "cicd", environment: "prod"}
```

---

## Implementation Steps

1. **Update `databricks.yml`**
   - Add `deployed_by` variable with `${env.USER}` default
   - Add `deployment_source` variable with `local` default

2. **Update resource files**
   - Add `tags:` section to all resources (jobs, pipelines, etc.)
   - Use `${var.deployed_by}`, `${var.deployment_source}`, `${bundle.target}` for tag values

3. **Update CI/CD workflow**
   - Set `DEPLOYED_BY` and `DEPLOYMENT_SOURCE` env vars before `databricks bundle deploy`

4. **Verification**
   - Local deploy to dev target, verify tags appear in Databricks UI
   - CI/CD deploy to dev/stg/prod, verify tags reflect `source=cicd`

---

## Query Examples (for Cleanup Project)

Once tags are deployed, a separate cleanup project can query resources:

```python
from databricks.sdk import WorkspaceClient

ws = WorkspaceClient()

# Find all locally deployed jobs
local_jobs = ws.jobs.list(filter='tags.source = "local"')

# Find resources deployed by a specific user
rahul_jobs = ws.jobs.list(filter='tags.deployed_by = "rahul"')

# Find stale local resources (older than 7 days)
cutoff_ms = (datetime.now() - timedelta(days=7)).timestamp() * 1000
stale_local = ws.jobs.list(
    filter=f'tags.source = "local" AND created_timestamp < {cutoff_ms}'
)
```

---

## Scope & Non-Scope

### In Scope
- Tag injection via DAB variables for all resources
- CI/CD workflow configuration to set deployer/source tags
- Documentation for developers on local deployment

### Out of Scope
- Cleanup/deletion of stale resources (separate project)
- Audit logging to UC tables (separate project)
- Hard enforcement/blocking (audit-only approach)

---

## Success Criteria

1. ✅ All deployed resources have three tags: `deployed_by`, `source`, `environment`
2. ✅ Local deployments tagged with `source=local` and actual username
3. ✅ CI/CD deployments tagged with `source=cicd` and `github-actions[bot]`
4. ✅ Cleanup project can query and identify stale local resources
5. ✅ No changes needed to individual resource definitions (tags injected at DAB level)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Developer forgets to set DEPLOYED_BY in CI/CD | Document in deployment runbook, enforce in PR template |
| Tags get out of sync if deployed manually (not via DAB) | Use DAB for all deployments, discourage manual edits |
| Tag values have typos or inconsistencies | Use constants/templates in DAB to avoid magic strings |

---

## References

- [Databricks Asset Bundles Documentation](https://docs.databricks.com/en/dev-tools/bundles/index.html)
- [Databricks Tags API](https://docs.databricks.com/api/workspace/jobs/get)
- Project: `supercharge-ai-dev`
- Related: Cleanup/audit job (separate project, will use these tags)
