# Accuracy Check Text File Format

## Purpose

The accuracy check text file format is used to test OCR extraction accuracy before building the Canvas-based GUI for template field mapping. It provides a simple, human-readable format for:

- Testing extraction accuracy
- Validating field mappings
- Comparing OCR output to expected values
- Shortcut pipeline testing

## File Format

**File Extension**: `.txt`

**Format**: Structured text with justified, column-aligned sections (no pipe delimiters). Field names are left-aligned, values are right-aligned in fixed-width columns. Receipt lines use justified columns with proper spacing.

## Structure

The file is organized into sections:

1. **RECEIPT: METADATA** - Receipt metadata fields
2. **RECEIPT: VENDOR INFORMATION** - Vendor details
3. **RECEIPT: CUSTOMER INFORMATION** - Customer details
4. **RECEIPT: AMOUNT INFORMATION** - Financial amounts
5. **RECEIPT LINES:** - Line item table

## Formatting Rules

### Field Name-Value Pairs

- Field names: Left-aligned in fixed-width column (25 characters)
- Field values: Right-aligned in fixed-width column (20 characters)
- Format: `{field_name}:{value:>20}`

### Receipt Lines Table

- Header row: Column names with justified spacing
- Data rows: Each column aligned to match header widths
- Numeric values: Right-aligned with 4 decimal precision
- Text values: Left-aligned
- No pipe delimiters (`|`) - only spaces for column alignment

### Numeric Values

- All numeric values maintain 4 decimal precision (e.g., `3.0000`, `125.0000`)
- Format: `{value:>10.4f}` for right-aligned numeric values

## Example

```
RECEIPT: METADATA
project_fk:              <looked up from vendor template>
creationTimestamp:       <timestamp>
createdBy:               <user reviewing document>

RECEIPT: VENDOR INFORMATION
vendorFK:                <UUID>
vendorName:              Mead Clark Lumber
vendor_address1:        123 Main St
vendor_address2:         Suite 100
vendor_city:             Oakland
vendor_state:            CA
vendor_zip:              94605
salesRep:                John Paul Destruel

RECEIPT: CUSTOMER INFORMATION
customerNumber:          SCOTTRD
customerName:            Scott Roberts
customer_address1:       6458 Outlook Ave
customer_city:            Oakland
customer_state:           CA
customer_zip:            94605

RECEIPT: AMOUNT INFORMATION
amountSubtotal:          595.1692
amountTaxable:           70.1692
taxRate:                 0.101250
amountTax:               7.1000
amountDiscountPercent:   0.0000
balancePrior:            0.0000
amountTotal:             665.3384
amountDueAmt:            665.3384
amountBalanceDue:        0.0000

RECEIPT LINES:
Line  Description        qty       UOM    Price      Subtotal    taxable_amount  codeCSI
  1   toy                3.0000    ea     2.9900     8.9700      8.9700          NULL
  2   labor/hr           4.2000    hr   125.0000   525.0000      0.0000          NULL
  3   tool               4.0000    ea     8.9123    35.6492     35.6492          NULL
  4   foo                1.0000    5/pk  25.5500    25.5500     25.5500          NULL
```

## Field Reference

### Metadata Fields
- `project_fk`: Project foreign key (looked up from vendor template)
- `creationTimestamp`: Timestamp when receipt was created
- `createdBy`: User who reviewed/created the document

### Vendor Fields
- `vendorFK`: Vendor UUID
- `vendorName`: Vendor name
- `vendor_address1`: Vendor street address line 1
- `vendor_address2`: Vendor street address line 2
- `vendor_city`: Vendor city
- `vendor_state`: Vendor state (2-letter code)
- `vendor_zip`: Vendor ZIP code
- `salesRep`: Sales representative name

### Customer Fields
- `customerNumber`: Customer number/code
- `customerName`: Customer name
- `customer_address1`: Customer street address line 1
- `customer_city`: Customer city
- `customer_state`: Customer state (2-letter code)
- `customer_zip`: Customer ZIP code

### Amount Fields
- `amountSubtotal`: Subtotal amount (4 decimals)
- `amountTaxable`: Taxable amount (4 decimals)
- `taxRate`: Tax rate (4 decimals, e.g., 0.101250 = 10.125%)
- `amountTax`: Tax amount (4 decimals)
- `amountDiscountPercent`: Discount percentage (4 decimals)
- `balancePrior`: Prior balance (4 decimals)
- `amountTotal`: Total amount (4 decimals)
- `amountDueAmt`: Amount due (4 decimals)
- `amountBalanceDue`: Balance due (4 decimals)

### Line Item Fields
- `Line`: Line number
- `Description`: Item description
- `qty`: Quantity (4 decimals)
- `UOM`: Unit of measure
- `Price`: Unit price (4 decimals)
- `Subtotal`: Line subtotal (4 decimals)
- `taxable_amount`: Taxable amount for line (4 decimals)
- `codeCSI`: CSI code (or NULL)

## Usage

1. Generate accuracy check files from sample receipts using the `check_extraction_accuracy.py` tool
2. Review and manually correct expected values
3. Run accuracy checks to compare OCR extraction to expected values
4. Use results to refine extraction patterns and field mappings
