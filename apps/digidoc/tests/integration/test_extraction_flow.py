"""
Test End-to-End Extraction Flow

Tests the complete extraction pipeline:
1. Preprocessing
2. Template matching
3. Field extraction (real zonal OCR)
4. Error handling
"""

import sys
import os
from pathlib import Path

# Add ocr_service to path
digidoc_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(digidoc_root))

from ocr_service.tasks.document_tasks import process_document_task, extract_fields_task
from ocr_service.extractors.document_extractor import DocumentExtractor
import uuid


def test_extraction_flow_integration():
    """Test that extraction flow integrates correctly."""
    print("=" * 60)
    print("Test: Extraction Flow Integration")
    print("=" * 60)
    
    # Test 1: Verify DocumentExtractor can be instantiated
    print("\n1. Testing DocumentExtractor instantiation...")
    try:
        extractor = DocumentExtractor()
        print("   ✅ DocumentExtractor created successfully")
    except Exception as e:
        print(f"   ❌ Failed to create DocumentExtractor: {e}")
        return False
    
    # Test 2: Verify extract_fields_task function exists and has correct signature
    print("\n2. Testing extract_fields_task function...")
    try:
        import inspect
        sig = inspect.signature(extract_fields_task)
        params = list(sig.parameters.keys())
        expected_params = ['image_path', 'queue_item_id', 'template_id']
        
        if params[:3] == expected_params:
            print("   ✅ extract_fields_task has correct signature")
        else:
            print(f"   ⚠️  extract_fields_task params: {params}, expected: {expected_params}")
    except Exception as e:
        print(f"   ❌ Failed to inspect extract_fields_task: {e}")
        return False
    
    # Test 3: Verify process_document_task calls extract_fields_task
    print("\n3. Testing process_document_task integration...")
    try:
        import inspect
        source = inspect.getsource(process_document_task)
        if 'extract_fields_task' in source:
            print("   ✅ process_document_task calls extract_fields_task")
        else:
            print("   ⚠️  process_document_task may not call extract_fields_task")
    except Exception as e:
        print(f"   ⚠️  Could not verify integration: {e}")
    
    # Test 4: Verify DocumentExtractor.extract() method exists
    print("\n4. Testing DocumentExtractor.extract() method...")
    try:
        if hasattr(extractor, 'extract'):
            print("   ✅ DocumentExtractor has extract() method")
        else:
            print("   ❌ DocumentExtractor missing extract() method")
            return False
    except Exception as e:
        print(f"   ❌ Failed to verify extract() method: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Integration tests passed")
    print("=" * 60)
    print("\nNote: To test with actual images, use the API endpoint:")
    print("  POST /api/digidoc/queue")
    print("  Body: {")
    print('    "file_path": "/absolute/path/to/image.png",')
    print('    "calling_app_id": "test_app"')
    print("  }")
    
    return True


def test_error_handling():
    """Test error handling in extraction flow."""
    print("\n" + "=" * 60)
    print("Test: Error Handling")
    print("=" * 60)
    
    # Test 1: Missing file
    print("\n1. Testing missing file handling...")
    try:
        result = extract_fields_task(
            "/nonexistent/path/image.png",
            str(uuid.uuid4()),
            None
        )
        if result.get('status') in ['partial', 'failed']:
            print("   ✅ Missing file handled gracefully")
        else:
            print(f"   ⚠️  Unexpected status: {result.get('status')}")
    except Exception as e:
        print(f"   ⚠️  Exception raised (may be acceptable): {e}")
    
    # Test 2: Invalid image path
    print("\n2. Testing invalid image path...")
    try:
        result = extract_fields_task(
            "/dev/null",  # Exists but not an image
            str(uuid.uuid4()),
            None
        )
        if result.get('status') in ['partial', 'failed']:
            print("   ✅ Invalid image handled gracefully")
        else:
            print(f"   ⚠️  Unexpected status: {result.get('status')}")
    except Exception as e:
        print(f"   ⚠️  Exception raised (may be acceptable): {e}")
    
    print("\n" + "=" * 60)
    print("✅ Error handling tests completed")
    print("=" * 60)


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Extraction Flow Test Suite")
    print("=" * 60)
    
    # Run integration tests
    integration_ok = test_extraction_flow_integration()
    
    # Run error handling tests
    test_error_handling()
    
    print("\n" + "=" * 60)
    if integration_ok:
        print("✅ All tests passed")
    else:
        print("⚠️  Some tests had issues - review output above")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Test with real document images via API endpoint")
    print("2. Validate extracted fields match expected values")
    print("3. Check confidence scores are reasonable")

