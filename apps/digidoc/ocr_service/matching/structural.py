"""
Structural Fingerprint Matching

Computes and compares structural fingerprints of documents using ratio-based features.
Fingerprints are DPI/scale invariant by using ratios instead of absolute pixel values.
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Any
from ..config import get_config


def compute_structural_fingerprint(image: np.ndarray) -> Dict[str, Any]:
    """
    Compute structural fingerprint of an image.
    
    Detects contours and extracts zones (header, tables, footer, logos).
    Computes ratios of zone positions and sizes relative to image dimensions.
    This makes the fingerprint DPI/scale invariant.
    
    Args:
        image: Grayscale or binary image (numpy array)
        
    Returns:
        Dictionary containing structural fingerprint with zone ratios:
        {
            'image_width': int,
            'image_height': int,
            'zones': [
                {
                    'type': str,  # 'header', 'table', 'footer', 'logo', 'other'
                    'x_ratio': float,  # X position / image_width
                    'y_ratio': float,  # Y position / image_height
                    'width_ratio': float,  # Width / image_width
                    'height_ratio': float,  # Height / image_height
                    'area_ratio': float  # Area / (image_width * image_height)
                },
                ...
            ],
            'zone_count': int,
            'total_content_area_ratio': float  # Total content area / image area
        }
    """
    h, w = image.shape[:2]
    
    # Detect contours
    # For binary images, use as-is; for grayscale, threshold first
    if len(np.unique(image)) > 2:
        # Grayscale image, threshold to binary
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        binary = image
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) == 0:
        # No content detected
        return {
            'image_width': w,
            'image_height': h,
            'zones': [],
            'zone_count': 0,
            'total_content_area_ratio': 0.0
        }
    
    # Extract zones from contours
    zones = []
    total_content_area = 0
    
    # Filter and process contours
    min_area = (w * h) * 0.001  # Minimum 0.1% of image area
    
    for contour in contours:
        # Calculate bounding box
        x, y, zone_w, zone_h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        
        # Skip very small contours (noise)
        if area < min_area:
            continue
        
        total_content_area += area
        
        # Compute ratios (relative to image dimensions)
        x_ratio = x / w
        y_ratio = y / h
        width_ratio = zone_w / w
        height_ratio = zone_h / h
        area_ratio = area / (w * h)
        
        # Classify zone type based on position and size
        zone_type = _classify_zone(y_ratio, height_ratio, width_ratio, area_ratio)
        
        zones.append({
            'type': zone_type,
            'x_ratio': float(x_ratio),
            'y_ratio': float(y_ratio),
            'width_ratio': float(width_ratio),
            'height_ratio': float(height_ratio),
            'area_ratio': float(area_ratio)
        })
    
    # Sort zones by y position (top to bottom)
    zones.sort(key=lambda z: z['y_ratio'])
    
    total_content_area_ratio = total_content_area / (w * h)
    
    return {
        'image_width': int(w),
        'image_height': int(h),
        'zones': zones,
        'zone_count': len(zones),
        'total_content_area_ratio': float(total_content_area_ratio)
    }


def _classify_zone(y_ratio: float, height_ratio: float, width_ratio: float, area_ratio: float) -> str:
    """
    Classify a zone based on its position and characteristics.
    
    Args:
        y_ratio: Y position ratio (0.0 = top, 1.0 = bottom)
        height_ratio: Height ratio relative to image height
        width_ratio: Width ratio relative to image width
        area_ratio: Area ratio relative to image area
        
    Returns:
        Zone type: 'header', 'table', 'footer', 'logo', or 'other'
    """
    # Header: typically at top (y_ratio < 0.2), wide, not too tall
    if y_ratio < 0.2 and width_ratio > 0.5 and height_ratio < 0.3:
        return 'header'
    
    # Footer: typically at bottom (y_ratio > 0.7), wide, not too tall
    if y_ratio > 0.7 and width_ratio > 0.5 and height_ratio < 0.3:
        return 'footer'
    
    # Table: typically in middle, wide, tall, large area
    if 0.2 <= y_ratio <= 0.7 and width_ratio > 0.6 and height_ratio > 0.3 and area_ratio > 0.1:
        return 'table'
    
    # Logo: typically small, square-ish, at top
    if y_ratio < 0.3 and area_ratio < 0.05 and abs(width_ratio - height_ratio) < 0.1:
        return 'logo'
    
    # Other: everything else
    return 'other'


def compare_fingerprints(fingerprint1: Dict[str, Any], fingerprint2: Dict[str, Any]) -> float:
    """
    Compare two structural fingerprints and return match score.
    
    Uses Euclidean distance on ratio-based features to compute similarity.
    Returns a score between 0.0 (no match) and 1.0 (perfect match).
    
    Args:
        fingerprint1: First structural fingerprint
        fingerprint2: Second structural fingerprint
        
    Returns:
        Match score between 0.0 and 1.0 (higher = better match)
    """
    # Extract features for comparison
    zones1 = fingerprint1.get('zones', [])
    zones2 = fingerprint2.get('zones', [])
    
    # If both have no zones, consider it a match (empty documents)
    if len(zones1) == 0 and len(zones2) == 0:
        return 1.0
    
    # If one has zones and the other doesn't, no match
    if len(zones1) == 0 or len(zones2) == 0:
        return 0.0
    
    # Compare zone counts (normalized)
    zone_count_diff = abs(len(zones1) - len(zones2))
    max_zones = max(len(zones1), len(zones2))
    zone_count_score = 1.0 - (zone_count_diff / max_zones) if max_zones > 0 else 1.0
    
    # Compare total content area ratio
    area1 = fingerprint1.get('total_content_area_ratio', 0.0)
    area2 = fingerprint2.get('total_content_area_ratio', 0.0)
    area_diff = abs(area1 - area2)
    area_score = 1.0 - min(area_diff, 1.0)  # Clamp to 0-1
    
    # Compare zone positions and sizes
    # Match zones by type and position
    zone_scores = []
    
    # Group zones by type
    zones1_by_type = {}
    zones2_by_type = {}
    
    for zone in zones1:
        zone_type = zone.get('type', 'other')
        if zone_type not in zones1_by_type:
            zones1_by_type[zone_type] = []
        zones1_by_type[zone_type].append(zone)
    
    for zone in zones2:
        zone_type = zone.get('type', 'other')
        if zone_type not in zones2_by_type:
            zones2_by_type[zone_type] = []
        zones2_by_type[zone_type].append(zone)
    
    # Compare zones of same type
    all_types = set(zones1_by_type.keys()) | set(zones2_by_type.keys())
    
    for zone_type in all_types:
        type_zones1 = zones1_by_type.get(zone_type, [])
        type_zones2 = zones2_by_type.get(zone_type, [])
        
        if len(type_zones1) == 0 or len(type_zones2) == 0:
            continue  # Skip if one fingerprint doesn't have this zone type
        
        # Compare each zone of this type
        # For simplicity, compare first zone of each type
        # (More sophisticated matching could use Hungarian algorithm)
        for z1 in type_zones1[:1]:  # Compare first zone of each type
            for z2 in type_zones2[:1]:
                # Compute Euclidean distance on ratio features
                features1 = [
                    z1['x_ratio'],
                    z1['y_ratio'],
                    z1['width_ratio'],
                    z1['height_ratio'],
                    z1['area_ratio']
                ]
                features2 = [
                    z2['x_ratio'],
                    z2['y_ratio'],
                    z2['width_ratio'],
                    z2['height_ratio'],
                    z2['area_ratio']
                ]
                
                # Euclidean distance
                distance = np.sqrt(sum((a - b) ** 2 for a, b in zip(features1, features2)))
                
                # Convert distance to similarity score (0-1)
                # Normalize: distance of 0 = score 1.0, distance of 1.0 = score 0.0
                # Using exponential decay for smoother scoring
                score = np.exp(-distance * 2)  # Adjust multiplier for sensitivity
                zone_scores.append(score)
    
    # Compute overall match score
    # Weight: zone_count (30%), area (20%), zone positions (50%)
    if len(zone_scores) > 0:
        avg_zone_score = np.mean(zone_scores)
    else:
        avg_zone_score = 0.0
    
    overall_score = (
        0.3 * zone_count_score +
        0.2 * area_score +
        0.5 * avg_zone_score
    )
    
    # Ensure score is between 0.0 and 1.0
    return float(np.clip(overall_score, 0.0, 1.0))
