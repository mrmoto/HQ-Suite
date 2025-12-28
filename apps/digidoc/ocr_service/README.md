# OCR Service

Python-based OCR service for processing receipt images.

## Setup

### 1. Install System Dependencies

**macOS:**
```bash
brew install tesseract
```

### 2. Install Python Dependencies

```bash
pip install -r requirements_ocr.txt
```

### 3. Run the Service

```bash
./ocr_service/run_server.sh
```

Or manually:
```bash
cd ocr_service
python3 -m ocr_service.api_server
```

The service will run on `http://127.0.0.1:5000` by default.

## API Endpoints

### POST /process
Process a receipt image.

**Request:**
- Multipart form data with `file` field, OR
- JSON with `image_path` field

**Response:**
```json
{
  "vendor": "Mead Clark Lumber",
  "format_detected": "mead_clark_format1",
  "confidence": 0.92,
  "confidence_level": "high",
  "fields": {
    "receipt_date": "2025-12-15",
    "receipt_number": "12345",
    "line_items": [...],
    "subtotal": 150.00,
    "tax_amount": 12.00,
    "total_amount": 162.00
  },
  "ocr_text": "...",
  "ocr_data": {...}
}
```

### GET /health
Health check endpoint.

### POST /format/detect
Detect receipt format only (no full extraction).

## Configuration

Set environment variables:
- `OCR_SERVICE_PORT` - Port to run on (default: 5000)
- `OCR_SERVICE_DEBUG` - Debug mode (default: false)

## Format Templates

Currently supports:
- Mead Clark Lumber Format 1
- Mead Clark Lumber Format 2

Format templates can be extended in `ocr_service/formats/`.

## Confidence Scoring

Confidence thresholds:
- **High (≥85%)**: Auto-process to `purchase_receipts` table
- **Medium (70-84%)**: Flag for quick review
- **Low (<70%)**: Require full manual review

Confidence is calculated based on:
- OCR text quality (30%)
- Field extraction success rate (40%)
- Pattern matching confidence (20%)
- Data validation (10%)
