#!/bin/bash

# Safe Git Commit Script
# Performs pre-commit checks and confirmation before committing

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if we're in a Git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "${RED}Error: Not in a Git repository${NC}"
    exit 1
fi

echo "=========================================="
echo "Safe Git Commit"
echo "=========================================="
echo ""

# Check Git user identity
GIT_NAME=$(git config user.name 2>/dev/null || git config --global user.name 2>/dev/null || echo "")
GIT_EMAIL=$(git config user.email 2>/dev/null || git config --global user.email 2>/dev/null || echo "")

if [ -z "$GIT_NAME" ] || [ -z "$GIT_EMAIL" ]; then
    echo "${YELLOW}Warning: Git user identity not configured${NC}"
    if [ -z "$GIT_NAME" ]; then
        echo "  Name: Not set"
    fi
    if [ -z "$GIT_EMAIL" ]; then
        echo "  Email: Not set"
    fi
    echo ""
    echo "Configure Git identity first:"
    echo "  ./SETUP_GIT_IDENTITY.sh"
    echo "  Or: git config --global user.name 'Your Name'"
    echo "      git config --global user.email 'your.email@example.com'"
    echo ""
    read -p "Continue anyway? (y/n): " continue_choice
    if [ "$continue_choice" != "y" ] && [ "$continue_choice" != "Y" ]; then
        echo "Commit cancelled."
        exit 0
    fi
    echo ""
fi

# Check for staged changes
STAGED=$(git diff --cached --name-only)
if [ -z "$STAGED" ]; then
    echo "${YELLOW}No staged changes found${NC}"
    echo ""
    echo "Current status:"
    git status --short
    echo ""
    read -p "Stage all changes and commit? (y/n): " stage_all
    if [ "$stage_all" = "y" ] || [ "$stage_all" = "Y" ]; then
        echo ""
        echo "Staging all changes..."
        git add .
        STAGED=$(git diff --cached --name-only)
        if [ -z "$STAGED" ]; then
            echo "${RED}No changes to commit${NC}"
            exit 0
        fi
    else
        echo "Commit cancelled. Stage files first: git add <file>"
        exit 0
    fi
fi

# Show what will be committed
echo "${BLUE}Files to be committed:${NC}"
git diff --cached --name-status
echo ""

# Show diff summary
echo "${BLUE}Changes summary:${NC}"
git diff --cached --stat
echo ""

# Show actual changes (first 20 lines)
echo "${BLUE}Preview of changes (first 20 lines):${NC}"
git diff --cached | head -20
if [ $(git diff --cached | wc -l) -gt 20 ]; then
    echo "... (more changes)"
fi
echo ""

# Get commit message
if [ -n "$1" ]; then
    COMMIT_MSG="$1"
    echo "${BLUE}Commit message:${NC} $COMMIT_MSG"
else
    read -p "Enter commit message: " COMMIT_MSG
    if [ -z "$COMMIT_MSG" ]; then
        echo "${RED}Error: Commit message is required${NC}"
        exit 1
    fi
fi

# Check for uncommitted changes
UNCOMMITTED=$(git status --porcelain | grep -v "^[AM]" || echo "")
if [ -n "$UNCOMMITTED" ]; then
    echo ""
    echo "${YELLOW}Warning: You have uncommitted changes${NC}"
    echo ""
    git status --short | grep -v "^[AM]"
    echo ""
    read -p "Commit anyway? (y/n): " commit_anyway
    if [ "$commit_anyway" != "y" ] && [ "$commit_anyway" != "Y" ]; then
        echo "Commit cancelled."
        exit 0
    fi
fi

# Final confirmation
echo ""
echo "${BLUE}Summary:${NC}"
echo "  Files: $(echo "$STAGED" | wc -l | tr -d ' ') file(s)"
echo "  Message: $COMMIT_MSG"
echo ""
read -p "${YELLOW}Create commit? (y/n):${NC} " confirm_commit

if [ "$confirm_commit" != "y" ] && [ "$confirm_commit" != "Y" ]; then
    echo "Commit cancelled."
    exit 0
fi

# Perform commit
echo ""
echo "Creating commit..."
if git commit -m "$COMMIT_MSG"; then
    echo ""
    echo "${GREEN}✓ Commit created successfully${NC}"
    echo ""
    echo "${BLUE}Commit details:${NC}"
    git log -1 --stat
    echo ""
    echo "${BLUE}Next step:${NC} Push to GitHub with ./git_safe_push.sh"
else
    echo ""
    echo "${RED}✗ Commit failed${NC}"
    exit 1
fi
