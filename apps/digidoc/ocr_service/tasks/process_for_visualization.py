"""
Processing Workflow for Visualization

Processes a queue item through the full pipeline and generates visualizations.
This is a simplified workflow for MVP that processes files for GUI display.
"""

import cv2
import os
from pathlib import Path

from ..utils.file_utils import ensure_queue_item_directory, save_original_file, save_preprocessed_image
from ..utils.image_preprocessing import ImagePreprocessor
from ..tasks.matching_task import match_template
from ..gui.utils.queue_utils import save_match_metadata
from ..config import get_config


def process_queue_item_for_visualization(source_file_path: str, queue_item_id: str, calling_app_id: str = "default") -> dict:
    """
    Process a queue item through the full pipeline for visualization.
    
    This function:
    1. Saves the original file
    2. Preprocesses the image
    3. Performs template matching
    4. Generates visualizations
    5. Saves metadata
    
    Args:
        source_file_path: Path to source file to process
        queue_item_id: Unique identifier for the queue item
        calling_app_id: ID of the calling application
        
    Returns:
        Dictionary with processing results:
        {
            'success': bool,
            'queue_item_id': str,
            'original_path': str,
            'preprocessed_path': str,
            'match_result': dict or None,
            'error': str or None
        }
    """
    try:
        # Ensure queue item directory exists
        queue_item_dir = ensure_queue_item_directory(queue_item_id)
        
        # Step 1: Save original file
        original_path = save_original_file(source_file_path, queue_item_id)
        
        # Step 2: Load and preprocess image
        image = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Could not load image: {original_path}")
        
        # Preprocess
        preprocessor = ImagePreprocessor()
        preprocessed_image = preprocessor.preprocess(image)
        
        # Save preprocessed image
        preprocessed_path = save_preprocessed_image(preprocessed_image, queue_item_id)
        
        # Step 3: Template matching
        match_result = None
        try:
            match_result = match_template(preprocessed_path, queue_item_id, calling_app_id)
            
            # Save match metadata
            if match_result:
                save_match_metadata(queue_item_id, match_result)
        except Exception as e:
            # Matching failed, but continue
            print(f"Template matching failed: {e}")
            match_result = {
                'matched_template_id': None,
                'match_score': 0.0,
                'template_name': None,
                'visualization_path': None,
                'fingerprint': None,
                'error': str(e)
            }
        
        return {
            'success': True,
            'queue_item_id': queue_item_id,
            'original_path': original_path,
            'preprocessed_path': preprocessed_path,
            'match_result': match_result,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'queue_item_id': queue_item_id,
            'original_path': None,
            'preprocessed_path': None,
            'match_result': None,
            'error': str(e)
        }
