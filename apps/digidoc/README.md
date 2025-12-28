# DigiDoc Application Directory

This directory contains data, logs, settings, and the file watcher service for the DigiDoc OCR application.

## Directory Structure

```
DigiDoc/
├── README.md                    # This file
├── settings/                     # Future: Application settings
├── logs/
│   ├── file_watcher_digidoc.log  # File watcher service logs
│   └── tenants/                  # Tenant-specific logs and cache
│       ├── <tenant_data.json>    # Tenant metadata (name, IP, availability, etc.)
│       └── cache/                # Cache files for reliable tenant sessions
├── [Data directory moved to ~/Dropbox/Application Data/DigiDoc/]
└── file_watcher_service/         # File watcher service (see README.md in that directory)
```

## Architecture

- **DigiDoc App**: Located at `~/Applications/Utilities/digidoc/` (system-installed)
- **File Watcher**: Located in this directory's `file_watcher_service/` subdirectory
- **Queue Directory**: `~/Dropbox/Application Data/DigiDoc/queue/` - Scanner saves files here, file watcher monitors for `ready_*.png` files
- **Processing Directory**: `~/Dropbox/Application Data/DigiDoc/processed/` - Temporary storage during processing

## Multi-Tenant Support

This directory structure supports multiple tenants:

- Each tenant can have its own configuration in `logs/tenants/`
- Tenant-specific cache in `logs/tenants/cache/`
- Future: Per-tenant queue directories

## Configuration

Configuration is managed via environment variables and the file watcher's `config.py`:

- `DIGIDOC_SERVICE_URL`: DigiDoc service endpoint
- `DOCUMENT_QUEUE_PATH`: Queue directory path (defaults to `~/Dropbox/Application Data/DigiDoc/queue/`)
- `CALLING_APP_ID`: Calling application identifier

**Path Requirements**:
- All file paths in API calls **MUST** be absolute paths (e.g., `/Users/username/Dropbox/Application Data/DigiDoc/queue/file.pdf`)
- Configuration paths using `~` (e.g., `~/Dropbox/Application Data/DigiDoc/queue/`) are expanded to absolute paths during configuration loading
- Relative paths are not accepted in API requests
- See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" for ecosystem-wide requirements

## File Watcher Service

See `file_watcher_service/README.md` for detailed information about the file watcher service, including installation and configuration.

## Logs

- **File Watcher Logs**: `logs/file_watcher_digidoc.log`
- **Tenant Logs**: `logs/tenants/<tenant_id>/`
- **Error Logs**: Check LaunchAgent/Daemon log locations (see file watcher README)

## Data Flow

1. Scanner saves file to `~/Dropbox/Application Data/DigiDoc/queue/<filename>.png`
2. Scanner issues close file command
3. File watcher detects file and renames to `ready_<filename>.png`
4. File watcher calls DigiDoc API at `/digidoc/process`
5. DigiDoc processes document (stateless, no file operations)
6. Results returned to calling application
7. Calling application handles file storage and database operations

## Notes

- All paths use `~/Dropbox/Application Data/DigiDoc/` as the base (configured in digidoc_config.yaml)
- The DigiDoc app itself is NOT in this directory (it's system-installed)
- This directory is for data, logs, and the file watcher service only
