# Path Specification Requirements

**Date**: 2025-12-24  
**Purpose**: Document path handling specifications to be integrated into MASTER_ARCHITECTURE.md restructuring  
**Source**: Based on `DOCUMENTATION_PATH_ANALYSIS.md` findings

---

## Key Requirements

### 1. Apps Use Absolute Paths Internally
- **Apps (hq, digidoc, watcher)**: All internal file operations use absolute paths
- **Rationale**: Eliminates ambiguity, ensures cross-system compatibility
- **Implementation**: After path expansion, all paths must be absolute

### 2. API Communications Require Absolute Paths
- **`file_path` parameter**: Must be absolute path in all API requests
- **Rationale**: Stateless services need explicit paths, no assumptions about working directories
- **Examples**: 
  - Watcher → DigiDoc API: `file_path` must be absolute
  - DigiDoc → Laravel API: Any file references must be absolute

### 3. Path Expansion for Cross-System Compatibility
- **Configuration paths**: Use `~` or environment variables, then expand to absolute
- **Method**: `os.path.expanduser()` or equivalent for path expansion
- **Rationale**: Supports different user accounts, deployment environments

### 4. Configuration Path Expansion
- **Paths with `~`**: Must be expanded to absolute paths before use
- **Example**: `~/digidoc_storage` → `/Users/username/digidoc_storage`
- **When**: During configuration loading, before any file operations

---

## Sections in MA.md Requiring Updates

### Priority 1: API Request/Response Examples

**Location 1**: Lines 1196-1210 (File Watcher Integration - Request Payload)
- **Current**: Shows `"file_path": "/path/to/renamed_file.pdf"` (example path)
- **Required**: Add explicit note that `file_path` must be absolute path
- **Action**: Add specification before or after example

**Location 2**: Lines 1442-1456 (Watcher API request payload - if exists)
- **Current**: Similar example path
- **Required**: Same as Location 1

### Priority 2: Configuration Sections

**Location**: Lines 733-741 (Configuration File Paths section)
- **Current**: Shows `storage_base: "~/digidoc_storage"` with `~` marker
- **Required**: Explicitly state:
  - Paths with `~` are expanded to absolute paths during configuration loading
  - Apps use absolute paths internally after expansion
- **Action**: Add specification paragraph after YAML example

### Priority 3: Integration Points Section

**Location**: Section 15 (Integration Points)
- **Current**: Describes API contracts but doesn't specify path requirements
- **Required**: Add "Path Handling" subsection specifying:
  - All `file_path` parameters in API requests must be absolute
  - Apps use absolute paths internally
  - Path expansion used for configuration
- **Action**: Add new subsection to Integration Points

### Priority 4: Shared Principles Section

**Location**: Section 1 (Core Architecture Principles)
- **Current**: Principles don't mention path handling
- **Required**: Add path handling as ecosystem-wide principle OR add to Configuration-Driven principle
- **Action**: Either new principle or expand existing principle

---

## Integration into Ecosystem Architecture Section

When creating the new "Ecosystem Architecture" section, include:

### Integration Contracts Subsection
- **Path Handling Specifications**:
  - Apps (hq, digidoc, watcher) use absolute paths internally
  - API communications require absolute paths in `file_path` parameters
  - Path expansion (e.g., `os.path.expanduser`) used for cross-system compatibility
  - Configuration paths with `~` are expanded to absolute paths during loading

---

## Verification Checklist

After restructuring, verify:
- [ ] All API request examples specify `file_path` must be absolute
- [ ] Configuration sections document path expansion requirements
- [ ] Integration Points section includes path handling specifications
- [ ] Shared Principles or Ecosystem Architecture section includes path handling as requirement
- [ ] All path-related ambiguities from DOCUMENTATION_PATH_ANALYSIS.md are resolved

---

## Notes

- These specifications align with industry best practices for multi-app ecosystems
- Path expansion ensures compatibility across different deployment environments
- Absolute paths eliminate ambiguity in stateless service architectures
- This document will be referenced during MA.md restructuring (Task 6)

