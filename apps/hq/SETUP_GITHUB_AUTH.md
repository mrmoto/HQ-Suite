# GitHub Authentication Setup Guide

## Quick Setup Options

### Option 1: HTTPS with Personal Access Token (Easiest - Recommended for Now)

**Best for:** Quick setup, no SSH configuration needed

**Steps:**

1. **Create Personal Access Token on GitHub:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: "HQ Development"
   - Expiration: 90 days (or your preference)
   - Scopes: Check `repo` (full control of private repositories)
   - Click "Generate token"
   - **COPY THE TOKEN** (you won't see it again!)

2. **Use Token When Pushing:**
   ```bash
   git push https://<YOUR_TOKEN>@github.com/<username>/<repo>.git main
   ```
   
   Or configure Git to use token:
   ```bash
   git remote set-url origin https://<YOUR_TOKEN>@github.com/<username>/<repo>.git
   ```

3. **Store Credentials (macOS Keychain):**
   ```bash
   git config --global credential.helper osxkeychain
   ```
   Then on first push, enter:
   - Username: your GitHub username
   - Password: your personal access token (not your GitHub password)

### Option 2: SSH Keys (More Secure - Recommended Long-term)

**Best for:** Secure, no password prompts after setup

**Steps:**

1. **Generate SSH Key:**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
   - Press Enter to accept default location
   - Enter passphrase (optional but recommended)

2. **Add SSH Key to SSH Agent:**
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

3. **Copy Public Key:**
   ```bash
   pbcopy < ~/.ssh/id_ed25519.pub
   ```
   This copies the key to your clipboard.

4. **Add to GitHub:**
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Title: "MacBook Pro" (or your computer name)
   - Key: Paste the copied key
   - Click "Add SSH key"

5. **Test Connection:**
   ```bash
   ssh -T git@github.com
   ```
   Should see: "Hi username! You've successfully authenticated..."

6. **Update Remote URL:**
   ```bash
   git remote set-url origin git@github.com:<username>/<repo>.git
   ```

### Option 3: GitHub CLI (Simplest if Installed)

**Best for:** Easiest authentication flow

```bash
# Install GitHub CLI (if not installed)
brew install gh

# Authenticate
gh auth login

# Follow prompts:
# - GitHub.com
# - HTTPS (or SSH)
# - Login with web browser
# - Authorize
```

## Which Should You Use?

**For Quick Start:** Option 1 (Personal Access Token)
- Fastest to set up
- Works immediately
- Good for getting started

**For Long-term:** Option 2 (SSH Keys)
- More secure
- No password prompts
- Standard for development

**For Convenience:** Option 3 (GitHub CLI)
- Easiest authentication
- Handles everything automatically

## Current Status Check

Run these to see what's already set up:

```bash
# Check for SSH keys
ls -la ~/.ssh/id_*.pub

# Check Git config
git config --global user.name
git config --global user.email

# Check remote URL
git remote -v
```

## Troubleshooting

### "Permission denied" error
- Check your token/key has `repo` permissions
- Verify remote URL is correct
- For SSH: Test with `ssh -T git@github.com`

### "Repository not found" error
- Verify repository exists on GitHub
- Check you have access to the repository
- Verify remote URL matches your repository

### Credentials not saving
```bash
# Enable credential helper
git config --global credential.helper osxkeychain

# Clear stored credentials
git credential-osxkeychain erase
# Then enter: host=github.com
```
