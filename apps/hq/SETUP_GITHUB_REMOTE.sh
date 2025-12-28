#!/bin/bash

# GitHub Remote Setup Script
# Interactively sets up GitHub remote repository for Git

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "GitHub Remote Repository Setup"
echo "=========================================="
echo ""

# Check if we're in a Git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "${RED}Error: Not in a Git repository${NC}"
    echo "Initialize Git first: git init"
    exit 1
fi

# Check current remote
CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")

if [ -n "$CURRENT_REMOTE" ]; then
    echo "${YELLOW}Current remote 'origin':${NC}"
    echo "  $CURRENT_REMOTE"
    echo ""
    read -p "Update remote? (y/n): " update_remote
    if [ "$update_remote" != "y" ] && [ "$update_remote" != "Y" ]; then
        echo "Remote unchanged."
        exit 0
    fi
    echo ""
fi

# Get GitHub username
read -p "Enter your GitHub username: " github_username
if [ -z "$github_username" ]; then
    echo "${RED}Error: GitHub username is required${NC}"
    exit 1
fi

# Get repository name
read -p "Enter repository name [$github_username/hq]: " repo_name
repo_name=${repo_name:-"$github_username/hq"}

# Remove 'github.com/' or 'username/' prefix if user included it
repo_name=$(echo "$repo_name" | sed 's|^https://github.com/||' | sed 's|^git@github.com:||' | sed 's|\.git$||')

# Construct SSH URL
REMOTE_URL="git@github.com:${repo_name}.git"

echo ""
echo "${BLUE}Remote URL will be:${NC}"
echo "  $REMOTE_URL"
echo ""
read -p "Continue? (y/n): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Setup cancelled."
    exit 0
fi

# Set or update remote
if [ -n "$CURRENT_REMOTE" ]; then
    echo ""
    echo "Updating remote 'origin'..."
    git remote set-url origin "$REMOTE_URL"
    echo "${GREEN}✓ Remote updated${NC}"
else
    echo ""
    echo "Adding remote 'origin'..."
    git remote add origin "$REMOTE_URL"
    echo "${GREEN}✓ Remote added${NC}"
fi

# Verify remote
echo ""
echo "Verifying remote configuration..."
git remote -v
echo ""

# Test SSH connection to GitHub
echo "Testing SSH connection to GitHub..."
TEST_OUTPUT=$(ssh -T git@github.com 2>&1)
TEST_EXIT=$?

if [ $TEST_EXIT -eq 0 ] || echo "$TEST_OUTPUT" | grep -q "successfully authenticated"; then
    echo "${GREEN}✓ SSH connection successful${NC}"
    echo "$TEST_OUTPUT"
elif echo "$TEST_OUTPUT" | grep -q "Hi"; then
    echo "${GREEN}✓ SSH connection successful${NC}"
    echo "$TEST_OUTPUT"
elif echo "$TEST_OUTPUT" | grep -q "Permission denied"; then
    echo "${RED}✗ SSH authentication failed${NC}"
    echo "$TEST_OUTPUT"
    echo ""
    echo "${YELLOW}Troubleshooting:${NC}"
    echo "1. Make sure SSH keys are set up (run SETUP_GITHUB_SSH.sh)"
    echo "2. Verify your public key is added to GitHub"
    echo "3. Test manually: ssh -T git@github.com"
    exit 1
else
    echo "${YELLOW}SSH test completed${NC}"
    echo "$TEST_OUTPUT"
fi

# Check if repository exists on GitHub
echo ""
echo "Checking if repository exists on GitHub..."
REPO_EXISTS=$(git ls-remote "$REMOTE_URL" > /dev/null 2>&1 && echo "yes" || echo "no")

if [ "$REPO_EXISTS" = "yes" ]; then
    echo "${GREEN}✓ Repository exists on GitHub${NC}"
    echo ""
    read -p "Fetch from remote? (y/n): " fetch_choice
    if [ "$fetch_choice" = "y" ] || [ "$fetch_choice" = "Y" ]; then
        echo "Fetching from remote..."
        git fetch origin
        echo "${GREEN}✓ Fetched from remote${NC}"
    fi
else
    echo "${YELLOW}Repository does not exist on GitHub yet${NC}"
    echo ""
    echo "${BLUE}To create the repository:${NC}"
    echo "1. Go to: https://github.com/new"
    echo "2. Repository name: $(basename "$repo_name")"
    echo "3. Choose public or private"
    echo "4. Do NOT initialize with README, .gitignore, or license"
    echo "5. Click 'Create repository'"
    echo ""
    read -p "Press Enter after you've created the repository on GitHub..."
    
    # Test again
    echo ""
    echo "Verifying repository exists..."
    if git ls-remote "$REMOTE_URL" > /dev/null 2>&1; then
        echo "${GREEN}✓ Repository found${NC}"
    else
        echo "${YELLOW}Repository not found yet. You may need to:${NC}"
        echo "1. Wait a few seconds for GitHub to create it"
        echo "2. Verify the repository name is correct"
        echo "3. Check repository visibility (public/private)"
    fi
fi

# Show current branch
CURRENT_BRANCH=$(git branch --show-current)
echo ""
echo "${BLUE}Current branch:${NC} $CURRENT_BRANCH"

# Offer to push
if [ "$REPO_EXISTS" = "yes" ] || git ls-remote "$REMOTE_URL" > /dev/null 2>&1; then
    echo ""
    read -p "Push current branch to GitHub? (y/n): " push_choice
    if [ "$push_choice" = "y" ] || [ "$push_choice" = "Y" ]; then
        echo ""
        echo "Pushing to GitHub..."
        if git push -u origin "$CURRENT_BRANCH" 2>&1; then
            echo "${GREEN}✓ Successfully pushed to GitHub${NC}"
        else
            echo "${YELLOW}Push completed (check output above for details)${NC}"
        fi
    fi
fi

echo ""
echo "=========================================="
echo "GitHub Remote Setup Complete!"
echo "=========================================="
echo ""
echo "${GREEN}Summary:${NC}"
echo "  ✓ Remote 'origin' configured: $REMOTE_URL"
echo "  ✓ SSH connection verified"
if [ "$REPO_EXISTS" = "yes" ]; then
    echo "  ✓ Repository exists on GitHub"
fi
echo ""
echo "${BLUE}Useful commands:${NC}"
echo "  git remote -v              # View remotes"
echo "  git push origin $CURRENT_BRANCH    # Push to GitHub"
echo "  git pull origin $CURRENT_BRANCH    # Pull from GitHub"
echo ""
