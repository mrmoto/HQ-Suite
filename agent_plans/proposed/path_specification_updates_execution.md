# Path Specification Updates Execution Plan

**Date**: 2025-12-24  
**Purpose**: Complete path handling specification updates across all documentation files  
**Source**: Based on `DOCUMENTATION_PATH_ANALYSIS.md` recommendations (Priorities 2-5)  
**Status**: Ready for execution

---

## Context

The ecosystem `MASTER_ARCHITECTURE.md` and `DigiDoc ARCHITECTURE.md` have been updated with explicit path handling specifications. This plan completes the remaining documentation updates to ensure consistency across all files.

**Reference Documents**:
- `shared_documentation/planning/DOCUMENTATION_PATH_ANALYSIS.md` - Analysis and recommendations
- `shared_documentation/planning/PATH_SPECIFICATION_REQUIREMENTS.md` - Requirements specification
- `shared_documentation/architecture/MASTER_ARCHITECTURE.md` - Lines 170-191 (Path Handling Specifications section) - **USE AS REFERENCE**

**Key Requirements** (from MASTER_ARCHITECTURE.md):
1. Apps use absolute paths internally
2. API `file_path` parameters must be absolute paths
3. Path expansion (`os.path.expanduser()`) used for cross-system compatibility
4. Configuration paths with `~` expanded to absolute during loading

---

## Execution Tasks

### Priority 2: API Documentation

#### Task 2.1: Update WATCHER_SPECIFICATION.md

**File**: `apps/watcher/documentation/WATCHER_SPECIFICATION.md`

**Location**: After API Request Payload example (around line 113)

**Action**: Add path specification note before or after the API request payload example

**Text to Add** (after line 125, before "API Response"):
```markdown
**Path Requirements**:
- The `file_path` parameter **MUST** be an absolute path (e.g., `/Users/username/Dropbox/Application Data/DigiDoc/queue/file.pdf`)
- Relative paths are not accepted
- Paths are expanded to absolute paths during configuration loading if `~` is used
```

**Verification**: Search for "file_path" in the file and ensure the requirement is clear.

---

#### Task 2.2: Update watcher_api_design_analysis.md

**File**: `apps/watcher/documentation/watcher_api_design_analysis.md`

**Location**: Add new section after "Migration Path" section (around line 209)

**Action**: Add a new "Path Handling Requirements" section

**Text to Add** (after line 233, before any "##" section):
```markdown
## Path Handling Requirements

**CRITICAL**: All file paths in API communications must be absolute paths.

**Requirements**:
1. **API Request `file_path` Parameter**: Must be an absolute path (e.g., `/Users/username/Dropbox/Application Data/DigiDoc/queue/file.pdf`)
2. **Path Expansion**: Configuration paths using `~` or environment variables are expanded to absolute paths using `os.path.expanduser()` or equivalent
3. **Internal Operations**: All apps (Watcher, DigiDoc) use absolute paths internally after expansion

**Rationale**:
- Stateless services need explicit paths (no assumptions about working directories)
- Cross-system compatibility (different user accounts, deployment environments)
- Eliminates ambiguity in file location

**Examples**:
- ✅ Correct: `"file_path": "/Users/username/Dropbox/Application Data/DigiDoc/queue/file.pdf"`
- ❌ Incorrect: `"file_path": "queue/file.pdf"` (relative path)

**Reference**: See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" section for ecosystem-wide requirements.
```

**Verification**: Ensure the new section is properly formatted and cross-references MASTER_ARCHITECTURE.md.

---

### Priority 3: App Documentation

#### Task 3.1: Update file_watcher_service/README.md

**File**: `apps/digidoc/file_watcher_service/README.md`

**Location**: In the "Data Flow" section (around line 91-97)

**Action**: Update the data flow description to specify absolute paths

**Current Text** (around line 91):
```
1. Scanner saves file to queue directory: `queue/<filename>.png`
```

**Replace With**:
```
1. Scanner saves file to queue directory: `~/Dropbox/Application Data/DigiDoc/queue/<filename>.png` (expanded to absolute path)
```

**Additional Action**: Add path specification note after the "Data Flow" section (after line 97)

**Text to Add** (after line 97):
```markdown
**Path Requirements**:
- The file watcher passes **absolute file paths** to the DigiDoc API
- Configuration paths using `~` (e.g., `~/Dropbox/Application Data/DigiDoc/queue/`) are expanded to absolute paths during configuration loading
- All internal file operations use absolute paths after expansion
- See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" for ecosystem-wide requirements
```

**Verification**: Check that both the data flow and the new note specify absolute paths.

---

#### Task 3.2: Update DigiDoc README.md

**File**: `apps/digidoc/README.md`

**Location**: After "Configuration" section (around line 42) or in "Data Flow" section (around line 53)

**Action**: Add path specification note

**Text to Add** (after line 42, before "File Watcher Service" section):
```markdown
**Path Requirements**:
- All file paths in API calls **MUST** be absolute paths (e.g., `/Users/username/Dropbox/Application Data/DigiDoc/queue/file.pdf`)
- Configuration paths using `~` (e.g., `~/Dropbox/Application Data/DigiDoc/queue/`) are expanded to absolute paths during configuration loading
- Relative paths are not accepted in API requests
- See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" for ecosystem-wide requirements
```

**Verification**: Ensure the note is clear and cross-references MASTER_ARCHITECTURE.md.

---

### Priority 4: Training & Best Practices

#### Task 4.1: Update AGENT_TRAINING_GUIDE.md

**File**: `shared_documentation/training/AGENT_TRAINING_GUIDE.md`

**Location**: In the "Critical Architecture Documents" section, after the DigiDoc ARCHITECTURE.md description (around line 128-150)

**Action**: Add a new subsection "Path Handling Requirements" or add to an existing relevant section

**Option A**: Add as new subsection after "1a. DigiDoc ARCHITECTURE.md" (around line 150)

**Text to Add**:
```markdown
### Path Handling Requirements

**CRITICAL**: All apps in the Construction Suite ecosystem use absolute paths for file operations and API communications.

**Key Requirements**:
1. **Apps Use Absolute Paths Internally**: All apps (hq, digidoc, watcher) use absolute paths for internal file operations
2. **API Communications Require Absolute Paths**: The `file_path` parameter in all API requests must be an absolute path
3. **Path Expansion**: Configuration paths using `~` or environment variables are expanded to absolute paths using `os.path.expanduser()` or equivalent
4. **Configuration Loading**: Paths with `~` in configuration files are expanded to absolute paths during configuration loading, before any file operations

**Rationale**:
- Stateless services need explicit paths (no assumptions about working directories)
- Cross-system compatibility (different user accounts, deployment environments)
- Eliminates ambiguity in file location

**Examples**:
- ✅ Correct: `"file_path": "/Users/username/Dropbox/Application Data/DigiDoc/queue/file.pdf"`
- ❌ Incorrect: `"file_path": "queue/file.pdf"` (relative path)
- ✅ Correct: Configuration `storage_base: "~/digidoc_storage"` → expanded to `/Users/username/digidoc_storage`

**Reference**: See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" section for complete requirements.
```

**Verification**: Ensure the section is properly placed and formatted.

---

#### Task 4.2: Update DEVELOPMENT_BEST_PRACTICES.md

**File**: `development/DEVELOPMENT_BEST_PRACTICES.md`

**Location**: In the "Configuration Loading" section (around line 442-450)

**Action**: Expand the path expansion note to be more explicit

**Current Text** (around line 448):
```
4. Expand paths (e.g., `~/Dropbox/...`)
```

**Replace With**:
```
4. Expand paths to absolute paths (e.g., `~/Dropbox/...` → `/Users/username/Dropbox/...`)
   - Use `os.path.expanduser()` or equivalent
   - All apps use absolute paths internally after expansion
   - Required for cross-system compatibility
```

**Additional Action**: Add a new subsection "Path Handling" in the Configuration section (after line 450)

**Text to Add** (after line 450):
```markdown
### Path Handling

**CRITICAL**: Path expansion is required for cross-system compatibility.

**Requirements**:
- Configuration paths with `~` must be expanded to absolute paths during configuration loading
- All apps use absolute paths internally after expansion
- API `file_path` parameters must be absolute paths
- Path expansion ensures compatibility across different user accounts and deployment environments

**Implementation**:
- Use `os.path.expanduser()` for `~` expansion
- Expand paths before any file operations
- Never use relative paths in API communications

**Reference**: See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" for ecosystem-wide requirements.
```

**Verification**: Ensure both the inline update and new subsection are clear.

---

### Priority 5: Supporting Documentation

#### Task 5.1: Update TESTING_GUIDE.md

**File**: `apps/digidoc/TESTING_GUIDE.md`

**Location**: In the "Configuration" section (around line 97-100)

**Action**: Add clarification about path expansion

**Current Text** (around line 99):
```
- [ ] Paths are correctly expanded
```

**Replace With** (or add note after):
```
- [ ] Paths are correctly expanded to absolute paths (e.g., `~/Dropbox/...` → `/Users/username/Dropbox/...`)
- [ ] All file operations use absolute paths after expansion
```

**Additional Action**: Add a note in the "Configuration" section (after line 100)

**Text to Add** (after line 100):
```markdown
**Note**: Configuration paths using `~` are expanded to absolute paths during configuration loading. All apps use absolute paths internally after expansion. See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" for requirements.
```

**Verification**: Ensure the clarification is clear and consistent.

---

#### Task 5.2: Update watcher_adoption_points_INITIAL.md

**File**: `shared_documentation/architecture/watcher_adoption_points_INITIAL.md`

**Location**: In any section that mentions `file_path` or API requests (likely around line 42+ in API-related questions)

**Action**: Add clarification about absolute path requirement

**Search For**: Any mention of `file_path` or API request examples

**Text to Add** (after the first mention of `file_path` in API context, or create new note section):
```markdown
**Path Requirement**: The `file_path` parameter in API requests **MUST** be an absolute path. See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" for ecosystem-wide requirements.
```

**Verification**: Ensure the note is placed where it's most relevant (likely in API-related questions).

---

#### Task 5.3: Update watcher_adoption_points_QUESTIONS.md

**File**: `shared_documentation/architecture/watcher_adoption_points_QUESTIONS.md`

**Location**: In any section that mentions `file_path` or API requests

**Action**: Add clarification about absolute path requirement (same as Task 5.2)

**Search For**: Any mention of `file_path` or API request examples

**Text to Add** (after the first mention of `file_path` in API context):
```markdown
**Path Requirement**: The `file_path` parameter in API requests **MUST** be an absolute path. See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" for ecosystem-wide requirements.
```

**Verification**: Ensure the note is placed where it's most relevant.

---

## Verification Checklist

After completing all tasks, verify:

- [ ] All API documentation files specify `file_path` must be absolute
- [ ] All app documentation files mention absolute path requirements
- [ ] Training guides include path handling specifications
- [ ] Best practices docs clarify path expansion requirements
- [ ] Supporting documentation mentions absolute paths where relevant
- [ ] All files cross-reference `MASTER_ARCHITECTURE.md` "Path Handling Specifications" where appropriate
- [ ] No relative path examples remain in API documentation
- [ ] Path expansion is explicitly documented in configuration sections

---

## Notes

- **Consistency**: Use the exact wording from `MASTER_ARCHITECTURE.md` "Path Handling Specifications" section (lines 170-191) as the reference
- **Cross-References**: Always include a reference to `MASTER_ARCHITECTURE.md` "Path Handling Specifications" section when adding new path requirements
- **Examples**: Use the same example format as in `MASTER_ARCHITECTURE.md` (✅ Correct / ❌ Incorrect)
- **Priority Order**: Execute tasks in priority order (2 → 3 → 4 → 5) for logical progression

---

## Completion Criteria

This plan is complete when:
1. All 9 files have been updated with path specifications
2. All verification checklist items are checked
3. All cross-references to `MASTER_ARCHITECTURE.md` are working
4. No relative path examples remain in API documentation
5. Path expansion is explicitly documented in all relevant sections

---

**Status**: Ready for execution  
**Estimated Time**: 30-45 minutes  
**Dependencies**: None (all reference documents exist)

