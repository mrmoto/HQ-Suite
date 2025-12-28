# Best Practices Q&A - Answers

**Date**: 2025-12-24  
**Purpose**: Answers to follow-up questions about best practices implementation

---

## 1. Is "pinning" in effect in AGENT_TRAINING_GUIDE.md and dev documents?

**Answer**: ✅ **Now Updated**

**Status**:
- ✅ **AGENT_TRAINING_GUIDE.md**: Updated with version pinning strategy section
- ✅ **DEVELOPMENT_BEST_PRACTICES.md**: Already had version pinning section
- ✅ **requirements_ocr.txt**: Added TODO comments to pin before production

**Strategy**:
- **Production** (`requirements.txt`): Use `==` for exact versions
- **Development** (`requirements-dev.txt`): Use `>=` for minimum versions

**Location in docs**:
- `AGENT_TRAINING_GUIDE.md` → "Virtual Environment Management" → "Version Pinning Strategy"
- `DEVELOPMENT_BEST_PRACTICES.md` → "Dependency Management" → "Version Pinning Strategy"

---

## 2. Do we have ">=" minimum versioning in reqs-dev.txt?

**Answer**: ✅ **Yes**

**Current state**: `development/requirements-dev.txt` uses `>=` for all packages

**Examples**:
```txt
pytest>=7.4.0
black>=23.7.0
mypy>=1.5.0
```

**Rationale**: Development tools can be flexible; minimum versions allow patch updates automatically.

---

## 3. How to schedule "pip list --outdated" process & branching?

**Answer**: ✅ **Documented in GIT_WORKFLOW.md**

**Process** (monthly or as needed):

1. **Create update branch**:
   ```bash
   git checkout -b chore/dependency-update-YYYY-MM
   ```

2. **Check outdated packages**:
   ```bash
   cd apps/digidoc
   pip list --outdated
   ```

3. **Update requirements file**:
   - Production: Change `>=` to `==` with exact versions
   - Dev tools: Keep `>=` (minimum versions)

4. **Test in clean environment**:
   ```bash
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements_ocr.txt
   pytest
   ```

5. **Commit and push**:
   ```bash
   git commit -m "chore(deps): update dependencies to latest versions"
   git push origin chore/dependency-update-YYYY-MM
   ```

**Full details**: See `development/GIT_WORKFLOW.md` → "Dependency Update Workflow"

---

## 4. Git Best Practices - How to reinforce execution?

**Answer**: ✅ **Created GIT_WORKFLOW.md with process and automation**

**Solutions implemented**:

### A. Pre-Commit Checklist
- **Location**: `development/GIT_WORKFLOW.md` → "Checklist: Before Every Commit"
- **Print and keep visible** - 8-point checklist before every commit

### B. Pre-Commit Hooks (Automated)
- **Setup**: Install `pre-commit` from requirements-dev.txt
- **Configuration**: `.pre-commit-config.yaml` (template in GIT_WORKFLOW.md)
- **Automatically checks**: Formatting, linting, type checking before commit

### C. Git Aliases
- **Quick commands**: `git st`, `git co`, `git br` (see GIT_WORKFLOW.md)

### D. Branch Strategy Documentation
- **Naming conventions**: `feature/`, `bugfix/`, `refactor/`, etc.
- **Workflow**: Step-by-step process documented

### E. Commit Message Format
- **Conventional Commits**: Template and examples provided
- **Git hook reminder**: Optional hook to remind before commit

**Key file**: `development/GIT_WORKFLOW.md` - Complete Git workflow guide

---

## 5. Token Drift Mitigation - Stateless solution?

**Answer**: ✅ **Created TOKEN_DRIFT_MITIGATION.md with checkpoint system**

**Solution**: Stateless checkpoint system

### Checkpoint Files
- **Location**: `development/checkpoints/checkpoint-{timestamp}.md`
- **Content**: Decisions made, files modified, next actions, critical updates needed
- **When**: After major tasks, before context switches, before expected token drift

### Helper Script
- **Location**: `development/scripts/create-checkpoint.sh`
- **Usage**: `./development/scripts/create-checkpoint.sh`
- **Creates**: Timestamped checkpoint file with template

### Critical Update Checklist
- **Before context switch**: Verify docs, requirements, Git are updated
- **After context switch**: Review latest checkpoint for missed updates

### Recovery Process
- **Step 1**: Check latest checkpoint
- **Step 2**: Review "Critical Updates Needed"
- **Step 3**: Review recent file changes
- **Step 4**: Complete pending updates

**Key file**: `development/TOKEN_DRIFT_MITIGATION.md` - Complete mitigation strategy

---

## 6. MVP→Production Transition Checklist

**Answer**: ✅ **Created MVP_TO_PRODUCTION_CHECKLIST.md**

**Includes**:
- ✅ **Security**: `safety check` and `bandit` runs
- ✅ **Dependency Security**: Section with safety/bandit tasks
- ✅ **All transition items**: Security, dependencies, code quality, testing, docs, config, performance, monitoring, deployment, Git

**Location**: `development/MVP_TO_PRODUCTION_CHECKLIST.md`

**Security Section** (as requested):
```markdown
## Security Hardening

### Dependency Security
- [ ] Run `safety check` on all requirements files
- [ ] Fix all vulnerabilities identified by safety

### Code Security
- [ ] Run `bandit -r .` on all Python code
- [ ] Fix all security issues identified by bandit
```

### Markdown Section References

**Question**: Does `#section###subsection` notation work?

**Answer**: ❌ **No**, standard markdown doesn't support that.

**Standard approach**:
- Headers auto-generate anchors: `# Section` → `#section`
- Reference: `[Section Name](#section-name)`
- GitHub/GitLab handle this automatically

**Better approach** (for explicit IDs):
```markdown
## Security Practices {#security-practices}

### Dependency Security {#dependency-security}

Reference: [Dependency Security](#dependency-security)
```

**Note**: Added explanation to `TOKEN_DRIFT_MITIGATION.md`

---

## 7. Why VS Code over Cursor?

**Answer**: ✅ **Updated to Cursor**

**Change made**: Updated `DEVELOPMENT_BEST_PRACTICES.md` to recommend Cursor (current IDE)

**Rationale**:
- Cursor is your current IDE environment
- VS Code extensions are compatible with Cursor
- Both provide excellent Python development support
- No functional difference for the extensions listed

**Updated section**:
```markdown
### IDE Setup

**Recommended**: Cursor (or VS Code) with extensions:
- Python
- Pylance
- Black Formatter
- Flake8
- MyPy Type Checker

**Note**: Cursor is the current IDE environment. VS Code extensions are compatible with Cursor.
```

---

## Summary of Files Created/Updated

### New Files
1. ✅ `development/MVP_TO_PRODUCTION_CHECKLIST.md` - Transition checklist
2. ✅ `development/GIT_WORKFLOW.md` - Complete Git workflow guide
3. ✅ `development/TOKEN_DRIFT_MITIGATION.md` - Token drift mitigation strategy
4. ✅ `development/scripts/create-checkpoint.sh` - Checkpoint creation script
5. ✅ `development/checkpoints/` - Directory for checkpoint files

### Updated Files
1. ✅ `shared_documentation/training/AGENT_TRAINING_GUIDE.md` - Added version pinning strategy
2. ✅ `development/DEVELOPMENT_BEST_PRACTICES.md` - Updated IDE recommendation to Cursor
3. ✅ `apps/digidoc/requirements_ocr.txt` - Added TODO comments for production pinning

---

## Next Steps

1. **Review new documents**:
   - `development/GIT_WORKFLOW.md`
   - `development/TOKEN_DRIFT_MITIGATION.md`
   - `development/MVP_TO_PRODUCTION_CHECKLIST.md`

2. **Set up pre-commit hooks** (when ready):
   ```bash
   cd apps/digidoc
   pip install pre-commit
   # Create .pre-commit-config.yaml (template in GIT_WORKFLOW.md)
   pre-commit install
   ```

3. **Create first checkpoint**:
   ```bash
   ./development/scripts/create-checkpoint.sh
   ```

4. **Pin production dependencies** (before production):
   - Update `requirements_ocr.txt` to use `==` instead of `>=`
   - Test in clean environment
   - Document in commit message

---

**Last Updated**: 2025-12-24

