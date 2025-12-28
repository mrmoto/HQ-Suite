#!/usr/bin/env python3
"""
Pattern Documentation Tool
Helps identify and document field patterns from OCR text.
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Any


def find_date_patterns(text: str) -> List[Dict[str, Any]]:
    """Find potential date patterns in text."""
    patterns = [
        (r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', 'MM/DD/YYYY or MM-DD-YYYY'),
        (r'\d{4}[/-]\d{1,2}[/-]\d{1,2}', 'YYYY/MM/DD or YYYY-MM-DD'),
        (r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b', 'Month DD, YYYY'),
        (r'\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b', 'DD Month YYYY'),
    ]
    
    matches = []
    for pattern, description in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matches.append({
                'pattern': pattern,
                'description': description,
                'match': match.group(0),
                'position': match.start(),
                'line': text[:match.start()].count('\n') + 1,
            })
    
    return matches


def find_currency_patterns(text: str) -> List[Dict[str, Any]]:
    """Find potential currency/amount patterns."""
    patterns = [
        (r'\$[\d,]+\.\d{2}', 'Dollar amount with cents'),
        (r'[\d,]+\.\d{2}', 'Decimal amount (may be currency)'),
        (r'total[\s:]*[\$]?([\d,]+\.\d{2})', 'Total amount'),
        (r'subtotal[\s:]*[\$]?([\d,]+\.\d{2})', 'Subtotal amount'),
        (r'tax[\s:]*[\$]?([\d,]+\.\d{2})', 'Tax amount'),
    ]
    
    matches = []
    for pattern, description in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matches.append({
                'pattern': pattern,
                'description': description,
                'match': match.group(0),
                'position': match.start(),
                'line': text[:match.start()].count('\n') + 1,
            })
    
    return matches


def find_receipt_number_patterns(text: str) -> List[Dict[str, Any]]:
    """Find potential receipt/invoice number patterns."""
    patterns = [
        (r'(?:receipt|invoice|inv|#)[\s:]*([A-Z0-9\-]+)', 'Receipt/Invoice number'),
        (r'#[\s]*([A-Z0-9\-]+)', 'Number with # prefix'),
        (r'(?:order|po|p\.o\.)[\s:]*([A-Z0-9\-]+)', 'Order/PO number'),
    ]
    
    matches = []
    for pattern, description in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matches.append({
                'pattern': pattern,
                'description': description,
                'match': match.group(0),
                'captured': match.group(1) if match.groups() else None,
                'position': match.start(),
                'line': text[:match.start()].count('\n') + 1,
            })
    
    return matches


def find_line_item_patterns(text: str) -> List[Dict[str, Any]]:
    """Find potential line item patterns."""
    lines = text.split('\n')
    items = []
    
    # Pattern: quantity description price
    pattern1 = re.compile(r'(\d+(?:\.\d+)?)\s+([A-Za-z0-9\s\-\.]+?)\s+[\$]?([\d,]+\.\d{2})', re.IGNORECASE)
    
    # Pattern: description quantity x price
    pattern2 = re.compile(r'([A-Za-z0-9\s\-\.]+?)\s+(\d+(?:\.\d+)?)\s*[xX]\s*[\$]?([\d,]+\.\d{2})', re.IGNORECASE)
    
    # Pattern: description price (quantity = 1)
    pattern3 = re.compile(r'([A-Za-z0-9\s\-\.]{5,}?)\s+[\$]?([\d,]+\.\d{2})$', re.IGNORECASE)
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or len(line) < 5:
            continue
        
        # Skip header/footer lines
        if any(skip in line.lower() for skip in ['receipt', 'invoice', 'total', 'subtotal', 'tax', 'date', 'thank']):
            continue
        
        # Try pattern 1
        match = pattern1.search(line)
        if match:
            items.append({
                'line_number': line_num,
                'line_text': line,
                'pattern': 'quantity description price',
                'quantity': match.group(1),
                'description': match.group(2).strip(),
                'price': match.group(3),
            })
            continue
        
        # Try pattern 2
        match = pattern2.search(line)
        if match:
            items.append({
                'line_number': line_num,
                'line_text': line,
                'pattern': 'description quantity x price',
                'description': match.group(1).strip(),
                'quantity': match.group(2),
                'price': match.group(3),
            })
            continue
        
        # Try pattern 3
        match = pattern3.search(line)
        if match:
            items.append({
                'line_number': line_num,
                'line_text': line,
                'pattern': 'description price (qty=1)',
                'description': match.group(1).strip(),
                'quantity': '1',
                'price': match.group(2),
            })
    
    return items


def analyze_patterns(text_file: str, output_file: str = None):
    """
    Analyze OCR text file and identify patterns.
    
    Args:
        text_file: Path to OCR text file
        output_file: Path to save pattern analysis (default: text_file with .patterns.json)
    """
    if not os.path.exists(text_file):
        print(f"Error: File not found: {text_file}")
        return
    
    # Read OCR text
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"Analyzing patterns in: {text_file}")
    print("=" * 80)
    
    # Find patterns
    dates = find_date_patterns(text)
    currencies = find_currency_patterns(text)
    receipt_numbers = find_receipt_number_patterns(text)
    line_items = find_line_item_patterns(text)
    
    # Compile results
    results = {
        'source_file': text_file,
        'dates': dates,
        'currencies': currencies,
        'receipt_numbers': receipt_numbers,
        'line_items': line_items,
        'summary': {
            'date_matches': len(dates),
            'currency_matches': len(currencies),
            'receipt_number_matches': len(receipt_numbers),
            'line_item_matches': len(line_items),
        }
    }
    
    # Save results
    if output_file is None:
        output_file = Path(text_file).with_suffix('.patterns.json')
    else:
        output_file = Path(output_file)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✓ Pattern analysis saved to: {output_file}")
    
    # Display summary
    print("\n" + "=" * 80)
    print("PATTERN ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"\nDates found: {len(dates)}")
    if dates:
        print("  Examples:")
        for date in dates[:3]:
            print(f"    Line {date['line']}: {date['match']} ({date['description']})")
    
    print(f"\nCurrency amounts found: {len(currencies)}")
    if currencies:
        print("  Examples:")
        for curr in currencies[:3]:
            print(f"    Line {curr['line']}: {curr['match']} ({curr['description']})")
    
    print(f"\nReceipt numbers found: {len(receipt_numbers)}")
    if receipt_numbers:
        print("  Examples:")
        for num in receipt_numbers[:3]:
            print(f"    Line {num['line']}: {num['match']} ({num['description']})")
    
    print(f"\nLine items found: {len(line_items)}")
    if line_items:
        print("  Examples:")
        for item in line_items[:3]:
            print(f"    Line {item['line_number']}: {item['pattern']}")
            print(f"      Description: {item.get('description', 'N/A')}")
            print(f"      Quantity: {item.get('quantity', 'N/A')}")
            print(f"      Price: {item.get('price', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Review pattern matches in the JSON file")
    print("2. Verify patterns are correct")
    print("3. Document confirmed patterns in patterns.md")
    print("4. Update template with verified patterns")


if __name__ == "__main__":
    import os
    
    if len(sys.argv) < 2:
        print("Usage: python3 document_patterns.py <ocr_text_file> [output_file]")
        print("\nExample:")
        print("  python3 document_patterns.py receipt_samples/receipt1_20241218.txt")
        print("  python3 document_patterns.py receipt_samples/receipt1_20241218.txt receipt1.patterns.json")
        sys.exit(1)
    
    text_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyze_patterns(text_file, output_file)
