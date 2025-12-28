#!/usr/bin/env python3
"""
Full Pipeline Test Script

Tests the complete DigiDoc pipeline:
1. Configuration loading
2. Image preprocessing
3. Structural fingerprinting
4. Template matching
5. Visualization generation
6. File storage
7. Queue utilities

Run with: python3 ocr_service/test_full_pipeline.py
"""

import os
import sys
import uuid
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("WARNING: OpenCV not available. Some tests will be skipped.")

from ocr_service.config import get_config, reload_config
from ocr_service.utils.file_utils import (
    ensure_queue_item_directory,
    save_original_file,
    save_preprocessed_image,
    get_queue_item_directory
)

# Import modules that require cv2 only if available
try:
    from ocr_service.utils.image_preprocessing import ImagePreprocessor
    PREPROCESSING_AVAILABLE = True
except ImportError:
    PREPROCESSING_AVAILABLE = False
    print("WARNING: Image preprocessing not available (cv2 required)")

try:
    from ocr_service.matching.structural import compute_structural_fingerprint, compare_fingerprints
    MATCHING_AVAILABLE = True
except ImportError:
    MATCHING_AVAILABLE = False
    print("WARNING: Matching not available (cv2 required)")

try:
    from ocr_service.tasks.matching_task import match_template, generate_match_visualization
    from ocr_service.tasks.process_for_visualization import process_queue_item_for_visualization
    TASKS_AVAILABLE = True
except ImportError:
    TASKS_AVAILABLE = False
    print("WARNING: Task processing not available (cv2 required)")

from ocr_service.gui.utils.queue_utils import get_queue_item_info, list_queue_items, save_match_metadata


def test_config_loading():
    """Test 1: Configuration loading"""
    print("\n" + "=" * 60)
    print("Test 1: Configuration Loading")
    print("=" * 60)
    
    try:
        config = reload_config()
        
        # Check all required sections
        required_sections = ['thresholds', 'scoring', 'preprocessing', 'paths', 'api', 'queue', 'database', 'llm']
        missing_sections = []
        
        for section in required_sections:
            if not hasattr(config, section):
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ FAILED: Missing sections: {missing_sections}")
            return False
        
        # Check some key values
        assert config.preprocessing.target_dpi > 0, "target_dpi must be positive"
        assert config.paths.storage_base, "storage_base must be set"
        
        print("✅ PASSED: Configuration loads correctly")
        print(f"   - Storage base: {config.paths.storage_base}")
        print(f"   - Target DPI: {config.preprocessing.target_dpi}")
        print(f"   - Queue directory: {config.paths.queue_directory}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_utils():
    """Test 2: File storage utilities"""
    print("\n" + "=" * 60)
    print("Test 2: File Storage Utilities")
    print("=" * 60)
    
    try:
        test_queue_item_id = f"test_{uuid.uuid4().hex[:8]}"
        
        # Test directory creation
        queue_item_dir = ensure_queue_item_directory(test_queue_item_id)
        assert os.path.exists(queue_item_dir), "Queue item directory should exist"
        print(f"✅ Queue item directory created: {queue_item_dir}")
        
        # Test directory retrieval
        retrieved_dir = get_queue_item_directory(test_queue_item_id)
        assert retrieved_dir == queue_item_dir, "Directory paths should match"
        print("✅ Directory retrieval works")
        
        # Cleanup
        if os.path.exists(queue_item_dir):
            import shutil
            shutil.rmtree(queue_item_dir)
            print("✅ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_preprocessing():
    """Test 3: Image preprocessing"""
    print("\n" + "=" * 60)
    print("Test 3: Image Preprocessing")
    print("=" * 60)
    
    if not CV2_AVAILABLE or not PREPROCESSING_AVAILABLE:
        print("⏭️  SKIPPED: OpenCV or preprocessing module not available")
        return True
    
    try:
        # Create a test image
        test_image = np.ones((500, 500), dtype=np.uint8) * 255
        # Add some content
        cv2.rectangle(test_image, (100, 100), (400, 400), 0, -1)
        cv2.putText(test_image, "TEST", (200, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, 255, 3)
        
        # Preprocess
        preprocessor = ImagePreprocessor()
        preprocessed = preprocessor.preprocess(test_image)
        
        assert preprocessed is not None, "Preprocessed image should not be None"
        assert preprocessed.shape[0] > 0 and preprocessed.shape[1] > 0, "Preprocessed image should have valid dimensions"
        
        print(f"✅ Preprocessing successful")
        print(f"   - Original size: {test_image.shape}")
        print(f"   - Preprocessed size: {preprocessed.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_structural_fingerprinting():
    """Test 4: Structural fingerprinting"""
    print("\n" + "=" * 60)
    print("Test 4: Structural Fingerprinting")
    print("=" * 60)
    
    if not CV2_AVAILABLE or not MATCHING_AVAILABLE:
        print("⏭️  SKIPPED: OpenCV or matching module not available")
        return True
    
    try:
        # Create a test image with zones
        test_image = np.ones((600, 400), dtype=np.uint8) * 255
        # Header zone
        cv2.rectangle(test_image, (50, 50), (350, 150), 0, -1)
        # Table zone
        cv2.rectangle(test_image, (50, 200), (350, 450), 0, -1)
        # Footer zone
        cv2.rectangle(test_image, (50, 500), (350, 550), 0, -1)
        
        # Compute fingerprint
        fingerprint = compute_structural_fingerprint(test_image)
        
        assert fingerprint is not None, "Fingerprint should not be None"
        assert 'zones' in fingerprint, "Fingerprint should have zones"
        assert 'image_width' in fingerprint, "Fingerprint should have image_width"
        assert 'image_height' in fingerprint, "Fingerprint should have image_height"
        
        print(f"✅ Fingerprint computed successfully")
        print(f"   - Image size: {fingerprint['image_width']} × {fingerprint['image_height']}")
        print(f"   - Zones detected: {len(fingerprint['zones'])}")
        
        # Test fingerprint comparison
        fingerprint2 = compute_structural_fingerprint(test_image)
        score = compare_fingerprints(fingerprint, fingerprint2)
        
        assert 0.0 <= score <= 1.0, "Match score should be between 0 and 1"
        assert score > 0.9, "Identical images should have high match score"
        
        print(f"✅ Fingerprint comparison works (score: {score:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_queue_utilities():
    """Test 5: Queue utilities"""
    print("\n" + "=" * 60)
    print("Test 5: Queue Utilities")
    print("=" * 60)
    
    try:
        # Test listing queue items
        queue_items = list_queue_items()
        print(f"✅ Queue listing works ({len(queue_items)} items found)")
        
        # Test getting queue item info (if any exist)
        if queue_items:
            test_item = queue_items[0]
            item_info = get_queue_item_info(test_item['queue_item_id'])
            if item_info:
                print(f"✅ Queue item info retrieval works")
                print(f"   - Item ID: {item_info['queue_item_id']}")
                print(f"   - Status: {item_info['status']}")
        
        # Test saving metadata
        test_queue_item_id = f"test_meta_{uuid.uuid4().hex[:8]}"
        test_metadata = {
            'matched_template_id': 'test_template',
            'match_score': 0.85,
            'template_name': 'Test Template'
        }
        
        success = save_match_metadata(test_queue_item_id, test_metadata)
        if success:
            print("✅ Metadata saving works")
            
            # Verify it was saved
            item_info = get_queue_item_info(test_queue_item_id)
            if item_info and item_info.get('match_metadata'):
                print("✅ Metadata retrieval works")
            
            # Cleanup
            queue_item_dir = get_queue_item_directory(test_queue_item_id)
            if os.path.exists(queue_item_dir):
                import shutil
                shutil.rmtree(queue_item_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_workflow():
    """Test 6: Full processing workflow"""
    print("\n" + "=" * 60)
    print("Test 6: Full Processing Workflow")
    print("=" * 60)
    
    if not CV2_AVAILABLE or not TASKS_AVAILABLE:
        print("⏭️  SKIPPED: OpenCV or task processing module not available")
        return True
    
    try:
        # Create a test image file
        test_queue_item_id = f"test_workflow_{uuid.uuid4().hex[:8]}"
        test_image = np.ones((500, 500), dtype=np.uint8) * 255
        cv2.rectangle(test_image, (100, 100), (400, 400), 0, -1)
        cv2.putText(test_image, "TEST", (200, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, 255, 3)
        
        # Save test image to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            cv2.imwrite(tmp_path, test_image)
        
        try:
            # Process the queue item
            result = process_queue_item_for_visualization(
                tmp_path,
                test_queue_item_id,
                calling_app_id="test_app"
            )
            
            assert result['success'], "Processing should succeed"
            assert result['original_path'], "Original path should be set"
            assert result['preprocessed_path'], "Preprocessed path should be set"
            assert os.path.exists(result['original_path']), "Original file should exist"
            assert os.path.exists(result['preprocessed_path']), "Preprocessed file should exist"
            
            print("✅ Full workflow completed successfully")
            print(f"   - Original saved: {result['original_path']}")
            print(f"   - Preprocessed saved: {result['preprocessed_path']}")
            
            if result['match_result']:
                print(f"   - Match score: {result['match_result'].get('match_score', 0.0):.2f}")
            
            # Cleanup
            queue_item_dir = get_queue_item_directory(test_queue_item_id)
            if os.path.exists(queue_item_dir):
                import shutil
                shutil.rmtree(queue_item_dir)
            
            return True
            
        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("DigiDoc Full Pipeline Test Suite")
    print("=" * 60)
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("File Storage Utilities", test_file_utils),
        ("Image Preprocessing", test_preprocessing),
        ("Structural Fingerprinting", test_structural_fingerprinting),
        ("Queue Utilities", test_queue_utilities),
        ("Full Processing Workflow", test_full_workflow),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
