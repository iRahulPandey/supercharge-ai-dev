# Branch Protection Rules — Enforcing GitFlow

This document describes the branch protection rules that enforce the GitFlow strategy for Supercharge AI Dev.

## Overview

Branch protection rules prevent direct merges that skip the promotion chain:

```
❌ feature/* → stg (BLOCKED)
❌ feature/* → master (BLOCKED)
❌ dev → master (BLOCKED) - must go through stg first
```

```
✅ feature/* → dev (ALLOWED)
✅ dev → stg (ALLOWED)
✅ stg → master (ALLOWED)
```

## Branch Protection Rules

### 1. `master` Branch Rules

**Enforce the following:**

- ✅ Require a pull request before merging
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require code reviews before merging (minimum 1 approval)
  - ✅ Require conversation resolution before merging

- ✅ Require status checks to pass before merging
  - ✅ Require branches to be up to date before merging
  - Status checks required: `test` (all jobs)

- ✅ Restrict who can push to matching branches
  - Only allow push from specific users/teams (optional, more restrictive)

- ✅ Allow force pushes: **NO**

- ✅ Allow deletions: **NO**

**Enforce rules for:**
- Administrators: ✅ YES (enforce on admins too)

**Allow specified actors to bypass required pull requests:**
- Leave empty (no bypass)

---

### 2. `stg` Branch Rules

**Enforce the following:**

- ✅ Require a pull request before merging
  - ✅ Dismiss stale pull request approvals
  - ✅ Require code reviews (minimum 1)
  - ✅ Require conversation resolution

- ✅ Require status checks to pass before merging
  - ✅ Require branches to be up to date before merging
  - Status checks required: `test` (all jobs)

- ✅ Restrict who can push to matching branches
  - Optional: restrict to team leads

- ✅ Allow force pushes: **NO**

- ✅ Allow deletions: **NO**

**Enforce rules for:**
- Administrators: ✅ YES

---

### 3. `dev` Branch Rules

**Enforce the following:**

- ✅ Require a pull request before merging
  - ✅ Dismiss stale pull request approvals
  - ✅ Require code reviews (minimum 1)
  - ✅ Require conversation resolution

- ✅ Require status checks to pass before merging
  - ✅ Require branches to be up to date before merging
  - Status checks required: `test` (all jobs)

- ✅ Allow force pushes: **NO**

- ✅ Allow deletions: **NO**

**Enforce rules for:**
- Administrators: ✅ YES

---

## Setup Instructions

### Option A: GitHub CLI (Recommended)

```bash
# Authenticate with GitHub (if not already)
gh auth login

# Set branch protection for master
gh api repos/{owner}/{repo}/branches/master/protection \
  --input - << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["test"]
  },
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "enforce_admins": true,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

# Set branch protection for stg
gh api repos/{owner}/{repo}/branches/stg/protection \
  --input - << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["test"]
  },
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "enforce_admins": true,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

# Set branch protection for dev
gh api repos/{owner}/{repo}/branches/dev/protection \
  --input - << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["test"]
  },
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "enforce_admins": true,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

echo "✅ Branch protection rules configured"
```

### Option B: GitHub Web UI (Manual)

1. Go to **Settings** → **Branches** → **Branch protection rules**

2. **Add rule for `master`:**
   - Pattern: `master`
   - ✅ Require a pull request before merging
     - ✅ Dismiss stale PR approvals
     - ✅ Require approvals (1)
     - ✅ Require conversation resolution
   - ✅ Require status checks
     - ✅ Require branches to be up to date
     - ✅ Status checks: `test`
   - ✅ Enforce on administrators
   - ❌ Allow force pushes
   - ❌ Allow deletions
   - Click **Create**

3. **Add rule for `stg`:** (Repeat with pattern `stg`)

4. **Add rule for `dev`:** (Repeat with pattern `dev`)

---

## PR Validation Workflow

Additionally, create a workflow that validates PR targets:

```yaml
# .github/workflows/validate-pr-target.yml
name: Validate PR Target Branch

on:
  pull_request:
    types: [opened, reopened, synchronize]

jobs:
  validate-target:
    runs-on: ubuntu-latest
    steps:
      - name: Validate PR target branch
        run: |
          BASE_BRANCH="${{ github.base_ref }}"
          HEAD_BRANCH="${{ github.head_ref }}"

          # Check if head branch is a feature branch
          if [[ $HEAD_BRANCH == feat/* || $HEAD_BRANCH == feature/* || $HEAD_BRANCH == fix/* ]]; then
            # Feature branches can only target dev
            if [ "$BASE_BRANCH" != "dev" ]; then
              echo "❌ ERROR: Feature branches can only merge to 'dev'"
              echo "   Your branch: $HEAD_BRANCH"
              echo "   Target: $BASE_BRANCH (should be 'dev')"
              exit 1
            fi
          fi

          # dev can only target stg
          if [ "$HEAD_BRANCH" = "dev" ] && [ "$BASE_BRANCH" != "stg" ]; then
            echo "❌ ERROR: 'dev' branch can only merge to 'stg'"
            echo "   Target: $BASE_BRANCH (should be 'stg')"
            exit 1
          fi

          # stg can only target master
          if [ "$HEAD_BRANCH" = "stg" ] && [ "$BASE_BRANCH" != "master" ]; then
            echo "❌ ERROR: 'stg' branch can only merge to 'master'"
            echo "   Target: $BASE_BRANCH (should be 'master')"
            exit 1
          fi

          echo "✅ PR target validation passed"
          echo "   Branch: $HEAD_BRANCH → $BASE_BRANCH"
```

---

## Enforcement Chain

| Source Branch | Target Branch | Status | Reason |
|---|---|---|---|
| `feat/*` | `dev` | ✅ ALLOWED | Part of promotion chain |
| `feat/*` | `stg` | ❌ BLOCKED | Skips dev validation |
| `feat/*` | `master` | ❌ BLOCKED | Skips dev and stg validation |
| `dev` | `stg` | ✅ ALLOWED | Part of promotion chain |
| `dev` | `master` | ❌ BLOCKED | Skips stg validation |
| `stg` | `master` | ✅ ALLOWED | Final promotion to prod |
| Any | `feat/*` | ❌ BLOCKED | Feature branches are source only |

---

## Bypass Scenarios

### Hotfix Emergency

In case of critical production bug requiring emergency merge:

1. Create `hotfix/description` branch from `master`
2. Create PR: `hotfix/description` → `master` (requires override)
3. **Requires:**
   - Emergency approval from team lead
   - Manual admin override (with documented reason)
   - Backport fix to `dev` after merge

### Admin Override

Only repository admins can bypass rules. **Always document override reason in PR comments.**

---

## Verification

To verify rules are active:

```bash
# Check master branch protection
gh api repos/{owner}/{repo}/branches/master/protection

# Check stg branch protection
gh api repos/{owner}/{repo}/branches/stg/protection

# Check dev branch protection
gh api repos/{owner}/{repo}/branches/dev/protection
```

Expected response:
```json
{
  "url": "...",
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "required_status_checks": {
    "strict": true,
    "contexts": ["test"]
  },
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

---

## Documentation

Always document:
- **What** changed
- **Why** it changed
- **How** to test it
- **Any manual steps** post-merge

This helps reviewers and ensures clean promotion through environments.
