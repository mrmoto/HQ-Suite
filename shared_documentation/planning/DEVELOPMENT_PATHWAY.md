# Development Pathway

**Purpose**: Hierarchical plan of WHAT NEEDS TO BE BUILT, with status tracking and links to detailed design docs.  
**Status Legend**: Q (Queued), IP (In Progress), C (Complete)  
**Last Updated**: 2025-12-24

**Note**: This document tracks development status. For ecosystem architecture specs, see [MASTER_ARCHITECTURE.md](../architecture/MASTER_ARCHITECTURE.md). For DigiDoc-specific architecture specs, see [DigiDoc ARCHITECTURE.md](../../apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md). For development order, see [SCHEDULE.md](SCHEDULE.md).

---

## DigiDoc Application

### Foundation & Infrastructure

#### Configuration System
- [C] Configuration file structure (digidoc_config.yaml)
- [C] Config loader with environment variable overrides
- [C] Variable substitution support
- [Q] Config validation (pydantic/cerberus) → [assessment: config validation]
- [Q] Config schema documentation → [assessment: config schema]
- [Q] Multi-environment configs (dev/staging/prod) → [assessment: environment management]

#### Database Management
- [C] SQLAlchemy models (CachedTemplate, TemplateSyncMetadata, AppRegistration)
- [C] Database initialization (init_db.py)
- [C] Alembic setup → [assessment: database migrations]
- [Q] Initial migration creation
- [Q] Migration strategy documentation
- [Q] Database backup automation → [assessment: database backups]
- [Q] Test database strategy → [assessment: database testing]
- [Q] Connection pooling configuration → [assessment: connection pooling]

#### File Storage Architecture
- [C] Queue item directory structure
- [C] File utilities (file_utils.py)
- [C] Storage base path configuration
- [Q] Build artifacts directory structure → [assessment: build artifacts]
- [Q] Deployment directory structure → [assessment: deployment structure]

---

### Queue System

#### Queue Abstraction Layer
- [C] QueueAdapter interface (queue_adapter.py)
- [C] Factory function (get_queue_adapter)
- [C] Queue-agnostic task functions

#### Queue Implementations
- [C] RQ Adapter (rq_adapter.py) - MVP
- [Q] Celery Adapter (celery_adapter.py) - Post-MVP → [slice: celery-adapter.md]
- [Q] Queue throttling → [assessment: queue throttling]

#### Queue Integration
- [C] API endpoint for queueing documents (/api/digidoc/queue)
- [C] Status endpoint (/api/digidoc/status/<task_id>)
- [Q] Queue monitoring and metrics
- [Q] Queue retry logic

---

### Preprocessing Pipeline

#### Preprocessing Steps
- [C] Deskew (HoughLinesP)
- [C] Denoise (fastNlMeansDenoising)
- [C] Binarization (adaptive threshold)
- [C] Scale normalization (300 DPI target)
- [C] Border removal (contour analysis)
- [C] Visual verification (before/after comparison)

#### Preprocessing Infrastructure
- [C] ImagePreprocessor class
- [C] Config-driven preprocessing parameters
- [C] Comparison image generation
- [Q] Preprocessing performance optimization
- [Q] Preprocessing quality metrics

---

### Template Matching System

#### Matching Methods
- [C] Structural fingerprint matching (ratio-based, DPI-invariant)
- [Q] Feature detection (ORB keypoints) → [slice: feature-detection.md]
- [Q] Text fallback matching → [slice: text-fallback.md]
- [Q] Two-phase template matching (coarse + detailed) → [slice: two-phase-template-matching.md]

#### Template Management
- [C] Template caching (CachedTemplate model)
- [C] Structural fingerprint storage
- [Q] Template sync with calling app
- [Q] Template drift mitigation
- [Q] Template versioning

#### Matching Infrastructure
- [C] Matching task (matching_task.py)
- [C] Match visualization
- [Q] Match confidence scoring refinement
- [Q] Match performance optimization

---

### Extraction Pipeline

#### Extraction Methods
- [C] Zonal OCR (basic implementation)
- [Q] Contour-based extraction → [slice: contour-extraction.md]
- [Q] LLM integration (Ollama) → [slice: llm-integration.md]
- [Q] Handwriting detection
- [Q] Multi-page support

#### Extraction Infrastructure
- [C] Receipt extractor (receipt_extractor.py)
- [C] Format classes (base_format.py, mead_clark_format*.py)
- [C] OCR processor (ocr_processor.py) - Tesseract integration with preprocessing
- [C] Text utilities (text_utils.py) - Text cleaning, date/currency extraction
- [C] Confidence scoring system (confidence_scorer.py) - Multi-factor extraction confidence
- [Q] Field mapping system
- [Q] Extraction validation
- [Q] Extraction quality metrics

---

### Review Queue & GUI

#### Streamlit GUI
- [C] Basic app structure (app.py)
- [C] Queue view (queue_view.py)
- [C] Visual match view (visual_match.py)
- [Q] Preprocessing review interface
- [Q] Extraction review with editing
- [Q] Tiered suggestions interface
- [Q] Template editing interface

#### GUI Infrastructure
- [C] Visualization utilities (visualization.py)
- [C] Queue utilities (queue_utils.py)
- [Q] GUI performance optimization
- [Q] GUI accessibility improvements

---

### API Server

#### API Endpoints
- [C] Queue document endpoint (POST /api/digidoc/queue)
- [C] Status endpoint (GET /api/digidoc/status/<task_id>)
- [Q] Process endpoint (POST /api/digidoc/process) - backward compatibility
- [Q] Template sync endpoints
- [Q] Health check endpoint

#### API Infrastructure
- [C] Flask API server (api_server.py)
- [Q] API authentication → [assessment: API security]
- [Q] Rate limiting → [assessment: rate limiting]
- [Q] CORS configuration → [assessment: CORS]
- [Q] API documentation (OpenAPI/Swagger) → [assessment: API documentation]
- [Q] Input validation → [assessment: input validation]

---

### Development Infrastructure

#### Testing Infrastructure
- [C] Test directory structure (tests/unit, tests/integration, tests/e2e)
- [C] pytest configuration (pytest.ini)
- [C] pytest-cov setup → [assessment: test coverage]
- [C] Test fixtures (conftest.py)
- [Q] Test data management (fixtures strategy) → [assessment: test data management]
- [Q] Property-based testing (Hypothesis) → [assessment: property-based testing]
- [Q] Performance testing → [assessment: performance testing]
- [Q] E2E test framework → [assessment: E2E testing]
- [Q] Visual regression testing → [assessment: visual regression]
- [Q] Test parallelization → [assessment: test parallelization]
- [Q] Test reporting (HTML/XML) → [assessment: test reporting]

#### Code Quality Tools
- [C] Development requirements (requirements-dev.txt)
- [Q] pyproject.toml configuration → [assessment: pyproject.toml]
- [Q] Pre-commit hooks (.pre-commit-config.yaml) → [assessment: pre-commit hooks]
- [Q] Black configuration → [assessment: formatting config]
- [Q] isort configuration → [assessment: import organization]
- [Q] flake8 configuration → [assessment: linting rules]
- [Q] mypy configuration → [assessment: type checking]
- [Q] Complexity checking (radon, xenon) → [assessment: code complexity]
- [Q] Code duplication detection → [assessment: code duplication]
- [Q] Quality gates (CI integration) → [assessment: quality gates]

#### CI/CD Pipeline
- [C] GitHub Actions workflow (.github/workflows/ci.yml) → [assessment: CI/CD]
- [C] Test automation in CI
- [C] Linting/formatting in CI
- [C] Security scanning in CI
- [Q] Coverage reporting in CI
- [Q] Deployment automation
- [Q] Feature flags → [assessment: feature flags]
- [Q] Canary deployments → [assessment: canary deployments]
- [Q] Rollback strategy → [assessment: rollback strategy]

#### Security Practices
- [C] Security tools documented (safety, bandit)
- [Q] Automated security scanning (pre-commit + CI) → [assessment: automate security]
- [Q] Dependency vulnerability scanning (safety check) → [assessment: dependency vulnerabilities]
- [Q] SAST (Static Analysis) → [assessment: SAST]
- [Q] Secrets management strategy (python-dotenv + .env.example) → [assessment: secrets management]
- [Q] Secret rotation strategy → [assessment: secret rotation]
- [Q] SQL injection prevention review → [assessment: SQL injection]
- [Q] HTTPS enforcement → [assessment: HTTPS]
- [Q] Security headers → [assessment: security headers]

#### Dependency Management
- [C] Requirements files (requirements_ocr.txt)
- [C] Development requirements (requirements-dev.txt)
- [Q] Version pinning (production dependencies) → [assessment: version pinning]
- [Q] pip-tools for dependency resolution → [assessment: pip-tools]
- [Q] requirements.lock files → [assessment: lock files]
- [Q] Automated dependency audit → [assessment: dependency audit]
- [Q] License checking (pip-licenses) → [assessment: dependency licenses]
- [Q] Dependency conflict detection → [assessment: dependency conflicts]

#### Logging & Error Handling
- [C] Error logging system (DEVELOPMENT_ERRORS_LOG.md)
- [Q] Structured logging (structlog/python-json-logger) → [assessment: structured logging]
- [Q] Log rotation (RotatingFileHandler) → [assessment: log rotation]
- [Q] Error tracking (Sentry) → [assessment: error tracking]
- [Q] Consistent log levels → [assessment: log levels]
- [Q] Log aggregation → [assessment: log aggregation]
- [Q] Error alerting → [assessment: error alerting]
- [Q] Performance logging → [assessment: performance logging]
- [Q] Audit logging → [assessment: audit logging]

#### Documentation
- [C] Architecture documentation (MASTER_ARCHITECTURE.md - Ecosystem, DigiDoc ARCHITECTURE.md - App-specific)
- [C] Path specification updates across all documentation files
- [C] Development documentation (various)
- [C] API documentation (basic)
- [Q] Documentation consolidation - Extract data from historical files and consolidate into appropriate locations (see `agent_plans/proposed/documentation_consolidation_execution.md`)
- [Q] API documentation (OpenAPI/Swagger) → [assessment: API documentation]
- [Q] Code documentation (docstring audit) → [assessment: code documentation]
- [Q] Developer onboarding guide → [assessment: onboarding docs]
- [Q] Operational runbooks → [assessment: runbooks]

---

### Production Readiness

#### Deployment
- [Q] Deployment strategy → [assessment: deployment strategy]
- [Q] Blue-green deployments → [assessment: blue-green]
- [Q] Zero-downtime deployment
- [Q] Environment management (dev/staging/prod) → [assessment: environment management]

#### Monitoring & Observability
- [Q] Performance monitoring → [assessment: performance monitoring]
- [Q] Application metrics
- [Q] Health checks
- [Q] Alerting system

#### Scalability
- [Q] Queue throttling
- [Q] Resource optimization
- [Q] Load balancing

---

## HQ Application

### Database Application (Laravel)
- [C] OCR processing service (OcrProcessingService.php) - HTTP client integration with DigiDoc
- [C] Confidence-based workflow (high confidence auto-creates receipts, low confidence queues for review)
- [C] Vendor lookup/creation
- [Q] Review queue management
- [Q] Queue reporting
- [Q] Template management
- [Q] Enhanced integration with DigiDoc API

---

## Shared Infrastructure

### Development Tools
- [C] Virtual environment standards (VENV_STANDARDS.md)
- [C] direnv integration
- [C] Development best practices (DEVELOPMENT_BEST_PRACTICES.md)
- [C] Git workflow (GIT_WORKFLOW.md)
- [C] Git learning guide (GIT_LEARNING_GUIDE.md)
- [C] Token drift mitigation (TOKEN_DRIFT_MITIGATION.md)
- [C] MVP to production checklist (MVP_TO_PRODUCTION_CHECKLIST.md)

### Documentation
- [C] Master architecture (MASTER_ARCHITECTURE.md - Ecosystem, DigiDoc ARCHITECTURE.md - App-specific)
- [C] Development pathway (this document)
- [C] Schedule (SCHEDULE.md)
- [C] Planning cache (PLANNING_CACHE.md)
- [C] Quick context (QUICK_CONTEXT.md)
- [C] Agent training guide (AGENT_TRAINING_GUIDE.md)
- [C] Development errors log (DEVELOPMENT_ERRORS_LOG.md)
- [C] Development environment assessment (DEV_ENVIRONMENT_ASSESSMENT.md)
- [C] Learnings track (learnings.md)

---

## Assessment Recommendations Integration

Items marked with `→ [assessment: ...]` are recommendations from the development environment assessment. These should be prioritized based on:
1. **Immediate**: Critical for MVP (pre-commit hooks, test coverage, Alembic)
2. **Short-term**: Important for production readiness (security scanning, API docs, structured logging)
3. **Medium-term**: Nice-to-have improvements (advanced testing, monitoring, deployment strategies)

See `shared_documentation/training/DEV_ENVIRONMENT_ASSESSMENT.md` for full details and priorities.

---

**Last Updated**: 2025-12-24  
**Next Review**: After completing current milestone

