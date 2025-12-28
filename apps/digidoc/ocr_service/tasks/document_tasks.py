"""
Document Processing Tasks

Queue-agnostic task functions for document processing.
These functions are pure Python with no queue-specific code.
"""

# Configure multiprocessing to use 'spawn' instead of 'fork' on macOS
# This prevents crashes when RQ worker forks processes with Objective-C runtime initialized
import multiprocessing
if hasattr(multiprocessing, 'set_start_method'):
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        # Already set, ignore
        pass

import os
import yaml
import subprocess
import platform
from typing import Dict, Any, Optional
from pathlib import Path

from ..config import get_config
from ..utils.file_utils import get_queue_item_directory, ensure_queue_item_directory
from ..utils.image_preprocessing import ImagePreprocessor
from ..matching.structural import compute_structural_fingerprint, compare_fingerprints
from ..database.models import CachedTemplate, get_session
from .matching_task import match_template
from ..extractors.document_extractor import DocumentExtractor

# Import cv2 for image operations
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def _load_skeleton_config() -> Dict[str, Any]:
    """
    Load skeleton development configuration.
    
    Returns skeleton.yaml config if it exists, otherwise returns empty dict.
    This allows graceful fallback if skeleton.yaml is not present.
    """
    # Find skeleton.yaml in Construction_Suite/development/ directory
    # Path: ocr_service/tasks/document_tasks.py -> digidoc -> apps -> Construction_Suite -> development/
    ocr_service_dir = Path(__file__).parent.parent.parent  # digidoc/
    construction_suite_dir = ocr_service_dir.parent.parent  # Construction_Suite/
    skeleton_path = construction_suite_dir / 'development' / 'skeleton.yaml'
    
    if skeleton_path.exists():
        try:
            with open(skeleton_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load skeleton.yaml: {e}")
            return {}
    return {}


def _save_preprocessing_comparison(original_path: str, preprocessed_image, queue_item_id: str) -> str:
    """
    Save before/after comparison image for visual verification.
    
    Args:
        original_path: Path to original image
        preprocessed_image: Preprocessed image as numpy array
        queue_item_id: Queue item ID
        
    Returns:
        Path to comparison image
    """
    if not CV2_AVAILABLE:
        print("Warning: OpenCV not available, skipping comparison image")
        return None
    
    queue_dir = Path(ensure_queue_item_directory(queue_item_id))
    comparison_path = queue_dir / 'preprocessing_comparison.png'
    
    try:
        # Load original image
        original = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
        if original is None:
            print(f"Warning: Could not load original image: {original_path}")
            return None
        
        # Get dimensions
        h1, w1 = original.shape
        h2, w2 = preprocessed_image.shape
        
        # Use max dimensions
        max_h = max(h1, h2)
        max_w = max(w1, w2)
        
        # Create side-by-side comparison
        comparison = np.zeros((max_h, w1 + w2 + 20), dtype=np.uint8)
        comparison[:h1, :w1] = original
        comparison[:h2, w1 + 20:w1 + 20 + w2] = preprocessed_image
        
        # Save comparison
        cv2.imwrite(str(comparison_path), comparison)
        return str(comparison_path)
    except Exception as e:
        print(f"Warning: Could not create comparison image: {e}")
        return None


def _visual_verification_pause(original_path: str, preprocessed_path: str, comparison_path: Optional[str], skeleton_config: Dict[str, Any]):
    """
    Pause workflow for visual verification of preprocessing results.
    
    Args:
        original_path: Path to original image
        preprocessed_path: Path to preprocessed image
        comparison_path: Path to comparison image (if created)
        skeleton_config: Skeleton configuration dict
    """
    visual_config = skeleton_config.get('preprocessing', {}).get('visual_verification', {})
    
    if not visual_config.get('enabled', True):
        return
    
    print("\n" + "=" * 60)
    print("PREPROCESSING VISUAL VERIFICATION")
    print("=" * 60)
    print(f"Original image: {original_path}")
    print(f"Preprocessed image: {preprocessed_path}")
    if comparison_path:
        print(f"Comparison image: {comparison_path}")
    print("\nPlease review the preprocessing results.")
    
    # Auto-open images on macOS if configured
    if visual_config.get('auto_open_images', False) and platform.system() == 'Darwin':
        try:
            if comparison_path and os.path.exists(comparison_path):
                subprocess.run(['open', comparison_path], check=False)
            else:
                subprocess.run(['open', original_path], check=False)
                subprocess.run(['open', preprocessed_path], check=False)
        except Exception as e:
            print(f"Warning: Could not auto-open images: {e}")
    
    # Wait for user input
    wait_seconds = visual_config.get('wait_seconds', 0)
    if wait_seconds > 0:
        import time
        print(f"\nWaiting {wait_seconds} seconds before continuing...")
        time.sleep(wait_seconds)
    else:
        # Check if stdin is available (interactive terminal) and not running in RQ worker
        import sys
        # Detect RQ worker context - RQ sets certain environment variables
        is_rq_worker = os.environ.get('RQ_WORKER_ID') is not None or 'rq' in sys.modules
        
        if sys.stdin.isatty() and not is_rq_worker:
            try:
                input("\nPress Enter to continue processing...")
            except (EOFError, KeyboardInterrupt):
                print("\nSkipping interactive pause (no stdin available)")
        else:
            if is_rq_worker:
                print("\nSkipping interactive pause (RQ worker context)")
            else:
                print("\nSkipping interactive pause (non-interactive environment)")
    
    print("Continuing with processing...\n")


def process_document_task(file_path: str, queue_item_id: str, calling_app_id: str) -> Dict[str, Any]:
    """
    Main document processing task.
    
    This is a queue-agnostic function that processes a document through the full pipeline:
    1. Preprocessing
    2. Template matching (structural fingerprinting)
    3. Field extraction (zonal OCR)
    4. Confidence scoring
    5. Route to review or auto-process
    
    Args:
        file_path: Path to the document image file
        queue_item_id: Unique identifier for this queue item
        calling_app_id: ID of the calling application (required)
        
    Returns:
        Dict with processing results and status
    """
    config = get_config()
    skeleton_config = _load_skeleton_config()
    
    try:
        # Ensure queue item directory exists
        queue_dir = Path(ensure_queue_item_directory(queue_item_id))
        
        # Step 1: Save original file
        from ..utils.file_utils import save_original_file
        original_path = save_original_file(file_path, queue_item_id)
        
        # Step 2: Preprocessing
        preprocessed_image = ImagePreprocessor.preprocess(file_path)
        
        # Save preprocessed image
        from ..utils.file_utils import save_preprocessed_image
        preprocessed_path = save_preprocessed_image(preprocessed_image, queue_item_id)
        
        # Step 2.5: Visual Verification (Skeleton Development)
        comparison_path = None
        visual_config = skeleton_config.get('preprocessing', {}).get('visual_verification', {})
        if visual_config.get('save_comparison', True):
            comparison_path = _save_preprocessing_comparison(original_path, preprocessed_image, queue_item_id)
        
        # Pause for visual verification
        _visual_verification_pause(original_path, preprocessed_path, comparison_path, skeleton_config)
        
        # Step 3: Template matching
        process_config = skeleton_config.get('process_receipt', {})
        template_config = process_config.get('template_matching', {})
        use_mock_matching = template_config.get('use_mock_matching', False)
        fallback_confidence = template_config.get('fallback_confidence', 0.85)
        mock_template_name = template_config.get('mock_template_name', 'mock_template')
        
        best_match = None
        best_score = fallback_confidence
        
        if use_mock_matching:
            # Emergency override: use mock
            print("Using mock template matching (skeleton mode override)")
            best_match = type('MockTemplate', (), {'format_name': mock_template_name, 'id': None})()
        else:
            # Real template matching using structural fingerprinting
            try:
                match_result = match_template(preprocessed_path, queue_item_id, calling_app_id)
                best_score = match_result.get('match_score', 0.0)
                matched_template_id = match_result.get('matched_template_id')
                template_name = match_result.get('template_name')
                
                if matched_template_id:
                    # Load template from DB for full details
                    session = get_session()
                    try:
                        best_match = session.query(CachedTemplate).filter_by(
                            template_id=matched_template_id,
                            calling_app_id=calling_app_id
                        ).first()
                    finally:
                        session.close()
                else:
                    # No match found, use fallback
                    best_match = None
                    if best_score == 0.0:
                        # No templates exist in database
                        best_score = fallback_confidence
                        print(f"No templates found in database, using fallback confidence: {fallback_confidence}")
            except Exception as e:
                # If template matching fails, use fallback from skeleton config
                print(f"Template matching error, using fallback: {e}")
                best_match = None
                best_score = fallback_confidence
        
        # Use mock template name if no match found
        if not best_match:
            best_match = type('MockTemplate', (), {'format_name': mock_template_name, 'id': None})()
        
        # Step 4: Decision logic
        decision_config = process_config.get('decision_logic', {})
        auto_match_threshold_override = decision_config.get('auto_match_threshold_override')
        force_status = decision_config.get('force_status')
        
        # Use override if provided, otherwise use config
        auto_match_threshold = auto_match_threshold_override if auto_match_threshold_override is not None else config.thresholds.auto_match
        
        # Force status if configured (for skeleton testing)
        if force_status:
            return {
                'status': force_status,
                'confidence': best_score,
                'template_matched': best_match.format_name if best_match else None,
                'queue_item_id': queue_item_id,
                'preprocessed_path': preprocessed_path,
                'original_path': original_path,
                'comparison_path': comparison_path,
                'skeleton_mode': True
            }
        
        if best_score >= auto_match_threshold:
            # Auto-process: Extract fields using real zonal OCR
            extraction_result = extract_fields_task(preprocessed_path, queue_item_id, best_match.id if best_match else None)
            
            # Prepare result with extracted fields
            result = {
                'status': 'completed',
                'confidence': best_score,
                'template_matched': best_match.format_name if best_match else mock_template_name,
                'extracted_fields': extraction_result.get('extracted_fields', {}),
                'queue_item_id': queue_item_id,
                'preprocessed_path': preprocessed_path,
                'original_path': original_path,
                'comparison_path': comparison_path,
                'skeleton_mode': extraction_result.get('skeleton_mode', False)
            }
            
            # Add extraction metadata if available
            if 'extraction_metadata' in extraction_result:
                result['extraction_metadata'] = extraction_result['extraction_metadata']
            
            return result
        else:
            # Route to review queue
            return {
                'status': 'review',
                'confidence': best_score,
                'template_matched': best_match.format_name if best_match else None,
                'message': 'Low confidence - requires human review',
                'queue_item_id': queue_item_id,
                'preprocessed_path': preprocessed_path,
                'original_path': original_path,
                'comparison_path': comparison_path,
                'skeleton_mode': True
            }
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in process_document_task: {error_trace}")
        
        return {
            'status': 'failed',
            'error': str(e),
            'queue_item_id': queue_item_id
        }


def preprocess_image_task(file_path: str, queue_item_id: str) -> Dict[str, Any]:
    """
    Preprocess an image file.
    
    Args:
        file_path: Path to the image file
        queue_item_id: Unique identifier for this queue item
        
    Returns:
        Dict with preprocessing results
    """
    config = get_config()
    
    try:
        queue_dir = ensure_queue_item_directory(queue_item_id)
        
        preprocessed_image = ImagePreprocessor.preprocess(file_path)
        
        # TODO: Save preprocessed image to queue_dir/preprocessed.png
        
        return {
            'status': 'success',
            'queue_item_id': queue_item_id,
            'preprocessed_path': str(queue_dir / 'preprocessed.png')
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'queue_item_id': queue_item_id
        }


def extract_fields_task(image_path: str, queue_item_id: str, template_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract fields from a document using zonal OCR.
    
    Args:
        image_path: Path to the preprocessed document image file
        queue_item_id: Unique identifier for this queue item
        template_id: ID of the matched template (if available)
        
    Returns:
        Dict with extracted fields and extraction metadata
    """
    skeleton_config = _load_skeleton_config()
    process_config = skeleton_config.get('process_receipt', {})
    extraction_config = process_config.get('field_extraction', {})
    use_mock_extraction = extraction_config.get('use_mock_extraction', False)  # Default to False (real extraction)
    
    if use_mock_extraction:
        # Emergency override: use mock (for testing/debugging)
        mock_fields = extraction_config.get('mock_fields', {
            'total': '0.00',
            'date': '2025-12-23',
            'vendor': 'Mock Vendor'
        })
        
        return {
            'status': 'success',
            'queue_item_id': queue_item_id,
            'template_id': template_id,
            'extracted_fields': mock_fields,
            'skeleton_mode': True
        }
    
    # Real zonal OCR extraction using DocumentExtractor
    try:
        extractor = DocumentExtractor()
        extraction_result = extractor.extract(image_path)
        
        # Extract the fields from the result
        extracted_fields = extraction_result.get('fields', {})
        
        # Add extraction metadata
        return {
            'status': 'success',
            'queue_item_id': queue_item_id,
            'template_id': template_id,
            'extracted_fields': extracted_fields,
            'extraction_metadata': {
                'vendor': extraction_result.get('vendor'),
                'format_detected': extraction_result.get('format_detected'),
                'confidence': extraction_result.get('confidence'),
                'confidence_level': extraction_result.get('confidence_level'),
                'ocr_text_length': len(extraction_result.get('ocr_text', '')),
            },
            'skeleton_mode': False
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in extract_fields_task: {error_trace}")
        
        # Return empty fields on error, but don't fail the task
        return {
            'status': 'partial',
            'queue_item_id': queue_item_id,
            'template_id': template_id,
            'extracted_fields': {},
            'error': str(e),
            'skeleton_mode': False
        }

