"""
File Storage Utilities

Handles file storage operations for queue items, including:
- Queue item directory management
- Saving original files
- Saving preprocessed images
- All paths use configurable storage_base from config
"""

import os
import shutil
from pathlib import Path
from typing import Optional
from ..config import get_config

# Import cv2 only when needed (for save_preprocessed_image)
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def get_queue_item_directory(queue_item_id: str) -> str:
    """
    Get the directory path for a queue item.
    
    Returns: {storage_base}/queue/{queue_item_id}/
    Uses configurable storage_base from config.
    
    Args:
        queue_item_id: Unique identifier for the queue item
        
    Returns:
        Absolute path to queue item directory (with trailing slash)
    """
    config = get_config()
    storage_base = config.paths.storage_base
    queue_directory = config.paths.queue_directory
    
    # Queue item directory: {queue_directory}/{queue_item_id}/
    queue_item_dir = os.path.join(queue_directory, queue_item_id)
    
    # Ensure trailing slash for consistency
    if not queue_item_dir.endswith(os.sep):
        queue_item_dir += os.sep
    
    return queue_item_dir


def ensure_queue_item_directory(queue_item_id: str) -> str:
    """
    Ensure queue item directory exists, creating it if needed.
    
    Args:
        queue_item_id: Unique identifier for the queue item
        
    Returns:
        Absolute path to queue item directory (with trailing slash)
    """
    queue_item_dir = get_queue_item_directory(queue_item_id)
    
    # Create directory if it doesn't exist
    os.makedirs(queue_item_dir, exist_ok=True)
    
    return queue_item_dir


def save_original_file(source_path: str, queue_item_id: str) -> str:
    """
    Copy original file to queue item directory.
    
    Copies the source file to {queue_item_id}/original.{ext}
    Preserves the original file extension.
    
    Args:
        source_path: Path to source file
        queue_item_id: Unique identifier for the queue item
        
    Returns:
        Path to saved original file
    """
    # Ensure queue item directory exists
    queue_item_dir = ensure_queue_item_directory(queue_item_id)
    
    # Get file extension from source
    source_ext = Path(source_path).suffix
    if not source_ext:
        source_ext = '.png'  # Default extension
    
    # Destination path
    dest_path = os.path.join(queue_item_dir, f"original{source_ext}")
    
    # Copy file
    shutil.copy2(source_path, dest_path)
    
    return dest_path


def save_preprocessed_image(image, queue_item_id: str) -> str:
    """
    Save preprocessed image to queue item directory.
    
    Saves the preprocessed image as {queue_item_id}/preprocessed.png
    
    Args:
        image: Preprocessed image as numpy array
        queue_item_id: Unique identifier for the queue item
        
    Returns:
        Path to saved preprocessed image
    """
    if not CV2_AVAILABLE:
        raise ImportError("OpenCV (cv2) is required to save preprocessed images. Install with: pip install opencv-python")
    
    # Ensure queue item directory exists
    queue_item_dir = ensure_queue_item_directory(queue_item_id)
    
    # Destination path
    dest_path = os.path.join(queue_item_dir, "preprocessed.png")
    
    # Save image
    cv2.imwrite(dest_path, image)
    
    return dest_path


def get_processed_directory() -> str:
    """
    Get the processed files directory path.
    
    Returns: {storage_base}/processed/
    Uses configurable storage_base from config.
    
    Returns:
        Absolute path to processed directory
    """
    config = get_config()
    return config.paths.processed_directory


def get_failed_directory() -> str:
    """
    Get the failed files directory path.
    
    Returns: {storage_base}/failed/
    Uses configurable storage_base from config.
    
    Returns:
        Absolute path to failed directory
    """
    config = get_config()
    return config.paths.failed_directory


def get_templates_directory() -> str:
    """
    Get the templates directory path.
    
    Returns: {storage_base}/templates/
    Uses configurable storage_base from config.
    
    Returns:
        Absolute path to templates directory
    """
    config = get_config()
    return config.paths.templates_directory
