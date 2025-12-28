"""
Visual Match Page

Displays three-panel view: original, preprocessed, and template match visualization.
"""

import streamlit as st
from pathlib import Path
from PIL import Image
import os
import json

from ...config import get_config
from ...utils.file_utils import get_queue_item_directory


def _load_image_safely(image_path: str) -> Image.Image:
    """
    Load image with error handling.
    
    Args:
        image_path: Path to image file
        
    Returns:
        PIL Image object, or None if loading fails
    """
    if not image_path or not os.path.exists(image_path):
        return None
    
    try:
        return Image.open(image_path)
    except Exception as e:
        st.error(f"Error loading image {image_path}: {e}")
        return None


def _scale_image_proportionally(image: Image.Image, max_width: int = 600) -> Image.Image:
    """
    Scale image proportionally to fit within max_width.
    
    Args:
        image: PIL Image object
        max_width: Maximum width in pixels
        
    Returns:
        Scaled PIL Image object
    """
    if image is None:
        return None
    
    width, height = image.size
    if width <= max_width:
        return image
    
    # Calculate proportional height
    ratio = max_width / width
    new_height = int(height * ratio)
    
    return image.resize((max_width, new_height), Image.Resampling.LANCZOS)


def _load_match_metadata(queue_item_id: str) -> dict:
    """
    Load match metadata if available.
    
    Checks for match_metadata.json in queue item directory.
    
    Args:
        queue_item_id: Queue item identifier
        
    Returns:
        Dictionary with match metadata, or empty dict if not found
    """
    queue_item_dir = get_queue_item_directory(queue_item_id)
    metadata_path = os.path.join(queue_item_dir, "match_metadata.json")
    
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"Could not load match metadata: {e}")
    
    return {}


def render():
    """Render the visual match page."""
    st.title("Visual Match")
    st.markdown("---")
    
    # Get selected queue item ID
    queue_item_id = st.session_state.get('selected_queue_item_id')
    
    if not queue_item_id:
        st.info("No queue item selected. Please select an item from the Queue View.")
        if st.button("Go to Queue View"):
            if 'selected_queue_item_id' in st.session_state:
                del st.session_state.selected_queue_item_id
            st.rerun()
        return
    
    # Get queue item directory
    queue_item_dir = get_queue_item_directory(queue_item_id)
    
    if not os.path.exists(queue_item_dir):
        st.error(f"Queue item directory not found: {queue_item_dir}")
        return
    
    # Load images
    original_path = None
    preprocessed_path = os.path.join(queue_item_dir, "preprocessed.png")
    match_visualization_path = os.path.join(queue_item_dir, "match_visualization.png")
    
    # Find original file (could be original.png, original.jpg, etc.)
    for file in os.listdir(queue_item_dir):
        if file.startswith('original.'):
            original_path = os.path.join(queue_item_dir, file)
            break
    
    # Load images
    original_image = _load_image_safely(original_path)
    preprocessed_image = _load_image_safely(preprocessed_path)
    match_visualization_image = _load_image_safely(match_visualization_path)
    
    # Load match metadata
    match_metadata = _load_match_metadata(queue_item_id)
    
    # Display match information
    if match_metadata:
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'matched_template_id' in match_metadata:
                st.metric("Template ID", match_metadata.get('matched_template_id', 'N/A'))
        with col2:
            if 'match_score' in match_metadata:
                score = match_metadata.get('match_score', 0.0)
                st.metric("Match Score", f"{score:.2%}")
        with col3:
            if 'template_name' in match_metadata:
                st.metric("Template Name", match_metadata.get('template_name', 'N/A'))
    
    st.markdown("---")
    
    # Three-panel view
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Original Image")
        if original_image:
            scaled_original = _scale_image_proportionally(original_image)
            st.image(scaled_original, use_container_width=True)
            st.caption(f"Size: {original_image.size[0]} × {original_image.size[1]} pixels")
        else:
            st.warning("Original image not found")
    
    with col2:
        st.subheader("Preprocessed Image")
        if preprocessed_image:
            scaled_preprocessed = _scale_image_proportionally(preprocessed_image)
            st.image(scaled_preprocessed, use_container_width=True)
            st.caption(f"Size: {preprocessed_image.size[0]} × {preprocessed_image.size[1]} pixels")
        else:
            st.warning("Preprocessed image not found")
    
    with col3:
        st.subheader("Template Match Visualization")
        if match_visualization_image:
            scaled_match = _scale_image_proportionally(match_visualization_image)
            st.image(scaled_match, use_container_width=True)
            st.caption(f"Size: {match_visualization_image.size[0]} × {match_visualization_image.size[1]} pixels")
        else:
            st.info("Match visualization not available. Processing may not be complete.")
    
    # Back button
    st.markdown("---")
    if st.button("← Back to Queue View"):
        if 'selected_queue_item_id' in st.session_state:
            del st.session_state.selected_queue_item_id
        st.rerun()
