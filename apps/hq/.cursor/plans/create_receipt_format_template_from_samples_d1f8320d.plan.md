---
name: Create Receipt Format Template from Samples
overview: Create a receipt format template for Mead Clark Lumber from scratch by analyzing sample receipts, identifying patterns, and building a working template. Architecture supports multiple formats but MVP starts with one format.
todos:
  - id: create_analysis_tool
    content: Create analyze_receipt.py tool to extract and analyze OCR text from sample receipts
    status: completed
  - id: create_pattern_tool
    content: Create document_patterns.py tool to help identify and document field patterns
    status: completed
  - id: create_samples_directory
    content: Create receipt_samples/ directory structure for samples and analysis
    status: completed
  - id: analyze_sample_receipts
    content: Process sample receipts through OCR and document structure
    status: completed
  - id: document_patterns
    content: Document field patterns, positions, and formats in patterns.md
    status: completed
  - id: rewrite_format1_detection
    content: Rewrite MeadClarkFormat1 detect_format() with actual patterns from samples
    status: completed
  - id: rewrite_format1_extraction
    content: Rewrite MeadClarkFormat1 extract_fields() with accurate field patterns
    status: completed
  - id: rewrite_format1_line_items
    content: Rewrite MeadClarkFormat1 extract_line_items() with actual line item patterns
    status: completed
  - id: simplify_processor
    content: Update OCRProcessor to only load Format1 for MVP (keep architecture for multiple)
    status: completed
  - id: test_template
    content: Test template with sample receipts and validate extraction accuracy
    status: completed
  - id: todo-1766186932074-iu4o83zpp
    content: ""
    status: pending
---

# Create Receipt Format Template from Samples

## Overview

Create a receipt format template for Mead Clark Lumber from scratch by analyzing sample receipts, identifying field patterns, and implementing accurate extraction logic. Architecture supports multiple formats but MVP focuses on a single format.

## Key Decisions

1. **OCR Engine**: Tesseract (already set up, good for MVP)
2. **Format Count**: One format for MVP (Mead Clark), architecture ready for multiple
3. **Template Status**: Create from scratch (current templates are placeholders)
4. **Architecture**: Multi-format ready, but start simple

## Current State

- Placeholder template exists (`mead_clark_format1.py`) but needs complete rewrite
- Second format template exists but won't be used for MVP
- OCR infrastructure is working
- Sample receipts are available

## Development Workflow

### Phase 1: Receipt Analysis Tools

**Goal**: Create tools to analyze sample receipts and extract patterns

1. **Create Analysis Tool** (`ocr_service/tools/analyze_receipt.py`)

- Process receipt image through OCR
- Extract raw OCR text with line numbers
- Show text structure (header, body, footer regions)
- Save OCR output to file for review
- Highlight potential field locations

2. **Create Pattern Documentation Tool** (`ocr_service/tools/document_patterns.py`)

- Interactive tool to identify field patterns
- Document field positions and formats
- Generate pattern documentation
- Create regex pattern suggestions

### Phase 2: Analyze Sample Receipts

**Goal**: Understand the actual receipt structure

1. **Process Sample Receipts**

- Run OCR on each sample receipt
- Save OCR text output
- Document receipt structure manually
- Identify field patterns:
    - Date format and location
    - Receipt number format and location
    - Total amount format and location
    - Line item structure (quantity, description, price)
    - Subtotal and tax patterns

2. **Document Findings**

- Create pattern documentation file
- Note field positions and formats
- Document line item layout
- Identify unique identifiers for format detection

### Phase 3: Create Template

**Goal**: Build working template from identified patterns

1. **Update Format Detection**

- Add vendor name detection (Mead Clark Lumber)
- Add format-specific identifiers (if any)
- Implement confidence scoring
- For MVP: Simple detection (vendor name + basic patterns)

2. **Implement Field Extraction**

- Date extraction: Use identified pattern
- Receipt number: Use identified pattern
- Total amount: Use identified pattern
- Subtotal and tax: Use identified patterns
- Payment method: Extract if present

3. **Implement Line Item Extraction**

- Identify line item pattern from samples
- Extract quantity, description, unit price
- Calculate line totals
- Handle edge cases (multi-line descriptions, etc.)

### Phase 4: Test and Refine

**Goal**: Validate template works correctly

1. **Test Extraction**

- Run extraction on all sample receipts
- Verify required fields extracted correctly
- Check line items accuracy
- Validate confidence scores

2. **Refine Patterns**

- Adjust regex patterns based on results
- Improve field extraction accuracy
- Handle OCR errors gracefully
- Optimize line item extraction

## Architecture: Multi-Format Ready

### Format Detection Strategy

For MVP: Simple vendor-based detection

- Check for "Mead Clark" in text
- If found, use Mead Clark template
- If not found, return no match

For Future: Pattern-based detection

- Each format has unique identifiers
- Score all formats, pick best match
- Architecture already supports this (format list in OCRProcessor)

### Template Structure

Each template implements:

- `detect_format()`: Returns (matches: bool, confidence: float)
- `extract_fields()`: Returns dict of extracted fields
- `extract_line_items()`: Returns list of line items
- `validate_fields()`: Validates extracted fields (inherited)

## Implementation Details

### Files to Create

1. **`ocr_service/tools/analyze_receipt.py`**

- Command-line tool to analyze receipt images
- Outputs formatted OCR text with line numbers
- Saves OCR text to file
- Shows confidence scores

2. **`ocr_service/tools/document_patterns.py`**

- Interactive tool to document field patterns
- Helps identify regex patterns
- Generates pattern documentation

3. **`receipt_samples/`** (directory)

- Store sample receipt images
- Store OCR text outputs
- Store pattern documentation

4. **`receipt_samples/patterns.md`** (documentation)

- Document identified patterns
- Field positions and formats
- Line item structure
- Regex patterns used

### Files to Modify

1. **`ocr_service/formats/mead_clark_format1.py`**

- Complete rewrite based on actual receipt analysis
- Implement accurate `detect_format()`
- Implement accurate `extract_fields()`
- Implement accurate `extract_line_items()`

2. **`ocr_service/ocr_processor.py`**

- For MVP: Only load MeadClarkFormat1
- Keep architecture for multiple formats
- Comment out Format2 for now

3. **`ocr_service/formats/__init__.py`**

- Export only MeadClarkFormat1 for MVP
- Keep Format2 commented for future

## Development Process

### Step 1: Analyze Receipts

```bash
# Process sample receipts
python3 ocr_service/tools/analyze_receipt.py receipt1.jpg
python3 ocr_service/tools/analyze_receipt.py receipt2.jpg
```



### Step 2: Document Patterns

- Review OCR output
- Identify field patterns manually
- Document in patterns.md
- Identify regex patterns needed

### Step 3: Create Template

- Update `mead_clark_format1.py` with actual patterns
- Implement field extraction
- Implement line item extraction
- Test with samples

### Step 4: Validate

- Run extraction on all samples
- Verify accuracy
- Refine patterns as needed

## Template Requirements

### Field Discovery Process

During template development, fields will be discovered from actual receipts. The process:

1. **Identify Fields in OCR Text**

- Analyze OCR output for all data points
- Document fields found on receipts
- Note which fields are missing from current schema

2. **Document Missing Fields**

- Create field discovery log
- Track receipt-level fields vs line-item fields
- Document field types and constraints

3. **Create Migrations**

- Generate migration for new fields
- Add fields to PurchaseReceipt or PurchaseReceiptLine tables
- Update models and Filament resources

### Current Schema Fields

**PurchaseReceipt table** (from migration):

- receipt_date, receipt_number, po_number
- subtotal, tax_amount, total_amount
- payment_method, payment_reference
- receipt_image_path, receipt_image_thumbnail
- notes, status
- purchase_date, purchased_by_user_id
- entered_by_user_id, approved_by_user_id, approved_at, reimbursed_at

**PurchaseReceiptLine table** (from migration):

- line_number, product_id, vendor_sku
- description, quantity, unit_price, line_total
- tax_rate_applied, csi_code_id
- project_phase, notes

### Field Discovery Workflow

1. **During Template Development**

- Extract all fields from sample receipts
- Compare extracted fields to schema
- Document missing fields in `receipt_samples/field_discovery.md`

2. **During Review Process**

- Review interface shows extracted fields
- Reviewer can flag missing fields
- System tracks fields not in schema

3. **Create Migrations**

- Use field discovery log to create migrations
- Add fields to appropriate tables
- Update template to extract new fields

### Files for Field Management

1. **`receipt_samples/field_discovery.md`** (new)

- Log of discovered fields
- Fields found in receipts
- Fields missing from schema
- Field types and constraints

2. **`ocr_service/tools/compare_fields_to_schema.py`** (new)

- Compares extracted fields to database schema
- Identifies missing fields
- Generates migration suggestions

3. **Review Interface Enhancement**

- Show extracted fields in review UI
- Allow flagging missing fields
- Track field discovery during review

## MVP Simplifications

1. **Single Format**: Only Mead Clark Format 1
2. **Simple Detection**: Vendor name + basic validation
3. **Focus on Accuracy**: Get one format working well
4. **Architecture Ready**: Can add Format 2 later easily