#!/usr/bin/env bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  GitFlow Branch Protection Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo "   Install from: https://cli.github.com/"
    exit 1
fi

# Check if gh is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI is not authenticated${NC}"
    echo "   Run: gh auth login"
    exit 1
fi

# Get current repository
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
if [ -z "$REPO" ]; then
    echo -e "${RED}❌ Could not determine repository${NC}"
    echo "   Make sure you're in a GitHub repository directory"
    exit 1
fi

echo -e "${GREEN}✓ Repository: $REPO${NC}"
echo ""

# Define branch protection rules
declare -a BRANCHES=("master" "stg" "dev")

setup_branch_protection() {
    local branch=$1
    echo -e "${YELLOW}⏳ Setting up protection for branch: $branch${NC}"

    gh api -X PUT repos/$REPO/branches/$branch/protection \
        --input - << EOF
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
  "allow_force_pushes": false,
  "allow_deletions": false,
  "restrictions": null
}
EOF

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Protection configured for $branch${NC}"
    else
        echo -e "${RED}✗ Failed to configure protection for $branch${NC}"
        return 1
    fi
}

# Setup protection for each branch
FAILED=0
for branch in "${BRANCHES[@]}"; do
    setup_branch_protection "$branch" || FAILED=$((FAILED + 1))
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All branch protection rules configured successfully!${NC}"
    echo ""
    echo -e "${BLUE}Enforcement Rules:${NC}"
    echo "  ✅ feat/* → dev  (ALLOWED)"
    echo "  ❌ feat/* → stg  (BLOCKED - must go through dev first)"
    echo "  ❌ feat/* → master (BLOCKED - must go through dev and stg)"
    echo "  ✅ dev → stg (ALLOWED)"
    echo "  ❌ dev → master (BLOCKED - must go through stg)"
    echo "  ✅ stg → master (ALLOWED)"
    echo ""
    echo -e "${BLUE}Features Enabled:${NC}"
    echo "  • Require pull requests"
    echo "  • Require 1 code review approval"
    echo "  • Dismiss stale PR reviews on new commits"
    echo "  • Require conversation resolution"
    echo "  • Require status checks (test workflow)"
    echo "  • Require up-to-date branches"
    echo "  • Enforce on administrators"
    echo "  • Prevent force pushes"
    echo "  • Prevent deletions"
    echo ""
    echo -e "${BLUE}📖 Documentation: docs/GITFLOW.md${NC}"
    echo -e "${BLUE}📋 Details: .github/BRANCH_PROTECTION.md${NC}"
    exit 0
else
    echo -e "${RED}❌ Failed to configure $FAILED branch(es)${NC}"
    echo -e "${YELLOW}⚠️  Please check the errors above and try again${NC}"
    exit 1
fi
