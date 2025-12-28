---
name: OpenCV-First Template Matching with OCR Fallback
overview: Implement OpenCV-based structural analysis and feature detection as primary template matching method, with Tesseract OCR as secondary/fallback when image-based confidence is low. This image-first approach improves accuracy before expensive OCR operations.
todos:
  - id: create_template_database
    content: "Create template image database: store reference images and structure metadata for each format"
    status: pending
  - id: implement_opencv_detector
    content: Implement OpenCVFormatDetector class with structural analysis and feature detection methods
    status: pending
  - id: update_base_format
    content: Add detect_format_from_image() and get_template_structure() methods to BaseReceiptFormat
    status: pending
  - id: add_structure_definitions
    content: Add get_template_structure() method to MeadClarkFormat1 with structural metadata
    status: pending
  - id: implement_hybrid_detection
    content: "Update OCRProcessor with hybrid detection: OpenCV first, OCR fallback"
    status: pending
  - id: update_api_flow
    content: Update API server to use hybrid detection in /process endpoint
    status: pending
  - id: test_opencv_detection
    content: Test OpenCV detection with sample receipts and tune confidence thresholds
    status: pending
---

# OpenCV-First Template Matching with OCR Fallback

## Overview

Implement a two-stage template matching system:

1. **Stage 1 (Primary)**: OpenCV image analysis - structural analysis + feature detection
2. **Stage 2 (Fallback)**: Tesseract OCR text analysis - only if image-based confidence is low

## Architecture

### Current Flow (OCR-First)

```
Image → Preprocess → OCR (Tesseract) → Text Analysis → Format Detection → Field Extraction
```

### New Flow (Image-First)

```
Image → Preprocess → OpenCV Analysis → Format Detection (High Confidence?)
    ├─ YES (≥0.85) → OCR (only for field extraction) → Field Extraction
    └─ NO (<0.85) → OCR (full text) → Text-Based Format Detection → Field Extraction
```

## OpenCV Template Matching Approaches

### Approach 1: Structural Analysis (Recommended Primary)

**What it does**: Analyzes receipt layout structure without reading text.

**Key Features to Detect**:

- Header region position and size
- Line item table structure (rows, columns, spacing)
- Footer region (totals, payment section)
- Column separators and boundaries
- Text region boundaries
- Overall layout proportions

**Implementation**:

```python
# Detect structural elements
- Horizontal lines (table rows)
- Vertical lines (column separators)
- Text regions (contours/blobs)
- Layout regions (header, body, footer)
- Spacing patterns (line item spacing)
```

**Advantages**:

- Fast (no OCR needed)
- Robust to OCR errors
- Works with poor image quality
- Layout is format-specific

**Confidence Scoring**:

- Match header structure: 30%
- Match line item table structure: 40%
- Match footer/payment section: 20%
- Match overall proportions: 10%

### Approach 2: Feature Detection (Supplemental)

**What it does**: Detects visual features like logos, form elements, specific shapes.

**Key Features**:

- Logo detection (if vendor logos are available)
- Form field detection (rectangles, checkboxes)
- Specific visual markers (borders, stamps, watermarks)
- Color patterns (if receipts have color coding)

**Implementation**:

```python
# Use SIFT/ORB for feature matching
- Extract keypoints from template images
- Match keypoints between template and input
- Detect specific visual elements (logos, stamps)
```

**Advantages**:

- Very specific format identification
- Works even with rotated/scaled images
- Can detect vendor-specific visual elements

**When to Use**:

- As supplement to structural analysis
- When vendor logos are available
- For distinguishing very similar formats

## Implementation Plan

### Phase 1: Create Template Image Database

**Goal**: Store reference template images for each format.

**Files to Create**:

- `ocr_service/templates/image_templates/mead_clark_format1/`
        - `template_reference.png` - Clean reference receipt
        - `header_region.png` - Header section only
        - `line_items_region.png` - Line items section only
        - `footer_region.png` - Footer/payment section only
        - `template_structure.json` - Structural metadata

**Template Structure Metadata**:

```json
{
  "format_id": "mead_clark_format1",
  "vendor": "Mead Clark Lumber",
  "regions": {
    "header": {"y": 0, "height": 200, "features": ["email", "customer_info"]},
    "line_items": {"y": 400, "height": 600, "columns": 5, "row_spacing": 30},
    "footer": {"y": 1000, "height": 150, "features": ["payment_method", "amount_received"]}
  },
  "structural_features": {
    "horizontal_lines": 15,
    "vertical_lines": 5,
    "column_count": 5,
    "line_item_pattern": "numbered_sku_description"
  }
}
```

### Phase 2: Implement OpenCV Format Detector

**File**: `ocr_service/utils/opencv_format_detector.py`

**Class**: `OpenCVFormatDetector`

**Methods**:

1. `detect_format(image_path, template_dir) -> (format_id, confidence)`

            - Primary detection method
            - Returns format ID and confidence (0.0-1.0)

2. `analyze_structure(image) -> dict`

            - Detect horizontal/vertical lines
            - Identify regions (header, body, footer)
            - Count columns and rows
            - Measure spacing patterns

3. `match_structure(input_structure, template_structure) -> float`

            - Compare structural features
            - Calculate similarity score

4. `detect_features(image, template_features) -> float`

            - Match visual features (SIFT/ORB)
            - Calculate feature match score

5. `extract_regions(image) -> dict`

            - Extract header, body, footer regions
            - Return region coordinates

**Structural Analysis Steps**:

```python
1. Load and preprocess image (grayscale, denoise)
2. Detect horizontal lines (HoughLinesP or contour detection)
3. Detect vertical lines (column separators)
4. Identify text regions (contours, connected components)
5. Calculate layout metrics:
   - Header height ratio
   - Line item row spacing
   - Column count and widths
   - Footer position and size
6. Compare with template structure
7. Calculate confidence score
```

### Phase 3: Update BaseReceiptFormat Interface

**File**: `ocr_service/formats/base_format.py`

**Add New Methods**:

```python
def detect_format_from_image(self, image_path: str) -> tuple[bool, float]:
    """
    Detect format using OpenCV image analysis.
    
    Args:
        image_path: Path to receipt image
        
    Returns:
        Tuple of (matches: bool, confidence: float)
    """
    # Default implementation uses OpenCV detector
    pass

def get_template_structure(self) -> dict:
    """
    Return structural template metadata for this format.
    
    Returns:
        Dictionary with structural features
    """
    pass
```

### Phase 4: Update OCRProcessor for Hybrid Approach

**File**: `ocr_service/ocr_processor.py`

**New Method**: `detect_format_hybrid(image_path) -> (format, confidence, method_used)`

**Logic**:

```python
1. Try OpenCV detection first:
   - opencv_result = opencv_detector.detect_format(image_path)
   - if opencv_result.confidence >= 0.85:
       return (format, confidence, "opencv")

2. Fallback to OCR if confidence low:
   - ocr_result = self.process_image(image_path)
   - text_result = self.detect_format(ocr_result['text'])
   - return (format, confidence, "ocr")

3. Combine results if both available:
   - weighted_confidence = (opencv * 0.7) + (ocr * 0.3)
   - return best match
```

### Phase 5: Create Template Structure Definitions

**File**: `ocr_service/formats/mead_clark_format1.py`

**Add Method**: `get_template_structure() -> dict`

**Return Structure**:

```python
{
    "regions": {
        "header": {
            "y_start": 0,
            "y_end": 0.20,  # 20% of image height
            "features": ["email_address", "invoice_address", "customer_info"]
        },
        "line_items": {
            "y_start": 0.40,
            "y_end": 0.85,
            "column_count": 5,
            "row_spacing_pixels": 30,
            "pattern": "numbered_sku_dash_description"
        },
        "footer": {
            "y_start": 0.85,
            "y_end": 1.0,
            "features": ["payment_method_column", "amount_received_column"]
        }
    },
    "structural_features": {
        "horizontal_line_count": 15,
        "vertical_line_count": 5,
        "has_table_structure": True,
        "line_item_format": "number_sku_description_qty_price_total"
    }
}
```

## Technical Implementation Details

### Structural Analysis Algorithm

**Step 1: Line Detection**

```python
# Detect horizontal lines (table rows)
horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)

# Detect vertical lines (column separators)
vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
```

**Step 2: Region Identification**

```python
# Find text regions using contours
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Group contours into regions
header_contours = [c for c in contours if c.y < header_threshold]
body_contours = [c for c in contours if header_threshold < c.y < footer_threshold]
footer_contours = [c for c in contours if c.y > footer_threshold]
```

**Step 3: Structure Comparison**

```python
# Compare detected structure with template
structure_score = 0.0

# Compare line counts
line_count_diff = abs(detected_lines - template_lines) / template_lines
structure_score += (1.0 - min(line_count_diff, 1.0)) * 0.3

# Compare region positions
header_pos_diff = abs(detected_header_y - template_header_y) / image_height
structure_score += (1.0 - min(header_pos_diff, 0.5)) * 0.2

# Compare column structure
column_match = detected_columns == template_columns
structure_score += (1.0 if column_match else 0.0) * 0.5
```

### Feature Detection (SIFT/ORB)

**Step 1: Extract Keypoints**

```python
# Initialize detector
sift = cv2.SIFT_create()  # or ORB_create()

# Extract keypoints and descriptors
keypoints_template, descriptors_template = sift.detectAndCompute(template_image, None)
keypoints_input, descriptors_input = sift.detectAndCompute(input_image, None)
```

**Step 2: Match Features**

```python
# Match descriptors
bf = cv2.BFMatcher()
matches = bf.knnMatch(descriptors_template, descriptors_input, k=2)

# Apply ratio test
good_matches = []
for match_pair in matches:
    if len(match_pair) == 2:
        m, n = match_pair
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

# Calculate match score
match_score = len(good_matches) / len(keypoints_template)
```

## Integration Points

### Update API Server

**File**: `ocr_service/api_server.py`

**Modify `/process` endpoint**:

```python
# New flow:
1. Try OpenCV detection first
   opencv_result = opencv_detector.detect_format(file_path)
   
2. If high confidence (≥0.85), use format directly
   if opencv_result.confidence >= 0.85:
       format_template = opencv_result.format
       # Run OCR only for field extraction (faster, targeted)
       ocr_text = ocr_processor.extract_text_regions(file_path, format_template.regions)
   
3. If low confidence, fallback to OCR-based detection
   else:
       ocr_result = ocr_processor.process_image(file_path)
       format_template = ocr_processor.detect_format(ocr_result['text'])
```

### Update Template Matching Flow

**File**: `ocr_service/templates/template_matcher.py`

**Add Method**: `find_matching_templates_from_image(image_path, ...)`

**Logic**:

```python
1. OpenCV detection (primary)
2. If confidence high, return result
3. If confidence low, call existing OCR-based method
4. Combine results with weighted scoring
```

## Benefits

1. **Performance**: Skip expensive OCR when format is clear from structure
2. **Accuracy**: Structural features are more reliable than OCR text
3. **Robustness**: Works with poor image quality, rotation, scaling
4. **Cost**: OCR only runs when needed (low confidence cases)
5. **Speed**: Image analysis is faster than full-page OCR

## Files to Create/Modify

### New Files

1. `ocr_service/utils/opencv_format_detector.py` - OpenCV detection implementation
2. `ocr_service/templates/image_templates/mead_clark_format1/template_structure.json` - Structure metadata
3. `ocr_service/templates/image_templates/mead_clark_format1/template_reference.png` - Reference image

### Modified Files

1. `ocr_service/formats/base_format.py` - Add `detect_format_from_image()` method
2. `ocr_service/formats/mead_clark_format1.py` - Add `get_template_structure()` method
3. `ocr_service/ocr_processor.py` - Add hybrid detection method
4. `ocr_service/api_server.py` - Update processing flow
5. `ocr_service/templates/template_matcher.py` - Add image-based matching

## Dependencies

- `opencv-python>=4.8.0` (already in requirements)
- `opencv-contrib-python` (for SIFT/ORB - may need to add)

## Testing Strategy

1. Test with clean reference receipts (should get high confidence from structure)
2. Test with rotated/scaled receipts (should still match structure)
3. Test with poor quality images (should fallback to OCR)
4. Test with unknown formats (should return low confidence, trigger OCR)
5. Measure performance improvement (OCR skip rate, speed improvement)

## Confidence Thresholds

- **High Confidence (≥0.85)**: Use format directly, OCR only for field extraction
- **Medium Confidence (0.60-0.84)**: Use format but verify with OCR
- **Low Confidence (<0.60)**: Fallback to OCR-based detection

## Next Steps

1. Create templa

4. Test with unknown formats (should return low confidence, triggerte structure database from sample receipts
5. Implement OpenCV format detector

3. Update format templates with structure definitions

4. Integrate hybrid detection into processing pipeline