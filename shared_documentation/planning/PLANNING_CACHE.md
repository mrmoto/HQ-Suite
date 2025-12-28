# Planning Cache: Workspace Organization and Planning Documentation System

**Purpose**: 
- Single source of truth for decisions made during plan development
- Updated in real-time as plan is being built
- Reviewed by user before plan execution
- Cleared/reset after plan is executed or approved
- Temporary scratch paper for nested planning sessions and decision tracking during active planning

**Workflow**:
1. When starting to build a plan, create/update PLANNING_CACHE.md
2. As decisions are made, questions asked, assumptions validated → update cache immediately
3. Before presenting plan to user, summarize cache in plan overview
4. User reviews cache before approving plan
5. After plan execution, archive cache or clear for next plan

**Lifecycle**: Clear after planning complete - archive important decisions to MASTER_ARCHITECTURE.md, then clear cache.  
**Note**: This is a working document, not permanent documentation.


**Entry Structure**:
- **Decisions Made**: 
  - Header: `### [Timestamp]: [Decision Title]`
  - **Decision**: [What was decided]
  - **Rationale**: [Why]
  - **Impact**: [What this affects] (may include bulleted sub-items)
  - Optional: **Benefit**, **Status**, or other relevant fields
  - Entire entry (header through last field) should be collapsible together
  - Multi-line fields (like Impact with bullets) should be collapsible as sub-sections

- **Questions Asked**: 
  - Header: `### [Timestamp]: [Question Title]`
  - **Question**: [Question asked]
  - **Answer**: [User's answer]
  - **Follow-up**: [Any follow-up needed]
  - Entire entry should be collapsible together

- **Assumptions Validated**: 
  - Header: `### [Timestamp]: [Assumption Title]`
  - **Assumption**: [What was assumed]
  - **Validation**: [How it was confirmed]
  - Entire entry should be collapsible together

- **Open Items**: `- [ ] Item that needs resolution before plan execution`

- **Plan Summary**: Brief summary of what the plan will do

---
## Decisions Made



### 2025-12-23: Phased Implementation Approach
**Decision**: Build structure now, move workspace file later (post-MVP)
- **Rationale**: Avoid retraining during active development
- **Impact**: 
  - Phase 1: Build structure, update workspace roots, keep workspace file in current location
  - Phase 2: Move workspace file after MVP, retrain AI
- **Benefit**: No disruption to current development workflow

### 2025-12-23: Absolute Paths in Workspace File
**Decision**: Use absolute paths (not relative) in workspace file
- **Rationale**: Reliability, clarity, easier updates when structure changes
- **Impact**: All root paths will be absolute paths like `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/apps/hq`

### 2025-12-23: Incremental AGENT_TRAINING_GUIDE.md Updates
**Decision**: Update AGENT_TRAINING_GUIDE.md incrementally with versioning
- **Rationale**: Best practice for documentation, maintains history
- **Impact**: Add "Update History" section, document both current and target states

### 2025-12-23: Planning Cache Document Pattern
**Decision**: Create PLANNING_CACHE.md for tracking decisions during plan development
- **Rationale**: Single source of truth for decisions, reviewable before plan execution
- **Impact**: All planning decisions tracked here, updated in real-time

### 2025-12-23: Documentation Migration Completed
**Decision**: Move all shared documentation from `apps/hq/*DOCUMENTATION/` to `shared_documentation/` organized by category
- **Rationale**: Centralize shared docs, organize by category (architecture/, planning/, training/, watcher/)
- **Impact**: All shared docs now in `shared_documentation/`, HQ-specific docs remain in `apps/hq/*DOCUMENTATION/`
- **Status**: ✅ COMPLETED

### 2025-12-23: Workspace Structure Decision
**Decision**: Construction_Suite as single root (simplified from 6 roots to 1)
- **Rationale**: Simpler navigation, matches filesystem organization, cleaner workspace structure
- **Impact**: Workspace file will be at `Construction_Suite/construction-suite.code-workspace` with single root
- **Old HQ Directory**: Excluded from workspace (kept in filesystem at `app_development/hq/` for AI context only)

### 2025-12-23: Git Repository Strategy
**Decision**: Separate repositories per app (hq, digidoc, watcher) + shared_documentation repository
- **Rationale**: Independent version control, separate release cycles, clear ownership boundaries
- **Impact**: 
  - Existing: `apps/hq/.git` (already configured)
  - To be created: `apps/digidoc/.git`, `shared_documentation/.git`
  - Future: `apps/watcher/.git`

---

## Questions Asked

### 2025-12-23: Workspace File Location
**Question**: Where should workspace file live?
**Answer**: Option C - `~/Dropbox/app_development/` (now `Construction_Suite/construction-suite.code-workspace`)

### 2025-12-23: DigiDoc Relocation
**Question**: Should DigiDoc be moved and reclassified?
**Answer**: Yes - Move to `Construction_Suite/apps/digidoc/`, reclassify as application

### 2025-12-23: Workspace Philosophy
**Question**: Master Control Plane vs individual workspaces?
**Answer**: Master Control Plane for active development, individual workspaces for future maintenance

---

## Assumptions Validated

### 2025-12-23: Agent Retraining Requirements
**Assumption**: Retraining required if workspace file moves to different directory
**Validation**: ✅ Confirmed - AGENT_TRAINING_GUIDE.md must be updated with new paths, new AI session needed

### 2025-12-23: Workspace File Location Impact
**Assumption**: Updating root paths doesn't require retraining if workspace file stays in same location
**Validation**: ✅ Confirmed - Only workspace file location change requires retraining

---

## Open Items

- [x] **Decision made**: Move HQ to Construction_Suite/apps/hq/ - ✅ COMPLETED
- [x] **Decision made**: Exact directory name for Construction Suite - ✅ `Construction_Suite` confirmed
- [x] **Decision made**: Shared documentation subdirectory structure - ✅ COMPLETED (architecture/, planning/, training/, watcher/)
- [ ] **In Progress**: Create new workspace file at Construction_Suite/construction-suite.code-workspace
- [ ] **In Progress**: Initialize Git repositories for digidoc and shared_documentation

---

## Plan Summary

**Objective**: Reorganize workspace structure for Construction Suite ecosystem with phased approach to avoid disrupting active development.

**Key Components**:
1. Create Construction Suite directory structure
2. Move apps to Construction_Suite/apps/
3. Create shared documentation structure
4. Update workspace file with absolute paths (keep file in current location)
5. Incremental updates to AGENT_TRAINING_GUIDE.md
6. Continue MVP development
7. Post-MVP: Move workspace file, retrain AI

**Status**: 
- ✅ Phase 1 (Documentation Migration): COMPLETED
- ⚠️ Phase 2 (Workspace Restructure): IN PROGRESS
  - Workspace structure decision made (single root)
  - Git strategy decision made (separate repos)
  - Workspace file creation pending
  - Git repository initialization pending

---

### 2025-12-23: MVP Development Approach - Vertical Slice Strategy
**Decision**: Use "End-to-End Skeleton First" approach for MVP completion
- **Rationale**: 
  - Discovers integration issues early (queue → task → extraction → API)
  - Validates architecture with real data flow before deep implementation
  - Reduces refactoring risk by validating integration patterns early
  - Matches user preference for fast iteration with architectural validation
- **Approach**: 
  - Phase 1: Build minimal end-to-end skeleton (2-3 hours)
  - Phase 2: Fill critical gaps with real implementations (2-3 hours)
  - Phase 3: Expand to full MVP (remaining time)
- **Impact**: 
  - Fast validation of architecture (2-3 hours vs days)
  - Early discovery of unknown unknowns
  - Clear path to MVP without over-engineering
  - Minimal refactoring risk
- **Status**: ✅ IN PROGRESS - Phase 1 started

### 2025-12-23: Skeleton Development Configuration
**Decision**: Create `development/skeleton.yaml` as single source of truth for all hardcoded test values
- **Rationale**: 
  - Zero chance of forgetting hardcoded values when moving to production
  - Easy to find all test configurations in one place
  - Organized by process/document/setting for clarity
  - Makes migration to production config straightforward
- **Location**: `Construction_Suite/development/skeleton.yaml` (ecosystem-level, not app-specific)
- **Organization**: Nested by process → document → setting
- **Impact**: 
  - All skeleton code reads from skeleton.yaml instead of hardcoded values
  - Clear migration path: replace skeleton.yaml references with config reading
  - Visual verification settings also in skeleton.yaml
- **Status**: ✅ COMPLETED

### 2025-12-23: Visual Verification in Skeleton Workflow
**Decision**: Add visual verification step for preprocessing (before/after images)
- **Rationale**: 
  - User needs to visually verify preprocessing results during skeleton development
  - Ensures preprocessing pipeline is working correctly before moving forward
  - Can pause workflow for manual review
- **Implementation**: 
  - Save original and preprocessed images
  - Create side-by-side comparison image
  - Pause workflow for user review (configurable wait time)
  - Optional auto-open images on macOS
- **Configuration**: `skeleton.yaml` → `preprocessing.visual_verification`
- **Impact**: 
  - Workflow pauses after preprocessing for visual verification
  - Comparison images saved to queue item directory
  - Can be disabled or configured via skeleton.yaml
- **Status**: ✅ COMPLETED

---

**Last Updated**: 2025-12-23 (Added MVP development approach decision)

