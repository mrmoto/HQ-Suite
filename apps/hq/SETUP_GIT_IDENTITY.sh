#!/bin/bash

# Git User Identity Setup Script
# Configures Git with your name and email for commits

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "Git User Identity Configuration"
echo "=========================================="
echo ""

# Check current configuration
CURRENT_NAME=$(git config --global user.name 2>/dev/null || echo "")
CURRENT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")

if [ -n "$CURRENT_NAME" ] || [ -n "$CURRENT_EMAIL" ]; then
    echo "${YELLOW}Current Git configuration:${NC}"
    if [ -n "$CURRENT_NAME" ]; then
        echo "  Name:  $CURRENT_NAME"
    else
        echo "  Name:  ${RED}Not set${NC}"
    fi
    if [ -n "$CURRENT_EMAIL" ]; then
        echo "  Email: $CURRENT_EMAIL"
    else
        echo "  Email: ${RED}Not set${NC}"
    fi
    echo ""
    read -p "Update configuration? (y/n): " update_choice
    if [ "$update_choice" != "y" ] && [ "$update_choice" != "Y" ]; then
        echo "Configuration unchanged."
        exit 0
    fi
    echo ""
fi

# Get name
if [ -z "$CURRENT_NAME" ] || [ "$update_choice" = "y" ] || [ "$update_choice" = "Y" ]; then
    if [ -n "$CURRENT_NAME" ]; then
        read -p "Enter your name [$CURRENT_NAME]: " git_name
        git_name=${git_name:-$CURRENT_NAME}
    else
        read -p "Enter your name: " git_name
    fi
    
    if [ -z "$git_name" ]; then
        echo "${RED}Error: Name is required${NC}"
        exit 1
    fi
    
    git config --global user.name "$git_name"
    echo "${GREEN}✓ Name set to: $git_name${NC}"
fi

# Get email
if [ -z "$CURRENT_EMAIL" ] || [ "$update_choice" = "y" ] || [ "$update_choice" = "Y" ]; then
    if [ -n "$CURRENT_EMAIL" ]; then
        read -p "Enter your email [$CURRENT_EMAIL]: " git_email
        git_email=${git_email:-$CURRENT_EMAIL}
    else
        read -p "Enter your email: " git_email
    fi
    
    if [ -z "$git_email" ]; then
        echo "${RED}Error: Email is required${NC}"
        exit 1
    fi
    
    # Basic email validation
    if [[ ! "$git_email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        echo "${YELLOW}Warning: Email format may be invalid${NC}"
        read -p "Continue anyway? (y/n): " continue_choice
        if [ "$continue_choice" != "y" ] && [ "$continue_choice" != "Y" ]; then
            exit 1
        fi
    fi
    
    git config --global user.email "$git_email"
    echo "${GREEN}✓ Email set to: $git_email${NC}"
fi

# Set default branch to main
git config --global init.defaultBranch main
echo "${GREEN}✓ Default branch set to: main${NC}"

# Display final configuration
echo ""
echo "=========================================="
echo "Git Configuration Complete"
echo "=========================================="
echo ""
echo "Current configuration:"
echo "  Name:  $(git config --global user.name)"
echo "  Email: $(git config --global user.email)"
echo "  Default branch: $(git config --global init.defaultBranch)"
echo ""
echo "${BLUE}This configuration will be used for all Git commits.${NC}"
echo ""
