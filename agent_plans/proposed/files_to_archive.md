# Files Under Consideration for Archiving

**Purpose**: Track files being considered for archiving during documentation consolidation review.  
**Status**: In Review - No files archived yet  
**Date**: 2025-12-24

---

## Files Identified for Archiving

### Phase 3: Historical Documents

1. `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/shared_documentation/architecture/watcher_adoption_points_INITIAL.md`
   - **Reason from plan**: Historical - Questions Resolved 2025-12-23. See MASTER_ARCHITECTURE.md for current Watcher integration specs.
   - **Status**: ✅ **NO DATA TO EXTRACT** - All information already consolidated into MASTER_ARCHITECTURE.md Watcher Integration section

2. `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/shared_documentation/architecture/watcher_adoption_points_QUESTIONS.md`
   - **Reason from plan**: Historical - Questions Resolved 2025-12-23. See MASTER_ARCHITECTURE.md for current Watcher integration specs.
   - **Status**: ✅ **NO DATA TO EXTRACT** - All information already consolidated into MASTER_ARCHITECTURE.md Watcher Integration section

3. `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/shared_documentation/planning/DOCUMENTATION_STRATEGY_ANALYSIS.md`
   - **Reason from plan**: Analysis document that led to decisions. Decisions have been implemented. Historical reference only.
   - **Content**: Analysis of documentation fragmentation, proposed strategy, implementation plan
   - **Status**: ✅ **NO DATA TO EXTRACT** - All recommendations implemented, purely historical analysis document

4. `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/shared_documentation/planning/format_plans_review.md`
   - **Reason from plan**: One-time review document from 2025-12-23. Recommendation made (use Plan 372785df). Historical reference only.
   - **Content**: Review of two plan files (372785df and 2ece7489) that no longer exist, recommendation to use plan 372785df
   - **Status**: ✅ **NO DATA TO EXTRACT** - Referenced plan files don't exist, field mapping already implemented, purely historical review

5. `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/shared_documentation/planning/workspace_organization_plan.md`
   - **Reason from plan**: Planning document from 2025-12-23. Phase 1 completed, Phase 2 in progress but tracked elsewhere now.
   - **Status**: ✅ **DELETED BY USER** - File no longer exists

6. `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/apps/digidoc/PHASE_A1_IMPLEMENTATION_SUMMARY.md`
   - **Reason from plan**: Historical implementation summary from Phase A.1. Status tracked in DEVELOPMENT_PATHWAY.md now.
   - **Content**: Summary of Phase A.1 implementation (OCR Service Structure, Format Templates, Processing, Confidence Scoring, Extraction Pipeline, Flask API, Laravel Integration)
   - **Status**: ✅ **VERIFIED & UPDATED** - Added missing items to DEVELOPMENT_PATHWAY.md:
     - [C] OCR processor (ocr_processor.py)
     - [C] Text utilities (text_utils.py)
     - [C] Confidence scoring system (confidence_scorer.py)
     - [C] OCR processing service (OcrProcessingService.php)
     - [C] Confidence-based workflow (Laravel)
   - **Result**: All Phase A.1 items now tracked in DEVELOPMENT_PATHWAY.md

### Phase 5: Status Documents (to be consolidated then archived)

7. `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/shared_documentation/planning/QUEUE_IMPLEMENTATION_STATUS.md`
   - **Reason from plan**: Status document from 2025-12-23. Queue implementation is now tracked in DEVELOPMENT_PATHWAY.md.
   - **Action**: Extract unique info, add to DEVELOPMENT_PATHWAY.md, then archive
   - **Status**: Under review

8. `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/apps/digidoc/IMPLEMENTATION_STATUS.md`
   - **Reason from plan**: Status document. Implementation status is now tracked in DEVELOPMENT_PATHWAY.md.
   - **Action**: Extract unique info, add to DEVELOPMENT_PATHWAY.md, then archive
   - **Status**: Under review

---

## Questions and Decisions

### Analysis: watcher_adoption_points_INITIAL.md and watcher_adoption_points_QUESTIONS.md

**Content Type**: Historical review documents comparing WATCHER_SPECIFICATION.md with MASTER_ARCHITECTURE.md

**Information Contained**:
1. User clarifications (Watcher independence, file locations, format support)
2. Question-by-question comparison and resolution status
3. Documentation gaps identified
4. Resolution decisions made

**Current Status**: 
- MASTER_ARCHITECTURE.md already has comprehensive "Watcher Integration" section (lines 1325-1607)
- Most resolved items appear to be incorporated into MASTER_ARCHITECTURE.md
- These files document the *process* of alignment, not just the final specs

**Question**: Should any information from these files be preserved elsewhere?
- User clarifications → Already in MASTER_ARCHITECTURE.md
- Resolution decisions → Already in MASTER_ARCHITECTURE.md  
- Historical context of how decisions were made → Could go in ARCHITECTURE_CHANGELOG.md?
- Review methodology → Not needed (process doc, not spec)

