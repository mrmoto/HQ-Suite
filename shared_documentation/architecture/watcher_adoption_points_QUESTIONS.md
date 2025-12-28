# Watcher Adoption Points - Questions for Resolution

**Date**: 2025-12-23  
**Purpose**: Organized questions from watcher_adoption_points_INITIAL.md for systematic resolution.

---

## High Priority Questions (API & Integration)

### Q1: API Endpoint Format
**Question**: What should the DigiDoc API endpoint be?
- **WS.md says**: `http://localhost:8001/process`
- **MA.md says**: `POST /api/digidoc/enqueue` (no port)

**Options**:
- A) `/api/digidoc/enqueue` (RESTful, matches MA.md)
- B) `/process` (simpler, matches WS.md)
- C) Other: ___________

**Also need**:
- Port number: `8001` or configurable?
- Auth token: Required for MVP or post-MVP?

---

### Q2: API Request Payload Structure
**Question**: What exact structure should Watcher send to DigiDoc?

**WS.md says**: "with file list" (unspecified structure)  
**MA.md says**: `file_path`, `calling_app_id`, `source`, `metadata`

**Need to define**:
- Single file or batch processing?
- Exact JSON structure
- Required vs optional fields

**Proposed structure** (based on MA.md):
```json
{
  "file_path": "/path/to/renamed_file.pdf",
  "calling_app_id": "required",
  "source": "scanner|sftp|shared_folder",
  "metadata": {
    "original_filename": "original.pdf",
    "source_directory": "/Incoming/SFTP",
    "renamed_filename": "20251223_104118_abcd1234.pdf",
    "timestamp": "2025-12-23T10:41:18Z"
  }
}
```

**Path Requirement**: The `file_path` parameter in API requests **MUST** be an absolute path. See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" for ecosystem-wide requirements.

**Confirm or modify**: ___________

---

### Q3: Post-Rename Action Options
**Question**: What does each option mean, and can Watcher skip calling DigiDoc?

**WS.md options**:
- `none` — do nothing (default)
- `auto` — immediately trigger DigiDoc processing
- `notify` — send user notification
- `both` — trigger processing + notify

**Clarification needed**:
- Does `none` mean: rename file but DON'T call DigiDoc API?
- Does `notify` mean: rename file, send notification, but DON'T call DigiDoc?
- Or does `none` mean something else?

**Your answer**: ___________

---

## Medium Priority Questions (Notifications & Errors)

### Q4: Notification Timing (MVP vs Post-MVP)
**Question**: Are notifications MVP or post-MVP?

**WS.md says**: Full notification system (Slack, email, HTTP POST)  
**MA.md says**: "Post-MVP (email/Slack)"

**Options**:
- A) MVP: Notifications available from start
- B) Post-MVP: Notifications added later
- C) Hybrid: Error notifications MVP, user notifications post-MVP

**Your answer**: ___________

---

### Q5: Error Notification Timing
**Question**: Are error notifications MVP or post-MVP?

**WS.md says**: "All errors logged + sent via notification webhook"  
**MA.md says**: "Error notification: Post-MVP"

**Options**:
- A) MVP: Error notifications via webhook
- B) Post-MVP: Error notifications added later
- C) MVP: Log only, notifications post-MVP

**Your answer**: ___________

---

## Lower Priority Questions (Details & Alignment)

### Q6: Binary Naming Consistency
**Question**: What should the plist name be?

**WS.md says**: Executable = `digidocwatcher`  
**MA.md says**: Plist = `com.digidoc.watcher.plist`  
**WS.md config**: `com.scottroberts.digidocwatcher.yaml`

**Options**:
- A) `com.digidoc.watcher.plist` (matches MA.md)
- B) `com.scottroberts.digidocwatcher.plist` (matches config file)
- C) Other: ___________

**Your answer**: ___________

---

### Q7: File Source Types
**Question**: How should source types be documented?

**WS.md says**: SFTP upload, macOS shared folder (SMB/AFP), direct scanner save  
**MA.md says**: (Not mentioned)

**Options**:
- A) Add to MA.md as informational (doesn't affect processing)
- B) Add to MA.md and document if source type affects processing
- C) Leave in WS.md only

**Your answer**: ___________

---

### Q8: Output Directory Alignment
**Question**: Should Watcher's output directory = DigiDoc's queue directory?

**WS.md says**: `output_directory: /Users/scott/DigiDoc/Incoming` (configurable)  
**MA.md says**: `queue_directory: "{storage_base}/queue"` (default: `~/digidoc_storage/queue`)

**Options**:
- A) Yes, they must match (Watcher output = DigiDoc queue input)
- B) No, they can differ (files move from Watcher output to DigiDoc queue)
- C) Configurable alignment

**Your answer**: ___________

---

### Q9: Config File Discovery
**Question**: How does Watcher find its config file?

**Options**:
- A) Auto-discovered by app name (standard macOS pattern)
- B) Specified in plist file
- C) Environment variable
- D) Command-line argument

**Your answer**: ___________

---

## Questions That Need Documentation Updates Only

These are resolved but need to be added to MA.md:

### Q10: File In-Use Handling
- **Answer**: 30 second timeout (from WS.md)
- **Action**: Add to MA.md error handling section

### Q11: Rename Collision Handling
- **Answer**: Append incrementing suffix (from WS.md)
- **Action**: Add to MA.md with suffix pattern

### Q12: Stabilization Delay
- **Answer**: 2 seconds (configurable), wait for file to be closed and stable
- **Action**: Add to MA.md workflow section

### Q13: Queue Item Metadata
- **Answer**: Need to define exact structure (see Q2 above)
- **Action**: Add to WS.md and align with MA.md

---

## Summary

**Questions Needing Your Answers** (9):
1. Q1: API endpoint format, port, auth token
2. Q2: API request payload structure
3. Q3: Post-rename action options behavior
4. Q4: Notification timing (MVP vs post-MVP)
5. Q5: Error notification timing (MVP vs post-MVP)
6. Q6: Binary/plist naming consistency
7. Q7: File source types documentation
8. Q8: Output directory alignment
9. Q9: Config file discovery method

**Questions Needing Documentation Only** (4):
- Q10-Q13: Add resolved items to MA.md

---

**Ready for your answers!**
