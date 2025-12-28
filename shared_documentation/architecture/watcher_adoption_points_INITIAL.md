# Watcher Adoption Points - Initial Review

**Date**: 2025-12-23  
**Purpose**: Compare WATCHER_SPECIFICATION.md with MASTER_ARCHITECTURE.md to identify contradictions, omissions, and alignment issues before integration.

**Status**: Initial Review - Questions for Resolution

---

## User Clarifications (2025-12-23)

### Critical Clarifications Applied:
1. **Watcher Independence**: Watcher operates **FIRST and COMPLETELY independently** of DigiDoc. Watcher completes the file renaming process **BEFORE** triggering DigiDoc. Other than error handling, Watcher completes completely before the configuration-based API call.

2. **File Locations**: Config and logs are stored in best practices locations for macOS non-GUI utilities:
   - **Config**: `~/Library/Preferences/` (user) or `/Library/Preferences/` (system) - ✅ **VERIFIED** as macOS best practice
   - **Logs**: `~/Library/Logs/` (user) or `/var/log/` (system) - ✅ **VERIFIED** as macOS best practice
   - These locations align with macOS standards for compiled binaries/daemons

3. **File Format Support**: All raster file formats should be accommodated: TIFF, JPG, PNG, PDF, etc.

### Impact on Review:
- Questions 1.2, 1.3: **RESOLVED** - Watcher rename happens first, two-stage naming confirmed
- Questions 3.1, 3.3: **VERIFIED** - File locations are correct per macOS best practices
- Question 4.1: **RESOLVED** - TIFF support confirmed, needs to be added to MA.md

---

## Review Methodology

This document compares:
- **WS.md**: `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/apps/watcher/documentation/WATCHER_SPECIFICATION.md`
- **MA.md**: `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/shared_documentation/architecture/MASTER_ARCHITECTURE.md`

Each section presents questions that need resolution to align both documents.

---

## 1. File Detection & Ingestion Workflow

### Question 1.1: File Detection Method
**WS.md says**: Uses FSEvents (macOS) / inotify (cloud) - native file system events, no polling  
**MA.md says**: "Watch directory with complex logic: atomic renaming, ghosted file detection, multiple simultaneous write handling"  
**Status**: ✅ **ALIGNED** - Both agree on event-driven, no polling

### Question 1.2: Atomic Rename Location
**WS.md says**: Watcher performs atomic rename BEFORE calling DigiDoc  
**MA.md says**: "File detected by watcher" → "Enqueue to DigiDoc" (no mention of rename happening first)  
**Status**: ✅ **RESOLVED** - User clarified: Watcher operates FIRST and COMPLETELY independently. Watcher completes rename BEFORE triggering DigiDoc.

**Resolution Needed**: 
- [x] **CONFIRMED**: Watcher renames files BEFORE enqueuing to DigiDoc
- [ ] **UPDATE MA.md**: State "Watcher renames file atomically, then calls DigiDoc API with new path"
- [ ] **UPDATE MA.md**: Clarify Watcher operates independently and completes before DigiDoc is triggered

### Question 1.3: File Naming Convention
**WS.md says**: Configurable pattern `{timestamp}_{random8}.{ext}` (e.g., `20251223_104118_abcd1234.pdf`)  
**MA.md says**: Archive format `{vendor}_{YYYYMMDD}_{total}.{ext}` (e.g., `mead_clark_20251219_665.34.pdf`)  
**Status**: ✅ **CLARIFIED** - Two-stage naming: Watcher rename (processing name) → DigiDoc archive (final name)

**Resolution Needed**:
- [x] **CONFIRMED**: Watcher rename is processing name, DigiDoc archive is final name
- [ ] **UPDATE MA.md**: Document two-stage naming explicitly: "Watcher renames to `{timestamp}_{random8}.{ext}`, DigiDoc receives this renamed file, then archives as `{vendor}_{YYYYMMDD}_{total}.{ext}`"
- [x] **CONFIRMED**: DigiDoc uses Watcher's renamed file, then renames again for archive

---

## 2. API Integration Points

### Question 2.1: DigiDoc API Endpoint
**WS.md says**: `http://localhost:8001/process` (configurable endpoint + auth token)  
**MA.md says**: `POST /api/digidoc/enqueue` (no port specified, no auth token mentioned for MVP)  
**Status**: ✅ **RESOLVED** - 2025-12-23

**Resolution**:
- [x] **Endpoint**: `/api/digidoc/queue` (RESTful, aligns with MA.md and best practices)
- [x] **Port**: `8001` (configurable via config file + environment variable)
- [x] **Auth Token**: Required from day 1 (Zero Trust principle - even localhost authenticates)
- [x] **Rationale**: RESTful design follows industry best practices, Zero Trust ensures security

### Question 2.2: API Request Payload
**WS.md says**: "send HTTP POST to local DigiDoc API (e.g., `http://localhost:8001/process` with file list)"  
**MA.md says**: Request includes `file_path`, `calling_app_id`, `source`, `metadata`  
**Status**: ✅ **RESOLVED** - 2025-12-23

**Resolution**:
- [x] **Single file** (not batch) - avoids async/WAN issues
- [x] **Payload structure defined** in WS.md:
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
- [x] **Additional fields**: `device_name` and `device_id` for troubleshooting stateless systems
- [x] **Path Requirement**: The `file_path` parameter in API requests **MUST** be an absolute path. See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" for ecosystem-wide requirements.

### Question 2.3: Post-Rename Action Options
**WS.md says**: `none`, `auto`, `notify`, `both` - where `auto` = "immediately trigger DigiDoc processing"  
**MA.md says**: "File detected by watcher" → "Enqueue to DigiDoc" (always enqueues, no mention of options)  
**Status**: ✅ **RESOLVED** - 2025-12-23

**Resolution**:
- [x] **`none`**: Rename file only, no API call, no notification
- [x] **`notify`**: Rename file, send notification, but don't call DigiDoc
- [x] **`auto`**: Rename file, call DigiDoc API directly
- [x] **`both`**: Rename file, call DigiDoc API + send notification
- [x] **Priority-based selection**: Watcher uses configurable priority list to select host and action based on network conditions
- [x] **MA.md updated**: Documents conditional enqueue logic and priority-based host selection
- [x] **Logic flow**: Environment detection → Priority list check → Action execution based on available host

---

## 3. Configuration & Deployment

### Question 3.1: Watcher Configuration Location
**WS.md says**: 
- User: `~/Library/Preferences/com.scottroberts.digidocwatcher.yaml`
- System: `/Library/Preferences/com.scottroberts.digidocwatcher.yaml`
- Cloud: Environment variables or mounted YAML

**MA.md says**: 
- Development: `~/.local/bin/` (executables), `~/Library/LaunchAgents/` (plist)
- Production: `/usr/local/bin/` (executables), `/Library/LaunchDaemons/` (plist)
- Cloud: Container filesystem

**Status**: ✅ **VERIFIED** - WS.md locations align with macOS best practices:
- `~/Library/Preferences/` is correct for user-level configs (macOS native apps)
- `/Library/Preferences/` is correct for system-level configs
- Alternative: `~/.config/` (XDG spec) but `~/Library/Preferences/` is more macOS-native for compiled binaries

**Resolution Needed**:
- [ ] **UPDATE MA.md**: Add Watcher config file locations (match WS.md)
- [ ] **UPDATE MA.md**: Document relationship: plist → executable → config file
- [ ] **CLARIFY**: Does config file path need to be in plist, or discovered automatically? (Typically auto-discovered by app name)

### Question 3.2: Binary Naming
**WS.md says**: `digidocwatcher`  
**MA.md says**: `com.digidoc.watcher.plist` (plist name, but executable name not specified)  
**Status**: ⚠️ **INCOMPLETE** - MA.md should specify executable name

**Resolution Needed**:
- [ ] Add executable name `digidocwatcher` to MA.md
- [ ] Align plist naming: `com.digidoc.watcher.plist` vs `com.scottroberts.digidocwatcher.plist`

### Question 3.3: Log File Location
**WS.md says**: 
- User: `~/Library/Logs/DigiDocWatcher.log`
- System: `/var/log/digidocwatcher.log`
- Cloud: Container stdout/stderr

**MA.md says**: (No Watcher log locations specified)  
**Status**: ✅ **VERIFIED** - WS.md locations align with macOS best practices:
- `~/Library/Logs/` is correct for user-level logs (macOS standard)
- `/var/log/` is correct for system-level logs (Unix standard)

**Resolution Needed**:
- [ ] **UPDATE MA.md**: Add Watcher log file locations (match WS.md)
- [ ] **UPDATE MA.md**: Document log format (YAML structured logs per WS.md)

---

## 4. File Types & Processing

### Question 4.1: Supported File Types
**WS.md says**: `.pdf`, `.jpg`, `.jpeg`, `.png`, `.tiff`  
**MA.md says**: "Raster Image: PDF/JPG/PNG" (TIFF not mentioned)  
**Status**: ✅ **RESOLVED** - User clarified: All raster file formats should be accommodated (TIFF, JPG, PNG, etc.)

**Resolution Needed**:
- [x] **CONFIRMED**: DigiDoc should support TIFF files
- [ ] **UPDATE MA.md**: Add TIFF to supported formats list: "Raster Image: PDF/JPG/PNG/TIFF"
- [ ] **UPDATE MA.md**: Ensure preprocessing pipeline handles TIFF format

### Question 4.2: File Source Types
**WS.md says**: SFTP upload, macOS shared folder (SMB/AFP), direct scanner save  
**MA.md says**: (No explicit source types mentioned)  
**Status**: ⚠️ **OMISSION** - MA.md should document file source types

**Resolution Needed**:
- [ ] Add file source types to MA.md
- [ ] Document how source type affects processing (if at all)

---

## 5. Error Handling & Resilience

### Question 5.1: File In-Use Handling
**WS.md says**: "File in use → wait and retry (max 30 seconds)"  
**MA.md says**: (No specific timeout mentioned for file locking)  
**Status**: ⚠️ **OMISSION** - MA.md should document file locking timeout

**Resolution Needed**:
- [ ] Add file locking timeout (30 seconds) to MA.md
- [ ] Document retry logic in MA.md error handling section

### Question 5.2: Rename Collision Handling
**WS.md says**: "Rename collision → append incrementing suffix"  
**MA.md says**: (No mention of rename collision handling)  
**Status**: ⚠️ **OMISSION** - MA.md should document collision handling

**Resolution Needed**:
- [ ] Add rename collision handling to MA.md
- [ ] Document incrementing suffix pattern

### Question 5.3: Error Notification
**WS.md says**: "All errors logged + sent via notification webhook"  
**MA.md says**: "Error notification: Post-MVP (email/Slack)"  
**Status**: ✅ **RESOLVED** - 2025-12-23

**Resolution**:
- [x] **Watcher has no MVP phase** - error notifications available from day 1
- [x] **MA.md updated**: Reflects that Watcher error notifications are available from day 1
- [x] **Note**: MA.md "Post-MVP" refers to DigiDoc's MVP timeline, not Watcher's (Watcher development happens post DigiDoc MVP)

---

## 6. Notification System

### Question 6.1: Notification Channels
**WS.md says**: Slack webhook, email (SMTP), HTTP POST to custom endpoint  
**MA.md says**: "Post-MVP (email/Slack)"  
**Status**: ✅ **RESOLVED** - 2025-12-23

**Resolution**:
- [x] **Watcher has no MVP phase** - notifications available from day 1
- [x] **MA.md updated**: Reflects that Watcher notifications are available from day 1
- [x] **Channels**: Slack webhook, email (SMTP), HTTP POST to custom endpoint
- [x] **Note**: MA.md "Post-MVP" refers to DigiDoc's MVP timeline, not Watcher's

### Question 6.2: Notification Triggers
**WS.md says**: On error OR when `notify`/`both` configured  
**MA.md says**: (No notification triggers specified)  
**Status**: ⚠️ **OMISSION** - MA.md should document when notifications are sent

**Resolution Needed**:
- [ ] Add notification trigger conditions to MA.md
- [ ] Document notification payload structure

---

## 7. Queue Integration

### Question 7.1: Queue Item Creation
**WS.md says**: When `auto` or `both` configured, send HTTP POST to DigiDoc API  
**MA.md says**: "Enqueue to DigiDoc (RQ Job)" - assumes always enqueues  
**Status**: ✅ **RESOLVED** - 2025-12-23

**Resolution**:
- [x] **Conditional enqueue confirmed**: Watcher can skip enqueueing (`none` or `notify` options)
- [x] **MA.md updated**: Documents conditional enqueue logic and priority-based host selection
- [x] **Logic**: Priority list determines which action to take based on available DigiDoc hosts

### Question 7.2: Queue Item Metadata
**WS.md says**: (No specific metadata mentioned)  
**MA.md says**: File path, metadata (source folder, timestamp), calling app ID, context  
**Status**: ✅ **RESOLVED** - 2025-12-23

**Resolution**:
- [x] **Exact metadata structure defined** in WS.md (see Question 2.2)
- [x] **Aligned with MA.md**: Includes all expected fields plus device_name/device_id
- [x] **Metadata includes**: source_directory, original_filename, renamed_filename, timestamp, device_name, device_id

---

## 8. Stabilization & Timing

### Question 8.1: Stabilization Delay
**WS.md says**: `stabilization_delay_seconds: 2` - wait until file closed (no modifications for delay)  
**MA.md says**: (No stabilization delay mentioned)  
**Status**: ✅ **RESOLVED** - 2025-12-23

**Resolution**:
- [x] **MA.md updated**: Documents stabilization delay (2 seconds configurable)
- [x] **Logic documented**: Watcher waits for file to be closed and stable before processing
- [x] **Rationale**: Prevents partial-file processing by ensuring file write is complete

---

## 9. Output Directory Alignment

### Question 9.1: Watcher Output vs DigiDoc Queue Directory
**WS.md says**: `output_directory: /Users/scott/DigiDoc/Incoming` (configurable)  
**MA.md says**: `queue_directory: "{storage_base}/queue"` (default: `~/digidoc_storage/queue`)  
**Status**: ⚠️ **POTENTIAL MISMATCH** - Need to ensure Watcher output = DigiDoc queue input

**Resolution Needed**:
- [ ] Confirm: Should Watcher's `output_directory` = DigiDoc's `queue_directory`?
- [ ] If yes: Document this alignment requirement
- [ ] If no: Document how files move from Watcher output to DigiDoc queue

---

## 10. Cloud/Container Deployment

### Question 10.1: Container Orchestration
**WS.md says**: Kubernetes/Docker Compose orchestration, config via environment variables or mounted YAML  
**MA.md says**: "Container filesystem (typically `/usr/local/bin/` or `/app/bin/`)", "Container orchestration (Kubernetes, Docker Swarm, systemd in container)"  
**Status**: ✅ **MOSTLY ALIGNED** - Both mention containers, WS.md more specific

**Resolution Needed**:
- [ ] Add Docker Compose mention to MA.md
- [ ] Align on container paths if needed

---

## Summary of Required Changes

### High Priority (Contradictions - Need Resolution)
1. ✅ **File Rename Timing**: **RESOLVED** - Watcher completes rename BEFORE calling DigiDoc
2. **Post-Rename Actions**: Align `none`/`auto`/`notify`/`both` options with MA.md workflow
3. **Notification Timing**: Clarify MVP vs post-MVP for notifications
4. **API Endpoint**: Align endpoint format, port, and auth token requirements

### Medium Priority (Omissions - Need Documentation)
5. ✅ **Config File Locations**: **VERIFIED** - WS.md locations are correct (macOS best practices)
6. ✅ **Log File Locations**: **VERIFIED** - WS.md locations are correct (macOS best practices)
7. **File Source Types**: Document SFTP/SMB/AFP/scanner sources in MA.md
8. **Error Handling Details**: Add file locking timeout, collision handling to MA.md
9. **Stabilization Delay**: Document file stabilization logic in MA.md
10. ✅ **File Types**: **RESOLVED** - All raster formats (TIFF, JPG, PNG, etc.) should be supported

### Low Priority (Inconsistencies - Need Alignment)
11. **Binary Naming**: Ensure consistent naming (`digidocwatcher`)
12. **Metadata Structure**: Define exact API payload structure in WS.md
13. **Output Directory**: Ensure Watcher output aligns with DigiDoc queue directory
14. **Config/Log Locations in MA.md**: Add verified locations from WS.md to MA.md documentation

---

## Review Status Summary

### ✅ Resolved (14 items) - 2025-12-23
1. **File Rename Timing** - Watcher completes rename BEFORE calling DigiDoc ✅
2. **File Naming Convention** - Two-stage naming confirmed (Watcher → DigiDoc → Archive) ✅
3. **Config File Locations** - Verified as macOS best practices ✅
4. **Log File Locations** - Verified as macOS best practices ✅
5. **File Format Support** - All raster formats (TIFF, JPG, PNG, etc.) confirmed ✅
6. **API Endpoint** - `/api/digidoc/queue` (RESTful), port 8001, auth token required ✅
7. **API Payload Structure** - Exact structure defined with device_name/device_id ✅
8. **Post-Rename Actions** - Priority-based host selection with none/auto/notify/both options ✅
9. **Notification Timing** - Available from day 1 (Watcher has no MVP phase) ✅
10. **Error Notification Timing** - Available from day 1 (Watcher has no MVP phase) ✅
11. **Stabilization Delay** - Documented in MA.md (2 seconds configurable) ✅
12. **File In-Use Handling** - Documented in MA.md (30 second timeout) ✅
13. **Rename Collision Handling** - Documented in MA.md (incrementing suffix) ✅
14. **Queue Item Metadata** - Exact structure defined in WS.md ✅

### ⚠️ Remaining Items (Documentation Only)
1. **File Source Types** - Add to MA.md as informational (SFTP/SMB/AFP/scanner)
2. **Binary Naming** - Ensure consistent naming (`digidocwatcher`, `com.digidoc.watcher.plist`)
3. **Output Directory** - Document alignment requirement (Watcher output = DigiDoc queue input)
4. **Config File Discovery** - Document auto-discovery method

### 📝 Documentation Updates Completed
- ✅ **MA.md**: Added Watcher Integration section, updated all Watcher references, added status markers, added decision rationale
- ✅ **WS.md**: Added exact API payload structure, priority-based host selection, clarified post-rename actions
- ✅ **Both**: Aligned on API endpoint format (`/api/digidoc/queue`), port (8001), authentication (required)
- ✅ **digidoc_config.yaml**: Added API port and endpoint configuration
- ✅ **ARCHITECTURE_CHANGELOG.md**: Created version tracking system

---

## Next Steps

1. **Review this document** - Answer remaining questions (9 pending items)
2. **Update WS.md** - Add missing details (API payload structure, clarify actions)
3. **Update MA.md** - Add Watcher-specific sections, align workflow, add resolved items
4. **Create integration plan** - Document how Watcher integrates with DigiDoc workflow
5. **Update timeline** - Add Watcher adoption milestones to SCHEDULE.md

---

**End of Initial Review**
