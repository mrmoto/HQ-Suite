# Documentation Path Analysis

**Date**: 2025-12-24  
**Purpose**: Assessment of documentation files to verify path handling specifications align with industry best practices: absolute paths for apps (hq, digidoc, watcher) and path expansion for API communications.

## Target Approach (Industry Best Practice)

- **Apps (hq, digidoc, watcher)**: Use absolute paths internally
- **API Communications**: Use path expansion (e.g., `os.path.expanduser`, environment variables) for cross-system compatibility

---

## Category A: Explicitly States Correct Approach

Files that clearly document the correct path handling approach.

### 1. `apps/hq/.cursor/plans/file_watcher_relocation_and_storage_path_configuration_29bd9cae.plan.md`

**Location**: Lines 187-207

**Quote**:
```
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
```

**Status**: ✅ **Explicitly states correct approach** - File watcher passes absolute paths to DigiDoc app

---

## Category B: Explicitly Contradicts

Files that explicitly contradict the target approach (e.g., specify relative paths, don't use path expansion).

**Result**: **None found** - No documentation files explicitly contradict the target approach.

---

## Category C: Ambiguous

Files that show path examples or mention paths but don't clearly specify whether absolute paths are required for API communications or apps.

### 1. `shared_documentation/architecture/MASTER_ARCHITECTURE.md`

**Locations**: 
- Lines 1196-1210 (API request payload example)
- Lines 1442-1456 (Watcher API request payload example)

**Quotes**:
```json
{
  "file_path": "/path/to/renamed_file.pdf",
  "calling_app_id": "required",
  ...
}
```

**Issue**: Shows example paths (`/path/to/renamed_file.pdf`) but doesn't explicitly state:
- Whether `file_path` in API requests must be absolute
- Whether path expansion should be used for API communications
- That apps should use absolute paths internally

**Recommendation**: Add explicit specification that:
- `file_path` in API requests must be absolute paths
- Apps (hq, digidoc, watcher) use absolute paths internally
- Path expansion (e.g., `os.path.expanduser`) is used for cross-system compatibility in API communications

### 2. `apps/watcher/documentation/WATCHER_SPECIFICATION.md`

**Location**: Lines 110-125 (API Request Payload)

**Quote**:
```json
{
  "file_path": "/path/to/renamed_file.pdf",
  ...
}
```

**Issue**: Shows example API payload with `file_path` but doesn't specify:
- Whether the path must be absolute
- Path expansion requirements for cross-system compatibility

**Recommendation**: Add explicit specification that `file_path` must be an absolute path.

### 3. `apps/watcher/documentation/watcher_api_design_analysis.md`

**Location**: Line 194 (Endpoint Path specification)

**Issue**: References API endpoint design but doesn't mention path requirements for the `file_path` parameter in requests.

**Recommendation**: Add specification that `file_path` parameter must be absolute path.

### 4. `shared_documentation/architecture/watcher_adoption_points_INITIAL.md`

**Location**: Lines 83, 91

**Quotes**:
- Line 83: `"MA.md says": Request includes file_path, calling_app_id, source, metadata`
- Line 91: `"file_path": "/path/to/renamed_file.pdf"`

**Issue**: References `file_path` in API requests but doesn't specify absolute vs relative or path expansion requirements.

**Recommendation**: Clarify that `file_path` must be absolute.

### 5. `shared_documentation/architecture/watcher_adoption_points_QUESTIONS.md`

**Location**: Lines 30, 40

**Quotes**:
- Line 30: `"MA.md says": file_path, calling_app_id, source, metadata`
- Line 40: `"file_path": "/path/to/renamed_file.pdf"`

**Issue**: Similar to above - references `file_path` without specifying absolute path requirement.

**Recommendation**: Clarify that `file_path` must be absolute.

---

## Category D: Missing Requirement

Files that reference file creation, file operations, or file paths but don't mention path handling requirements. These could benefit from explicit path handling documentation.

### 1. `apps/digidoc/file_watcher_service/README.md`

**Locations**: 
- Lines 9-10 (Directory paths)
- Line 73 (Environment variable `DOCUMENT_QUEUE_PATH`)
- Line 95 (Workflow mentions "with file path")

**Quotes**:
- Line 9: `- **Location**: ~/Dropbox/cloud_storage/DigiDoc/file_watcher_service/`
- Line 10: `- **Queue Directory**: ~/Dropbox/Application Data/DigiDoc/queue/`
- Line 95: `5. File watcher calls DigiDoc API: POST /digidoc/process with file path`

**Issue**: 
- References file paths and directory paths
- Mentions calling API "with file path" but doesn't specify:
  - That the file path must be absolute
  - That path expansion should be used for cross-system compatibility

**Recommendation**: Add explicit specification that:
- File watcher passes absolute file paths to DigiDoc API
- Path expansion (e.g., `os.path.expanduser`) is used for configurable paths

### 2. `apps/digidoc/README.md`

**Locations**:
- Lines 22-24 (Directory structure)
- Line 40 (Configuration: `DOCUMENT_QUEUE_PATH`)
- Lines 55-61 (Data flow mentions file paths)

**Quotes**:
- Line 24: `- **Queue Directory**: ~/Dropbox/Application Data/DigiDoc/queue/`
- Line 40: `- DOCUMENT_QUEUE_PATH: Queue directory path (defaults to ~/Dropbox/Application Data/DigiDoc/queue/)`
- Line 58: `4. File watcher calls DigiDoc API at /digidoc/process`

**Issue**: 
- References queue directory paths
- Mentions API calls but doesn't specify that file paths in API calls must be absolute
- Doesn't mention path expansion for API communications

**Recommendation**: Add explicit specification that:
- File paths passed to DigiDoc API must be absolute
- Path expansion is used for configuration paths

### 3. `shared_documentation/training/AGENT_TRAINING_GUIDE.md`

**Locations**:
- Lines 597-609 (File Storage Pattern section)
- Line 600 (MUST use configurable storage_base)

**Quotes**:
- Line 600: `- Use configurable storage_base (default ~/digidoc_storage/)`
- Line 601: `- Create queue item directory: {storage_base}/queue/{queue_item_id}/`
- Line 607: `- Hardcode storage paths`

**Issue**: 
- Specifies using configurable paths (good)
- Doesn't explicitly state:
  - That apps should use absolute paths internally
  - That API communications should use path expansion

**Recommendation**: Add explicit specification:
- Apps use absolute paths internally
- Path expansion (e.g., `os.path.expanduser`) for configurable paths

### 4. `development/DEVELOPMENT_BEST_PRACTICES.md`

**Location**: Lines 442-448 (Configuration Loading section)

**Quote**:
```
**Process**:
1. Load default config from YAML
2. Override with environment variables
3. Validate required values
4. Expand paths (e.g., `~/Dropbox/...`)
```

**Issue**: 
- Mentions path expansion in configuration loading (good)
- Doesn't explicitly state this as a requirement for:
  - Apps using absolute paths internally
  - API communications requiring path expansion

**Recommendation**: Clarify that:
- Path expansion is required for cross-system compatibility
- Apps use absolute paths internally after expansion

### 5. `shared_documentation/planning/workspace_best_practices_guidance.md`

**Location**: Lines 294-311 (Best Practice: Path Management section)

**Quote**:
```
**Use Absolute Paths in Documentation**:
- More reliable than relative paths
- Clear and explicit
- Easier to update when structure changes
```

**Issue**: 
- Specifies absolute paths for **documentation** (not code)
- Doesn't mention absolute paths for apps or path expansion for API communications

**Recommendation**: Clarify that this best practice applies to documentation, and separately document that:
- Apps use absolute paths internally
- API communications use path expansion

### 6. `shared_documentation/architecture/MASTER_ARCHITECTURE.md` (Additional sections)

**Location**: Lines 733-741 (Configuration File Paths section)

**Quote**:
```yaml
paths:
  storage_base: "~/digidoc_storage"
  queue_directory: "{storage_base}/queue"
  processed_directory: "{storage_base}/processed"
  failed_directory: "{storage_base}/failed"
  templates_directory: "{storage_base}/templates"
```

**Issue**: 
- Shows path configuration using `~` (path expansion marker)
- Doesn't explicitly state:
  - That these paths are expanded to absolute paths
  - That apps use absolute paths internally
  - Path expansion requirements for API communications

**Recommendation**: Add explicit specification:
- Configuration paths with `~` are expanded to absolute paths
- Apps use absolute paths internally after expansion
- API communications pass absolute paths

### 7. `apps/digidoc/TESTING_GUIDE.md`

**Location**: Line 99

**Quote**: `- [ ] Paths are correctly expanded`

**Issue**: 
- References path expansion testing (good)
- Doesn't specify that paths should be expanded to absolute paths
- Doesn't mention absolute path requirement for apps

**Recommendation**: Clarify that:
- Paths are expanded to absolute paths
- Apps use absolute paths internally

### 8. `apps/digidoc/IMPLEMENTATION_STATUS.md`

**Locations**: 
- Lines 9-14 (Path Corrections section)
- Lines 18-20 (Files Updated with Correct Paths)

**Quotes**:
- Line 11: `- **Cloud Storage Base**: ~/Dropbox/cloud_storage/ (NOT ~/cloud_storage/)`
- Line 18: `- ✅ ~/Dropbox/cloud_storage/DigiDoc/file_watcher_service/config.py - Uses ~/Dropbox/cloud_storage`

**Issue**: 
- Focuses on correct path values
- Doesn't mention:
  - That these paths are expanded to absolute paths
  - Absolute path requirement for apps
  - Path expansion for API communications

**Recommendation**: Add note that:
- Paths with `~` are expanded to absolute paths
- Apps use absolute paths internally

### 9. `development/TESTING_SKELETON.md`

**Location**: Line 88

**Quote**: `"file_path": "/Users/scottroberts/Dropbox/Application Data/DigiDoc/queue/Scan2025-12-18_133624_000.png"`

**Issue**: 
- Shows example with absolute path (good)
- Doesn't explicitly state this is a requirement

**Recommendation**: Add note that file_path in test examples must be absolute paths.

### 10. `shared_documentation/planning/PLANNING_CACHE.md` and `PLANNING_CACHE_TEMP.md`

**Locations**: Lines 61-64 (both files)

**Quotes**:
```
### 2025-12-23: Absolute Paths in Workspace File
**Decision**: Use absolute paths (not relative) in workspace file
```

**Issue**: 
- Specifies absolute paths for **workspace file** (not apps or API)
- Doesn't mention absolute paths for apps or path expansion for API communications

**Recommendation**: These are planning cache files (temporary), but if similar decisions are made about apps/API, they should be documented in permanent architecture docs.

---

## Summary Statistics

- **Category A (Explicitly Correct)**: 1 file
- **Category B (Contradicts)**: 0 files
- **Category C (Ambiguous)**: 5 files
- **Category D (Missing Requirement)**: 10 files

**Total Files Analyzed**: 16 files with significant path-related content

---

## Recommendations

### Priority 1: Update Architecture Documentation

1. **`shared_documentation/architecture/MASTER_ARCHITECTURE.md`**
   - Add explicit specification that `file_path` in API requests must be absolute paths
   - Clarify that apps (hq, digidoc, watcher) use absolute paths internally
   - Document that path expansion (e.g., `os.path.expanduser`) is used for cross-system compatibility

### Priority 2: Update API Documentation

2. **`apps/watcher/documentation/WATCHER_SPECIFICATION.md`**
   - Add specification that `file_path` parameter must be absolute path

3. **`apps/watcher/documentation/watcher_api_design_analysis.md`**
   - Add path requirements section specifying absolute paths

### Priority 3: Update App Documentation

4. **`apps/digidoc/file_watcher_service/README.md`**
   - Add specification that file watcher passes absolute file paths to DigiDoc API
   - Document path expansion usage for configurable paths

5. **`apps/digidoc/README.md`**
   - Add specification that file paths in API calls must be absolute
   - Document path expansion for configuration paths

### Priority 4: Update Training & Best Practices

6. **`shared_documentation/training/AGENT_TRAINING_GUIDE.md`**
   - Add explicit specification that apps use absolute paths internally
   - Clarify path expansion requirements

7. **`development/DEVELOPMENT_BEST_PRACTICES.md`**
   - Clarify that path expansion is required for cross-system compatibility
   - Document that apps use absolute paths internally after expansion

### Priority 5: Update Supporting Documentation

8. **`apps/digidoc/TESTING_GUIDE.md`**
   - Clarify that paths are expanded to absolute paths

9. **`shared_documentation/architecture/watcher_adoption_points_INITIAL.md`** and **`watcher_adoption_points_QUESTIONS.md`**
   - Add clarification that `file_path` must be absolute

---

## Notes

- The implementation plan (`file_watcher_relocation_and_storage_path_configuration_29bd9cae.plan.md`) correctly specifies the approach and can serve as a reference for updates.
- Most documentation uses `~` in path examples, which implicitly suggests path expansion, but this should be made explicit.
- API request examples show paths like `/path/to/renamed_file.pdf` which look absolute, but the documentation doesn't explicitly state this is required.

