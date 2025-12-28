"""
Mead Clark Lumber Receipt Format 1
Template for first receipt format from Mead Clark Lumber.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from .base_format import BaseDocumentFormat
from ..utils.text_utils import TextUtils


class MeadClarkFormat1(BaseDocumentFormat):
    """Format template for Mead Clark Lumber receipt format 1."""
    
    def __init__(self):
        super().__init__()
        self.vendor_name = "Mead Clark Lumber"
        self.format_id = "mead_clark_format1"
        self.required_fields = [
            'receipt_date',
            'receipt_number',
            'total_amount',
        ]
        self.optional_fields = [
            'subtotal',
            'amount_subtotal',
            'amount_taxable',
            'tax_rate',
            'tax_amount',
            'amount_discount_percent',
            'balance_prior',
            'amount_due_amt',
            'amount_balance_due',
            'vendor_address1',
            'vendor_address2',
            'vendor_city',
            'vendor_state',
            'vendor_zip',
            'sales_rep',
            'customer_number',
            'customer_name',
            'customer_address1',
            'customer_city',
            'customer_state',
            'customer_zip',
            'payment_method',
            'payment_terms',
            'line_items',
        ]
    
    def get_field_mappings(self) -> Dict[str, str]:
        """
        Get field mappings for Mead Clark Format 1.
        
        Maps format-specific extraction field names to database field names.
        """
        return {
            # Receipt metadata
            'receipt_date': 'receipt_date',
            'receipt_number': 'receipt_number',
            'po_number': 'po_number',
            
            # Vendor information
            'vendor_name': 'vendor_name',  # Used for vendor lookup
            'vendor_address1': 'vendor_address1',
            'vendor_address2': 'vendor_address2',
            'vendor_city': 'vendor_city',
            'vendor_state': 'vendor_state',
            'vendor_zip': 'vendor_zip',
            'sales_rep': 'sales_rep',
            
            # Customer information
            'customer_number': 'customer_number',
            'customer_name': 'customer_name',
            'customer_address1': 'customer_address1',
            'customer_city': 'customer_city',
            'customer_state': 'customer_state',
            'customer_zip': 'customer_zip',
            
            # Amount fields
            'subtotal': 'subtotal',  # Legacy field (2 decimals)
            'amount_subtotal': 'amount_subtotal',  # New field (4 decimals)
            'amount_taxable': 'amount_taxable',
            'tax_rate': 'tax_rate',
            'tax_amount': 'tax_amount',
            'amount_discount_percent': 'amount_discount_percent',
            'balance_prior': 'balance_prior',
            'total_amount': 'total_amount',
            'amount_due_amt': 'amount_due_amt',
            'amount_balance_due': 'amount_balance_due',
            
            # Payment information
            'payment_method': 'payment_method',
            'payment_terms': 'payment_terms',
            
            # Line items
            'line_items': 'line_items',
        }
    
    def detect_format(self, text: str) -> tuple[bool, float]:
        """
        Detect if text matches Mead Clark Format 1.
        
        Format detection uses ONLY structural and vendor indicators:
        - Vendor name "Mead Clark" or "Mead Clark Lumber" (required)
        - "Our Ref" pattern (Mead Clark specific identifier)
        - Line item pattern (number + SKU + dash format)
        - Date patterns (if present)
        - Total amount patterns (if present)
        - Receipt number patterns (if present)
        
        NOTE: Payment method is NOT used for format detection - it's only extracted
        after format is matched. Payment method varies per transaction and is not
        a format identifier.
        """
        if not text:
            return False, 0.0
        
        text_lower = text.lower()
        
        # Primary indicator: Vendor name (required)
        # Handle OCR errors: "meagCialk", "meadciark", "SCVice@meagCialk.COIrn", etc.
        vendor_indicators = [
            'mead clark',
            'mead clark lumber',
            'mead clark lumber co',
            'mead clark lumber company',
            'service@meadclark.com',  # Email address is reliable
            'meadclark.com',  # Domain name
            'meagcialk',  # OCR error variant
            'meadciark',  # OCR error variant
            'scvice@meagcialk',  # OCR error: "SCVice@meagCialk.COIrn"
            'cMail. service@meadciark',  # OCR error variant
        ]
        has_vendor = any(indicator in text_lower for indicator in vendor_indicators)
        
        # Also check for email pattern even if domain is OCR'd incorrectly
        # Pattern: service@[something]clark.com or service@mead[something].com
        # Also handle: SCVice@meagCialk, cMail. service@meadciark
        if not has_vendor:
            email_patterns = [
                r'service@[a-z]*clark\.com',
                r'service@mead[a-z]*\.com',
                r'[sc]vice@[a-z]*cl[a-z]{2,}',  # SCVice@meagCialk, service@meadciark
                r'c?mail[.\s]*service@[a-z]*cl[a-z]{2,}',  # cMail. service@meadciark
            ]
            for pattern in email_patterns:
                if re.search(pattern, text_lower):
                    has_vendor = True
                    break
        
        # Also check for partial matches in email (handle OCR errors)
        # Look for email-like patterns with "clark" or "mead" in them
        if not has_vendor:
            # Look for "@" followed by something containing "clark" or "mead"
            email_fuzzy = re.search(r'@[a-z]*cl[a-z]{2,}|@mead[a-z]*', text_lower)
            if email_fuzzy:
                has_vendor = True
        
        # Vendor name is preferred but not strictly required if we have other strong indicators
        # (vendor name may be completely garbled by OCR)
        vendor_required = False  # Allow detection without vendor if other indicators are strong
        
        # Secondary indicators: Common receipt patterns
        # Date patterns (MM/DD/YYYY, MM-DD-YYYY, etc.)
        has_date = bool(re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text))
        
        # Total amount patterns
        has_total = bool(re.search(
            r'(?:total|amount|sum|due)[\s:]*[\$]?[\d,]+\.\d{2}',
            text_lower
        ))
        
        # Receipt/invoice number patterns - Mead Clark uses "Our Ref"
        # "Our Ref" may be on a different line from the number, so check both patterns
        has_receipt_num = bool(re.search(
            r'(?:our\s+ref|receipt|invoice|inv|#|no\.?)[\s:]*[\d\-]+',
            text_lower
        ))
        
        # Also check for "Our Ref" specifically (Mead Clark format)
        # Pattern 1: "Our Ref" followed by number on same line
        has_our_ref = bool(re.search(r'our\s+ref\s+\d+', text_lower))
        
        # Pattern 2: "Our Ref" on one line, number on next line (common OCR issue)
        # Look for "Our Ref" and then check if there's a 7-digit number nearby
        if not has_our_ref:
            our_ref_match = re.search(r'our\s+ref', text_lower)
            if our_ref_match:
                # Check for 7-digit number within 5 lines after "Our Ref"
                lines = text.split('\n')
                our_ref_line_idx = text[:our_ref_match.start()].count('\n')
                # Look in next 5 lines for a 7-digit number
                for i in range(our_ref_line_idx + 1, min(our_ref_line_idx + 6, len(lines))):
                    if re.search(r'\b\d{7}\b', lines[i]):
                        has_our_ref = True
                        has_receipt_num = True
                        break
        
        # Calculate confidence based on pattern matches
        confidence = 0.0
        
        # Vendor name is required (40% weight)
        if has_vendor:
            confidence += 0.4
        
        # Date pattern (20% weight)
        if has_date:
            confidence += 0.2
        
        # Total amount pattern (20% weight)
        if has_total:
            confidence += 0.2
        
        # Receipt number pattern (20% weight)
        if has_receipt_num:
            confidence += 0.2
        
        # Mead Clark specific: "Our Ref" pattern (10% bonus)
        if has_our_ref:
            confidence += 0.1
        
        # Check for line item pattern (Mead Clark format: number SKU - description)
        # Pattern: number, space, SKU (alphanumeric), space, dash, description
        has_line_item_pattern = bool(re.search(r'^\d+\s+[A-Z0-9]+\s+-', text, re.MULTILINE))
        if has_line_item_pattern:
            confidence += 0.1
        
        # Check for "Invoice Address" header (Mead Clark specific)
        has_invoice_address = bool(re.search(r'invoice\s+address', text_lower))
        if has_invoice_address:
            confidence += 0.05
        
        # Check for "Customer" section (Mead Clark specific)
        has_customer_section = bool(re.search(r'^customer\s', text, re.MULTILINE | re.IGNORECASE))
        if has_customer_section:
            confidence += 0.05
        
        # Minimum confidence threshold: Adjust based on available indicators
        # If we have "Our Ref" + line items, that's strong evidence even without vendor name
        # (vendor name may be OCR'd beyond recognition)
        if has_our_ref and has_line_item_pattern:
            threshold = 0.5  # Very confident with Our Ref + line items
        elif has_vendor and has_our_ref and has_line_item_pattern:
            threshold = 0.5  # Very confident with all three indicators
        elif has_vendor and has_our_ref:
            threshold = 0.5  # Good confidence with vendor + Our Ref
        elif has_our_ref and has_invoice_address:
            threshold = 0.5  # Good confidence with Our Ref + Invoice Address
        else:
            threshold = 0.6  # Need more indicators
        
        return confidence >= threshold, min(confidence, 1.0)
    
    def extract_fields(self, text: str) -> Dict[str, Any]:
        """
        Extract fields from Mead Clark Format 1 receipt.
        
        Uses improved patterns for better accuracy. Should be refined with actual receipt samples.
        """
        fields = {
            'vendor': self.vendor_name,
            'format': self.format_id,
        }
        
        # Extract date - try multiple patterns
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',  # MM/DD/YYYY or MM-DD-YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',    # YYYY/MM/DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                fields['receipt_date'] = TextUtils.extract_date(text)
                break
        else:
            # Fallback to TextUtils
            fields['receipt_date'] = TextUtils.extract_date(text)
        
        # Extract receipt/invoice number - Mead Clark uses "Our Ref" pattern
        # Pattern: "Our Ref 1741680" or "Invoice Address Our Ref 1710785"
        # Important: "Our Ref" may be on a different line from the number
        receipt_number = None
        
        # Pattern 1: "Invoice Address Our Ref 1710785" (all on one line) - check this first
        invoice_our_ref = re.search(r'invoice\s+address\s+our\s+ref\s+(\d{7})', text, re.IGNORECASE)
        if invoice_our_ref:
            receipt_number = invoice_our_ref.group(1)
        
        # Pattern 2: "Our Ref" followed by 7-digit number on same line
        if not receipt_number:
            our_ref_same_line = re.search(r'our\s+ref\s+(\d{7})', text, re.IGNORECASE)
            if our_ref_same_line:
                receipt_number = our_ref_same_line.group(1)
        
        # Pattern 3: "Our Ref" on one line, number on next line(s)
        # This is common when OCR splits them - number can be up to 15 lines away
        if not receipt_number:
            our_ref_match = re.search(r'^our\s+ref$', text, re.MULTILINE | re.IGNORECASE)
            if our_ref_match:
                lines = text.split('\n')
                our_ref_line_idx = text[:our_ref_match.start()].count('\n')
                # Look in next 15 lines for a 7-digit number (skip the "Our Ref" line itself)
                # The number is often separated by other fields like "Taken By", "Sales Rep", etc.
                for i in range(our_ref_line_idx + 1, min(our_ref_line_idx + 16, len(lines))):
                    # Check if line contains only a 7-digit number (or number with whitespace)
                    line_stripped = lines[i].strip()
                    if re.match(r'^\d{7}$', line_stripped):
                        receipt_number = line_stripped
                        break
                    # Also check for 7-digit number anywhere on the line (but not as part of address)
                    # Skip lines that look like addresses (contain "Ave", "St", "Rd", etc.)
                    if not re.search(r'\b(ave|street|st|road|rd|blvd|boulevard|drive|dr|way|ln|lane|address)\b', line_stripped, re.IGNORECASE):
                        seven_digit_match = re.search(r'\b(\d{7})\b', lines[i])
                        if seven_digit_match:
                            receipt_number = seven_digit_match.group(1)
                            break
        
        # Fallback patterns (less specific) - only if "Our Ref" patterns didn't work
        # Be careful not to match "Invoice Address" - only match if followed by number
        if not receipt_number:
            # Look for standalone 7-digit numbers that might be receipt numbers
            # (but not if they're part of addresses or other contexts)
            standalone_seven_digit = re.findall(r'\b(\d{7})\b', text)
            if standalone_seven_digit:
                # Use the first 7-digit number found (usually the receipt number)
                # But skip if it's clearly part of an address (zip codes are 5 digits)
                receipt_number = standalone_seven_digit[0]
        
        if receipt_number:
            fields['receipt_number'] = receipt_number
        else:
            # Final fallback to TextUtils (but this might not work well for Mead Clark format)
            extracted = TextUtils.extract_receipt_number(text)
            # Only use if it's a 7-digit number (Mead Clark format)
            if extracted and re.match(r'^\d{7}$', str(extracted)):
                fields['receipt_number'] = extracted
            else:
                fields['receipt_number'] = None
        
        # Extract total amount - Mead Clark uses "Amount Received" pattern
        # Pattern: "Amount Received $934.26" or "Amount Received | ... | 81.78"
        total_patterns = [
            r'amount\s+received\s+\$?([\d,]+\.\d{2})',  # Primary: "Amount Received $934.26"
            r'amount\s+received\s*\|[^|]*\|\s*([\d,]+\.\d{2})',  # OCR error variant with pipes
            r'total[\s:]*[\$]?\s*([\d,]+\.\d{2})',
            r'amount[\s]+due[\s:]*[\$]?\s*([\d,]+\.\d{2})',
            r'grand[\s]+total[\s:]*[\$]?\s*([\d,]+\.\d{2})',
            r'total[\s]+amount[\s:]*[\$]?\s*([\d,]+\.\d{2})',
            r'[\$]([\d,]+\.\d{2})[\s]*(?:total|due)',  # $XX.XX total/due
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    fields['total_amount'] = Decimal(amount_str)
                    break
                except (ValueError, TypeError):
                    continue
        
        # Extract subtotal - improved patterns
        subtotal_patterns = [
            r'subtotal[\s:]*[\$]?\s*([\d,]+\.\d{2})',
            r'sub[\s-]*total[\s:]*[\$]?\s*([\d,]+\.\d{2})',
            r'sub[\s]+total[\s:]*[\$]?\s*([\d,]+\.\d{2})',
        ]
        
        for pattern in subtotal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    fields['subtotal'] = Decimal(amount_str)
                    break
                except (ValueError, TypeError):
                    continue
        
        # Extract tax amount - improved patterns
        tax_patterns = [
            r'tax[\s:]*[\$]?\s*([\d,]+\.\d{2})',
            r'sales[\s]+tax[\s:]*[\$]?\s*([\d,]+\.\d{2})',
            r'tax[\s]+amount[\s:]*[\$]?\s*([\d,]+\.\d{2})',
        ]
        
        for pattern in tax_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    fields['tax_amount'] = Decimal(amount_str)
                    break
                except (ValueError, TypeError):
                    continue
        
        # Extract line items
        fields['line_items'] = self.extract_line_items(text)
        
        # Extract payment method - Mead Clark format
        # 
        # IMPORTANT: Payment method is in a column under "Payment Method" heading at bottom of receipt.
        # The payment section is bounded by a rectangle with column headers.
        # 
        # Pattern: Look for "Payment Method" column heading, then extract value from that column.
        # Typical format: "Payment Method | Amount Received" with values below.
        # Payment method value is typically "Visa" (or other payment types).
        # 
        # NOTE: "** CASH ACCOUNT ONLY **" is NOT a payment method indicator.
        # This text is for sales rep reference only and does not indicate the actual payment method.
        # Payment method should ONLY be extracted from the "Payment Method" column.
        
        lines = text.split('\n')
        payment_method = None
        
        # Find the line with "Payment Method" column header
        payment_header_line_idx = None
        for i, line in enumerate(lines):
            if re.search(r'payment\s+method', line, re.IGNORECASE):
                payment_header_line_idx = i
                break
        
        if payment_header_line_idx is not None:
            # Payment method value is typically on the same line or within 2-3 lines after header
            # Look for payment method value in the Payment Method column area
            
            # Try same line first (if header and value are on same line)
            header_line = lines[payment_header_line_idx]
            # Pattern: "Payment Method | Visa" or "Payment Method Visa" or "| Payment Method | Visa |"
            # Extract value after "Payment Method" separator
            same_line_match = re.search(
                r'payment\s+method\s*[|:]\s*([a-z]+)',
                header_line,
                re.IGNORECASE
            )
            if same_line_match:
                potential_method = same_line_match.group(1).lower()
                # Verify it's not a column header word
                if potential_method not in ['amount', 'received', 'payment', 'method']:
                    payment_method = potential_method
            else:
                # Try next 3 lines (values below header in table structure)
                # Look for common payment methods in the payment section area
                payment_keywords = ['visa', 'mastercard', 'amex', 'american express', 'cash', 'check', 'credit', 'debit', 'ach']
                
                # Skip column header words
                skip_words = ['amount', 'received', 'payment', 'method', 'eee', 'cng']
                
                for offset in range(1, 4):  # Check next 3 lines
                    if payment_header_line_idx + offset < len(lines):
                        value_line = lines[payment_header_line_idx + offset].strip()
                        # Skip empty lines or lines that are clearly amounts/numbers
                        if not value_line or re.match(r'^[\d,\.\s\$]+$', value_line):
                            continue
                        
                        # Look for payment method keywords (case-insensitive whole word match)
                        for keyword in payment_keywords:
                            pattern = r'\b' + re.escape(keyword) + r'\b'
                            if re.search(pattern, value_line, re.IGNORECASE):
                                # Verify it's not part of a column header
                                if keyword.lower() not in skip_words:
                                    payment_method = keyword.lower()
                                    break
                        if payment_method:
                            break
        
        # If still not found, search entire payment section area (last 15% of receipt)
        # This handles cases where OCR may have missed the column structure or payment method is OCR'd incorrectly
        if not payment_method:
            # Get lines from bottom 15% of receipt (payment section area)
            payment_section_start = max(0, len(lines) - max(5, int(len(lines) * 0.15)))
            payment_section_lines = lines[payment_section_start:]
            payment_section = '\n'.join(payment_section_lines)
            
            # Look for payment method keywords in payment section
            # Skip common column header words
            payment_keywords = ['visa', 'mastercard', 'amex', 'american express', 'cash', 'check', 'credit', 'debit']
            skip_words = ['amount', 'received', 'payment', 'method', 'eee', 'cng', 'goods', 'condition']
            
            for keyword in payment_keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, payment_section, re.IGNORECASE):
                    # Verify it's in context of payment section (near "Payment Method" or payment-related text)
                    keyword_pos = payment_section.lower().find(keyword)
                    context_start = max(0, keyword_pos - 100)
                    context_end = min(len(payment_section), keyword_pos + len(keyword) + 100)
                    context = payment_section[context_start:context_end].lower()
                    
                    # Check if context includes payment-related terms but not skip words
                    has_payment_context = any(term in context for term in ['payment', 'method', 'amount', 'received'])
                    has_skip_word = any(word in context for word in skip_words if word != keyword)
                    
                    # Prefer matches that are near payment context but not mixed with skip words
                    if has_payment_context and not (has_skip_word and keyword not in ['visa', 'mastercard', 'amex']):
                        payment_method = keyword.lower()
                        break
        
        # Normalize payment method
        if payment_method:
            if payment_method in ['visa', 'mastercard', 'amex', 'american express', 'credit', 'card']:
                fields['payment_method'] = 'credit'
            elif payment_method == 'debit':
                fields['payment_method'] = 'debit'
            elif payment_method == 'check':
                fields['payment_method'] = 'check'
            elif payment_method == 'cash':
                fields['payment_method'] = 'cash'
            else:
                fields['payment_method'] = payment_method
        
        # Extract sales rep (from "Taken By" field)
        # Pattern: "Taken By" header followed by name on next line or same line
        taken_by_patterns = [
            r'taken\s+by\s*:?\s*([A-Za-z\s]+)',  # "Taken By: John Paul Destruel"
            r'taken\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "Taken By John Paul Destruel"
        ]
        
        for pattern in taken_by_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                sales_rep = match.group(1).strip()
                # Find the actual value - it might be on the next line
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if re.search(r'taken\s+by', line, re.IGNORECASE):
                        # Check next few lines for the name
                        for offset in range(1, 4):
                            if i + offset < len(lines):
                                next_line = lines[i + offset].strip()
                                # Check if it looks like a name (starts with capital, has letters)
                                if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', next_line):
                                    fields['sales_rep'] = next_line
                                    break
                        if 'sales_rep' in fields:
                            break
                if 'sales_rep' not in fields and match.group(1):
                    fields['sales_rep'] = sales_rep
                break
        
        # Extract customer information
        # Pattern: "Customer" section with customer number and name
        # Customer number is typically a code like "SCOTTRD"
        customer_number_pattern = re.search(
            r'customer\s+number\s*:?\s*([A-Z0-9]+)',
            text,
            re.IGNORECASE
        )
        if not customer_number_pattern:
            # Try to find customer number after "Customer" header
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if re.search(r'^customer\s*$', line, re.IGNORECASE):
                    # Look for customer number in next few lines (typically uppercase code)
                    for offset in range(1, 5):
                        if i + offset < len(lines):
                            next_line = lines[i + offset].strip()
                            if re.match(r'^[A-Z0-9]{4,}$', next_line):
                                fields['customer_number'] = next_line
                                break
                    # Look for customer name (typically follows customer number)
                    for offset in range(1, 6):
                        if i + offset < len(lines):
                            next_line = lines[i + offset].strip()
                            # Check if it looks like a name
                            if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', next_line):
                                fields['customer_name'] = next_line
                                break
                    break
        
        # Extract customer address from "Invoice Address" or "Delivery Address" section
        # Note: In Mead Clark format, "Invoice Address" shows customer address, not vendor
        invoice_address_match = re.search(
            r'(?:invoice|delivery)\s+address\s*:?\s*(.+?)(?:\n\n|\nCustomer|\nJob|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        if invoice_address_match:
            address_text = invoice_address_match.group(1)
            address_lines = [line.strip() for line in address_text.split('\n') if line.strip()]
            
            # Parse address components
            # Format: Company Name, Address Line 1, City, State ZIP
            if len(address_lines) >= 1:
                # First line might be company name, skip it
                addr_start = 0
                for i, line in enumerate(address_lines):
                    if re.search(r'\d+.*(?:st|ave|street|road|rd|blvd|boulevard|drive|dr|way|ln|lane)', line, re.IGNORECASE):
                        addr_start = i
                        fields['customer_address1'] = line
                        break
                
                # Parse city, state, zip
                for line in address_lines[addr_start:]:
                    city_state_zip = re.search(
                        r'([A-Za-z\s]+),\s*([A-Za-z\s]+),\s*(\d{5}(?:-\d{4})?)',
                        line
                    )
                    if city_state_zip:
                        fields['customer_city'] = city_state_zip.group(1).strip()
                        state = city_state_zip.group(2).strip()
                        # Extract state abbreviation if full state name
                        state_abbrev = self._extract_state_abbreviation(state)
                        fields['customer_state'] = state_abbrev or state[:2].upper()
                        fields['customer_zip'] = city_state_zip.group(3)
                        break
        
        # Extract vendor address (Mead Clark's address - typically in header/footer)
        # Look for Mead Clark address patterns in header (first 20% of text) or footer (last 20%)
        lines = text.split('\n')
        header_lines = lines[:max(5, int(len(lines) * 0.2))]
        footer_lines = lines[-max(5, int(len(lines) * 0.2)):]
        
        # Look for address pattern in header/footer
        for section_lines in [header_lines, footer_lines]:
            for i, line in enumerate(section_lines):
                # Look for street address pattern
                street_match = re.search(
                    r'(\d+\s+[A-Za-z0-9\s]+(?:st|ave|street|road|rd|blvd|boulevard|drive|dr|way|ln|lane))',
                    line,
                    re.IGNORECASE
                )
                if street_match and 'vendor_address1' not in fields:
                    fields['vendor_address1'] = street_match.group(1).strip()
                    
                    # Look for city, state, zip in nearby lines
                    for offset in range(1, 3):
                        if i + offset < len(section_lines):
                            city_line = section_lines[i + offset]
                            city_state_zip = re.search(
                                r'([A-Za-z\s]+),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)',
                                city_line
                            )
                            if city_state_zip:
                                fields['vendor_city'] = city_state_zip.group(1).strip()
                                fields['vendor_state'] = city_state_zip.group(2)
                                fields['vendor_zip'] = city_state_zip.group(3)
                                break
                    break
        
        # Calculate amount fields from line items if not explicitly extracted
        line_items = fields.get('line_items', [])
        if line_items:
            # Calculate amount_subtotal from line items
            if 'amount_subtotal' not in fields and 'subtotal' not in fields:
                calculated_subtotal = sum(
                    Decimal(str(item.get('line_total', 0))) for item in line_items
                )
                fields['amount_subtotal'] = calculated_subtotal
                fields['subtotal'] = calculated_subtotal  # Legacy field
            
            # Calculate amount_taxable (sum of taxable amounts from line items)
            if 'amount_taxable' not in fields:
                calculated_taxable = sum(
                    Decimal(str(item.get('taxable_amount', item.get('line_total', 0))))
                    for item in line_items
                )
                fields['amount_taxable'] = calculated_taxable
            
            # Calculate tax_rate if we have tax_amount and amount_taxable
            if 'tax_rate' not in fields and 'tax_amount' in fields and 'amount_taxable' in fields:
                tax_amount = Decimal(str(fields['tax_amount']))
                amount_taxable = Decimal(str(fields['amount_taxable']))
                if amount_taxable > 0:
                    fields['tax_rate'] = tax_amount / amount_taxable
            
            # Set amount_due_amt to total_amount if not specified
            if 'amount_due_amt' not in fields and 'total_amount' in fields:
                fields['amount_due_amt'] = fields['total_amount']
        
        # Extract payment terms (if present)
        # Look for terms like "Net 30", "Due on receipt", etc.
        payment_terms_patterns = [
            r'payment\s+terms\s*:?\s*([^\n]+)',
            r'terms\s*:?\s*([^\n]+)',
            r'net\s+(\d+)',  # "Net 30"
            r'due\s+(?:on\s+)?(?:receipt|invoice|delivery)',
        ]
        
        for pattern in payment_terms_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'net' in pattern.lower():
                    fields['payment_terms'] = f"Net {match.group(1)}"
                else:
                    fields['payment_terms'] = match.group(1).strip() if match.lastindex else 'Due on receipt'
                break
        
        return fields
    
    def _extract_state_abbreviation(self, state_name: str) -> Optional[str]:
        """Extract state abbreviation from full state name."""
        state_map = {
            'california': 'CA',
            'texas': 'TX',
            'florida': 'FL',
            'new york': 'NY',
            'pennsylvania': 'PA',
            'illinois': 'IL',
            'ohio': 'OH',
            'georgia': 'GA',
            'north carolina': 'NC',
            'michigan': 'MI',
        }
        return state_map.get(state_name.lower())
    
    def extract_line_items(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract line items from Format 1.
        
        Improved patterns for better accuracy. Should be refined with actual receipt samples.
        """
        items = []
        lines = text.split('\n')
        
        # Patterns for different line item formats:
        # 1. Quantity Description @ Price = Total
        # 2. Description Price
        # 3. Description Qty Price Total
        
        # Mead Clark line item pattern: [NUMBER] [SKU] - [DESCRIPTION] [QTY] [UNIT] [UNIT_PRICE] [UNIT] [LINE_TOTAL]
        # Example: "1 LAX600G - STABILA 3-PLANE GREEN LASER KIT 1 ea 624.97 ea 624.97"
        # Example: "1 248CHR - 2X4X8' RWD CON HRT GRN RGH 4 mbf 3,833.24"
        mead_clark_pattern = re.compile(
            r'^(\d+)\s+([A-Z0-9]+)\s+-\s+(.+?)\s+(\d+(?:\.\d+)?)\s+(\w+)\s+([\d,]+\.\d{2})\s+\w+\s+([\d,]+\.\d{2})$',
            re.IGNORECASE
        )
        
        # Pattern 1: Quantity Description @ Price (or = Total) - fallback
        qty_desc_price_pattern = re.compile(
            r'^(\d+(?:\.\d+)?)\s+([A-Za-z0-9\s\-\.]+?)\s+[@=]?\s*[\$]?([\d,]+\.\d{2})',
            re.IGNORECASE
        )
        
        # Pattern 2: Description followed by price at end - fallback
        desc_price_pattern = re.compile(
            r'^(.+?)\s+[\$]?([\d,]+\.\d{2})$',
            re.IGNORECASE
        )
        
        # Pattern 3: Description Qty Price Total (tab or space separated) - fallback
        desc_qty_price_total_pattern = re.compile(
            r'^(.+?)\s+(\d+(?:\.\d+)?)\s+[\$]?([\d,]+\.\d{2})\s+[\$]?([\d,]+\.\d{2})$',
            re.IGNORECASE
        )
        
        # Skip patterns for header/footer lines
        skip_keywords = [
            'receipt', 'invoice', 'inv', 'total', 'subtotal', 'tax', 
            'date', 'amount', 'due', 'payment', 'thank', 'store',
            'address', 'phone', 'email', 'website'
        ]
        
        # Handle multi-line items: sometimes price/total are on separate lines
        # First, try to find complete line items on single lines
        # Then, try to reconstruct multi-line items
        
        i = 0
        while i < len(lines):
            line = TextUtils.clean_text(lines[i])
            if not line or len(line) < 5:
                i += 1
                continue
            
            line_lower = line.lower()
            
            # Skip header/footer lines
            if any(skip in line_lower for skip in skip_keywords):
                i += 1
                continue
            
            # Skip lines that are clearly not line items (too short, all numbers, etc.)
            if len(line.split()) < 2:
                i += 1
                continue
            
            item = None
            
            # Try Mead Clark pattern first: [NUMBER] [SKU] - [DESCRIPTION] [QTY] [UNIT] [UNIT_PRICE] [UNIT] [LINE_TOTAL]
            match = mead_clark_pattern.search(line)
            if match:
                # Complete line item on single line
                line_number = int(match.group(1))
                sku = match.group(2).strip()
                description = match.group(3).strip()
                quantity = Decimal(match.group(4))
                unit = match.group(5).strip()
                unit_price_str = match.group(6).replace(',', '')
                line_total_str = match.group(7).replace(',', '')
                
                try:
                    unit_price = Decimal(unit_price_str)
                    line_total = Decimal(line_total_str)
                    
                    if description and unit_price:
                        # Determine taxable amount (usually equals line_total, sometimes 0 for labor)
                        # Check if description contains "labor" or similar non-taxable keywords
                        desc_lower = description.lower()
                        is_taxable = not any(keyword in desc_lower for keyword in ['labor', 'labour', 'service', 'delivery'])
                        taxable_amount = line_total if is_taxable else Decimal('0')
                        
                        item = {
                            'line_number': line_number,
                            'vendor_sku': sku,
                            'description': description,
                            'quantity': quantity,
                            'uom': unit,
                            'unit_price': unit_price,
                            'line_total': line_total,
                            'taxable_amount': taxable_amount,
                        }
                except (ValueError, TypeError):
                    pass
            
            # Try multi-line pattern: [NUMBER] [SKU] - [DESCRIPTION] [QTY] [UNIT] on one line,
            # price/total on following lines
            if not item and re.match(r'^\d+\s+[A-Z0-9]+\s+-', line):
                # This looks like the start of a line item
                # Pattern: "1 248CHR - 2X4X8' RWD CON HRT GRN RGH 4"
                # Next lines might have: "3,833.24" and "mbf"
                multi_line_match = re.match(r'^(\d+)\s+([A-Z0-9]+)\s+-\s+(.+?)\s+(\d+(?:\.\d+)?)\s*$', line)
                if multi_line_match:
                    line_number = int(multi_line_match.group(1))
                    sku = multi_line_match.group(2).strip()
                    description = multi_line_match.group(3).strip()
                    quantity = Decimal(multi_line_match.group(4))
                    
                    # Look ahead for price and unit on next lines
                    unit = None
                    unit_price = None
                    line_total = None
                    
                    # Check next 5 lines for price and unit
                    for j in range(i + 1, min(i + 6, len(lines))):
                        next_line = TextUtils.clean_text(lines[j]).strip()
                        if not next_line:
                            continue
                        
                        # Check for price (currency format) - this is likely the line total
                        price_match = re.search(r'([\d,]+\.\d{2})', next_line)
                        if price_match and not line_total:
                            line_total_str = price_match.group(1).replace(',', '')
                            try:
                                line_total = Decimal(line_total_str)
                            except (ValueError, TypeError):
                                pass
                        
                        # Check for unit (short text like "ea", "mbf", "hr")
                        if not unit and re.match(r'^[a-z]{1,5}$', next_line, re.IGNORECASE):
                            unit = next_line
                    
                    # Calculate unit price from line total and quantity
                    if description and line_total:
                        unit_price = line_total / quantity if quantity > 0 else Decimal('0')
                        
                        # Determine taxable amount
                        desc_lower = description.lower()
                        is_taxable = not any(keyword in desc_lower for keyword in ['labor', 'labour', 'service', 'delivery'])
                        taxable_amount = line_total if is_taxable else Decimal('0')
                        
                        item = {
                            'line_number': line_number,
                            'vendor_sku': sku,
                            'description': description,
                            'quantity': quantity,
                            'uom': unit or 'ea',
                            'unit_price': unit_price or Decimal('0'),
                            'line_total': line_total or Decimal('0'),
                            'taxable_amount': taxable_amount,
                        }
            
            # Try Pattern 3: Description Qty Price Total (fallback)
            if not item:
                match = desc_qty_price_total_pattern.search(line)
                if match:
                    description = match.group(1).strip()
                    quantity = Decimal(match.group(2))
                    unit_price = TextUtils.extract_currency(match.group(3))
                    line_total = TextUtils.extract_currency(match.group(4))
                    
                    if description and unit_price:
                        line_total = line_total if line_total else quantity * unit_price
                        # Determine taxable amount
                        desc_lower = description.lower()
                        is_taxable = not any(keyword in desc_lower for keyword in ['labor', 'labour', 'service', 'delivery'])
                        taxable_amount = line_total if is_taxable else Decimal('0')
                        
                        item = {
                            'description': description,
                            'quantity': quantity,
                            'unit_price': unit_price,
                            'line_total': line_total,
                            'taxable_amount': taxable_amount,
                        }
            
            # Try Pattern 1: Quantity Description @ Price (fallback)
            if not item:
                match = qty_desc_price_pattern.search(line)
                if match:
                    quantity = Decimal(match.group(1))
                    description = match.group(2).strip()
                    unit_price = TextUtils.extract_currency(match.group(3))
                    
                    if description and unit_price:
                        line_total = quantity * unit_price
                        # Determine taxable amount
                        desc_lower = description.lower()
                        is_taxable = not any(keyword in desc_lower for keyword in ['labor', 'labour', 'service', 'delivery'])
                        taxable_amount = line_total if is_taxable else Decimal('0')
                        
                        item = {
                            'description': description,
                            'quantity': quantity,
                            'unit_price': unit_price,
                            'line_total': line_total,
                            'taxable_amount': taxable_amount,
                        }
            
            # Try Pattern 2: Description Price (fallback)
            if not item:
                match = desc_price_pattern.search(line)
                if match:
                    description = match.group(1).strip()
                    price = TextUtils.extract_currency(match.group(2))
                    
                    # Validate description is meaningful (not just numbers/symbols)
                    if description and price and len(description) > 3:
                        # Check if description looks like a product name
                        if re.search(r'[A-Za-z]', description):
                            # Determine taxable amount
                            desc_lower = description.lower()
                            is_taxable = not any(keyword in desc_lower for keyword in ['labor', 'labour', 'service', 'delivery'])
                            taxable_amount = price if is_taxable else Decimal('0')
                            
                            item = {
                                'description': description,
                                'quantity': Decimal('1'),
                                'unit_price': price,
                                'line_total': price,
                                'taxable_amount': taxable_amount,
                            }
            
            # Add item if valid
            if item and item.get('description') and item.get('unit_price'):
                items.append(item)
                # Skip ahead if we processed a multi-line item
                if 'vendor_sku' in item and item.get('vendor_sku'):
                    # Skip the lines we used for this item
                    i += 1
                    continue
            
            i += 1
        
        return items
