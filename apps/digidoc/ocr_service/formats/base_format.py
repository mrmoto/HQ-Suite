"""
Base Document Format Template
Abstract base class for document format templates.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from decimal import Decimal


class BaseDocumentFormat(ABC):
    """Base class for document format templates."""
    
    def __init__(self):
        self.vendor_name = None
        self.format_id = None
        self.required_fields = []
        self.optional_fields = []
    
    @abstractmethod
    def detect_format(self, text: str) -> tuple[bool, float]:
        """
        Detect if text matches this format.
        
        Args:
            text: OCR text
            
        Returns:
            Tuple of (matches: bool, confidence: float)
        """
        pass
    
    @abstractmethod
    def extract_fields(self, text: str) -> Dict[str, Any]:
        """
        Extract structured fields from document text.
        
        Args:
            text: OCR text
            
        Returns:
            Dictionary of extracted fields
        """
        pass
    
    def validate_fields(self, fields: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate extracted fields.
        
        Args:
            fields: Extracted fields dictionary
            
        Returns:
            Tuple of (is_valid: bool, missing_fields: List[str])
        """
        missing = []
        
        for field in self.required_fields:
            if field not in fields or fields[field] is None:
                missing.append(field)
        
        return len(missing) == 0, missing
    
    def get_field_extraction_rate(self, fields: Dict[str, Any]) -> float:
        """
        Calculate percentage of required fields successfully extracted.
        
        Args:
            fields: Extracted fields dictionary
            
        Returns:
            Extraction rate (0.0 to 1.0)
        """
        if not self.required_fields:
            return 1.0
        
        extracted = sum(1 for field in self.required_fields 
                       if field in fields and fields[field] is not None)
        
        return extracted / len(self.required_fields)
    
    def extract_line_items(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract line items from receipt text.
        
        Override in subclasses for format-specific extraction.
        
        Args:
            text: OCR text
            
        Returns:
            List of line item dictionaries
        """
        # Basic implementation - should be overridden
        return []
    
    def get_field_mappings(self) -> Dict[str, str]:
        """
        Get field mappings for this format.
        
        Returns a dictionary mapping format-specific field names to database field names.
        Format: { 'format_field_name': 'database_field_name' }
        
        Override in subclasses to define format-specific mappings.
        
        Returns:
            Dictionary of field mappings
        """
        return {}
    
    def get_required_fields(self) -> List[str]:
        """
        Get list of required fields for this format.
        
        Returns field names that must be extracted for this format to be considered valid.
        These are format-specific, not global to all receipt types.
        
        Returns:
            List of required field names (database field names)
        """
        return self.required_fields if hasattr(self, 'required_fields') else []
    
    def get_optional_fields(self) -> List[str]:
        """
        Get list of optional fields for this format.
        
        Returns field names that may be extracted but are not required.
        These are format-specific, not global to all receipt types.
        
        Returns:
            List of optional field names (database field names)
        """
        return self.optional_fields if hasattr(self, 'optional_fields') else []
