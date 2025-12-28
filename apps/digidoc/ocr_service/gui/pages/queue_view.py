"""
Queue View Page

Displays list of queue items with status, confidence scores, and thumbnails.
"""

import streamlit as st
from pathlib import Path
from PIL import Image
import os

from ...gui.utils.queue_utils import list_queue_items, get_queue_item_info


def _get_thumbnail(image_path: str, max_size: tuple = (150, 150)) -> Image.Image:
    """
    Load and resize image for thumbnail display.
    
    Args:
        image_path: Path to image file
        max_size: Maximum thumbnail size (width, height)
        
    Returns:
        PIL Image object resized for thumbnail
    """
    try:
        img = Image.open(image_path)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        # Return placeholder if image can't be loaded
        placeholder = Image.new('RGB', max_size, color='gray')
        return placeholder


def render():
    """Render the queue view page."""
    st.title("Queue View")
    st.markdown("---")
    
    # Get queue items
    queue_items = list_queue_items()
    
    if len(queue_items) == 0:
        st.info("No queue items found.")
        return
    
    # Filter by status
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "pending", "processing", "completed", "failed", "unknown"],
        index=0
    )
    
    # Filter items
    if status_filter != "All":
        queue_items = [item for item in queue_items if item['status'] == status_filter]
    
    st.write(f"Showing {len(queue_items)} queue item(s)")
    st.markdown("---")
    
    # Display queue items in a grid
    cols_per_row = 3
    for i in range(0, len(queue_items), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(queue_items):
                item = queue_items[i + j]
                
                with col:
                    # Display thumbnail
                    thumbnail_path = item.get('preprocessed_path') or item.get('original_path')
                    
                    if thumbnail_path:
                        thumbnail = _get_thumbnail(thumbnail_path)
                        st.image(thumbnail, use_container_width=True)
                    
                    # Display filename
                    st.write(f"**{item['filename']}**")
                    
                    # Display status badge
                    status_colors = {
                        'pending': '🟡',
                        'processing': '🔵',
                        'completed': '🟢',
                        'failed': '🔴',
                        'unknown': '⚪'
                    }
                    status_emoji = status_colors.get(item['status'], '⚪')
                    st.write(f"{status_emoji} {item['status'].title()}")
                    
                    # Display creation time
                    if item['created_at']:
                        st.caption(f"Created: {item['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Click to navigate to visual match view
                    if st.button("View Details", key=f"view_{item['queue_item_id']}"):
                        st.session_state.selected_queue_item_id = item['queue_item_id']
                        st.rerun()
