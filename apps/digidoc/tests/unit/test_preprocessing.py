#!/usr/bin/env python3
"""
Preprocessing Visual Test Script

Tests preprocessing methods and saves before/after images for visual comparison.
Requires OpenCV and other dependencies to be installed.

Usage:
    python3 test_preprocessing.py <image_path> [output_dir]
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import cv2
    import numpy as np
    from ocr_service.utils.image_preprocessing import ImagePreprocessor
    from ocr_service.config import get_config
except ImportError as e:
    print(f"Error: Missing required dependency: {e}")
    print("Please install dependencies: pip install -r requirements_ocr.txt")
    sys.exit(1)


def test_preprocessing(image_path: str, output_dir: str = None):
    """
    Test preprocessing on an image and save before/after comparison.
    
    Args:
        image_path: Path to input image
        output_dir: Directory to save output images (default: same as input)
    """
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        return False
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.dirname(image_path)
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("Preprocessing Visual Test")
    print("=" * 60)
    print(f"Input image: {image_path}")
    print(f"Output directory: {output_dir}\n")
    
    # Load config
    config = get_config()
    print("Configuration:")
    print(f"  denoise_level: {config.preprocessing.denoise_level}")
    print(f"  deskew_enabled: {config.preprocessing.deskew_enabled}")
    print()
    
    # Load original image
    original = cv2.imread(image_path)
    if original is None:
        print(f"Error: Could not load image: {image_path}")
        return False
    
    original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    print(f"Original image: {original_gray.shape[1]}x{original_gray.shape[0]}")
    
    # Run preprocessing
    print("\nRunning preprocessing...")
    try:
        preprocessed = ImagePreprocessor.preprocess(image_path)
        print(f"Preprocessed image: {preprocessed.shape[1]}x{preprocessed.shape[0]}")
    except Exception as e:
        print(f"Error during preprocessing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Save images for comparison
    base_name = Path(image_path).stem
    
    # Save original grayscale
    original_path = os.path.join(output_dir, f"{base_name}_original.png")
    cv2.imwrite(original_path, original_gray)
    print(f"  ✓ Saved original: {original_path}")
    
    # Save preprocessed
    preprocessed_path = os.path.join(output_dir, f"{base_name}_preprocessed.png")
    cv2.imwrite(preprocessed_path, preprocessed)
    print(f"  ✓ Saved preprocessed: {preprocessed_path}")
    
    # Create side-by-side comparison
    # Resize if needed to make comparison
    h1, w1 = original_gray.shape
    h2, w2 = preprocessed.shape
    
    # Use max dimensions
    max_h = max(h1, h2)
    max_w = max(w1, w2)
    
    # Create comparison image
    comparison = np.zeros((max_h, w1 + w2 + 20), dtype=np.uint8)
    comparison[:h1, :w1] = original_gray
    comparison[:h2, w1 + 20:w1 + 20 + w2] = preprocessed
    
    comparison_path = os.path.join(output_dir, f"{base_name}_comparison.png")
    cv2.imwrite(comparison_path, comparison)
    print(f"  ✓ Saved comparison: {comparison_path}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
    print(f"\nVisual comparison images saved to: {output_dir}")
    print("Review the images to verify preprocessing improvements.")
    
    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 test_preprocessing.py <image_path> [output_dir]")
        print("\nExample:")
        print("  python3 test_preprocessing.py ~/Dropbox/Application\\ Data/DigiDoc/queue/Scan2025-12-18_133624_000.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = test_preprocessing(image_path, output_dir)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
