# Agent Training Guide: Construction Suite Ecosystem

**Purpose**: This document provides comprehensive context for AI agents working on the Construction Suite ecosystem (HQ, DigiDoc, Watcher). It captures architectural decisions, user preferences, current state, and development patterns.

**Last Updated**: 2025-12-24  
**Status**: Active Development - Construction Suite Ecosystem

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Critical Architecture Documents](#critical-architecture-documents)
3. [Core Architecture Principles](#core-architecture-principles)
4. [User Communication Preferences](#user-communication-preferences)
5. [Current Milestone Status](#current-milestone-status)
6. [Technical Patterns and Decisions](#technical-patterns-and-decisions)
7. [File Structure and Organization](#file-structure-and-organization)
8. [Development Workflow](#development-workflow)
9. [Critical Alignment Requirements](#critical-alignment-requirements)
10. [Common Pitfalls to Avoid](#common-pitfalls-to-avoid)
11. [Information Verification and Cross-Checking Rules](#information-verification-and-cross-checking-rules)
12. [Workspace Organization and Context Preservation](#workspace-organization-and-context-preservation)
13. [Planning Cache Workflow](#planning-cache-workflow)
14. [Development Errors Log](#development-errors-log)

---

## Project Overview

**Construction Suite** is an ecosystem of interconnected applications:
- **HQ**: Master application (web-based dashboard, Laravel PHP)
- **DigiDoc**: OCR application (Python, offline-first LLM OCR)
- **Watcher**: File monitoring daemon (future, separate app)

**DigiDoc** provides:
- Image preprocessing pipeline (deskew, denoise, binarize, normalize, border removal)
- Template matching system (structural fingerprint, feature detection, text fallback)
- Field extraction with confidence scoring
- Streamlit GUI for visual review and inspection
- Queue-based asynchronous processing (RQ for MVP, Celery-ready architecture)

### Technology Stack

- **Backend**: Python 3.12+ (DigiDoc OCR service), Laravel PHP (HQ application)
- **OCR Engine**: Tesseract
- **Image Processing**: OpenCV (cv2)
- **GUI**: Streamlit (web-based, for development verification)
- **Queue**: RQ (Redis Queue) for MVP, abstraction layer for Celery migration
- **Database**: SQLite (local template cache), Laravel MySQL (main database)
- **LLM**: Ollama (local, offline-first)
- **Storage**: Local filesystem with configurable base path

### Project Location - Construction Suite Ecosystem

**Workspace File**: `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/construction-suite.code-workspace`  
**Note**: Workspace file located at Construction Suite root. Single root structure simplifies navigation and matches filesystem organization.

**Workspace Structure**:
- **Single Root**: `Construction_Suite/` contains all apps and shared documentation nested within
- **Old HQ Directory**: Excluded from workspace (kept in filesystem at `app_development/hq/` for AI context preservation only)

**Workspace Root** (single root):
- **Construction Suite**: `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite`
  - Contains: `apps/` (hq, digidoc, watcher), `shared_documentation/`

**Construction Suite Structure**:
```
app_development/
|---- Construction_Suite/
|        |── construction-suite.code-workspace (workspace file - single root)
|        |---- shared_documentation/          ✅ All shared docs migrated here
|        |      |── architecture/
|        |      |      ├── MASTER_ARCHITECTURE.md (Ecosystem Architecture)
|        |      |      └── ARCHITECTURE_CHANGELOG.md
|        |      |── apps/
|        |      |      ├── digidoc/
|        |      |      |      └── *DOCUMENTATION/
|        |      |      |            └── ARCHITECTURE.md (DigiDoc Architecture)
|        |      |      ├── ARCHITECTURE_CHANGELOG.md
|        |      |      ├── watcher_adoption_points_INITIAL.md
|        |      |      └── watcher_adoption_points_QUESTIONS.md
|        |      |── planning/
|        |      |      ├── SCHEDULE.md
|        |      |      ├── NEXT_PLAN_STEPS.md
|        |      |      ├── PLANNING_CACHE.md
|        |      |      ├── format_plans_review.md
|        |      |      ├── workspace_best_practices_guidance.md
|        |      |      └── workspace_organization_plan.md
|        |      |── training/
|        |      |      ├── AGENT_TRAINING_GUIDE.md (this file)
|        |      |      └── LATENCY_DIAGNOSIS.md
|        |      └── watcher/
|        |             ├── WATCHER_SPECIFICATION.md
|        |             └── watcher_api_design_analysis.md
|        └── apps/
|                 ├── digidoc/
|                 ├── hq/
|                 │   └── *DOCUMENTATION/     # HQ-specific docs only
|                 └── watcher/
```

**Documentation Locations**:
- **Shared Documentation**: `Construction_Suite/shared_documentation/` (organized by category)
- **HQ-Specific Docs**: `Construction_Suite/apps/hq/*DOCUMENTATION/`
- **DigiDoc-Specific Docs**: `Construction_Suite/apps/digidoc/*DOCUMENTATION/`

---

## Critical Architecture Documents

### 1. MASTER_ARCHITECTURE.md (Ecosystem Architecture)

**Location**: `Construction_Suite/shared_documentation/architecture/MASTER_ARCHITECTURE.md`

**Purpose**: The definitive source of truth for Construction Suite ecosystem architecture, app relationships, and integration contracts.

**Key Sections**:
- Ecosystem Overview (Construction Suite structure)
- App Layer Architecture (DigiDoc, HQ, Watcher)
- App Relationships & Data Flow
- Integration Contracts (API contracts, path handling specifications)
- Shared Architecture Principles (offline-first, configuration-driven, modular, path handling)
- Development Workflow

**CRITICAL**: All ecosystem-level decisions and integration contracts MUST align with MASTER_ARCHITECTURE.md.

### 1a. DigiDoc ARCHITECTURE.md (App-Specific)

**Location**: `Construction_Suite/apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md`

**Purpose**: DigiDoc-specific architecture and implementation details.

**Key Sections**:
- Ecosystem Context (DigiDoc's role in ecosystem)
- System Overview (DigiDoc workflow)
- Preprocessing Pipeline (5-step process with exact methods)
- Template Matching System (three-tier approach with weights)
- Extraction Pipeline
- Review Queue & GUI
- File Storage Architecture (queue item directory structure)
- Configuration Management (all parameters configurable)
- Workflow Implementation (granular processing steps)
- Risk Mitigations
- Module Structure

**CRITICAL**: All DigiDoc code changes MUST align with DigiDoc ARCHITECTURE.md. For ecosystem context, see MASTER_ARCHITECTURE.md.

### Path Handling Requirements

**CRITICAL**: All apps in the Construction Suite ecosystem use absolute paths for file operations and API communications.

**Key Requirements**:
1. **Apps Use Absolute Paths Internally**: All apps (hq, digidoc, watcher) use absolute paths for internal file operations
2. **API Communications Require Absolute Paths**: The `file_path` parameter in all API requests must be an absolute path
3. **Path Expansion**: Configuration paths using `~` or environment variables are expanded to absolute paths using `os.path.expanduser()` or equivalent
4. **Configuration Loading**: Paths with `~` in configuration files are expanded to absolute paths during configuration loading, before any file operations

**Rationale**:
- Stateless services need explicit paths (no assumptions about working directories)
- Cross-system compatibility (different user accounts, deployment environments)
- Eliminates ambiguity in file location

**Examples**:
- ✅ Correct: `"file_path": "/Users/username/Dropbox/Application Data/DigiDoc/queue/file.pdf"`
- ❌ Incorrect: `"file_path": "queue/file.pdf"` (relative path)
- ✅ Correct: Configuration `storage_base: "~/digidoc_storage"` → expanded to `/Users/username/digidoc_storage`

**Reference**: See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" section for complete requirements.

### 2. SCHEDULE.md and DEVELOPMENT_PATHWAY.md

**Location**: `Construction_Suite/shared_documentation/planning/SCHEDULE.md` and `DEVELOPMENT_PATHWAY.md`

**Purpose**: Track project milestones, chunks, and immediate next steps.

### 3. PLANNING_CACHE.md

**Location**: `Construction_Suite/shared_documentation/planning/PLANNING_CACHE.md`

**Purpose**: Real-time decision tracking during plan development. Updated as decisions are made, reviewed before plan execution.

### 4. Current Milestone Plans

**Location**: `.cursor/plans/` directory (check for latest)

**Purpose**: Specific implementation plans for milestones and features.

---

## Core Architecture Principles

### 1. Offline-First Operation (CRITICAL)

**Rule**: DigiDoc must operate 100% offline with zero internet connection to cloud hosting providers or LLM host providers.

**Implications**:
- All processing occurs locally
- Models, templates, caches stored locally
- LLM operations (Ollama) run locally
- No external API dependencies for core functionality
- Cloud mirroring is post-MVP concern

**Always state this explicitly** in documentation and code comments.

### 2. Configuration-Driven (GLOBAL PRINCIPLE)

**Rule**: No thresholds, limits, or decision parameters are hardcoded. All must be configurable via configuration files.

**What Must Be Configurable**:
- All confidence thresholds
- All scoring weights
- All retry limits
- All file paths
- All API endpoints
- All preprocessing parameters (DPI, denoise level, binarization method, etc.)

**Implementation**:
- Configuration file: `digidoc_config.yaml` in DigiDoc root
- Configuration loader: `ocr_service/config.py`
- Environment variable override support (e.g., `DIGIDOC_TARGET_DPI`)

**Violation**: Any hardcoded threshold, weight, or path is a violation of this principle.

### 3. Modular Development

**Rule**: Build small modules at a time with incremental testing.

**Approach**:
- Each sub-plan must have its own plan before execution
- Graphical output steps for model learning and preprocessing progress
- Incremental implementation with testing at each stage
- Small, testable modules

### 4. Fast Communication Loop

**Rule**: Avoid long "Planning next steps" queues. Maintain fast back-and-forth.

**User Preference**:
- Ask ONE question at a time (not lists)
- Only ask when questions are complete should you "build plan"
- Avoid long planning phases
- Provide visual progress tracking

### 5. Planning Cache Document Pattern

**Rule**: Track decisions in real-time during plan development using PLANNING_CACHE.md

**Workflow**:
1. When starting to build a plan, create/update `PLANNING_CACHE.md`
2. As decisions are made, questions asked, assumptions validated → update cache immediately
3. Before presenting plan to user, summarize cache in plan overview
4. User reviews cache before approving plan
5. After plan execution, archive cache or clear for next plan

**Location**: `Construction_Suite/shared_documentation/planning/PLANNING_CACHE.md`

---

## User Communication Preferences

### Question Strategy

**DO**:
- Ask one question at a time
- Wait for answer before asking next question
- Only build plan after all questions are answered

**DON'T**:
- Prepare "question lists" for the plan
- Ask multiple questions in one message
- Start planning before questions are complete

### Planning and Execution

**DO**:
- Create concise, actionable plans
- Break work into small, executable tasks (15-30 minute chunks)
- Reference specific file paths and code snippets
- Use mermaid diagrams for complex flows (when helpful)
- Update PLANNING_CACHE.md in real-time during plan development

**DON'T**:
- Create overly verbose plans
- Over-engineer simple tasks
- Make assumptions without asking
- Take multiple minutes for simple operations

### Documentation

**DO**:
- Update MASTER_ARCHITECTURE.md when ecosystem-level architectural decisions are made
- Update DigiDoc ARCHITECTURE.md when DigiDoc-specific architectural decisions are made
- Keep documentation live and current
- Reference specific sections in the appropriate architecture document when aligning code
- Update PLANNING_CACHE.md during plan development

**DON'T**:
- Create duplicate documentation
- Leave documentation stale
- Make architectural changes without updating the appropriate architecture document (MASTER_ARCHITECTURE.md for ecosystem, DigiDoc ARCHITECTURE.md for DigiDoc)

### Code Changes

**DO**:
- Align all changes with the appropriate architecture document (MASTER_ARCHITECTURE.md for ecosystem, DigiDoc ARCHITECTURE.md for DigiDoc)
- Remove hardcoded values (use config)
- Follow existing patterns
- Test incrementally

**DON'T**:
- Hardcode thresholds or paths
- Deviate from architecture documents without discussion
- Make large changes without breaking into modules

---

## Current Milestone Status

### Completed: subject_and_template_visual_match (2025-12-19)

**Goal (Achieved)**:
Display in Streamlit web browser:
- Original scan image from queue (left panel)
- Preprocessed version (middle panel)
- Template match visualization with zone overlays (right panel)

All three views side-by-side, proportionally scaled for equal display.

**Status**: ✅ All 24 chunks completed across 6 phases:
- ✅ Configuration System (4 chunks)
- ✅ Preprocessing Pipeline (8 chunks)
- ✅ File Storage Utilities (2 chunks)
- ✅ Structural Fingerprint Matching (3 chunks)
- ✅ Streamlit GUI (5 chunks)
- ✅ Integration and Testing (2 chunks)

**Next Milestone**: To be determined (likely extraction pipeline or queue system completion)

---

## Technical Patterns and Decisions

### Preprocessing Pipeline

**Exact Methods** (from MASTER_ARCHITECTURE.md):
1. Deskew: `HoughLinesP + rotation` (not `minAreaRect`)
2. Denoise: `fastNlMeansDenoising` (not `bilateralFilter`)
3. Binarize: Adaptive threshold (Otsu or Gaussian)
4. Scale Normalization: 300 DPI with cubic interpolation
5. Border Removal: Contour analysis

**Order**: Deskew → Denoise → Binarize → Scale Normalization → Border Removal

**All parameters**: Load from configuration, no hardcoded values.

### Template Matching

**Three-Tier Approach** (from MASTER_ARCHITECTURE.md):
1. **Structural Fingerprint** (70% weight): Ratio-based, DPI/scale invariant
2. **Feature Detection** (20% weight): ORB keypoints on logo regions (post-MVP)
3. **Text Fallback** (10% weight): Text pattern matching (post-MVP)

**For MVP**: Only structural fingerprint matching is required.

**Critical**: Structural fingerprints must use ratios (position/size relative to image dimensions), NOT absolute pixels.

### File Storage Pattern

**Queue Item Directory Structure**:
```
{storage_base}/queue/{queue_item_id}/
├── original.{ext}
├── preprocessed.png
├── template_match.png
├── preprocessing_metadata.json
└── (future: extracted_fields.json, audit_log.json)
```

**Storage Base**: Configurable, default `~/digidoc_storage/`

**Benefits**:
- Easy cleanup
- Crash recovery (resume from queue item directory)
- Audit trail per item
- Soft error handling (continue where left off)

### Configuration Pattern

**File**: `digidoc_config.yaml` in DigiDoc root (`Construction_Suite/apps/digidoc/`)

**Loader**: `ocr_service/config.py`

**Sections**:
- `preprocessing`: All preprocessing parameters
- `paths`: All file paths (with variable substitution)
- `scoring`: All weights and thresholds
- `thresholds`: Confidence thresholds
- `api`: API endpoints (port, enqueue_endpoint, auth_required)
- `queue`: Queue configuration
- `database`: Database configuration
- `llm`: LLM (Ollama) configuration

**Environment Variable Override**: All values can be overridden via environment variables (e.g., `DIGIDOC_TARGET_DPI`).

### Queue Abstraction Pattern

**Architecture**: Abstraction layer for RQ (MVP) and Celery (post-MVP)

**Location**: `ocr_service/queue/` (to be created post-MVP)

**Pattern**: Queue-agnostic task functions in `ocr_service/tasks/`, adapter layer for queue implementation.

---

## File Structure and Organization

### Construction Suite Structure

```
app_development/
|---- Construction_Suite/
|        |── construction-suite.code-workspace (future - post-MVP)
|        |---- shared_documentation/
|        |      |── architecture/
|        |      |      ├── MASTER_ARCHITECTURE.md (Ecosystem Architecture)
|        |      |      └── ARCHITECTURE_CHANGELOG.md
|        |      |── apps/
|        |      |      ├── digidoc/
|        |      |      |      └── *DOCUMENTATION/
|        |      |      |            └── ARCHITECTURE.md (DigiDoc Architecture)
|        |      |      ├── ARCHITECTURE_CHANGELOG.md
|        |      |      └── watcher_adoption_points_*.md
|        |      |── planning/
|        |      |      ├── SCHEDULE.md
|        |      |      ├── NEXT_PLAN_STEPS.md
|        |      |      ├── PLANNING_CACHE.md
|        |      |      └── format_plans_review.md
|        |      |── training/
|        |      |      └── AGENT_TRAINING_GUIDE.md (this file)
|        |      └── watcher/
|        |             ├── WATCHER_SPECIFICATION.md
|        |             └── watcher_api_design_analysis.md
|        └── apps/
|                 ├── digidoc/
|                 │   ├── digidoc_config.yaml
|                 │   ├── ocr_service/
|                 │   │   ├── config.py
|                 │   │   ├── utils/
|                 │   │   │   ├── image_preprocessing.py
|                 │   │   │   └── file_utils.py
|                 │   │   ├── matching/
|                 │   │   │   └── structural.py
|                 │   │   ├── tasks/
|                 │   │   │   ├── matching_task.py
|                 │   │   │   └── process_for_visualization.py
|                 │   │   ├── gui/
|                 │   │   │   ├── app.py
|                 │   │   │   └── pages/
|                 │   │   └── database/
|                 │   │       └── models.py
|                 │   └── requirements_ocr.txt
|                 ├── hq/
|                 │   ├── app/                    # Laravel PHP application
|                 │   │   ├── Services/Ocr/
|                 │   │   └── Models/
|                 │   ├── config/
|                 │   │   └── services.php
|                 │   └── *DOCUMENTATION/         # HQ-specific docs
|                 └── watcher/                    # Future
```

### Workspace File Location

**Current**: `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/construction-suite.code-workspace`

**Workspace Structure**: Single root at Construction_Suite level
- All apps and shared documentation accessible via single root
- Old hq directory (`app_development/hq/`) excluded from workspace (kept in filesystem for AI context only)
- Simplifies navigation and matches filesystem organization

**Rationale**: Single root structure provides cleaner workspace organization, easier navigation, and aligns with the actual filesystem structure. Old hq directory remains in filesystem but is not included in workspace to avoid confusion.

---

## Development Workflow

### Virtual Environment Management (CRITICAL)

**Rule**: Every Python app MUST have its own `.venv` directory.

**Automatic Activation**: The suite uses `direnv` for automatic virtual environment activation:
- Each app directory contains a `.envrc` file
- direnv automatically activates `.venv` when you `cd` into the directory
- No manual `source .venv/bin/activate` needed
- direnv hook is installed in `~/.zshrc`

**Setup**:
- direnv is installed system-wide via Homebrew
- Each app's `.envrc` is configured and allowed
- When creating new apps, always create `.envrc` and run `direnv allow`

**Requirements Files**:
- **App-specific**: `apps/{app}/requirements.txt` - Production dependencies (pinned with `==`)
- **Suite-wide dev tools**: `development/requirements-dev.txt` - Testing, linting, tooling (minimum versions with `>=`)
- **Installation**: `pip install -r requirements.txt && pip install -r ../../development/requirements-dev.txt`

**Version Pinning Strategy**:
- **Production dependencies** (`requirements.txt`): Pin exact versions with `==` for reproducibility
  - Example: `redis==7.1.0`, `rq==2.6.1`
- **Development dependencies** (`requirements-dev.txt`): Use minimum versions with `>=` for flexibility
  - Example: `pytest>=7.4.0`, `black>=23.7.0`
- **Rationale**: Production needs exact versions for reproducibility; dev tools can be flexible

**Standards Documentation**: See `development/VENV_STANDARDS.md` for complete requirements.

**For AI Agents**: When creating or modifying Python apps:
1. Always create `.venv` in app directory
2. Always create `.envrc` for direnv
3. Always update `.gitignore` with Python venv patterns
4. Always install suite-wide dev tools from `development/requirements-dev.txt`
5. Never move or copy venvs - always recreate if needed

### Development Workflow

### Starting Work on This Project

1. **Read appropriate architecture document first** (MASTER_ARCHITECTURE.md for ecosystem, DigiDoc ARCHITECTURE.md for DigiDoc)
   - Understand core principles
   - Understand preprocessing pipeline
   - Understand file storage structure
   - Understand configuration requirements

2. **Check Current Milestone Status**
   - Read `SCHEDULE.md` for completed milestones
   - Read `SCHEDULE.md` for current focus and immediate next steps
   - Read `DEVELOPMENT_PATHWAY.md` for feature-level tracking
   - Check `PLANNING_CACHE.md` for active planning decisions

3. **Review This Training Guide**
   - Understand user preferences
   - Understand technical patterns
   - Understand common pitfalls
   - Understand workspace structure

4. **Ask Questions (One at a Time)**
   - If anything is unclear, ask one question
   - Wait for answer before proceeding
   - Only build plan after questions are complete
   - Update PLANNING_CACHE.md as decisions are made

### Making Code Changes

1. **Check Architecture Document Alignment** (MASTER_ARCHITECTURE.md for ecosystem, DigiDoc ARCHITECTURE.md for DigiDoc)
   - Does this change align with architecture?
   - Are all parameters configurable?
   - Does file storage follow structure?

2. **Verify Information Sources**
   - If using web search results, cross-check against:
      - Platform standards
      - Multiple authoritative sources
      - User-provided information
      - Existing project patterns
   - If user provides conflicting information, verify it and use it

3. **Remove Hardcoded Values**
   - Replace with config lookups
   - Add to `digidoc_config.yaml` if new parameter
   - Support environment variable override

4. **Follow Preprocessing Methods**
   - Use exact methods from the appropriate architecture document
   - Follow correct order
   - Load all parameters from config

5. **Test Incrementally**
   - Test each module as you build
   - Verify alignment with architecture
   - Check file storage structure

6. **Update Documentation**
   - Update the appropriate architecture document if architectural decision made
   - Update this guide if pattern changes
   - Update PLANNING_CACHE.md during plan development
   - Keep documentation current

### Planning New Features

1. **Reference appropriate architecture document** (MASTER_ARCHITECTURE.md for ecosystem, DigiDoc ARCHITECTURE.md for DigiDoc)
   - Check if feature is already specified
   - Understand how it fits into architecture
   - Identify alignment requirements

2. **Create/Update PLANNING_CACHE.md**
   - Track decisions in real-time
   - Document questions asked
   - Record assumptions validated

3. **Ask User (One Question at a Time)**
   - Clarify scope
   - Understand requirements
   - Get approval for approach
   - Update PLANNING_CACHE.md with each decision

4. **Create Plan**
   - Only after questions are complete
   - Reference specific files and code
   - Break into small, executable tasks (15-30 minute chunks)
   - Include alignment requirements
   - Summarize PLANNING_CACHE.md in plan overview

5. **Execute Incrementally**
   - Build small modules
   - Test as you go
   - Verify alignment

---

## Critical Alignment Requirements

### When Implementing Preprocessing

**MUST**:
- Use `HoughLinesP` for deskew (not `minAreaRect`)
- Use `fastNlMeansDenoising` for denoise (not `bilateralFilter`)
- Follow order: Deskew → Denoise → Binarize → Scale Normalization → Border Removal
- Load all parameters from config (no hardcoded values)
- Save to queue item directory structure

**MUST NOT**:
- Hardcode thresholds, DPI, or method choices
- Use wrong preprocessing methods
- Skip configuration loading
- Save files to wrong locations

### When Implementing Template Matching

**MUST**:
- Use ratio-based structural fingerprints (not absolute pixels)
- Store zone positions/sizes as ratios relative to image dimensions
- Use 70% weight for structural matching
- Compare using Euclidean distance or SSIM on ratios

**MUST NOT**:
- Use absolute pixel positions (not DPI/scale invariant)
- Hardcode matching weights
- Skip ratio computation

### When Implementing File Storage

**MUST**:
- Use configurable `storage_base` (default `~/digidoc_storage/`)
- Create queue item directory: `{storage_base}/queue/{queue_item_id}/`
- Save original as `{queue_item_id}/original.{ext}`
- Save preprocessed as `{queue_item_id}/preprocessed.png`
- Load storage_base from config

**MUST NOT**:
- Hardcode storage paths
- Use different directory structure
- Skip queue item directory creation

### When Implementing Configuration

**MUST**:
- Create `digidoc_config.yaml` with all parameters
- Create `ocr_service/config.py` loader
- Support environment variable overrides
- Load all parameters from config (no hardcoded values)

**MUST NOT**:
- Hardcode any thresholds, weights, or paths
- Skip configuration system
- Use different config file format without approval

---

## Common Pitfalls to Avoid

### 1. Hardcoding Values

**Pitfall**: Adding hardcoded thresholds, weights, or paths.

**Solution**: Always use configuration. If a new parameter is needed, add it to `digidoc_config.yaml` and load it via `config.py`.

**Example Violation**:
```python
# BAD
confidence_threshold = 0.85
target_dpi = 300

# GOOD
from ocr_service.config import get_config
config = get_config()
confidence_threshold = config.thresholds.auto_match
target_dpi = config.preprocessing.target_dpi
```

### 2. Using Wrong Preprocessing Methods

**Pitfall**: Using `minAreaRect` for deskew or `bilateralFilter` for denoise.

**Solution**: Always check DigiDoc ARCHITECTURE.md for exact methods. Use `HoughLinesP` for deskew and `fastNlMeansDenoising` for denoise.

### 3. Wrong Preprocessing Order

**Pitfall**: Not following the correct preprocessing order.

**Solution**: Order must be: Deskew → Denoise → Binarize → Scale Normalization → Border Removal.

### 4. Absolute Pixels in Template Matching

**Pitfall**: Using absolute pixel positions in structural fingerprints.

**Solution**: Always use ratios (position/size relative to image dimensions) for DPI/scale invariance.

**Example**:
```python
# BAD
fingerprint = {
    "header": {"x": 100, "y": 50, "width": 800, "height": 200}
}

# GOOD
fingerprint = {
    "header": {
        "x_ratio": 0.1,      # 100 / 1000 (image width)
        "y_ratio": 0.05,     # 50 / 1000 (image height)
        "width_ratio": 0.8,  # 800 / 1000
        "height_ratio": 0.2  # 200 / 1000
    }
}
```

### 5. Wrong File Storage Structure

**Pitfall**: Not following queue item directory structure.

**Solution**: Always use `{storage_base}/queue/{queue_item_id}/` structure with configurable `storage_base`.

### 6. Asking Multiple Questions

**Pitfall**: Asking multiple questions in one message.

**Solution**: Ask one question at a time, wait for answer, then ask next question.

### 7. Planning Before Questions Complete

**Pitfall**: Creating plan before all questions are answered.

**Solution**: Only build plan after all questions are complete.

### 8. Not Updating Architecture Documents

**Pitfall**: Making architectural changes without updating documentation.

**Solution**: Always update the appropriate architecture document (MASTER_ARCHITECTURE.md for ecosystem, DigiDoc ARCHITECTURE.md for DigiDoc) when architectural decisions are made.

### 9. Trusting Single Sources Without Verification

**Pitfall**: Accepting information from a single source (web search, documentation, or another AI) without cross-checking against established conventions, user-provided information, or multiple authoritative sources.

**Solution**: 
- Always cross-check information from web searches against:
  1. Standard platform conventions (e.g., macOS Filesystem Hierarchy Standard)
  2. User-provided information or corrections
  3. Multiple authoritative sources
  4. Existing project documentation
- Prioritize user knowledge: If user provides information that conflicts with a search result, trust the user and verify their information
- Acknowledge uncertainty: If sources conflict, ask the user (one question at a time) rather than guessing
- Verify against standards: For platform-specific conventions (file paths, directory structures), verify against official platform documentation or widely-accepted standards

### 10. Slow Operations / Latency Issues

**Pitfall**: Taking multiple minutes for simple operations, terminal commands being aborted.

**Solution**: 
- Avoid terminal commands for file operations in Dropbox-synced directories
- Use file read/write tools for documentation updates
- If operations are slow, acknowledge and suggest manual alternatives
- See LATENCY_DIAGNOSIS.md for detailed analysis

---

## Information Verification and Cross-Checking Rules

### When Researching Information

**MUST**:
1. **Cross-check multiple sources**: Never rely on a single web search result
2. **Prioritize standard conventions**: Platform standards (e.g., macOS `~/.local/bin/`, Linux FHS) take precedence over single-source suggestions
3. **Trust user-provided information**: If user corrects you or provides information from another source, trust it and verify it
4. **Check against project documentation**: Verify against appropriate architecture document (MASTER_ARCHITECTURE.md for ecosystem, DigiDoc ARCHITECTURE.md for DigiDoc) and existing project patterns
5. **Acknowledge conflicts**: If sources conflict, acknowledge the conflict and ask user for clarification (one question at a time)

**MUST NOT**:
- Accept single web search results without verification
- Ignore user corrections or information from other sources
- Assume unconventional locations are correct without checking standards
- Make recommendations based on single sources when multiple sources are available

### Verification Checklist

Before recommending file paths, directory structures, or platform-specific conventions:

- [ ] Checked against platform standards (macOS Filesystem Hierarchy, Linux FHS, etc.)
- [ ] Cross-referenced multiple authoritative sources
- [ ] Verified against user-provided information (if available)
- [ ] Checked against existing project patterns in MASTER_ARCHITECTURE.md
- [ ] Acknowledged any conflicts between sources
- [ ] Asked user for clarification if sources conflict (one question at a time)

### When User Provides Conflicting Information

**Process**:
1. **Acknowledge the conflict**: "I found X from a web search, but you mentioned Y. Let me verify Y against standard conventions."
2. **Verify user's information**: Check user's suggestion against platform standards and multiple sources
3. **Accept user's information if verified**: If user's information aligns with standards, use it and acknowledge the correction
4. **Ask for clarification if still uncertain**: If verification is inconclusive, ask user (one question at a time)

**Example**:
- Web search: `~/Library/Application Support/bin/`
- User: `~/.local/bin/` (from another AI agent)
- Action: Verify `~/.local/bin/` against macOS standards → Confirmed as standard → Use `~/.local/bin/` and acknowledge correction

---

## Workspace Organization and Context Preservation

### Construction Suite Ecosystem

**Purpose**: Master Control Plane workspace for active development of interconnected Construction Suite applications (HQ, DigiDoc, Watcher).

**Workspace Philosophy**:
- **Active Development**: One master workspace (`construction-suite.code-workspace`) for coordinating cross-app development
- **Future Maintenance**: Individual workspaces per app (`hq.code-workspace`, `digidoc.code-workspace`) for focused maintenance

**Current State** (2025-12-23):
- ✅ **Workspace file**: `Construction_Suite/construction-suite.code-workspace` (single root structure)
- ✅ **Documentation migration**: All shared docs moved to `shared_documentation/` organized by category
- ✅ **Workspace structure**: Single root at Construction_Suite level
- ✅ **Old hq directory**: Excluded from workspace (kept in filesystem for AI context only)
- All apps located at: `Construction_Suite/apps/{app_name}/`
- Shared documentation: `Construction_Suite/shared_documentation/`

**Workspace Structure**:
- **Single Root**: `Construction_Suite/` contains all nested directories
- **Benefits**: Simpler navigation, matches filesystem, cleaner organization
- **Old Location**: `app_development/hq/` directory remains in filesystem but excluded from workspace

### Agent Retraining Requirements

**If workspace file moves to different directory**: Retraining REQUIRED
- Update AGENT_TRAINING_GUIDE.md with new paths FIRST
- Update all documentation path references
- New AI session learns from updated guide

**If only adding/updating roots** (workspace file stays in same location): No retraining needed
- Just update workspace file
- Update AGENT_TRAINING_GUIDE.md with new roots
- Agent learns from existing guide

### Planning Cache Workflow

**Document**: `Construction_Suite/shared_documentation/planning/PLANNING_CACHE.md`

**Usage**:
- Created/updated when building plans
- Tracks decisions, questions, assumptions in real-time
- Reviewed by user before plan execution
- Cleared/archived after plan completion

**Structure**: Decisions, Questions Asked, Assumptions Validated, Open Items, Plan Summary

### Git Repository Structure

**Strategy**: Separate repositories per app + shared documentation repository

**Current Git State**:
- ✅ **HQ Application**: `Construction_Suite/apps/hq/.git` (existing, configured with remote)
- ⚠️ **DigiDoc Application**: `Construction_Suite/apps/digidoc/.git` (to be initialized)
- ⚠️ **Shared Documentation**: `Construction_Suite/shared_documentation/.git` (to be initialized)
- ⚠️ **Watcher Application**: `Construction_Suite/apps/watcher/.git` (future)

**Benefits**:
- Independent version control per app
- Separate release cycles
- Clear ownership boundaries
- Can clone individual apps independently
- Shared documentation has its own version history

**Repository Locations**:
```
Construction_Suite/
├── apps/
│   ├── hq/.git              ✅ Existing
│   ├── digidoc/.git         ⚠️ To be created
│   └── watcher/.git         ⚠️ Future
└── shared_documentation/.git ⚠️ To be created
```

---

## Quick Reference

### Key Files to Read First

1. `Construction_Suite/shared_documentation/architecture/MASTER_ARCHITECTURE.md` - Ecosystem architecture source of truth
2. `Construction_Suite/apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md` - DigiDoc architecture source of truth
2. `Construction_Suite/shared_documentation/planning/SCHEDULE.md` - Current milestones and progress
3. `Construction_Suite/shared_documentation/planning/SCHEDULE.md` - Development schedule and current focus
4. `Construction_Suite/shared_documentation/planning/DEVELOPMENT_PATHWAY.md` - Feature-level tracking
4. `Construction_Suite/shared_documentation/planning/PLANNING_CACHE.md` - Active planning decisions
5. This file - Training guide

### Key Code Files

1. `Construction_Suite/apps/digidoc/ocr_service/utils/image_preprocessing.py` - Preprocessing (implemented)
2. `Construction_Suite/apps/digidoc/ocr_service/config.py` - Configuration loader (implemented)
3. `Construction_Suite/apps/digidoc/digidoc_config.yaml` - Configuration file (implemented)
4. `Construction_Suite/apps/digidoc/ocr_service/database/models.py` - Database models (implemented)
5. `Construction_Suite/apps/digidoc/ocr_service/gui/app.py` - Streamlit GUI (implemented)
6. `Construction_Suite/apps/hq/app/Services/Ocr/OcrProcessingService.php` - HQ OCR service

### Key Principles

1. **Offline-First**: Always explicit, always local
2. **Configuration-Driven**: No hardcoded values
3. **Modular**: Small, testable modules (15-30 minute chunks)
4. **Fast Communication**: One question at a time
5. **Planning Cache**: Track decisions in real-time

### Alignment Checklist

Before making changes, verify:
- [ ] Aligns with appropriate architecture document (MASTER_ARCHITECTURE.md for ecosystem, DigiDoc ARCHITECTURE.md for DigiDoc)
- [ ] No hardcoded values (use config)
- [ ] Correct preprocessing methods
- [ ] Correct preprocessing order
- [ ] Correct file storage structure
- [ ] Ratio-based template matching (if applicable)
- [ ] Configuration system used

---

## Questions to Ask User

If you need clarification, ask ONE question at a time:

1. **Scope Questions**: "Should X be included in this milestone?"
2. **Implementation Questions**: "Should we use approach A or approach B?"
3. **Configuration Questions**: "What should the default value be for X?"
4. **Architecture Questions**: "Does this align with your vision for X?"

**Remember**: Wait for answer before asking next question. Update PLANNING_CACHE.md with each decision.

---

## Update History

**2025-12-23** (Comprehensive Update):
- ✅ **Documentation Migration Completed**: All shared docs moved from `apps/hq/*DOCUMENTATION/` to `shared_documentation/` organized by category (architecture/, planning/, training/). Watcher-specific docs moved to `apps/watcher/documentation/`.
- ✅ **Workspace Structure Decision**: Construction_Suite as single root (simplified from 6 roots to 1)
- ✅ **Workspace File Location**: Updated to `Construction_Suite/construction-suite.code-workspace`
- ✅ **Old HQ Directory**: Excluded from workspace (kept in filesystem for AI context only)
- ✅ **Git Repository Strategy**: Separate repositories per app (hq, digidoc, watcher) + shared_documentation repo
- Updated file paths to reflect new shared_documentation structure
- Added planning cache workflow
- Updated milestone status (completed)
- Added agent retraining requirements
- Added latency diagnosis reference
- Added Git repository structure section

**2025-12-19**: Initial version

---

## Conclusion

This guide provides the essential context for working on the Construction Suite ecosystem. Always:

1. Reference appropriate architecture document first (MASTER_ARCHITECTURE.md for ecosystem, DigiDoc ARCHITECTURE.md for DigiDoc)
2. Follow configuration-driven principles
3. Ask one question at a time
4. Align all changes with architecture
5. Verify information from multiple sources
6. Trust user-provided information and verify it
7. Test incrementally
8. Update documentation
9. Update PLANNING_CACHE.md during plan development
10. Avoid slow operations - acknowledge and suggest alternatives

When in doubt, ask the user (one question at a time) rather than making assumptions.

**Information Verification Principle**: Never trust a single source. Always cross-check against standards, multiple sources, and user-provided information.

**Performance Principle**: If operations are slow (multiple minutes), acknowledge immediately and suggest manual alternatives. Do not wait for timeouts.

---

## Development Errors Log

**Reference**: `shared_documentation/training/DEVELOPMENT_ERRORS_LOG.md`

When encountering errors during development:

1. **Document immediately** - Don't just fix and move on
2. **Add entry to DEVELOPMENT_ERRORS_LOG.md** with full context
3. **Check the log first** - Many errors have been encountered before

The error log captures:
- Error message and context
- Assumptions that led to the error
- Root cause analysis
- Correction applied
- Prevention strategies

**Before starting new work**, review the error log for similar patterns to avoid repeating mistakes.

**Common error categories**:
- Import errors (library structure assumptions)
- Type errors (class design assumptions)
- Runtime errors (environment assumptions)

See `DEVELOPMENT_ERRORS_LOG.md` for complete entries and searchable tags.

---

**Good luck, and happy coding!**
