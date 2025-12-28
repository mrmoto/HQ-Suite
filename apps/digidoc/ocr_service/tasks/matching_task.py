"""
Template Matching Task

Performs structural fingerprint matching between images and cached templates.
Generates visualization showing matched zones.
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

from ..matching.structural import compute_structural_fingerprint, compare_fingerprints
from ..database.models import CachedTemplate, get_session
from ..utils.file_utils import ensure_queue_item_directory
from ..config import get_config


def match_template(image_path: str, queue_item_id: str, calling_app_id: str) -> Dict[str, Any]:
    """
    Match image against cached templates using structural fingerprinting.
    
    Args:
        image_path: Path to preprocessed image
        queue_item_id: Unique identifier for the queue item
        calling_app_id: ID of the calling application
        
    Returns:
        Dictionary with match results:
        {
            'matched_template_id': str or None,
            'match_score': float (0.0-1.0),
            'template_name': str or None,
            'visualization_path': str,
            'fingerprint': dict
        }
    """
    # Load config
    config = get_config()
    
    # Load preprocessed image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    # Compute structural fingerprint of image
    image_fingerprint = compute_structural_fingerprint(image)
    
    # Load templates from cache
    session = get_session()
    try:
        templates = session.query(CachedTemplate).filter(
            CachedTemplate.calling_app_id == calling_app_id,
            CachedTemplate.structural_fingerprint.isnot(None)
        ).all()
        
        if len(templates) == 0:
            # No templates with fingerprints available
            return {
                'matched_template_id': None,
                'match_score': 0.0,
                'template_name': None,
                'visualization_path': None,
                'fingerprint': image_fingerprint
            }
        
        # Compare with each template
        best_match = None
        best_score = 0.0
        
        for template in templates:
            template_fingerprint = template.structural_fingerprint
            if template_fingerprint is None:
                continue
            
            score = compare_fingerprints(image_fingerprint, template_fingerprint)
            
            if score > best_score:
                best_score = score
                best_match = template
        
        # Generate visualization
        visualization_path = None
        if best_match and best_score > 0.0:
            visualization_path = generate_match_visualization(
                image,
                image_fingerprint,
                best_match.structural_fingerprint,
                queue_item_id,
                best_match,
                best_score
            )
        
        result = {
            'matched_template_id': best_match.template_id if best_match else None,
            'match_score': float(best_score),
            'template_name': best_match.format_name if best_match else None,
            'visualization_path': visualization_path,
            'fingerprint': image_fingerprint
        }
        
        return result
        
    finally:
        session.close()


def generate_match_visualization(
    image: np.ndarray,
    image_fingerprint: Dict[str, Any],
    template_fingerprint: Dict[str, Any],
    queue_item_id: str,
    template: CachedTemplate,
    match_score: float
) -> str:
    """
    Generate visualization showing matched zones between image and template.
    
    Creates an image with zone overlays showing:
    - Detected zones in the image
    - Matched zones from template
    - Match score and template name
    
    Args:
        image: Preprocessed image
        image_fingerprint: Structural fingerprint of image
        template_fingerprint: Structural fingerprint of matched template
        queue_item_id: Queue item identifier
        template: Matched template object
        match_score: Match score (0.0-1.0)
        
    Returns:
        Path to saved visualization image
    """
    # Ensure queue item directory exists
    queue_item_dir = ensure_queue_item_directory(queue_item_id)
    
    # Create visualization image (copy of original)
    vis_image = image.copy()
    
    # Convert to color for visualization
    if len(vis_image.shape) == 2:
        vis_image = cv2.cvtColor(vis_image, cv2.COLOR_GRAY2BGR)
    
    h, w = image.shape[:2]
    
    # Draw zones from image fingerprint
    image_zones = image_fingerprint.get('zones', [])
    for i, zone in enumerate(image_zones):
        # Convert ratios to pixel coordinates
        x = int(zone['x_ratio'] * w)
        y = int(zone['y_ratio'] * h)
        zone_w = int(zone['width_ratio'] * w)
        zone_h = int(zone['height_ratio'] * h)
        
        # Color by zone type
        colors = {
            'header': (0, 255, 0),      # Green
            'table': (255, 0, 0),       # Blue
            'footer': (0, 0, 255),      # Red
            'logo': (255, 255, 0),      # Cyan
            'other': (128, 128, 128)    # Gray
        }
        color = colors.get(zone['type'], (128, 128, 128))
        
        # Draw rectangle
        cv2.rectangle(vis_image, (x, y), (x + zone_w, y + zone_h), color, 2)
        
        # Add label
        label = f"{zone['type']}"
        cv2.putText(vis_image, label, (x, y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    # Add match information text
    info_text = [
        f"Template: {template.format_name or template.template_id}",
        f"Match Score: {match_score:.2f}",
        f"Zones: {len(image_zones)}"
    ]
    
    y_offset = 20
    for text in info_text:
        cv2.putText(vis_image, text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(vis_image, text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        y_offset += 25
    
    # Save visualization
    vis_path = Path(queue_item_dir) / "match_visualization.png"
    cv2.imwrite(str(vis_path), vis_image)
    
    return str(vis_path)
