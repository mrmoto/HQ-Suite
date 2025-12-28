#!/bin/bash

# GitHub SSH Setup Script
# Sets up SSH keys for GitHub authentication

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "GitHub SSH Key Setup"
echo "=========================================="
echo ""

# Check Git user identity
GIT_NAME=$(git config --global user.name 2>/dev/null || echo "")
GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")

if [ -z "$GIT_NAME" ] || [ -z "$GIT_EMAIL" ]; then
    echo "${YELLOW}Warning: Git user identity not configured${NC}"
    if [ -z "$GIT_NAME" ]; then
        echo "  Name: Not set"
    fi
    if [ -z "$GIT_EMAIL" ]; then
        echo "  Email: Not set"
    fi
    echo ""
    echo "Git identity is recommended for commits. You can set it now or later."
    read -p "Configure Git identity now? (y/n): " config_git
    if [ "$config_git" = "y" ] || [ "$config_git" = "Y" ]; then
        if [ -f "$(dirname "$0")/SETUP_GIT_IDENTITY.sh" ]; then
            "$(dirname "$0")/SETUP_GIT_IDENTITY.sh"
        else
            echo "Please run SETUP_GIT_IDENTITY.sh separately, or configure manually:"
            echo "  git config --global user.name 'Your Name'"
            echo "  git config --global user.email 'your.email@example.com'"
        fi
        echo ""
    fi
fi

# Check for existing SSH keys
if [ -f ~/.ssh/id_ed25519.pub ] || [ -f ~/.ssh/id_rsa.pub ]; then
    echo "${YELLOW}Existing SSH keys found:${NC}"
    ls -la ~/.ssh/id_*.pub 2>/dev/null || true
    echo ""
    read -p "Use existing key or create new? (use/new): " key_choice
    
    if [ "$key_choice" != "new" ]; then
        EXISTING_KEY=$(ls ~/.ssh/id_*.pub 2>/dev/null | head -1)
        echo "Using existing key: $EXISTING_KEY"
    else
        EXISTING_KEY=""
    fi
else
    EXISTING_KEY=""
fi

# Get email for key
if [ -z "$EXISTING_KEY" ]; then
    echo "Enter your GitHub email address:"
    read -p "Email: " github_email
    
    if [ -z "$github_email" ]; then
        echo "${RED}Error: Email required${NC}"
        exit 1
    fi
    
    # Generate SSH key
    echo ""
    echo "Generating SSH key..."
    echo "Press Enter to accept default location (~/.ssh/id_ed25519)"
    echo "Enter a passphrase (recommended) or leave empty:"
    echo ""
    
    ssh-keygen -t ed25519 -C "$github_email"
    
    KEY_FILE=~/.ssh/id_ed25519
else
    KEY_FILE="${EXISTING_KEY%.pub}"
fi

# Start SSH agent
echo ""
echo "Starting SSH agent..."
eval "$(ssh-agent -s)"

# Add key to agent
echo "Adding key to SSH agent..."
if ! ssh-add "$KEY_FILE" 2>/dev/null; then
    echo "${YELLOW}Note: Key may require passphrase entry${NC}"
    ssh-add "$KEY_FILE"
fi
echo "${GREEN}✓ Key added to SSH agent${NC}"

# Setup SSH config for GitHub
SSH_CONFIG=~/.ssh/config
SSH_CONFIG_BACKUP=""

if [ -f "$SSH_CONFIG" ]; then
    # Check if GitHub config already exists
    if grep -q "Host github.com" "$SSH_CONFIG" 2>/dev/null; then
        echo "${YELLOW}GitHub configuration already exists in SSH config${NC}"
        read -p "Update GitHub SSH config? (y/n): " update_config
        if [ "$update_config" = "y" ] || [ "$update_config" = "Y" ]; then
            SSH_CONFIG_BACKUP="${SSH_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
            cp "$SSH_CONFIG" "$SSH_CONFIG_BACKUP"
            echo "${BLUE}Backup created: $SSH_CONFIG_BACKUP${NC}"
            
            # Remove existing GitHub config block
            sed -i.tmp '/^Host github.com$/,/^$/d' "$SSH_CONFIG" 2>/dev/null || \
            sed -i '' '/^Host github.com$/,/^$/d' "$SSH_CONFIG" 2>/dev/null || true
            rm -f "${SSH_CONFIG}.tmp" 2>/dev/null || true
        else
            update_config="n"
        fi
    else
        update_config="y"
    fi
else
    update_config="y"
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
fi

if [ "$update_config" = "y" ] || [ "$update_config" = "Y" ]; then
    echo ""
    echo "Configuring SSH for GitHub..."
    
    # Determine key file path (handle both absolute and relative)
    if [[ "$KEY_FILE" == ~* ]]; then
        KEY_PATH="$KEY_FILE"
    else
        KEY_PATH="~/.ssh/$(basename "$KEY_FILE")"
    fi
    
    # Append GitHub config
    {
        echo ""
        echo "Host github.com"
        echo "  AddKeysToAgent yes"
        echo "  UseKeychain yes"
        echo "  IdentityFile $KEY_PATH"
    } >> "$SSH_CONFIG"
    
    chmod 600 "$SSH_CONFIG"
    echo "${GREEN}✓ SSH config updated${NC}"
fi

# Copy public key to clipboard
PUBLIC_KEY_FILE="${KEY_FILE}.pub"
if [ -f "$PUBLIC_KEY_FILE" ]; then
    echo ""
    echo "Copying public key to clipboard..."
    pbcopy < "$PUBLIC_KEY_FILE"
    echo "${GREEN}✓ Public key copied to clipboard${NC}"
    echo ""
    echo "Your public key:"
    echo "----------------------------------------"
    cat "$PUBLIC_KEY_FILE"
    echo "----------------------------------------"
    echo ""
    echo "${BLUE}Next steps:${NC}"
    echo "1. Go to: https://github.com/settings/keys"
    echo "2. Click 'New SSH key'"
    echo "3. Title: Your computer name (e.g., 'MacBook Pro')"
    echo "4. Key: Paste (already in clipboard) or paste the key above"
    echo "5. Click 'Add SSH key'"
    echo ""
    read -p "Press Enter after you've added the key to GitHub..."

    # Test connection
    echo ""
    echo "Testing GitHub connection..."
    TEST_OUTPUT=$(ssh -T git@github.com 2>&1)
    TEST_EXIT=$?
    
    if [ $TEST_EXIT -eq 0 ] || echo "$TEST_OUTPUT" | grep -q "successfully authenticated"; then
        echo "${GREEN}✓ Successfully authenticated with GitHub!${NC}"
        echo "$TEST_OUTPUT"
    elif echo "$TEST_OUTPUT" | grep -q "Hi"; then
        echo "${GREEN}✓ Authentication successful!${NC}"
        echo "$TEST_OUTPUT"
    elif echo "$TEST_OUTPUT" | grep -q "Permission denied"; then
        echo "${RED}✗ Authentication failed${NC}"
        echo "$TEST_OUTPUT"
        echo ""
        echo "${YELLOW}Troubleshooting:${NC}"
        echo "1. Make sure you added the public key to GitHub"
        echo "2. Check that the key was added correctly"
        echo "3. Try: ssh -T git@github.com"
        exit 1
    else
        echo "${YELLOW}Connection test completed${NC}"
        echo "$TEST_OUTPUT"
        echo ""
        echo "${BLUE}If you see 'Hi username!', authentication is working${NC}"
    fi
    
    echo ""
    echo "=========================================="
    echo "SSH Setup Complete!"
    echo "=========================================="
    echo ""
    echo "${GREEN}Summary:${NC}"
    echo "  ✓ SSH key generated/configured"
    echo "  ✓ Key added to SSH agent"
    if [ "$update_config" = "y" ] || [ "$update_config" = "Y" ]; then
        echo "  ✓ SSH config updated for GitHub"
    fi
    echo "  ✓ GitHub connection tested"
    echo ""
    echo "${BLUE}Next steps:${NC}"
    echo "1. Set up GitHub remote (run SETUP_GITHUB_REMOTE.sh)"
    echo "2. Configure YubiKey 2FA (see SETUP_YUBIKEY_GITHUB_2FA.md)"
    echo ""
    echo "To manually set remote URL:"
    echo "  git remote set-url origin git@github.com:<username>/<repo>.git"
    echo ""
else
    echo "${RED}Error: Public key file not found${NC}"
    echo "Expected: $PUBLIC_KEY_FILE"
    exit 1
fi
