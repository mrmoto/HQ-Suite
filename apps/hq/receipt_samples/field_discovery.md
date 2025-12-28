# Field Discovery Log

Track fields discovered during template development that may need to be added to the database schema.

## How to Use

1. **During Template Development**: Document all fields found in receipts
2. **Compare to Schema**: Check if fields exist in PurchaseReceipt or PurchaseReceiptLine tables
3. **Flag Missing Fields**: Mark fields that need migrations
4. **Create Migrations**: Generate migrations for missing fields

## Field Categories

### Receipt-Level Fields
Fields that belong to the `purchase_receipts` table.

### Line Item Fields
Fields that belong to the `purchase_receipt_lines` table.

## Discovered Fields

### Receipt-Level Fields

| Field Name | Type | Found In | In Schema? | Notes |
|------------|------|----------|------------|-------|
| receipt_date | date | All receipts | Yes | Already in schema |
| receipt_number | string | All receipts | Yes | Already in schema |
| total_amount | decimal | All receipts | Yes | Already in schema |
| | | | | |

### Line Item Fields

| Field Name | Type | Found In | In Schema? | Notes |
|------------|------|----------|------------|-------|
| description | text | All receipts | Yes | Already in schema |
| quantity | decimal | All receipts | Yes | Already in schema |
| unit_price | decimal | All receipts | Yes | Already in schema |
| | | | | |

## Fields Needing Migrations

### Receipt-Level Fields
- *Add fields here as they are discovered*

### Line Item Fields
- *Add fields here as they are discovered*

## Migration Notes

When creating migrations for new fields:

1. Create migration: `php artisan make:migration add_<field_name>_to_purchase_receipts_table`
2. Add field to migration
3. Update model fillable/casts
4. Update Filament resource forms
5. Update template extraction logic
6. Test with sample receipts

## Template

Use this template for new field entries:

```markdown
| field_name | type | found_in | in_schema? | notes |
|------------|------|----------|------------|-------|
| example_field | string | receipt1.jpg | No | Description of field |
```
