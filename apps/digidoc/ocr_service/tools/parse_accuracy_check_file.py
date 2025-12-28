"""
Parser for accuracy check text files.

Parses the justified, column-aligned text format used for accuracy checking.
"""

import re
from typing import Dict, List, Any, Optional
from decimal import Decimal


class AccuracyCheckParser:
    """Parser for accuracy check text files."""
    
    def __init__(self):
        self.field_width = 25
        self.value_width = 20
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse an accuracy check text file.
        
        Args:
            file_path: Path to accuracy check text file
            
        Returns:
            Dictionary with parsed data:
            {
                'metadata': dict,
                'vendor': dict,
                'customer': dict,
                'amounts': dict,
                'lines': list,
            }
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = {
            'metadata': {},
            'vendor': {},
            'customer': {},
            'amounts': {},
            'lines': [],
        }
        
        lines = content.split('\n')
        current_section = None
        in_lines_section = False
        line_headers = None
        
        for line in lines:
            line = line.rstrip()
            
            # Detect section headers
            if line.startswith('RECEIPT: METADATA'):
                current_section = 'metadata'
                in_lines_section = False
                continue
            elif line.startswith('RECEIPT: VENDOR INFORMATION'):
                current_section = 'vendor'
                in_lines_section = False
                continue
            elif line.startswith('RECEIPT: CUSTOMER INFORMATION'):
                current_section = 'customer'
                in_lines_section = False
                continue
            elif line.startswith('RECEIPT: AMOUNT INFORMATION'):
                current_section = 'amounts'
                in_lines_section = False
                continue
            elif line.startswith('RECEIPT LINES:'):
                current_section = None
                in_lines_section = True
                line_headers = None
                continue
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Parse field-value pairs
            if not in_lines_section and ':' in line:
                # Parse field: value format
                parts = line.split(':', 1)
                if len(parts) == 2:
                    field_name = parts[0].strip()
                    value = parts[1].strip()
                    
                    # Remove placeholder markers
                    if value.startswith('<') and value.endswith('>'):
                        value = None
                    elif value == 'NULL':
                        value = None
                    else:
                        # Try to parse as number
                        value = self._parse_value(value)
                    
                    # Store in appropriate section
                    if current_section:
                        result[current_section][field_name] = value
            
            # Parse receipt lines table
            elif in_lines_section:
                if line_headers is None:
                    # First non-empty line after "RECEIPT LINES:" is the header
                    line_headers = self._parse_line_headers(line)
                else:
                    # Parse data row
                    line_data = self._parse_line_row(line, line_headers)
                    if line_data:
                        result['lines'].append(line_data)
        
        return result
    
    def _parse_value(self, value: str) -> Any:
        """
        Parse a value string, attempting to convert to appropriate type.
        
        Args:
            value: Value string
            
        Returns:
            Parsed value (Decimal for numbers, str otherwise)
        """
        value = value.strip()
        
        # Try to parse as decimal number
        try:
            # Remove commas
            cleaned = value.replace(',', '')
            return Decimal(cleaned)
        except (ValueError, TypeError):
            pass
        
        # Return as string
        return value
    
    def _parse_line_headers(self, header_line: str) -> List[Dict[str, Any]]:
        """
        Parse receipt lines table header to determine column positions.
        
        Args:
            header_line: Header line text
            
        Returns:
            List of column definitions: [{'name': str, 'start': int, 'end': int, 'align': str}]
        """
        headers = []
        words = header_line.split()
        
        # Simple approach: split on whitespace and track positions
        # More sophisticated: could use regex to find column boundaries
        current_pos = 0
        
        for word in words:
            word_start = header_line.find(word, current_pos)
            word_end = word_start + len(word)
            
            # Determine alignment based on header name
            align = 'left'
            if word.lower() in ['line', 'qty', 'price', 'subtotal', 'taxable_amount']:
                align = 'right'
            
            headers.append({
                'name': word,
                'start': word_start,
                'end': word_end,
                'align': align,
            })
            
            current_pos = word_end
        
        return headers
    
    def _parse_line_row(self, row_line: str, headers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Parse a receipt line data row.
        
        Args:
            row_line: Data row text
            headers: Column header definitions from _parse_line_headers
            
        Returns:
            Dictionary with line item data, or None if parsing fails
        """
        if not row_line.strip():
            return None
        
        result = {}
        
        # Simple approach: split on whitespace
        # More sophisticated: could use column positions from headers
        parts = row_line.split()
        
        if len(parts) < 3:
            return None
        
        # Map parts to expected fields
        # Format: Line Description qty UOM Price Subtotal taxable_amount codeCSI
        field_mapping = ['line', 'description', 'qty', 'uom', 'price', 'subtotal', 'taxable_amount', 'code_csi']
        
        for i, part in enumerate(parts):
            if i < len(field_mapping):
                field_name = field_mapping[i]
                value = part
                
                # Parse numeric fields
                if field_name in ['line', 'qty', 'price', 'subtotal', 'taxable_amount']:
                    try:
                        value = Decimal(value.replace(',', ''))
                    except (ValueError, TypeError):
                        if value == 'NULL':
                            value = None
                        else:
                            continue  # Skip invalid numeric
                elif value == 'NULL':
                    value = None
                
                result[field_name] = value
        
        return result if result else None


def parse_accuracy_check_file(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to parse an accuracy check file.
    
    Args:
        file_path: Path to accuracy check text file
        
    Returns:
        Parsed data dictionary
    """
    parser = AccuracyCheckParser()
    return parser.parse(file_path)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python parse_accuracy_check_file.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = parse_accuracy_check_file(file_path)
    
    import json
    print(json.dumps(result, indent=2, default=str))
