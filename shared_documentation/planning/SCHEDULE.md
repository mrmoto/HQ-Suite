# DigiDoc Project Schedule

**Purpose**: Time-based workflow tracking for project steps, milestones, and progress.  
**Differs from MASTER_ARCHITECTURE.md**: This file tracks time and steps, not specs, dependencies, and logic.

**Last Updated**: 2025-12-23  
**Current Phase**: MVP Development

---

## Layered Framework for Assumption Mapping

### Layer 1: System Architecture and Purpose
- Two stateless applications communicate through APIs
- Database application (Laravel PHP) + OCR application (Python DigiDoc)

### Layer 2: Application Purposes
- **Database app (HQ)**: 
  - Review queue (low confidence documents)
  - Manage queue and reporting
- **Queue logic**: Affected by DigiDoc OCR + host computer daemon utilities

### Layer 3: Logic Workflows
- DigiDoc workflow (preprocessing → matching → extraction)
- Database application (HQ) workflow
- System daemons workflow

### Layer 4: Packages and Dependencies
- All packages used for each step of each logical package
- Python: OpenCV, Tesseract, Streamlit, RQ, SQLAlchemy
- PHP: Laravel, Filament

### Layer 5: Configs, Data, API Formats
- Configs for all packages and functions
- Data structures (queue items, templates, fingerprints)
- API formats (HTTP endpoints, JSON payloads)

---

## Current Focus

**Last Updated**: 2025-12-24

### What We're Working On Now
- **Milestone**: queue_and_extraction_pipeline (MVP Completion)
- **Current Phase**: Phase 2 - Fill critical gaps with real implementations
- **Status**: Template matching replaced with real implementation ✅, Field extraction replaced with real zonal OCR ✅
- **Next**: Test end-to-end extraction flow and validate accuracy

### Where We Stopped
- **Last Completed**: Field extraction now uses real zonal OCR (DocumentExtractor)
- **Why Stopped**: Completed extraction implementation, ready to test and validate
- **Blockers**: None

### Immediate Next Steps (Next 2-3 Chunks)
1. **Test end-to-end flow** with real extraction
2. **Validate extraction accuracy** and adjust as needed
3. **Test error handling** (missing template, extraction failures)

**Note**: For detailed feature tracking and status, see [DEVELOPMENT_PATHWAY.md](DEVELOPMENT_PATHWAY.md). For detailed chunk breakdowns, see slice docs in `planning/slices/`.

---

## Development Phases

### Phase 1: Foundation (MVP) - COMPLETE ✅
**Status**: ✅ Completed (2025-12-19)  
**Summary**: Configuration system, preprocessing pipeline, file storage, structural matching, and Streamlit GUI all functional.

**Completed Features**:
- ✅ Queue abstraction layer (RQ adapter)
- ✅ Configuration management system
- ✅ Basic preprocessing pipeline (5 steps)
- ✅ SQLite database setup
- ✅ Basic template matching (structural fingerprint)
- ✅ Basic Streamlit GUI (queue dashboard, visual match view)
- ✅ File storage organization

**Stopped**: Field extraction still using mocks  
**Next**: Replace mock field extraction with real zonal OCR

---

### Phase 2: Enhanced Matching & Extraction - IN PROGRESS
**Status**: ⚠️ **IN PROGRESS**  
**Started**: 2025-12-24

**Completed**:
- ✅ Template matching replaced with real structural fingerprinting
- ✅ Queue system integrated with API
- ✅ Field extraction replaced with real zonal OCR (DocumentExtractor)

**In Progress**:
- ⚠️ Field extraction testing and validation

**Planned**:
- [ ] Feature detection (ORB keypoints)
- [ ] Text fallback matching
- [ ] Template drift mitigation
- [ ] Template sync with calling app

**Stopped**: Need to test and validate zonal OCR extraction  
**Why**: Extraction implementation complete, now need to validate accuracy

---

### Phase 3: Advanced Extraction - PLANNED
**Status**: ⚠️ **PLANNED**

**Planned Features**:
- [ ] Contour-based extraction
- [ ] LLM integration (Ollama)
- [ ] Handwriting detection
- [ ] Multi-page support

---

### Phase 4: GUI Enhancement - PLANNED
**Status**: ⚠️ **PLANNED**

**Planned Features**:
- [ ] Preprocessing review interface
- [ ] Template matching visualization (enhanced)
- [ ] Extraction review with editing
- [ ] Tiered suggestions interface

---

### Phase 5: Production Readiness - PLANNED
**Status**: ⚠️ **PLANNED**

**Planned Features**:
- [ ] Celery adapter implementation
- [ ] Queue throttling
- [ ] Authentication integration
- [ ] Notifications (email/Slack)
- [ ] Retention policies
- [ ] Cloud mirroring support

---

## Completed Milestones

### ✅ subject_and_template_visual_match (Completed 2025-12-19)
**Goal**: Display original, preprocessed, and template match visualization side-by-side in Streamlit GUI.

**Summary**: Successfully implemented Streamlit GUI with three-panel visualization, complete preprocessing pipeline, structural fingerprint matching, and file storage utilities. All components are functional and integrated.

**Details**: See [DEVELOPMENT_PATHWAY.md](DEVELOPMENT_PATHWAY.md) for feature-level tracking.

---

## Next Milestone: queue_and_extraction_pipeline (MVP Completion)

### Phase 1: Configuration System (Bedrock) - 4 chunks

**Note**: Detailed chunk breakdowns have been moved to [DEVELOPMENT_PATHWAY.md](DEVELOPMENT_PATHWAY.md) for feature-level tracking. This schedule focuses on high-level phases and milestones.

### Next Milestone: queue_and_extraction_pipeline (MVP Completion)

**Goal**: Complete queue abstraction layer and extraction pipeline to finish MVP requirements.

**Status**: ⚠️ **PLANNED** - Ready to start

**MVP Requirements Remaining**:
- [ ] Queue abstraction layer (RQ adapter) - Critical for async processing
- [ ] Simple extraction (zonal OCR) - Critical for field extraction

**Rationale**:
- Queue system enables async processing and integration with Watcher (post-MVP)
- Extraction pipeline is the final missing piece for MVP functionality
- Both are required for end-to-end workflow: file → queue → process → extract → output

**Estimated Chunks**: 15-20 chunks (to be broken down)

---

## Development Infrastructure Milestones

### Infrastructure Phase 1: Critical Automation (Week 1) ✅ COMPLETED

**Goal**: Set up essential automation tools for code quality and testing.

**Status**: ✅ **COMPLETED** (2025-12-24)

**Completed Tasks**:
- ✅ Set up pytest-cov (test coverage tracking)
- ✅ Set up Alembic (database migrations)
- ✅ Create CI/CD pipeline (GitHub Actions)
- ✅ Organize test structure (tests/ directory)
- ✅ Create Git learning guide

**Rationale**: These tools provide immediate value by catching errors early and enforcing quality automatically. See `shared_documentation/training/CI_CD_BENEFITS_AT_SCALE.md` for benefits explanation.

---

### Infrastructure Phase 2: Code Quality Enforcement (Week 2)

**Goal**: Automate code quality checks and enforce standards.

**Status**: ⚠️ **PLANNED**

**Tasks**:
- [ ] Set up pre-commit hooks (.pre-commit-config.yaml)
  - Black (code formatting)
  - isort (import sorting)
  - flake8 (linting)
  - bandit (security scanning)
  - safety (dependency vulnerabilities)
- [ ] Create pyproject.toml (centralized tool configuration)
- [ ] Configure black, isort, flake8, mypy
- [ ] Set up quality gates (fail CI if quality drops)

**Rationale**: Pre-commit hooks catch issues before they're committed, saving time and maintaining code quality. See `development/GIT_LEARNING_GUIDE.md` for Git concepts.

**Estimated Time**: 4-6 hours

---

### Infrastructure Phase 3: Testing Infrastructure (Week 3-4)

**Goal**: Build comprehensive testing infrastructure.

**Status**: ⚠️ **PLANNED**

**Tasks**:
- [ ] Migrate existing tests to pytest format
- [ ] Add test fixtures for common data
- [ ] Set coverage threshold (80% for critical paths, 60% overall)
- [ ] Add integration test framework
- [ ] Add E2E test framework
- [ ] Set up test data management strategy

**Rationale**: Comprehensive testing prevents regressions and provides confidence in code changes. See `apps/digidoc/tests/README.md` for test organization.

**Estimated Time**: 8-12 hours

---

### Infrastructure Phase 4: Security Automation (Week 5)

**Goal**: Automate security scanning and vulnerability detection.

**Status**: ⚠️ **PLANNED**

**Tasks**:
- [ ] Integrate safety check into CI/CD
- [ ] Integrate bandit into pre-commit hooks
- [ ] Set up secrets management strategy (python-dotenv + .env.example)
- [ ] Add dependency vulnerability alerts (GitHub Dependabot)
- [ ] Document security practices

**Rationale**: Automated security scanning catches vulnerabilities early, before they reach production. See `development/MVP_TO_PRODUCTION_CHECKLIST.md` for security checklist.

**Estimated Time**: 4-6 hours

---

### Infrastructure Phase 5: Documentation & API (Week 6)

**Goal**: Complete documentation and API specifications.

**Status**: ⚠️ **PLANNED**

**Tasks**:
- [ ] Documentation consolidation - Extract data from historical files and consolidate into appropriate locations (see `agent_plans/proposed/documentation_consolidation_execution.md` and `agent_plans/proposed/files_to_archive.md`)
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Code documentation audit (docstrings)
- [ ] Developer onboarding guide
- [ ] Operational runbooks

**Rationale**: Good documentation enables collaboration and reduces onboarding time. See assessment recommendations (lines 39-41).

**Estimated Time**: 6-8 hours

---

### Infrastructure Phase 6: Dependency Management (Week 7)

**Goal**: Implement production-ready dependency management.

**Status**: ⚠️ **PLANNED**

**Tasks**:
- [ ] Pin all production dependencies (exact versions)
- [ ] Set up pip-tools for dependency resolution
- [ ] Generate requirements.lock files
- [ ] Add automated dependency audit script
- [ ] Add license checking (pip-licenses)

**Rationale**: Proper dependency management ensures reproducible builds and prevents version conflicts. See `development/DEVELOPMENT_BEST_PRACTICES.md` for version pinning strategy.

**Estimated Time**: 4-6 hours

---

### Infrastructure Phase 7: Logging & Monitoring (Week 8)

**Goal**: Implement structured logging and error tracking.

**Status**: ⚠️ **PLANNED**

**Tasks**:
- [ ] Implement structured logging (structlog/python-json-logger)
- [ ] Set up log rotation (RotatingFileHandler)
- [ ] Define consistent log levels
- [ ] Add error tracking (Sentry for production)
- [ ] Add performance logging

**Rationale**: Structured logging enables better debugging and monitoring. See assessment recommendations (lines 406-410).

**Estimated Time**: 6-8 hours

---

### Infrastructure Phase 8: Database Migrations (Week 9)

**Goal**: Complete database migration strategy.

**Status**: ⚠️ **PLANNED** (Alembic setup completed, migrations pending)

**Tasks**:
- [ ] Create initial migration from existing schema
- [ ] Document migration workflow
- [ ] Set up database backup automation
- [ ] Create test database strategy
- [ ] Document rollback procedures

**Rationale**: Database migrations enable version control for schema changes and safe rollbacks. See `apps/digidoc/alembic/README.md` for migration guide.

**Estimated Time**: 4-6 hours

---

## Assessment Recommendations Integration

All infrastructure phases are based on recommendations from `shared_documentation/training/DEV_ENVIRONMENT_ASSESSMENT.md`. Items are prioritized as:

1. **Immediate (Week 1-2)**: Critical automation (pytest-cov, Alembic, CI/CD, pre-commit hooks)
2. **Short-term (Week 3-6)**: Testing, security, documentation
3. **Medium-term (Week 7-9)**: Dependency management, logging, migrations

See `shared_documentation/planning/DEVELOPMENT_PATHWAY.md` for detailed feature tracking with assessment recommendations.

---

## Assumption Tracking by Layer

### Layer 1 Assumptions
- [ ] Two applications can communicate via HTTP APIs
- [ ] Stateless design is sufficient

### Layer 2 Assumptions
- [ ] Queue logic separation between DigiDoc and HQ is clear
- [ ] Daemon utilities integration points understood

### Layer 3 Assumptions
- [ ] Preprocessing pipeline order is optimal
- [ ] Structural fingerprint matching approach sufficient
- [ ] Zone detection logic works for all receipt types

### Layer 4 Assumptions
- [ ] OpenCV methods available and performant
- [ ] Streamlit suitable for development GUI
- [ ] PyYAML available and reliable

### Layer 5 Assumptions
- [ ] YAML config format acceptable
- [ ] Variable substitution pattern works
- [ ] Environment variable naming convention clear
- [ ] JSON storage for fingerprints sufficient

---

## Dependencies Between Chunks

```
Phase 1 (Config) → Phase 2 (Preprocessing Fixes) → Phase 3 (Add Steps)
Phase 1 (Config) → Phase 4 (File Storage)
Phase 1 (Config) → Phase 6 (GUI)
Phase 3 (Add Steps) → Phase 5 (Matching)
Phase 5 (Matching) → Phase 6 (GUI - visual_match)
```

---

## Notes

- **MVP Focus**: Architecture decisions now, error handling later
- **Structural Allowances**: Code for future needs, not full implementation
- **No Hardcoding**: Weights, API params, URLs/ports, inter-app paths, env vars must be configurable
- **Configuration First**: Bedrock for entire system - must be completed before other phases
