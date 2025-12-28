#!/bin/bash

# Master Git and GitHub Setup Script
# Orchestrates complete setup: Git identity, SSH keys, remote, and YubiKey 2FA

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Git and GitHub Complete Setup"
echo "=========================================="
echo ""
echo "This script will guide you through:"
echo "  1. Git user identity configuration"
echo "  2. SSH key generation and GitHub setup"
echo "  3. GitHub remote repository configuration"
echo "  4. YubiKey 2FA setup instructions"
echo ""
read -p "Continue? (y/n): " start_setup
if [ "$start_setup" != "y" ] && [ "$start_setup" != "Y" ]; then
    echo "Setup cancelled."
    exit 0
fi

echo ""
echo "=========================================="
echo "Step 1: Git User Identity"
echo "=========================================="
echo ""

# Check current Git identity
GIT_NAME=$(git config --global user.name 2>/dev/null || echo "")
GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")

if [ -n "$GIT_NAME" ] && [ -n "$GIT_EMAIL" ]; then
    echo "${GREEN}Git identity already configured:${NC}"
    echo "  Name:  $GIT_NAME"
    echo "  Email: $GIT_EMAIL"
    echo ""
    read -p "Update Git identity? (y/n): " update_git
    if [ "$update_git" = "y" ] || [ "$update_git" = "Y" ]; then
        if [ -f "$SCRIPT_DIR/SETUP_GIT_IDENTITY.sh" ]; then
            "$SCRIPT_DIR/SETUP_GIT_IDENTITY.sh"
        else
            echo "${RED}Error: SETUP_GIT_IDENTITY.sh not found${NC}"
            exit 1
        fi
    fi
else
    echo "${YELLOW}Git identity not configured${NC}"
    if [ -f "$SCRIPT_DIR/SETUP_GIT_IDENTITY.sh" ]; then
        "$SCRIPT_DIR/SETUP_GIT_IDENTITY.sh"
    else
        echo "${RED}Error: SETUP_GIT_IDENTITY.sh not found${NC}"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Step 2: SSH Key Setup"
echo "=========================================="
echo ""

# Check for existing SSH keys
if [ -f ~/.ssh/id_ed25519.pub ] || [ -f ~/.ssh/id_rsa.pub ]; then
    echo "${YELLOW}Existing SSH keys found${NC}"
    ls -la ~/.ssh/id_*.pub 2>/dev/null || true
    echo ""
    read -p "Set up SSH keys anyway? (y/n): " setup_ssh
    if [ "$setup_ssh" = "y" ] || [ "$setup_ssh" = "Y" ]; then
        if [ -f "$SCRIPT_DIR/SETUP_GITHUB_SSH.sh" ]; then
            "$SCRIPT_DIR/SETUP_GITHUB_SSH.sh"
        else
            echo "${RED}Error: SETUP_GITHUB_SSH.sh not found${NC}"
            exit 1
        fi
    else
        echo "Skipping SSH setup."
    fi
else
    echo "${BLUE}No SSH keys found. Setting up now...${NC}"
    if [ -f "$SCRIPT_DIR/SETUP_GITHUB_SSH.sh" ]; then
        "$SCRIPT_DIR/SETUP_GITHUB_SSH.sh"
    else
        echo "${RED}Error: SETUP_GITHUB_SSH.sh not found${NC}"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Step 3: GitHub Remote Repository"
echo "=========================================="
echo ""

# Check if remote exists
REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
if [ -n "$REMOTE" ]; then
    echo "${GREEN}Remote 'origin' already configured:${NC}"
    echo "  $REMOTE"
    echo ""
    read -p "Update remote? (y/n): " update_remote
    if [ "$update_remote" = "y" ] || [ "$update_remote" = "Y" ]; then
        if [ -f "$SCRIPT_DIR/SETUP_GITHUB_REMOTE.sh" ]; then
            "$SCRIPT_DIR/SETUP_GITHUB_REMOTE.sh"
        else
            echo "${RED}Error: SETUP_GITHUB_REMOTE.sh not found${NC}"
            exit 1
        fi
    else
        echo "Skipping remote setup."
    fi
else
    echo "${BLUE}No remote configured. Setting up now...${NC}"
    if [ -f "$SCRIPT_DIR/SETUP_GITHUB_REMOTE.sh" ]; then
        "$SCRIPT_DIR/SETUP_GITHUB_REMOTE.sh"
    else
        echo "${RED}Error: SETUP_GITHUB_REMOTE.sh not found${NC}"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Step 4: YubiKey 2FA Setup"
echo "=========================================="
echo ""

echo "${CYAN}YubiKey 2FA Setup (Manual Process)${NC}"
echo ""
echo "YubiKey 2FA must be set up through GitHub's web interface."
echo "This cannot be automated, but we'll guide you through it."
echo ""
echo "${BLUE}Instructions:${NC}"
echo "1. See detailed guide: SETUP_YUBIKEY_GITHUB_2FA.md"
echo "2. Or follow these quick steps:"
echo ""
echo "   a. Go to: https://github.com/settings/security"
echo "   b. Click 'Edit' next to 'Two-factor authentication'"
echo "   c. Click 'Add security key' or 'Register new device'"
echo "   d. Insert your YubiKey and touch when prompted"
echo "   e. Name it (e.g., 'YubiKey 5C Primary')"
echo "   f. Repeat for your backup YubiKey"
echo ""
read -p "Have you completed YubiKey 2FA setup? (y/n): " yubikey_done

if [ "$yubikey_done" != "y" ] && [ "$yubikey_done" != "Y" ]; then
    echo ""
    echo "${YELLOW}You can set up YubiKey 2FA later.${NC}"
    echo "See: $SCRIPT_DIR/SETUP_YUBIKEY_GITHUB_2FA.md"
    echo ""
    read -p "Continue with setup anyway? (y/n): " continue_anyway
    if [ "$continue_anyway" != "y" ] && [ "$continue_anyway" != "Y" ]; then
        echo "Setup paused. Run this script again when ready."
        exit 0
    fi
fi

echo ""
echo "=========================================="
echo "Step 5: Verification"
echo "=========================================="
echo ""

# Verify Git identity
echo "${BLUE}Verifying Git configuration...${NC}"
GIT_NAME=$(git config --global user.name 2>/dev/null || echo "")
GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")

if [ -n "$GIT_NAME" ] && [ -n "$GIT_EMAIL" ]; then
    echo "${GREEN}✓ Git identity:${NC} $GIT_NAME <$GIT_EMAIL>"
else
    echo "${YELLOW}⚠ Git identity not fully configured${NC}"
fi

# Verify SSH
echo ""
echo "${BLUE}Verifying SSH connection...${NC}"
if ssh -T git@github.com 2>&1 | grep -q "Hi\|successfully authenticated"; then
    echo "${GREEN}✓ SSH connection to GitHub working${NC}"
else
    echo "${YELLOW}⚠ SSH connection test inconclusive${NC}"
    echo "   Run manually: ssh -T git@github.com"
fi

# Verify remote
echo ""
echo "${BLUE}Verifying Git remote...${NC}"
REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
if [ -n "$REMOTE" ]; then
    echo "${GREEN}✓ Remote configured:${NC} $REMOTE"
else
    echo "${YELLOW}⚠ No remote configured${NC}"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""

echo "${GREEN}Summary:${NC}"
echo "  ✓ Git user identity configured"
echo "  ✓ SSH keys set up"
echo "  ✓ GitHub remote configured"
if [ "$yubikey_done" = "y" ] || [ "$yubikey_done" = "Y" ]; then
    echo "  ✓ YubiKey 2FA configured"
else
    echo "  ⚠ YubiKey 2FA pending (see SETUP_YUBIKEY_GITHUB_2FA.md)"
fi

echo ""
echo "${BLUE}Next Steps:${NC}"
echo ""
echo "1. ${CYAN}Complete YubiKey 2FA${NC} (if not done):"
echo "   See: SETUP_YUBIKEY_GITHUB_2FA.md"
echo ""
echo "2. ${CYAN}Create initial commit${NC} (optional):"
echo "   git add ."
echo "   git commit -m 'Initial commit'"
echo "   ./git_safe_push.sh"
echo ""
echo "3. ${CYAN}Use helper scripts for safe Git operations:${NC}"
echo "   ./git_safe_commit.sh    # Safe commit with checks"
echo "   ./git_safe_branch.sh    # Safe branch creation"
echo "   ./git_safe_push.sh      # Safe push with pre-checks"
echo ""
echo "4. ${CYAN}Read the complete guide:${NC}"
echo "   See: GIT_COMPLETE_SETUP_GUIDE.md"
echo ""

echo "${GREEN}You're all set! Happy coding!${NC}"
echo ""
