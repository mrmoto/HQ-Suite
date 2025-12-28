# Token Drift Mitigation Strategy

**Purpose**: Ensure critical updates (docs, requirements, Git) are captured before token drift occurs.

**Problem**: When token drift occurs before BPs are solidified, critical updates may be missed.

**Solution**: Stateless checkpoints and automated reminders.

---

## Table of Contents

- [Stateless Checkpoint System](#stateless-checkpoint-system)
  - [Checkpoint Files](#checkpoint-files)
  - [When to Create Checkpoints](#when-to-create-checkpoints)
- [Automated Reminders](#automated-reminders)
  - [Pre-Commit Hook Reminder](#pre-commit-hook-reminder)
  - [Git Hook Reminder](#git-hook-reminder)
- [Critical Update Checklist](#critical-update-checklist)
  - [Documentation Updates](#documentation-updates)
  - [Requirements Updates](#requirements-updates)
  - [Git Updates](#git-updates)
  - [Configuration Updates](#configuration-updates)
- [Stateless Recovery Process](#stateless-recovery-process)
  - [After Token Drift](#after-token-drift)
- [Integration with Development Workflow](#integration-with-development-workflow)
  - [Before Context Switch](#before-context-switch)
  - [After Context Switch](#after-context-switch)
- [Helper Scripts](#helper-scripts)
  - [Create Checkpoint Script](#create-checkpoint-script)
- [Best Practices](#best-practices)
  - [Regular Checkpoints](#regular-checkpoints)
  - [Critical Updates Priority](#critical-updates-priority)
  - [Recovery Strategy](#recovery-strategy)
- [Markdown Section References](#markdown-section-references)

---

## Stateless Checkpoint System

### Checkpoint Files

**Location**: `development/checkpoints/`

**Format**: `checkpoint-{timestamp}.md`

**Content**: Snapshot of critical state at decision points

**Example**:
```markdown
# Checkpoint: 2025-12-24-11:30

## Decisions Made
- direnv setup completed
- requirements-dev.txt created
- Git workflow documented

## Files Modified
- development/requirements-dev.txt (new)
- development/VENV_STANDARDS.md (new)
- apps/digidoc/.envrc (new)

## Next Actions
- [ ] Install dev tools in digidoc venv
- [ ] Test direnv activation
- [ ] Review Git workflow

## Critical Updates Needed
- [ ] Update AGENT_TRAINING_GUIDE.md with version pinning
- [ ] Pin production dependencies in requirements_ocr.txt
- [ ] Set up pre-commit hooks
```

### When to Create Checkpoints

**Create checkpoint**:
1. After completing a major task
2. Before switching contexts
3. When making architectural decisions
4. Before token drift is expected
5. After updating critical files (requirements, docs)

**Process**:
```bash
# Create checkpoint
cd development/checkpoints
cat > checkpoint-$(date +%Y-%m-%d-%H%M).md << 'EOF'
# Checkpoint: $(date)

## Decisions Made
...

## Files Modified
...

## Next Actions
...

## Critical Updates Needed
...
EOF
```

---

## Automated Reminders

### Pre-Commit Hook Reminder

**Add to `.pre-commit-config.yaml`**:
```yaml
- repo: local
  hooks:
    - id: checkpoint-reminder
      name: Checkpoint Reminder
      entry: bash -c 'echo "⚠️  Remember to create checkpoint if major changes made"'
      language: system
      pass_filenames: false
      always_run: true
```

### Git Hook Reminder

**Add to `.git/hooks/pre-commit`** (or use pre-commit framework):
```bash
#!/bin/bash
# Reminder to update docs/requirements before committing

echo "📝 Pre-commit checklist:"
echo "  [ ] Updated requirements.txt if dependencies changed?"
echo "  [ ] Updated documentation if architecture changed?"
echo "  [ ] Created checkpoint if major changes made?"
echo ""
read -p "Continue with commit? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi
```

---

## Critical Update Checklist

**Before any major context switch or token drift**, verify:

### Documentation Updates
- [ ] **AGENT_TRAINING_GUIDE.md**: Updated with new patterns/decisions?
- [ ] **DEVELOPMENT_BEST_PRACTICES.md**: Updated with new practices?
- [ ] **VENV_STANDARDS.md**: Updated if venv patterns changed?
- [ ] **README.md**: Updated if setup process changed?

### Requirements Updates
- [ ] **requirements.txt**: Updated if dependencies changed?
- [ ] **requirements-dev.txt**: Updated if dev tools changed?
- [ ] **Version pinning**: Production deps use `==`, dev deps use `>=`?

### Git Updates
- [ ] **.gitignore**: Updated if new patterns needed?
- [ ] **Pre-commit hooks**: Set up if not already?
- [ ] **Branch strategy**: Following conventions?

### Configuration Updates
- [ ] **Config files**: Updated if new parameters added?
- [ ] **Environment variables**: Documented if new vars added?

---

## Stateless Recovery Process

### After Token Drift

**Step 1**: Check latest checkpoint
```bash
ls -t development/checkpoints/ | head -1
cat development/checkpoints/checkpoint-*.md | tail -20
```

**Step 2**: Review "Critical Updates Needed" section

**Step 3**: Review recent file changes
```bash
git log --oneline -10
git diff HEAD~5 HEAD --name-only
```

**Step 4**: Review open todos
```bash
# Check for TODO comments
grep -r "TODO\|FIXME\|XXX" apps/ development/
```

**Step 5**: Review planning cache
```bash
cat shared_documentation/planning/PLANNING_CACHE.md
```

---

## Integration with Development Workflow

### Before Context Switch

**Run checklist**:
```bash
# 1. Create checkpoint
./scripts/create-checkpoint.sh

# 2. Review critical updates
cat development/TOKEN_DRIFT_MITIGATION.md | grep "## Critical Update"

# 3. Update docs/requirements if needed
# ... make updates ...

# 4. Commit checkpoint
git add development/checkpoints/
git commit -m "chore: create checkpoint before context switch"
```

### After Context Switch

**Recovery process**:
```bash
# 1. Read latest checkpoint
cat development/checkpoints/checkpoint-*.md | tail -50

# 2. Review "Critical Updates Needed"
# 3. Complete any pending updates
# 4. Update checkpoint with completion status
```

---

## Helper Scripts

### Create Checkpoint Script

**`development/scripts/create-checkpoint.sh`**:
```bash
#!/bin/bash
# Create a checkpoint file

TIMESTAMP=$(date +%Y-%m-%d-%H%M)
CHECKPOINT_FILE="development/checkpoints/checkpoint-${TIMESTAMP}.md"

cat > "$CHECKPOINT_FILE" << EOF
# Checkpoint: ${TIMESTAMP}

## Decisions Made
- [Add decisions made since last checkpoint]

## Files Modified
- [List files modified]

## Next Actions
- [ ] [Action 1]
- [ ] [Action 2]

## Critical Updates Needed
- [ ] [Update 1]
- [ ] [Update 2]
EOF

echo "✅ Checkpoint created: $CHECKPOINT_FILE"
echo "📝 Edit it to add details"
```

**Make executable**:
```bash
chmod +x development/scripts/create-checkpoint.sh
```

---

## Best Practices

### Regular Checkpoints
- **Create checkpoints** at natural break points
- **Don't wait** for token drift - be proactive
- **Review checkpoints** regularly to catch missed updates

### Critical Updates Priority
- **Documentation** updates are highest priority
- **Requirements** updates are critical for reproducibility
- **Git** updates ensure workflow consistency

### Recovery Strategy
- **Always** check latest checkpoint after context switch
- **Always** review "Critical Updates Needed" section
- **Always** complete updates before continuing work

---

## Markdown Section References

**Question**: Does `#section###subsection` notation work for referencing sections?

**Answer**: No, standard markdown doesn't support that notation. Use:

**Standard approach**:
- `# Section Name` → Reference as `[Section Name](#section-name)`
- `## Subsection` → Reference as `[Subsection](#subsection)`
- GitHub/GitLab auto-generate anchors from headers

**Better approach for this document**:
- Use explicit section IDs: `{#section-id}`
- Or use relative links: `[See Git Workflow](./GIT_WORKFLOW.md#branch-strategy)`

**Example**:
```markdown
## Security Practices {#security-practices}

### Dependency Security {#dependency-security}

Reference: [Dependency Security](#dependency-security)
```

---

**Last Updated**: 2025-12-24

