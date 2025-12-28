# Terminal Customization Guide

**Purpose**: Guide for customizing the Cursor IDE terminal (ZSH) to improve productivity and readability.

**Scope**: Ecosystem-level development tool configuration.

## Goals

1. **Remove or abbreviate username** in ZSH prompt to save space
2. **Enable color coding per command** for easier reading of code and commands

## Solution Overview

These customizations are done at the **shell level** (`~/.zshrc`), not via Cursor extensions. Cursor uses your system's terminal, so changes apply automatically.

## 1. Customize ZSH Prompt (Remove/Abbreviate Username)

### Option A: Simple Custom Prompt

Edit `~/.zshrc` and add:

```bash
# Show only directory and prompt symbol
export PS1="%1~ %# "
```

Or with colors:

```bash
# Green directory, white prompt
export PS1="%F{green}%1~%f %# "
```

### Option B: Use a Prompt Framework (Recommended)

#### Starship (Cross-Shell, Fast, Highly Configurable)

**Installation:**

```bash
curl -sS https://starship.rs/install.sh | sh
```

**Add to `~/.zshrc`:**

```bash
eval "$(starship init zsh)"
```

**Create `~/.config/starship.toml`:**

```toml
[username]
show_always = false  # Hide username
format = "[$user]($style) "

[directory]
truncation_length = 3
truncate_to_repo = true
```

#### Powerlevel10k (If Using Oh My Zsh)

**Installation:**

```bash
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
```

**In `~/.zshrc`:**

```bash
ZSH_THEME="powerlevel10k/powerlevel10k"
```

Then run `p10k configure` to hide the username.

## 2. Enable Command Color Coding

### zsh-syntax-highlighting

This plugin provides real-time syntax highlighting as you type commands.

**Installation:**

```bash
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

**Add to `~/.zshrc` plugins array:**

```bash
plugins=(... zsh-syntax-highlighting)
```

**Must be sourced last in `~/.zshrc`:**

```bash
source ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
```

**What it highlights:**
- ✅ Valid commands → **Green**
- ❌ Invalid commands → **Red**
- 📁 Paths → **Cyan**
- 🔧 Built-ins → Different colors
- 🔑 Keywords → Highlighted appropriately

**Customize colors (optional):**

```bash
ZSH_HIGHLIGHT_STYLES[command]='fg=green,bold'
ZSH_HIGHLIGHT_STYLES[builtin]='fg=magenta'
ZSH_HIGHLIGHT_STYLES[path]='fg=cyan,underline'
```

## Quick Setup Script

Run this to set up both Starship and zsh-syntax-highlighting:

# Install Starship
curl -sS https://starship.rs/install.sh | sh

# Install zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

# Add to ~/.zshrc
cat >> ~/.zshrc << 'EOF'

# Starship prompt
eval "$(starship init zsh)"

# zsh-syntax-highlighting (must be last)
source ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
EOF

# Reload shell configuration
source ~/.zshrc

## Applying Changes

After making modifications to `~/.zshrc`:

1. **Restart terminal** in Cursor, or
2. **Reload configuration:**
   ```bash
   source ~/.zshrc
   ```

## Cursor-Specific Notes

- ✅ **No Cursor extension needed** - Changes are at the shell level
- ✅ **Works automatically** - Cursor uses your system's terminal
- ✅ **Persists across sessions** - Changes are in `~/.zshrc`
- ✅ **Applies to all terminals** - Not just Cursor

## Recommended Setup

1. **Install Starship** for a clean, configurable prompt
2. **Install zsh-syntax-highlighting** for command color coding
3. **Configure both** in `~/.zshrc`

**Why Starship?**
- ⚡ Fast and lightweight
- 🎨 Highly customizable
- 🔄 Cross-shell compatible (works with bash, fish, etc.)
- 📦 Easy to configure via TOML file
- 🎯 Modern, clean appearance

## Troubleshooting

### Prompt not changing
- Ensure changes are in `~/.zshrc` (not `~/.zprofile` or `~/.bashrc`)
- Run `source ~/.zshrc` or restart terminal
- Check for conflicting prompt configurations

### Syntax highlighting not working
- Ensure `zsh-syntax-highlighting` is sourced **last** in `~/.zshrc`
- Verify plugin is installed in correct directory
- Check that plugin is in the `plugins` array if using Oh My Zsh

### Starship not appearing
- Verify installation: `which starship`
- Check `~/.zshrc` has `eval "$(starship init zsh)"`
- Ensure Starship is in your PATH

## Additional Resources

- [Starship Documentation](https://starship.rs/)
- [zsh-syntax-highlighting GitHub](https://github.com/zsh-users/zsh-syntax-highlighting)
- [Powerlevel10k GitHub](https://github.com/romkatv/powerlevel10k)