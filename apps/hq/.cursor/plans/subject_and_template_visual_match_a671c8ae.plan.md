---
name: subject_and_template_visual_match
overview: Develop milestone to display original image, preprocessed image, and template match visualization side-by-side in Streamlit GUI. All preprocessing methods and file storage must align with MASTER_ARCHITECTURE.md specifications.
todos:
  - id: config-system
    content: "Create configuration system: config.py loader and digidoc_config.yaml with all preprocessing parameters, file paths, and matching weights from MASTER_ARCHITECTURE.md"
    status: pending
  - id: preprocessing-deskew
    content: "Replace deskew method in image_preprocessing.py: change from minAreaRect to HoughLinesP + rotation as specified in MASTER_ARCHITECTURE.md"
    status: pending
  - id: preprocessing-denoise
    content: "Replace denoise method in image_preprocessing.py: change from bilateralFilter to fastNlMeansDenoising as specified in MASTER_ARCHITECTURE.md"
    status: pending
  - id: preprocessing-pipeline
    content: "Add missing preprocessing steps: binarization (adaptive threshold), scale normalization (300 DPI), border removal (contour analysis). Update order to: Deskew → Denoise → Binarize → Scale Normalization → Border Removal"
    status: pending
  - id: file-storage
    content: "Create file_utils.py with queue item directory management following MASTER_ARCHITECTURE.md structure: {storage_base}/queue/{queue_item_id}/ with configurable storage_base (default ~/digidoc_storage/)"
    status: pending
  - id: preprocessing-task
    content: Create preprocessing_task.py that uses config parameters, follows correct preprocessing order, and saves files to queue item directory
    status: pending
  - id: structural-matching
    content: Create structural.py for ratio-based structural fingerprint computation (not absolute pixels) for DPI/scale invariance as per MASTER_ARCHITECTURE.md
    status: pending
  - id: template-storage
    content: Update database/models.py to add structural_fingerprint JSON column to CachedTemplate model
    status: pending
  - id: matching-task
    content: Create matching_task.py that computes structural fingerprints, compares to templates, and generates match visualization with zone overlays
    status: pending
  - id: visualization-utils
    content: Create visualization.py with functions to generate match visualization and create proportionally scaled side-by-side comparison images
    status: pending
  - id: streamlit-gui
    content: "Create Streamlit GUI: app.py (main), queue_view.py (list), visual_match.py (three-panel view with proportional scaling)"
    status: pending
  - id: queue-utils
    content: Create queue_utils.py to read ReceiptQueue items from Laravel database
    status: pending
  - id: processing-workflow
    content: Create process_for_visualization.py to orchestrate preprocessing and matching for GUI display
    status: pending
  - id: dependencies
    content: "Update requirements_ocr.txt: add streamlit>=1.28.0 and pyyaml>=6.0"
    status: pending
---

# Subject and Template Visual Match Milestone Plan

## Milestone Goal

Display in Streamlit web browser:

- Original scan image from queue (left panel)
- Preprocessed version (middle panel)
- Template match visualization with zone overlays (right panel)

All three views side-by-side, proportionally scaled for equal display.

## Critical MASTER_ARCHITECTURE.md Alignment Requirements

### Preprocessing Methods (Must Match Exactly)

- **Deskew**: Replace `minAreaRect` with `HoughLinesP + rotation` (as specified in MASTER_ARCHITECTURE.md line 229)
- **Denoise**: Replace `bilateralFilter` with `fastNlMeansDenoising` (as specified in MASTER_ARCHITECTURE.md line 235)
- **Preprocessing Order**: Deskew → Denoise → Binarize → Scale Normalization → Border Removal (MASTER_ARCHITECTURE.md lines 228-256)

### File Storage (Must Match Exactly)

- **Storage Base**: Configurable path, default `~/digidoc_storage/` (MASTER_ARCHITECTURE.md line 559)
- **Queue Item Directory**: `{storage_base}/queue/{queue_item_id}/` (MASTER_ARCHITECTURE.md line 565)
- **Original File**: `{queue_item_id}/original.{ext}` (MASTER_ARCHITECTURE.md line 566)
- **Preprocessed**: `{queue_item_id}/preprocessed.png` (MASTER_ARCHITECTURE.md line 567)

### Configuration (Must Match Exactly)

- **All Parameters Configurable**: No hardcoded values (MASTER_ARCHITECTURE.md line 639)
- **Environment Variable Override**: Support for all config values (MASTER_ARCHITECTURE.md lines 723-729)
- **Preprocessing Config**: `target_dpi: 300`, `denoise_level: "medium"`, `binarization_method: "otsu"`, `deskew_enabled: true`, `border_removal_enabled: true` (MASTER_ARCHITECTURE.md lines 671-679)

### Template Matching (Must Match Exactly)

- **Structural Fingerprint**: Ratio-based (not absolute pixels) for DPI/scale invariance (MASTER_ARCHITECTURE.md lines 301-309)
- **Weight**: 70% for structural matching (MASTER_ARCHITECTURE.md line 662)

## Implementation Plan

### Phase 1: Configuration System (Priority: First)

**Create** `ocr_service/config.py`:

- Load `digidoc_config.yaml` from project root
- Support environment variable overrides (e.g., `DIGIDOC_TARGET_DPI`)
- Provide typed accessors for all config sections
- Default values matching MASTER_ARCHITECTURE.md if config missing

**Create** `digidoc_config.yaml` in project root:

- `preprocessing` section: `target_dpi: 300`, `denoise_level: "medium"`, `binarization_method: "otsu"`, `deskew_enabled: true`, `border_removal_enabled: true`
- `paths` section: `storage_base: "~/digidoc_storage"`, `queue_directory: "{storage_base}/queue"`
- `scoring` section: `structural_weight: 0.70`
- All values from MASTER_ARCHITECTURE.md lines 649-689

### Phase 2: Preprocessing Pipeline Updates (Critical Alignment)

**Update** `ocr_service/utils/image_preprocessing.py`:

1. **Replace Deskew Method** (lines 56-91):

- Remove `minAreaRect` approach
- Implement `HoughLinesP` line detection
- Calculate rotation angle from detected lines
- Apply rotation using `cv2.warpAffine` with cubic interpolation
- Load `deskew_enabled` from config

2. **Replace Denoise Method** (lines 42-46):

- Remove `bilateralFilter`
- Implement `cv2.fastNlMeansDenoising`
- Load `denoise_level` from config (convert "medium" to appropriate parameters)

3. **Add Binarization Step**:

- Implement adaptive threshold (Otsu or Gaussian)
- Load `binarization_method` from config
- Apply after denoise, before scale normalization

4. **Add Scale Normalization**:

- Normalize to 300 DPI using cubic interpolation
- Load `target_dpi` from config
- Detect current DPI if possible, or estimate from dimensions

5. **Add Border Removal**:

- Implement contour analysis to detect white borders
- Crop to content area
- Load `border_removal_enabled` from config

6. **Update Preprocessing Order**:

- Change from: Denoise → Contrast → Deskew
- To: Deskew → Denoise → Binarize → Scale Normalization → Border Removal
- Remove hardcoded values, load all from config

7. **Remove Contrast Enhancement** (or make optional):

- MASTER_ARCHITECTURE.md doesn't specify CLAHE in the 5-step pipeline
- Keep as optional enhancement if needed

**Create** `ocr_service/utils/file_utils.py`:

- `get_queue_item_directory(queue_item_id: str) -> str`: Returns `{storage_base}/queue/{queue_item_id}/` using config
- `ensure_queue_item_directory(queue_item_id: str) -> str`: Creates directory if needed
- `save_original_file(source_path: str, queue_item_id: str) -> str`: Copies original to `{queue_item_id}/original.{ext}`
- `save_preprocessed_image(image: np.ndarray, queue_item_id: str) -> str`: Saves to `{queue_item_id}/preprocessed.png`
- All paths use configurable `storage_base` (default `~/digidoc_storage/`)

**Create** `ocr_service/tasks/preprocessing_task.py`:

- `preprocess_image(image_path: str, queue_item_id: str) -> dict`:
- Load config
- Copy original to queue item directory
- Run preprocessing pipeline in correct order
- Save preprocessed image
- Save preprocessing metadata JSON (skew angle, DPI detected, etc.)
- Return paths dict

### Phase 3: Template Matching (Structural Fingerprint)

**Create** `ocr_service/matching/__init__.py` (empty)**Create** `ocr_service/matching/structural.py`:

- `compute_structural_fingerprint(image: np.ndarray) -> dict`:
- Detect contours using `cv2.findContours`
- Extract zones (bounding boxes for header, tables, footer, logos)
- Compute ratios: zone positions relative to image dimensions (not absolute pixels)
- Compute ratios: zone sizes relative to image dimensions
- Return fingerprint dict with zone ratios
- `compare_fingerprints(fingerprint1: dict, fingerprint2: dict) -> float`:
- Compare using Euclidean distance or SSIM on ratio-based features
- Return match score (0.0-1.0)

**Update** `ocr_service/database/models.py`:

- Add `structural_fingerprint` JSON column to `CachedTemplate` model
- Store zone positions and size ratios (not absolute pixels)
- Support template variant flag and similarity percentage

**Create** `ocr_service/tasks/matching_task.py`:

- `match_template(preprocessed_image_path: str, queue_item_id: str) -> dict`:
- Load templates from cache
- Compute structural fingerprint of preprocessed image (ratio-based)
- Compare to template fingerprints
- Return best match with confidence score
- Generate match visualization with zone overlays
- Save visualization: `{queue_item_id}/template_match.png`

### Phase 4: Visualization Generation

**Create** `ocr_service/gui/utils/visualization.py`:

- `generate_match_visualization(image: np.ndarray, matched_template: dict, zones: list) -> np.ndarray`:
- Draw zone overlays (header, tables, footer, logos) with colored bounding boxes
- Highlight matched template zones
- Add confidence score text overlay
- Return visualization image
- `create_side_by_side_comparison(original: np.ndarray, preprocessed: np.ndarray, match_viz: np.ndarray) -> np.ndarray`:
- Proportionally scale all images for equal display (as per MASTER_ARCHITECTURE.md line 281)
- Combine into single image with labels
- Return combined image

### Phase 5: Streamlit GUI

**Create** `ocr_service/gui/__init__.py` (empty)**Create** `ocr_service/gui/app.py`:

- Main Streamlit application entry point
- Load configuration on startup
- Multi-page navigation setup
- Page routing

**Create** `ocr_service/gui/pages/queue_view.py`:

- Display list of ReceiptQueue items
- Show: filename, status, confidence score, thumbnail
- Click to navigate to visual match view
- Simple filtering by status

**Create** `ocr_service/gui/pages/visual_match.py`:

- Three-panel view:
- Left: Original image (proportionally scaled)
- Middle: Preprocessed image (proportionally scaled)
- Right: Template match visualization with zone overlays (proportionally scaled)
- Display match confidence and template name
- Display preprocessing metadata (skew angle, DPI, etc.)
- Navigation back to queue list
- Auto-process if files don't exist:
- Check for `{queue_item_id}/preprocessed.png`
- Check for `{queue_item_id}/template_match.png`
- Run preprocessing/matching if missing

**Create** `ocr_service/gui/utils/queue_utils.py`:

- `get_queue_items() -> list`: Read ReceiptQueue items from Laravel database
- `get_queue_item(queue_item_id: str) -> dict`: Get single queue item
- `get_queue_item_file_path(queue_item_id: str) -> str`: Get original file path

**Create** `ocr_service/tasks/process_for_visualization.py`:

- `process_queue_item_for_visualization(queue_item_id: str) -> dict`:
- Get queue item from database
- Copy original to queue item directory
- Run preprocessing (save preprocessed.png)
- Run template matching (save template_match.png)
- Return paths to all images

### Phase 6: Dependencies and Integration

**Update** `requirements_ocr.txt`:

- Add `streamlit>=1.28.0`
- Add `pyyaml>=6.0` (for config file parsing)
- Ensure `opencv-python>=4.8.0` (for `fastNlMeansDenoising` and `HoughLinesP`)

**Update** `ocr_service/__init__.py` (if needed):

- Add imports for new modules

## Files to Create

1. `ocr_service/config.py` - Configuration loader with env var support
2. `digidoc_config.yaml` - Configuration file (project root)
3. `ocr_service/utils/file_utils.py` - File organization utilities
4. `ocr_service/tasks/preprocessing_task.py` - Preprocessing function
5. `ocr_service/matching/__init__.py`
6. `ocr_service/matching/structural.py` - Structural fingerprint computation
7. `ocr_service/tasks/matching_task.py` - Template matching function
8. `ocr_service/gui/__init__.py`
9. `ocr_service/gui/app.py` - Streamlit main app
10. `ocr_service/gui/pages/queue_view.py` - Queue list view
11. `ocr_service/gui/pages/visual_match.py` - Three-panel visualization
12. `ocr_service/gui/utils/queue_utils.py` - Queue data access
13. `ocr_service/gui/utils/visualization.py` - Visualization utilities
14. `ocr_service/tasks/process_for_visualization.py` - Processing workflow

## Files to Modify

1. `ocr_service/utils/image_preprocessing.py`:

- Replace deskew: `minAreaRect` → `HoughLinesP + rotation`
- Replace denoise: `bilateralFilter` → `fastNlMeansDenoising`
- Add binarization step (adaptive threshold)
- Add scale normalization (300 DPI)
- Add border removal (contour analysis)
- Update preprocessing order: Deskew → Denoise → Binarize → Scale Normalization → Border Removal
- Remove all hardcoded values, load from config

2. `ocr_service/database/models.py`:

- Add `structural_fingerprint` JSON column to `CachedTemplate`

3. `requirements_ocr.txt`:

- Add `streamlit>=1.28.0`
- Add `pyyaml>=6.0`

## Success Criteria

- [ ] All preprocessing methods match MASTER_ARCHITECTURE.md:
- [ ] Deskew uses `HoughLinesP` (not `minAreaRect`)
- [ ] Denoise uses `fastNlMeansDenoising` (not `bilateralFilter`)
- [ ] Preprocessing order: Deskew → Denoise → Binarize → Scale Normalization → Border Removal
- [ ] File storage follows MASTER_ARCHITECTURE.md structure:
- [ ] Configurable `storage_base` (default `~/digidoc_storage/`)
- [ ] Queue item directory: `{storage_base}/queue/{queue_item_id}/`
- [ ] Original file: `{queue_item_id}/original.{ext}`
- [ ] All parameters configurable (no hardcoded values)
- [ ] Environment variable override support
- [ ] Structural fingerprint is ratio-based (DPI/scale invariant)
- [ ] Streamlit GUI displays three-panel view:
- [ ] Original (left), Preprocessed (middle), Template match (right)
- [ ] All images proportionally scaled for equal display
- [ ] Works with existing ReceiptQueue items

## Out of Scope

- Feature detection (ORB keypoints) - structural only for this milestone
- Text fallback matching - structural only for this milestone
- LLM integration
- Color logo processing (HSV)
- Handwriting detection
- Full RQ queue system
- File upload capability