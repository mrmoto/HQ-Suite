# MVP to Production Transition Checklist

**Purpose**: Track explicit changes required when transitioning from MVP to production development.

**Status**: Active - Updated as requirements are identified

---

## Security Hardening

### Dependency Security
- [ ] **Run `safety check`** on all requirements files
  - `apps/digidoc/requirements_ocr.txt`
  - `development/requirements-dev.txt`
  - Any app-specific requirements files
- [ ] **Fix all vulnerabilities** identified by safety
- [ ] **Document security fixes** in commit messages

### Code Security
- [ ] **Run `bandit -r .`** on all Python code
- [ ] **Fix all security issues** identified by bandit
- [ ] **Document security fixes** in commit messages

### Configuration Security
- [ ] **Audit all configuration files** for hardcoded secrets
- [ ] **Move secrets to environment variables** or secure vault
- [ ] **Update .gitignore** to exclude all secret files
- [ ] **Document secret management** in README

---

## Dependency Management

### Version Pinning
- [ ] **Convert all `>=` to `==`** in production requirements files
  - `apps/digidoc/requirements_ocr.txt` → pin all versions
  - Any other app-specific `requirements.txt` files
- [ ] **Keep `>=` in `development/requirements-dev.txt`** (dev tools can be flexible)
- [ ] **Test pinned versions** in clean environment
- [ ] **Document version pinning rationale** in requirements files

### Dependency Audit
- [ ] **Run `pip list --outdated`** in each app's venv
- [ ] **Review outdated packages** for security patches
- [ ] **Update critical security patches** (create branch, test, merge)
- [ ] **Document update process** in commit messages

---

## Code Quality

### Type Checking
- [ ] **Run `mypy .`** on all code
- [ ] **Fix all type errors** or add `# type: ignore` with justification
- [ ] **Aim for 80%+ type coverage** (document exceptions)

### Linting
- [ ] **Run `flake8 .`** and fix all issues
- [ ] **Run `pylint .`** and address critical issues
- [ ] **Configure pre-commit hooks** to enforce linting

### Formatting
- [ ] **Run `black .`** to format all code
- [ ] **Run `isort .`** to sort imports
- [ ] **Configure pre-commit hooks** to enforce formatting

---

## Testing

### Test Coverage
- [ ] **Run `pytest --cov`** to measure coverage
- [ ] **Aim for 80%+ coverage** on critical paths
- [ ] **Document coverage exceptions** (if any)
- [ ] **Add coverage badges** to README (optional)

### Test Execution
- [ ] **Run full test suite** in clean environment
- [ ] **Fix all failing tests**
- [ ] **Add integration tests** for critical workflows
- [ ] **Document test execution** in CI/CD (future)

---

## Documentation

### Code Documentation
- [ ] **Add docstrings** to all public functions/classes
- [ ] **Use Google-style docstrings** consistently
- [ ] **Document all configuration parameters**
- [ ] **Update README** with production setup instructions

### Architecture Documentation
- [ ] **Review `MASTER_ARCHITECTURE.md`** for accuracy
- [ ] **Update `ARCHITECTURE_CHANGELOG.md`** with MVP→Production changes
- [ ] **Document production deployment** process
- [ ] **Create production runbook** (if applicable)

---

## Configuration

### Hardcoded Values
- [ ] **Audit all code** for hardcoded values
- [ ] **Move all values to config files** or environment variables
- [ ] **Document all configuration options** in config file comments
- [ ] **Create `.env.example`** files for each app

### Environment Variables
- [ ] **Document all environment variables** in README
- [ ] **Create `.env.example`** files
- [ ] **Validate required environment variables** at startup
- [ ] **Add environment variable validation** to config loader

---

## Performance

### Profiling
- [ ] **Run `py-spy`** on critical paths
- [ ] **Identify bottlenecks** and optimize
- [ ] **Document performance characteristics**
- [ ] **Add performance tests** (if applicable)

### Resource Management
- [ ] **Review memory usage** with `memory-profiler`
- [ ] **Optimize memory-intensive operations**
- [ ] **Document resource requirements**
- [ ] **Add resource limits** (if applicable)

---

## Monitoring & Logging

### Logging
- [ ] **Review all logging statements**
- [ ] **Use structured logging** (JSON format)
- [ ] **Set appropriate log levels** (DEBUG, INFO, WARNING, ERROR)
- [ ] **Document log locations** and rotation policies

### Monitoring
- [ ] **Add health check endpoints** (if applicable)
- [ ] **Set up error tracking** (Sentry, etc.)
- [ ] **Document monitoring setup**
- [ ] **Create alerting rules** (if applicable)

---

## Deployment

### Build Process
- [ ] **Create build scripts** for each app
- [ ] **Test builds** in clean environment
- [ ] **Document build process**
- [ ] **Create deployment scripts** (if applicable)

### Environment Setup
- [ ] **Document production environment** requirements
- [ ] **Create setup scripts** for production
- [ ] **Test setup scripts** in clean environment
- [ ] **Document deployment process**

---

## Git & Version Control

### Branch Strategy
- [ ] **Review branch naming** conventions
- [ ] **Ensure all branches** follow conventions
- [ ] **Document branch strategy** in README

### Commit Messages
- [ ] **Review commit history** for consistency
- [ ] **Ensure all commits** follow Conventional Commits
- [ ] **Document commit message format** in CONTRIBUTING.md

### Pre-commit Hooks
- [ ] **Set up pre-commit hooks** (black, flake8, mypy, etc.)
- [ ] **Test pre-commit hooks** work correctly
- [ ] **Document pre-commit setup** in README

---

## Notes

- **This checklist is living** - add items as they're identified
- **Check off items** as they're completed
- **Document exceptions** in commit messages or README
- **Review before each production release**

---

**Last Updated**: 2025-12-24  
**Next Review**: Before production deployment

