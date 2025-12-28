"""
Document Extractor
Extracts structured data from documents using OCR and format templates.
"""

from typing import Dict, Any, Optional
from ..ocr_processor import OCRProcessor
from ..confidence_scorer import ConfidenceScorer
from ..formats.base_format import BaseDocumentFormat
from ..utils.text_utils import TextUtils


class DocumentExtractor:
    """Extracts structured document data from images."""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize receipt extractor.
        
        Args:
            tesseract_cmd: Path to tesseract executable
        """
        self.ocr_processor = OCRProcessor(tesseract_cmd)
        self.confidence_scorer = ConfidenceScorer()
    
    def extract(self, image_path: str) -> Dict[str, Any]:
        """
        Extract structured data from document image.
        
        Args:
            image_path: Path to document image
            
        Returns:
            Dictionary with extraction results:
            {
                'vendor': str,
                'format_detected': str,
                'confidence': float,
                'confidence_level': str,
                'fields': {
                    'receipt_date': str,
                    'receipt_number': str,
                    'line_items': list,
                    'subtotal': Decimal,
                    'tax_amount': Decimal,
                    'total_amount': Decimal,
                    ...
                },
                'ocr_text': str,
                'ocr_data': dict,
            }
        """
        # Step 1: Preprocess and run OCR
        ocr_result = self.ocr_processor.process_image(image_path)
        ocr_text = ocr_result.get('text', '')
        ocr_data = ocr_result.get('data', {})
        
        # Step 2: Detect format
        format_template, format_confidence = self.ocr_processor.detect_format(ocr_text)
        
        if not format_template:
            # No format detected - return minimal result
            return {
                'vendor': None,
                'format_detected': None,
                'confidence': 0.0,
                'confidence_level': 'low',
                'fields': {},
                'ocr_text': ocr_text,
                'ocr_data': ocr_data,
                'error': 'No matching format detected',
            }
        
        # Step 3: Extract fields using format template
        extracted_fields = format_template.extract_fields(ocr_text)
        
        # Add format detection confidence to fields
        extracted_fields['format_detection_confidence'] = format_confidence
        extracted_fields['vendor'] = format_template.vendor_name
        extracted_fields['format'] = format_template.format_id
        
        # Step 4: Calculate confidence score
        confidence = self.confidence_scorer.calculate_confidence(
            ocr_data,
            extracted_fields,
            format_template
        )
        
        confidence_level = self.confidence_scorer.get_confidence_level(confidence)
        
        # Step 5: Prepare result
        result = {
            'vendor': format_template.vendor_name,
            'format_detected': format_template.format_id,
            'confidence': confidence,
            'confidence_level': confidence_level,
            'fields': extracted_fields,
            'ocr_text': ocr_text,
            'ocr_data': {
                'conf': ocr_result.get('conf', []),
                'text_length': len(ocr_text),
            },
        }
        
        return result
    
    def extract_fields_only(self, image_path: str) -> Dict[str, Any]:
        """
        Extract only the structured fields (without OCR metadata).
        
        Args:
            image_path: Path to document image
            
        Returns:
            Dictionary with extracted fields
        """
        result = self.extract(image_path)
        return result.get('fields', {})
