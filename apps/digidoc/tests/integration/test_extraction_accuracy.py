"""
Semi-Automated Extraction Accuracy Validation

Tests extraction accuracy by:
1. Processing test documents via queue API
2. Comparing extracted fields to expected values
3. Generating validation report
"""

import sys
import os
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add ocr_service to path
digidoc_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(digidoc_root))

from ocr_service.tools.check_extraction_accuracy import AccuracyCheckGenerator


class ExtractionAccuracyValidator:
    """Validates extraction accuracy against expected values."""
    
    def __init__(self, api_base_url: str = "http://localhost:8001"):
        self.api_base_url = api_base_url
        self.generator = AccuracyCheckGenerator()
    
    def process_document_via_queue(
        self,
        file_path: str,
        calling_app_id: str = "validation_test",
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Process a document via queue API and wait for results.
        
        Args:
            file_path: Absolute path to document image
            calling_app_id: Calling application ID
            timeout: Maximum time to wait for completion (seconds)
            
        Returns:
            Extraction result dictionary
        """
        # Verify file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        # Enqueue task
        print(f"\n📤 Enqueueing document: {file_path}")
        response = requests.post(
            f"{self.api_base_url}/api/digidoc/queue",
            json={
                "file_path": file_path,
                "calling_app_id": calling_app_id
            },
            timeout=10
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to enqueue: {response.status_code} - {response.text}")
        
        task_data = response.json()
        task_id = task_data.get('task_id')
        print(f"   Task ID: {task_id}")
        
        # Poll for completion
        print("   Waiting for processing...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            status_response = requests.get(
                f"{self.api_base_url}/api/digidoc/status/{task_id}",
                timeout=10
            )
            
            if status_response.status_code != 200:
                raise Exception(f"Failed to get status: {status_response.status_code}")
            
            status_data = status_response.json()
            status = status_data.get('status')
            
            if status == 'completed':
                print("   ✅ Processing complete")
                return status_data.get('result', {})
            elif status == 'failed':
                error = status_data.get('error', 'Unknown error')
                raise Exception(f"Processing failed: {error}")
            
            time.sleep(1)
        
        raise TimeoutError(f"Processing timed out after {timeout} seconds")
    
    def extract_directly(self, file_path: str) -> Dict[str, Any]:
        """
        Extract fields directly (bypasses queue, faster for testing).
        
        Args:
            file_path: Absolute path to document image
            
        Returns:
            Extraction result dictionary
        """
        from ocr_service.extractors.document_extractor import DocumentExtractor
        
        print(f"\n🔍 Extracting directly from: {file_path}")
        extractor = DocumentExtractor()
        result = extractor.extract(file_path)
        print("   ✅ Extraction complete")
        return result
    
    def compare_to_expected(
        self,
        extracted_fields: Dict[str, Any],
        expected_file_path: str
    ) -> Dict[str, Any]:
        """
        Compare extracted fields to expected values.
        
        Args:
            extracted_fields: Extracted fields dictionary
            expected_file_path: Path to accuracy check file with expected values
            
        Returns:
            Comparison results dictionary
        """
        print(f"\n📊 Comparing to expected values: {expected_file_path}")
        comparison = self.generator.compare_extraction_to_expected(
            extracted_fields,
            expected_file_path
        )
        
        accuracy = comparison.get('overall_accuracy', 0.0)
        matching = comparison.get('matching_fields', 0)
        total = comparison.get('total_fields', 0)
        
        print(f"   Overall Accuracy: {accuracy:.2%}")
        print(f"   Matching Fields: {matching}/{total}")
        
        return comparison
    
    def validate_document(
        self,
        document_path: str,
        expected_path: Optional[str] = None,
        use_queue: bool = False,
        save_extracted: bool = True
    ) -> Dict[str, Any]:
        """
        Validate a single document.
        
        Args:
            document_path: Path to document image
            expected_path: Path to expected values file (optional)
            use_queue: If True, use queue API; if False, extract directly
            save_extracted: If True, save extracted fields to JSON
            
        Returns:
            Validation results dictionary
        """
        document_name = Path(document_path).stem
        
        # Extract fields
        if use_queue:
            result = self.process_document_via_queue(document_path)
            extracted_fields = result.get('extracted_fields', {})
        else:
            result = self.extract_directly(document_path)
            extracted_fields = result.get('fields', {})
        
        # Save extracted fields if requested
        if save_extracted:
            extracted_dir = digidoc_root.parent.parent / "hq" / "receipt_samples" / "accuracy_checks" / "extracted"
            extracted_dir.mkdir(parents=True, exist_ok=True)
            extracted_file = extracted_dir / f"{document_name}_extracted.json"
            
            with open(extracted_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"   💾 Saved extracted fields: {extracted_file}")
        
        # Compare if expected values provided
        comparison = None
        if expected_path and os.path.exists(expected_path):
            comparison = self.compare_to_expected(extracted_fields, expected_path)
        elif expected_path:
            print(f"   ⚠️  Expected file not found: {expected_path}")
        
        return {
            'document': document_path,
            'document_name': document_name,
            'extracted_fields': extracted_fields,
            'extraction_result': result,
            'comparison': comparison,
            'extracted_file': str(extracted_file) if save_extracted else None
        }
    
    def validate_batch(
        self,
        test_documents: List[Dict[str, str]],
        use_queue: bool = False
    ) -> Dict[str, Any]:
        """
        Validate multiple documents.
        
        Args:
            test_documents: List of dicts with 'document' and optionally 'expected' keys
            use_queue: If True, use queue API; if False, extract directly
            
        Returns:
            Batch validation results
        """
        print("=" * 80)
        print("Extraction Accuracy Validation - Batch Mode")
        print("=" * 80)
        
        results = []
        for i, doc_config in enumerate(test_documents, 1):
            document_path = doc_config['document']
            expected_path = doc_config.get('expected')
            
            print(f"\n{'=' * 80}")
            print(f"Document {i}/{len(test_documents)}: {Path(document_path).name}")
            print(f"{'=' * 80}")
            
            try:
                result = self.validate_document(
                    document_path,
                    expected_path,
                    use_queue=use_queue
                )
                results.append(result)
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    'document': document_path,
                    'error': str(e)
                })
        
        # Generate summary
        summary = self._generate_summary(results)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'summary': summary
        }
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from validation results."""
        total = len(results)
        successful = sum(1 for r in results if 'error' not in r)
        with_comparison = sum(1 for r in results if r.get('comparison') is not None)
        
        accuracies = [
            r['comparison']['overall_accuracy']
            for r in results
            if r.get('comparison') is not None
        ]
        
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.0
        
        return {
            'total_documents': total,
            'successful_extractions': successful,
            'with_comparison': with_comparison,
            'average_accuracy': avg_accuracy,
            'min_accuracy': min(accuracies) if accuracies else None,
            'max_accuracy': max(accuracies) if accuracies else None
        }
    
    def save_report(self, validation_results: Dict[str, Any], output_path: str):
        """Save validation report to file."""
        report_dir = Path(output_path).parent
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON results
        json_path = Path(output_path).with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump(validation_results, f, indent=2, default=str)
        
        # Generate markdown report
        md_path = Path(output_path).with_suffix('.md')
        with open(md_path, 'w') as f:
            f.write("# Extraction Accuracy Validation Report\n\n")
            f.write(f"**Date**: {validation_results['timestamp']}\n\n")
            
            summary = validation_results['summary']
            f.write("## Summary\n\n")
            f.write(f"- **Total Documents**: {summary['total_documents']}\n")
            f.write(f"- **Successful Extractions**: {summary['successful_extractions']}\n")
            f.write(f"- **With Comparison**: {summary['with_comparison']}\n")
            if summary['average_accuracy']:
                f.write(f"- **Average Accuracy**: {summary['average_accuracy']:.2%}\n")
                f.write(f"- **Min Accuracy**: {summary['min_accuracy']:.2%}\n")
                f.write(f"- **Max Accuracy**: {summary['max_accuracy']:.2%}\n")
            
            f.write("\n## Detailed Results\n\n")
            for i, result in enumerate(validation_results['results'], 1):
                f.write(f"### Document {i}: {result.get('document_name', 'Unknown')}\n\n")
                
                if 'error' in result:
                    f.write(f"**Error**: {result['error']}\n\n")
                    continue
                
                if result.get('comparison'):
                    comp = result['comparison']
                    f.write(f"- **Accuracy**: {comp['overall_accuracy']:.2%}\n")
                    f.write(f"- **Matching Fields**: {comp['matching_fields']}/{comp['total_fields']}\n")
                
                if result.get('extracted_file'):
                    f.write(f"- **Extracted Fields**: `{result['extracted_file']}`\n")
                
                f.write("\n")
        
        print(f"\n📄 Report saved:")
        print(f"   JSON: {json_path}")
        print(f"   Markdown: {md_path}")


def main():
    """Main entry point for validation script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate extraction accuracy')
    parser.add_argument('--document', help='Path to single document image')
    parser.add_argument('--expected', help='Path to expected values file')
    parser.add_argument('--config', help='Path to JSON config file with test documents')
    parser.add_argument('--use-queue', action='store_true', help='Use queue API instead of direct extraction')
    parser.add_argument('--api-url', default='http://localhost:8001', help='API base URL')
    parser.add_argument('--output', help='Path to save validation report')
    
    args = parser.parse_args()
    
    validator = ExtractionAccuracyValidator(api_base_url=args.api_url)
    
    if args.config:
        # Batch mode from config file
        with open(args.config, 'r') as f:
            config = json.load(f)
        test_documents = config.get('test_documents', [])
        
        results = validator.validate_batch(test_documents, use_queue=args.use_queue)
        
        output_path = args.output or f"logs/testing/extraction_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        validator.save_report(results, output_path)
    
    elif args.document:
        # Single document mode
        result = validator.validate_document(
            args.document,
            args.expected,
            use_queue=args.use_queue
        )
        
        if result.get('comparison'):
            print("\n" + "=" * 80)
            print("Validation Complete")
            print("=" * 80)
            comp = result['comparison']
            print(f"Overall Accuracy: {comp['overall_accuracy']:.2%}")
            print(f"Matching Fields: {comp['matching_fields']}/{comp['total_fields']}")
    
    else:
        parser.print_help()
        print("\nExample usage:")
        print("  # Single document:")
        print("  python3 test_extraction_accuracy.py --document /path/to/image.png --expected /path/to/expected.txt")
        print("\n  # Batch from config:")
        print("  python3 test_extraction_accuracy.py --config test_documents.json --output validation_report.md")


if __name__ == '__main__':
    main()

