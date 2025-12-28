# Receipt Samples Directory

This directory contains sample receipts and analysis outputs for template development.

## Structure

```
receipt_samples/
├── images/              # Sample receipt images (JPG, PNG, PDF)
├── ocr_output/          # OCR text outputs from analyze_receipt.py
├── patterns/            # Pattern analysis outputs from document_patterns.py
├── patterns.md          # Documented field patterns
└── field_discovery.md   # Discovered fields and schema gaps
```

## Usage

### 1. Analyze a receipt
```bash
python3 ocr_service/tools/analyze_receipt.py images/receipt1.jpg
```

### 2. Document patterns
```bash
python3 ocr_service/tools/document_patterns.py ocr_output/receipt1_*.txt
```

### 3. Review and document
- Review OCR output in `ocr_output/`
- Review pattern analysis in `patterns/`
- Document confirmed patterns in `patterns.md`
- Track discovered fields in `field_discovery.md`

## Notes

- Keep original receipt images for reference
- OCR outputs help identify field patterns
- Pattern analysis helps create extraction logic
- Field discovery tracks schema gaps
