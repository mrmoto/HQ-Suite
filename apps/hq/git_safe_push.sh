#!/bin/bash

# Safe Git Push Script
# Performs pre-push checks and confirmation before pushing to remote

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

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    echo "${RED}Error: Could not determine current branch${NC}"
    exit 1
fi

echo "=========================================="
echo "Safe Git Push"
echo "=========================================="
echo ""

# Check for uncommitted changes
UNCOMMITTED=$(git status --porcelain)
if [ -n "$UNCOMMITTED" ]; then
    echo "${YELLOW}Warning: You have uncommitted changes${NC}"
    echo ""
    git status --short
    echo ""
    read -p "Continue anyway? (y/n): " continue_choice
    if [ "$continue_choice" != "y" ] && [ "$continue_choice" != "Y" ]; then
        echo "Push cancelled. Commit or stash changes first."
        exit 0
    fi
    echo ""
fi

# Check if remote exists
REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
if [ -z "$REMOTE" ]; then
    echo "${RED}Error: No remote 'origin' configured${NC}"
    echo "Set up remote first: ./SETUP_GITHUB_REMOTE.sh"
    exit 1
fi

# Show remote URL
echo "${BLUE}Remote:${NC} $REMOTE"
echo "${BLUE}Branch:${NC} $CURRENT_BRANCH"
echo ""

# Check if branch exists on remote
REMOTE_BRANCH_EXISTS=$(git ls-remote --heads origin "$CURRENT_BRANCH" 2>/dev/null | grep -q . && echo "yes" || echo "no")

if [ "$REMOTE_BRANCH_EXISTS" = "yes" ]; then
    echo "${YELLOW}Branch '$CURRENT_BRANCH' already exists on remote${NC}"
    
    # Check for local commits not on remote
    LOCAL_COMMITS=$(git log origin/"$CURRENT_BRANCH"..HEAD --oneline 2>/dev/null | wc -l | tr -d ' ')
    if [ "$LOCAL_COMMITS" -gt 0 ]; then
        echo "${BLUE}Local commits to push:${NC} $LOCAL_COMMITS"
        echo ""
        echo "Recent commits:"
        git log origin/"$CURRENT_BRANCH"..HEAD --oneline -5
        echo ""
    else
        echo "${GREEN}No new commits to push${NC}"
        echo ""
        read -p "Push anyway? (y/n): " push_anyway
        if [ "$push_anyway" != "y" ] && [ "$push_anyway" != "Y" ]; then
            echo "Push cancelled."
            exit 0
        fi
    fi
    
    # Check for remote commits not in local
    REMOTE_COMMITS=$(git log HEAD..origin/"$CURRENT_BRANCH" --oneline 2>/dev/null | wc -l | tr -d ' ')
    if [ "$REMOTE_COMMITS" -gt 0 ]; then
        echo "${YELLOW}Warning: Remote has $REMOTE_COMMITS commit(s) you don't have locally${NC}"
        echo ""
        echo "Remote commits:"
        git log HEAD..origin/"$CURRENT_BRANCH" --oneline -5
        echo ""
        echo "${RED}Pushing now may cause conflicts. Consider pulling first.${NC}"
        read -p "Pull first? (y/n): " pull_first
        if [ "$pull_first" = "y" ] || [ "$pull_first" = "Y" ]; then
            echo ""
            echo "Pulling from remote..."
            if git pull origin "$CURRENT_BRANCH"; then
                echo "${GREEN}✓ Pull successful${NC}"
            else
                echo "${RED}✗ Pull failed. Resolve conflicts and try again.${NC}"
                exit 1
            fi
            echo ""
        else
            read -p "Continue with push anyway? (y/n): " continue_push
            if [ "$continue_push" != "y" ] && [ "$continue_push" != "Y" ]; then
                echo "Push cancelled."
                exit 0
            fi
        fi
    fi
else
    echo "${BLUE}This will create a new branch on remote: '$CURRENT_BRANCH'${NC}"
    echo ""
    LOCAL_COMMITS=$(git log --oneline | wc -l | tr -d ' ')
    echo "Commits to push: $LOCAL_COMMITS"
    echo ""
    echo "Recent commits:"
    git log --oneline -5
    echo ""
fi

# Show what will be pushed
echo "${BLUE}Summary:${NC}"
echo "  Remote: $REMOTE"
echo "  Branch: $CURRENT_BRANCH"
if [ "$REMOTE_BRANCH_EXISTS" = "yes" ]; then
    echo "  Action: Update existing branch"
else
    echo "  Action: Create new branch"
fi
echo ""

# Final confirmation
read -p "${YELLOW}Push to GitHub? (y/n):${NC} " confirm_push
if [ "$confirm_push" != "y" ] && [ "$confirm_push" != "Y" ]; then
    echo "Push cancelled."
    exit 0
fi

# Perform push
echo ""
echo "Pushing to GitHub..."
if [ "$REMOTE_BRANCH_EXISTS" = "no" ]; then
    # First push, set upstream
    if git push -u origin "$CURRENT_BRANCH"; then
        echo ""
        echo "${GREEN}✓ Successfully pushed and set upstream${NC}"
    else
        echo ""
        echo "${RED}✗ Push failed${NC}"
        exit 1
    fi
else
    # Regular push
    if git push origin "$CURRENT_BRANCH"; then
        echo ""
        echo "${GREEN}✓ Successfully pushed to GitHub${NC}"
    else
        echo ""
        echo "${RED}✗ Push failed${NC}"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Push Complete!"
echo "=========================================="
echo ""
