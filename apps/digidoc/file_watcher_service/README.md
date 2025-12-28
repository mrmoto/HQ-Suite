# DigiDoc File Watcher Service

## Overview

The DigiDoc File Watcher Service is a separate macOS service that monitors the queue directory for `ready_*.png` files and automatically calls the DigiDoc OCR service API to process them.

## Architecture

- **Location**: `~/Dropbox/cloud_storage/DigiDoc/file_watcher_service/`
- **Queue Directory**: `~/Dropbox/Application Data/DigiDoc/queue/`
- **DigiDoc Service**: Runs at `http://127.0.0.1:5000` (configurable)
- **API Prefix**: All DigiDoc API calls use `/digidoc/` prefix

## Directory Structure

```
~/Dropbox/cloud_storage/DigiDoc/
├── file_watcher_service/
│   ├── watcher.py              # Main watcher script
│   ├── config.py                # Configuration management
│   ├── requirements.txt         # Python dependencies
│   ├── README.md                # This file
│   ├── com.digidoc.filewatcher.plist          # LaunchAgent (user)
│   ├── com.digidoc.filewatcher.daemon.plist   # LaunchDaemon (system)
│   ├── install_launchagent.sh   # User installation script
│   ├── install_launchdaemon.sh  # System installation script (requires sudo)
│   ├── uninstall_launchagent.sh
│   └── uninstall_launchdaemon.sh
└── logs/
    ├── file_watcher_digidoc.log  # Watcher logs
    └── tenants/                  # Tenant-specific logs

Note: Queue directory is now at ~/Dropbox/Application Data/DigiDoc/queue/
```

## Installation

### User-Level (LaunchAgent)

For development or user-specific installation:

```bash
cd ~/Dropbox/cloud_storage/DigiDoc/file_watcher_service
./install_launchagent.sh
```

This will:
- Copy plist to `~/Library/LaunchAgents/`
- Load and start the service
- Run at user login

### System-Level (LaunchDaemon)

For headless server installation:

```bash
cd ~/Dropbox/cloud_storage/DigiDoc/file_watcher_service
sudo ./install_launchdaemon.sh
```

This will:
- Copy plist to `/Library/LaunchDaemons/` (requires root)
- Load and start the service
- Run at system boot

## Configuration

Configuration is managed via `config.py` and environment variables:

### Environment Variables

- `DIGIDOC_SERVICE_URL`: DigiDoc service endpoint (default: `http://127.0.0.1:5000`)
- `DOCUMENT_QUEUE_PATH`: Queue directory path (default: `~/Dropbox/Application Data/DigiDoc/queue`)
- `CALLING_APP_ID`: Calling application identifier (default: `construction_suite`)

### Configuration File

Edit `config.py` to change defaults or add custom configuration.

## API Requirements

The file watcher calls the DigiDoc service at:

- **Health Check**: `GET /digidoc/health`
- **Process Document**: `POST /digidoc/process`

All API endpoints use the `/digidoc/` prefix to disambiguate from future OCR services.

## Workflow

1. Scanner saves file to queue directory: `~/Dropbox/Application Data/DigiDoc/queue/<filename>.png` (expanded to absolute path)
2. Scanner issues close file command
3. File watcher detects file closure via macOS FSEvents
4. File watcher atomically renames: `<filename>.png` → `ready_<filename>.png`
5. File watcher calls DigiDoc API: `POST /digidoc/process` with file path
6. DigiDoc processes document and returns results
7. File watcher logs results

**Path Requirements**:
- The file watcher passes **absolute file paths** to the DigiDoc API
- Configuration paths using `~` (e.g., `~/Dropbox/Application Data/DigiDoc/queue/`) are expanded to absolute paths during configuration loading
- All internal file operations use absolute paths after expansion
- See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" for ecosystem-wide requirements

## Monitoring

### Check Status

```bash
# User-level
launchctl list | grep digidoc

# System-level
sudo launchctl list | grep digidoc
```

### View Logs

```bash
# User-level logs
tail -f ~/Dropbox/cloud_storage/DigiDoc/logs/file_watcher_digidoc.log

# System-level logs
sudo tail -f /var/log/digidoc_filewatcher.log
```

### Manual Testing

```bash
# Run watcher manually (for testing)
cd ~/Dropbox/cloud_storage/DigiDoc/file_watcher_service
python3 watcher.py
```

## Troubleshooting

### Service Not Starting

1. Check plist syntax: `plutil -lint ~/Library/LaunchAgents/com.digidoc.filewatcher.plist`
2. Check logs for errors
3. Verify Python path in plist matches your system
4. Verify DigiDoc service is running: `curl http://127.0.0.1:5000/digidoc/health`

### Files Not Being Processed

1. Verify queue directory exists and is writable
2. Check that files are being renamed to `ready_*.png`
3. Verify DigiDoc service is accessible
4. Check watcher logs for API errors

### Permission Issues

- Ensure queue directory has correct permissions
- For system daemon, ensure file paths are accessible to the service user

## Multi-Tenant Considerations

The file watcher is designed to support multiple tenants in the future:

- Each tenant can have its own queue directory
- Tenant configuration stored in `logs/tenants/`
- API calls include `calling_app_id` to identify tenant

## Uninstallation

### User-Level

```bash
cd ~/Dropbox/cloud_storage/DigiDoc/file_watcher_service
./uninstall_launchagent.sh
```

### System-Level

```bash
cd ~/Dropbox/cloud_storage/DigiDoc/file_watcher_service
sudo ./uninstall_launchdaemon.sh
```

## Dependencies

Install Python dependencies:

```bash
pip3 install -r requirements.txt
```

Required packages:
- `watchdog>=3.0.0` - File system event monitoring
- `requests>=2.31.0` - HTTP client for API calls
