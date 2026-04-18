# DAB Resource Segregation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement tag-based segregation of Databricks resources deployed locally vs via CI/CD, enabling governance tracking and cleanup automation.

**Architecture:** Add DAB variables to `databricks.yml` that inject three metadata tags (`deployed_by`, `source`, `environment`) on all resources. Local deployments capture the OS username; CI/CD deployments are tagged via environment variables set in the GitHub Actions workflow.

**Tech Stack:** Databricks Asset Bundles, DAB variables, GitHub Actions

---

## Task 1: Update databricks.yml with Tag Variables

**Files:**
- Modify: `databricks.yml`

- [ ] **Step 1: Read current databricks.yml**

Run: `cat databricks.yml` to review current structure

Expected output: YAML with existing `variables`, `targets`, etc.

- [ ] **Step 2: Add deployed_by variable**

After the `git_sha` variable in `variables:` section, add:

```yaml
  deployed_by:
    description: "User or service that deployed this bundle"
    default: "${env.USER}"
```

This uses `${env.USER}` for local deployments (OS username) and will be overridden by `DEPLOYED_BY` env var in CI/CD.

- [ ] **Step 3: Add deployment_source variable**

After the `deployed_by` variable, add:

```yaml
  deployment_source:
    description: "Source of deployment: local or cicd"
    default: "local"
```

This defaults to `local` for local deployments and will be overridden by `DEPLOYMENT_SOURCE` env var in CI/CD.

- [ ] **Step 4: Verify structure**

Run: `databricks bundle validate`

Expected: No errors, validates successfully

- [ ] **Step 5: Commit**

```bash
git add databricks.yml
git commit -m "feat: add deployed_by and deployment_source variables to DAB"
```

---

## Task 2: Update hello_world_job.yml with Tags

**Files:**
- Modify: `resources/hello_world_job.yml`

- [ ] **Step 1: Read current job file**

Run: `cat resources/hello_world_job.yml`

Expected: Job definition with `name`, `description`, `tasks`, etc.

- [ ] **Step 2: Add tags section after name**

After the `description:` field and before `tasks:`, insert:

```yaml
      tags:
        deployed_by: ${var.deployed_by}
        source: ${var.deployment_source}
        environment: ${bundle.target}
```

The complete structure should be:

```yaml
resources:
  jobs:
    hello_world_job:
      name: Hello World Job
      description: Demonstrates basic notebook execution via DAB
      tags:
        deployed_by: ${var.deployed_by}
        source: ${var.deployment_source}
        environment: ${bundle.target}
      tasks:
        # ... rest of tasks
```

- [ ] **Step 3: Verify DAB validation**

Run: `databricks bundle validate`

Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add resources/hello_world_job.yml
git commit -m "feat: add segregation tags to hello_world_job"
```

---

## Task 3: Update config_demo_job.yml with Tags

**Files:**
- Modify: `resources/config_demo_job.yml`

- [ ] **Step 1: Read current job file**

Run: `cat resources/config_demo_job.yml`

Expected: Job definition

- [ ] **Step 2: Add tags section after name**

After the `description:` field (or name if no description), insert:

```yaml
      tags:
        deployed_by: ${var.deployed_by}
        source: ${var.deployment_source}
        environment: ${bundle.target}
```

- [ ] **Step 3: Verify structure**

Run: `databricks bundle validate`

Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add resources/config_demo_job.yml
git commit -m "feat: add segregation tags to config_demo_job"
```

---

## Task 4: Update GitHub Actions Deploy Workflow

**Files:**
- Modify: `.github/workflows/deploy.yml`

- [ ] **Step 1: Read current deploy workflow**

Run: `cat .github/workflows/deploy.yml`

Expected: Workflow with job steps, including `databricks bundle deploy` command

- [ ] **Step 2: Add env vars to deploy step**

Find the step that runs `databricks bundle deploy` (typically named "Deploy to Databricks" or similar).

Add `env:` section before `run:`:

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

Note: Keep existing `DATABRICKS_HOST` and `DATABRICKS_TOKEN` if present; add the two new vars after them.

- [ ] **Step 3: Verify workflow syntax**

Run: `grep -A 10 'DEPLOYED_BY' .github/workflows/deploy.yml`

Expected: Shows `DEPLOYED_BY: "github-actions[bot]"` and `DEPLOYMENT_SOURCE: "cicd"`

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: set DEPLOYED_BY and DEPLOYMENT_SOURCE env vars for CI/CD tagging"
```

---

## Task 5: Create Deployment Documentation

**Files:**
- Create: `docs/DEPLOYMENT.md` (if doesn't exist) or Modify: add section to existing deployment docs

- [ ] **Step 1: Create DEPLOYMENT.md**

Create `docs/DEPLOYMENT.md` with content:

```markdown
# Deployment Guide

## Tag-Based Resource Segregation

All Databricks resources (jobs, pipelines, notebooks) deployed via DAB are automatically tagged with metadata for governance and auditing.

### Tags

Every deployed resource receives three tags:

| Tag | Local Value | CI/CD Value | Purpose |
|-----|-------------|-------------|---------|
| `deployed_by` | Your OS username | `github-actions[bot]` | Who deployed the resource |
| `source` | `local` | `cicd` | Deployment source (local machine or CI/CD) |
| `environment` | `dev` (or target) | `dev`, `stg`, or `prod` | Target environment |

### Local Deployment

To deploy locally to the dev environment:

```bash
databricks bundle deploy --target dev
```

Tags will be set to:
- `deployed_by`: Your username (e.g., `rahul`)
- `source`: `local`
- `environment`: `dev`

### CI/CD Deployment

CI/CD deployments (via GitHub Actions) are tagged with:
- `deployed_by`: `github-actions[bot]`
- `source`: `cicd`
- `environment`: Target environment from branch (dev, stg, or prod)

### Viewing Tags

In the Databricks UI, navigate to a job and scroll to the "Tags" section to see the metadata.

To query tags programmatically:

```python
from databricks.sdk import WorkspaceClient

ws = WorkspaceClient()

# Find all locally deployed jobs
local_jobs = ws.jobs.list(filter='tags.source = "local"')

# Find resources deployed by a specific user
user_jobs = ws.jobs.list(filter='tags.deployed_by = "rahul"')

# Find stale local resources (older than 7 days)
cutoff_ms = (datetime.now() - timedelta(days=7)).timestamp() * 1000
stale = ws.jobs.list(filter=f'tags.source = "local" AND created_timestamp < {cutoff_ms}')
```

### Governance

Local deployments are tagged but **not blocked**. This allows for experimentation while maintaining a clear audit trail. A separate cleanup job (not in this project) handles deletion of stale local resources.
```

- [ ] **Step 2: Commit**

```bash
git add docs/DEPLOYMENT.md
git commit -m "docs: add deployment guide with tag segregation information"
```

---

## Task 6: Local Verification Test

**Files:**
- Test: Local deployment (manual verification)

- [ ] **Step 1: Deploy hello_world_job locally**

Run:

```bash
databricks bundle deploy --target dev
```

Expected output: Deployment succeeds, shows job was created/updated

- [ ] **Step 2: Verify tags in Databricks UI**

1. Go to Databricks workspace
2. Navigate to Compute → Jobs
3. Click on "Hello World Job"
4. Scroll to "Tags" section
5. Verify tags are present:
   - `deployed_by: <your_username>`
   - `source: local`
   - `environment: dev`

- [ ] **Step 3: Query tags via CLI**

Run:

```bash
databricks jobs list --output json | jq '.[] | select(.job_id == <job_id>) | .tags'
```

(Replace `<job_id>` with the actual job ID from previous step)

Expected output: JSON object with three tags

- [ ] **Step 4: Document results**

Screenshot or note the job ID and tag values for reference

---

## Task 7: CI/CD Verification (Smoke Test)

**Files:**
- Test: CI/CD workflow (automated)

- [ ] **Step 1: Push feature branch to GitHub**

Run:

```bash
git push origin feature/local-vs-remote-segregation
```

- [ ] **Step 2: Create a Pull Request**

Create PR against `dev` branch (assuming GitFlow).

Expected: GitHub Actions workflow triggers automatically

- [ ] **Step 3: Monitor workflow execution**

Go to GitHub repo → Actions → find the "Deploy" workflow for your PR

Expected: Workflow runs without errors

- [ ] **Step 4: Verify CI/CD deployment**

Once workflow completes and merges to dev (or is staged), check Databricks:

1. Navigate to job in Databricks UI
2. Check Tags section
3. Verify:
   - `deployed_by: github-actions[bot]`
   - `source: cicd`
   - `environment: dev` (or appropriate target)

- [ ] **Step 5: Query via API (Optional)**

Run:

```bash
databricks jobs get-run --run-id <run_id> --output json | jq '.tags'
```

Expected: Tags show cicd source and github-actions deployer

---

## Task 8: Summary and Handoff

**Files:**
- None

- [ ] **Step 1: Run all tests**

Ensure existing test suite still passes:

```bash
uv run pytest
```

Expected: All tests pass (no regression)

- [ ] **Step 2: Review all commits**

Run:

```bash
git log --oneline -8
```

Expected: Shows 6 commits (one per task):
- docs: add DAB resource segregation design spec
- feat: add deployed_by and deployment_source variables to DAB
- feat: add segregation tags to hello_world_job
- feat: add segregation tags to config_demo_job
- ci: set DEPLOYED_BY and DEPLOYMENT_SOURCE env vars for CI/CD tagging
- docs: add deployment guide with tag segregation information

- [ ] **Step 3: Verify documentation**

Check that:
1. `docs/DEPLOYMENT.md` exists and is complete
2. Spec is saved at `docs/superpowers/specs/2026-04-17-dab-resource-segregation-design.md`
3. Tags are visible in Databricks UI

- [ ] **Step 4: Merge and close**

Once all steps complete:
1. Create final PR with all commits
2. Request review
3. Merge to dev once approved
4. Mark feature complete

---

## Implementation Notes

### DAB Variable Resolution

DAB resolves variables in this order:
1. Environment variables (highest priority)
2. Variable defaults (lowest priority)

So when CI/CD sets `DEPLOYED_BY=github-actions[bot]`, DAB uses that value instead of `${env.USER}`.

### Tag Limitations

- Databricks tags support string values only (no nested objects)
- Tag keys must be lowercase alphanumeric + underscore
- Tag values can contain more characters (spaces, hyphens, etc.) but should be simple strings

### Future Enhancements

The spec identifies these as out-of-scope but they will be implemented in a separate project:
- Cleanup job to delete stale local resources (age-based)
- Audit table in UC to log all deployments
- Hard enforcement (blocking unsafe deployments)

---

## Success Criteria Checklist

- [ ] All new variables added to `databricks.yml`
- [ ] All resource files have tags section
- [ ] CI/CD workflow sets env vars
- [ ] Local deployment tags verified in UI
- [ ] CI/CD deployment tags verified in UI
- [ ] Documentation updated
- [ ] All tests pass
- [ ] Code review approved
- [ ] Merged to dev branch
