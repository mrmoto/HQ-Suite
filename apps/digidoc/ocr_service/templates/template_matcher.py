"""
Template Matcher
Matches documents to cached templates with confidence scoring.
Supports multiple formats per vendor/document type.
"""

from typing import Dict, List, Tuple, Optional, Any
from .template_cache import TemplateCache
from ..ocr_processor import OCRProcessor


class TemplateMatcher:
    """Matches documents to templates with confidence scoring."""
    
    def __init__(self, cache: TemplateCache, ocr_processor: OCRProcessor):
        """
        Initialize template matcher.
        
        Args:
            cache: TemplateCache instance
            ocr_processor: OCRProcessor instance
        """
        self.cache = cache
        self.ocr_processor = ocr_processor
    
    def find_matching_templates(
        self,
        ocr_text: str,
        calling_app_id: str,
        document_type: Optional[str] = None,
        vendor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find matching templates for OCR text.
        
        Args:
            ocr_text: OCR extracted text
            calling_app_id: Calling application identifier
            document_type: Document type filter (optional)
            vendor: Vendor name filter (optional)
            
        Returns:
            List of template matches with confidence scores, sorted by confidence
        """
        # Get all relevant templates from cache
        templates = self.cache.get_templates_for_context(
            calling_app_id,
            document_type,
            vendor
        )
        
        if not templates:
            return []
        
        # Score each template
        matches = []
        for template in templates:
            confidence = self._score_template_match(ocr_text, template)
            if confidence >= 0.80:  # Only return matches with >=80% confidence
                matches.append({
                    'template_id': template['template_id'],
                    'document_type': template['document_type'],
                    'vendor': template['vendor'],
                    'format_name': template['format_name'],
                    'confidence': confidence,
                    'template_data': template['template_data'],
                })
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Return top 5 matches
        return matches[:5]
    
    def _score_template_match(
        self,
        ocr_text: str,
        template: Dict[str, Any]
    ) -> float:
        """
        Score how well OCR text matches a template.
        
        Args:
            ocr_text: OCR extracted text
            template: Template dictionary
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not ocr_text or not template:
            return 0.0
        
        text_lower = ocr_text.lower()
        confidence = 0.0
        
        # Check vendor name match (if template has vendor)
        if template.get('vendor'):
            vendor_lower = template['vendor'].lower()
            if vendor_lower in text_lower:
                confidence += 0.4
            else:
                # Vendor mismatch significantly reduces confidence
                return 0.0
        
        # Check document type indicators (if template has document_type)
        if template.get('document_type'):
            doc_type = template['document_type'].lower()
            # Common indicators for document types
            indicators = {
                'receipt': ['receipt', 'invoice', 'total', 'subtotal', 'tax'],
                'contract': ['contract', 'agreement', 'terms', 'signature'],
                'bid': ['bid', 'quote', 'estimate', 'proposal'],
                'timecard': ['timecard', 'timesheet', 'hours', 'employee'],
            }
            
            if doc_type in indicators:
                matches = sum(1 for indicator in indicators[doc_type] if indicator in text_lower)
                if matches > 0:
                    confidence += 0.2 * min(matches / len(indicators[doc_type]), 1.0)
        
        # Check template-specific patterns (if template_data has patterns)
        template_data = template.get('template_data', {})
        patterns = template_data.get('detection_patterns', [])
        
        if patterns:
            pattern_matches = 0
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    pattern_matches += 1
            
            if pattern_matches > 0:
                confidence += 0.3 * (pattern_matches / len(patterns))
        
        # Check field presence (if template has field_mappings)
        field_mappings = template.get('field_mappings', {})
        if field_mappings:
            # Look for common field indicators
            field_indicators = ['date', 'total', 'amount', 'number', 'receipt', 'invoice']
            field_matches = sum(1 for indicator in field_indicators if indicator in text_lower)
            if field_matches > 0:
                confidence += 0.1 * min(field_matches / len(field_indicators), 1.0)
        
        # Normalize to 0.0-1.0 range
        return min(confidence, 1.0)
    
    def get_best_match(
        self,
        ocr_text: str,
        calling_app_id: str,
        document_type: Optional[str] = None,
        vendor: Optional[str] = None,
        min_confidence: float = 0.90
    ) -> Optional[Dict[str, Any]]:
        """
        Get the best matching template if confidence is high enough.
        
        Args:
            ocr_text: OCR extracted text
            calling_app_id: Calling application identifier
            document_type: Document type filter (optional)
            vendor: Vendor name filter (optional)
            min_confidence: Minimum confidence threshold
            
        Returns:
            Best matching template or None if no match meets threshold
        """
        matches = self.find_matching_templates(
            ocr_text,
            calling_app_id,
            document_type,
            vendor
        )
        
        if matches and matches[0]['confidence'] >= min_confidence:
            return matches[0]
        
        return None
