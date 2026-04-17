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
