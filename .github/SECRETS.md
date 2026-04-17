# GitHub Secrets Setup

Configure these secrets in your GitHub repository for CI/CD. **Important:** Use dedicated service accounts for each environment, not personal accounts.

## Development Environment (env:dev)
- `DATABRICKS_DEV_HOST` — Databricks workspace URL (e.g., https://your-workspace.cloud.databricks.com)
- `DATABRICKS_DEV_TOKEN` — PAT token from the `ci-bot-dev` service account
- `DATABRICKS_DEV_SERVICE_ACCOUNT` — Service account identifier (e.g., `ci-bot-dev@databricks.com`)

## Staging Environment (env:stg)
- `DATABRICKS_STG_HOST` — Databricks workspace URL
- `DATABRICKS_STG_TOKEN` — PAT token from the `ci-bot-stg` service account
- `DATABRICKS_STG_SERVICE_ACCOUNT` — Service account identifier (e.g., `ci-bot-stg@databricks.com`)

## Production Environment (env:prod)
- `DATABRICKS_PROD_HOST` — Databricks workspace URL
- `DATABRICKS_PROD_TOKEN` — PAT token from the `ci-bot-prod` service account
- `DATABRICKS_PROD_SERVICE_ACCOUNT` — Service account identifier (e.g., `ci-bot-prod@databricks.com`)

## Creating Service Accounts

1. In Databricks Admin Console → Users & Groups → Service Principals
2. Click "Add service principal"
3. Provide a name (e.g., `ci-bot-dev`, `ci-bot-stg`, `ci-bot-prod`)
4. Optionally add a description: "CI/CD automation for [environment]"
5. Click "Create"
6. Add workspace access:
   - Select the service principal
   - Grant `Workspace Admin` or appropriate catalog permissions
7. Generate PAT token (see section below)

## Generating PAT Tokens for Service Accounts

1. In Databricks Admin Console → Users & Groups → Service Principals
2. Click on the service principal
3. Click "Generate token" in the "Access tokens" section
4. Set appropriate expiration (e.g., 90 days, or "Never" with rotation policy)
5. Copy the token immediately (it won't be shown again)
6. Add to GitHub Secrets with the appropriate name

## Adding Secrets to GitHub

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret name and value

### Create GitHub Environments

1. Settings → Environments → New environment
2. Create `dev`, `stg`, `prod` environments
3. Add the corresponding secrets to each environment:
   - For `dev` environment: Add `DATABRICKS_DEV_HOST`, `DATABRICKS_DEV_TOKEN`, `DATABRICKS_DEV_SERVICE_ACCOUNT`
   - For `stg` environment: Add `DATABRICKS_STG_HOST`, `DATABRICKS_STG_TOKEN`, `DATABRICKS_STG_SERVICE_ACCOUNT`
   - For `prod` environment: Add `DATABRICKS_PROD_HOST`, `DATABRICKS_PROD_TOKEN`, `DATABRICKS_PROD_SERVICE_ACCOUNT`

## Security Best Practices

- **Never use personal access tokens** in CI/CD. Service accounts provide better audit trails and access control.
- **Rotate tokens regularly** (90 days recommended). Set up a reminder to refresh before expiration.
- **Use workspace-level or catalog-level permissions** for service accounts. Avoid giving Admin access unless necessary.
- **Restrict service account permissions** to only what's needed for deployment (e.g., Jobs, Pipelines, Tables in specific catalogs).
- **Monitor token usage** in workspace audit logs to detect unauthorized access.
