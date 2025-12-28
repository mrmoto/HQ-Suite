# Watcher Utility — File Ingestion Monitor

**Date**: 2025-12-23
**Author**: Scott Roberts (with Grok assistance)
**Purpose**: Reliable, atomic file ingestion for DigiDoc OCR pipeline on macOS
(local M4 Max and future headless server). The utility is a **compiled binary
executable** (Swift for macOS environments), not a script.

## 1. Overview

The Watcher Utility is a **background daemon** that monitors designated input
directories for new raster image files (PDF, JPG, PNG, TIFF) arriving via:

- SFTP upload
- macOS shared folder (SMB/AFP)
- Direct scanner save (USB or network scanner)

It uses **native file system events** (no polling) for instant detection on
supported platforms.

Upon detection of a complete file, it performs an **atomic rename**, logs the
event, and optionally triggers the DigiDoc processing workflow or notifies the
user based on configurable settings.

This utility is the **first link** in the DigiDoc → HQ pipeline.

## 2. Requirements

### Functional

1. **Event-driven monitoring** using native file system events (no polling).
2. **Atomic rename** upon file close/completion to prevent partial-file
   processing.
3. **Log entry** for every successful rename (original name → new name,
   timestamp, source directory).
4. **Configurable watch directories** (multiple allowed).
5. **Configurable output directory** for renamed files.
6. **Naming convention** for renamed files (configurable pattern).
7. **Graceful handling** of file-in-use (wait until closed).
8. **Error notification** via external channels (Slack webhook, email, HTTP
   POST).
9. **Configurable post-rename workflow**:
   - After successful rename, initiate DigiDoc processing based on predefined
     options and priority-based host selection.
   - **Options** (defined per host in priority list):
     - `none` — Rename file only, no API call, no notification
     - `auto` — Rename file + call DigiDoc API directly
     - `notify` — Rename file + send notification, **no API call** (avoids slow WAN calls)
     - `both` — Rename file + call DigiDoc API + send notification
   - **Priority-based selection**: Watcher checks hosts in priority order, uses first available host's action
10. **User notification system**:
    - When `notify` or `both` selected, send configurable notification with
      details (file count, paths, timestamp).
    - Notification channels: Slack webhook, email (SMTP), HTTP POST to custom
      endpoint.

### Non-Functional

- **Compiled binary** (Swift for macOS) — no runtime dependencies.
- **User-level daemon** on desktop (runs as current user).
- **System-level capable** on headless server.
- **Cloud Host Capable** (containerized deployment in cloud environments).
- **Low resource usage** (<5 % CPU, <50 MB RAM).
- **Crash-resistant** (auto-restart via launchd or container orchestration).
- **macOS 14+ compatible** (Tahoe and later) for native deployments.

## 3. Architecture

### Components

1. **Watcher Daemon** (compiled Swift binary for macOS, containerized for cloud)
   - Uses **FSEvents** framework on macOS (native file system events — instant,
     efficient).
   - In cloud/container environments, uses inotify or equivalent (via language
     libraries).
   - Monitors configured directories.
   - On relevant events, tracks file handles.
   - When file is closed (no modifications for configurable delay), triggers
     rename + post-rename workflow.

2. **Renamer Module**
   - Atomic rename using language-native atomic move operations.
   - Generates new filename (configurable pattern).

3. **Logger Module**
   - Structured YAML log file (location per best practices).
   - Entry format:
     ```yaml
     timestamp: 2025-12-23T10:41:18Z
     event: rename_success
     original_path: /path/to/original.pdf
     new_path: /path/to/20251223_104118_abcd1234.pdf
     source_directory: /Incoming/SFTP
     ```

4. **Notifier Module**
   - On error or when `notify`/`both` configured, send notification via:
     - HTTP POST to configurable webhook
     - SMTP email (configurable server)
     - Slack incoming webhook

5. **DigiDoc Trigger Module**
   - When `auto` or `both` configured, send HTTP POST to DigiDoc API
   - **Endpoint**: `POST /api/digidoc/queue` (RESTful)
   - **Port**: 8001 (configurable via config file + environment variable)
   - **Authentication**: API token required (Zero Trust - even localhost authenticates)
   - **Request Headers**: `Authorization: Bearer <api_token>`, `Content-Type: application/json`
   - **Single file processing** (not batch - avoids async/WAN issues)
   
   **API Request Payload**:
   ```json
   {
     "file_path": "/path/to/renamed_file.pdf",
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
   
   **Path Requirements**:
   - The `file_path` parameter **MUST** be an absolute path (e.g., `/Users/username/Dropbox/Application Data/DigiDoc/queue/file.pdf`)
   - Relative paths are not accepted
   - Paths are expanded to absolute paths during configuration loading if `~` is used
   
   **API Response**:
   ```json
   {
     "queue_item_id": "uuid",
     "status": "pending",
     "message": "File enqueued successfully"
   }
   ```

### Priority-Based Host Selection

Watcher uses a configurable priority list to intelligently route files to DigiDoc instances based on network conditions and availability.

**Environments**:
- **Dev Machine**: This development computer
- **Headless Server**: Scanner computer (e.g., macmini)
- **Cloud Computer**: VPS/container environment

**Decision Logic**:
1. Detect environment: Dev machine | Headless server | Cloud computer
2. For each file:
   a. **ALWAYS** perform atomic rename (100% uptime guarantee)
   b. Check priority list of DigiDoc hosts (in order)
   c. For each host in priority:
      - Test connectivity (MAC address match + ping for LAN, ping for WAN/cloud)
      - IF available: Execute action from config, break (stop checking)
      - IF not available: Continue to next host
   d. IF no hosts available: Send error notification to webhook

**Network Detection**:
- **LAN Detection**: MAC address matching against known local devices + network ping
  - Handles multiple MACs per device (WiFi + Ethernet)
  - VPN configuration noted for future (DDNS utility)
- **WAN/Cloud Detection**: Ping-based connectivity test

**Example Priority List** (for headless server):
```yaml
digidoc_hosts_priority:
  - host: "dev_computer_lan"
    endpoint: "http://192.168.1.100:8001/api/digidoc/queue"
    action: "both"  # Trigger DigiDoc + notify
    detection: "mac_address_match + ping"
  - host: "dev_computer_wan"
    endpoint: "http://ddns.example.com:8001/api/digidoc/queue"
    action: "notify"  # Notify only (avoid slow WAN API calls)
    detection: "ping_only"
  - host: "cloud_digidoc_1"
    endpoint: "https://cloud.example.com/api/digidoc/queue"
    action: "auto"  # Direct API call
    detection: "ping_only"
```

### Deployment Locations (2025 Best Practices)

| Environment | Binary Location                  | Config Location                                      | Log Location                     | Orchestration                                       |
|-------------|----------------------------------|------------------------------------------------------|----------------------------------|-----------------------------------------------------|
| User (desktop) | `~/.local/bin/digidocwatcher`    | `~/Library/Preferences/com.scottroberts.digidocwatcher.yaml` | `~/Library/Logs/DigiDocWatcher.log` | `~/Library/LaunchAgents/com.scottroberts.digidocwatcher.plist` |
| System (headless macOS) | `/usr/local/bin/digidocwatcher`  | `/Library/Preferences/com.scottroberts.digidocwatcher.yaml` | `/var/log/digidocwatcher.log`    | `/Library/LaunchDaemons/com.scottroberts.digidocwatcher.plist` |
| Cloud (container) | Docker image                     | Config via environment variables or mounted YAML      | Container stdout/stderr          | Kubernetes/Docker Compose orchestration             |

### Configuration File (YAML format)

```yaml
watch_directories:
  - /Users/scott/Incoming/SFTP
  - /Users/scott/Incoming/SharedFolder
  - /Users/scott/Incoming/Scanner
output_directory: /Users/scott/DigiDoc/Incoming
naming_pattern: "{timestamp}_{random8}.{ext}"
file_types:
  - .pdf
  - .jpg
  - .jpeg
  - .png
  - .tiff
stabilization_delay_seconds: 2
post_rename_action: both  # none, auto, notify, both
digidoc_hosts_priority:
  - host: "dev_computer_lan"
    endpoint: "http://192.168.1.100:8001/api/digidoc/queue"
    action: "both"
    detection: "mac_address_match + ping"
  - host: "dev_computer_wan"
    endpoint: "http://ddns.example.com:8001/api/digidoc/queue"
    action: "notify"
    detection: "ping_only"
  - host: "cloud_digidoc_1"
    endpoint: "https://cloud.example.com/api/digidoc/queue"
    action: "auto"
    detection: "ping_only"
digidoc_api_token: your-secret-token
notification_webhook: https://hooks.slack.com/services/...
```

## 4. Error Handling & Resilience

- **File in use**: Wait and retry (max 30 seconds timeout).
- **Rename collision**: Append incrementing suffix (e.g., `_001`, `_002`).
- **Monitoring failure**: Auto-restart via launchd (macOS) or container orchestration (cloud).
- **No DigiDoc host available**: **ALWAYS** rename file (100% uptime guarantee), send error notification to webhook, log error.
- **All errors**: Logged to structured YAML log file + sent via notification webhook.

## 5. Testing Strategy

- Unit tests for renamer, logger, notifier, trigger.
- Integration test: simulate file creation in watch directory.
- Stress test: 100 simultaneous file drops.
