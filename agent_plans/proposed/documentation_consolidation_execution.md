# Documentation Consolidation Execution Plan

**Purpose**: Execute documentation consolidation actions to eliminate fragmentation, remove duplicates, and archive historical documents.  
**Status**: Ready for Execution  
**Date**: 2025-12-24  
**Created By**: Planning Agent  
**For Execution By**: Implementation Agent

---

## Prerequisites

1. Read this entire plan before starting
2. Review `agent_plans/QUICK_CONTEXT.md` to understand project structure
3. Review `shared_documentation/planning/DOCUMENTATION_CONSOLIDATION_PLAN.md` for original analysis
4. All file paths are relative to workspace root: `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/`

## Important Note: Watcher Documentation Location

**UPDATE (2025-12-24)**: Watcher-specific documentation has been moved from `shared_documentation/watcher/` to `apps/watcher/documentation/` per best practices (app-specific docs belong in app directories). This consolidation plan should update any remaining references to the old location.

---

## Execution Order

### Phase 1: Review QUICK_CONTEXT.md Location

**Task 1.1**: Verify QUICK_CONTEXT.md location and references
- **File**: `agent_plans/QUICK_CONTEXT.md` (moved from `shared_documentation/QUICK_CONTEXT.md`)
- **Action**: 
  1. Read `agent_plans/QUICK_CONTEXT.md`
  2. Check if any references in other docs point to old location (`shared_documentation/QUICK_CONTEXT.md`)
  3. Update any references to point to `agent_plans/QUICK_CONTEXT.md`
  4. Verify QUICK_CONTEXT.md content is current (should reference ARCHITECTURE_CHANGELOG.md)
- **Files to Check**: 
  - `shared_documentation/training/AGENT_TRAINING_GUIDE.md`
  - `shared_documentation/planning/PLANNING_CACHE.md`
  - Any other files that reference QUICK_CONTEXT.md

**Task 1.2**: Decide on QUICK_CONTEXT.md final location
- **Current**: `agent_plans/QUICK_CONTEXT.md`
- **Options**:
  - A) Keep in `agent_plans/` (agent-specific location)
  - B) Move back to `shared_documentation/QUICK_CONTEXT.md` (shared location)
  - C) Keep copy in both locations
- **Recommendation**: Keep in `agent_plans/` if it's agent-specific, or move to `shared_documentation/` if it's for all developers
- **Action**: Document decision, update references accordingly

---

### Phase 2: Create Archive Directory

**Task 2.1**: Create archive directory structure
- **Action**: Create `shared_documentation/archive/` directory
- **Structure**:
  ```
  shared_documentation/archive/
  ├── planning/          # Archived planning docs
  ├── architecture/      # Archived architecture docs
  └── README.md         # Archive index/explanation
  ```

**Task 2.2**: Create archive README
- **File**: `shared_documentation/archive/README.md`
- **Content**: Explain archive purpose, organization, and how to find historical documents

---

### Phase 3: Archive Historical Documents

**Task 3.1**: Archive watcher adoption points documents
- **Files**:
  - `shared_documentation/architecture/watcher_adoption_points_INITIAL.md` → `shared_documentation/archive/architecture/watcher_adoption_points_INITIAL.md`
  - `shared_documentation/architecture/watcher_adoption_points_QUESTIONS.md` → `shared_documentation/archive/architecture/watcher_adoption_points_QUESTIONS.md`
- **Action**: 
  1. Move files to archive
  2. Add header note: "**ARCHIVED**: Historical - Questions Resolved 2025-12-23. See MASTER_ARCHITECTURE.md for current Watcher integration specs."

**Task 3.2**: Archive planning documents
- **Files**:
  - `shared_documentation/planning/DOCUMENTATION_STRATEGY_ANALYSIS.md` → `shared_documentation/archive/planning/DOCUMENTATION_STRATEGY_ANALYSIS.md`
  - `shared_documentation/planning/format_plans_review.md` → `shared_documentation/archive/planning/format_plans_review.md`
  - `shared_documentation/planning/workspace_organization_plan.md` → `shared_documentation/archive/planning/workspace_organization_plan.md`
- **Action**: 
  1. Move files to archive
  2. Add header note with archive reason and date

**Task 3.3**: Archive implementation summary
- **File**: `apps/digidoc/PHASE_A1_IMPLEMENTATION_SUMMARY.md` → `shared_documentation/archive/planning/PHASE_A1_IMPLEMENTATION_SUMMARY.md`
- **Action**: 
  1. Move file to archive
  2. Add header note: "**ARCHIVED**: Historical - Phase A.1 Complete. Status tracked in DEVELOPMENT_PATHWAY.md"

---

### Phase 4: Mark Complete Documents

**Task 4.1**: Mark DOCUMENTATION_IMPLEMENTATION_PLAN.md as complete
- **File**: `shared_documentation/planning/DOCUMENTATION_IMPLEMENTATION_PLAN.md`
- **Action**: 
  1. Add header note after title: "**✅ COMPLETED** - Kept for historical reference. All tasks completed 2025-12-24."
  2. Keep file in place (useful as reference)

---

### Phase 5: Consolidate Status Documents

**Task 5.1**: Consolidate QUEUE_IMPLEMENTATION_STATUS.md
- **Source**: `shared_documentation/planning/QUEUE_IMPLEMENTATION_STATUS.md`
- **Target**: `shared_documentation/planning/DEVELOPMENT_PATHWAY.md`
- **Action**:
  1. Read QUEUE_IMPLEMENTATION_STATUS.md
  2. Extract any unique information not already in DEVELOPMENT_PATHWAY.md
  3. Add extracted info to DEVELOPMENT_PATHWAY.md Queue System section (if missing)
  4. Archive QUEUE_IMPLEMENTATION_STATUS.md → `shared_documentation/archive/planning/QUEUE_IMPLEMENTATION_STATUS.md`
  5. Add header note: "**ARCHIVED**: Consolidated into DEVELOPMENT_PATHWAY.md 2025-12-24"

**Task 5.2**: Consolidate IMPLEMENTATION_STATUS.md
- **Source**: `apps/digidoc/IMPLEMENTATION_STATUS.md`
- **Target**: `shared_documentation/planning/DEVELOPMENT_PATHWAY.md`
- **Action**:
  1. Read IMPLEMENTATION_STATUS.md
  2. Extract any unique information not already in DEVELOPMENT_PATHWAY.md
  3. Add extracted info to DEVELOPMENT_PATHWAY.md (if missing)
  4. Archive IMPLEMENTATION_STATUS.md → `shared_documentation/archive/planning/IMPLEMENTATION_STATUS.md`
  5. Add header note: "**ARCHIVED**: Consolidated into DEVELOPMENT_PATHWAY.md 2025-12-24"

---

### Phase 6: Delete Duplicate Files

**Task 6.1**: Delete duplicate REDIS_INSTALLATION.md
- **File**: `apps/digidoc/REDIS_INSTALLATION.md`
- **Reason**: Duplicate of `development/REDIS_INSTALLATION.md` (ecosystem-level guide)
- **Action**: Delete file (keep `development/REDIS_INSTALLATION.md`)

**Task 6.2**: Check and remove empty *DOCUMENTATION/ directory
- **Directory**: `apps/digidoc/*DOCUMENTATION/`
- **Action**: 
  1. Verify directory is empty
  2. If empty, remove directory
  3. If not empty, list contents and report

---

### Phase 7: Review and Decide on Remaining Files

**Task 7.1**: Review TEMPLATE_SEARCH_LOGIC.md
- **File**: `shared_documentation/architecture/TEMPLATE_SEARCH_LOGIC.md`
- **Current Status**: KEEP (technical reference)
- **Action**: 
  1. Read file to understand its purpose
  2. Decide: Keep in architecture/ or move to planning/slices/?
  3. **Recommendation**: Keep in architecture/ as technical reference (not a design doc)
  4. Document decision

**Task 7.2**: Review workspace_best_practices_guidance.md
- **File**: `shared_documentation/planning/workspace_best_practices_guidance.md`
- **Current Status**: KEEP (consider consolidating)
- **Action**:
  1. Read file
  2. Compare with `shared_documentation/training/AGENT_TRAINING_GUIDE.md`
  3. Check for overlap
  4. **Decision Options**:
     - A) Keep as-is (unique content)
     - B) Consolidate into AGENT_TRAINING_GUIDE.md
     - C) Move to development/ directory (if it's dev environment guidance)
  5. **Recommendation**: Review content, if unique keep, if redundant consolidate
  6. Document decision and execute

---

### Phase 8: Update Cross-References

**Task 8.1**: Update references to archived files
- **Action**: Search for references to archived files and update:
  - References to `watcher_adoption_points_INITIAL.md` → point to archive or MASTER_ARCHITECTURE.md
  - References to `watcher_adoption_points_QUESTIONS.md` → point to archive or MASTER_ARCHITECTURE.md
  - References to `DOCUMENTATION_STRATEGY_ANALYSIS.md` → point to archive
  - References to `format_plans_review.md` → point to archive
  - References to `workspace_organization_plan.md` → point to archive
  - References to `QUEUE_IMPLEMENTATION_STATUS.md` → point to DEVELOPMENT_PATHWAY.md
  - References to `IMPLEMENTATION_STATUS.md` → point to DEVELOPMENT_PATHWAY.md
  - References to `PHASE_A1_IMPLEMENTATION_SUMMARY.md` → point to archive or DEVELOPMENT_PATHWAY.md

**Task 8.2**: Update references to QUICK_CONTEXT.md location
- **Action**: Update any references from `shared_documentation/QUICK_CONTEXT.md` to `agent_plans/QUICK_CONTEXT.md` (or vice versa based on Task 1.2 decision)

---

### Phase 9: Final Verification

**Task 9.1**: Verify archive structure
- **Action**: 
  1. List all files in `shared_documentation/archive/`
  2. Verify archive README.md exists
  3. Verify all archived files have header notes

**Task 9.2**: Verify no broken references
- **Action**: 
  1. Search for references to archived files
  2. Verify all references are updated or point to correct locations
  3. Check for any broken links

**Task 9.3**: Update DOCUMENTATION_CONSOLIDATION_PLAN.md
- **File**: `shared_documentation/planning/DOCUMENTATION_CONSOLIDATION_PLAN.md`
- **Action**: 
  1. Mark plan as "✅ EXECUTED"
  2. Add execution summary
  3. List all actions taken

---

## Decisions Made (Pre-Approved)

1. **Archive Location**: Create `shared_documentation/archive/` with subdirectories (planning/, architecture/)
2. **TEMPLATE_SEARCH_LOGIC.md**: Keep in architecture/ (technical reference, not design doc)
3. **Archive Method**: Move files to archive/ and add header notes (don't just mark in-place)
4. **Consolidation Method**: Extract unique info, add to target doc, then archive source

---

## Questions Requiring User Input

1. **QUICK_CONTEXT.md Location**: Should it stay in `agent_plans/` or move to `shared_documentation/`?
   - **Recommendation**: If it's for AI agents only, keep in `agent_plans/`. If it's for all developers, move to `shared_documentation/`.

2. **workspace_best_practices_guidance.md**: After review, should it be consolidated or kept separate?
   - **Action**: Review content first, then decide based on overlap analysis.

---

## Success Criteria

- [ ] All historical documents archived with header notes
- [ ] All duplicate files deleted
- [ ] All status documents consolidated into DEVELOPMENT_PATHWAY.md
- [ ] All cross-references updated
- [ ] Archive directory structure created
- [ ] Archive README.md created
- [ ] QUICK_CONTEXT.md location verified and references updated
- [ ] No broken references remain
- [ ] DOCUMENTATION_CONSOLIDATION_PLAN.md marked as executed

---

## Notes

- **Be careful**: Don't delete files until you've verified they're truly duplicates or have been consolidated
- **Archive everything**: When in doubt, archive rather than delete (can always delete later)
- **Header notes**: Always add header notes to archived files explaining why they were archived
- **Cross-references**: Update all references to maintain documentation integrity
- **Verification**: Double-check all actions before marking complete

---

**Ready for Execution**

