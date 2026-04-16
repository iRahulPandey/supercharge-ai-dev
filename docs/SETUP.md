# Setup Guide — Supercharge AI Dev

This guide walks you through the complete setup process for developing with Supercharge AI Dev on your local machine and deploying to Databricks.

**Estimated setup time:** 15-20 minutes

## Prerequisites

Before starting, ensure you have:

- **Git** — Version control system (https://git-scm.com/)
- **Python 3.12** — Required runtime version
- **Databricks CLI** — Command-line tool for Databricks workspace access
- **Databricks Personal Access Token** — For workspace authentication
- **VS Code** (optional but recommended) — With Databricks extension
- **Administrator access** to a Databricks workspace (for initial setup)

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd supercharge-ai-dev
```

Verify you're on the correct branch:
```bash
git branch  # Should show feat/initial-dev or similar
git log --oneline -5  # Verify recent commits
```

## Step 2: Python 3.12 Installation

Choose the method appropriate for your operating system:

### macOS — Homebrew (Recommended)

```bash
# Install Python 3.12
brew install python@3.12

# Verify installation
/usr/local/opt/python@3.12/bin/python3.12 --version

# Create virtual environment
/usr/local/opt/python@3.12/bin/python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### macOS — Pyenv (For multiple Python versions)

```bash
# Install pyenv
brew install pyenv

# Add pyenv to shell (add to ~/.zprofile or ~/.bash_profile)
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"

# Install Python 3.12
pyenv install 3.12.x  # Replace x with latest patch version

# Set local Python version
pyenv local 3.12.x

# Create virtual environment
python -m venv venv
source venv/bin/activate
```

### Linux — Ubuntu/Debian

```bash
# Update package manager
sudo apt-get update
sudo apt-get install -y build-essential libssl-dev libffi-dev python3.12 python3.12-venv

# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Linux — Fedora/RHEL/CentOS

```bash
# Install Python 3.12
sudo dnf install python3.12 python3.12-devel

# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Windows — Python.org Installer

1. Download installer from https://www.python.org/downloads/
2. Run installer, ensure "Add Python to PATH" is checked
3. Open Command Prompt or PowerShell:

```cmd
# Verify installation
python --version

# Create virtual environment
python -m venv venv

# Activate virtual environment (Command Prompt)
venv\Scripts\activate

# Activate virtual environment (PowerShell)
venv\Scripts\Activate.ps1
```

**Verify activation:** Your terminal should show `(venv)` prefix:
```bash
(venv) $ python --version
Python 3.12.x
```

## Step 3: Install UV Package Manager

UV is a fast Python package manager written in Rust. It's optional but highly recommended for dependency management.

### macOS and Linux

```bash
# Install uv using official installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH (may be required)
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
uv --version
```

### Windows

**Option 1: MSI Installer (Easiest)**
- Download from https://github.com/astral-sh/uv/releases
- Run the `.msi` installer and follow prompts

**Option 2: pip**
```cmd
pip install uv
uv --version
```

### macOS — Homebrew

```bash
brew install uv
uv --version
```

## Step 4: Install Project Dependencies

With your virtual environment activated, install all dependencies:

### Using UV (Recommended)

```bash
# Install with dev dependencies
uv sync --extra dev

# Verify installation
uv run python -c "import supercharge_ai; print('✓ Package imported successfully')"
```

### Using pip

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
python -c "import supercharge_ai; print('✓ Package imported successfully')"
```

## Step 5: Databricks Authentication

You need to authenticate with your Databricks workspace. Choose one of three methods:

### Method A: Databricks CLI (Recommended)

```bash
# Install Databricks CLI (if not already installed)
pip install databricks-cli

# Configure workspace authentication
databricks configure --token

# When prompted, enter:
# Databricks Host: https://your-workspace.cloud.databricks.com
# Databricks Token: dapi... (your personal access token)
```

To generate a personal access token:
1. Log in to your Databricks workspace
2. Click your profile icon (top-right)
3. Go to User Settings → Personal Access Tokens
4. Click "Generate new token"
5. Copy and save the token (shown once)

Verify configuration:
```bash
databricks workspace get-status /
# Should show workspace information
```

### Method B: Environment Variables

If you prefer environment variables, create a `.env` file:

```bash
# .env file (NOT committed to git)
DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
DATABRICKS_TOKEN="dapi..."
```

The `python-dotenv` package automatically loads this file. Verify:
```bash
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('DATABRICKS_HOST'))"
```

### Method C: VS Code Databricks Extension

1. Install "Databricks" extension from VS Code Marketplace
2. Open command palette (Cmd+Shift+P on macOS, Ctrl+Shift+P on Windows/Linux)
3. Search for "Databricks: Configure"
4. Follow authentication prompts
5. VS Code automatically picks up the configuration

## Step 6: Create Databricks Resources

Create necessary Unity Catalog objects in your Databricks workspace. Log in to your workspace and run the following SQL in a new notebook cell:

```sql
-- Create catalogs if they don't exist
CREATE CATALOG IF NOT EXISTS dev;
CREATE CATALOG IF NOT EXISTS stg;
CREATE CATALOG IF NOT EXISTS prod;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS dev.supercharge_ai;
CREATE SCHEMA IF NOT EXISTS stg.supercharge_ai;
CREATE SCHEMA IF NOT EXISTS prod.supercharge_ai;

-- Create volumes for data storage
CREATE VOLUME IF NOT EXISTS dev.supercharge_ai.data;
CREATE VOLUME IF NOT EXISTS stg.supercharge_ai.data;
CREATE VOLUME IF NOT EXISTS prod.supercharge_ai.data;

-- Set permissions (adjust as needed for your workspace)
ALTER CATALOG dev OWNER TO `account admins`;
ALTER CATALOG stg OWNER TO `account admins`;
ALTER CATALOG prod OWNER TO `account admins`;
```

After running, verify the resources exist:
```sql
SHOW CATALOGS;
SHOW SCHEMAS IN dev;
SHOW VOLUMES IN dev.supercharge_ai;
```

## Step 7: Configure Project Files

Update configuration files with your workspace-specific settings:

### Update databricks.yml

Edit `databricks.yml` with your workspace URLs:

```yaml
bundle:
  name: supercharge-ai

targets:
  dev:
    mode: development
    workspace:
      host: https://your-dev-workspace.cloud.databricks.com
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}

  stg:
    workspace:
      host: https://your-stg-workspace.cloud.databricks.com
      root_path: /Shared/.bundle/${bundle.name}/${bundle.target}

  prod:
    workspace:
      host: https://your-prod-workspace.cloud.databricks.com
      root_path: /Shared/.bundle/${bundle.name}/${bundle.target}
```

### Create .env File (Optional)

Create `.env` in project root for local development (NOT committed):

```bash
# .env (don't commit this file)
DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
DATABRICKS_TOKEN="dapi..."
CATALOG="dev"
SCHEMA="supercharge_ai"
VOLUME="data"
LOG_LEVEL="INFO"
```

Add to `.gitignore` if not already present:
```bash
echo ".env" >> .gitignore
```

## Step 8: Install Pre-commit Hooks

Pre-commit hooks automatically run code quality checks before each commit:

```bash
# Install pre-commit framework
uv run pre-commit install

# Run all hooks on current changes
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --all-files
```

If hooks fail, they auto-fix many issues:
```bash
# After auto-fix, stage and commit
git add .
git commit -m "chore: fix linting issues"
```

## Step 9: Run Tests

Verify everything works by running the test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Expected output:
# ✓ test_imports.py passed
# ✓ unit/test_config.py passed
# ✓ unit/test_logger.py passed
# ✓ All tests passed
```

Check coverage meets minimum (80%):
```bash
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html  # View detailed coverage report
```

## Step 10: Validate Databricks Bundle

Test your Databricks Asset Bundle configuration:

```bash
# Validate bundle for dev environment
databricks bundle validate -t dev

# Expected output:
# ✓ Bundle validated successfully
# ✓ 2 job resources found
# ✓ Configuration valid for deployment

# If validation fails, check:
# 1. Workspace URLs in databricks.yml
# 2. Databricks CLI authentication
# 3. Resource definitions in resources/*.yml
```

## Step 11: Deploy to Dev Environment

Deploy the bundle to your dev workspace:

```bash
# Deploy bundle
databricks bundle deploy -t dev

# Expected output:
# ✓ Uploading files...
# ✓ Registering jobs...
# ✓ Deployment successful
```

View deployed resources:
```bash
# List all bundle resources
databricks bundle list -t dev

# View specific job
databricks jobs get --job-id <job_id>
```

## Step 12: GitHub Secrets (CI/CD Setup)

If setting up GitHub Actions for CI/CD, add these secrets to your repository:

1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Add new secrets:

| Secret Name | Value | Notes |
|-------------|-------|-------|
| `DATABRICKS_HOST` | `https://your-workspace.cloud.databricks.com` | Dev workspace URL |
| `DATABRICKS_TOKEN` | Your personal access token | Read-only PAT recommended for CI |
| `PYTHON_VERSION` | `3.12` | Match `.python-version` |

For automated deployments, create a separate service principal with limited permissions:

```bash
# Create service principal in Databricks admin console
# Grant permissions to stg and prod catalogs only
# Create token and add as GitHub secret: DATABRICKS_TOKEN_DEPLOY
```

## Verification Checklist

Before starting development, verify all components work:

- [ ] Python 3.12 installed: `python --version`
- [ ] Virtual environment active: `(venv)` shown in terminal
- [ ] Dependencies installed: `uv run python -c "import supercharge_ai"`
- [ ] Databricks CLI configured: `databricks workspace get-status /`
- [ ] Pre-commit hooks installed: `cat .git/hooks/pre-commit`
- [ ] Tests pass: `uv run pytest` (all tests green)
- [ ] Linting passes: `uv run ruff check .`
- [ ] Type checking passes: `uv run python -m mypy src/ --ignore-missing-imports`
- [ ] Bundle validates: `databricks bundle validate -t dev`
- [ ] Bundle deploys: `databricks bundle deploy -t dev`
- [ ] GitHub secrets configured (if using CI/CD)
- [ ] `.env` file created and `.gitignore` updated
- [ ] Notebooks created in workspace
- [ ] Jobs visible in `databricks bundle list -t dev`

## Development Commands

Now that setup is complete, here are common commands for daily development:

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint check
uv run ruff check . --fix

# Type checking
uv run mypy src/ --ignore-missing-imports

# Run main entry point
uv run python main.py

# Validate bundle
databricks bundle validate -t dev

# Deploy bundle
databricks bundle deploy -t dev

# Run a job
databricks bundle run -t dev hello_world_job

# View logs
databricks jobs get-run --run-id <run_id>
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'supercharge_ai'"

**Solution:**
```bash
# Ensure package is installed in editable mode
pip install -e "."

# Or with uv
uv sync --extra dev

# Verify Python path
python -c "import sys; print(sys.path)"
```

### Issue: "No Databricks credentials found"

**Solution:**
```bash
# Check if CLI is configured
cat ~/.databrickscfg

# If empty, configure it
databricks configure --token

# Or set environment variables
export DATABRICKS_HOST="https://workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."
```

### Issue: "Bundle validation fails with 'Workspace not found'"

**Solution:**
```bash
# Verify workspace URL is correct
cat databricks.yml | grep host

# Test workspace access
databricks workspace list

# Ensure Databricks CLI uses correct auth
databricks auth current
```

### Issue: "Pre-commit hook fails"

**Solution:**
```bash
# Run hooks manually to see errors
uv run pre-commit run --all-files

# Auto-fix common issues
uv run ruff check . --fix
uv run ruff format .

# Commit after fixing
git add .
git commit -m "chore: fix linting"
```

### Issue: "Tests fail after changes"

**Solution:**
```bash
# Run with verbose output
uv run pytest -vv

# Run specific test
uv run pytest tests/unit/test_config.py::test_name -vv

# Check coverage
uv run pytest --cov=src --cov-report=html
```

### Issue: "Python version mismatch in CI"

**Solution:**
```bash
# Verify local Python version matches .python-version
cat .python-version
python --version

# Update CI configuration if needed
cat .github/workflows/tests.yml
```

## Next Steps

After completing setup:

1. **Read documentation:**
   - [README.md](../README.md) — Project overview
   - [ARCHITECTURE.md](ARCHITECTURE.md) — Design patterns
   - [CLAUDE.md](../CLAUDE.md) — Development guidelines

2. **Explore example code:**
   - `notebooks/1_hello_world.py` — Hello world notebook
   - `notebooks/2_config_usage.py` — Configuration example
   - `src/supercharge_ai/config.py` — Configuration implementation

3. **Start developing:**
   - Create feature branch: `git checkout -b feat/my-feature`
   - Write tests in `tests/` directory
   - Implement code in `src/supercharge_ai/`
   - Commit with conventional format
   - Create pull request for review

4. **Deploy to production:**
   - Follow promotion process: dev → stg → prod
   - Validate bundle at each stage
   - Run full test suite before deployment
   - Monitor job runs in Databricks workspace

## Resources

- [Databricks Documentation](https://docs.databricks.com/)
- [Databricks Asset Bundles](https://docs.databricks.com/en/dev-tools/bundles/)
- [Python 3.12 Documentation](https://docs.python.org/3.12/)
- [Pytest Documentation](https://docs.pytest.org/)
- [UV Package Manager](https://docs.astral.sh/uv/)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design patterns
3. Check existing GitHub issues
4. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Your environment (OS, Python version, etc.)
   - Relevant log output

---

**Setup completed!** You're ready to start development. See [README.md](../README.md) for next steps.
