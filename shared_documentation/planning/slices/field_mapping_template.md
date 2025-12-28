# Field Mapping Template Specification

**Purpose**: Specification for document-agnostic field extraction using template-provided context  
**Status**: Draft - Awaiting Review  
**Date**: 2025-12-26  
**Phase**: MVP - Testing Mode  
**Related**: [DEVELOPMENT_PATHWAY.md](../DEVELOPMENT_PATHWAY.md) - Extraction Pipeline section

---

## Overview

Field extraction must be **document-agnostic** in design, with context learned from template matching. The template provides field mappings and zone definitions that guide extraction, eliminating hardcoding. While MVP testing uses receipts, the system must support any document type.

### Key Principles

1. **Document Agnostic**: No hardcoded assumptions about document structure
2. **Template-Driven**: Template matching provides context (field mappings, zones, required fields)
3. **Configuration-Based**: All extraction parameters configurable, no hardcoding
4. **MVP Testing**: First pass focuses on end-to-end testing with receipt documents

---

## Architecture Context

### Ecosystem Framework

From `MASTER_ARCHITECTURE.md`:
- DigiDoc processes files through: preprocessing → template matching → **field extraction** → HQ API
- Template matching identifies document format and provides context
- Field extraction uses template-provided mappings to extract structured data
- Extracted fields sent to HQ via HTTP API with confidence scores

### Template Matching Provides Context

The matched template provides:
- **Field Mappings**: Dictionary mapping format-specific field names to database field names
- **Zone Definitions**: Spatial regions (header, body, footer, tables) for zonal OCR
- **Required Fields**: List of fields that must be extracted for validation
- **Optional Fields**: List of fields that may be extracted
- **Field Types**: Data types and validation rules for each field
- **Extraction Methods**: Per-field extraction strategy (zonal OCR, contour-based, LLM)

---

## Proposed Process

### Phase 1: Template Context Loading

**Input**: Matched template from template matching phase

**Process**:
1. Load matched template from cache (CachedTemplate model)
2. Extract template metadata:
   - `field_mappings`: `{format_field_name: database_field_name}`
   - `zone_definitions`: `{zone_name: {x, y, width, height}}`
   - `required_fields`: `[field_name, ...]`
   - `optional_fields`: `[field_name, ...]`
   - `field_types`: `{field_name: type}` (date, currency, number, text, etc.)
   - `extraction_strategy`: `{field_name: strategy}` (zonal_ocr, contour, llm)

**Output**: Template context object containing all extraction guidance

### Phase 2: Zone-Based Field Extraction

**Input**: 
- Preprocessed image
- Template context (from Phase 1)
- OCR text (from preprocessing phase)

**Process**:
1. **For each field in template field_mappings**:
   a. Determine extraction strategy from template (default: zonal_ocr)
   b. If strategy is `zonal_ocr`:
      - Get zone definition from template
      - Extract zone image from preprocessed image
      - Run OCR on zone image
      - Extract field value using field type validation
   c. If strategy is `contour`:
      - Use contour detection for table/structured data
      - Extract from detected regions
   d. If strategy is `llm`:
      - Extract zone image
      - Send to LLM with field-specific prompt
      - Parse LLM response

2. **Field Type Validation**:
   - Apply type-specific parsing (date parsing, currency parsing, number parsing)
   - Validate format (e.g., date format, currency format)
   - Return typed value or None if extraction fails

3. **Confidence Scoring**:
   - Per-field confidence based on OCR confidence in zone
   - Type validation success/failure
   - Template match confidence (higher match = higher field confidence)

**Output**: Dictionary of extracted fields with confidence scores:
```python
{
    'field_name': {
        'value': extracted_value,
        'confidence': float(0.0-1.0),
        'source': 'zonal_ocr' | 'contour' | 'llm',
        'zone': 'zone_name'
    },
    ...
}
```

### Phase 3: Field Validation

**Input**: Extracted fields dictionary

**Process**:
1. Check required fields: All required fields must have non-None values
2. Validate field types: Each field value must match expected type
3. Calculate extraction rate: `extracted_required / total_required`
4. Generate validation report: List missing fields, invalid fields, low-confidence fields

**Output**: Validation result:
```python
{
    'is_valid': bool,
    'extraction_rate': float(0.0-1.0),
    'missing_fields': [field_name, ...],
    'invalid_fields': [field_name, ...],
    'low_confidence_fields': [field_name, ...]
}
```

### Phase 4: Output Formatting

**Input**: Extracted fields, validation result

**Process**:
1. Format fields according to template field_mappings (format → database field names)
2. Add metadata:
   - Template ID
   - Extraction timestamp
   - Overall confidence score
   - Extraction method used
3. Structure for API output

**Output**: Structured JSON for HQ API:
```json
{
    "queue_item_id": "uuid",
    "template_id": "template_uuid",
    "extracted_fields": {
        "database_field_name": {
            "value": "extracted_value",
            "confidence": 0.95,
            "source": "zonal_ocr"
        },
        ...
    },
    "extraction_metadata": {
        "extraction_rate": 0.92,
        "missing_fields": [],
        "low_confidence_fields": ["field_name"],
        "extraction_method": "zonal_ocr"
    },
    "confidence": 0.92
}
```

---

## Implementation Components

### 1. Template Context Loader

**File**: `ocr_service/extraction/template_context.py`

**Class**: `TemplateContext`
- Loads template from cache
- Provides field mappings, zones, required fields
- Validates template structure
- Returns context object

### 2. Zone Extractor

**File**: `ocr_service/extraction/zone_extractor.py`

**Class**: `ZoneExtractor`
- Extracts zone images from preprocessed image
- Handles zone coordinate transformations
- Returns zone images for OCR

### 3. Field Extractor

**File**: `ocr_service/extraction/field_extractor.py`

**Class**: `FieldExtractor`
- Main extraction orchestrator
- Uses TemplateContext and ZoneExtractor
- Applies extraction strategies per field
- Returns extracted fields dictionary

### 4. Field Validator

**File**: `ocr_service/extraction/field_validator.py`

**Class**: `FieldValidator`
- Validates extracted fields against template requirements
- Type validation
- Required field checking
- Confidence threshold checking

### 5. Extraction Task

**File**: `ocr_service/tasks/extraction_task.py`

**Function**: `extract_fields(image_path, queue_item_id, template_id, calling_app_id)`
- Main task function for queue processing
- Orchestrates all extraction phases
- Updates queue item status
- Returns extraction results

---

## Template Structure Requirements

Templates must provide the following structure for field extraction:

```python
{
    'template_id': 'uuid',
    'format_name': 'vendor_format1',
    'field_mappings': {
        'receipt_date': 'receipt_date',  # format_field: database_field
        'receipt_number': 'receipt_number',
        'total_amount': 'total_amount',
        ...
    },
    'zone_definitions': {
        'header': {'x': 0, 'y': 0, 'width': 1000, 'height': 200},
        'body': {'x': 0, 'y': 200, 'width': 1000, 'height': 600},
        'footer': {'x': 0, 'y': 800, 'width': 1000, 'height': 200},
        'receipt_date_zone': {'x': 50, 'y': 50, 'width': 200, 'height': 30},
        'total_amount_zone': {'x': 700, 'y': 750, 'width': 200, 'height': 30},
        ...
    },
    'required_fields': ['receipt_date', 'receipt_number', 'total_amount'],
    'optional_fields': ['vendor_name', 'subtotal', 'tax_amount'],
    'field_types': {
        'receipt_date': 'date',
        'receipt_number': 'text',
        'total_amount': 'currency',
        'subtotal': 'currency',
        ...
    },
    'extraction_strategy': {
        'receipt_date': 'zonal_ocr',
        'receipt_number': 'zonal_ocr',
        'total_amount': 'zonal_ocr',
        'line_items': 'contour',  # table extraction
        ...
    }
}
```

---

## MVP Testing Approach

### Test Documents
- Use receipt samples (Mead Clark format)
- Template already matched via structural fingerprinting
- Focus on zonal OCR extraction (contour and LLM are post-MVP)

### Test Scenarios

1. **Happy Path**: All required fields extractable
   - Template matched with high confidence
   - All zones clearly defined
   - OCR text readable in zones
   - Expected: All required fields extracted with high confidence

2. **Partial Extraction**: Some fields missing
   - Template matched
   - Some zones have poor OCR quality
   - Expected: Missing fields identified, validation reports missing fields

3. **Low Confidence**: Fields extracted but low confidence
   - Template matched
   - OCR quality poor in zones
   - Expected: Fields extracted but flagged for review

4. **Type Validation**: Field type mismatches
   - Template matched
   - OCR extracts text but type validation fails (e.g., date format)
   - Expected: Field marked as invalid, validation report includes invalid fields

### Success Criteria

- [ ] Template context loads correctly from matched template
- [ ] Zone extraction works for all defined zones
- [ ] Zonal OCR extracts text from zones
- [ ] Field mappings applied correctly (format → database field names)
- [ ] Required field validation works
- [ ] Type validation works (date, currency, number, text)
- [ ] Confidence scoring per field
- [ ] Validation report generated correctly
- [ ] Output format matches API contract

---

## Configuration

All extraction parameters must be configurable via `digidoc_config.yaml`:

```yaml
extraction:
  zonal_ocr:
    min_confidence: 0.70
    zone_padding: 5  # pixels
  field_validation:
    required_field_threshold: 1.0  # all required must be present
    confidence_threshold: 0.85  # minimum confidence for auto-process
  types:
    date:
      formats: ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']
    currency:
      symbols: ['$', 'USD']
      decimal_places: 2
```

---

## Dependencies

- Template matching must be complete (provides matched template)
- Preprocessing must be complete (provides preprocessed image)
- OCR processing must be available (for zonal OCR)
- Template cache must contain templates with field mappings and zones

---

## Next Steps After Review

1. Review and approve this specification
2. Create implementation plan (if changes needed)
3. Implement components
4. Write tests (unit tests for each component)
5. Integration testing with real receipt samples
6. Update DEVELOPMENT_PATHWAY.md when complete

---

## Questions for Review

1. **Zone Definitions**: Should zones be absolute coordinates or relative (percentage-based)? Recommendation: Absolute coordinates for MVP, relative for post-MVP flexibility.

2. **Extraction Strategy Default**: If template doesn't specify strategy for a field, default to zonal_ocr? Recommendation: Yes, zonal_ocr as default.

3. **Multi-Zone Fields**: Can a field span multiple zones? Recommendation: Not for MVP, single zone per field.

4. **Zone Overlap**: What if zones overlap? Recommendation: Process in order, later zones override earlier if overlap.

5. **Missing Zones**: What if template defines field but no zone? Recommendation: Fall back to full-image OCR with field name search.

---

**Ready for Review**

