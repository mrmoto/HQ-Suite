# OCR Service Setup Guide

## Phase A.1 Implementation Complete

The OCR infrastructure has been implemented. Follow these steps to set up and test.

## Prerequisites

### 1. Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

Verify installation:
```bash
tesseract --version
```

### 2. Install Python Dependencies

```bash
cd /Users/scottroberts/Library/CloudStorage/Dropbox/cloud_storage/DigiDoc
pip3 install -r requirements_ocr.txt
```

### 3. Configure Laravel

Add to your `.env` file:
```env
OCR_SERVICE_URL=http://127.0.0.1:5000
OCR_SERVICE_TIMEOUT=60
```

## Starting the OCR Service

### Option 1: Using the script
```bash
./ocr_service/run_server.sh
```

### Option 2: Manual start
```bash
cd ocr_service
python3 -m ocr_service.api_server
```

The service will run on `http://127.0.0.1:5000` by default.

## Testing the Service

### 1. Health Check
```bash
curl http://127.0.0.1:5000/health
```

### 2. Test with Sample Receipt

Once you have scanned Mead Clark Lumber receipts:

```bash
curl -X POST http://127.0.0.1:5000/process \
  -F "file=@/path/to/receipt.jpg"
```

## Workflow

1. **Scan Receipt** → File appears in Dropbox queue folder
2. **File Watcher** → Detects file, uploads to Laravel API
3. **Laravel** → Creates `ReceiptQueue` entry, calls OCR service
4. **OCR Service** → Processes image, extracts data, calculates confidence
5. **Confidence Decision:**
   - **High (≥85%)**: Auto-creates `PurchaseReceipt` record
   - **Medium/Low (<85%)**: Stores in queue for manual review
6. **Review** → User reviews in Filament interface if needed

## Format Templates

The system currently has placeholder templates for:
- Mead Clark Lumber Format 1
- Mead Clark Lumber Format 2

**Next Step:** Once you have sample receipts, we'll refine these templates to match the actual receipt formats.

## Troubleshooting

### Tesseract not found
- Ensure Tesseract is installed: `brew install tesseract`
- Check PATH: `which tesseract`
- The service will try to find Tesseract automatically

### OCR Service won't start
- Check Python dependencies: `pip3 list | grep -E "(pytesseract|flask|pillow|opencv)"`
- Check port 5000 is available: `lsof -i :5000`

### Low confidence scores
- This is expected initially - templates need refinement with actual receipts
- Review extracted data in `ReceiptQueue` table
- Adjust format templates based on actual receipt structure

## Next Steps

1. Install Tesseract and Python dependencies
2. Start OCR service
3. Scan sample Mead Clark Lumber receipts
4. Test end-to-end workflow
5. Refine format templates based on results
6. Calibrate confidence thresholds
