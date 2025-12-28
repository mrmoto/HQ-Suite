#!/bin/bash

# Safe Git Branch Script
# Safely creates a new branch with optional stashing and backup

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
echo "Safe Git Branch Creation"
echo "=========================================="
echo ""

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    echo "${RED}Error: Could not determine current branch${NC}"
    exit 1
fi

echo "${BLUE}Current branch:${NC} $CURRENT_BRANCH"
echo ""

# Get new branch name
if [ -n "$1" ]; then
    NEW_BRANCH="$1"
else
    read -p "Enter new branch name: " NEW_BRANCH
    if [ -z "$NEW_BRANCH" ]; then
        echo "${RED}Error: Branch name is required${NC}"
        exit 1
    fi
fi

# Validate branch name (basic check)
if [[ ! "$NEW_BRANCH" =~ ^[a-zA-Z0-9/_-]+$ ]]; then
    echo "${RED}Error: Invalid branch name${NC}"
    echo "Branch names should contain only letters, numbers, /, _, and -"
    exit 1
fi

# Check if branch already exists locally
if git show-ref --verify --quiet refs/heads/"$NEW_BRANCH"; then
    echo "${YELLOW}Branch '$NEW_BRANCH' already exists locally${NC}"
    read -p "Switch to existing branch? (y/n): " switch_branch
    if [ "$switch_branch" = "y" ] || [ "$switch_branch" = "Y" ]; then
        git checkout "$NEW_BRANCH"
        echo "${GREEN}✓ Switched to branch '$NEW_BRANCH'${NC}"
        exit 0
    else
        echo "Operation cancelled."
        exit 0
    fi
fi

# Check for uncommitted changes
UNCOMMITTED=$(git status --porcelain)
if [ -n "$UNCOMMITTED" ]; then
    echo "${YELLOW}You have uncommitted changes:${NC}"
    echo ""
    git status --short
    echo ""
    echo "Options:"
    echo "  1. Stash changes (recommended)"
    echo "  2. Commit changes first"
    echo "  3. Create branch anyway (changes will come with you)"
    echo "  4. Cancel"
    echo ""
    read -p "Choose option (1-4): " uncommitted_choice
    
    case "$uncommitted_choice" in
        1)
            echo ""
            echo "Stashing changes..."
            git stash push -m "Stashed before creating branch $NEW_BRANCH"
            echo "${GREEN}✓ Changes stashed${NC}"
            STASHED=true
            ;;
        2)
            echo ""
            echo "Please commit your changes first:"
            echo "  ./git_safe_commit.sh"
            echo "  Or: git commit -m 'Your message'"
            exit 0
            ;;
        3)
            echo ""
            echo "${YELLOW}Creating branch with uncommitted changes...${NC}"
            STASHED=false
            ;;
        4)
            echo "Operation cancelled."
            exit 0
            ;;
        *)
            echo "Invalid choice. Operation cancelled."
            exit 0
            ;;
    esac
else
    STASHED=false
fi

# Offer to create backup branch
echo ""
read -p "Create backup branch of current state? (y/n): " create_backup
if [ "$create_backup" = "y" ] || [ "$create_backup" = "Y" ]; then
    BACKUP_BRANCH="${CURRENT_BRANCH}-backup-$(date +%Y%m%d-%H%M%S)"
    echo ""
    echo "Creating backup branch: $BACKUP_BRANCH"
    git branch "$BACKUP_BRANCH"
    echo "${GREEN}✓ Backup branch created: $BACKUP_BRANCH${NC}"
fi

# Create and switch to new branch
echo ""
echo "Creating new branch: $NEW_BRANCH"
if git checkout -b "$NEW_BRANCH"; then
    echo "${GREEN}✓ Branch created and switched${NC}"
else
    echo "${RED}✗ Failed to create branch${NC}"
    exit 1
fi

# Restore stashed changes if applicable
if [ "$STASHED" = true ]; then
    echo ""
    read -p "Restore stashed changes? (y/n): " restore_stash
    if [ "$restore_stash" = "y" ] || [ "$restore_stash" = "Y" ]; then
        echo "Restoring stashed changes..."
        if git stash pop; then
            echo "${GREEN}✓ Stashed changes restored${NC}"
        else
            echo "${YELLOW}⚠ Stash restore had conflicts or issues${NC}"
        fi
    fi
fi

# Show status
echo ""
echo "=========================================="
echo "Branch Creation Complete!"
echo "=========================================="
echo ""
echo "${GREEN}Summary:${NC}"
echo "  Previous branch: $CURRENT_BRANCH"
echo "  New branch: $NEW_BRANCH"
if [ "$STASHED" = true ]; then
    echo "  Changes: Stashed (restore if needed)"
fi
if [ "$create_backup" = "y" ] || [ "$create_backup" = "Y" ]; then
    echo "  Backup: $BACKUP_BRANCH"
fi
echo ""
echo "${BLUE}Current status:${NC}"
git status --short
echo ""
echo "${BLUE}Useful commands:${NC}"
echo "  git status              # Check status"
echo "  git log --oneline      # View commits"
echo "  git push -u origin $NEW_BRANCH  # Push new branch"
echo ""
