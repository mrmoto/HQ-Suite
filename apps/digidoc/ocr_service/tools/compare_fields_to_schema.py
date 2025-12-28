#!/usr/bin/env python3
"""
Field Comparison Tool
Compares extracted fields from receipts to database schema to identify missing fields.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any


# Known schema fields from migrations
PURCHASE_RECEIPT_FIELDS = {
    'receipt_date', 'receipt_number', 'po_number',
    'subtotal', 'tax_amount', 'total_amount',
    'payment_method', 'payment_reference',
    'receipt_image_path', 'receipt_image_thumbnail',
    'notes', 'status',
    'purchase_date', 'purchased_by_user_id',
    'entered_by_user_id', 'approved_by_user_id', 'approved_at', 'reimbursed_at',
    # Foreign keys and metadata (not extracted from OCR)
    'id', 'project_id', 'vendor_id', 'created_at', 'updated_at', 'deleted_at',
}

PURCHASE_RECEIPT_LINE_FIELDS = {
    'line_number', 'product_id', 'vendor_sku',
    'description', 'quantity', 'unit_price', 'line_total',
    'tax_rate_applied', 'csi_code_id',
    'project_phase', 'notes',
    # Foreign keys and metadata
    'id', 'receipt_id', 'created_at', 'updated_at',
}

# Common field mappings (OCR field name -> schema field name)
FIELD_MAPPINGS = {
    # Receipt fields
    'date': 'receipt_date',
    'receipt_date': 'receipt_date',
    'invoice_date': 'receipt_date',
    'receipt_number': 'receipt_number',
    'invoice_number': 'receipt_number',
    'receipt_num': 'receipt_number',
    'inv_number': 'receipt_number',
    'total': 'total_amount',
    'total_amount': 'total_amount',
    'amount': 'total_amount',
    'grand_total': 'total_amount',
    'subtotal': 'subtotal',
    'tax': 'tax_amount',
    'tax_amount': 'tax_amount',
    'sales_tax': 'tax_amount',
    'payment_method': 'payment_method',
    'payment_type': 'payment_method',
    'paid_with': 'payment_method',
    # Line item fields
    'item_description': 'description',
    'description': 'description',
    'item': 'description',
    'product': 'description',
    'qty': 'quantity',
    'quantity': 'quantity',
    'amount': 'quantity',
    'unit_price': 'unit_price',
    'price': 'unit_price',
    'unit_cost': 'unit_price',
    'line_total': 'line_total',
    'extended_price': 'line_total',
    'line_amount': 'line_total',
}


def normalize_field_name(field_name: str) -> str:
    """Normalize field name for comparison."""
    # Convert to lowercase, remove special chars
    normalized = re.sub(r'[^a-z0-9_]', '_', field_name.lower())
    # Remove multiple underscores
    normalized = re.sub(r'_+', '_', normalized)
    return normalized.strip('_')


def map_to_schema_field(field_name: str) -> str:
    """Map OCR field name to schema field name."""
    normalized = normalize_field_name(field_name)
    return FIELD_MAPPINGS.get(normalized, normalized)


def compare_fields(extracted_fields: Dict[str, Any], line_items: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Compare extracted fields to schema.
    
    Args:
        extracted_fields: Dictionary of extracted receipt-level fields
        line_items: List of line item dictionaries
        
    Returns:
        Dictionary with comparison results
    """
    # Normalize extracted field names
    receipt_fields_found = set()
    receipt_fields_missing = []
    
    for field_name, value in extracted_fields.items():
        if value is None or value == '':
            continue
        
        mapped_name = map_to_schema_field(field_name)
        receipt_fields_found.add(mapped_name)
        
        if mapped_name not in PURCHASE_RECEIPT_FIELDS:
            receipt_fields_missing.append({
                'ocr_field': field_name,
                'mapped_field': mapped_name,
                'value': str(value)[:50],  # Truncate for display
                'type': type(value).__name__,
            })
    
    # Check line items
    line_fields_found = set()
    line_fields_missing = []
    
    if line_items:
        for item in line_items:
            for field_name, value in item.items():
                if value is None or value == '':
                    continue
                
                mapped_name = map_to_schema_field(field_name)
                line_fields_found.add(mapped_name)
                
                if mapped_name not in PURCHASE_RECEIPT_LINE_FIELDS:
                    # Check if we already have this field
                    if not any(m['mapped_field'] == mapped_name for m in line_fields_missing):
                        line_fields_missing.append({
                            'ocr_field': field_name,
                            'mapped_field': mapped_name,
                            'value': str(value)[:50],
                            'type': type(value).__name__,
                        })
    
    return {
        'receipt_fields': {
            'found': sorted(receipt_fields_found),
            'missing': receipt_fields_missing,
            'schema_fields': sorted(PURCHASE_RECEIPT_FIELDS),
        },
        'line_item_fields': {
            'found': sorted(line_fields_found),
            'missing': line_fields_missing,
            'schema_fields': sorted(PURCHASE_RECEIPT_LINE_FIELDS),
        },
        'summary': {
            'receipt_fields_found': len(receipt_fields_found),
            'receipt_fields_missing': len(receipt_fields_missing),
            'line_fields_found': len(line_fields_found),
            'line_fields_missing': len(line_fields_missing),
        }
    }


def analyze_extraction_result(json_file: str, output_file: str = None):
    """
    Analyze extraction result JSON and compare to schema.
    
    Args:
        json_file: Path to extraction result JSON (from DocumentExtractor)
        output_file: Path to save comparison results
    """
    if not Path(json_file).exists():
        print(f"Error: File not found: {json_file}")
        return
    
    # Load extraction result
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract fields
    fields = data.get('fields', {})
    line_items = fields.get('line_items', [])
    
    print(f"Analyzing extraction result: {json_file}")
    print("=" * 80)
    
    # Compare to schema
    comparison = compare_fields(fields, line_items)
    
    # Save results
    if output_file is None:
        output_file = Path(json_file).parent / f"{Path(json_file).stem}_schema_comparison.json"
    else:
        output_file = Path(output_file)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, default=str)
    
    print(f"\n✓ Comparison saved to: {output_file}")
    
    # Display results
    print("\n" + "=" * 80)
    print("SCHEMA COMPARISON RESULTS")
    print("=" * 80)
    
    print(f"\nReceipt-Level Fields:")
    print(f"  Found in schema: {comparison['summary']['receipt_fields_found']}")
    print(f"  Missing from schema: {comparison['summary']['receipt_fields_missing']}")
    
    if comparison['receipt_fields']['missing']:
        print("\n  Missing fields:")
        for field in comparison['receipt_fields']['missing']:
            print(f"    - {field['ocr_field']} -> {field['mapped_field']} ({field['type']})")
            print(f"      Example value: {field['value']}")
    
    print(f"\nLine Item Fields:")
    print(f"  Found in schema: {comparison['summary']['line_fields_found']}")
    print(f"  Missing from schema: {comparison['summary']['line_fields_missing']}")
    
    if comparison['line_item_fields']['missing']:
        print("\n  Missing fields:")
        for field in comparison['line_item_fields']['missing']:
            print(f"    - {field['ocr_field']} -> {field['mapped_field']} ({field['type']})")
            print(f"      Example value: {field['value']}")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    if comparison['receipt_fields']['missing'] or comparison['line_item_fields']['missing']:
        print("1. Review missing fields in comparison JSON")
        print("2. Document fields in receipt_samples/field_discovery.md")
        print("3. Create migrations for new fields")
        print("4. Update models and Filament resources")
    else:
        print("✓ All extracted fields exist in schema!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 compare_fields_to_schema.py <extraction_result.json> [output_file]")
        print("\nExample:")
        print("  python3 compare_fields_to_schema.py receipt_samples/extraction_result.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyze_extraction_result(json_file, output_file)
