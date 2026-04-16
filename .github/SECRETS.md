# GitHub Secrets Setup

Configure these secrets in your GitHub repository for CI/CD:

## Development Environment (env:dev)
- `DATABRICKS_DEV_HOST` — Databricks workspace URL (e.g., https://your-workspace.cloud.databricks.com)
- `DATABRICKS_DEV_TOKEN` — Databricks PAT (Personal Access Token)

## Acceptance Environment (env:acc)
- `DATABRICKS_ACC_HOST` — Databricks workspace URL
- `DATABRICKS_ACC_TOKEN` — Databricks PAT

## Production Environment (env:prd)
- `DATABRICKS_PRD_HOST` — Databricks workspace URL
- `DATABRICKS_PRD_TOKEN` — Databricks PAT

### How to Create Databricks PAT

1. Log into your Databricks workspace
2. Click on your user profile (top right)
3. Select "User Settings"
4. Click "Generate new token"
5. Copy the token and add to GitHub Secrets

### How to Add GitHub Secrets

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret name and value
4. Also create GitHub Environments:
   - Settings → Environments → New environment
   - Create `dev`, `acc`, `prd` environments
   - Add the corresponding secrets to each environment
