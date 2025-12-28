#!/usr/bin/env python3
"""
Verbose Field Extraction Tool

Provides human-readable output showing the field extraction process step-by-step.
Shows what fields are found in OCR text, what template expects, and what was extracted.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractors.document_extractor import DocumentExtractor
from ocr_processor import OCRProcessor
from database.models import CachedTemplate, get_session
from tasks.matching_task import match_template
from utils.text_utils import TextUtils
import json
from typing import Dict, Any, List, Set


def print_section(title: str, char: str = "="):
    """Print a section header."""
    print(f"\n{char * 60}")
    print(f"{title}")
    print(f"{char * 60}")


def print_step(step_num: int, description: str):
    """Print a process step."""
    print(f"\n[Step {step_num}] {description}")
    print("-" * 60)


def analyze_ocr_text_for_fields(ocr_text: str) -> Dict[str, Any]:
    """
    Analyze OCR text to find potential field values.
    Returns dictionary of found field indicators.
    """
    text_lower = ocr_text.lower()
    found_indicators = {
        'dates': [],
        'currency_amounts': [],
        'numbers': [],
        'receipt_indicators': [],
        'vendor_indicators': [],
    }
    
    # Look for dates
    dates = TextUtils.extract_date(ocr_text)
    if dates:
        found_indicators['dates'].append(str(dates))
    
    # Look for currency amounts
    currency_pattern = r'\$[\d,]+\.?\d*'
    import re
    currency_matches = re.findall(currency_pattern, ocr_text)
    found_indicators['currency_amounts'] = list(set(currency_matches[:10]))  # Limit to 10
    
    # Look for receipt indicators
    receipt_keywords = ['receipt', 'invoice', 'total', 'subtotal', 'tax', 'date', 'number']
    for keyword in receipt_keywords:
        if keyword in text_lower:
            found_indicators['receipt_indicators'].append(keyword)
    
    # Look for vendor indicators
    vendor_keywords = ['mead', 'clark', 'lumber', 'vendor', 'company']
    for keyword in vendor_keywords:
        if keyword in text_lower:
            found_indicators['vendor_indicators'].append(keyword)
    
    return found_indicators


def get_template_field_info(template: CachedTemplate) -> Dict[str, Any]:
    """Extract field information from template."""
    info = {
        'template_id': template.template_id,
        'format_name': template.format_name,
        'vendor': template.vendor,
        'document_type': template.document_type,
        'field_mappings': template.field_mappings or {},
        'template_data': template.template_data or {},
    }
    
    # Extract required/optional fields from template_data if available
    if isinstance(info['template_data'], dict):
        info['required_fields'] = info['template_data'].get('required_fields', [])
        info['optional_fields'] = info['template_data'].get('optional_fields', [])
    else:
        info['required_fields'] = []
        info['optional_fields'] = []
    
    # If field_mappings exist, use those keys as expected fields
    if info['field_mappings']:
        if not info['required_fields']:
            # Assume all mapped fields are expected
            info['expected_fields'] = list(info['field_mappings'].keys())
        else:
            info['expected_fields'] = info['required_fields'] + info['optional_fields']
    else:
        info['expected_fields'] = info['required_fields'] + info['optional_fields']
    
    return info


def format_field_value(value: Any, max_length: int = 50) -> str:
    """Format a field value for display."""
    if value is None:
        return "<None>"
    if isinstance(value, (list, dict)):
        return json.dumps(value)[:max_length]
    str_value = str(value)
    if len(str_value) > max_length:
        return str_value[:max_length] + "..."
    return str_value


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python3 verbose_field_extraction.py <image_path> [calling_app_id]")
        print("  Example: python3 verbose_field_extraction.py receipt.jpg default")
        sys.exit(1)
    
    image_path = sys.argv[1]
    calling_app_id = sys.argv[2] if len(sys.argv) > 2 else "default"
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    print_section("Field Extraction Process - Verbose Output")
    print(f"Image: {image_path}")
    print(f"Calling App ID: {calling_app_id}")
    
    # Step 1: OCR Processing
    print_step(1, "OCR Processing")
    print("Running OCR on image...")
    ocr_processor = OCRProcessor()
    try:
        ocr_result = ocr_processor.process_image(image_path)
        ocr_text = ocr_result.get('text', '')
        ocr_data = ocr_result.get('data', {})
        ocr_confidences = ocr_result.get('conf', [])
        
        print(f"✓ OCR completed")
        print(f"  Text length: {len(ocr_text)} characters")
        if ocr_confidences:
            avg_confidence = sum(ocr_confidences) / len(ocr_confidences) if ocr_confidences else 0.0
            print(f"  Average OCR confidence: {avg_confidence:.2%}")
        
        # Analyze OCR text for field indicators
        print("\n  Analyzing OCR text for field indicators...")
        field_indicators = analyze_ocr_text_for_fields(ocr_text)
        
        print(f"  Found {len(field_indicators['dates'])} date(s): {field_indicators['dates']}")
        print(f"  Found {len(field_indicators['currency_amounts'])} currency amount(s): {field_indicators['currency_amounts'][:5]}")
        print(f"  Found {len(field_indicators['receipt_indicators'])} receipt indicator(s): {field_indicators['receipt_indicators']}")
        if field_indicators['vendor_indicators']:
            print(f"  Found {len(field_indicators['vendor_indicators'])} vendor indicator(s): {field_indicators['vendor_indicators']}")
        
    except Exception as e:
        print(f"✗ OCR processing failed: {e}")
        sys.exit(1)
    
    # Step 2: Template Matching
    print_step(2, "Template Matching")
    print("Matching document to templates...")
    
    # Generate a temporary queue_item_id for matching
    import uuid
    queue_item_id = str(uuid.uuid4())
    
    try:
        match_result = match_template(image_path, queue_item_id, calling_app_id)
        match_score = match_result.get('match_score', 0.0)
        matched_template_id = match_result.get('matched_template_id')
        template_name = match_result.get('template_name')
        
        print(f"✓ Template matching completed")
        print(f"  Match score: {match_score:.2%}")
        
        if matched_template_id:
            print(f"  Matched template ID: {matched_template_id}")
            print(f"  Template name: {template_name}")
            
            # Load template details
            session = get_session()
            try:
                template = session.query(CachedTemplate).filter_by(
                    template_id=matched_template_id,
                    calling_app_id=calling_app_id
                ).first()
                
                if template:
                    template_info = get_template_field_info(template)
                    print(f"\n  Template Details:")
                    print(f"    Vendor: {template_info.get('vendor', 'N/A')}")
                    print(f"    Document Type: {template_info.get('document_type', 'N/A')}")
                    print(f"    Format: {template_info.get('format_name', 'N/A')}")
                    
                    expected_fields = template_info.get('expected_fields', [])
                    required_fields = template_info.get('required_fields', [])
                    optional_fields = template_info.get('optional_fields', [])
                    
                    print(f"\n  Template shows {len(expected_fields)} field(s) to attempt matching:")
                    if required_fields:
                        print(f"    Required fields ({len(required_fields)}): {', '.join(required_fields)}")
                    if optional_fields:
                        print(f"    Optional fields ({len(optional_fields)}): {', '.join(optional_fields)}")
                    if template_info.get('field_mappings'):
                        print(f"    Field mappings available: {len(template_info['field_mappings'])} mapping(s)")
                else:
                    print(f"  ⚠ Template not found in database")
                    template = None
            finally:
                session.close()
        else:
            print(f"  ⚠ No template matched")
            template = None
            
    except Exception as e:
        print(f"✗ Template matching failed: {e}")
        import traceback
        traceback.print_exc()
        template = None
    
    # Step 3: Format Detection (using DocumentExtractor's method)
    print_step(3, "Format Detection")
    print("Detecting document format...")
    
    try:
        format_template, format_confidence = ocr_processor.detect_format(ocr_text)
        
        if format_template:
            print(f"✓ Format detected")
            print(f"  Format: {format_template.format_id}")
            print(f"  Vendor: {format_template.vendor_name}")
            print(f"  Confidence: {format_confidence:.2%}")
            
            required_fields = format_template.get_required_fields()
            optional_fields = format_template.get_optional_fields()
            
            print(f"\n  Format template expects:")
            print(f"    Required fields ({len(required_fields)}): {', '.join(required_fields)}")
            if optional_fields:
                print(f"    Optional fields ({len(optional_fields)}): {', '.join(optional_fields)}")
        else:
            print(f"  ⚠ No format detected")
            format_template = None
            
    except Exception as e:
        print(f"✗ Format detection failed: {e}")
        format_template = None
    
    # Step 4: Field Extraction
    print_step(4, "Field Extraction")
    print("Extracting fields from document...")
    
    try:
        extractor = DocumentExtractor()
        extraction_result = extractor.extract(image_path)
        
        extracted_fields = extraction_result.get('fields', {})
        confidence = extraction_result.get('confidence', 0.0)
        confidence_level = extraction_result.get('confidence_level', 'unknown')
        
        print(f"✓ Field extraction completed")
        print(f"  Overall confidence: {confidence:.2%} ({confidence_level})")
        print(f"  Vendor: {extraction_result.get('vendor', 'N/A')}")
        print(f"  Format detected: {extraction_result.get('format_detected', 'N/A')}")
        
        # Count extracted fields
        non_none_fields = {k: v for k, v in extracted_fields.items() if v is not None and v != ''}
        print(f"\n  Found {len(non_none_fields)} field(s) with values (out of {len(extracted_fields)} total):")
        
        # Show extracted fields
        if non_none_fields:
            print("\n  Extracted Fields:")
            for field_name, field_value in sorted(non_none_fields.items()):
                print(f"    • {field_name}: {format_field_value(field_value)}")
        
        # Show missing/empty fields
        empty_fields = {k: v for k, v in extracted_fields.items() if v is None or v == ''}
        if empty_fields:
            print(f"\n  Fields with no value ({len(empty_fields)}):")
            for field_name in sorted(empty_fields.keys()):
                print(f"    • {field_name}: <empty>")
        
        # Compare with template expectations if available
        if format_template:
            required_fields = format_template.get_required_fields()
            missing_required = [f for f in required_fields if f not in non_none_fields]
            
            if missing_required:
                print(f"\n  ⚠ Missing required fields ({len(missing_required)}):")
                for field_name in missing_required:
                    print(f"    • {field_name}")
            else:
                print(f"\n  ✓ All required fields extracted")
        
    except Exception as e:
        print(f"✗ Field extraction failed: {e}")
        import traceback
        traceback.print_exc()
        extracted_fields = {}
    
    # Step 5: Summary
    print_section("Summary", "=")
    
    print(f"OCR Text Length: {len(ocr_text)} characters")
    if 'match_score' in locals():
        print(f"Template Match Score: {match_score:.2%}")
    if 'confidence' in locals():
        print(f"Extraction Confidence: {confidence:.2%} ({confidence_level})")
    if 'non_none_fields' in locals():
        print(f"Fields Extracted: {len(non_none_fields)}")
    if 'format_template' in locals() and format_template:
        required_fields = format_template.get_required_fields()
        if required_fields:
            missing = [f for f in required_fields if f not in non_none_fields]
            print(f"Required Fields Status: {len(required_fields) - len(missing)}/{len(required_fields)} extracted")
    
    print("\n" + "=" * 60)
    print("Process complete")


if __name__ == "__main__":
    main()

