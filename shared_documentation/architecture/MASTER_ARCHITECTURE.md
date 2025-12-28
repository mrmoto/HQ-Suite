# Construction Suite Ecosystem Architecture

**Version:** 2.0  
**Last Updated:** 2025-12-24  
**Status:** Development Phase

**Note**: This document describes the Construction Suite ecosystem architecture, app relationships, and integration contracts. For DigiDoc-specific implementation details, see [DigiDoc Architecture](../../apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md). For version history and decision rationale, see [ARCHITECTURE_CHANGELOG.md](ARCHITECTURE_CHANGELOG.md).

## Table of Contents

1. [Ecosystem Overview](#ecosystem-overview)
2. [App Layer Architecture](#app-layer-architecture)
3. [App Relationships & Data Flow](#app-relationships--data-flow)
4. [Integration Contracts](#integration-contracts)
5. [Shared Architecture Principles](#shared-architecture-principles)
6. [Development Workflow](#development-workflow)

---

## Ecosystem Overview

### Construction Suite

The Construction Suite is an ecosystem of interconnected applications designed for construction business management. The suite provides a modular architecture where applications can operate independently while sharing data and services through well-defined integration contracts.

**Suite Structure**:
- **Construction_Suite/**: Primary suite containing related apps
  - **DigiDoc**: OCR processing service
  - **HQ**: Master dashboard application
  - **Watcher**: File monitoring utility
- **Future Suites**: Additional suites may be added (e.g., web_scheduler)

**Design Principles**:
- **Modular architecture**: Each app operates independently
- **Integration contracts**: Well-defined APIs for app-to-app communication
- **Shared principles**: Common architectural principles across all apps
- **Scalability**: Suite structure supports adding new apps and suites

---

## App Layer Architecture

### DigiDoc

**Type**: Application  
**Role**: OCR processing service  
**Technology**: Python (Flask API, Streamlit GUI)  
**Status**: Active Development (MVP Phase)

**Description**: 
DigiDoc provides offline-first OCR processing for document extraction. It receives files from Watcher, processes them through preprocessing, template matching, and field extraction pipelines, then sends extracted data to HQ.

**Coupling**:
- **Closely coupled with**: Watcher (file ingestion), HQ databases (data storage)
- **Integration points**: 
  - Receives files from Watcher via HTTP API
  - Sends extracted data to HQ via HTTP API
  - Syncs templates with HQ

**Architecture Document**: [DigiDoc Architecture](../../apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md)

### HQ

**Type**: Application  
**Role**: Master dashboard for construction business management  
**Technology**: Laravel PHP (web application)  
**Status**: Active Development

**Description**:
HQ is the primary application providing business management functionality. It receives processed documents from DigiDoc, stores them in tenant-aware databases, and provides user interfaces for business operations.

**Coupling**:
- **Closely coupled with**: DigiDoc (receives extracted data), Watcher (may trigger file processing)
- **Integration points**:
  - Receives extracted data from DigiDoc
  - Provides template storage and sync to DigiDoc
  - Manages tenant-aware data storage

**Architecture Document**: [HQ Architecture](../../apps/hq/*DOCUMENTATION/ARCHITECTURE.md) (future)

### Watcher

**Type**: Utility  
**Role**: File monitoring and ingestion daemon  
**Technology**: Swift (macOS), cross-platform (future)  
**Status**: Planned (Post DigiDoc MVP)

**Description**:
Watcher is an OS-level daemon that monitors input directories for new files, performs atomic renames, and optionally triggers DigiDoc processing. It operates independently with 100% uptime guarantee for file ingestion.

**Coupling**:
- **Closely coupled with**: DigiDoc (triggers processing)
- **Integration points**:
  - Monitors directories for new files
  - Performs atomic file renames
  - Calls DigiDoc API to trigger processing
  - Sends notifications (Slack, email, HTTP)

**Architecture Document**: [Watcher Specification](../../apps/watcher/documentation/WATCHER_SPECIFICATION.md)

### Future Callers of DigiDoc

**Status**: Future  
**Description**: Additional applications may call DigiDoc for OCR processing in the future. The integration contracts are designed to support multiple calling applications.

**Integration Pattern**: Same as HQ - HTTP API with `calling_app_id` parameter

---

## App Relationships & Data Flow

### Data Flow Diagram

```
[File System]
    ↓
[Watcher] (monitors, renames)
    ↓ (HTTP API: file_path, calling_app_id)
[DigiDoc] (preprocessing, matching, extraction)
    ↓ (HTTP API: extracted_fields, confidence)
[HQ] (stores, displays)
    ↑ (HTTP API: templates sync)
[DigiDoc] (pulls templates)
```

### Integration Patterns

#### Pattern 1: File Ingestion Flow
- **Watcher → DigiDoc**: File detection and processing trigger
- **Flow**: Watcher detects file → atomic rename → HTTP API call to DigiDoc
- **Data**: File path (absolute), calling_app_id, metadata
- **Contract**: See [Integration Contracts](#integration-contracts) section

#### Pattern 2: Data Extraction Flow
- **DigiDoc → HQ**: Extracted document data
- **Flow**: DigiDoc processes file → extracts fields → HTTP API call to HQ
- **Data**: Extracted fields, confidence scores, processing metadata
- **Contract**: See [Integration Contracts](#integration-contracts) section

#### Pattern 3: Template Synchronization
- **HQ ↔ DigiDoc**: Template storage and sync
- **Flow**: HQ stores templates → DigiDoc pulls via API → DigiDoc caches locally
- **Data**: Template definitions, fingerprints, field mappings
- **Contract**: See [Integration Contracts](#integration-contracts) section

### Coupling Analysis

**Tightly Coupled**:
- **Watcher ↔ DigiDoc**: Watcher's primary purpose is to trigger DigiDoc processing
- **DigiDoc ↔ HQ**: DigiDoc's primary purpose is to extract data for HQ

**Loosely Coupled**:
- **Watcher ↔ HQ**: Indirect relationship (Watcher → DigiDoc → HQ)
- **Future callers ↔ DigiDoc**: Same integration contract as HQ

**Decoupling Strategy**:
- Integration via HTTP APIs (stateless)
- Well-defined contracts (see Integration Contracts)
- No direct database access between apps
- Each app maintains its own data store

---

## Integration Contracts

### Overview

Integration contracts define how applications in the Construction Suite communicate. All integrations use HTTP APIs with JSON payloads. Contracts are designed to be stateless and support multiple calling applications.

### Path Handling Specifications

**CRITICAL**: All file paths in API communications must be absolute paths. This ensures stateless service operation and eliminates ambiguity about file locations.

**Requirements**:
1. **Apps Use Absolute Paths Internally**: All apps (hq, digidoc, watcher) use absolute paths for internal file operations
2. **API Communications Require Absolute Paths**: The `file_path` parameter in all API requests must be an absolute path
3. **Path Expansion for Cross-System Compatibility**: Configuration paths using `~` or environment variables are expanded to absolute paths using `os.path.expanduser()` or equivalent
4. **Configuration Path Expansion**: Paths with `~` in configuration files are expanded to absolute paths during configuration loading, before any file operations

**Rationale**:
- Stateless services need explicit paths (no assumptions about working directories)
- Cross-system compatibility (different user accounts, deployment environments)
- Eliminates ambiguity in file location
- Aligns with industry best practices for multi-app ecosystems

**Examples**:
- ✅ Correct: `"file_path": "/Users/username/Dropbox/Application Data/DigiDoc/queue/file.pdf"`
- ❌ Incorrect: `"file_path": "queue/file.pdf"` (relative path)
- ✅ Correct: Configuration `storage_base: "~/digidoc_storage"` → expanded to `/Users/username/digidoc_storage`
- ❌ Incorrect: Using relative paths in configuration without expansion

### Contract 1: Watcher → DigiDoc

**Endpoint**: `POST /api/digidoc/queue`  
**Port**: 8001 (configurable)  
**Authentication**: API token required (Zero Trust)

**Request Headers**:
```
Authorization: Bearer <api_token>
Content-Type: application/json
```

**Request Payload**:
```json
{
  "file_path": "/absolute/path/to/renamed_file.pdf",  // MUST be absolute
  "calling_app_id": "required",
  "source": "scanner|sftp|shared_folder",
  "device_name": "Scanner-01",
  "device_id": "optional-device-uuid",
  "metadata": {
    "original_filename": "original.pdf",
    "source_directory": "/Incoming/SFTP",
    "renamed_filename": "20251223_104118_abcd1234.pdf",
    "timestamp": "2025-12-23T10:41:18Z"
  }
}
```

**Response**:
```json
{
  "queue_item_id": "uuid",
  "status": "pending",
  "message": "File enqueued successfully"
}
```

**Path Requirement**: `file_path` MUST be an absolute path. Watcher passes the absolute path of the renamed file.

**Priority-Based Host Selection**:
Watcher uses configurable priority list to select DigiDoc host and action:
- Checks hosts in priority order (LAN → WAN → Cloud)
- Tests connectivity (MAC match + ping for LAN, ping for WAN/cloud)
- Executes action from config (`none`, `auto`, `notify`, `both`)
- If no hosts available: Sends error notification to webhook

**Post-Rename Actions**:
- `none`: Rename only, no API call
- `auto`: Rename + call DigiDoc API
- `notify`: Rename + send notification, no API call
- `both`: Rename + call DigiDoc API + send notification

**Note**: Watcher **ALWAYS** performs atomic rename (100% uptime guarantee) before any API calls or notifications.

### Contract 2: DigiDoc → HQ

**Endpoint**: Configurable (default: `/api/digidoc/process-complete`)  
**Authentication**: API token (post-MVP)

**Request**:
```json
{
  "queue_item_id": "uuid",
  "calling_app_id": "string",
  "extracted_fields": {
    "receipt_date": "2025-12-19",
    "receipt_number": "12345",
    "total_amount": 665.34,
    "line_items": [...]
  },
  "confidence": 0.92,
  "template_matched": "mead_clark_format1",
  "processing_metadata": {...}
}
```

**Response**:
```json
{
  "status": "success",
  "receipt_id": "uuid"
}
```

### Contract 3: HQ ↔ DigiDoc (Template Sync)

**DigiDoc → HQ (Pull)**:
- **Endpoint**: `/api/digidoc/templates/sync`
- **Purpose**: DigiDoc pulls templates from HQ
- **Request**: `{ "calling_app_id": "string", "document_type": "receipt", "vendor": "..." }`
- **Response**: `{ "templates": [...], "count": 5 }`

**DigiDoc → HQ (Push)**:
- **Endpoint**: `/api/digidoc/templates/create`
- **Purpose**: DigiDoc pushes new templates to HQ
- **Request**: `{ "calling_app_id": "string", "template_data": {...} }`
- **Response**: `{ "status": "success", "template_id": "uuid" }`

### Data Ownership

**HQ Owns**:
- Template definitions (primary storage)
- Extracted document data (final storage)
- Tenant data
- Business logic data

**DigiDoc Owns**:
- Template cache (local, synced from HQ)
- Queue items (temporary, during processing)
- Processing metadata
- Preprocessed images (temporary)

**Watcher Owns**:
- File monitoring configuration
- Rename logs
- Notification configuration

**Rule**: Each app maintains its own data store. No direct database access between apps.

### Communication Patterns

**Synchronous**:
- Watcher → DigiDoc (file processing trigger)
- DigiDoc → HQ (extracted data submission)
- Template sync (pull/push)

**Asynchronous**:
- Queue-based processing (DigiDoc internal)
- Notifications (Watcher → external services)

**Error Handling**:
- All APIs return error responses with status codes
- Apps handle errors gracefully (log, retry, fallback)
- No app depends on another app's availability for core operations

### Authentication Integration (Post-MVP)

**Interface**: API context parameter

**Request Header**:
```
X-Calling-App-ID: required
X-User-ID: user-uuid (post-MVP)
X-Auth-Token: jwt-token (post-MVP)
X-Environment: production (post-MVP)
```

**Processing**:
- Store context in queue item
- Pass context through processing pipeline
- Include in audit logs
- Available for GUI display

---

## Shared Architecture Principles

These principles apply to all applications in the Construction Suite ecosystem. Each app implements these principles according to its specific needs.

### 1. Offline-First Operation

**Ecosystem Application**: All apps in the suite operate offline-first where possible.

- **DigiDoc**: 100% offline processing, local models and templates
- **HQ**: Web application, but designed for offline data entry (post-MVP)
- **Watcher**: OS-level daemon, operates independently

**Rationale**: Ensures suite functionality even without internet connectivity.

### 2. Configuration-Driven

**Ecosystem Application**: All apps use configuration files for thresholds, limits, and parameters.

- **DigiDoc**: YAML configuration for all processing parameters
- **HQ**: Laravel configuration system
- **Watcher**: YAML configuration for monitoring and routing

**Rationale**: Enables environment-specific configuration without code changes.

### 3. Modular Development

**Ecosystem Application**: Each app is developed as a modular system.

- **DigiDoc**: Queue abstraction, preprocessing modules, extraction modules
- **HQ**: Laravel modules/features
- **Watcher**: Modular daemon architecture

**Rationale**: Enables independent development and testing of components.

### 4. Path Handling

**Ecosystem Application**: All apps use absolute paths internally and in API communications.

- **DigiDoc**: Absolute paths for all file operations
- **HQ**: Absolute paths for file storage operations
- **Watcher**: Absolute paths for file monitoring and API calls

**Rationale**: Ensures stateless operation and cross-system compatibility.

See [Path Handling Specifications](#path-handling-specifications) in Integration Contracts section.

---

## Development Workflow

### Planning Process

1. **Master Plan**: MASTER_ARCHITECTURE.md (ecosystem architecture)
2. **App Plans**: Each app has its own architecture document
3. **Sub-Plans**: Module-level plans as needed
4. **Incremental Development**: Build small modules at a time

### Module Development Steps

1. **Create Sub-Plan**: Document module architecture, interfaces, dependencies
2. **Implement Module**: Build according to sub-plan
3. **Generate Visual Output**: Create comparison images, progress charts
4. **Test Module**: Unit tests, integration tests
5. **Update Architecture Docs**: Document what was built, lessons learned
6. **Update ARCHITECTURE_CHANGELOG.md**: Document major changes, decisions, and rationale
7. **Move to Next Module**: Repeat

### Documentation Updates

- **Ecosystem Changes**: Update MASTER_ARCHITECTURE.md
- **App Changes**: Update app-specific ARCHITECTURE.md
- **Integration Changes**: Update both ecosystem and app docs
- **Changelog**: Update ARCHITECTURE_CHANGELOG.md for significant changes

### Communication Strategy

**Avoid Long Planning Queues**:
- Break work into small, executable tasks
- Ask one question at a time
- Build incrementally
- Update MASTER_ARCHITECTURE.md frequently

**Chat Continuity**:
- MASTER_ARCHITECTURE.md is source of truth for ecosystem architecture
- App-specific ARCHITECTURE.md documents are source of truth for app details
- New chat sessions can read these documents
- All decisions documented here
- Architecture evolves as we build
- ARCHITECTURE_CHANGELOG.md provides version history and decision rationale

---

## References

- [DigiDoc Architecture](../../apps/digidoc/*DOCUMENTATION/ARCHITECTURE.md)
- [Watcher Specification](../../apps/watcher/documentation/WATCHER_SPECIFICATION.md)
- [Development Pathway](../planning/DEVELOPMENT_PATHWAY.md)
- [Schedule](../planning/SCHEDULE.md)
- [Architecture Changelog](ARCHITECTURE_CHANGELOG.md)

---

**End of MASTER_ARCHITECTURE.md**
