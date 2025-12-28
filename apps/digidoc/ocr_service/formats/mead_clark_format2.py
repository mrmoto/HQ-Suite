"""
Mead Clark Lumber Receipt Format 2
Template for second receipt format from Mead Clark Lumber.
"""

import re
from typing import Dict, List, Any, Tuple
from decimal import Decimal, InvalidOperation
from .base_format import BaseDocumentFormat
from ..utils.text_utils import TextUtils


class MeadClarkFormat2(BaseDocumentFormat):
    """Format template for Mead Clark Lumber receipt format 2."""
    
    def __init__(self):
        super().__init__()
        self.vendor_name = "Mead Clark Lumber"
        self.format_id = "mead_clark_format2"
        self.required_fields = [
            'receipt_date',
            'receipt_number',
            'total_amount',
        ]
        self.optional_fields = [
            'subtotal',
            'tax_amount',
            'line_items',
            'payment_method',
        ]
    
    def detect_format(self, text: str) -> tuple[bool, float]:
        """
        Detect if text matches Mead Clark Format 2.
        
        This format may have different layout/structure than Format 1.
        To be refined with actual receipt samples.
        """
        if not text:
            return False, 0.0
        
        text_lower = text.lower()
        
        # Check for vendor name
        vendor_indicators = ['mead clark', 'mead clark lumber']
        has_vendor = any(indicator in text_lower for indicator in vendor_indicators)
        
        if not has_vendor:
            return False, 0.0
        
        # Format 2 specific patterns (to be refined with actual samples)
        # May have different header/footer structure or field positions
        has_date = bool(re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text))
        has_total = bool(re.search(r'total|amount|sum', text_lower))
        has_receipt_num = bool(re.search(r'receipt|invoice|inv|#', text_lower))
        
        # Format 2 might have different indicators
        # For now, if it matches vendor but Format 1 doesn't match well, try Format 2
        # This logic should be refined with actual samples
        
        confidence = 0.0
        if has_vendor:
            confidence += 0.4
        if has_date:
            confidence += 0.2
        if has_total:
            confidence += 0.2
        if has_receipt_num:
            confidence += 0.2
        
        return confidence >= 0.6, confidence
    
    def extract_fields(self, text: str) -> Dict[str, Any]:
        """
        Extract fields from Mead Clark Format 2 receipt.
        
        Similar to Format 1 but may have different field positions or patterns.
        To be refined with actual receipt samples.
        """
        fields = {
            'vendor': self.vendor_name,
            'format': self.format_id,
        }
        
        # Extract date
        fields['receipt_date'] = TextUtils.extract_date(text)
        
        # Extract receipt number
        fields['receipt_number'] = TextUtils.extract_receipt_number(text)
        
        # Extract totals (may be in different position than Format 1)
        total_patterns = [
            r'total[\s:]*[\$]?([\d,]+\.\d{2})',
            r'amount[\s]+due[\s:]*[\$]?([\d,]+\.\d{2})',
            r'grand[\s]+total[\s:]*[\$]?([\d,]+\.\d{2})',
            r'balance[\s]+due[\s:]*[\$]?([\d,]+\.\d{2})',
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['total_amount'] = TextUtils.extract_currency(match.group(0))
                break
        
        # Extract subtotal
        subtotal_patterns = [
            r'subtotal[\s:]*[\$]?([\d,]+\.\d{2})',
            r'sub[\s-]*total[\s:]*[\$]?([\d,]+\.\d{2})',
        ]
        
        for pattern in subtotal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['subtotal'] = TextUtils.extract_currency(match.group(0))
                break
        
        # Extract tax
        tax_patterns = [
            r'tax[\s:]*[\$]?([\d,]+\.\d{2})',
            r'sales[\s]+tax[\s:]*[\$]?([\d,]+\.\d{2})',
        ]
        
        for pattern in tax_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['tax_amount'] = TextUtils.extract_currency(match.group(0))
                break
        
        # Extract line items
        fields['line_items'] = self.extract_line_items(text)
        
        # Extract payment method
        payment_patterns = [
            r'(cash|check|credit|debit|ach|card)',
        ]
        
        for pattern in payment_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['payment_method'] = match.group(1).lower()
                break
        
        return fields
    
    def extract_line_items(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract line items from Format 2.
        
        May have different line item structure than Format 1.
        To be refined with actual receipt samples.
        """
        items = []
        lines = text.split('\n')
        
        # Format 2 might have different line item patterns
        # Try multiple patterns
        item_patterns = [
            # Pattern 1: quantity description @ price = total
            re.compile(r'(\d+(?:\.\d+)?)\s+([A-Za-z0-9\s\-\.]+?)\s+[\$@]?([\d,]+\.\d{2})', re.IGNORECASE),
            # Pattern 2: description quantity x price = total
            re.compile(r'([A-Za-z0-9\s\-\.]+?)\s+(\d+(?:\.\d+)?)\s*[xX]\s*[\$]?([\d,]+\.\d{2})', re.IGNORECASE),
        ]
        
        for line in lines:
            line = TextUtils.clean_text(line)
            if not line or len(line) < 5:
                continue
            
            # Skip header/footer lines
            if any(skip in line.lower() for skip in ['receipt', 'invoice', 'total', 'subtotal', 'tax', 'date']):
                continue
            
            for pattern in item_patterns:
                match = pattern.search(line)
                if match:
                    if len(match.groups()) == 3:
                        # Determine which group is quantity vs description
                        # First try: group 1 is quantity
                        try:
                            quantity = Decimal(match.group(1))
                            description = match.group(2).strip()
                            unit_price = TextUtils.extract_currency(match.group(3))
                            
                            if description and unit_price:
                                items.append({
                                    'description': description,
                                    'quantity': quantity,
                                    'unit_price': unit_price,
                                    'line_total': quantity * unit_price,
                                })
                                break
                        except (ValueError, InvalidOperation):
                            # Try alternative: group 2 is quantity
                            try:
                                description = match.group(1).strip()
                                quantity = Decimal(match.group(2))
                                unit_price = TextUtils.extract_currency(match.group(3))
                                
                                if description and unit_price:
                                    items.append({
                                        'description': description,
                                        'quantity': quantity,
                                        'unit_price': unit_price,
                                        'line_total': quantity * unit_price,
                                    })
                                    break
                            except (ValueError, InvalidOperation):
                                continue
            
            # Fallback: simple description price pattern
            if not any(pattern.search(line) for pattern in item_patterns):
                price_match = re.search(r'[\$]?([\d,]+\.\d{2})$', line)
                if price_match:
                    description = line[:price_match.start()].strip()
                    price = TextUtils.extract_currency(price_match.group(0))
                    
                    if description and price and len(description) > 3:
                        items.append({
                            'description': description,
                            'quantity': Decimal('1'),
                            'unit_price': price,
                            'line_total': price,
                        })
        
        return items
