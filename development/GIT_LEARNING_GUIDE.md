# Git Learning Guide

**Purpose**: Learning resources and practical guide for Git concepts needed in this project.  
**Target Audience**: Developers new to Git or needing to understand advanced concepts.  
**Source**: Based on assessment recommendations (DEV_ENVIRONMENT_ASSESSMENT.md lines 69-96)

---

## Learning Path

### Phase 1: Fundamentals (Start Here)

#### 1. Git Basics
**What to Learn**:
- What is Git and version control
- Basic commands: `git init`, `git add`, `git commit`, `git status`, `git log`
- Understanding the working directory, staging area, and repository
- Branching basics: `git branch`, `git checkout`, `git merge`

**Resources**:
- [Git Official Documentation - Getting Started](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control)
- [Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials)
- **Practice**: Create a test repository and practice basic commands

**Time Estimate**: 2-4 hours

#### 2. Branching and Merging
**What to Learn**:
- Creating and switching branches
- Merging branches (`git merge`)
- Resolving merge conflicts
- Branch naming conventions

**Resources**:
- [Git Branching Tutorial](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)
- **Practice**: Create feature branches, make changes, merge them

**Time Estimate**: 2-3 hours

#### 3. Remote Repositories
**What to Learn**:
- `git remote`, `git push`, `git pull`, `git fetch`
- Working with GitHub/GitLab
- Understanding origin and upstream

**Resources**:
- [Working with Remotes](https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes)
- **Practice**: Push your test repository to GitHub

**Time Estimate**: 1-2 hours

---

### Phase 2: Intermediate Concepts

#### 4. Rebase vs. Merge
**What to Learn**:
- When to use `git rebase` vs. `git merge`
- Interactive rebase (`git rebase -i`)
- Rebase workflow vs. merge workflow
- Pros and cons of each approach

**Resources**:
- [Merging vs. Rebasing](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)
- [Git Rebase Tutorial](https://git-scm.com/book/en/v2/Git-Branching-Rebasing)

**Decision for This Project**:
- **Strategy**: Use merge for feature branches, rebase for cleaning up commits before merge
- **Documentation**: See `development/GIT_WORKFLOW.md` for our specific strategy

**Time Estimate**: 2-3 hours

#### 5. Git Hooks
**What to Learn**:
- What are Git hooks (pre-commit, pre-push, etc.)
- Client-side hooks vs. server-side hooks
- How to write custom hooks
- Using pre-commit framework

**Resources**:
- [Git Hooks Documentation](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [Pre-commit Framework](https://pre-commit.com/)

**Implementation in This Project**:
- We use `pre-commit` framework (see `.pre-commit-config.yaml`)
- Hooks run: black, flake8, isort, bandit, safety

**Time Estimate**: 2-3 hours

#### 6. Commit Messages and Conventional Commits
**What to Learn**:
- Writing good commit messages
- Conventional Commits specification
- Commit message format: `type(scope): description`

**Resources**:
- [Conventional Commits](https://www.conventionalcommits.org/)
- [How to Write a Git Commit Message](https://cbea.ms/git-commit/)

**Our Format**:
```
type(scope): short description

Longer description if needed

Fixes #123
```

**Time Estimate**: 1 hour

---

### Phase 3: Advanced Concepts (Future)

#### 7. Git LFS (Large File Storage)
**What to Learn**:
- What is Git LFS and when to use it
- Installing and configuring Git LFS
- Tracking large files (images, models, binaries)

**When We'll Need It**:
- When storing large template images
- When storing ML models
- When binary files exceed 100MB

**Resources**:
- [Git LFS Documentation](https://git-lfs.github.com/)
- [Atlassian Git LFS Tutorial](https://www.atlassian.com/git/tutorials/git-lfs)

**Time Estimate**: 1-2 hours

#### 8. Git Submodules
**What to Learn**:
- What are submodules
- When to use submodules
- Adding, updating, and removing submodules

**When We'll Need It**:
- If we need to include external repositories
- If we share code between multiple projects

**Resources**:
- [Git Submodules Tutorial](https://git-scm.com/book/en/v2/Git-Tools-Submodules)

**Time Estimate**: 2-3 hours

#### 9. Git Worktrees
**What to Learn**:
- What are worktrees
- Working on multiple branches simultaneously
- Use cases for worktrees

**When We'll Need It**:
- Working on multiple features simultaneously
- Testing different versions side-by-side

**Resources**:
- [Git Worktrees Documentation](https://git-scm.com/docs/git-worktree)

**Time Estimate**: 1-2 hours

#### 10. Commit Signing with GPG
**What to Learn**:
- What is commit signing
- Setting up GPG keys
- Signing commits and verifying signatures

**When We'll Need It**:
- For production code
- For security-sensitive projects
- For team collaboration

**Resources**:
- [Signing Commits](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)
- [GitHub: Signing Commits](https://docs.github.com/en/authentication/managing-commit-signature-verification)

**Time Estimate**: 1-2 hours

---

## Practical Exercises

### Exercise 1: Basic Workflow
1. Create a test repository
2. Make several commits
3. Create a feature branch
4. Make changes on the branch
5. Merge the branch back to main

### Exercise 2: Conflict Resolution
1. Create two branches from the same commit
2. Modify the same file in both branches
3. Merge one branch into the other
4. Resolve the merge conflict

### Exercise 3: Rebase Practice
1. Create a feature branch with multiple commits
2. Rebase onto main
3. Use interactive rebase to squash commits

### Exercise 4: Hooks Setup
1. Install pre-commit
2. Create a simple pre-commit hook
3. Test the hook by making a commit

---

## Concepts to Implement in This Project

### Immediate (This Week)
- [ ] **Pre-commit hooks**: Set up `.pre-commit-config.yaml`
- [ ] **Branch strategy**: Document merge vs. rebase approach
- [ ] **Commit format**: Enforce Conventional Commits

### Short-term (This Month)
- [ ] **Git aliases**: Set up useful aliases (see `development/GIT_WORKFLOW.md`)
- [ ] **Branch protection**: Set up if using GitHub/GitLab
- [ ] **Git LFS**: Evaluate if needed for large files

### Medium-term (Next 3 Months)
- [ ] **Commit signing**: Set up GPG signing
- [ ] **Git submodules**: Evaluate if needed
- [ ] **Git worktrees**: Learn for parallel work

---

## Quick Reference

### Essential Commands
```bash
# Status and log
git status
git log --oneline --graph

# Branching
git branch                    # List branches
git checkout -b feature/name  # Create and switch to branch
git merge feature/name        # Merge branch

# Committing
git add .                    # Stage all changes
git commit -m "message"      # Commit with message
git push origin branch-name  # Push to remote

# Undoing
git reset HEAD~1             # Undo last commit (keep changes)
git checkout -- file         # Discard changes to file
```

### Our Workflow Commands
```bash
# See development/GIT_WORKFLOW.md for our specific workflow
```

---

## Common Mistakes to Avoid

1. **Committing to main directly** - Always use feature branches
2. **Forgetting to pull before push** - Always pull latest changes first
3. **Large commits** - Break changes into logical, small commits
4. **Bad commit messages** - Use Conventional Commits format
5. **Force pushing to shared branches** - Never force push to main/develop

---

## Resources Summary

### Official Documentation
- [Git Official Documentation](https://git-scm.com/doc)
- [Git Book](https://git-scm.com/book)

### Tutorials
- [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)
- [GitHub Learning Lab](https://lab.github.com/)

### Interactive Learning
- [Learn Git Branching](https://learngitbranching.js.org/) - Visual, interactive tutorial
- [Oh My Git!](https://ohmygit.org/) - Game for learning Git

### Reference
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Last Updated**: 2025-12-24  
**Next Review**: After completing Phase 1 fundamentals

