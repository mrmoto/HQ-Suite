# Detailed Restructuring Plan: Split Architecture Documents

**Date**: 2025-12-24  
**Approach**: Option B (Split Documents)  
**Status**: Ready for Implementation

---

## Overview

Split current `MASTER_ARCHITECTURE.md` into:
1. **Ecosystem MASTER_ARCHITECTURE.md**: Construction Suite ecosystem architecture
2. **DigiDoc ARCHITECTURE.md**: DigiDoc-specific architecture

---

## Phase 1: Create Ecosystem MASTER_ARCHITECTURE.md

### File Location
`shared_documentation/architecture/MASTER_ARCHITECTURE.md` (replace existing)

### New Structure

```markdown
# Construction Suite Ecosystem Architecture

**Version:** 2.0  
**Last Updated:** 2025-12-24  
**Status:** Development Phase

**Note**: This document describes the Construction Suite ecosystem architecture, app relationships, and integration contracts. For DigiDoc-specific implementation details, see [DigiDoc Architecture](../../apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md).

## Table of Contents

1. [Ecosystem Overview](#ecosystem-overview)
2. [App Layer Architecture](#app-layer-architecture)
3. [App Relationships & Data Flow](#app-relationships--data-flow)
4. [Integration Contracts](#integration-contracts)
5. [Shared Architecture Principles](#shared-architecture-principles)
6. [Development Workflow](#development-workflow)

---

## 1. Ecosystem Overview

### Construction Suite
[New content: Suite as ecosystem of related apps, multi-suite vision]

### App Layer Architecture
[New content: DigiDoc, HQ, Watcher, future callers]

## 2. App Relationships & Data Flow
[New content: Data flow diagrams, integration patterns, coupling analysis]

## 3. Integration Contracts
[Expanded from current Integration Points section]
- File Watcher Integration
- Laravel API Integration
- Template Sync Integration
- Authentication Integration
- **Path Handling Specifications** (NEW - from PATH_SPECIFICATION_REQUIREMENTS.md)

## 4. Shared Architecture Principles
[From current Core Architecture Principles, expanded to show ecosystem application]
- Offline-First Operation
- Configuration-Driven
- Modular Development
- Fast Communication Loop

## 5. Development Workflow
[From current Development Workflow section]

---

## References

- [DigiDoc Architecture](../../apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md)
- [Development Pathway](../planning/DEVELOPMENT_PATHWAY.md)
- [Schedule](../planning/SCHEDULE.md)
- [Architecture Changelog](ARCHITECTURE_CHANGELOG.md)
```

### Content Mapping (Old → New)

| Old Section | New Location | Action |
|-------------|--------------|--------|
| Title: "DigiDoc Architecture Model" | Title: "Construction Suite Ecosystem Architecture" | Replace |
| Core Architecture Principles | Shared Architecture Principles | Move, expand |
| System Overview (workflow) | App Relationships & Data Flow | Extract ecosystem parts, move details to DigiDoc doc |
| Integration Points | Integration Contracts | Move, expand, add path handling |
| Watcher Integration | Integration Contracts (consolidate) | Consolidate with Integration Points |
| Development Workflow | Development Workflow | Move as-is |
| Offline-First Architecture (principle) | Shared Architecture Principles | Extract principle, move details to DigiDoc doc |
| Configuration Management (principle) | Shared Architecture Principles | Extract principle, move examples to DigiDoc doc |
| All DigiDoc-specific sections | → DigiDoc ARCHITECTURE.md | Move to app doc |

---

## Phase 2: Create DigiDoc ARCHITECTURE.md

### File Location
`apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md` (new file)

### Structure

```markdown
# DigiDoc Architecture

**Version:** 1.0  
**Last Updated:** 2025-12-24  
**Status:** Development Phase

**Note**: This document describes DigiDoc-specific architecture and implementation details. For ecosystem context, app relationships, and integration contracts, see [Construction Suite Ecosystem Architecture](../../../shared_documentation/architecture/MASTER_ARCHITECTURE.md).

## Table of Contents

1. [Ecosystem Context](#ecosystem-context)
2. [System Overview](#system-overview)
3. [Queue Abstraction Layer](#queue-abstraction-layer)
4. [Preprocessing Pipeline](#preprocessing-pipeline)
5. [Template Matching System](#template-matching-system)
6. [Extraction Pipeline](#extraction-pipeline)
7. [Review Queue & GUI](#review-queue--gui)
8. [File Storage Architecture](#file-storage-architecture)
9. [Configuration Management](#configuration-management)
10. [Workflow Implementation](#workflow-implementation)
11. [Risk Mitigations](#risk-mitigations)
12. [Unknown Unknowns](#unknown-unknowns)
13. [Module Structure](#module-structure)
14. [Integration Implementation](#integration-implementation)
15. [Future Requirements](#future-requirements)

---

## 1. Ecosystem Context

[Link back to ecosystem MA.md, brief summary of DigiDoc's role]

## 2. System Overview

[From current System Overview, DigiDoc-specific workflow]

## 3-14. All Current DigiDoc Sections

[Move all current DigiDoc-specific sections as-is]

## 15. Integration Implementation

[DigiDoc's side of integration contracts - references ecosystem contracts]
```

### Content Mapping (Old → New)

| Old Section | New Location | Action |
|-------------|--------------|--------|
| Queue Abstraction Layer | Queue Abstraction Layer | Move as-is |
| Preprocessing Pipeline | Preprocessing Pipeline | Move as-is |
| Template Matching System | Template Matching System | Move as-is |
| Extraction Pipeline | Extraction Pipeline | Move as-is |
| Review Queue & GUI | Review Queue & GUI | Move as-is |
| File Storage Architecture | File Storage Architecture | Move as-is |
| Configuration Management | Configuration Management | Move as-is (with examples) |
| Workflow Implementation | Workflow Implementation | Move as-is (DigiDoc-specific steps) |
| Risk Mitigations | Risk Mitigations | Move as-is |
| Unknown Unknowns | Unknown Unknowns | Move as-is |
| Module Structure | Module Structure | Move as-is |
| Future Requirements | Future Requirements | Move as-is |
| Offline-First Architecture (details) | System Overview or new section | Move DigiDoc-specific details |
| Integration Points (DigiDoc side) | Integration Implementation | Extract DigiDoc implementation details |

---

## Phase 3: Path Specification Integration

### Locations to Update

#### Ecosystem MASTER_ARCHITECTURE.md

1. **Integration Contracts Section**:
   - Add new subsection: "Path Handling Specifications"
   - Content from PATH_SPECIFICATION_REQUIREMENTS.md
   - Specify: Apps use absolute paths, API requires absolute paths, path expansion

2. **API Request Examples**:
   - Add explicit note: `file_path` must be absolute path
   - Update examples with comments

#### DigiDoc ARCHITECTURE.md

1. **Configuration Management Section**:
   - Add path expansion documentation
   - Specify: Configuration paths with `~` expanded to absolute

2. **Integration Implementation Section**:
   - Reference ecosystem path handling contracts
   - Document DigiDoc's path handling implementation

---

## Phase 4: Cross-Reference Strategy

### Ecosystem MASTER_ARCHITECTURE.md

**In "App Layer Architecture" section**:
```markdown
### DigiDoc
[Description]
- **Architecture Document**: [DigiDoc Architecture](../../apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md)
- **Role**: OCR processing service
- **Coupling**: Closely coupled with Watcher and HQ databases
```

**In "Integration Contracts" section**:
```markdown
For DigiDoc-specific implementation details, see [DigiDoc Architecture](../../apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md).
```

### DigiDoc ARCHITECTURE.md

**At top of document**:
```markdown
## Ecosystem Context

DigiDoc is part of the Construction Suite ecosystem. For ecosystem architecture, app relationships, and integration contracts, see [Construction Suite Ecosystem Architecture](../../../shared_documentation/architecture/MASTER_ARCHITECTURE.md).

**DigiDoc's Role**:
- OCR processing service
- Closely coupled with Watcher (file ingestion) and HQ (data storage)
- Provides API endpoints for file processing
```

**In "Integration Implementation" section**:
```markdown
This section describes DigiDoc's implementation of the integration contracts defined in [Construction Suite Ecosystem Architecture](../../../shared_documentation/architecture/MASTER_ARCHITECTURE.md#integration-contracts).
```

---

## Phase 5: Update Related Documentation

### Files to Update

1. **ARCHITECTURE_CHANGELOG.md**:
   - Add Version 2.0 entry documenting split
   - Rationale: Better separation of concerns, ecosystem-first structure

2. **AGENT_TRAINING_GUIDE.md**:
   - Update MASTER_ARCHITECTURE.md description
   - Add reference to DigiDoc ARCHITECTURE.md
   - Update section references

3. **QUICK_CONTEXT.md**:
   - Update MASTER_ARCHITECTURE.md reference
   - Note split structure

4. **DEVELOPMENT_PATHWAY.md**:
   - Update any references to MA.md sections
   - Note new structure

### Search & Replace Strategy

1. Search for references to "MASTER_ARCHITECTURE.md" sections
2. Update section references to new structure
3. Add references to DigiDoc ARCHITECTURE.md where appropriate
4. Verify all links work

---

## Implementation Order

### Step 1: Create Ecosystem MASTER_ARCHITECTURE.md
1. Create new ecosystem sections (Overview, App Layer, Relationships)
2. Move and adapt shared principles
3. Move and expand integration contracts
4. Add path handling specifications
5. Update title and metadata
6. Add cross-references to DigiDoc doc

### Step 2: Create DigiDoc ARCHITECTURE.md
1. Create file in `apps/digidoc/*DOCUMENTATION/`
2. Add ecosystem context section
3. Move all DigiDoc-specific sections
4. Add cross-references to ecosystem doc
5. Update section references

### Step 3: Update Path Specifications
1. Add path handling to ecosystem Integration Contracts
2. Add path expansion to DigiDoc Configuration Management
3. Update API examples with absolute path requirements

### Step 4: Update Cross-References
1. Update ecosystem doc links to DigiDoc doc
2. Update DigiDoc doc links to ecosystem doc
3. Verify all relative paths work

### Step 5: Update Related Documentation
1. Update ARCHITECTURE_CHANGELOG.md
2. Update AGENT_TRAINING_GUIDE.md
3. Update QUICK_CONTEXT.md
4. Update DEVELOPMENT_PATHWAY.md
5. Search for other references

### Step 6: Verification
1. All ecosystem relationships clearly shown
2. DigiDoc details properly scoped
3. Path specifications explicit and correct
4. TOC reflects new structure
5. Cross-references work
6. No content lost in migration

---

## Content Boundaries (Clear Rules)

### Ecosystem MASTER_ARCHITECTURE.md Contains:
- ✅ Suite overview and organization
- ✅ App descriptions and roles
- ✅ App relationships and data flow
- ✅ Integration contracts (API contracts, data ownership)
- ✅ Shared principles (how they apply to ecosystem)
- ✅ Path handling specifications (ecosystem-wide requirement)

### DigiDoc ARCHITECTURE.md Contains:
- ✅ DigiDoc implementation details
- ✅ Internal architecture (modules, components)
- ✅ Processing pipelines
- ✅ Configuration examples
- ✅ Risk mitigations (DigiDoc-specific)
- ✅ Integration implementation (DigiDoc's side of contracts)

### Rule of Thumb:
- **If it affects multiple apps or defines how apps interact** → Ecosystem doc
- **If it's internal to DigiDoc** → DigiDoc doc
- **If it's a principle that applies to all apps** → Ecosystem doc (with examples in app docs)

---

## Verification Checklist

After restructuring:
- [ ] Ecosystem MASTER_ARCHITECTURE.md shows ecosystem relationships first
- [ ] DigiDoc ARCHITECTURE.md contains all DigiDoc-specific details
- [ ] Path specifications are explicit in both docs
- [ ] Cross-references work (test all links)
- [ ] TOC reflects new structure
- [ ] No content lost in migration
- [ ] Related documentation updated
- [ ] ARCHITECTURE_CHANGELOG.md updated

---

## Estimated Effort

- **Phase 1** (Ecosystem doc): ~2-3 hours
- **Phase 2** (DigiDoc doc): ~1-2 hours
- **Phase 3** (Path specs): ~30 minutes
- **Phase 4** (Cross-refs): ~30 minutes
- **Phase 5** (Related docs): ~1 hour
- **Phase 6** (Verification): ~30 minutes

**Total**: ~5-7 hours

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Content duplication | Clear content boundaries, regular review |
| Broken cross-references | Test all links, use relative paths |
| Missing content | Systematic content mapping, verification checklist |
| Inconsistent updates | Clear ownership (ecosystem vs app) |

---

## Next Steps

1. ✅ Content categorization complete
2. ✅ Best practices research complete
3. ✅ Option evaluation complete
4. ✅ Restructuring plan complete
5. ⏭️ Design ecosystem architecture section (Task 5)
6. ⏭️ Execute restructuring (Task 6)

