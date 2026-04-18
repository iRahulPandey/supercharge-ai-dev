# Databricks Asset Bundle File Synchronization

## Problem: Notebooks Not Being Deployed

When deploying via DAB, the directory structure was created at `/Workspace/supercharge-ai/dev/files/notebooks/` but **no notebook files were actually copied into it**. This happened because:

1. **Missing `sync.paths` configuration** — DAB wasn't told which local directories to sync to the workspace
2. **Incorrect notebook path references** — Job tasks referenced absolute workspace paths instead of relative paths

## How DAB Deployment Works

### 1. Resource Inclusion (`include:` directive)

The `include:` directive in `databricks.yml` specifies which YAML resource files to include in the bundle definition:

```yaml
include:
  - resources/*.yml      # Includes all job definitions
```

This **only includes configuration files**, not source code or notebooks.

### 2. File Synchronization (`sync.paths` directive)

The `sync.paths` directive specifies which local directories should be synchronized to the workspace:

```yaml
sync:
  paths:
    - ./notebooks       # Sync notebooks directory to workspace
    - ./src            # Sync source code directory (if needed)
```

**This is the critical configuration that was missing.** Without it, no source files are synced, only the directory structure is created.

### 3. Deployment Flow

When you run `databricks bundle deploy --target dev`:

```
Local Project Structure:
├── databricks.yml              (bundle config)
├── resources/
│   ├── hello_world_job.yml     (job definition)
│   └── config_demo_job.yml     (job definition)
└── notebooks/
    ├── 1_hello_world.py        ← sync.paths includes this
    └── 2_config_usage.py       ← sync.paths includes this

DAB Deployment Process:
1. Read databricks.yml and target configuration
2. Include YAML resources (via include: directive)
3. Sync local files (via sync.paths directive) to:
   /Workspace/supercharge-ai/dev/files/
4. Create workspace directory structure:
   /Workspace/supercharge-ai/dev/files/
   ├── notebooks/
   │   ├── 1_hello_world.py      ← Now deployed!
   │   └── 2_config_usage.py      ← Now deployed!
   └── .bundle/ (metadata)
```

### 4. Notebook Path Resolution

In job task definitions, specify relative paths from the bundle root:

**Incorrect (absolute path):**
```yaml
notebook_path: ${workspace.root_path}/notebooks/1_hello_world  # Path doesn't exist yet!
```

**Correct (relative path):**
```yaml
notebook_path: ./notebooks/1_hello_world  # Relative to bundle root
```

DAB resolves the relative path to the actual workspace location:
- Bundle root path: `/Workspace/supercharge-ai/dev/files/`
- Relative path: `./notebooks/1_hello_world`
- Resolved workspace path: `/Workspace/supercharge-ai/dev/files/notebooks/1_hello_world`

## Our Implementation

### databricks.yml

```yaml
bundle:
  name: supercharge-ai

sync:
  paths:
    - ./notebooks           # ← Enables notebook deployment

include:
  - resources/*.yml        # ← Includes job definitions

variables:
  # ... tag variables for local vs CI/CD segregation
```

### Job Definitions (hello_world_job.yml)

```yaml
resources:
  jobs:
    hello_world_job:
      name: Hello World Job
      tags:
        deployed_by: ${var.deployed_by}      # local-developer or ci-bot-dev
        source: ${var.deployment_source}     # local or cicd
        environment: ${bundle.target}         # dev, stg, or prod
      tasks:
        - task_key: hello_world
          notebook_task:
            notebook_path: ./notebooks/1_hello_world  # ← Relative path
          environment_key: default
```

## Testing the Fix

### Local Deployment

```bash
# Navigate to project root
cd ~/Projects/supercharge-ai-dev

# Validate bundle configuration
databricks bundle validate --target dev

# Deploy to dev
databricks bundle deploy --target dev

# Run the validation job
databricks bundle run hello_world_job --target dev
```

### Verify Notebooks in Workspace

```bash
# Query the API to verify notebook deployment
curl -s https://dbc-8943fe10-4fbf.cloud.databricks.com/api/2.0/workspace/get-status \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -d '{
    "path": "/Workspace/supercharge-ai/dev/files/notebooks/1_hello_world"
  }' | jq '.path, .object_type'

# Output should show:
# "/Workspace/supercharge-ai/dev/files/notebooks/1_hello_world"
# "NOTEBOOK"
```

### Verify Tags

```bash
# Query deployed job to verify tags
curl -s https://dbc-8943fe10-4fbf.cloud.databricks.com/api/2.1/jobs/get \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -d '{"job_id": JOB_ID}' | jq '.job.tags'

# Output should show:
# {
#   "deployed_by": "local-developer",
#   "source": "local",
#   "environment": "dev"
# }
```

## Key Takeaways

1. **`sync.paths` is essential** — Without it, no source files are deployed, only empty directories
2. **Relative paths for notebooks** — Job tasks reference notebooks relative to the bundle root
3. **Tags for segregation** — DAB variables inject tags to track deployment source (local vs CI/CD)
4. **Workspace folder structure** — All environments deploy to managed folder structure:
   - `/Workspace/supercharge-ai/dev/`
   - `/Workspace/supercharge-ai/stg/`
   - `/Workspace/supercharge-ai/prod/`

## References

- [Databricks Asset Bundles Documentation](https://docs.databricks.com/gcp/en/dev-tools/bundles/)
- [Bundle Sync Configuration](https://docs.databricks.com/aws/en/dev-tools/bundles/reference#sync-configuration)
- [Notebook Task Paths](https://docs.databricks.com/gcp/en/dev-tools/bundles/job-task-types#notebook-task)
