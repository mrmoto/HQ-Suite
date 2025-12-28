# Development Directory

This directory contains development-specific files, tools, and configurations used across the Construction Suite ecosystem.

## Purpose

The `development/` directory serves as the **single source of truth** for:
- Development tooling and dependencies
- Testing frameworks and utilities
- Automation scripts and configurations
- Development standards and documentation
- Skeleton/Phase 1 development configurations

## Structure

```
development/
├── README.md                    # This file
├── requirements-dev.txt         # Suite-wide development dependencies
├── VENV_STANDARDS.md            # Virtual environment standards
├── skeleton.yaml                # Skeleton development configuration
├── test_skeleton_flow.py        # Skeleton testing script
├── TESTING_SKELETON.md          # Skeleton testing guide
└── REDIS_INSTALLATION.md        # Redis setup guide
```

## Key Files

### `requirements-dev.txt`

**Purpose**: Suite-wide development dependencies (testing, linting, tooling)

**Usage**:
```bash
cd apps/{app_name}
# direnv auto-activates .venv
pip install -r ../../development/requirements-dev.txt
```

**Contents**:
- Testing frameworks (pytest, pytest-cov, etc.)
- Code quality tools (black, flake8, mypy, etc.)
- Development utilities (ipython, pre-commit, etc.)
- Documentation tools (sphinx)
- Security tools (bandit, safety)

**Important**: This is for **development tools only**. App-specific dependencies go in each app's `requirements.txt`.

### `VENV_STANDARDS.md`

**Purpose**: Standards and requirements for virtual environment management

**Key Rules**:
- Every app must have its own `.venv`
- Use direnv for automatic activation
- All apps must have `.gitignore` with Python patterns
- New apps must update `requirements-dev.txt` if adding new dev tools

**Read this before creating new apps!**

### `skeleton.yaml`

**Purpose**: Single source of truth for hardcoded test values during skeleton/Phase 1 development

**Usage**: See `development/README.md` in the main development directory for details.

**Location**: `Construction_Suite/development/skeleton.yaml`

## Adding New Development Tools

When adding a new development tool to the suite:

1. **Add to `requirements-dev.txt`**:
   ```txt
   # Tool Name
   tool-name>=1.0.0  # Brief description
   ```

2. **Update this README** if the tool requires special setup

3. **Update `VENV_STANDARDS.md`** if it affects venv management

4. **Install in existing apps**:
   ```bash
   cd apps/{app_name}
   pip install -r ../../development/requirements-dev.txt
   ```

## Best Practices

### Virtual Environments

- **One venv per app**: Each app in `apps/` has its own `.venv`
- **Automatic activation**: Use direnv (see `VENV_STANDARDS.md`)
- **Never commit venvs**: Always in `.gitignore`

### Dependencies

- **App-specific**: `apps/{app}/requirements.txt`
- **Development tools**: `development/requirements-dev.txt`
- **Version pinning**: Production = exact, Dev = minimum

### Testing

- Use `pytest` (from requirements-dev.txt)
- Run tests within app's venv
- Coverage: `pytest --cov`

### Code Quality

- Format: `black .`
- Lint: `flake8 .`
- Type check: `mypy .`

## Quick Reference

### Setup New App
```bash
cd apps/new_app
python3 -m venv .venv
# Create .envrc (see VENV_STANDARDS.md)
direnv allow
pip install -r requirements.txt
pip install -r ../../development/requirements-dev.txt
```

### Update Dev Tools
```bash
# In development/
# Edit requirements-dev.txt
# Then in each app:
cd apps/{app_name}
pip install -r ../../development/requirements-dev.txt
```

### Run Tests
```bash
cd apps/{app_name}
# direnv auto-activates
pytest
```

## Related Documentation

- `VENV_STANDARDS.md` - Virtual environment standards
- `apps/{app}/README.md` - App-specific documentation
- `shared_documentation/training/AGENT_TRAINING_GUIDE.md` - AI agent guidelines

---

**Last Updated**: 2025-12-24
