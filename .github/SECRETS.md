# GitHub Secrets Setup

Configure these secrets in your GitHub repository for CI/CD. **Important:** Use OAuth with service accounts (not deprecated PAT tokens).

## Development Environment (env:dev)
- `DATABRICKS_DEV_HOST` — Databricks workspace URL (e.g., https://your-workspace.cloud.databricks.com)
- `DATABRICKS_DEV_CLIENT_ID` — OAuth client ID from the `ci-bot-dev` service account
- `DATABRICKS_DEV_CLIENT_SECRET` — OAuth client secret from the `ci-bot-dev` service account
- `DATABRICKS_DEV_SERVICE_ACCOUNT` — Service account name (e.g., `ci-bot-dev`)

## Staging Environment (env:stg)
- `DATABRICKS_STG_HOST` — Databricks workspace URL
- `DATABRICKS_STG_CLIENT_ID` — OAuth client ID from the `ci-bot-stg` service account
- `DATABRICKS_STG_CLIENT_SECRET` — OAuth client secret from the `ci-bot-stg` service account
- `DATABRICKS_STG_SERVICE_ACCOUNT` — Service account name (e.g., `ci-bot-stg`)

## Production Environment (env:prod)
- `DATABRICKS_PROD_HOST` — Databricks workspace URL
- `DATABRICKS_PROD_CLIENT_ID` — OAuth client ID from the `ci-bot-prod` service account
- `DATABRICKS_PROD_CLIENT_SECRET` — OAuth client secret from the `ci-bot-prod` service account
- `DATABRICKS_PROD_SERVICE_ACCOUNT` — Service account name (e.g., `ci-bot-prod`)

## Creating Service Accounts with OAuth Credentials

1. In Databricks Admin Console → Users & Groups → Service Principals
2. Click "Add service principal"
3. Provide a name (e.g., `ci-bot-dev`, `ci-bot-stg`, `ci-bot-prod`)
4. Optionally add a description: "CI/CD automation for [environment]"
5. Click "Create"
6. Add workspace access:
   - Select the service principal
   - Grant appropriate catalog permissions (avoid blanket Admin access)
7. Generate OAuth credentials (see section below)

## Generating OAuth Credentials for Service Accounts

1. In Databricks Admin Console → Users & Groups → Service Principals
2. Click on the service principal
3. Click "Generate secret" in the "Secrets" section
4. Copy both the **Client ID** and **Client Secret** immediately (secret won't be shown again)
5. Add both values to GitHub Secrets with the appropriate names

**Note:** OAuth credentials are more secure than PAT tokens because:
- They're scoped to a specific service principal
- They support token expiration and rotation
- They enable fine-grained permission control
- They provide better audit trails

## Adding Secrets to GitHub

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret name and value

### Create GitHub Environments

1. Settings → Environments → New environment
2. Create `dev`, `stg`, `prod` environments
3. Add the corresponding secrets to each environment:
   - For `dev`: `DATABRICKS_DEV_HOST`, `DATABRICKS_DEV_CLIENT_ID`, `DATABRICKS_DEV_CLIENT_SECRET`, `DATABRICKS_DEV_SERVICE_ACCOUNT`
   - For `stg`: `DATABRICKS_STG_HOST`, `DATABRICKS_STG_CLIENT_ID`, `DATABRICKS_STG_CLIENT_SECRET`, `DATABRICKS_STG_SERVICE_ACCOUNT`
   - For `prod`: `DATABRICKS_PROD_HOST`, `DATABRICKS_PROD_CLIENT_ID`, `DATABRICKS_PROD_CLIENT_SECRET`, `DATABRICKS_PROD_SERVICE_ACCOUNT`

## Security Best Practices

- **Use OAuth instead of PAT tokens.** OAuth provides better scoping, expiration, and audit trails.
- **Rotate secrets regularly** (90 days recommended). Set up a reminder to refresh before expiration.
- **Use minimal permissions** for service accounts. Grant only what's needed for deployment (e.g., Jobs, Pipelines in specific catalogs).
- **Never commit secrets** to version control. Only store in GitHub Secrets.
- **Monitor OAuth token usage** in workspace audit logs to detect unauthorized access.
- **Restrict secret access** in GitHub. Use GitHub Environments to limit which workflows can access which secrets.
