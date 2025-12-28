"""
Accuracy Check Tool

Generates accuracy check text files from OCR extraction results and compares
against expected values. Uses justified, column-aligned text formatting.
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from formats.mead_clark_format1 import MeadClarkFormat1
from extractors.document_extractor import DocumentExtractor
from tools.parse_accuracy_check_file import AccuracyCheckParser


class AccuracyCheckGenerator:
    """Generates accuracy check text files with justified formatting."""
    
    def __init__(self):
        self.field_name_width = 25
        self.field_value_width = 20
        self.line_column_widths = {
            'line': 4,
            'description': 20,
            'qty': 10,
            'uom': 8,
            'price': 10,
            'subtotal': 12,
            'taxable_amount': 15,
            'code_csi': 8,
        }
    
    def generate_from_extraction(
        self,
        extracted_fields: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate accuracy check text file from extracted fields.
        
        Args:
            extracted_fields: Dictionary of extracted fields from OCR
            output_path: Optional path to save file (if None, returns as string)
            
        Returns:
            Generated text content
        """
        lines = []
        
        # METADATA section
        lines.append('RECEIPT: METADATA')
        lines.append(self._format_field('project_fk', '<looked up from vendor template>'))
        lines.append(self._format_field('creationTimestamp', datetime.now().isoformat()))
        lines.append(self._format_field('createdBy', '<user reviewing document>'))
        lines.append('')
        
        # VENDOR INFORMATION section
        lines.append('RECEIPT: VENDOR INFORMATION')
        lines.append(self._format_field('vendorFK', '<UUID>'))
        lines.append(self._format_field('vendorName', extracted_fields.get('vendor', 'Mead Clark Lumber')))
        lines.append(self._format_field('vendor_address1', extracted_fields.get('vendor_address1', '<address>')))
        lines.append(self._format_field('vendor_address2', extracted_fields.get('vendor_address2')))
        lines.append(self._format_field('vendor_city', extracted_fields.get('vendor_city')))
        lines.append(self._format_field('vendor_state', extracted_fields.get('vendor_state')))
        lines.append(self._format_field('vendor_zip', extracted_fields.get('vendor_zip')))
        lines.append(self._format_field('salesRep', extracted_fields.get('sales_rep')))
        lines.append('')
        
        # CUSTOMER INFORMATION section
        lines.append('RECEIPT: CUSTOMER INFORMATION')
        lines.append(self._format_field('customerNumber', extracted_fields.get('customer_number')))
        lines.append(self._format_field('customerName', extracted_fields.get('customer_name')))
        lines.append(self._format_field('customer_address1', extracted_fields.get('customer_address1')))
        lines.append(self._format_field('customer_city', extracted_fields.get('customer_city')))
        lines.append(self._format_field('customer_state', extracted_fields.get('customer_state')))
        lines.append(self._format_field('customer_zip', extracted_fields.get('customer_zip')))
        lines.append('')
        
        # AMOUNT INFORMATION section
        lines.append('RECEIPT: AMOUNT INFORMATION')
        lines.append(self._format_field('amountSubtotal', self._format_decimal(extracted_fields.get('amount_subtotal') or extracted_fields.get('subtotal'))))
        lines.append(self._format_field('amountTaxable', self._format_decimal(extracted_fields.get('amount_taxable'))))
        lines.append(self._format_field('taxRate', self._format_decimal(extracted_fields.get('tax_rate'), precision=6)))
        lines.append(self._format_field('amountTax', self._format_decimal(extracted_fields.get('tax_amount'))))
        lines.append(self._format_field('amountDiscountPercent', self._format_decimal(extracted_fields.get('amount_discount_percent'), default=Decimal('0'))))
        lines.append(self._format_field('balancePrior', self._format_decimal(extracted_fields.get('balance_prior'), default=Decimal('0'))))
        lines.append(self._format_field('amountTotal', self._format_decimal(extracted_fields.get('total_amount'))))
        lines.append(self._format_field('amountDueAmt', self._format_decimal(extracted_fields.get('amount_due_amt'))))
        lines.append(self._format_field('amountBalanceDue', self._format_decimal(extracted_fields.get('amount_balance_due'), default=Decimal('0'))))
        lines.append('')
        
        # RECEIPT LINES section
        lines.append('RECEIPT LINES:')
        line_items = extracted_fields.get('line_items', [])
        
        if line_items:
            # Generate header
            header = self._format_line_header()
            lines.append(header)
            
            # Generate data rows
            for i, item in enumerate(line_items, 1):
                line_row = self._format_line_row(i, item)
                lines.append(line_row)
        
        content = '\n'.join(lines)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return content
    
    def _format_field(self, field_name: str, value: Any) -> str:
        """
        Format a field name-value pair with justified alignment.
        
        Args:
            field_name: Field name (left-aligned)
            value: Field value (right-aligned)
            
        Returns:
            Formatted line string
        """
        if value is None:
            value_str = 'NULL'
        elif isinstance(value, str) and value.startswith('<'):
            # Placeholder value
            value_str = value
        else:
            value_str = str(value)
        
        # Format: field_name: value (right-aligned)
        return f"{field_name:<{self.field_name_width}}:{value_str:>{self.field_value_width}}"
    
    def _format_decimal(self, value: Any, precision: int = 4, default: Optional[Decimal] = None) -> str:
        """
        Format a decimal value with specified precision.
        
        Args:
            value: Value to format (Decimal, float, str, or None)
            precision: Number of decimal places
            default: Default value if value is None
            
        Returns:
            Formatted decimal string
        """
        if value is None:
            if default is not None:
                value = default
            else:
                return 'NULL'
        
        try:
            if isinstance(value, str):
                value = Decimal(value)
            elif isinstance(value, (int, float)):
                value = Decimal(str(value))
            
            return f"{value:.{precision}f}"
        except (ValueError, TypeError):
            return 'NULL'
    
    def _format_line_header(self) -> str:
        """
        Format receipt lines table header.
        
        Returns:
            Formatted header line
        """
        parts = [
            f"{'Line':<{self.line_column_widths['line']}}",
            f"{'Description':<{self.line_column_widths['description']}}",
            f"{'qty':>{self.line_column_widths['qty']}}",
            f"{'UOM':<{self.line_column_widths['uom']}}",
            f"{'Price':>{self.line_column_widths['price']}}",
            f"{'Subtotal':>{self.line_column_widths['subtotal']}}",
            f"{'taxable_amount':>{self.line_column_widths['taxable_amount']}}",
            f"{'codeCSI':<{self.line_column_widths['code_csi']}}",
        ]
        return '  '.join(parts)
    
    def _format_line_row(self, line_number: int, item: Dict[str, Any]) -> str:
        """
        Format a receipt line item row.
        
        Args:
            line_number: Line number
            item: Line item dictionary
            
        Returns:
            Formatted line row string
        """
        description = item.get('description', '')[:self.line_column_widths['description']]
        qty = self._format_decimal(item.get('quantity', 0))
        uom = item.get('uom', 'NULL') or 'NULL'
        price = self._format_decimal(item.get('unit_price', 0))
        subtotal = self._format_decimal(item.get('line_total', 0))
        taxable = self._format_decimal(item.get('taxable_amount', 0))
        csi = item.get('code_csi', 'NULL') or 'NULL'
        
        parts = [
            f"{line_number:>{self.line_column_widths['line']}}",
            f"{description:<{self.line_column_widths['description']}}",
            f"{qty:>{self.line_column_widths['qty']}}",
            f"{uom:<{self.line_column_widths['uom']}}",
            f"{price:>{self.line_column_widths['price']}}",
            f"{subtotal:>{self.line_column_widths['subtotal']}}",
            f"{taxable:>{self.line_column_widths['taxable_amount']}}",
            f"{csi:<{self.line_column_widths['code_csi']}}",
        ]
        return '  '.join(parts)
    
    def compare_extraction_to_expected(
        self,
        extracted_fields: Dict[str, Any],
        expected_file_path: str
    ) -> Dict[str, Any]:
        """
        Compare extracted fields to expected values from accuracy check file.
        
        Args:
            extracted_fields: Extracted fields from OCR
            expected_file_path: Path to accuracy check file with expected values
            
        Returns:
            Comparison results dictionary
        """
        parser = AccuracyCheckParser()
        expected = parser.parse(expected_file_path)
        
        comparison = {
            'metadata': self._compare_section(extracted_fields, expected.get('metadata', {}), 'metadata'),
            'vendor': self._compare_section(extracted_fields, expected.get('vendor', {}), 'vendor'),
            'customer': self._compare_section(extracted_fields, expected.get('customer', {}), 'customer'),
            'amounts': self._compare_section(extracted_fields, expected.get('amounts', {}), 'amounts'),
            'lines': self._compare_lines(extracted_fields.get('line_items', []), expected.get('lines', [])),
        }
        
        # Calculate overall accuracy
        total_fields = 0
        matching_fields = 0
        
        for section_name, section_results in comparison.items():
            if section_name == 'lines':
                for line_result in section_results:
                    total_fields += len(line_result.get('fields', {}))
                    matching_fields += sum(1 for match in line_result.get('fields', {}).values() if match)
            else:
                total_fields += len(section_results.get('fields', {}))
                matching_fields += sum(1 for match in section_results.get('fields', {}).values() if match)
        
        comparison['overall_accuracy'] = matching_fields / total_fields if total_fields > 0 else 0.0
        comparison['total_fields'] = total_fields
        comparison['matching_fields'] = matching_fields
        
        return comparison
    
    def _compare_section(
        self,
        extracted: Dict[str, Any],
        expected: Dict[str, Any],
        section_name: str
    ) -> Dict[str, Any]:
        """Compare a section of fields."""
        field_mapping = {
            'metadata': {},
            'vendor': {
                'vendorName': 'vendor',
                'vendor_address1': 'vendor_address1',
                'vendor_address2': 'vendor_address2',
                'vendor_city': 'vendor_city',
                'vendor_state': 'vendor_state',
                'vendor_zip': 'vendor_zip',
                'salesRep': 'sales_rep',
            },
            'customer': {
                'customerNumber': 'customer_number',
                'customerName': 'customer_name',
                'customer_address1': 'customer_address1',
                'customer_city': 'customer_city',
                'customer_state': 'customer_state',
                'customer_zip': 'customer_zip',
            },
            'amounts': {
                'amountSubtotal': 'amount_subtotal',
                'amountTaxable': 'amount_taxable',
                'taxRate': 'tax_rate',
                'amountTax': 'tax_amount',
                'amountDiscountPercent': 'amount_discount_percent',
                'balancePrior': 'balance_prior',
                'amountTotal': 'total_amount',
                'amountDueAmt': 'amount_due_amt',
                'amountBalanceDue': 'amount_balance_due',
            },
        }
        
        mapping = field_mapping.get(section_name, {})
        results = {'fields': {}}
        
        for expected_key, extracted_key in mapping.items():
            expected_value = expected.get(expected_key)
            extracted_value = extracted.get(extracted_key)
            
            # Skip if expected value is a placeholder
            if expected_value is None or (isinstance(expected_value, str) and expected_value.startswith('<')):
                continue
            
            # Compare values
            match = self._values_match(extracted_value, expected_value)
            results['fields'][expected_key] = {
                'match': match,
                'expected': expected_value,
                'extracted': extracted_value,
            }
        
        return results
    
    def _compare_lines(
        self,
        extracted_lines: List[Dict[str, Any]],
        expected_lines: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Compare line items."""
        results = []
        
        max_lines = max(len(extracted_lines), len(expected_lines))
        
        for i in range(max_lines):
            extracted = extracted_lines[i] if i < len(extracted_lines) else {}
            expected = expected_lines[i] if i < len(expected_lines) else {}
            
            line_result = {
                'line_number': i + 1,
                'fields': {},
            }
            
            # Compare each field
            for field in ['description', 'qty', 'uom', 'price', 'subtotal', 'taxable_amount', 'code_csi']:
                expected_key = field
                extracted_key = field if field != 'subtotal' else 'line_total'
                extracted_key = extracted_key if extracted_key != 'code_csi' else 'csi_code_id'
                
                expected_value = expected.get(expected_key)
                extracted_value = extracted.get(extracted_key)
                
                if expected_value is None:
                    continue
                
                match = self._values_match(extracted_value, expected_value)
                line_result['fields'][field] = {
                    'match': match,
                    'expected': expected_value,
                    'extracted': extracted_value,
                }
            
            results.append(line_result)
        
        return results
    
    def _values_match(self, value1: Any, value2: Any, tolerance: Decimal = Decimal('0.01')) -> bool:
        """Check if two values match (with tolerance for decimals)."""
        if value1 is None and value2 is None:
            return True
        if value1 is None or value2 is None:
            return False
        
        # Convert to Decimal for comparison
        try:
            if isinstance(value1, str):
                value1 = Decimal(value1.replace(',', ''))
            elif isinstance(value1, (int, float)):
                value1 = Decimal(str(value1))
            
            if isinstance(value2, str):
                value2 = Decimal(value2.replace(',', ''))
            elif isinstance(value2, (int, float)):
                value2 = Decimal(str(value2))
            
            return abs(value1 - value2) <= tolerance
        except (ValueError, TypeError):
            # String comparison
            return str(value1).strip() == str(value2).strip()


def main():
    """Main entry point for accuracy check tool."""
    parser = argparse.ArgumentParser(description='Generate and compare accuracy check files')
    parser.add_argument('command', choices=['generate', 'compare'], help='Command to execute')
    parser.add_argument('--image', help='Path to receipt image file (for generate)')
    parser.add_argument('--extracted', help='Path to JSON file with extracted fields (for generate/compare)')
    parser.add_argument('--expected', help='Path to accuracy check text file with expected values (for compare)')
    parser.add_argument('--output', help='Path to output file (for generate)')
    
    args = parser.parse_args()
    
    generator = AccuracyCheckGenerator()
    
    if args.command == 'generate':
        if args.image:
            # Extract from image
            extractor = DocumentExtractor()
            result = extractor.extract(args.image)
            extracted_fields = result.get('fields', {})
        elif args.extracted:
            # Load from JSON
            with open(args.extracted, 'r') as f:
                extracted_fields = json.load(f)
        else:
            print("Error: Must provide --image or --extracted")
            sys.exit(1)
        
        output_path = args.output or 'accuracy_check.txt'
        content = generator.generate_from_extraction(extracted_fields, output_path)
        print(f"Generated accuracy check file: {output_path}")
        
    elif args.command == 'compare':
        if not args.extracted or not args.expected:
            print("Error: Must provide --extracted and --expected for compare")
            sys.exit(1)
        
        # Load extracted fields
        with open(args.extracted, 'r') as f:
            extracted_fields = json.load(f)
        
        # Compare
        comparison = generator.compare_extraction_to_expected(extracted_fields, args.expected)
        
        # Print results
        print(f"\nAccuracy Check Results:")
        print(f"Overall Accuracy: {comparison['overall_accuracy']:.2%}")
        print(f"Matching Fields: {comparison['matching_fields']}/{comparison['total_fields']}")
        print(f"\nDetailed Results:")
        print(json.dumps(comparison, indent=2, default=str))


if __name__ == '__main__':
    main()
