# Architecture Changelog

**Purpose**: Track version history, major architectural decisions, and rationale for the DigiDoc + HQ system.

**Note**: This file tracks changes to `MASTER_ARCHITECTURE.md`. For implementation progress, see `SCHEDULE.md`.

---

## Version History

### Version 2.0 - 2025-12-24
**Status**: Development Phase  
**Major Changes**:
- **Ecosystem Architecture Restructuring**: Split MASTER_ARCHITECTURE.md into ecosystem and app-specific documents
  - **Ecosystem MASTER_ARCHITECTURE.md**: "Construction Suite Ecosystem Architecture" (ecosystem-level only)
    - Ecosystem Overview
    - App Layer Architecture (DigiDoc, HQ, Watcher)
    - App Relationships & Data Flow
    - Integration Contracts (including path handling specifications)
    - Shared Architecture Principles
    - Development Workflow
  - **DigiDoc ARCHITECTURE.md**: "DigiDoc Architecture" (DigiDoc-specific implementation details)
    - All DigiDoc-specific sections moved to `apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md`
    - References ecosystem MASTER_ARCHITECTURE.md for integration context
- **Path Handling Specifications**: Added explicit path handling requirements to Integration Contracts
  - Apps use absolute paths internally
  - API communications require absolute paths in `file_path` parameters
  - Path expansion for cross-system compatibility documented
  - Configuration path expansion requirements specified

**Rationale**:
- Better separation of concerns: ecosystem relationships clearly shown first, separate from app details
- Aligns with monorepo best practices (app docs in app directories)
- Supports delegation strategy (different agents for ecosystem vs app architecture)
- More maintainable (focused documents vs single 1800+ line document)
- Scalable for future apps (easy to add HQ, Watcher architecture docs)
- Path specifications resolve ambiguities identified in DOCUMENTATION_PATH_ANALYSIS.md

**Impact**:
- Ecosystem MASTER_ARCHITECTURE.md: ~450 lines (focused ecosystem content)
- DigiDoc ARCHITECTURE.md: ~1500 lines (all DigiDoc-specific details)
- Clear cross-references between ecosystem and app docs
- Path handling now explicit in all API contracts
- All path-related ambiguities from DOCUMENTATION_PATH_ANALYSIS.md resolved

**Reference**: RESTRUCTURING_PLAN.md, OPTION_EVALUATION.md, PATH_SPECIFICATION_REQUIREMENTS.md

### Version 1.3 - 2025-12-24
**Status**: Development Phase  
**Major Changes**:
- **Documentation Workflow Consolidation**: Implemented consolidated documentation strategy
  - Created `DEVELOPMENT_PATHWAY.md` for hierarchical feature tracking (Q/IP/C status)
  - Simplified `SCHEDULE.md` (removed detailed chunks, added Current Focus section)
  - Removed `NEXT_PLAN_STEPS.md` (consolidated into SCHEDULE.md)
  - Created `planning/slices/` directory for detailed design docs
  - Updated `MASTER_ARCHITECTURE.md` (added Development Pathway section, Future Requirements section, marked Implementation Phases as historical)
- **Development Infrastructure Setup**: Established professional development tooling
  - Set up pytest-cov for test coverage tracking (60% minimum, 80% for critical paths)
  - Set up Alembic for database migrations (SQLite support)
  - Created CI/CD pipeline (GitHub Actions with automated testing, linting, security scanning)
  - Organized test structure (`tests/unit/`, `tests/integration/`, `tests/e2e/`)
  - Created Git learning guide for developer education
- **Assessment-Driven Development**: Integrated all recommendations from development environment assessment
  - All assessment recommendations added to `DEVELOPMENT_PATHWAY.md` with status tracking
  - Infrastructure phases added to `SCHEDULE.md` (8 phases, prioritized by immediate/short-term/medium-term)
  - Created `learnings.md` to track all learning items from assessment

**Rationale**:
- Documentation consolidation eliminates fragmentation and provides clear separation of concerns (spec vs. tracking vs. schedule)
- Development infrastructure automation catches errors early and enforces quality automatically
- Assessment-driven approach ensures systematic improvement based on professional best practices
- Hierarchical feature tracking provides clear visibility into what needs to be built

**Impact**:
- Documentation structure: MA.md (spec), DP.md (tracking), schedule.md (order), cache.md (scratch paper)
- Test coverage now tracked automatically with CI/CD
- Database migrations now versioned with Alembic
- All code quality checks automated via CI/CD pipeline
- Development pathway provides single source of truth for feature status

### Version 1.2 - 2025-12-23
**Status**: Development Phase  
**Major Changes**:
- **Workspace Organization**: Construction Suite restructured with single root workspace
- **Documentation Migration**: All shared documentation moved to `shared_documentation/` organized by category
- **Git Repository Strategy**: Separate repositories per app (hq, digidoc, watcher) + shared_documentation
- **Workspace Structure**: Simplified from 6 roots to single root at Construction_Suite level
- Updated all documentation paths to reflect new structure

**Rationale**:
- Single root workspace simplifies navigation and matches filesystem organization
- Centralized shared documentation improves discoverability and organization
- Separate Git repositories enable independent version control per app
- Cleaner workspace structure reduces complexity

**Impact**:
- Workspace file location: `Construction_Suite/construction-suite.code-workspace`
- All shared docs in `shared_documentation/` (architecture/, planning/, training/, watcher/)
- Old hq directory excluded from workspace (kept in filesystem for AI context only)

### Version 1.1 - 2025-12-23
**Status**: Planning Phase → Development Phase  
**Major Changes**:
- Added status tracking system (Implemented/Planned/Future)
- Added Watcher Integration section (Planned - Post DigiDoc MVP)
- Updated API endpoint to RESTful `/api/digidoc/queue`
- Added Zero Trust authentication requirements
- Added priority-based host selection for Watcher
- Added device_name/device_id to API payload

**Rationale**:
- Status system provides clarity on what's built vs. planned
- Watcher integration documented for future development
- RESTful endpoint aligns with best practices
- Zero Trust ensures security even on localhost
- Priority-based selection enables intelligent routing

---

## Major Architectural Decisions

### 2025-12-23: Watcher Integration Architecture

**Decision**: Watcher operates completely independently, completes rename BEFORE calling DigiDoc.

**Rationale**:
- Ensures atomic file operations complete before API calls
- Prevents partial-file processing
- Allows Watcher to function even if DigiDoc is unavailable
- Aligns with stateless service architecture

**Reference**: MA.md Section "Watcher Integration", WS.md Section 1

---

### 2025-12-23: API Endpoint Design

**Decision**: Use RESTful `/api/digidoc/queue` endpoint with API token authentication.

**Rationale**:
- RESTful design follows industry best practices
- Resource-based naming (`/queue`) is clearer than verb-based (`/process`)
- Aligns with existing `/api/digidoc/templates/sync` pattern
- API token authentication implements Zero Trust principles
- Configurable port (8001 default) allows flexibility

**Reference**: MA.md Section "Integration Points", WS.md Section 3

---

### 2025-12-23: Priority-Based Host Selection

**Decision**: Watcher uses configurable priority list to select DigiDoc host and action.

**Rationale**:
- Enables intelligent routing based on network conditions
- Supports multiple deployment scenarios (LAN, WAN, Cloud)
- Allows graceful degradation when primary host unavailable
- Config-driven approach aligns with "no hardcoding" principle

**Reference**: MA.md Section "Watcher Integration", WS.md Section 3

---

### 2025-12-19: Configuration System

**Decision**: Use YAML for configuration files instead of JSON.

**Rationale**:
- Human-readable and editable
- Supports comments for documentation
- Better for configuration files (vs. JSON for data exchange)
- Minor performance difference acceptable for config files

**Reference**: MA.md Section "Configuration Management"

---

### 2025-12-19: Preprocessing Pipeline

**Decision**: Use HoughLinesP for deskew instead of minAreaRect.

**Rationale**:
- HoughLinesP better detects text line angles
- More accurate for documents with text
- minAreaRect works better for geometric shapes, not text documents
- Aligns with 2025 OCR best practices

**Reference**: MA.md Section "Preprocessing Pipeline"

---

### 2025-12-19: Structural Fingerprinting

**Decision**: Use ratio-based fingerprints (not absolute pixels) for template matching.

**Rationale**:
- DPI/scale invariant
- Works across different scanner resolutions
- More robust than pixel-based matching
- Essential for variable DPI documents

**Reference**: MA.md Section "Template Matching System"

---

### 2025-12-19: Streamlit GUI

**Decision**: Use Streamlit for development verification GUI instead of Flask/Laravel.

**Rationale**:
- Rapid development for visual inspection
- Encapsulated within DigiDoc (no separate GUI app)
- Web-based for easy access
- Sufficient for MVP development verification needs

**Reference**: MA.md Section "Review Queue & GUI"

---

### 2025-12-24: Documentation Strategy Consolidation

**Decision**: Implement consolidated documentation strategy with clear separation of concerns.

**Rationale**:
- Eliminates fragmentation between overlapping documents (schedule.md, next.md, cache.md)
- Provides clear purpose for each document (spec vs. tracking vs. schedule)
- Enables efficient context loading for new AI chat sessions
- Reduces maintenance overhead and confusion

**Structure**:
- **MA.md**: Master spec - WHAT WILL BE BUILT (finished system)
- **DP.md**: Development Pathway - WHAT NEEDS TO BE BUILT (hierarchical tracking with Q/IP/C status)
- **schedule.md**: Development order - WHEN things are being built (phases, milestones, where stopped)
- **cache.md**: Scratch paper for nested planning sessions (temporary, cleared after planning)

**Reference**: DOCUMENTATION_STRATEGY_ANALYSIS.md, DOCUMENTATION_IMPLEMENTATION_PLAN.md

---

### 2025-12-24: Development Infrastructure Automation

**Decision**: Establish automated development infrastructure (CI/CD, test coverage, database migrations).

**Rationale**:
- Automated testing catches errors before they're committed
- Test coverage tracking provides visibility into code quality
- Database migrations enable version control for schema changes
- CI/CD enforces quality automatically without manual effort
- Reduces time spent on manual checks and debugging

**Components**:
- pytest-cov for coverage tracking (60% minimum, 80% for critical paths)
- Alembic for database migrations (SQLite support)
- GitHub Actions CI/CD pipeline (testing, linting, security scanning)
- Organized test structure (unit/, integration/, e2e/)

**Reference**: DEV_ENVIRONMENT_ASSESSMENT.md, SCHEDULE.md (Infrastructure Phases)

---

### 2025-12-24: Assessment-Driven Development

**Decision**: Integrate all recommendations from development environment assessment into development pathway.

**Rationale**:
- Systematic improvement based on professional best practices
- All recommendations tracked with status (Q/IP/C) in DEVELOPMENT_PATHWAY.md
- Infrastructure phases prioritized by immediate/short-term/medium-term needs
- Learning items tracked in learnings.md for developer education

**Impact**:
- All assessment recommendations now have clear implementation path
- Infrastructure improvements scheduled in logical phases
- Developer learning tracked and organized

**Reference**: DEV_ENVIRONMENT_ASSESSMENT.md, DEVELOPMENT_PATHWAY.md, SCHEDULE.md

---

### 2025-12-24: Ecosystem Architecture Split

**Decision**: Split MASTER_ARCHITECTURE.md into ecosystem-level and app-specific architecture documents.

**Rationale**:
- User requirement: "ecosystem relationships should precede information about how DigiDoc works"
- Better for delegation: MCP/PM agent works on ecosystem doc, implementation agent works on app doc
- More maintainable: Focused documents (450 lines vs 2000+ lines)
- Aligns with monorepo best practices: App docs in app directories
- Scalable: Easy to add HQ, Watcher architecture docs in future

**Structure**:
- **Ecosystem MASTER_ARCHITECTURE.md**: Suite overview, app relationships, integration contracts, shared principles
- **DigiDoc ARCHITECTURE.md**: All DigiDoc-specific implementation details

**Reference**: MASTER_ARCHITECTURE.md, apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md, OPTION_EVALUATION.md

---

### 2025-12-24: Path Handling Specifications

**Decision**: Explicitly specify path handling requirements in Integration Contracts section.

**Rationale**:
- Resolves ambiguities identified in DOCUMENTATION_PATH_ANALYSIS.md
- Ensures stateless service operation (no assumptions about working directories)
- Cross-system compatibility (different user accounts, deployment environments)
- Aligns with industry best practices for multi-app ecosystems

**Requirements**:
- Apps use absolute paths internally
- API communications require absolute paths in `file_path` parameters
- Path expansion for cross-system compatibility
- Configuration paths with `~` expanded to absolute paths during loading

**Reference**: MASTER_ARCHITECTURE.md Integration Contracts section, PATH_SPECIFICATION_REQUIREMENTS.md

---

## Implementation Status Tracking

### Completed (2025-12-19 to 2025-12-23)
- Configuration system (YAML-based with env overrides)
- Preprocessing pipeline (deskew, denoise, binarize, normalize, border removal)
- Structural fingerprinting (ratio-based, DPI invariant)
- File storage utilities (queue item directory structure)
- Streamlit GUI (queue view, visual match view)
- Template matching task (fingerprint computation and comparison)

### Planned (Post DigiDoc MVP)
- Watcher integration
- Extraction pipeline
- LLM confirmation
- Multi-page document support

### Future
- Cloud mirroring
- Advanced queue throttling
- Authentication integration
- Retention policies

---

**Last Updated**: 2025-12-24 (Version 2.0 restructuring)
