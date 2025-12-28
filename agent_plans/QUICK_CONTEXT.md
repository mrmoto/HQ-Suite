# Quick Context: Construction Suite Development

**Purpose**: Fast context loading for new AI chat sessions. Read this first to understand project state and how to work effectively.

**Last Updated**: 2025-12-24

---

## Critical Documents (Read These First)

### 1. Project Specification
**Ecosystem Architecture**: `shared_documentation/architecture/MASTER_ARCHITECTURE.md`  
**DigiDoc Architecture**: `apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md`  
**Purpose**: Single source of truth for WHAT WILL BE BUILT  
**Contains**: 
- **MASTER_ARCHITECTURE.md**: Ecosystem architecture, app relationships, integration contracts
- **DigiDoc ARCHITECTURE.md**: DigiDoc-specific architecture, specs, dependencies, logic, status (Implemented/Planned/Future)  
**Note**: These are NOT for development tracking - they're the specs of the finished system

### 2. Development Status
**File**: `shared_documentation/planning/DEVELOPMENT_PATHWAY.md`  
**Purpose**: Hierarchical plan of WHAT NEEDS TO BE BUILT  
**Contains**: Project structure with status (Q=Queued, IP=In Progress, C=Complete), links to slice docs  
**Status Updates**: Update as you work through slices

**File**: `shared_documentation/planning/SCHEDULE.md`  
**Purpose**: Development order - WHEN things are being built  
**Contains**: Phases, milestones, where/why development stopped  
**Note**: Tracks time and order, not detailed specs

### 3. Active Planning
**File**: `shared_documentation/planning/PLANNING_CACHE.md`  
**Purpose**: Scratch paper for nested planning sessions  
**Contains**: Decisions, questions, assumptions during active planning  
**Note**: Clear after planning complete - it's temporary working space

### 4. Detailed Design Docs
**Directory**: `shared_documentation/planning/slices/`  
**Purpose**: Detailed design for each feature/module  
**Contains**: Implementation approach, dependencies, success criteria  
**When to Create**: As soon as you enter planning for a DP section

### 5. Architecture History
**File**: `shared_documentation/architecture/ARCHITECTURE_CHANGELOG.md`  
**Purpose**: Track version history, major architectural decisions, and rationale  
**Contains**: Version history, major decisions with rationale, implementation status tracking  
**Note**: Updated whenever MASTER_ARCHITECTURE.md changes significantly

---

## How to Work with This User

### Communication Style
- **Short, fast conversations** - High conversational velocity preferred
- **One question at a time** - Don't batch questions
- **Answer "why" questions directly** - Don't take action, just explain
- **Wait for all messages** - If user says "multiple messages coming", wait
- **Acknowledge explicitly** - When user requests acknowledgment, provide it

### Development Approach
- **This chat = Development discussion** - Keep coding to separate agent/session
- **Token depth concern** - User wants to preserve token budget for development discussion
- **Slice files** - Be aggressive about suggesting slice files when appropriate
- **Status updates** - Update DP.md and schedule.md as you work (primarily AI responsibility)

### Planning Workflow
1. **Planning session starts** → Create/update slice file in `planning/slices/`
2. **Update cache.md** → Track decisions/questions during planning
3. **Update DP.md** → Mark section as IP, link to slice file
4. **Planning complete** → Clear cache.md, update DP.md status
5. **Execution** → Use separate agent/session for coding

---

## Current Development State

### Best Practices Adoption
**Status**: Infrastructure Phase 1 Complete (Week 1)  
**Last Completed**: pytest-cov, Alembic, CI/CD pipeline, tests/ directory structure, Git learning guide  
**Next**: Infrastructure Phase 2 - Code Quality Enforcement (Week 2)  
**Reference**: `shared_documentation/training/DEV_ENVIRONMENT_ASSESSMENT.md`  
**Reference**: `shared_documentation/planning/SCHEDULE.md` (Infrastructure Phases section)

### MVP Development
**Phase**: MVP Development - Phase 2 (Filling critical gaps)  
**Last Milestone**: Template matching now uses real structural fingerprinting (2025-12-24)  
**Next**: Field extraction needs real implementation

**Key Files**:
- Development Pathway: `shared_documentation/planning/DEVELOPMENT_PATHWAY.md`
- Schedule: `shared_documentation/planning/SCHEDULE.md`
- Active Planning: `shared_documentation/planning/PLANNING_CACHE.md`

---

## Project Structure

**Workspace**: `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/`  
**Apps**: `apps/digidoc/`, `apps/hq/`, `apps/watcher/`  
**Shared Docs**: `shared_documentation/` (architecture/, planning/, training/)

---

## Quick Reference

- **Ecosystem Architecture**: `shared_documentation/architecture/MASTER_ARCHITECTURE.md`
- **DigiDoc Architecture**: `apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md`
- **Architecture History**: `shared_documentation/architecture/ARCHITECTURE_CHANGELOG.md`
- **What to Build**: `shared_documentation/planning/DEVELOPMENT_PATHWAY.md`
- **When to Build**: `shared_documentation/planning/SCHEDULE.md`
- **Planning Scratch**: `shared_documentation/planning/PLANNING_CACHE.md`
- **Slice Docs**: `shared_documentation/planning/slices/`
- **Training Guide**: `shared_documentation/training/AGENT_TRAINING_GUIDE.md`
- **Error Log**: `shared_documentation/training/DEVELOPMENT_ERRORS_LOG.md`

---

**Remember**: This chat is for development discussion. Use separate agent/session for actual coding to preserve token budget.

