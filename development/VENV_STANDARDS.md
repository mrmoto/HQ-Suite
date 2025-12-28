# Virtual Environment Standards for Construction Suite

## Overview

All Python applications in the Construction Suite ecosystem **MUST** have their own isolated virtual environment (`.venv`). This document defines the standards and requirements for managing virtual environments across the suite.

## Requirements

### 1. Every App Must Have Its Own `.venv`

**Rule**: Each Python application in `apps/` must maintain its own `.venv/` directory.

**Location**: `apps/{app_name}/.venv/`

**Rationale**:
- Dependency isolation prevents version conflicts
- Independent updates and maintenance
- Clear boundaries between applications
- Team collaboration without conflicts

### 2. Automatic Activation with direnv

**Rule**: All apps use direnv for automatic virtual environment activation.

**Implementation**:
- Each app directory contains a `.envrc` file
- direnv automatically activates `.venv` when you `cd` into the directory
- No manual `source .venv/bin/activate` needed

**Setup**:
```bash
# Install direnv (one-time, system-wide)
brew install direnv

# Add to ~/.zshrc (already done)
eval "$(direnv hook zsh)"

# Allow direnv in each app directory (one-time per app)
cd apps/digidoc
direnv allow
```

### 3. Requirements Files

**Rule**: Each app must have its own requirements file(s).

**Structure**:
- `apps/{app_name}/requirements.txt` - Production dependencies
- `apps/{app_name}/requirements-dev.txt` - Development dependencies (optional, app-specific)
- `development/requirements-dev.txt` - **Suite-wide development tools** (shared)

**Installation**:
```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (app-specific)
pip install -r requirements-dev.txt  # if exists

# Suite-wide development tools
pip install -r ../../development/requirements-dev.txt
```

### 4. .gitignore Requirements

**Rule**: All `.gitignore` files must exclude virtual environments.

**Required Patterns**:
```
# Virtual environments
.venv/
venv/
ENV/
env/
__pycache__/
*.py[cod]
*.egg-info/
```

**Location**: `apps/{app_name}/.gitignore`

### 5. Creating a New App

**When adding a new Python app to the suite:**

1. **Create app directory structure**:
   ```bash
   mkdir -p apps/new_app
   cd apps/new_app
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv .venv
   ```

3. **Create `.envrc` file**:
   ```bash
   cat > .envrc << 'EOF'
   # New App - Automatic Virtual Environment Activation
   if [ ! -d .venv ]; then
       echo "Creating .venv for new_app..."
       python3 -m venv .venv
   fi
   source .venv/bin/activate
   if [ -f .env ]; then
       dotenv
   fi
   EOF
   ```

4. **Allow direnv**:
   ```bash
   direnv allow
   ```

5. **Create requirements.txt**:
   ```bash
   # Activate venv (automatic with direnv)
   pip install --upgrade pip
   # Install your app dependencies
   pip install package1 package2
   pip freeze > requirements.txt
   ```

6. **Install suite-wide dev tools**:
   ```bash
   pip install -r ../../development/requirements-dev.txt
   ```

7. **Create/update .gitignore**:
   ```bash
   # Add Python venv patterns (see section 4)
   ```

8. **Update `development/requirements-dev.txt`**:
   - If the new app introduces new development tools, add them to `development/requirements-dev.txt`
   - Document why the tool is needed

### 6. Updating Suite-Wide Development Tools

**When adding new development tools to `development/requirements-dev.txt`:**

1. **Add the package** to `development/requirements-dev.txt`
2. **Document the purpose** in a comment
3. **Update this document** if the tool requires special setup
4. **Notify team** if the tool requires configuration changes

**Installation in existing apps**:
```bash
cd apps/{app_name}
# direnv auto-activates .venv
pip install -r ../../development/requirements-dev.txt
```

### 7. Best Practices

#### Version Pinning
- **Production**: Pin exact versions in `requirements.txt`
  ```
  redis==7.1.0
  rq==2.6.1
  ```
- **Development**: Use minimum versions in `requirements-dev.txt`
  ```
  pytest>=7.4.0
  black>=23.7.0
  ```

#### Dependency Management
- **Never** install packages globally (outside venv)
- **Always** activate venv before installing (automatic with direnv)
- **Regularly** update dependencies: `pip list --outdated`

#### Environment Variables
- Use `.env` files for local configuration
- Load with `python-dotenv` (included in requirements-dev.txt)
- Never commit `.env` files (already in .gitignore)

#### Testing
- Run tests within the app's venv
- Use `pytest` (from requirements-dev.txt)
- Coverage reports: `pytest --cov`

## Troubleshooting

### direnv Not Activating
```bash
# Check if direnv is installed
which direnv

# Check if hook is in .zshrc
grep "direnv hook" ~/.zshrc

# Reload shell
source ~/.zshrc

# Allow direnv in directory
cd apps/{app_name}
direnv allow
```

### Wrong venv Active
```bash
# Check which Python is active
which python

# Should show: /path/to/apps/{app_name}/.venv/bin/python

# If wrong, check .envrc file exists and is allowed
ls -la .envrc
direnv status
```

### Packages Not Found
```bash
# Verify venv is active
which pip

# Reinstall requirements
pip install -r requirements.txt
pip install -r ../../development/requirements-dev.txt
```

### Moving/Copying venv
**Never move or copy a venv**. Always recreate:
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate  # or rely on direnv
pip install -r requirements.txt
```

## Documentation Requirements

**For AI Agents and Developers:**

When creating or modifying apps:
1. **Always** create `.venv` in the app directory
2. **Always** create `.envrc` for direnv
3. **Always** update `.gitignore` with Python patterns
4. **Always** create `requirements.txt`
5. **Always** install suite-wide dev tools from `development/requirements-dev.txt`
6. **Always** document any new development tools added to `development/requirements-dev.txt`

## Summary Checklist

For each new Python app:
- [ ] `.venv/` directory created
- [ ] `.envrc` file created and allowed
- [ ] `requirements.txt` created with app dependencies
- [ ] `.gitignore` includes Python venv patterns
- [ ] Suite-wide dev tools installed: `pip install -r ../../development/requirements-dev.txt`
- [ ] `development/requirements-dev.txt` updated if new tools added
- [ ] README documents venv setup

---

**Last Updated**: 2025-12-24  
**Maintained By**: Construction Suite Development Team

