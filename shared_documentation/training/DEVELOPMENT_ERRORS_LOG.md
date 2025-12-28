# Development Errors Log

**Purpose**: Capture errors encountered during development, including context, assumptions, and corrections. Used as training material to prevent similar issues in future development cycles.

**Last Updated**: 2025-12-24

---

## How to Use This Log

When encountering an error during development:

1. **Stop and document immediately** - Don't just fix and move on
2. **Fill in the template below** with all details
3. **Add the entry chronologically** (newest at top)
4. **Tag appropriately** for easy searching

### Entry Template

```markdown
### [Error ID]: [Brief Error Description]

**Date**: YYYY-MM-DD  
**Component**: [e.g., Queue System, Preprocessing, API Server]  
**Error Type**: [ImportError, TypeError, RuntimeError, Logic Error, etc.]  
**Severity**: [Critical, High, Medium, Low]

**Error Message**:
```
[Exact error message]
```

**Context**:
- What were you trying to do?
- What code was executing?
- What environment/conditions?

**Assumption Made**:
- What did you assume that turned out to be wrong?
- Why did you make this assumption?

**Root Cause**:
- Why did this error occur?
- What was the actual behavior vs. expected?

**Correction Applied**:
- What was the fix?
- Why does this fix work?

**Prevention Strategy**:
- How can this be prevented in the future?
- What checks/documentation would have caught this?

**Related Files**:
- `path/to/file.py` (line numbers if relevant)

**Tags**: `#tag1` `#tag2` `#tag3`
```

---

## Error Entries

### ERR-003: EOFError when reading input in background worker

**Date**: 2025-12-24  
**Component**: Queue System / Task Processing  
**Error Type**: RuntimeError (EOFError)  
**Severity**: Medium

**Error Message**:
```
EOFError: EOF when reading a line
```

**Context**:
- Visual verification step in `process_receipt_task()` was calling `input()` to pause for user review
- Task was running in background RQ worker (daemon process)
- Test script was running automated end-to-end flow

**Assumption Made**:
- Assumed the RQ worker would have an interactive terminal with stdin available
- Assumed `input()` would work in any Python process context
- Didn't consider that background workers are typically non-interactive

**Root Cause**:
- Background workers (daemons, RQ workers, systemd services) don't have interactive terminals attached
- The `input()` function requires a connected stdin stream, which doesn't exist in non-interactive environments
- When `input()` is called without stdin, Python raises EOFError

**Correction Applied**:
- Added check for `sys.stdin.isatty()` before calling `input()`
- Graceful fallback: skip interactive pause in non-interactive environments
- Code now handles both interactive (development) and non-interactive (production) contexts

**Prevention Strategy**:
- Always assume background workers are non-interactive
- Check for interactive environment before using stdin/stdout operations
- Use configuration flags to control interactive behavior
- Test in both interactive and non-interactive contexts

**Related Files**:
- `apps/digidoc/ocr_service/tasks/receipt_tasks.py` (line 142)

**Tags**: `#background-workers` `#stdin` `#interactive` `#rq` `#runtime-error`

---

### ERR-002: TypeError - ImagePreprocessor() takes no arguments

**Date**: 2025-12-24  
**Component**: Image Preprocessing  
**Error Type**: TypeError  
**Severity**: High

**Error Message**:
```
TypeError: ImagePreprocessor() takes no arguments
```

**Context**:
- Code in `receipt_tasks.py` was trying to instantiate `ImagePreprocessor(config)`
- Task was being executed by RQ worker during skeleton flow testing
- Error occurred during preprocessing step of receipt processing

**Assumption Made**:
- Assumed `ImagePreprocessor` was an instance-based class that needed to be instantiated with config
- Assumed it followed a common pattern: `obj = Class(config); obj.method()`
- Didn't check the actual class definition before using it

**Root Cause**:
- `ImagePreprocessor` is a utility class with only static methods (`@staticmethod`)
- The class has no `__init__` method that accepts arguments
- Config is loaded internally via `get_config()` within the static methods
- The class was designed as a stateless utility, not an instance-based class

**Correction Applied**:
- Changed from: `preprocessor = ImagePreprocessor(config); preprocessor.preprocess(...)`
- Changed to: `ImagePreprocessor.preprocess(file_path)` (direct static method call)
- Removed unnecessary config parameter passing

**Prevention Strategy**:
- Always review class definition before using (check for `@staticmethod` or `@classmethod`)
- Look for `__init__` signature to understand instantiation requirements
- Use IDE "Go to Definition" to inspect class structure
- Document class design patterns (static vs. instance) in code comments

**Related Files**:
- `apps/digidoc/ocr_service/tasks/receipt_tasks.py` (lines 178, 310)
- `apps/digidoc/ocr_service/utils/image_preprocessing.py` (class definition)

**Tags**: `#type-error` `#class-design` `#static-methods` `#api-usage`

---

### ERR-001: ImportError - cannot import name 'Job' from 'rq'

**Date**: 2025-12-24  
**Component**: Queue System / RQ Adapter  
**Error Type**: ImportError  
**Severity**: High

**Error Message**:
```
ImportError: cannot import name 'Job' from 'rq' (/Users/.../site-packages/rq/__init__.py)
```

**Context**:
- Implementing RQ adapter for queue abstraction layer
- Code in `rq_adapter.py` was trying to import `Job` directly from `rq` package
- Error occurred when API server tried to enqueue a task

**Assumption Made**:
- Assumed `Job` was exported from the top-level `rq` package like `Queue`
- Assumed all RQ classes would be available from `from rq import ...`
- Didn't check RQ documentation or package structure before importing

**Root Cause**:
- RQ's `Job` class is in the `rq.job` submodule, not the top-level package
- The `rq` package's `__init__.py` doesn't export `Job` directly
- This is a common Python library pattern where related classes are organized into submodules
- Only `Queue` and some other classes are exported at the top level

**Correction Applied**:
- Changed from: `from rq import Queue, Job`
- Changed to: `from rq import Queue` and `from rq.job import Job, JobStatus`
- Imported from the correct submodule where `Job` actually lives

**Prevention Strategy**:
- Always check library documentation for correct import paths
- Use IDE autocomplete to see what's actually exported from a package
- When in doubt, check the package's `__init__.py` or use `dir(package)` to see exports
- Read library documentation before writing imports

**Related Files**:
- `apps/digidoc/ocr_service/queue/rq_adapter.py` (line 10)

**Tags**: `#import-error` `#library-usage` `#rq` `#package-structure`

---

## Error Statistics

**Total Errors Logged**: 3  
**By Severity**:
- Critical: 0
- High: 2
- Medium: 1
- Low: 0

**By Error Type**:
- ImportError: 1
- TypeError: 1
- RuntimeError: 1

**By Component**:
- Queue System: 2
- Image Preprocessing: 1

---

## Common Patterns & Lessons

### Pattern 1: Library Import Assumptions
**Issue**: Assuming all classes are exported from top-level package  
**Solution**: Check documentation, use IDE autocomplete, inspect package structure  
**Prevention**: Always verify import paths before using

### Pattern 2: Class Design Assumptions
**Issue**: Assuming classes follow common instantiation patterns  
**Solution**: Review class definition, check for static/class methods  
**Prevention**: Use "Go to Definition" to inspect class structure

### Pattern 3: Environment Assumptions
**Issue**: Assuming interactive environment features in non-interactive contexts  
**Solution**: Check environment capabilities before using (stdin, stdout, etc.)  
**Prevention**: Test in both interactive and non-interactive contexts

---

## Search Tags

Use these tags to find related errors:

- `#import-error` - Import-related issues
- `#type-error` - Type-related issues  
- `#runtime-error` - Runtime execution issues
- `#library-usage` - Third-party library usage issues
- `#class-design` - Class design and usage issues
- `#api-usage` - API/interface usage issues
- `#background-workers` - Issues specific to background/daemon processes
- `#stdin` - Standard input/output issues
- `#interactive` - Interactive vs. non-interactive environment issues
- `#rq` - Redis Queue specific issues
- `#queue-system` - Queue system issues
- `#preprocessing` - Image preprocessing issues

---

## Notes

- **Chronological Order**: Newest entries at top for easy access to recent issues
- **Completeness**: Each entry should be self-contained and understandable without context
- **Actionable**: Prevention strategies should be specific and implementable
- **Searchable**: Tags and component fields enable quick searching

