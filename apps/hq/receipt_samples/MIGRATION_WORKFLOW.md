# Migration Workflow for New Fields

When new fields are discovered during template development, follow this workflow to add them to the database schema.

## Discovery Process

1. **During Template Development**
   - Analyze sample receipts using `analyze_receipt.py`
   - Extract all fields from receipts
   - Document fields in `field_discovery.md`

2. **During Review Process**
   - Review extracted fields in ReceiptQueueReview interface
   - Flag missing fields using the ⚠️ button
   - Fields are logged for tracking

3. **Field Comparison**
   - Run `compare_fields_to_schema.py` on extraction results
   - Review comparison output
   - Document missing fields

## Creating Migrations

### Step 1: Identify Field Details

For each missing field, determine:
- **Field name**: Use snake_case (e.g., `receipt_date`)
- **Field type**: string, text, decimal, integer, date, datetime, boolean, etc.
- **Nullable**: Can the field be null?
- **Default value**: Should there be a default?
- **Table**: PurchaseReceipt or PurchaseReceiptLine?

### Step 2: Create Migration

```bash
# For receipt-level fields
php artisan make:migration add_<field_name>_to_purchase_receipts_table

# For line item fields
php artisan make:migration add_<field_name>_to_purchase_receipt_lines_table
```

### Step 3: Write Migration

Example for receipt-level field:

```php
public function up(): void
{
    Schema::table('purchase_receipts', function (Blueprint $table) {
        $table->string('field_name')->nullable()->after('existing_field');
        // Or:
        // $table->decimal('field_name', 12, 2)->nullable();
        // $table->text('field_name')->nullable();
        // $table->date('field_name')->nullable();
    });
}

public function down(): void
{
    Schema::table('purchase_receipts', function (Blueprint $table) {
        $table->dropColumn('field_name');
    });
}
```

Example for line item field:

```php
public function up(): void
{
    Schema::table('purchase_receipt_lines', function (Blueprint $table) {
        $table->string('field_name')->nullable()->after('existing_field');
    });
}

public function down(): void
{
    Schema::table('purchase_receipt_lines', function (Blueprint $table) {
        $table->dropColumn('field_name');
    });
}
```

### Step 4: Run Migration

```bash
php artisan migrate
```

### Step 5: Update Model

Add field to model's `$fillable` array:

**PurchaseReceipt.php:**
```php
protected $fillable = [
    // ... existing fields
    'field_name',
];
```

**PurchaseReceiptLine.php:**
```php
protected $fillable = [
    // ... existing fields
    'field_name',
];
```

### Step 6: Update Filament Resource

Add field to Filament resource forms:

**PurchaseReceiptResource.php:**
```php
public static function form(Form $form): Form
{
    return $form->schema([
        // ... existing fields
        TextInput::make('field_name')
            ->label('Field Label')
            ->maxLength(255),
    ]);
}
```

### Step 7: Update Template Extraction

Update the receipt format template to extract the new field:

**mead_clark_format1.py:**
```python
def extract_fields(self, text: str) -> Dict[str, Any]:
    fields = {
        # ... existing fields
        'field_name': self._extract_field_name(text),
    }
    return fields
```

### Step 8: Update OcrProcessingService

Ensure the service maps the extracted field correctly:

**OcrProcessingService.php:**
```php
// Field mapping happens automatically if field name matches
// If different name, add mapping:
$receipt->field_name = $fields['ocr_field_name'] ?? null;
```

## Field Type Guidelines

### String Fields
- Use `string()` for short text (up to 255 chars)
- Use `text()` for longer text
- Specify `maxLength()` if needed

### Numeric Fields
- Use `decimal(12, 2)` for currency amounts
- Use `decimal(10, 4)` for quantities
- Use `integer()` for whole numbers

### Date Fields
- Use `date()` for date-only fields
- Use `dateTime()` for date+time fields
- Use `timestamp()` for created/updated timestamps

### Boolean Fields
- Use `boolean()` with `default(false)`

## Common Field Patterns

### Receipt-Level Fields
- Vendor information (name, address, phone)
- Receipt metadata (date, number, PO number)
- Financial totals (subtotal, tax, total, discounts)
- Payment information (method, reference, card last 4)
- Customer information (if on receipt)

### Line Item Fields
- Product information (SKU, UPC, product code)
- Quantity and pricing (quantity, unit price, line total)
- Product details (description, category, brand)
- Tax information (tax rate, tax amount per line)
- Project tracking (CSI code, phase, location)

## Testing

After adding fields:

1. **Test Migration**
   ```bash
   php artisan migrate:rollback
   php artisan migrate
   ```

2. **Test Extraction**
   - Process sample receipt through OCR
   - Verify field is extracted correctly
   - Verify field is saved to database

3. **Test Review Interface**
   - Verify field appears in review interface
   - Verify field can be edited if needed

## Documentation

After adding fields:

1. Update `field_discovery.md` - Mark field as added
2. Update template documentation - Document field extraction
3. Update API documentation - Document new field in responses

## Rollback

If migration needs to be rolled back:

```bash
php artisan migrate:rollback --step=1
```

Then:
1. Remove field from model `$fillable`
2. Remove field from Filament resource
3. Update template to not extract field (or handle gracefully)

## Notes

- Always use nullable fields initially (can make required later)
- Add indexes for frequently queried fields
- Consider field length limits based on actual receipt data
- Test with multiple receipt samples before finalizing
- Document field purpose and format in code comments
