# Receipt Pattern Documentation

Documented field patterns for Mead Clark Lumber receipts based on actual OCR analysis.

## Receipt Structure

### Header Section
- Email: `service@meadclark.com` (often OCR'd as "SCVice@meagCialk.COIrn" or "cMail. service@meadciark.com")
- Invoice Address section
- Customer information section

### Body Section
- Customer details (Customer code, Contact Name, Contact Number, Job)
- Reference numbers (Your Ref, Our Ref)
- Sales information (Taken By, Sales Rep)
- Line items (numbered list with SKU, description, quantity, unit, prices)
- Delivery Address

### Footer Section
- Payment Method and Amount Received
- "Goods received in good condition" text
- Page number ("Page 1 of 1")

## Field Patterns

### Vendor Name Pattern
- **Location**: Top of receipt, email address
- **Format**: "Mead Clark" or variations
- **OCR Variations**: "meagCialk", "meadciark", "Mead Clark"
- **Regex**: `(?i)(mead\s*clark|service@meadclark\.com)`
- **Example**: "service@meadclark.com", "SCVice@meagCialk.COIrn"

### Receipt/Invoice Number Pattern
- **Location**: "Our Ref" field, typically near customer info
- **Format**: Numeric, 7 digits
- **Pattern**: `Our Ref\s+(\d{7})`
- **Regex**: `(?i)our\s+ref\s+(\d{7})`
- **Examples**: 
  - "Our Ref 1741680"
  - "Our Ref 1710785"
  - "Our Ref 3023855"

### Date Pattern
- **Location**: Header section (may be OCR'd inconsistently)
- **Format**: Not clearly visible in samples analyzed - may need additional preprocessing
- **Note**: Date may appear in header that OCR misses - check image preprocessing

### Total Amount Pattern
- **Location**: Bottom section, "Amount Received" field
- **Format**: Currency amount with dollar sign
- **Pattern**: `Amount Received\s+\$?([\d,]+\.\d{2})`
- **Regex**: `(?i)amount\s+received\s+\$?([\d,]+\.\d{2})`
- **Examples**:
  - "Amount Received $934.26"
  - "Amount Received | EEE cng 73 | 81.78" (OCR error, actual amount is 81.78)

### Subtotal Pattern
- **Location**: May appear before line items or in totals section
- **Format**: Not clearly visible in samples - may be calculated from line items
- **Note**: May need to calculate from line item totals

### Tax Amount Pattern
- **Location**: Totals section
- **Format**: Not clearly visible in samples analyzed
- **Note**: May need additional samples or better OCR preprocessing

### Payment Method Pattern
- **Location**: Bottom section, "Payment Method" field
- **Format**: Text description (Cash, Check, Credit, etc.)
- **Pattern**: `Payment Method\s+([A-Za-z]+)`
- **Regex**: `(?i)payment\s+method\s+([A-Za-z]+)`
- **Examples**: "Payment Method | Amount Received" (method may be on same line or previous line)

## Line Item Patterns

### Line Item Structure
Each line item follows this pattern:
```
[NUMBER] [SKU] - [DESCRIPTION] [QUANTITY] [UNIT] [UNIT_PRICE] [UNIT] [LINE_TOTAL]
```

### Line Item Pattern Details

**Pattern 1: Full format with quantity and unit**
- **Format**: `[NUMBER] [SKU] - [DESCRIPTION] [QTY] [UNIT] [PRICE] [UNIT] [TOTAL]`
- **Regex**: `^(\d+)\s+([A-Z0-9]+)\s+-\s+(.+?)\s+(\d+(?:\.\d+)?)\s+(\w+)\s+([\d,]+\.\d{2})\s+\w+\s+([\d,]+\.\d{2})$`
- **Examples**:
  - "1 LAX600G - STABILA 3-PLANE GREEN LASER KIT 1 ea 624.97 ea 624.97"
  - "2 344210 - STABILA REC500RG RED/GREEN RCVR 1 ea 309.29 ea 309.29"
  - "1 248CHR - 2X4X8' RWD CON HRT GRN RGH 4 mbf 3,833.24" (note: quantity 4, unit "mbf")

**Pattern 2: Simplified format**
- **Format**: `[NUMBER] [SKU] - [DESCRIPTION] [QTY] [UNIT] [PRICE] [UNIT] [TOTAL]`
- **Examples**:
  - "1 674171 - DRYWALL CUTTING BLADE 1 ea 14.75 ea 14.75"
  - "2 628501 - 5PC ASSORTED NUTSETTER SET 1 ea 30.77 ea 30.77"

### Quantity Pattern
- **Location**: After description, before unit
- **Format**: Integer or decimal number
- **Regex**: `(\d+(?:\.\d+)?)`
- **Examples**: "1", "4", "2"

### Description Pattern
- **Location**: Between SKU and quantity
- **Format**: Product description, may include dashes, numbers, letters
- **Pattern**: Text between SKU and quantity
- **Examples**: 
  - "2X4X8' RWD CON HRT GRN RGH"
  - "STABILA 3-PLANE GREEN LASER KIT"
  - "DRYWALL CUTTING BLADE"

### Unit Pattern
- **Location**: After quantity
- **Format**: Abbreviation (ea, mbf, etc.)
- **Examples**: "ea", "mbf"

### Unit Price Pattern
- **Location**: After unit, before second unit mention
- **Format**: Currency amount (may include commas)
- **Regex**: `([\d,]+\.\d{2})`
- **Examples**: "624.97", "309.29", "3,833.24"

### Line Total Pattern
- **Location**: End of line item
- **Format**: Currency amount (may include commas)
- **Regex**: `([\d,]+\.\d{2})$`
- **Examples**: "624.97", "309.29", "3,833.24"

## Format Detection Patterns

### Vendor Name Indicators
- "Mead Clark" (various OCR spellings)
- "service@meadclark.com" (email address)
- "meadclark.com" (domain)

### Format-Specific Identifiers
- "Our Ref" followed by 7-digit number
- "Invoice Address" header
- "Customer" section with customer code
- "Taken By" and "Sales Rep" fields
- Line items starting with number + SKU + dash

## OCR Quality Notes

- Average confidence: 42-53% (moderate quality)
- Common OCR errors:
  - "Mead Clark" → "meagCialk", "meadciark"
  - Email addresses may have character recognition issues
  - Numbers and prices generally well-recognized
- Recommendations:
  - Preprocess images to improve contrast
  - Consider image enhancement before OCR
  - Use fuzzy matching for vendor name detection

## Notes

- Receipts are invoices with "Our Ref" as the invoice/receipt number
- Customer information includes customer code (e.g., "SCOTTRD", "CASHCUST")
- Line items are well-structured and consistent
- Payment information appears at bottom but may be OCR'd inconsistently
- Date may need special handling - not clearly visible in OCR output

## Next Steps

1. Test template with these patterns
2. Refine patterns based on more samples
3. Add date extraction logic (may need image preprocessing)
4. Improve payment method extraction
5. Handle OCR errors in vendor name detection
