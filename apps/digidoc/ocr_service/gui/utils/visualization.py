"""
Visualization Utilities

Helper functions for creating and displaying visualizations in the GUI.
"""

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None
    np = None

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

from typing import Optional, Tuple, List
import os


def create_side_by_side_comparison(
    image1,
    image2,
    image3: Optional = None,
    labels: Tuple[str, str, Optional[str]] = ("Original", "Preprocessed", "Match Visualization"),
    max_width: int = 600
):
    """
    Create a side-by-side comparison image from multiple images.
    
    All images are scaled proportionally to fit within max_width per panel,
    then combined horizontally with labels.
    
    Args:
        image1: First image (numpy array, grayscale or BGR)
        image2: Second image (numpy array, grayscale or BGR)
        image3: Optional third image (numpy array, grayscale or BGR)
        labels: Tuple of labels for each image
        max_width: Maximum width per panel in pixels
        
    Returns:
        Combined image as numpy array (BGR format)
    """
    if not CV2_AVAILABLE:
        raise ImportError("OpenCV (cv2) is required for visualization. Install with: pip install opencv-python")
    
    images = [image1, image2]
    if image3 is not None:
        images.append(image3)
    
    # Scale images proportionally
    scaled_images = []
    for img in images:
        if img is None:
            continue
        
        # Convert to BGR if grayscale
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        
        h, w = img.shape[:2]
        if w > max_width:
            ratio = max_width / w
            new_h = int(h * ratio)
            img = cv2.resize(img, (max_width, new_h), interpolation=cv2.INTER_CUBIC)
        
        scaled_images.append(img)
    
    # Find maximum height
    max_height = max(img.shape[0] for img in scaled_images) if scaled_images else 0
    
    # Resize all images to same height (pad if needed)
    padded_images = []
    for i, img in enumerate(scaled_images):
        h, w = img.shape[:2]
        if h < max_height:
            # Pad bottom
            pad_bottom = max_height - h
            img = cv2.copyMakeBorder(img, 0, pad_bottom, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        padded_images.append(img)
    
    # Combine horizontally
    if len(padded_images) == 2:
        combined = np.hstack(padded_images)
    elif len(padded_images) == 3:
        combined = np.hstack(padded_images)
    else:
        combined = padded_images[0] if padded_images else np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Add labels at the top
    label_height = 30
    combined_with_labels = np.ones((combined.shape[0] + label_height, combined.shape[1], 3), dtype=np.uint8) * 255
    
    # Place labels
    x_offset = 0
    for i, (img, label) in enumerate(zip(padded_images, labels[:len(padded_images)])):
        if label:
            # Add text
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            text_x = x_offset + (img.shape[1] // 2) - (text_size[0] // 2)
            cv2.putText(combined_with_labels, label, (text_x, 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        x_offset += img.shape[1]
    
    # Place images below labels
    combined_with_labels[label_height:, :] = combined
    
    return combined_with_labels


def draw_zone_overlays(
    image,
    fingerprint: dict,
    colors: Optional[dict] = None
):
    """
    Draw zone overlays on an image based on structural fingerprint.
    
    Args:
        image: Input image (numpy array, grayscale or BGR)
        fingerprint: Structural fingerprint dictionary with zones
        colors: Optional dictionary mapping zone types to BGR colors
        
    Returns:
        Image with zone overlays drawn (BGR format)
    """
    if not CV2_AVAILABLE:
        raise ImportError("OpenCV (cv2) is required for visualization. Install with: pip install opencv-python")
    
    if colors is None:
        colors = {
            'header': (0, 255, 0),      # Green
            'table': (255, 0, 0),       # Blue
            'footer': (0, 0, 255),      # Red
            'logo': (255, 255, 0),      # Cyan
            'other': (128, 128, 128)    # Gray
        }
    
    # Convert to BGR if grayscale
    if len(image.shape) == 2:
        vis_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        vis_image = image.copy()
    
    h, w = image.shape[:2]
    zones = fingerprint.get('zones', [])
    
    for zone in zones:
        # Convert ratios to pixel coordinates
        x = int(zone['x_ratio'] * w)
        y = int(zone['y_ratio'] * h)
        zone_w = int(zone['width_ratio'] * w)
        zone_h = int(zone['height_ratio'] * h)
        
        # Get color for zone type
        zone_type = zone.get('type', 'other')
        color = colors.get(zone_type, (128, 128, 128))
        
        # Draw rectangle
        cv2.rectangle(vis_image, (x, y), (x + zone_w, y + zone_h), color, 2)
        
        # Add label
        label = f"{zone_type}"
        cv2.putText(vis_image, label, (x, y - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    return vis_image


def load_image_for_display(image_path: str, max_size: Optional[Tuple[int, int]] = None):
    """
    Load image from file and optionally resize for display.
    
    Args:
        image_path: Path to image file
        max_size: Optional maximum size (width, height) for resizing
        
    Returns:
        PIL Image object, or None if loading fails
    """
    if not PIL_AVAILABLE:
        raise ImportError("PIL (Pillow) is required for image loading. Install with: pip install pillow")
    
    if not os.path.exists(image_path):
        return None
    
    try:
        img = Image.open(image_path)
        if max_size:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None


def save_visualization(image, output_path: str) -> bool:
    """
    Save visualization image to file.
    
    Args:
        image: Image as numpy array (BGR format)
        output_path: Path to save image
        
    Returns:
        True if successful, False otherwise
    """
    if not CV2_AVAILABLE:
        raise ImportError("OpenCV (cv2) is required for saving visualizations. Install with: pip install opencv-python")
    
    try:
        cv2.imwrite(output_path, image)
        return True
    except Exception as e:
        print(f"Error saving visualization to {output_path}: {e}")
        return False
