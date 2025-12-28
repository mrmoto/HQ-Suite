"""
Text Processing Utilities
Helper functions for text cleaning, validation, and parsing.
"""

import re
from datetime import datetime
from typing import Optional, List, Dict
from decimal import Decimal, InvalidOperation


class TextUtils:
    """Utility functions for text processing."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean OCR text by removing extra whitespace and fixing common issues."""
        if not text:
            return ""
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_date(text: str) -> Optional[str]:
        """
        Extract date from text in various formats.
        
        Returns:
            ISO format date string (YYYY-MM-DD) or None
        """
        if not text:
            return None
        
        # Common date patterns
        patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',  # MM/DD/YYYY or MM-DD-YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',    # YYYY/MM/DD
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if len(match.group(3)) == 2:
                        # Two-digit year
                        year = int(match.group(3))
                        if year < 50:
                            year += 2000
                        else:
                            year += 1900
                        month = int(match.group(1))
                        day = int(match.group(2))
                    else:
                        # Four-digit year
                        if len(match.group(1)) == 4:
                            year = int(match.group(1))
                            month = int(match.group(2))
                            day = int(match.group(3))
                        else:
                            month = int(match.group(1))
                            day = int(match.group(2))
                            year = int(match.group(3))
                    
                    # Validate date
                    date_obj = datetime(year, month, day)
                    return date_obj.strftime('%Y-%m-%d')
                except (ValueError, IndexError):
                    continue
        
        return None
    
    @staticmethod
    def extract_currency(text: str) -> Optional[Decimal]:
        """
        Extract currency amount from text.
        
        Returns:
            Decimal amount or None
        """
        if not text:
            return None
        
        # Remove currency symbols and extract number
        # Pattern: $123.45 or 123.45 or 123,45.67
        pattern = r'[\$]?([\d,]+\.?\d*)'
        match = re.search(pattern, text.replace(',', ''))
        
        if match:
            try:
                amount_str = match.group(1).replace(',', '')
                return Decimal(amount_str)
            except (InvalidOperation, ValueError):
                return None
        
        return None
    
    @staticmethod
    def extract_receipt_number(text: str) -> Optional[str]:
        """Extract receipt/invoice number from text."""
        if not text:
            return None
        
        # Common patterns: "Receipt #12345" or "Invoice: 12345" or "No. 12345"
        patterns = [
            r'(?:receipt|invoice|inv)[\s#:]*([A-Z0-9-]+)',
            r'(?:no|number|#)[\s.:]*([A-Z0-9-]+)',
            r'#\s*([A-Z0-9-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    @staticmethod
    def find_vendor_name(text: str, known_vendors: List[str] = None) -> Optional[str]:
        """
        Find vendor name in text.
        
        Args:
            text: OCR text
            known_vendors: List of known vendor names to match against
            
        Returns:
            Vendor name if found, None otherwise
        """
        if not text or not known_vendors:
            return None
        
        text_lower = text.lower()
        
        for vendor in known_vendors:
            if vendor.lower() in text_lower:
                return vendor
        
        return None
    
    @staticmethod
    def extract_line_items(text: str) -> List[Dict[str, any]]:
        """
        Extract line items from receipt text.
        
        This is a basic implementation. Format-specific extractors should override.
        
        Returns:
            List of line items with description, quantity, price, etc.
        """
        items = []
        
        # Basic pattern: description followed by price
        # This is a placeholder - format templates should provide better extraction
        lines = text.split('\n')
        
        for line in lines:
            line = TextUtils.clean_text(line)
            if not line:
                continue
            
            # Try to extract price at end of line
            price_match = re.search(r'[\$]?([\d,]+\.\d{2})$', line)
            if price_match:
                description = line[:price_match.start()].strip()
                price = TextUtils.extract_currency(price_match.group(0))
                
                if description and price:
                    items.append({
                        'description': description,
                        'quantity': Decimal('1'),
                        'unit_price': price,
                        'line_total': price,
                    })
        
        return items
    
    @staticmethod
    def calculate_text_confidence(ocr_data: Dict) -> float:
        """
        Calculate average confidence from Tesseract OCR data.
        
        Args:
            ocr_data: Tesseract OCR result dictionary
            
        Returns:
            Average confidence score (0.0 to 1.0)
        """
        if not ocr_data or 'conf' not in ocr_data:
            return 0.0
        
        confidences = [float(conf) for conf in ocr_data['conf'] if conf != '-1']
        
        if not confidences:
            return 0.0
        
        # Normalize from 0-100 to 0-1
        avg_conf = sum(confidences) / len(confidences) / 100.0
        return avg_conf
