#!/usr/bin/env python3
"""
File Storage Utilities Test Script

Tests file storage utilities to verify:
- Queue item directory paths are correct
- Directories are created correctly
- File saving works
- All paths use config values
"""

import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ocr_service.utils.file_utils import (
    get_queue_item_directory,
    ensure_queue_item_directory,
    save_original_file,
    save_preprocessed_image,
    get_processed_directory,
    get_failed_directory,
    get_templates_directory
)
from ocr_service.config import get_config


def test_path_retrieval():
    """Test that path retrieval functions work."""
    print("=" * 60)
    print("Test 1: Path Retrieval")
    print("=" * 60)
    
    config = get_config()
    storage_base = config.paths.storage_base
    
    print(f"  storage_base: {storage_base}")
    
    # Test queue item directory
    queue_item_id = "test-123"
    queue_dir = get_queue_item_directory(queue_item_id)
    print(f"  queue_item_directory: {queue_dir}")
    
    # Verify it uses storage_base
    assert storage_base in queue_dir, "Queue directory should contain storage_base"
    assert queue_item_id in queue_dir, "Queue directory should contain queue_item_id"
    print("  ✓ Queue item directory path is correct")
    
    # Test other directories
    processed_dir = get_processed_directory()
    failed_dir = get_failed_directory()
    templates_dir = get_templates_directory()
    
    print(f"  processed_directory: {processed_dir}")
    print(f"  failed_directory: {failed_dir}")
    print(f"  templates_directory: {templates_dir}")
    
    # Verify all use storage_base
    assert storage_base in processed_dir, "Processed directory should contain storage_base"
    assert storage_base in failed_dir, "Failed directory should contain storage_base"
    assert storage_base in templates_dir, "Templates directory should contain storage_base"
    
    print("  ✓ All directory paths use storage_base from config")
    return True


def test_directory_creation():
    """Test that directories are created correctly."""
    print("\n" + "=" * 60)
    print("Test 2: Directory Creation")
    print("=" * 60)
    
    queue_item_id = "test-create-456"
    queue_dir = ensure_queue_item_directory(queue_item_id)
    
    print(f"  Created directory: {queue_dir}")
    
    # Verify directory exists
    assert os.path.exists(queue_dir), "Queue item directory should exist"
    assert os.path.isdir(queue_dir), "Queue item directory should be a directory"
    print("  ✓ Directory created successfully")
    
    # Test that calling again doesn't fail
    queue_dir2 = ensure_queue_item_directory(queue_item_id)
    assert queue_dir == queue_dir2, "Should return same path on second call"
    print("  ✓ Idempotent: calling again returns same path")
    
    return True


def test_file_saving():
    """Test that file saving works."""
    print("\n" + "=" * 60)
    print("Test 3: File Saving")
    print("=" * 60)
    
    queue_item_id = "test-save-789"
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
        tmp.write("Test content for original file")
        tmp_path = tmp.name
    
    try:
        # Test saving original file
        saved_original = save_original_file(tmp_path, queue_item_id)
        print(f"  Saved original file: {saved_original}")
        
        assert os.path.exists(saved_original), "Saved original file should exist"
        assert "original.txt" in saved_original, "Should have original extension"
        print("  ✓ Original file saved correctly")
        
        # Test saving preprocessed image (requires OpenCV)
        try:
            import cv2
            import numpy as np
            
            # Create a simple test image
            test_image = np.zeros((100, 100), dtype=np.uint8)
            test_image[25:75, 25:75] = 255  # White square
            
            saved_preprocessed = save_preprocessed_image(test_image, queue_item_id)
            print(f"  Saved preprocessed image: {saved_preprocessed}")
            
            assert os.path.exists(saved_preprocessed), "Saved preprocessed image should exist"
            assert saved_preprocessed.endswith("preprocessed.png"), "Should be preprocessed.png"
            print("  ✓ Preprocessed image saved correctly")
            
        except ImportError:
            print("  ⚠ OpenCV not available, skipping preprocessed image test")
            print("  (This is expected if dependencies aren't installed)")
        
        return True
        
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_path_structure():
    """Test that path structure matches expected format."""
    print("\n" + "=" * 60)
    print("Test 4: Path Structure")
    print("=" * 60)
    
    queue_item_id = "test-structure-abc"
    queue_dir = get_queue_item_directory(queue_item_id)
    
    # Verify structure: {storage_base}/queue/{queue_item_id}/
    config = get_config()
    storage_base = config.paths.storage_base
    expected_queue_base = config.paths.queue_directory
    
    print(f"  Expected queue base: {expected_queue_base}")
    print(f"  Queue item directory: {queue_dir}")
    
    # Verify it starts with queue base
    assert queue_dir.startswith(expected_queue_base), "Should start with queue_directory"
    assert queue_dir.endswith(os.sep) or queue_dir.endswith('/'), "Should end with separator"
    
    # Verify queue_item_id is in path
    assert queue_item_id in queue_dir, "Should contain queue_item_id"
    
    print("  ✓ Path structure is correct")
    return True


def main():
    """Run all file storage utility tests."""
    print("\n" + "=" * 60)
    print("File Storage Utilities Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Path Retrieval", test_path_retrieval),
        ("Directory Creation", test_directory_creation),
        ("File Saving", test_file_saving),
        ("Path Structure", test_path_structure),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n  ✗ Test '{test_name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  ✓ All file storage utility tests passed!")
        return 0
    else:
        print(f"\n  ✗ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
