---
name: DigiDoc Service Relocation and Storage Path Configuration
overview: Relocate DigiDoc OCR service outside project directory, set up macOS daemon management, and make storage paths configurable to support multi-tenant architecture. Service is named "DigiDoc" (lowercase "digidoc" in code/directories/APIs) to disambiguate from future OCR services.
todos:
  - id: relocate_digidoc_app
    content: Move DigiDoc app from project to ~/Applications/Utilities/digidoc/ (user) or /Applications/Utilities/digidoc/ (system)
    status: completed
  - id: create_directory_structure
    content: Create ~/cloud_storage/DigiDoc/ directory structure with logs/tenants, Data/queue, etc.
    status: completed
  - id: relocate_watcher
    content: Move file watcher service to ~/cloud_storage/DigiDoc/file_watcher_service/ and create config.py
    status: completed
  - id: create_launchagent_daemon
    content: Create macOS LaunchAgent (user) and LaunchDaemon (system) plists with installation scripts
    status: completed
  - id: implement_write_lock_protection
    content: Implement write lock protection for app_registrations table with retry logic and timeout handling
    status: completed
  - id: create_watcher_readme
    content: Create README.md in watcher directory documenting architecture and requirements
    status: completed
  - id: update_filesystem_config
    content: Update config/filesystems.php to use environment variables and add documents disk
    status: completed
  - id: add_storage_path_migration
    content: Create migration to add storage_base_path and queue_directory_path to app_registrations
    status: completed
  - id: update_post_processing
    content: Update OcrPostProcessingService to use configurable storage paths
    status: completed
  - id: update_upload_controller
    content: Update ReceiptUploadController to use documents disk instead of receipts
    status: completed
  - id: update_queue_review
    content: Update ReceiptQueueReview to resolve paths using tenant configuration
    status: completed
  - id: update_document_queue_model
    content: Add path resolution methods to DocumentQueue model
    status: completed
  - id: update_watcher_config
    content: Update watcher.py to use config.py and environment variables
    status: completed
---

# File Watcher Relocation and Storage Path Configurati

on

## Overview

Address architectural concerns for **DigiDoc** OCR service (named to disambiguate from future OCR services):

1. **DigiDoc App Location**: Move DigiDoc service outside project directory to system location (`~/Applications/Utilities/digidoc/` or `/Applications/Utilities/digidoc/`)
2. **File Watcher Location**: Move watcher service to `~/cloud_storage/DigiDoc/file_watcher_service/` with macOS launchd daemon setup
3. **Storage Path Configuration**: Make all storage paths configurable (currently hardcoded to `cloud-storage/receipts`) to support multi-tenant, stateless architecture
4. **Service Naming**: Systematically use "DigiDoc" (display name) and "digidoc" (lowercase in code/directories/APIs) throughout the entire application structure

## Problem Analysis

### Current Issues

1. **File Watcher Location**:

- Currently in project: `hq/file_watcher_service/watcher.py`
- Should be at: `~/Dropbox/cloud_storage/file_watcher_service/` (one level up from queue directory)
- No daemon/launchd setup for auto-start
- No README documenting architecture

2. **Hardcoded Storage Paths**:

- `config/filesystems.php`: Hardcoded to `/Users/scottroberts/Library/CloudStorage/Dropbox/cloud-storage/receipts`
- `file_watcher_service/watcher.py`: Hardcoded `~/Dropbox/cloud_storage/queue`
- `app/Services/Ocr/OcrPostProcessingService.php`: Uses `Storage::disk('receipts')` with hardcoded path
- `app/Http/Controllers/Api/ReceiptUploadController.php`: Stores to `receipts` disk
- Database `document_queue.file_path` stores relative paths that assume specific disk root

3. **Multi-Tenant Incompatibility**:

- OCR app is stateless but storage paths are tenant-specific
- No mechanism to pass storage context from calling app to OCR app
- File paths in database may not resolve correctly for different tenants

## Solution Architecture

### 1. DigiDoc App Relocation

**Service Name**: **DigiDoc** (display name), **digidoc** (lowercase in code/directories/APIs)**DigiDoc App Location** (NOT in Dropbox):

- **User Computer**: `~/Applications/Utilities/digidoc/`
- **Headless Server**: `/Applications/Utilities/digidoc/` or `/usr/local/digidoc/`

**DigiDoc App Structure**:

```javascript
~/Applications/Utilities/digidoc/
├── api_server.py              # DigiDoc API server
├── ocr_processor.py
├── database/
├── templates/
├── static/
└── ... (existing DigiDoc app files)
```

**API Endpoints**: All endpoints use `/digidoc/` prefix (e.g., `/digidoc/process`, `/digidoc/templates/sync`)

### 2. File Watcher and Data Directory Structure

**New Location**: `~/cloud_storage/DigiDoc/`**Structure**:

```javascript
~/cloud_storage/
├── DigiDoc/
│   ├── README.md
│   ├── settings/              # Future use
│   ├── logs/
│   │   └── tenants/
│   │       ├── <tenant_data.json>  # name, IP, availability, etc.
│   │       └── cache/              # As needed for reliable sessions
│   ├── Data/
│   │   ├── queue/             # Scanner drops files here
│   │   ├── processing/
│   │   └── <other directories>
│   └── file_watcher_service/  # Watcher service
│       ├── watcher.py
│       ├── config.py
│       ├── requirements.txt
│       ├── README.md
│       ├── com.digidoc.filewatcher.plist  # LaunchAgent (user)
│       └── com.digidoc.filewatcher.daemon.plist  # LaunchDaemon (system)
├── other application 1/
└── other application 2/
```

**Changes**:

- Move `watcher.py` to new location
- Create `config.py` for configuration management
- Create `requirements.txt` (copy from project)
- Create `README.md` with architecture documentation
- Create macOS LaunchAgent plist for auto-start

### 3. Storage Path Configuration

**Approach**: Environment-based configuration with database fallback**Configuration Levels**:

1. **Environment Variables** (highest priority):

- `DOCUMENT_STORAGE_BASE_PATH`: Base path for document storage
- `DOCUMENT_QUEUE_PATH`: Path for queue directory
- `DIGIDOC_SERVICE_URL`: DigiDoc service endpoint (replaces OCR_SERVICE_URL)
- `CALLING_APP_ID`: Calling application identifier

2. **Laravel Config** (`config/filesystems.php`):

- Update `receipts` disk to use `env('DOCUMENT_STORAGE_BASE_PATH')`
- Add new `documents` disk (generic, document-type aware)
- Support tenant-specific paths via `app_registrations` table

3. **Database** (`app_registrations` table):

- Add `storage_base_path` column
- Store per-tenant storage configuration

4. **File Watcher Config**:

- Read from environment variables
- Support per-tenant queue directories

### 4. Tenant Table Write Lock Protection

**Problem**: `app_registrations` table in DigiDoc app database needs protection against silent failures from write locks (e.g., concurrent registration attempts, template sync operations).**Solution**: Implement database-level locking mechanisms:

- Use SQLAlchemy's `with_for_update()` for row-level locking
- Add retry logic with exponential backoff
- Implement transaction isolation
- Add lock timeout handling
- Log lock conflicts for monitoring

**Implementation**:

- Update `template_sync.py` to use row-level locks
- Add lock timeout configuration
- Implement retry decorator for database operations
- Add monitoring/logging for lock conflicts

### 5. Path Resolution Strategy

**For Laravel App**:

- Use `Storage::disk('documents')` with tenant-aware path resolution
- `document_queue.file_path` stores relative paths from storage root
- Resolve full paths using tenant's `storage_base_path`

**For DigiDoc App**:

- Receive absolute file paths from file watcher
- No storage path assumptions (stateless)
- Return extracted data only (no file operations)
- All API endpoints prefixed with `/digidoc/`

**For File Watcher**:

- Monitor tenant-specific queue directories
- Pass absolute file paths to DigiDoc app
- Use `/digidoc/` API prefix for all service calls
- No knowledge of final storage location

## Implementation Tasks

### Task 1: Relocate DigiDoc App

**Service Naming**: Use "DigiDoc" (display) and "digidoc" (code) consistently**Files to Move**:

- Move entire `ocr_service/` directory from project to:
- User: `~/Applications/Utilities/digidoc/`
- Server: `/Applications/Utilities/digidoc/` or `/usr/local/digidoc/`

**Files to Rename/Update**:

- Rename directory from `ocr_service` to `digidoc`
- Update all API endpoints to use `/digidoc/` prefix
- Update database path in `digidoc/database/models.py` to use absolute path or environment variable
- Update any hardcoded paths in DigiDoc app to use configuration
- Update service references in code from "ocr_service" to "digidoc"
- Update environment variable names: `OCR_SERVICE_URL` → `DIGIDOC_SERVICE_URL`

**Changes**:

- DigiDoc app is now system-installed, not in project directory
- Database location should be configurable (environment variable or config file)
- All API calls use `/digidoc/` prefix for future multi-service support

### Task 2: Create Directory Structure and Relocate File Watcher

**Directories to Create**:

- `~/cloud_storage/DigiDoc/`
- `~/cloud_storage/DigiDoc/settings/`
- `~/cloud_storage/DigiDoc/logs/tenants/`
- `~/cloud_storage/DigiDoc/logs/tenants/cache/`
- `~/cloud_storage/DigiDoc/Data/queue/`
- `~/cloud_storage/DigiDoc/Data/processing/`
- `~/cloud_storage/DigiDoc/file_watcher_service/`

**Files to Create**:

- `~/cloud_storage/DigiDoc/README.md` (architecture documentation)
- `~/cloud_storage/DigiDoc/file_watcher_service/watcher.py` (move from project)
- `~/cloud_storage/DigiDoc/file_watcher_service/config.py` (new)
- `~/cloud_storage/DigiDoc/file_watcher_service/requirements.txt` (new)
- `~/cloud_storage/DigiDoc/file_watcher_service/README.md` (new)
- `~/cloud_storage/DigiDoc/file_watcher_service/com.digidoc.filewatcher.plist` (LaunchAgent for user)
- `~/cloud_storage/DigiDoc/file_watcher_service/com.digidoc.filewatcher.daemon.plist` (LaunchDaemon for system)

**Files to Update**:

- `file_watcher_service/watcher.py`: Update imports, use config.py, point to new queue path, update API calls to use `/digidoc/` prefix

**Changes**:

- Extract configuration to `config.py`
- Update `QUEUE_DIRECTORY` to `~/cloud_storage/DigiDoc/Data/queue/`
- Update `OCR_SERVICE_URL` references to `DIGIDOC_SERVICE_URL`
- Update API endpoint calls to use `/digidoc/` prefix (e.g., `/digidoc/process`)
- Add logging configuration
- Add health check endpoint support
- Support both user and system daemon configurations

### Task 2: Create macOS LaunchAgent

**File**: `~/Dropbox/cloud_storage/file_watcher_service/com.filewatcher.ocr.plist`**Configuration**:

- Run at user login
- Restart on crash
- Log to `~/Library/Logs/file_watcher_ocr.log`
- Use Python from virtual environment

**Installation Script**: `install_launchagent.sh`

- Copy plist to `~/Library/LaunchAgents/`
- Load with `launchctl`
- Provide uninstall script

### Task 4: Implement Tenant Table Write Lock Protection

**File**: `ocr_service/database/models.py` (in relocated OCR app)**Changes**:

- Add `with_for_update()` support for row-level locking
- Add lock timeout configuration
- Implement retry decorator for database operations

**File**: `ocr_service/templates/template_sync.py` (in relocated OCR app)**Changes**:

- Use `with_for_update()` when updating `app_registrations`
- Add retry logic with exponential backoff
- Handle `OperationalError` for lock timeouts
- Log lock conflicts

**New File**: `ocr_service/database/locking.py`**Content**:

- Retry decorator with exponential backoff
- Lock timeout configuration
- Transaction isolation helpers
- Lock conflict logging

### Task 5: Update Laravel Storage Configuration

**File**: `config/filesystems.php`**Changes**:

- Update `receipts` disk to use `env('DOCUMENT_STORAGE_BASE_PATH', '~/Dropbox/cloud_storage/receipts')`
- Add new `documents` disk (generic, document-type aware):
  ```php
              'documents' => [
                  'driver' => 'local',
                  'root' => env('DOCUMENT_STORAGE_BASE_PATH', storage_path('app/documents')),
                  'url' => env('APP_URL').'/documents',
                  'visibility' => 'private',
              ],
  ```




### Task 6: Update Database Schema

**Migration**: `2025_12_19_000002_add_storage_path_to_app_registrations.php`**Changes**:

- Add `storage_base_path` column to `app_registrations` table
- Add `queue_directory_path` column
- Add indexes

**Model Update**: `app/Models/AppRegistration.php` (if exists, or create)

- Add fillable fields
- Add accessor methods for path resolution

### Task 7: Update Services to Use Configurable Paths

**Files to Update**:

1. **`app/Services/Ocr/OcrPostProcessingService.php`**:

- Replace `Storage::disk('receipts')` with `Storage::disk('documents')`
- Use tenant-aware path resolution
- Get storage path from `app_registrations` or environment

2. **`app/Http/Controllers/Api/ReceiptUploadController.php`**:

- Update to use `documents` disk
- Store relative paths in database

3. **`app/Filament/Pages/ReceiptQueueReview.php`**:

- Update path resolution for file URLs
- Support tenant-specific storage

4. **`app/Models/DocumentQueue.php`**:

- Add method to resolve full file path
- Use tenant storage configuration

### Task 8: Update File Watcher to Use Config

**File**: `~/Dropbox/cloud_storage/file_watcher_service/watcher.py`**Changes**:

- Import from `config.py`
- Read `QUEUE_DIRECTORY` from config/environment
- Support multiple queue directories (future: per-tenant)
- Add configuration validation

**File**: `~/Dropbox/cloud_storage/file_watcher_service/config.py`**Content**:

- Environment variable reading
- Default values
- Configuration validation
- Logging setup

### Task 9: Create README Documentation

**File**: `~/Dropbox/cloud_storage/file_watcher_service/README.md`**Sections**:

- Architecture Overview
- Installation Instructions
- Configuration
- LaunchAgent Setup
- API Requirements
- Troubleshooting
- Multi-Tenant Considerations

### Task 10: Update OCR App API Contract

**File**: `ocr_service/api_server.py`**Changes**:

- Document that file paths must be absolute
- No storage path assumptions
- Return only extracted data (no file operations)

**Documentation**:

- Update API docs to clarify path requirements
- Add examples for multi-tenant scenarios

## Configuration Examples

### Environment Variables (.env)

```bash
# Document Storage
DOCUMENT_STORAGE_BASE_PATH=/Users/scottroberts/Library/CloudStorage/Dropbox/cloud_storage/documents
DOCUMENT_QUEUE_PATH=/Users/scottroberts/Library/CloudStorage/Dropbox/cloud_storage/DigiDoc/Data/queue
DIGIDOC_APP_PATH=/Users/scottroberts/Applications/Utilities/digidoc

# DigiDoc Service
DIGIDOC_SERVICE_URL=http://127.0.0.1:5000
CALLING_APP_ID=construction_suite
```



### File Watcher Config

```python
# config.py
QUEUE_DIRECTORY = os.environ.get('DOCUMENT_QUEUE_PATH', 
    os.path.expanduser('~/cloud_storage/DigiDoc/Data/queue'))
DIGIDOC_SERVICE_URL = os.environ.get('DIGIDOC_SERVICE_URL', 'http://127.0.0.1:5000')
TENANT_LOGS_DIR = os.path.expanduser('~/cloud_storage/DigiDoc/logs/tenants')
# API endpoints use /digidoc/ prefix
DIGIDOC_API_BASE = f"{DIGIDOC_SERVICE_URL}/digidoc"
```



## Migration Path

1. **Phase 1**: Move file watcher, add config (backward compatible)
2. **Phase 2**: Update Laravel to use configurable paths (maintains existing data)
3. **Phase 3**: Add database storage paths (optional, for multi-tenant)
4. **Phase 4**: Remove hardcoded path references

## Testing Checklist

- [ ] File watcher runs from new location
- [ ] LaunchAgent starts watcher on login
- [ ] Watcher monitors correct queue directory
- [ ] OCR app receives absolute file paths
- [ ] Laravel resolves file paths correctly
- [ ] Storage operations work with new disk configuration
- [ ] Database paths resolve correctly
- [ ] Multi-tenant path resolution (future)

## Files Summary

**New Files**:

- `~/Applications/Utilities/digidoc/` (relocated DigiDoc app, renamed from ocr_service)
- `~/cloud_storage/DigiDoc/README.md`
- `~/cloud_storage/DigiDoc/file_watcher_service/watcher.py`
- `~/cloud_storage/DigiDoc/file_watcher_service/config.py`
- `~/cloud_storage/DigiDoc/file_watcher_service/requirements.txt`
- `~/cloud_storage/DigiDoc/file_watcher_service/README.md`
- `~/cloud_storage/DigiDoc/file_watcher_service/com.digidoc.filewatcher.plist` (LaunchAgent)
- `~/cloud_storage/DigiDoc/file_watcher_service/com.digidoc.filewatcher.daemon.plist` (LaunchDaemon)
- `~/cloud_storage/DigiDoc/file_watcher_service/install_launchagent.sh`
- `~/cloud_storage/DigiDoc/file_watcher_service/install_launchdaemon.sh`
- `digidoc/database/locking.py` (write lock protection)
- `database/migrations/2025_12_19_000002_add_storage_path_to_app_registrations.php`

**Modified Files**:

- `digidoc/database/models.py` (update database path, add lock support, rename from ocr_service)
- `digidoc/templates/template_sync.py` (add write lock protection, rename from ocr_service)
- `digidoc/api_server.py` (update API routes to use `/digidoc/` prefix, rename from ocr_service)
- `config/filesystems.php`
- `app/Services/Ocr/OcrPostProcessingService.php` (update API calls to use `/digidoc/` prefix)