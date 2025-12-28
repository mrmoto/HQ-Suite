# Complete Git and GitHub Setup Guide

## Overview

This guide provides comprehensive instructions for setting up Git and GitHub with SSH keys and YubiKey 2FA. It covers everything from initial configuration to daily Git operations.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Detailed Setup Steps](#detailed-setup-steps)
3. [Helper Scripts](#helper-scripts)
4. [Daily Git Workflow](#daily-git-workflow)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

## Quick Start

### Option 1: Automated Setup (Recommended)

Run the master setup script to configure everything:

```bash
./SETUP_GIT_AND_GITHUB.sh
```

This script will guide you through:
- Git user identity configuration
- SSH key generation and GitHub setup
- GitHub remote repository configuration
- YubiKey 2FA setup instructions

### Option 2: Manual Setup

Follow the detailed steps below for manual configuration.

## Detailed Setup Steps

### Step 1: Configure Git User Identity

Set your name and email for Git commits:

```bash
./SETUP_GIT_IDENTITY.sh
```

Or manually:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main
```

**Verify:**
```bash
git config --global user.name
git config --global user.email
```

### Step 2: Generate SSH Keys

Generate SSH keys for GitHub authentication:

```bash
./SETUP_GITHUB_SSH.sh
```

This script will:
- Generate an ed25519 SSH key (or use existing)
- Add the key to your SSH agent
- Copy the public key to your clipboard
- Guide you through adding it to GitHub
- Test the connection

**Manual alternative:**
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
# Press Enter for default location
# Enter passphrase (recommended) or leave empty
```

**Add to GitHub:**
1. Copy public key: `cat ~/.ssh/id_ed25519.pub | pbcopy`
2. Go to: https://github.com/settings/keys
3. Click "New SSH key"
4. Paste key and save

**Test connection:**
```bash
ssh -T git@github.com
# Should see: "Hi username! You've successfully authenticated..."
```

### Step 3: Configure GitHub Remote

Set up your GitHub repository remote:

```bash
./SETUP_GITHUB_REMOTE.sh
```

This will:
- Prompt for GitHub username and repository name
- Configure the remote URL
- Test the connection
- Optionally push your code

**Manual alternative:**
```bash
git remote add origin git@github.com:username/repo.git
# Or update existing:
git remote set-url origin git@github.com:username/repo.git
```

**Verify:**
```bash
git remote -v
```

### Step 4: Set Up YubiKey 2FA

Follow the comprehensive guide:

```bash
# Open the guide
open SETUP_YUBIKEY_GITHUB_2FA.md
# Or view in terminal:
cat SETUP_YUBIKEY_GITHUB_2FA.md
```

**Quick steps:**
1. Go to: https://github.com/settings/security
2. Click "Edit" next to "Two-factor authentication"
3. Click "Add security key" or "Register new device"
4. Insert YubiKey and touch when prompted
5. Name it (e.g., "YubiKey 5C Primary")
6. Repeat for backup YubiKey

**Important:** Register both YubiKeys for redundancy!

## Helper Scripts

### git_safe_commit.sh

Safely commit changes with pre-checks:

```bash
./git_safe_commit.sh
```

Features:
- Shows what will be committed
- Checks for uncommitted changes
- Prompts for confirmation
- Validates commit message

### git_safe_branch.sh

Safely create a new branch:

```bash
./git_safe_branch.sh
```

Features:
- Checks for uncommitted changes
- Optionally stashes changes
- Creates backup branch of current state
- Switches to new branch

### git_safe_push.sh

Safely push to GitHub with pre-checks:

```bash
./git_safe_push.sh
```

Features:
- Checks for uncommitted changes
- Verifies remote connection
- Checks for remote commits (warns about conflicts)
- Shows what will be pushed
- Confirms before pushing

## Daily Git Workflow

### Making Changes

1. **Check status:**
   ```bash
   git status
   ```

2. **Stage changes:**
   ```bash
   git add <file>
   # Or stage all:
   git add .
   ```

3. **Commit:**
   ```bash
   ./git_safe_commit.sh
   # Or manually:
   git commit -m "Descriptive commit message"
   ```

4. **Push:**
   ```bash
   ./git_safe_push.sh
   # Or manually:
   git push origin main
   ```

### Creating a Branch

```bash
./git_safe_branch.sh
# Or manually:
git checkout -b feature-name
```

### Switching Branches

```bash
git checkout branch-name
# Or with Git 2.23+:
git switch branch-name
```

### Pulling Changes

```bash
git pull origin main
# Or just:
git pull
```

### Viewing History

```bash
git log --oneline
git log --graph --oneline --all
```

## Troubleshooting

### SSH Connection Issues

**Problem:** `Permission denied (publickey)`

**Solutions:**
1. Verify SSH key is added to GitHub:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # Compare with keys at: https://github.com/settings/keys
   ```

2. Test SSH connection:
   ```bash
   ssh -T git@github.com
   ```

3. Check SSH agent:
   ```bash
   ssh-add -l
   # If empty, add key:
   ssh-add ~/.ssh/id_ed25519
   ```

4. Verify SSH config:
   ```bash
   cat ~/.ssh/config
   # Should have GitHub configuration
   ```

5. Re-run SSH setup:
   ```bash
   ./SETUP_GITHUB_SSH.sh
   ```

### Git Identity Not Set

**Problem:** Commits show wrong name/email

**Solution:**
```bash
./SETUP_GIT_IDENTITY.sh
# Or manually:
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Remote Not Configured

**Problem:** `fatal: no upstream branch`

**Solution:**
```bash
./SETUP_GITHUB_REMOTE.sh
# Or manually:
git remote add origin git@github.com:username/repo.git
git push -u origin main
```

### Push Conflicts

**Problem:** `Updates were rejected because the remote contains work...`

**Solution:**
```bash
# Pull first, then push:
git pull origin main
# Resolve any conflicts, then:
git push origin main
```

### YubiKey 2FA Issues

**Problem:** YubiKey not recognized during GitHub login

**Solutions:**
1. Try different USB port
2. Try different browser (Chrome has best support)
3. Check YubiKey Manager:
   ```bash
   brew install ykman
   ykman info
   ```
4. See detailed guide: `SETUP_YUBIKEY_GITHUB_2FA.md`

### Git Repository Not Found

**Problem:** `Repository not found` when pushing

**Solutions:**
1. Verify repository exists on GitHub
2. Check repository name and username
3. Verify SSH key has access
4. Check repository visibility (public/private)

## Best Practices

### Commit Messages

- Use clear, descriptive messages
- Start with a verb (e.g., "Add", "Fix", "Update")
- Keep first line under 50 characters
- Add details in body if needed

**Good examples:**
```
Add OCR service for receipt processing
Fix date parsing in receipt extractor
Update confidence scoring algorithm
```

**Bad examples:**
```
fix
changes
update
```

### Branch Naming

Use descriptive branch names:

- `feature/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation

**Examples:**
```
feature/ocr-service
fix/receipt-date-parsing
refactor/confidence-scorer
```

### When to Commit

- Commit related changes together
- Commit working code (don't commit broken code)
- Commit frequently (small, logical commits)
- Commit before major refactoring

### When to Push

- Push after completing a feature
- Push before switching branches (if sharing)
- Push at end of work session
- Don't push broken code

### Using Helper Scripts

Always use helper scripts for safety:
- `./git_safe_commit.sh` - Prevents accidental commits
- `./git_safe_branch.sh` - Protects current work
- `./git_safe_push.sh` - Prevents push conflicts

### Security

- **Never commit secrets:** Use `.env` files (already in `.gitignore`)
- **Use SSH keys:** More secure than HTTPS tokens
- **Enable YubiKey 2FA:** Protects your GitHub account
- **Keep keys secure:** Don't share private keys

### Backup Strategy

- **GitHub remote:** Your code is backed up on GitHub
- **Local commits:** Commit frequently
- **YubiKey backup:** Register both YubiKeys
- **Recovery codes:** Save GitHub 2FA recovery codes

## Configuration Files

### ~/.gitconfig

Global Git configuration:
```ini
[user]
    name = Your Name
    email = your.email@example.com
[init]
    defaultBranch = main
```

### ~/.ssh/config

SSH configuration for GitHub:
```
Host github.com
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/id_ed25519
```

## Useful Git Commands

### Status and Information

```bash
git status                    # Show working directory status
git log --oneline             # Show commit history
git log --graph --all         # Show branch graph
git diff                      # Show changes
git diff --staged             # Show staged changes
```

### Branching

```bash
git branch                    # List branches
git branch -a                 # List all branches (including remote)
git checkout -b new-branch    # Create and switch to branch
git branch -d branch-name    # Delete branch (merged)
git branch -D branch-name    # Force delete branch
```

### Remote Operations

```bash
git remote -v                 # Show remotes
git fetch origin              # Fetch from remote
git pull origin main          # Pull and merge
git push origin main          # Push to remote
git push -u origin main       # Push and set upstream
```

### Undoing Changes

```bash
git restore <file>            # Discard changes in working directory
git restore --staged <file>   # Unstage file
git reset HEAD~1             # Undo last commit (keep changes)
git reset --hard HEAD~1      # Undo last commit (discard changes)
```

**Warning:** Be careful with `reset --hard` - it discards changes!

## Additional Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub SSH Setup](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [GitHub 2FA](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa)
- [YubiKey Setup](https://www.yubico.com/setup/)

## Getting Help

If you encounter issues:

1. **Check this guide's troubleshooting section**
2. **Review the specific setup guide:**
   - `SETUP_YUBIKEY_GITHUB_2FA.md` - For YubiKey issues
   - `SETUP_GITHUB_SSH.sh` - For SSH issues
3. **Check Git status:**
   ```bash
   git status
   git remote -v
   ssh -T git@github.com
   ```
4. **Re-run setup scripts** if needed

## Summary

You now have:
- ✅ Git user identity configured
- ✅ SSH keys set up for GitHub
- ✅ GitHub remote configured
- ✅ YubiKey 2FA for account protection
- ✅ Helper scripts for safe Git operations
- ✅ Complete documentation

Happy coding! 🚀
