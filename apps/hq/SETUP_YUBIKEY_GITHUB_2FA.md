# YubiKey GitHub 2FA Setup Guide

## Overview

This guide walks you through setting up your YubiKey 5C (and backup YubiKey) as hardware security keys for GitHub account two-factor authentication. This provides hardware-backed protection for your GitHub account login.

## Prerequisites

- YubiKey 5C (primary)
- YubiKey 5C (backup) - recommended
- GitHub account
- Web browser (Chrome, Firefox, Safari, or Edge)
- YubiKey Manager installed (optional, for verification)

## Why Use YubiKey for GitHub 2FA?

- **Hardware-backed security**: Keys stored on physical device
- **Phishing protection**: WebAuthn prevents phishing attacks
- **No codes to enter**: Just touch the YubiKey
- **Backup support**: Register multiple YubiKeys for redundancy

## Step-by-Step Setup

### Step 1: Access GitHub Security Settings

1. Log in to GitHub: https://github.com
2. Click your profile picture (top right)
3. Click **Settings**
4. In the left sidebar, click **Security**
5. Scroll down to **Two-factor authentication** section
6. Click **Edit** next to "Two-factor authentication"

### Step 2: Enable 2FA (If Not Already Enabled)

If you haven't enabled 2FA yet:

1. Click **Enable two-factor authentication**
2. Choose **Set up using a security key** (or use authenticator app first, then add security key)
3. Follow the prompts to register your first security key

If 2FA is already enabled with an authenticator app:

1. You'll see your current 2FA methods
2. Look for **Security keys** section
3. Click **Add** or **Register new device**

### Step 3: Register Primary YubiKey

1. **Insert your primary YubiKey** into a USB-C port
2. Click **Register a new security key** or **Add security key**
3. GitHub will prompt you to:
   - **Name the key**: Enter a descriptive name (e.g., "YubiKey 5C Primary" or "MacBook Pro YubiKey")
   - **Touch the YubiKey**: When prompted, physically touch the YubiKey button
4. Wait for confirmation that the key was registered
5. You should see your YubiKey listed under "Security keys"

### Step 4: Register Backup YubiKey

1. **Insert your backup YubiKey** into a USB-C port
2. Click **Register a new security key** again
3. Name it (e.g., "YubiKey 5C Backup")
4. **Touch the YubiKey** when prompted
5. Wait for confirmation

### Step 5: Verify Both Keys Are Registered

You should now see:
- Primary YubiKey listed
- Backup YubiKey listed
- Both under "Security keys" section

## Testing Your Setup

### Test Login with YubiKey

1. **Log out** of GitHub (or use incognito/private window)
2. Go to https://github.com/login
3. Enter your username and password
4. When prompted for 2FA:
   - Insert your YubiKey
   - Touch the YubiKey when prompted
5. You should be logged in successfully

### Test with Backup YubiKey

1. Log out again
2. Log in with username/password
3. When prompted for 2FA:
   - Insert your **backup** YubiKey
   - Touch it when prompted
4. Verify login works with backup key too

## Using YubiKey 2FA

### Normal Login Flow

1. Enter username and password on GitHub
2. GitHub prompts for 2FA
3. Insert YubiKey (either one works)
4. Touch YubiKey when prompted
5. Logged in!

### Git Operations

**Important**: YubiKey 2FA protects your **GitHub account login**, not Git operations directly.

- Git operations (push, pull) use **SSH keys** (separate from 2FA)
- YubiKey 2FA is for web login, API access, and account changes
- You won't need to touch YubiKey for normal `git push` operations

## Troubleshooting

### YubiKey Not Recognized

**Symptoms**: Browser doesn't detect YubiKey

**Solutions**:
1. **Try a different USB port** (some ports may not work)
2. **Try a different browser** (Chrome, Firefox, Safari)
3. **Check YubiKey Manager**: Install and verify YubiKey is working
   ```bash
   brew install ykman
   ykman info
   ```
4. **Clean the USB-C port**: Dust or debris can interfere
5. **Try the backup YubiKey**: Verify if it's a hardware issue

### "Touch Required" Not Appearing

**Symptoms**: YubiKey inserted but no touch prompt

**Solutions**:
1. **Check browser permissions**: Some browsers need permission for security keys
2. **Try different browser**: Chrome has best WebAuthn support
3. **Check YubiKey mode**: Ensure YubiKey is in FIDO2 mode (default)
4. **Update browser**: Ensure browser is up to date

### Can't Register Second YubiKey

**Symptoms**: First key works, second key registration fails

**Solutions**:
1. **Remove and re-insert**: Unplug and plug back in
2. **Try different port**: USB port may be issue
3. **Clear browser cache**: Sometimes helps with WebAuthn
4. **Try incognito mode**: Eliminates extension interference

### Lost YubiKey

**If you lose your primary YubiKey**:

1. **Use your backup YubiKey** to log in
2. Go to GitHub Settings → Security → Two-factor authentication
3. Remove the lost YubiKey from your account
4. Register a new YubiKey as replacement

**If you lose both YubiKeys**:

1. Use your **recovery codes** (you should have saved these when enabling 2FA)
2. Log in with recovery code
3. Disable 2FA temporarily
4. Register new YubiKeys
5. Re-enable 2FA

**Important**: Always keep recovery codes in a safe place!

## Best Practices

### 1. Register Both YubiKeys
- Always register both YubiKeys
- Test both keys after registration
- Keep backup key in safe location

### 2. Save Recovery Codes
- When enabling 2FA, GitHub provides recovery codes
- Save these in a secure password manager
- Print and store in safe physical location
- Never store recovery codes in the same place as your YubiKeys

### 3. Test Regularly
- Periodically test both YubiKeys
- Verify backup key still works
- Test recovery codes (but don't use them unless needed)

### 4. Keep YubiKeys Secure
- Don't leave YubiKeys unattended
- Keep backup key in different location than primary
- Consider a safe or lockbox for backup key

### 5. Update YubiKey Firmware
- Periodically check for YubiKey firmware updates
- Use YubiKey Manager to update:
  ```bash
  ykman update
  ```

## Verification Commands

### Check YubiKey Status

```bash
# Install YubiKey Manager (if not installed)
brew install ykman

# Check YubiKey info
ykman info

# Check FIDO2 application
ykman fido info
```

### Verify GitHub 2FA Status

1. Go to: https://github.com/settings/security
2. Check "Two-factor authentication" section
3. Verify both YubiKeys are listed under "Security keys"

## Security Notes

### What YubiKey 2FA Protects

- ✅ GitHub web login
- ✅ GitHub API access
- ✅ Account settings changes
- ✅ Repository access (when using HTTPS with token)

### What YubiKey 2FA Does NOT Protect

- ❌ Git operations via SSH (uses SSH keys, not 2FA)
- ❌ Local Git commits (no authentication needed)
- ❌ Git operations if SSH keys are compromised

**For Git operations**: Use SSH keys (separate setup) for authentication.

## Next Steps

After setting up YubiKey 2FA:

1. ✅ **Test both YubiKeys** - Verify both work for login
2. ✅ **Save recovery codes** - Store securely
3. ✅ **Set up SSH keys** - For Git operations (see SETUP_GITHUB_SSH.sh)
4. ✅ **Configure GitHub remote** - Set up repository (see SETUP_GITHUB_REMOTE.sh)

## Additional Resources

- [GitHub 2FA Documentation](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa)
- [YubiKey Setup Guide](https://www.yubico.com/setup/)
- [WebAuthn Specification](https://www.w3.org/TR/webauthn-2/)

## Summary

You've now set up:
- ✅ Primary YubiKey registered for GitHub 2FA
- ✅ Backup YubiKey registered for redundancy
- ✅ Hardware-backed account protection
- ✅ Phishing-resistant authentication

Your GitHub account is now protected with hardware security keys!
