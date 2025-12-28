# Development Best Practices - Construction Suite

**Purpose**: Professional development practices and patterns used across the Construction Suite ecosystem.

**Last Updated**: 2025-12-24

---

## Table of Contents

1. [Virtual Environment Management](#virtual-environment-management)
2. [Dependency Management](#dependency-management)
3. [Code Quality](#code-quality)
4. [Testing Strategy](#testing-strategy)
5. [Git Workflow](#git-workflow)
6. [Documentation Standards](#documentation-standards)
7. [Security Practices](#security-practices)
8. [Performance Considerations](#performance-considerations)
9. [Error Handling](#error-handling)
10. [Configuration Management](#configuration-management)

---

## Virtual Environment Management

### One venv Per App

**Rule**: Every Python application has its own isolated `.venv` directory.

**Location**: `apps/{app_name}/.venv/`

**Benefits**:
- Dependency isolation prevents version conflicts
- Independent updates and maintenance
- Clear boundaries between applications
- Team collaboration without conflicts

### Automatic Activation with direnv

**Setup**: direnv automatically activates the correct venv when you `cd` into an app directory.

**Requirements**:
- direnv installed system-wide (`brew install direnv`)
- Hook added to `~/.zshrc`: `eval "$(direnv hook zsh)"`
- `.envrc` file in each app directory
- `direnv allow` run once per app directory

**Benefits**:
- No manual activation needed
- Prevents "wrong venv" errors
- Automatic environment variable loading
- Seamless directory switching

**See**: `development/VENV_STANDARDS.md` for complete standards.

---

## Dependency Management

### Requirements Files Structure

**App-Specific Dependencies**:
- `apps/{app}/requirements.txt` - Production dependencies (pinned versions)
- `apps/{app}/requirements-dev.txt` - App-specific dev dependencies (optional)

**Suite-Wide Development Tools**:
- `development/requirements-dev.txt` - Testing, linting, tooling (minimum versions)

### Version Pinning Strategy

**Production Dependencies** (`requirements.txt`):
```txt
redis==7.1.0
rq==2.6.1
flask==3.1.2
```
- **Pin exact versions** for reproducibility
- Update carefully with testing

**Development Dependencies** (`requirements-dev.txt`):
```txt
pytest>=7.4.0
black>=23.7.0
mypy>=1.5.0
```
- **Use minimum versions** for flexibility
- Allow patch updates automatically

### Dependency Updates

**Process**:
1. Check outdated packages: `pip list --outdated`
2. Update in isolated branch
3. Run full test suite
4. Update `requirements.txt` with new versions
5. Test in clean environment

**Never**:
- Update all dependencies at once without testing
- Commit `requirements.txt` changes without testing
- Mix production and development dependencies

---

## Code Quality

### Formatting

**Tool**: `black` (from requirements-dev.txt)

**Usage**:
```bash
# Format all Python files
black .

# Check without formatting
black --check .
```

**Configuration**: Use default black settings (88 char line length, no config file needed for MVP)

### Linting

**Primary**: `flake8` (from requirements-dev.txt)

**Usage**:
```bash
flake8 .
```

**Additional**: `pylint` for deeper analysis (optional, from requirements-dev.txt)

### Type Checking

**Tool**: `mypy` (from requirements-dev.txt)

**Usage**:
```bash
mypy .
```

**Strategy**: Start with basic type hints, expand gradually. Don't require 100% coverage initially.

### Import Sorting

**Tool**: `isort` (from requirements-dev.txt)

**Usage**:
```bash
isort .
```

**Integration**: Can be combined with black (black-compatible mode)

### Pre-commit Hooks

**Tool**: `pre-commit` (from requirements-dev.txt)

**Setup** (future enhancement):
```bash
pre-commit install
```

**Benefits**: Automatic formatting/linting before commits

---

## Testing Strategy

### Framework

**Primary**: `pytest` (from requirements-dev.txt)

**Structure**:
```
apps/{app}/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
```

### Test Organization

**Unit Tests**:
- Test individual functions/modules in isolation
- Fast execution
- No external dependencies

**Integration Tests**:
- Test component interactions
- May use test databases/files
- Slower but more realistic

**Test Fixtures**: Use `pytest.fixture` for reusable test data

### Coverage

**Tool**: `pytest-cov` (from requirements-dev.txt)

**Usage**:
```bash
pytest --cov=. --cov-report=html
```

**Target**: Aim for 80%+ coverage on critical paths (not required for MVP)

### Test Execution

**Run all tests**:
```bash
pytest
```

**Run specific test**:
```bash
pytest tests/unit/test_specific.py::test_function
```

**Run with coverage**:
```bash
pytest --cov
```

---

## Git Workflow

### Branch Strategy

**Main Branch**: `main` (or `master`)

**Feature Branches**: `feature/{feature-name}`
- Short-lived branches for features
- Merge to main after review/testing

**Naming Conventions**:
- `feature/queue-abstraction`
- `bugfix/preprocessing-error`
- `refactor/config-loading`

### Commit Messages

**Format**: Conventional Commits (recommended)
```
type(scope): subject

body (optional)

footer (optional)
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

**Example**:
```
feat(queue): add RQ adapter implementation

Implements RQAdapter for Redis Queue integration.
Includes task enqueueing, status checking, and error handling.

Closes #123
```

### .gitignore Best Practices

**Always Ignore**:
- Virtual environments (`.venv/`, `venv/`, etc.)
- Python cache (`__pycache__/`, `*.pyc`)
- IDE files (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`)
- Environment files (`.env`)
- Build artifacts (`dist/`, `build/`, `*.egg-info/`)
- Test artifacts (`.pytest_cache/`, `.coverage`)

**See**: Each app's `.gitignore` for app-specific patterns

---

## Documentation Standards

### Code Documentation

**Docstrings**: Use Google-style docstrings
```python
def process_receipt(file_path: str, queue_id: str) -> dict:
    """Process a receipt through the full pipeline.
    
    Args:
        file_path: Path to the receipt image file
        queue_id: Unique identifier for this queue item
        
    Returns:
        Dict with processing results and status
        
    Raises:
        FileNotFoundError: If file_path doesn't exist
    """
```

**Comments**: Explain "why", not "what"
- Good: `# Use Otsu thresholding for better contrast on scanned documents`
- Bad: `# Apply threshold`

### README Files

**Every app must have**:
- `apps/{app}/README.md` - App overview, setup, usage

**Should include**:
- Installation instructions
- Configuration setup
- Running the application
- Development setup (venv, dependencies)
- Testing instructions

### Architecture Documentation

**Location**: `shared_documentation/architecture/`

**Key Documents**:
- `MASTER_ARCHITECTURE.md` - Single source of truth
- `ARCHITECTURE_CHANGELOG.md` - Version history

**Rule**: Update architecture docs when making architectural changes

---

## Security Practices

### Secrets Management

**Never commit**:
- API keys
- Database passwords
- Authentication tokens
- Private keys

**Use**:
- `.env` files (in `.gitignore`)
- Environment variables
- Configuration files with secrets excluded from git

### Dependency Security

**Tool**: `safety` (from requirements-dev.txt)

**Usage**:
```bash
safety check
```

**Process**: Run regularly to check for vulnerable dependencies

### Code Security

**Tool**: `bandit` (from requirements-dev.txt)

**Usage**:
```bash
bandit -r .
```

**Focus**: SQL injection, shell injection, hardcoded secrets

---

## Performance Considerations

### Profiling

**Tool**: `py-spy` (from requirements-dev.txt)

**Usage**:
```bash
py-spy record -o profile.svg -- python script.py
```

**Memory Profiling**: `memory-profiler` (from requirements-dev.txt)

### Optimization Principles

1. **Measure first**: Profile before optimizing
2. **Bottlenecks**: Focus on actual bottlenecks, not micro-optimizations
3. **Readability**: Don't sacrifice readability for minor performance gains
4. **Caching**: Use caching for expensive operations
5. **Async**: Consider async for I/O-bound operations

---

## Error Handling

### Exception Strategy

**Be Specific**: Catch specific exceptions, not bare `except:`
```python
# Good
try:
    process_file(path)
except FileNotFoundError:
    logger.error(f"File not found: {path}")
except PermissionError:
    logger.error(f"Permission denied: {path}")

# Bad
try:
    process_file(path)
except:
    pass
```

**Log Errors**: Always log errors with context
```python
logger.error(f"Failed to process {queue_id}: {error}", exc_info=True)
```

### Error Recovery

**Retry Logic**: Use exponential backoff for transient errors
**Graceful Degradation**: Continue operation when possible
**User Feedback**: Provide clear error messages

---

## Configuration Management

### Configuration Files

**Rule**: No hardcoded values (from MASTER_ARCHITECTURE.md)

**Structure**:
- `apps/{app}/config.yaml` - App configuration
- Environment variables override config values
- Pattern: `{APP}_{SECTION}_{KEY}`

### Configuration Loading

**Process**:
1. Load default config from YAML
2. Override with environment variables
3. Validate required values
4. Expand paths to absolute paths (e.g., `~/Dropbox/...` → `/Users/username/Dropbox/...`)
   - Use `os.path.expanduser()` or equivalent
   - All apps use absolute paths internally after expansion
   - Required for cross-system compatibility

**See**: `apps/digidoc/digidoc_config.yaml` for example

### Path Handling

**CRITICAL**: Path expansion is required for cross-system compatibility.

**Requirements**:
- Configuration paths with `~` must be expanded to absolute paths during configuration loading
- All apps use absolute paths internally after expansion
- API `file_path` parameters must be absolute paths
- Path expansion ensures compatibility across different user accounts and deployment environments

**Implementation**:
- Use `os.path.expanduser()` for `~` expansion
- Expand paths before any file operations
- Never use relative paths in API communications

**Reference**: See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" for ecosystem-wide requirements.

---

## Additional Recommendations

### IDE Setup

**Recommended**: Cursor (or VS Code) with extensions:
- Python
- Pylance
- Black Formatter
- Flake8
- MyPy Type Checker

**Note**: Cursor is the current IDE environment. VS Code extensions are compatible with Cursor. Both IDEs provide excellent Python development support.

### Development Scripts

**Consider creating**:
- `scripts/setup.sh` - Initial setup
- `scripts/test.sh` - Run tests
- `scripts/lint.sh` - Run linters
- `scripts/format.sh` - Format code

### Continuous Integration (Future)

**Consider**:
- GitHub Actions for automated testing
- Pre-commit hooks for code quality
- Automated dependency updates (Dependabot)

---

## Quick Reference

### Daily Workflow

```bash
# 1. Navigate to app (direnv auto-activates venv)
cd apps/digidoc

# 2. Check you're in the right venv
which python  # Should show .venv/bin/python

# 3. Install/update dependencies
pip install -r requirements.txt
pip install -r ../../development/requirements-dev.txt

# 4. Run tests
pytest

# 5. Format code
black .

# 6. Lint
flake8 .

# 7. Type check
mypy .
```

### Creating New App

See `development/VENV_STANDARDS.md` for complete checklist.

---

**Last Updated**: 2025-12-24  
**Maintained By**: Construction Suite Development Team

