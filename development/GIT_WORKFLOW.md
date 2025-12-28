# Git Workflow & Best Practices - Construction Suite

**Purpose**: Reinforce Git best practices through process and automation.

**Last Updated**: 2025-12-24

---

## Quick Reference: Before Every Git Command

**Ask yourself**:
1. ✅ Am I on the right branch? (`git branch` or `git status`)
2. ✅ Have I committed my changes? (`git status`)
3. ✅ Do I need to create a branch? (`git checkout -b feature/name`)
4. ✅ Is my commit message clear? (Conventional Commits format)

---

## Branch Strategy

### Branch Naming Convention

**Format**: `{type}/{description}`

**Types**:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test additions/changes
- `chore/` - Maintenance tasks

**Examples**:
```bash
feature/queue-abstraction
bugfix/preprocessing-error
refactor/config-loading
docs/venv-standards
test/coverage-improvement
chore/dependency-update
```

### Branch Workflow

**Before starting work**:
```bash
# 1. Check current branch
git branch

# 2. Ensure you're on main (or latest)
git checkout main
git pull origin main

# 3. Create feature branch
git checkout -b feature/my-feature

# 4. Verify you're on new branch
git branch  # Should show * feature/my-feature
```

**During work**:
```bash
# Commit frequently with clear messages
git add .
git commit -m "feat(scope): description"

# Push to remote regularly
git push origin feature/my-feature
```

**After work**:
```bash
# 1. Ensure all tests pass
pytest  # or your test command

# 2. Ensure code is formatted
black .
flake8 .

# 3. Final commit if needed
git add .
git commit -m "chore: final cleanup"

# 4. Push to remote
git push origin feature/my-feature

# 5. Create pull request (or merge locally)
```

---

## Commit Message Format

### Conventional Commits

**Format**:
```
{type}({scope}): {subject}

{body (optional)}

{footer (optional)}
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance
- `style`: Formatting (no code change)
- `perf`: Performance improvement
- `ci`: CI/CD changes

**Examples**:
```bash
# Good
git commit -m "feat(queue): add RQ adapter implementation"

git commit -m "fix(preprocessing): correct deskew angle calculation

The previous implementation used minAreaRect which was incorrect.
Now uses HoughLinesP as specified in MASTER_ARCHITECTURE.md."

git commit -m "docs(venv): add direnv setup instructions"

# Bad
git commit -m "updates"
git commit -m "fix stuff"
git commit -m "WIP"
```

### Commit Message Checklist

Before committing, verify:
- [ ] Type is correct (feat, fix, docs, etc.)
- [ ] Scope is clear (queue, preprocessing, config, etc.)
- [ ] Subject is concise (< 50 chars)
- [ ] Body explains "why" not "what" (if needed)
- [ ] References issue/PR if applicable

---

## Pre-Commit Checklist

**Before every commit**, run:

```bash
# 1. Check what you're committing
git status

# 2. Review changes
git diff

# 3. Run tests (if applicable)
pytest

# 4. Format code
black .

# 5. Lint code
flake8 .

# 6. Type check (if applicable)
mypy .

# 7. Check for secrets (manual review)
# Look for: API keys, passwords, tokens

# 8. Commit with clear message
git add .
git commit -m "type(scope): description"
```

---

## Automated Git Hooks (Pre-commit)

### Setup

**Install pre-commit** (from requirements-dev.txt):
```bash
pip install pre-commit
```

**Create `.pre-commit-config.yaml`** in app root:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

**Install hooks**:
```bash
pre-commit install
```

**Test hooks**:
```bash
pre-commit run --all-files
```

### What Hooks Do

**Automatically**:
- Remove trailing whitespace
- Fix end-of-file issues
- Check YAML/JSON/TOML syntax
- Detect large files
- Detect merge conflicts
- Detect private keys
- Format code with black
- Sort imports with isort
- Lint with flake8
- Type check with mypy

**Result**: Commits are automatically checked before they're created.

---

## Dependency Update Workflow

### Scheduled Process

**Frequency**: Monthly (or as needed for security patches)

**Process**:

1. **Create update branch**:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b chore/dependency-update-YYYY-MM
   ```

2. **Check outdated packages**:
   ```bash
   cd apps/digidoc
   source .venv/bin/activate  # or rely on direnv
   pip list --outdated
   ```

3. **Update requirements file**:
   ```bash
   # For production: pin exact versions
   # Edit requirements_ocr.txt, change >= to ==
   # For dev tools: keep >= (minimum versions)
   ```

4. **Test in clean environment**:
   ```bash
   # Recreate venv
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements_ocr.txt
   
   # Run tests
   pytest
   ```

5. **Commit and push**:
   ```bash
   git add requirements_ocr.txt
   git commit -m "chore(deps): update dependencies to latest versions

   - Updated redis from 7.0.0 to 7.1.0
   - Updated rq from 2.5.0 to 2.6.1
   - All tests passing"
   
   git push origin chore/dependency-update-YYYY-MM
   ```

6. **Create PR or merge**:
   - Review changes
   - Ensure all tests pass
   - Merge to main

### Security Updates

**For critical security patches**, follow same process but:
- Create branch: `bugfix/security-update-{package}`
- Update immediately (don't wait for monthly cycle)
- Test thoroughly
- Document security fix in commit message

---

## Common Git Mistakes & Prevention

### Mistake 1: Committing to Wrong Branch

**Prevention**:
```bash
# Always check branch before committing
git branch  # Shows current branch with *
git status  # Shows branch name at top
```

**Fix**:
```bash
# If committed to wrong branch:
git log -1  # Get commit hash
git reset HEAD~1  # Undo commit (keeps changes)
git checkout correct-branch
git commit -m "feat: ..."  # Commit to correct branch
```

### Mistake 2: Unclear Commit Messages

**Prevention**: Use commit message template

**Create `.gitmessage`**:
```
# <type>(<scope>): <subject>
#
# <body>
#
# <footer>
```

**Use template**:
```bash
git config commit.template .gitmessage
```

### Mistake 3: Forgetting to Pull Before Push

**Prevention**: Always pull before push
```bash
git pull origin main  # or your branch
git push origin feature/my-feature
```

### Mistake 4: Committing Secrets

**Prevention**:
- Use `.env` files (in `.gitignore`)
- Never commit `.env` files
- Review `git diff` before committing
- Use pre-commit hook to detect private keys

**Fix** (if already committed):
```bash
# Remove from history (requires force push - be careful!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

---

## Git Aliases (Optional but Helpful)

**Add to `~/.gitconfig`**:
```ini
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = !gitk
    lg = log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit
    amend = commit --amend --no-edit
    wip = commit -am "WIP"
    unwip = reset HEAD~1
```

**Usage**:
```bash
git st    # Instead of git status
git co -b feature/new  # Instead of git checkout -b
git lg    # Pretty log view
```

---

## Integration with Development Workflow

### Daily Workflow

```bash
# Morning
git checkout main
git pull origin main
git checkout -b feature/my-work

# During work
git add .
git commit -m "feat(scope): description"
git push origin feature/my-work

# End of day
git push origin feature/my-work  # Backup work
```

### Before Major Changes

```bash
# 1. Ensure clean working directory
git status  # Should be clean

# 2. Create backup branch
git checkout -b backup/before-major-change

# 3. Return to feature branch
git checkout feature/my-work

# 4. Make changes
# ... work ...

# 5. Commit frequently
git add .
git commit -m "feat: ..."
```

---

## Checklist: Before Every Commit

Print this and keep it visible:

- [ ] **Branch**: Am I on the correct branch? (`git branch`)
- [ ] **Status**: What am I committing? (`git status`, `git diff`)
- [ ] **Tests**: Do all tests pass? (`pytest`)
- [ ] **Format**: Is code formatted? (`black .`)
- [ ] **Lint**: Does code pass linting? (`flake8 .`)
- [ ] **Secrets**: Am I committing any secrets? (manual review)
- [ ] **Message**: Is commit message clear? (Conventional Commits format)
- [ ] **Scope**: Is commit focused on one change? (if not, split commits)

---

## Resources

- **Conventional Commits**: https://www.conventionalcommits.org/
- **Git Best Practices**: https://github.com/git/git/blob/master/Documentation/SubmittingPatches
- **Pre-commit**: https://pre-commit.com/

---

**Last Updated**: 2025-12-24

