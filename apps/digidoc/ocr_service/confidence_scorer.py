"""
Confidence Scoring System
Calculates confidence scores for OCR extraction results.
"""

from typing import Dict, Any, List
from .formats.base_format import BaseDocumentFormat
from .utils.text_utils import TextUtils


class ConfidenceScorer:
    """Calculates confidence scores for document OCR extraction."""
    
    # Confidence thresholds
    HIGH_THRESHOLD = 0.85  # Auto-process
    MEDIUM_THRESHOLD = 0.70  # Quick review
    LOW_THRESHOLD = 0.0  # Full manual review
    
    def __init__(self):
        self.weights = {
            'ocr_quality': 0.30,  # OCR text quality
            'field_extraction': 0.40,  # Field extraction success rate
            'pattern_matching': 0.20,  # Pattern matching confidence
            'data_validation': 0.10,  # Data validation (dates, numbers)
        }
    
    def calculate_confidence(
        self,
        ocr_data: Dict[str, Any],
        extracted_fields: Dict[str, Any],
        format_template: BaseDocumentFormat
    ) -> float:
        """
        Calculate overall confidence score.
        
        Args:
            ocr_data: Tesseract OCR result data
            extracted_fields: Extracted receipt fields
            format_template: Format template used for extraction
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        scores = {}
        
        # 1. OCR Quality Score
        scores['ocr_quality'] = self._calculate_ocr_quality(ocr_data)
        
        # 2. Field Extraction Score
        scores['field_extraction'] = self._calculate_field_extraction_score(
            extracted_fields,
            format_template
        )
        
        # 3. Pattern Matching Score
        scores['pattern_matching'] = self._calculate_pattern_matching_score(
            extracted_fields,
            format_template
        )
        
        # 4. Data Validation Score
        scores['data_validation'] = self._calculate_validation_score(
            extracted_fields
        )
        
        # Weighted average
        total_confidence = sum(
            scores[key] * self.weights[key]
            for key in self.weights
        )
        
        return min(1.0, max(0.0, total_confidence))
    
    def _calculate_ocr_quality(self, ocr_data: Dict[str, Any]) -> float:
        """
        Calculate OCR text quality score.
        
        Uses Tesseract's per-word confidence scores.
        """
        if not ocr_data:
            return 0.0
        
        # Get average confidence from Tesseract
        if 'conf' in ocr_data:
            confidences = [float(conf) for conf in ocr_data['conf'] if conf != '-1']
            if confidences:
                avg_conf = sum(confidences) / len(confidences)
                # Normalize from 0-100 to 0-1
                return avg_conf / 100.0
        
        # Fallback: check if text was extracted
        if 'text' in ocr_data and ocr_data['text']:
            # If text exists but no confidence data, assume medium quality
            return 0.6
        
        return 0.0
    
    def _calculate_field_extraction_score(
        self,
        extracted_fields: Dict[str, Any],
        format_template: BaseDocumentFormat
    ) -> float:
        """
        Calculate score based on field extraction success rate.
        """
        if not format_template.required_fields:
            return 1.0
        
        # Get extraction rate from template
        extraction_rate = format_template.get_field_extraction_rate(extracted_fields)
        
        # Bonus for extracting optional fields
        optional_extracted = sum(
            1 for field in format_template.optional_fields
            if field in extracted_fields and extracted_fields[field] is not None
        )
        
        optional_bonus = 0.0
        if format_template.optional_fields:
            optional_bonus = (optional_extracted / len(format_template.optional_fields)) * 0.1
        
        return min(1.0, extraction_rate + optional_bonus)
    
    def _calculate_pattern_matching_score(
        self,
        extracted_fields: Dict[str, Any],
        format_template: BaseDocumentFormat
    ) -> float:
        """
        Calculate score based on pattern matching confidence.
        
        This uses the format detection confidence if available.
        """
        # If format detection was done, use that confidence
        if 'format_detection_confidence' in extracted_fields:
            return extracted_fields['format_detection_confidence']
        
        # Otherwise, base on whether required fields were found
        if format_template.required_fields:
            required_found = sum(
                1 for field in format_template.required_fields
                if field in extracted_fields and extracted_fields[field] is not None
            )
            return required_found / len(format_template.required_fields)
        
        return 0.8  # Default if no required fields defined
    
    def _calculate_validation_score(self, extracted_fields: Dict[str, Any]) -> float:
        """
        Calculate score based on data validation.
        
        Validates dates, numbers, and other field formats.
        """
        validation_score = 1.0
        issues = 0
        
        # Validate date format
        if 'receipt_date' in extracted_fields and extracted_fields['receipt_date']:
            date_str = extracted_fields['receipt_date']
            # Check if it's a valid date format (YYYY-MM-DD)
            if not self._is_valid_date_format(date_str):
                issues += 1
        
        # Validate currency amounts
        currency_fields = ['total_amount', 'subtotal', 'tax_amount']
        for field in currency_fields:
            if field in extracted_fields and extracted_fields[field] is not None:
                value = extracted_fields[field]
                if not self._is_valid_currency(value):
                    issues += 1
        
        # Validate line items
        if 'line_items' in extracted_fields and extracted_fields['line_items']:
            items = extracted_fields['line_items']
            if isinstance(items, list):
                for item in items:
                    if not self._is_valid_line_item(item):
                        issues += 1
        
        # Calculate score (reduce by 0.1 per issue, minimum 0.0)
        validation_score = max(0.0, 1.0 - (issues * 0.1))
        
        return validation_score
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """Check if date string is in valid format (YYYY-MM-DD)."""
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        return bool(re.match(pattern, date_str))
    
    def _is_valid_currency(self, value: Any) -> bool:
        """Check if value is a valid currency amount."""
        from decimal import Decimal, InvalidOperation
        try:
            if isinstance(value, (int, float, Decimal)):
                return float(value) >= 0
            if isinstance(value, str):
                Decimal(value)
                return True
        except (InvalidOperation, ValueError):
            return False
        return False
    
    def _is_valid_line_item(self, item: Dict[str, Any]) -> bool:
        """Check if line item has required fields."""
        required = ['description', 'line_total']
        return all(field in item and item[field] is not None for field in required)
    
    def get_confidence_level(self, confidence: float) -> str:
        """
        Get confidence level category.
        
        Args:
            confidence: Confidence score (0.0 to 1.0)
            
        Returns:
            'high', 'medium', or 'low'
        """
        if confidence >= self.HIGH_THRESHOLD:
            return 'high'
        elif confidence >= self.MEDIUM_THRESHOLD:
            return 'medium'
        else:
            return 'low'
    
    def should_auto_process(self, confidence: float) -> bool:
        """
        Determine if receipt should be auto-processed.
        
        Args:
            confidence: Confidence score
            
        Returns:
            True if confidence >= HIGH_THRESHOLD
        """
        return confidence >= self.HIGH_THRESHOLD
