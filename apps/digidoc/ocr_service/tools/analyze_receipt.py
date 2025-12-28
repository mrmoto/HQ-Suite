#!/usr/bin/env python3
"""
Receipt Analysis Tool
Analyzes receipt images and extracts OCR text for template development.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import ocr_service modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ocr_service.ocr_processor import OCRProcessor
from ocr_service.utils.image_preprocessing import ImagePreprocessor


def analyze_receipt(image_path: str, output_dir: str = None):
    """
    Analyze a receipt image and extract OCR text with structure.
    
    Args:
        image_path: Path to receipt image
        output_dir: Directory to save analysis output (default: receipt_samples/)
    """
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        return
    
    # Set default output directory
    if output_dir is None:
        project_root = Path(__file__).parent.parent.parent
        output_dir = project_root / "receipt_samples"
        output_dir.mkdir(exist_ok=True)
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
    
    print(f"Analyzing receipt: {image_path}")
    print("=" * 80)
    
    # Initialize OCR processor
    processor = OCRProcessor()
    
    # Process image
    try:
        ocr_result = processor.process_image(image_path)
        ocr_text = ocr_result.get('text', '')
        ocr_data = ocr_result.get('data', {})
        confidences = ocr_result.get('conf', [])
    except Exception as e:
        print(f"Error processing image: {e}")
        return
    
    # Generate output filename
    image_name = Path(image_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_base = output_dir / f"{image_name}_{timestamp}"
    
    # Save raw OCR text
    txt_file = output_base.with_suffix('.txt')
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(ocr_text)
    print(f"\n✓ OCR text saved to: {txt_file}")
    
    # Save structured OCR data
    json_file = output_base.with_suffix('.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'image_path': image_path,
            'timestamp': timestamp,
            'text': ocr_text,
            'confidence_scores': confidences,
            'average_confidence': sum(confidences) / len(confidences) if confidences else 0,
            'word_count': len(ocr_text.split()),
            'line_count': len(ocr_text.split('\n')),
            'data': ocr_data,
        }, f, indent=2, default=str)
    print(f"✓ Structured data saved to: {json_file}")
    
    # Display formatted output
    print("\n" + "=" * 80)
    print("OCR TEXT OUTPUT")
    print("=" * 80)
    print()
    
    # Show text with line numbers
    lines = ocr_text.split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip():  # Only show non-empty lines
            print(f"{i:4d} | {line}")
    
    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Total lines: {len(lines)}")
    print(f"Non-empty lines: {sum(1 for line in lines if line.strip())}")
    print(f"Word count: {len(ocr_text.split())}")
    print(f"Character count: {len(ocr_text)}")
    if confidences:
        avg_conf = sum(confidences) / len(confidences)
        print(f"Average confidence: {avg_conf:.2f}%")
        print(f"Min confidence: {min(confidences):.2f}%")
        print(f"Max confidence: {max(confidences):.2f}%")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nNext steps:")
    print(f"1. Review OCR text in: {txt_file}")
    print(f"2. Identify field patterns (date, receipt number, totals, line items)")
    print(f"3. Document patterns in: {output_dir}/patterns.md")
    print(f"4. Update template with identified patterns")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_receipt.py <image_path> [output_dir]")
        print("\nExample:")
        print("  python3 analyze_receipt.py receipt1.jpg")
        print("  python3 analyze_receipt.py receipt1.jpg receipt_samples/")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyze_receipt(image_path, output_dir)
