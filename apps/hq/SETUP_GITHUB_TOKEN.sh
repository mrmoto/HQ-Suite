#!/bin/bash

# GitHub Personal Access Token Setup
# Sets up HTTPS authentication with personal access token

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "GitHub Personal Access Token Setup"
echo "=========================================="
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "${RED}Error: Not in a Git repository${NC}"
    exit 1
fi

echo "${BLUE}Step 1: Create Personal Access Token${NC}"
echo ""
echo "1. Go to: https://github.com/settings/tokens"
echo "2. Click 'Generate new token' → 'Generate new token (classic)'"
echo "3. Name: 'HQ Development'"
echo "4. Expiration: 90 days (or your preference)"
echo "5. Scopes: Check 'repo' (full control)"
echo "6. Click 'Generate token'"
echo "7. ${RED}COPY THE TOKEN${NC} (you won't see it again!)"
echo ""
read -p "Press Enter after you've created the token..."

echo ""
echo "${BLUE}Step 2: Enter Token Information${NC}"
echo ""
read -p "Enter your GitHub username: " github_username
read -p "Enter your personal access token: " github_token
read -p "Enter your repository name (e.g., 'hq'): " repo_name

if [ -z "$github_username" ] || [ -z "$github_token" ] || [ -z "$repo_name" ]; then
    echo "${RED}Error: All fields required${NC}"
    exit 1
fi

# Configure credential helper
echo ""
echo "Configuring Git credential helper..."
git config --global credential.helper osxkeychain
echo "${GREEN}✓ Credential helper configured${NC}"

# Set remote URL with token
REMOTE_URL="https://${github_token}@github.com/${github_username}/${repo_name}.git"

echo ""
echo "Setting remote URL..."
if git remote | grep -q origin; then
    git remote set-url origin "$REMOTE_URL"
    echo "${GREEN}✓ Remote URL updated${NC}"
else
    git remote add origin "$REMOTE_URL"
    echo "${GREEN}✓ Remote added${NC}"
fi

echo ""
echo "Remote configured:"
git remote -v
echo ""

# Test connection
echo "${BLUE}Step 3: Test Connection${NC}"
echo ""
read -p "Test push to GitHub? (y/n): " test_push

if [ "$test_push" = "y" ] || [ "$test_push" = "Y" ]; then
    # Determine current branch
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
    
    echo "Pushing to GitHub..."
    if git push -u origin "$CURRENT_BRANCH" 2>&1; then
        echo ""
        echo "${GREEN}✓ Successfully pushed to GitHub!${NC}"
    else
        echo ""
        echo "${YELLOW}Push may have failed. Check the output above.${NC}"
        echo "Common issues:"
        echo "  - Repository doesn't exist on GitHub"
        echo "  - Token doesn't have correct permissions"
        echo "  - Branch name mismatch"
    fi
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "${YELLOW}Note:${NC} Your token is stored in the remote URL."
echo "For better security, consider using SSH keys instead."
echo ""
echo "To use SSH instead, run: ./SETUP_GITHUB_SSH.sh"
echo ""
