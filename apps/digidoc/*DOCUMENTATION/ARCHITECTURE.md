# DigiDoc Architecture

**Version:** 1.0  
**Last Updated:** 2025-12-24  
**Status:** Development Phase

**Note**: This document describes DigiDoc-specific architecture and implementation details. For ecosystem context, app relationships, and integration contracts, see [Construction Suite Ecosystem Architecture](../../../shared_documentation/architecture/MASTER_ARCHITECTURE.md).

## Table of Contents

1. [Ecosystem Context](#ecosystem-context)
2. [System Overview](#system-overview)
3. [Offline-First Architecture](#offline-first-architecture)
4. [Queue Abstraction Layer](#queue-abstraction-layer)
5. [Preprocessing Pipeline](#preprocessing-pipeline)
6. [Template Matching System](#template-matching-system)
7. [Extraction Pipeline](#extraction-pipeline)
8. [Review Queue & GUI](#review-queue--gui)
9. [File Storage Architecture](#file-storage-architecture)
10. [Configuration Management](#configuration-management)
11. [Workflow Implementation](#workflow-implementation)
12. [Risk Mitigations](#risk-mitigations)
13. [Unknown Unknowns](#unknown-unknowns)
14. [Module Structure](#module-structure)
15. [Integration Implementation](#integration-implementation)
16. [Future Requirements](#future-requirements)

---

## Ecosystem Context

DigiDoc is part of the Construction Suite ecosystem. For ecosystem architecture, app relationships, and integration contracts, see [Construction Suite Ecosystem Architecture](../../../shared_documentation/architecture/MASTER_ARCHITECTURE.md).

**DigiDoc's Role**:
- OCR processing service
- Closely coupled with Watcher (file ingestion) and HQ (data storage)
- Provides API endpoints for file processing
- Operates offline-first with local processing

**Integration Points**:
- Receives files from Watcher via HTTP API (`POST /api/digidoc/queue`)
- Sends extracted data to HQ via HTTP API (`POST /api/digidoc/process-complete`)
- Syncs templates with HQ (pull/push via API)

---

## System Overview

### High-Level Workflow

```
Input (Raster Image: PDF/JPG/PNG/TIFF)
    ↓
[File Watcher - OS Level, Separate Service]
    ├─ Atomic Rename (ALWAYS - 100% uptime)
    ├─ Stabilization Delay (2 seconds configurable)
    └─ Priority-Based Host Selection
    ↓
Enqueue to DigiDoc (RQ Job) [if auto/both configured]
    ↓
Preprocessing Pipeline
    ├─ Deskew
    ├─ Denoise
    ├─ Binarize
    ├─ Scale Normalization
    ├─ Border Removal
    └─ Generate Comparison Images (for GUI)
    ↓
Template Matching
    ├─ Structural Fingerprint (Primary: 70%)
    ├─ Feature Detection (Secondary: 20%)
    └─ Text Fallback (Tertiary: 10%)
    ↓
Confidence Check
    ├─ ≥85%: Auto-process
    └─ <85%: Route to Review Queue
    ↓
Extraction (if matched)
    ├─ Zonal OCR
    ├─ Contour-Based Extraction
    └─ LLM Confirmation (if needed)
    ↓
Output
    ├─ JSON to Laravel API
    └─ Rename/Archive File
```

### Queue Item Status Flow

```
pending → preprocessing → matching → extracting → review → completed
                                                          ↓
                                                       failed
```

**Status Definitions:**
- `pending`: Queued, awaiting processing
- `preprocessing`: Image preprocessing in progress
- `matching`: Template matching in progress
- `extracting`: Field extraction in progress
- `review`: In human review queue
- `completed`: Successfully processed and sent to Laravel
- `failed`: Processing failed, requires attention

---

## Offline-First Architecture

### Local Processing Requirements

**MVP Scope:**
- All sessions, training, model evaluations on local machine only
- Cloud sync operations addressed post-MVP
- No external service dependencies

**Local Components:**
- Tesseract OCR (local installation)
- Ollama LLM (local installation)
- SQLite database (local file)
- Redis queue (local instance)
- Template cache (local SQLite)
- File storage (local filesystem)

**Cloud Mirroring (Post-MVP):**
- Must utilize Container (i.e. Docker) for deployment
- Architecture must support cloud mirroring without code changes
- Template sync between local and cloud
- Queue synchronization
- Model file synchronization

---

## Queue Abstraction Layer

**Status**: Implemented (2025-12-19)

### Architecture

**Purpose**: Allow immediate use of RQ for MVP, seamless switch to Celery for production without code refactoring.

### Implementation Structure

```
digidoc/
├── queue/
│   ├── __init__.py              # Public API: enqueue_ocr_task()
│   ├── queue_adapter.py         # Abstract base class + factory
│   ├── rq_adapter.py            # RQ implementation (MVP)
│   └── celery_adapter.py        # Celery implementation (future)
└── tasks/
    ├── __init__.py
    └── receipt_tasks.py          # Queue-agnostic task functions
```

### Queue Adapter Interface

```python
class QueueAdapter(ABC):
    @abstractmethod
    def enqueue(self, task_name: str, *args, **kwargs) -> TaskResult:
        """Enqueue a task for processing."""
        pass
    
    @abstractmethod
    def enqueue_delayed(self, task_name: str, delay_seconds: int, *args, **kwargs) -> TaskResult:
        """Enqueue a task with delay."""
        pass
    
    @abstractmethod
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a task."""
        pass
```

### Factory Function

```python
def get_queue_adapter() -> QueueAdapter:
    """Get configured queue adapter based on QUEUE_ADAPTER env var."""
    adapter_type = os.getenv('QUEUE_ADAPTER', 'rq').lower()
    
    if adapter_type == 'rq':
        return RQAdapter()
    elif adapter_type == 'celery':
        return CeleryAdapter()
    else:
        raise ValueError(f"Unknown queue adapter: {adapter_type}")
```

### Configuration

**Environment Variable:**
- `QUEUE_ADAPTER`: `rq` (MVP) or `celery` (production)
- `REDIS_URL`: Redis connection string

**Migration Path:**
1. MVP: Use RQ (`QUEUE_ADAPTER=rq`)
2. Production: Switch to Celery (`QUEUE_ADAPTER=celery`)
3. Zero code changes required - only environment variable

### Task Functions (Queue-Agnostic)

All task functions are pure Python functions with no queue-specific code:

```python
def process_receipt_task(file_path: str, queue_item_id: str, calling_app_id: str) -> Dict[str, Any]:
    """Process receipt - works with RQ or Celery."""
    # Pure Python logic - no queue dependencies
    pass
```

---

## Preprocessing Pipeline

**Status**: Implemented (2025-12-19)

### Pipeline Steps

1. **Deskew** (Rotation Correction)
   - Method: OpenCV HoughLinesP + rotation
   - Detects text line angles
   - Rotates image to correct orientation
   - Output: Deskewed image
   
   **Implementation Notes**: HoughLinesP was chosen over minAreaRect because it better detects text line angles in documents. minAreaRect works well for geometric shapes but is less accurate for text-based documents. HoughLinesP aligns with 2025 OCR best practices for document preprocessing.

2. **Denoise**
   - Method: OpenCV fastNlMeansDenoising
   - Removes scanner noise
   - Preserves text edges
   - Output: Denoised image

3. **Binarize**
   - Method: Adaptive threshold (Otsu or Gaussian)
   - Converts to black/white for better text contrast
   - Handles variable lighting
   - Output: Binary image

4. **Scale Normalization**
   - Target: 300 DPI standard
   - Method: Cubic interpolation
   - Maintains aspect ratio
   - Output: Normalized image

5. **Border Removal**
   - Method: Contour analysis
   - Detects white borders
   - Crops to content area
   - Output: Cropped image

### Risk Mitigations

#### Handwriting Detection
- **Detection**: High variance in line thickness via contour irregularity
- **Fallback**: LLM-only extraction (Ollama vision model)
- **Threshold**: 75% accuracy (2025 Journal of Document Analysis benchmark)
- **Rationale**: LLM beats Tesseract on handwriting by 25-35%

#### Color Logo Processing
- **Method**: Process in color first (no grayscale conversion)
- **Technique**: HSV color space to extract logos before binarization
- **Process**: Extract logos in color, then grayscale the rest for text
- **Implementation**: OpenCV cv2.cvtColor + color filtering

### GUI Integration

**Preprocessing Output:**
- Save preprocessed image as temporary file
- Store in queue item directory: `{queue_item_id}/preprocessed.png`
- Generate comparison image: original vs preprocessed side-by-side
- Display in Streamlit GUI with:
  - Original image (left)
  - Preprocessed image (right)
  - Proportionally scaled for equal display
  - Overlaid corrections (skew lines, color filters)

**Human Review:**
- "View Preprocess Output" button in review queue
- Side-by-side comparison view
- Manual adjustment options:
  - Re-run preprocessing with different parameters
  - Adjust denoising level
  - Adjust binarization threshold
  - Manual deskew correction

**Why**: Variable DPI/skew are #1 OCR killers (2025 PaddleOCR benchmarks: preprocessing improves accuracy 25-40%). GUI allows human to inspect if denoising removed critical details.

---

## Template Matching System

**Status**: Implemented (2025-12-19)

### Three-Tier Matching Approach

#### Primary: Structural Fingerprint (70% weight)
- **Method**: Image-first, DPI/scale invariant
- **Steps**:
  1. Detect contours (OpenCV findContours)
  2. Extract zones (bounding boxes for header, tables, footer, logos)
  3. Compute structural hash (position + size ratios of zones)
  4. Compare to stored template fingerprints (Euclidean distance or SSIM)
- **Handles**: Scale, rotation (minor), DPI differences
- **Output**: Structural match score (0.0-1.0)

**Implementation Notes**: Ratio-based fingerprints (not absolute pixels) ensure DPI/scale invariance. This is essential for handling documents from different scanners with varying resolutions. Absolute pixel-based matching would fail when the same document is scanned at 200 DPI vs 300 DPI. Ratio-based approach makes the system robust across variable scanner resolutions.

#### Secondary: Feature Detection (20% weight)
- **Method**: ORB keypoints on logo regions
- **Steps**:
  1. Extract ORB features from logo area
  2. Match to template logos (FLANN matcher)
  3. Calculate match ratio
- **Handles**: Partial occlusions, lighting variations
- **GUI Integration**: Show keypoint matches (lines connecting receipt logo to template logo) for visual inspection
- **Output**: Feature match score (0.0-1.0)

#### Tertiary: Text Fallback (10% weight)
- **Method**: Tesseract/PaddleOCR on header
- **Steps**:
  1. OCR header section
  2. Search for vendor name/patterns
  3. Calculate text match score
- **Handles**: When layout fails (rare)
- **GUI Integration**: Highlight matched text in image preview
- **Output**: Text match score (0.0-1.0)

### Matching Logic

**Score Calculation:**
```
Final Score = (0.7 × structural) + (0.2 × feature) + (0.1 × text)
```

**Decision Thresholds** (configurable):
- `>0.85`: Auto-match → proceed to extraction
- `0.60-0.85`: Partial match → review queue with tiered suggestions
- `<0.60`: No match → review queue with tiered suggestions

### Template Drift Mitigation

**Risk**: Vendors change formats over time

**Mitigation Strategy:**
1. On partial match (score 0.60-0.85):
   - Auto-add as "variant template" to database
   - Flag with 80% similarity to original
   - Trigger GUI review to confirm/approve as new template
2. GUI Integration:
   - "Approve as new variant" button
   - "Create new template" option
   - Visual comparison: original template vs variant
3. **Result**: Template library evolves dynamically, avoiding drift

### Template Storage

**Primary Storage**: Calling application (Laravel)
- Templates stored in calling app database
- DigiDoc pulls templates via API sync

**Local Cache**: SQLite database
- Cached templates for offline operation
- Cache TTL: configurable (default 24 hours)
- Cache invalidation: on template update from calling app

**Template Structure:**
```json
{
  "template_id": "uuid",
  "calling_app_id": "string",
  "document_type": "receipt",
  "vendor": "Mead Clark Lumber",
  "format_name": "mead_clark_format1",
  "structural_fingerprint": {
    "zones": [...],
    "ratios": {...}
  },
  "logo_features": [...],
  "field_mappings": {...}
}
```

---

## Extraction Pipeline

**Status**: Planned

### Extraction Methods

#### 1. Zonal OCR
- **Method**: Use template zones to extract specific fields
- **Process**:
  1. Load matched template
  2. Extract zones (header, tables, footer)
  3. Run OCR on each zone
  4. Map text to fields using template field mappings
- **Output**: Structured field data

#### 2. Contour-Based Extraction
- **Method**: OpenCV contour detection after matching
- **Process**:
  1. Detect table rows/columns using contours
  2. Extract text within bounding boxes
  3. Use PaddleOCR table engine for structured data
  4. Group related fields
- **Output**: Table-structured data (line items)

#### 3. LLM Confirmation
- **Method**: Ollama vision model on matched zones
- **Process**:
  1. Extract zone image
  2. Send to Ollama: "extract total amount from this box image"
  3. Parse LLM response
  4. Validate against OCR result
- **Use Case**: Handwriting, low OCR confidence, ambiguous fields
- **Output**: LLM-extracted field values

### Line Items Extraction

**Table Detection:**
- Method: PaddleOCR table engine or OpenCV contour grouping
- Process:
  1. Detect table structure
  2. Identify rows and columns
  3. Extract cell content
  4. Map to line item fields (description, quantity, price, etc.)

**Line Item Fields:**
- Line number
- Description
- Quantity
- UOM (unit of measure)
- Unit price
- Line total
- Taxable amount
- CSI code (if available)

### Risk Mitigations

#### Handwriting
- **Detection**: Low OCR confidence (<70%)
- **Fallback**: Route to LLM vision model (Ollama)
- **If Still Low**: GUI review with manual entry option
- **GUI Integration**: Handwriting zoom view, manual entry form

#### Multi-Page Documents
- **Detection**: Process page 1 for matching
- **If Match**: Extract from all pages sequentially
- **For Unknown Multi-Page**: Tiered approach suggests:
  - "Split and process pages separately"
  - "Extract text only"
- **GUI Integration**: Page thumbnails for selection, page-by-page processing

---

## Review Queue & GUI

**Status**: Implemented (2025-12-19)

### Streamlit GUI Architecture

**Stack**: Streamlit (web-based, encapsulated in DigiDoc)
- GUI stack independent from OCR Python logic
- All GUI elements web-based
- No authentication for MVP (provisions for future integration)

#### Implementation Notes

**Why Streamlit over Flask/Laravel**:
- Rapid development for visual inspection and verification
- Encapsulated within DigiDoc (no separate GUI application needed)
- Web-based for easy access during development
- Sufficient for MVP development verification needs
- Allows quick iteration on preprocessing and matching visualization
- Can be replaced with more robust solution post-MVP if needed

### GUI Components

#### 1. Review Queue Dashboard
- **Page**: Queue list view
- **Features**:
  - List of queue items with:
    - File name
    - Confidence score
    - Status
    - Thumbnail
    - Created timestamp
  - Filtering: by status, confidence level, date
  - Sorting: by date, confidence, status
  - Search: by filename, vendor

#### 2. Preprocessing Review
- **Page**: Preprocessing output viewer
- **Features**:
  - Side-by-side comparison:
    - Original image (left)
    - Preprocessed image (right)
    - Proportionally scaled for equal display
  - Overlay visualizations:
    - Skew correction lines
    - Color filter regions
    - Denoising areas
  - Manual adjustment controls:
    - Re-run preprocessing
    - Adjust parameters
    - Manual corrections

#### 3. Template Matching Review
- **Page**: Template match visualization
- **Features**:
  - Keypoint matches visualization (lines connecting receipt to template)
  - Structural zone overlays
  - Match score breakdown
  - Template comparison view

#### 4. Extraction Review
- **Page**: Extracted fields editor
- **Features**:
  - Contour-overlaid image
  - Extracted fields displayed next to image
  - Editable fields (click to edit)
  - Re-run OCR on zone button
  - Add notes capability
  - Save revisions back to JSON

#### 5. Tiered Suggestions Interface
- **Page**: Non-match handling
- **Features**:
  - List of suggested actions:
    1. Manual entry (enter fields yourself)
    2. New template (upload as new vendor/format)
    3. Partial match (extract text only without template)
    4. Skip and archive
  - User selects option
  - System processes accordingly

### GUI File Organization

**Queue Item Directory Structure:**
```
{queue_item_id}/
├── original.{ext}              # Original source file
├── preprocessed.png            # Preprocessed image
├── comparison.png              # Side-by-side comparison
├── template_match.png          # Template match visualization
├── extraction_overlay.png      # Contour overlay
├── extracted_fields.json       # Extracted data
├── ocr_text.txt               # Raw OCR text
└── audit_log.json             # Processing audit trail
```

### Authentication (Post-MVP)

**MVP**: No authentication required

**Future Integration**:
- API call provides context for environment
- User authenticated at API call
- JWT token passed to DigiDoc
- Streamlit validates token (or calls Laravel API to verify)
- User context available throughout processing

---

## File Storage Architecture

### Storage Organization

**Base Directory**: Configurable (default: `~/digidoc_storage/`)

**Note**: Configuration paths with `~` are expanded to absolute paths during configuration loading. All file operations use absolute paths internally.

**Directory Structure:**
```
digidoc_storage/
├── queue/                      # Active processing queue
│   └── {queue_item_id}/       # Per-item directory
│       ├── original.{ext}
│       ├── preprocessed.png
│       ├── comparison.png
│       ├── extracted_fields.json
│       └── audit_log.json
├── processed/                  # Successfully processed
│   └── {vendor}_{date}_{total}.{ext}
├── failed/                     # Failed processing
│   └── {queue_item_id}_{error}.{ext}
├── templates/                  # Template cache
│   └── {template_id}/
│       ├── fingerprint.json
│       └── logo_features.bin
├── models/                     # ML models (post-MVP)
└── logs/                       # Application logs
```

### File Organization by Queue Item ID

**Principle**: All files related to a queue item stored in `{queue_item_id}/` directory

**Benefits**:
- Easy cleanup
- Crash recovery (resume from queue item directory)
- Audit trail per item
- Soft error handling (continue where left off)

### File Types

1. **Source Files**
   - Original uploaded files (PDF/JPG/PNG/TIFF - all raster formats supported)
   - Moved to different directory in same parent folder
   - Renamed when moved (format: `{vendor}_{YYYYMMDD}_{total}.{ext}`)

2. **Preprocessed Images**
   - Temporary files for GUI review
   - Stored in queue item directory
   - Retention policy: post-MVP

3. **Template Files**
   - Model files for form matching
   - Stored in calling app (primary)
   - Cached locally in DigiDoc
   - New templates created in DigiDoc, pushed to calling app
   - Error handling if calling app cannot store/receive

4. **Extracted Data**
   - JSON results
   - Stored in queue item directory
   - Sent to Laravel API

5. **Audit Logs**
   - Processing steps
   - Errors
   - Human review actions
   - Stored in queue item directory

6. **LLM Cache**
   - Ollama processing cache
   - Stored in queue item directory
   - Retention policy: post-MVP

### Retention Policy

**MVP**: No automatic cleanup (manual cleanup)

**Post-MVP**:
- Configurable retention periods
- Automatic cleanup of old files
- Archive strategy for long-term storage

---

## Configuration Management

**Status**: Implemented (2025-12-19)

### Configuration File Structure

**File**: `digidoc_config.yaml` (or `.json`, `.toml`)

#### Implementation Notes

**Why YAML over JSON**:
- Human-readable and easily editable
- Supports comments for documentation
- Better suited for configuration files (vs. JSON for data exchange)
- Minor performance difference acceptable for config file loading
- Aligns with industry best practices for configuration management

**Location**: DigiDoc root (`/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/apps/digidoc/`) or configurable via `DIGIDOC_CONFIG_PATH` environment variable

### Configuration Sections

#### 1. Thresholds
```yaml
thresholds:
  auto_match: 0.85          # Auto-process if confidence ≥ this
  partial_match_min: 0.60   # Partial match range
  partial_match_max: 0.85
  ocr_confidence_min: 0.70  # Minimum OCR confidence before LLM fallback
  llm_accuracy_min: 0.75     # Minimum LLM accuracy for handwriting
```

#### 2. Scoring Weights
```yaml
scoring:
  structural_weight: 0.70   # Structural fingerprint weight
  feature_weight: 0.20       # Feature detection weight
  text_weight: 0.10          # Text fallback weight
  ocr_quality_weight: 0.30
  field_extraction_weight: 0.40
  pattern_matching_weight: 0.20
  data_validation_weight: 0.10
```

#### 3. Preprocessing
```yaml
preprocessing:
  target_dpi: 300
  denoise_level: "medium"
  binarization_method: "otsu"  # or "gaussian"
  deskew_enabled: true
  border_removal_enabled: true
```

#### 4. File Paths

**Path Expansion**: All paths with `~` are expanded to absolute paths during configuration loading using `os.path.expanduser()` or equivalent. All file operations use absolute paths internally.

```yaml
paths:
  storage_base: "~/digidoc_storage"  # Expanded to absolute path
  queue_directory: "{storage_base}/queue"
  processed_directory: "{storage_base}/processed"
  failed_directory: "{storage_base}/failed"
  templates_directory: "{storage_base}/templates"
```

#### 5. API Endpoints
```yaml
api:
  laravel_base_url: "http://127.0.0.1:8000"
  laravel_complete_endpoint: "/api/digidoc/process-complete"
  template_sync_endpoint: "/api/digidoc/templates/sync"
```

#### 6. Queue Configuration
```yaml
queue:
  adapter: "rq"  # or "celery"
  redis_url: "redis://localhost:6379/0"
  max_retries: 3
  job_timeout: 300  # seconds
```

#### 7. Database
```yaml
database:
  type: "sqlite"
  path: "{storage_base}/digidoc.db"
```

#### 8. LLM (Ollama)
```yaml
llm:
  ollama_url: "http://localhost:11434"
  model: "llama-vision"
  timeout: 60
```

### Environment Variables Override

All configuration values can be overridden by environment variables:
- `DIGIDOC_CONFIG_PATH`: Path to config file
- `DIGIDOC_AUTO_MATCH_THRESHOLD`: Override auto_match threshold
- `DIGIDOC_QUEUE_ADAPTER`: Override queue adapter
- etc.

---

## Workflow Implementation

### Granular Steps

#### 1. File Detection (OS Level - Separate Service)
**Status**: Planned (Post DigiDoc MVP)

- **Service**: File watcher (100% silo separation, completely independent)
- **Function**: Watch directory with complex logic:
  - **Event-driven monitoring**: FSEvents (macOS) / inotify (cloud) - no polling
  - **Stabilization delay**: Wait for file to be closed and stable (configurable, default 2 seconds)
  - **Atomic renaming**: **ALWAYS** performed (100% uptime guarantee)
    - Pattern: `{timestamp}_{random8}.{ext}`
    - Prevents partial-file processing
    - Handles rename collisions (append incrementing suffix)
  - **File locking**: If file in use, wait and retry (max 30 seconds)
  - **Ghosted file detection**: Prevents processing incomplete files
  - **Multiple simultaneous write handling**: Atomic operations prevent conflicts
- **Output**: After successful rename, calls DigiDoc API with renamed file path (absolute path required)

#### 2. Enqueue
- **Trigger**: File detected by watcher
- **Action**: Create RQ job with:
  - File path (absolute)
  - Metadata (source folder, timestamp)
  - Calling app ID (required)
  - Context (environment, user - post-MVP)
- **Queue**: Redis queue (via queue abstraction layer)

#### 3. Preprocess
- **Task**: OpenCV pipeline
- **Steps**:
  1. Deskew
  2. Denoise
  3. Binarize
  4. Scale normalization
  5. Border removal
- **Output**: Preprocessed image saved to `{queue_item_id}/preprocessed.png`
- **Status Update**: `preprocessing` → `matching`

#### 4. Fingerprint
- **Task**: Structural + feature hash computation
- **Steps**:
  1. Detect contours
  2. Extract zones
  3. Compute structural hash
  4. Extract ORB features
  5. Compare to template DB (SQLite)
- **Output**: Match scores for all templates
- **Status Update**: `matching` → `extracting` (if match) or `review` (if no match)

#### 5. Match Decision
- **Input**: Match scores
- **Logic**:
  - If score >0.85: Auto-match → proceed to extraction
  - If score 0.60-0.85: Partial match → review queue with suggestions
  - If score <0.60: No match → review queue with suggestions
- **Output**: Best match template (if any) or tiered suggestions

#### 6. Extraction (if matched)
- **Task**: Zonal OCR + contour extraction + LLM confirmation
- **Steps**:
  1. Load matched template
  2. Extract zones
  3. Run OCR on zones
  4. Detect contours for tables
  5. Extract line items
  6. LLM confirmation (if needed)
- **Output**: Extracted fields JSON
- **Status Update**: `extracting` → `review` (if confidence <85%) or `completed` (if ≥85%)

#### 7. Confidence Check
- **Input**: Extracted fields + confidence scores
- **Logic**:
  - Calculate overall confidence
  - If ≥85%: Auto-process
  - If <85%: Route to review queue
- **Output**: Processing decision

#### 8. Auto-Process (if high confidence)
- **Action**: POST JSON to Laravel API
- **Endpoint**: Configurable (default: `/api/digidoc/process-complete`)
- **Payload**:
  ```json
  {
    "queue_item_id": "uuid",
    "calling_app_id": "string",
    "extracted_fields": {...},
    "confidence": 0.92,
    "template_matched": "mead_clark_format1"
  }
  ```
- **Status Update**: `completed`

#### 9. Review Queue (if low confidence)
- **Action**: Enqueue to review queue
- **Notification**: Post-MVP (email/Slack)
- **GUI**: Streamlit dashboard shows item
- **Status Update**: `review`

#### 10. Archive File
- **Action**: Rename and move processed file
- **Format**: `{vendor}_{YYYYMMDD}_{total}.{ext}`
- **Location**: `processed/` directory
- **Cleanup**: Remove queue item directory (post-MVP retention policy)

#### 11. Audit Logging
- **Action**: Log every step
- **Content**:
  - Step name
  - Success/failure
  - Confidence scores
  - Human review actions (if any)
  - Timestamps
- **Location**: `{queue_item_id}/audit_log.json`

### Error Handling

**Try/Except on Each Step:**
- Log error to audit log
- Update queue item status to `failed`
- Store error message
- Queue for review (if recoverable)
- Continue processing other items

**Crash Recovery:**
- On restart, scan queue directories
- Resume from last completed step
- Use audit log to determine state
- Retry failed steps

---

## Risk Mitigations

### 1. Multi-Page Documents

**Risk**: Absolute (will happen with RFPs, contracts, etc.)

**Mitigation**:
- Page-by-page processing in workflow
- Process page 1 for matching
- If match: extract from all pages sequentially
- GUI thumbnail selector for manual page choice
- Tiered suggestion: "This is a multi-page document — process all pages or select specific?"

**Implementation**:
- PDF page extraction
- Per-page preprocessing
- Per-page matching
- Aggregate extraction results

### 2. Handwriting

**Risk**: Absolute (receipts have notes, signatures, etc.)

**Mitigation**:
- **Detection**: High variance in line thickness via contour irregularity
- **Fallback**: LLM vision model (Ollama) for handwriting recognition
- **Threshold**: 75% accuracy (2025 Journal of Document Analysis benchmark)
- **GUI**: Manual entry with handwriting zoom
- **Tiered Suggestion**: "Handwriting detected — manual entry recommended?"

**Implementation**:
- Contour analysis for handwriting detection
- Route to Ollama if detected
- GUI manual entry form
- Save corrections to JSON

### 3. Color Logos

**Risk**: Absolute (logos on receipts are often color)

**Mitigation**:
- Color preprocessing in step 2
- Process in color first (no grayscale conversion)
- HSV color space to extract logos before binarization
- GUI color preview + manual match
- **Tiered Suggestion**: "Color logo not matched — upload as new template?"

**Implementation**:
- HSV color filtering
- Logo region extraction
- Template logo matching
- GUI color preview

### 4. Template Drift

**Risk**: Absolute (vendors change formats over time)

**Mitigation**:
- Auto-variant addition in matching
- On partial match (0.60-0.85): auto-add as variant with 80% similarity flag
- GUI "approve as new variant" button
- **Tiered Suggestion**: "Partial match detected — create new template or ignore?"

**Implementation**:
- Variant detection in template matcher
- Database flag for variants
- GUI approval workflow
- Template versioning

### 5. Scalability

**Risk**: Absolute (volume growth)

**Mitigation**:
- RQ auto-scale workers (post-MVP)
- Queue throttling (max 100 in queue - post-MVP)
- GUI queue throttling controls
- **Tiered Suggestion**: "High volume — prioritize queue items?"

**Implementation**:
- Worker pool management
- Queue size monitoring
- Priority queue support (post-MVP)
- Throttling controls in config

### 6. Variable Sizes/DPIs

**Risk**: Absolute (scanners have different DPIs)

**Mitigation**:
- All matching is scale/DPI invariant (use ratios, not absolute pixels)
- Normalization step: resize to template DPI (300) using cubic interpolation
- Rotation correction: deskew first (Hough lines on text lines)
- GUI: Show original + normalized images side-by-side with DPI/scale metrics

**Implementation**:
- DPI detection
- Normalization pipeline
- Ratio-based matching
- GUI DPI display

---

## Unknown Unknowns

### Identified Risks

1. **OCR Quality Degradation**
   - **Unknown**: How preprocessing affects different document types
   - **Mitigation**: GUI allows human inspection and manual adjustment
   - **Monitoring**: Track preprocessing success rates

2. **Template Matching False Positives**
   - **Unknown**: How often similar templates match incorrectly
   - **Mitigation**: Confidence thresholds, human review
   - **Monitoring**: Track false positive rates

3. **LLM Response Parsing**
   - **Unknown**: How reliable is LLM response parsing
   - **Mitigation**: Validation against OCR, human review fallback
   - **Monitoring**: Track LLM accuracy rates

4. **File Format Variations**
   - **Unknown**: Edge cases in PDF/JPG/PNG/TIFF parsing
   - **Mitigation**: Robust file handling, error logging
   - **Monitoring**: Track file format errors

5. **Concurrent Processing**
   - **Unknown**: How many concurrent jobs can run
   - **Mitigation**: Queue throttling, worker limits
   - **Monitoring**: Track processing times, queue depth

6. **Memory Usage**
   - **Unknown**: Memory requirements for large documents
   - **Mitigation**: Image resizing, chunked processing
   - **Monitoring**: Track memory usage per job

### Risk Monitoring

**Metrics to Track:**
- Processing success rate
- Average processing time
- Queue depth
- Error rates by type
- Confidence score distribution
- Human review rate
- Template match accuracy
- LLM usage rate

**Logging:**
- All errors logged to audit log
- Metrics logged to separate metrics file
- GUI dashboard for monitoring (post-MVP)

---

## Module Structure

### Directory Structure

```
digidoc/
├── __init__.py
├── config.py                    # Configuration management
├── queue/                       # Queue abstraction layer
│   ├── __init__.py
│   ├── queue_adapter.py
│   ├── rq_adapter.py
│   └── celery_adapter.py
├── tasks/                       # Queue-agnostic tasks
│   ├── __init__.py
│   └── receipt_tasks.py
├── preprocessing/               # Preprocessing pipeline
│   ├── __init__.py
│   ├── deskew.py
│   ├── denoise.py
│   ├── binarize.py
│   ├── normalize.py
│   └── border_removal.py
├── matching/                     # Template matching
│   ├── __init__.py
│   ├── structural.py
│   ├── feature.py
│   └── text_fallback.py
├── extraction/                  # Field extraction
│   ├── __init__.py
│   ├── zonal_ocr.py
│   ├── contour_extraction.py
│   └── llm_confirmation.py
├── templates/                   # Template management
│   ├── __init__.py
│   ├── cache.py
│   ├── sync.py
│   └── matcher.py
├── database/                    # Database models
│   ├── __init__.py
│   ├── models.py
│   └── init_db.py
├── gui/                         # Streamlit GUI
│   ├── __init__.py
│   ├── app.py                   # Main Streamlit app
│   ├── pages/
│   │   ├── queue_dashboard.py
│   │   ├── preprocessing_review.py
│   │   ├── template_matching.py
│   │   ├── extraction_review.py
│   │   └── tiered_suggestions.py
│   └── utils/
│       ├── image_utils.py
│       └── visualization.py
├── api/                         # Flask API (for integration)
│   ├── __init__.py
│   ├── routes.py
│   └── handlers.py
└── utils/                       # Utilities
    ├── __init__.py
    ├── file_utils.py
    ├── image_utils.py
    └── text_utils.py
```

### Module Dependencies

```
digidoc/
├── queue/ (no dependencies on other digidoc modules)
├── tasks/ (depends on: preprocessing, matching, extraction)
├── preprocessing/ (depends on: OpenCV, PIL)
├── matching/ (depends on: templates, OpenCV)
├── extraction/ (depends on: templates, Tesseract, Ollama)
├── templates/ (depends on: database)
├── database/ (depends on: SQLAlchemy)
├── gui/ (depends on: Streamlit, all other modules for data)
└── api/ (depends on: Flask, tasks)
```

---

## Integration Implementation

This section describes DigiDoc's implementation of the integration contracts defined in [Construction Suite Ecosystem Architecture](../../../shared_documentation/architecture/MASTER_ARCHITECTURE.md#integration-contracts).

### Receiving Files from Watcher

**Endpoint**: `POST /api/digidoc/queue`  
**Port**: 8001 (configurable)  
**Authentication**: API token required (Zero Trust)

**Implementation**:
- Flask API endpoint receives HTTP POST request
- Validates `file_path` is absolute path
- Creates queue item in database
- Enqueues processing task via queue abstraction layer
- Returns queue_item_id and status

**Path Handling**: 
- Validates `file_path` parameter is absolute path
- Uses absolute path for all file operations
- No path expansion needed (Watcher provides absolute path)

### Sending Data to HQ

**Endpoint**: Configurable (default: `/api/digidoc/process-complete`)

**Implementation**:
- HTTP POST request to HQ API
- Sends extracted fields, confidence scores, processing metadata
- Handles errors gracefully (log, retry, fallback)
- Updates queue item status based on response

### Template Synchronization

**Pull from HQ**:
- Periodic sync or on-demand
- HTTP GET request to HQ template sync endpoint
- Updates local template cache
- Handles errors (continue with cached templates)

**Push to HQ**:
- When new template created in DigiDoc
- HTTP POST request to HQ template create endpoint
- Handles errors (log, retry, store locally)

---

## Future Requirements

This section lists features and enhancements planned for post-MVP implementation. Detailed design documents are located in `shared_documentation/planning/slices/`.

### Template Matching Enhancements

#### Two-Phase Template Matching
**Status**: Future  
**Purpose**: Performance optimization for large template libraries (50-100+ templates)  
**Design Document**: [two-phase-template-matching.md](../../../shared_documentation/planning/slices/two-phase-template-matching.md)  
**Description**: Coarse-grained initial filter followed by detailed comparison for improved performance with large template libraries.

#### Feature Detection (ORB Keypoints)
**Status**: Future  
**Purpose**: Secondary matching method for improved accuracy  
**Description**: ORB keypoint detection and matching as a secondary matching method (20% weight in combined scoring).

#### Text Fallback Matching
**Status**: Future  
**Purpose**: Tertiary matching method when structural and feature matching fail  
**Description**: Text-based matching using OCR-extracted text as a fallback (10% weight in combined scoring).

### Extraction Enhancements

#### Contour-Based Extraction
**Status**: Future  
**Purpose**: Alternative extraction method for complex layouts  
**Description**: Contour analysis for field detection in documents with non-standard layouts.

#### LLM Integration (Ollama)
**Status**: Future  
**Purpose**: Intelligent field extraction and validation  
**Description**: Local LLM integration for field extraction confirmation and validation.

#### Handwriting Detection
**Status**: Future  
**Purpose**: Support for handwritten fields  
**Description**: Detection and processing of handwritten text in documents.

#### Multi-Page Support
**Status**: Future  
**Purpose**: Process multi-page documents  
**Description**: Support for processing documents with multiple pages.

### Production Enhancements

#### Celery Adapter
**Status**: Future  
**Purpose**: Production-grade queue system  
**Description**: Celery adapter implementation for production deployment (replaces RQ for MVP).

#### Queue Throttling
**Status**: Future  
**Purpose**: Rate limiting and resource management  
**Description**: Throttling mechanisms to prevent resource exhaustion.

#### Authentication Integration
**Status**: Future  
**Purpose**: Secure API access  
**Description**: Authentication and authorization for API endpoints.

#### Notifications
**Status**: Future  
**Purpose**: Alert system for processing events  
**Description**: Email/Slack notifications for processing events and errors.

#### Retention Policies
**Status**: Future  
**Purpose**: Automated data cleanup  
**Description**: Policies for automatic cleanup of old queue items and processed files.

#### Cloud Mirroring Support
**Status**: Future  
**Purpose**: Backup and sync capabilities  
**Description**: Cloud mirroring for backup and synchronization (post-MVP).

---

## Notes

- This document is **LIVE** and will be updated as development progresses
- All architectural decisions should be reflected here
- Sub-plans reference this master plan
- Unknown unknowns added as discovered
- Risk mitigations updated as implemented

---

**End of ARCHITECTURE.md**

