# CI/CD Standards & Security Practices

This document outlines the industry-standard CI/CD, security, and code quality practices implemented in this project.

## Overview

Our CI/CD pipeline enforces production-grade standards covering:
- **Security** — Secret detection, dependency scanning, SAST
- **Code Quality** — Linting, formatting, type checking
- **Naming Conventions** — Commits, branches, files
- **Testing** — Unit tests, coverage, integration tests
- **Documentation** — Docstring coverage, architecture docs

---

## 1. Secret Detection & Leak Prevention

### Pre-commit Hooks (Local)

#### 1.1 Gitleaks
- **Tool**: Gitleaks (https://github.com/gitleaks/gitleaks)
- **Purpose**: Detect secrets before they're committed
- **Patterns**: API keys, passwords, tokens, private keys, AWS credentials
- **Run**: Automatically on every `git commit`

#### 1.2 Private Key Detection
- **Tool**: `detect-private-key` (pre-commit hook)
- **Patterns**: RSA keys, SSH keys, PGP keys

### CI Pipeline (GitHub Actions)

#### 1.3 Pip-audit
- **Runs**: On every push and PR
- **Purpose**: Scan dependencies for known vulnerabilities
- **Reports**: CVE, severity, fix versions

---

## 2. Code Quality & Style

### 2.1 Linting with Ruff
- **Enabled**: F, E, W, B, I, UP, SIM, ANN
- **Line Length**: 90 characters
- **Auto-fix**: Available for many issues

### 2.2 Code Formatting
- **Tool**: Ruff formatter
- **Indent**: Spaces (4 chars)
- **Enforcement**: Strict

### 2.3 Type Checking with MyPy
- **Coverage**: All `src/` files
- **Strictness**: Type hints required

### 2.4 Docstring Coverage
- **Tool**: Interrogate
- **Minimum**: 50% coverage
- **Target**: 80%+ coverage

---

## 3. Security Scanning (SAST)

### 3.1 Bandit — Static Application Security Testing
- **Checks**: SQL injection, hardcoded secrets, insecure crypto
- **Skipped**: B101 (assert in tests)

---

## 4. Naming Conventions

### 4.1 Commit Messages (Conventional Commits)

**Format**: `<type>(<scope>): <description>`

**Types**:
- `feat` — New feature
- `fix` — Bug fix
- `refactor` — Code restructuring
- `docs` — Documentation
- `test` — Tests
- `chore` — Tooling/config
- `perf` — Performance
- `ci` — CI/CD changes
- `security` — Security fixes

**Rules**:
- Imperative mood, lowercase
- < 72 characters
- Explain WHY, not WHAT

**Examples**:
```
feat(config): add environment-specific configuration loading
fix(logger): handle async logging in Databricks notebooks
security: add gitleaks secret detection
```

### 4.2 Branch Naming

**Format**: `<type>/<description-in-kebab-case>`

**Examples**:
```
feat/environment-configuration
fix/async-logging-databricks
security/add-secret-scanning
```

### 4.3 File Naming
- **Python**: `snake_case`
- **Directories**: `snake_case`
- **Constants**: `SCREAMING_SNAKE_CASE`

---

## 5. Testing Standards

### 5.1 Test Coverage

| Component | Minimum |
|-----------|---------|
| Core logic | 100% |
| Security | 100% |
| SDK integration | 95% |
| Overall | 80% |

### 5.2 Test Naming
```
test_<function>_<scenario>
test_config_loads_from_yaml
test_config_raises_on_invalid_environment
```

---

## 6. CI/CD Pipeline Stages

### Local (Pre-commit)
1. Whitespace/formatting
2. YAML/JSON validation
3. Large file detection
4. Secret detection (Gitleaks)
5. Private key detection
6. Linting (Ruff)
7. Type checking (MyPy)
8. Security (Bandit)
9. Docstring coverage

### Remote (GitHub Actions)

**Lint & Format Job**:
- Ruff linting
- Ruff formatting
- MyPy type checking

**Tests Job**:
- Pytest suite
- Coverage report
- Codecov upload

**Security Job**:
- Pip-audit vulnerability scan

### Deployment (Master Only)
```
Master Push → Dev → Staging → Production
```

---

## 7. Security Best Practices

### DO
- Use `.env` files (never commit)
- Use GitHub Secrets for CI/CD
- Pin all package versions
- Validate all user input
- Parameterized queries only

### DON'T
- Hardcode credentials
- Commit `.env` files
- Log secrets
- Use `eval()` or `exec()`
- Share PATs in messages

---

## 8. Running All Checks

```bash
# Pre-commit hooks (automatic)
uv run pre-commit install
uv run pre-commit run --all-files

# Manual checks
uv run ruff check .
uv run mypy src/ --ignore-missing-imports
uv run pytest --cov=src --cov-report=term-missing
uv run pip-audit --skip-editable
```

---

**Last Updated**: April 2026
