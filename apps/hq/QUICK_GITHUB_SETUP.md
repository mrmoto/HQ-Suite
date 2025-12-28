# Quick GitHub Setup Guide

## Fastest Method: Personal Access Token

### Step 1: Create Token on GitHub

1. Go to: **https://github.com/settings/tokens**
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Fill in:
   - **Note:** `HQ Development`
   - **Expiration:** 90 days (or your preference)
   - **Scopes:** Check ✅ **`repo`** (Full control of private repositories)
4. Click **"Generate token"**
5. **⚠️ COPY THE TOKEN NOW** - You won't see it again!

### Step 2: Run Setup Script

```bash
./SETUP_GITHUB_TOKEN.sh
```

The script will:
- Ask for your GitHub username
- Ask for the token you just created
- Ask for your repository name
- Configure Git to use the token
- Test the connection

### Step 3: Create Repository on GitHub

If you haven't created the repository yet:

1. Go to: **https://github.com/new**
2. Repository name: `hq` (or your choice)
3. **Don't** initialize with README, .gitignore, or license
4. Click **"Create repository"**
5. Copy the repository URL

### Step 4: Connect and Push

The setup script will handle this, or manually:

```bash
# If repository already exists on GitHub
git remote add origin https://<YOUR_TOKEN>@github.com/<username>/<repo>.git

# Push your code
git push -u origin main
```

## Alternative: SSH Keys (More Secure)

If you prefer SSH (no password prompts after setup):

```bash
./SETUP_GITHUB_SSH.sh
```

This will:
- Generate SSH key
- Add it to SSH agent
- Copy public key to clipboard
- Guide you to add it to GitHub
- Test the connection

## Configure Git User (Required First)

Before committing, set your name and email:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Troubleshooting

### "Repository not found"
- Make sure repository exists on GitHub
- Check you have access to it
- Verify the repository name is correct

### "Permission denied"
- Check your token has `repo` scope
- Verify token hasn't expired
- Make sure you copied the full token

### "Authentication failed"
- For HTTPS: Re-enter token
- For SSH: Check key was added to GitHub
