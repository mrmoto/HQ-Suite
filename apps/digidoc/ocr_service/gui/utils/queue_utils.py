"""
Queue Utilities

Helper functions for accessing and managing queue items in the GUI.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from ...config import get_config
from ...utils.file_utils import get_queue_item_directory


def get_queue_item_info(queue_item_id: str) -> Optional[Dict]:
    """
    Get information about a queue item.
    
    Args:
        queue_item_id: Queue item identifier
        
    Returns:
        Dictionary with queue item information, or None if not found
    """
    queue_item_dir = get_queue_item_directory(queue_item_id)
    
    if not os.path.exists(queue_item_dir):
        return None
    
    # Find files
    original_path = None
    preprocessed_path = os.path.join(queue_item_dir, "preprocessed.png")
    match_visualization_path = os.path.join(queue_item_dir, "match_visualization.png")
    match_metadata_path = os.path.join(queue_item_dir, "match_metadata.json")
    
    # Find original file
    for file in os.listdir(queue_item_dir):
        if file.startswith('original.'):
            original_path = os.path.join(queue_item_dir, file)
            break
    
    # Load match metadata if available
    match_metadata = {}
    if os.path.exists(match_metadata_path):
        try:
            with open(match_metadata_path, 'r') as f:
                match_metadata = json.load(f)
        except Exception:
            pass
    
    # Determine status
    if os.path.exists(match_visualization_path):
        status = 'completed'
    elif os.path.exists(preprocessed_path):
        status = 'processing'
    elif original_path and os.path.exists(original_path):
        status = 'pending'
    else:
        status = 'unknown'
    
    # Get filename
    filename = queue_item_id
    if original_path:
        filename = os.path.basename(original_path)
    
    # Get creation time
    created_at = None
    if original_path and os.path.exists(original_path):
        created_at = datetime.fromtimestamp(os.path.getctime(original_path))
    
    return {
        'queue_item_id': queue_item_id,
        'filename': filename,
        'original_path': original_path,
        'preprocessed_path': preprocessed_path if os.path.exists(preprocessed_path) else None,
        'match_visualization_path': match_visualization_path if os.path.exists(match_visualization_path) else None,
        'match_metadata': match_metadata,
        'status': status,
        'created_at': created_at
    }


def list_queue_items(status_filter: Optional[str] = None) -> List[Dict]:
    """
    List all queue items, optionally filtered by status.
    
    Args:
        status_filter: Optional status filter ('pending', 'processing', 'completed', 'failed', 'unknown')
        
    Returns:
        List of queue item information dictionaries
    """
    config = get_config()
    queue_dir = config.paths.queue_directory
    
    if not os.path.exists(queue_dir):
        return []
    
    queue_items = []
    
    # Scan queue directory - handle both subdirectories AND loose files
    for item_name in os.listdir(queue_dir):
        item_path = os.path.join(queue_dir, item_name)
        
        if os.path.isdir(item_path):
            # Existing subdirectory structure: queue/{queue_item_id}/original.png
            queue_item_id = item_name
            item_info = get_queue_item_info(queue_item_id)
            
            if item_info:
                # Apply status filter if specified
                if status_filter and item_info['status'] != status_filter:
                    continue
                
                queue_items.append(item_info)
        
        elif os.path.isfile(item_path) and item_name.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            # Loose file in queue directory: queue/Scan2025-12-18_133624_000.png
            # Create queue item info for loose file
            file_stat = os.stat(item_path)
            created_at = datetime.fromtimestamp(file_stat.st_ctime)
            
            # Determine status: if file exists but no processing artifacts, it's pending
            status = 'pending'
            
            item_info = {
                'queue_item_id': item_name,  # Use filename as ID for loose files
                'filename': item_name,
                'original_path': item_path,
                'preprocessed_path': None,
                'match_visualization_path': None,
                'match_metadata': {},
                'status': status,
                'created_at': created_at
            }
            
            # Apply status filter if specified
            if status_filter and item_info['status'] != status_filter:
                continue
            
            queue_items.append(item_info)
    
    # Sort by creation time (newest first)
    queue_items.sort(key=lambda x: x['created_at'] or datetime.min, reverse=True)
    
    return queue_items


def save_match_metadata(queue_item_id: str, metadata: Dict) -> bool:
    """
    Save match metadata to queue item directory.
    
    Args:
        queue_item_id: Queue item identifier
        metadata: Dictionary with match metadata
        
    Returns:
        True if successful, False otherwise
    """
    queue_item_dir = get_queue_item_directory(queue_item_id)
    metadata_path = os.path.join(queue_item_dir, "match_metadata.json")
    
    try:
        os.makedirs(queue_item_dir, exist_ok=True)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving match metadata: {e}")
        return False
