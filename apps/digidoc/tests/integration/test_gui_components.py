#!/usr/bin/env python3
"""
GUI Components Test Script

Tests GUI components without requiring Streamlit to be running:
- Queue utilities
- Visualization utilities
- Image loading and processing

Run with: python3 ocr_service/test_gui_components.py
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
    from PIL import Image
    CV2_AVAILABLE = True
    PIL_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    PIL_AVAILABLE = False
    print("WARNING: OpenCV or PIL not available. Some tests will be skipped.")

from ocr_service.gui.utils.queue_utils import (
    list_queue_items,
    get_queue_item_info,
    save_match_metadata
)

try:
    from ocr_service.gui.utils.visualization import (
        create_side_by_side_comparison,
        draw_zone_overlays,
        load_image_for_display,
        save_visualization
    )
    VISUALIZATION_AVAILABLE = True
except (ImportError, AttributeError):
    VISUALIZATION_AVAILABLE = False
    print("WARNING: Visualization utilities not available (cv2/PIL required)")

from ocr_service.utils.file_utils import (
    ensure_queue_item_directory,
    save_preprocessed_image,
    get_queue_item_directory
)

try:
    from ocr_service.matching.structural import compute_structural_fingerprint
    MATCHING_AVAILABLE = True
except ImportError:
    MATCHING_AVAILABLE = False
    print("WARNING: Matching not available (cv2 required)")


def test_queue_utilities():
    """Test queue utility functions"""
    print("\n" + "=" * 60)
    print("Test 1: Queue Utilities")
    print("=" * 60)
    
    try:
        # Test listing queue items
        items = list_queue_items()
        print(f"✅ list_queue_items() works ({len(items)} items)")
        
        # Test filtering
        pending_items = list_queue_items(status_filter='pending')
        print(f"✅ Status filtering works ({len(pending_items)} pending items)")
        
        # Test getting item info (if items exist)
        if items:
            item_info = get_queue_item_info(items[0]['queue_item_id'])
            if item_info:
                print(f"✅ get_queue_item_info() works")
                print(f"   - Item: {item_info['queue_item_id']}")
                print(f"   - Status: {item_info['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization_utilities():
    """Test visualization utility functions"""
    print("\n" + "=" * 60)
    print("Test 2: Visualization Utilities")
    print("=" * 60)
    
    if not CV2_AVAILABLE or not VISUALIZATION_AVAILABLE:
        print("⏭️  SKIPPED: OpenCV or visualization module not available")
        return True
    
    try:
        # Create test images
        img1 = np.ones((300, 400), dtype=np.uint8) * 255
        img2 = np.ones((300, 400), dtype=np.uint8) * 200
        img3 = np.ones((300, 400), dtype=np.uint8) * 150
        
        # Test side-by-side comparison
        combined = create_side_by_side_comparison(
            img1, img2, img3,
            labels=("Original", "Preprocessed", "Match")
        )
        
        assert combined is not None, "Combined image should not be None"
        assert combined.shape[0] > 0 and combined.shape[1] > 0, "Combined image should have valid dimensions"
        print("✅ create_side_by_side_comparison() works")
        
        # Test zone overlays
        if MATCHING_AVAILABLE:
            fingerprint = compute_structural_fingerprint(img1)
            if fingerprint and fingerprint.get('zones'):
                overlay = draw_zone_overlays(img1, fingerprint)
                assert overlay is not None, "Overlay image should not be None"
                print("✅ draw_zone_overlays() works")
        
        # Test saving visualization
        test_path = "/tmp/test_visualization.png"
        success = save_visualization(combined, test_path)
        if success and os.path.exists(test_path):
            print("✅ save_visualization() works")
            os.unlink(test_path)
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_image_loading():
    """Test image loading utilities"""
    print("\n" + "=" * 60)
    print("Test 3: Image Loading Utilities")
    print("=" * 60)
    
    if not CV2_AVAILABLE or not PIL_AVAILABLE:
        print("⏭️  SKIPPED: OpenCV or PIL not available")
        return True
    
    try:
        # Create and save a test image
        test_image = np.ones((500, 500), dtype=np.uint8) * 255
        cv2.rectangle(test_image, (100, 100), (400, 400), 0, -1)
        
        test_path = "/tmp/test_image_loading.png"
        cv2.imwrite(test_path, test_image)
        
        try:
            # Test loading
            loaded = load_image_for_display(test_path, max_size=(300, 300))
            if loaded:
                print("✅ load_image_for_display() works")
                print(f"   - Original size: {test_image.shape}")
                print(f"   - Loaded size: {loaded.size}")
            
            # Test with non-existent file
            non_existent = load_image_for_display("/tmp/nonexistent.png")
            assert non_existent is None, "Non-existent file should return None"
            print("✅ Error handling works")
            
            return True
            
        finally:
            if os.path.exists(test_path):
                os.unlink(test_path)
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metadata_operations():
    """Test metadata save/load operations"""
    print("\n" + "=" * 60)
    print("Test 4: Metadata Operations")
    print("=" * 60)
    
    try:
        test_queue_item_id = f"test_meta_{uuid.uuid4().hex[:8]}"
        
        # Test saving metadata
        test_metadata = {
            'matched_template_id': 'test_template_123',
            'match_score': 0.92,
            'template_name': 'Test Template',
            'fingerprint': {
                'zones': [
                    {'type': 'header', 'x_ratio': 0.1, 'y_ratio': 0.05}
                ]
            }
        }
        
        success = save_match_metadata(test_queue_item_id, test_metadata)
        assert success, "Saving metadata should succeed"
        print("✅ save_match_metadata() works")
        
        # Test retrieving metadata
        item_info = get_queue_item_info(test_queue_item_id)
        if item_info and item_info.get('match_metadata'):
            retrieved_meta = item_info['match_metadata']
            assert retrieved_meta['matched_template_id'] == 'test_template_123'
            assert retrieved_meta['match_score'] == 0.92
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


def main():
    """Run all GUI component tests"""
    print("\n" + "=" * 60)
    print("DigiDoc GUI Components Test Suite")
    print("=" * 60)
    
    tests = [
        ("Queue Utilities", test_queue_utilities),
        ("Visualization Utilities", test_visualization_utilities),
        ("Image Loading", test_image_loading),
        ("Metadata Operations", test_metadata_operations),
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
        print("\n🎉 All GUI component tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
