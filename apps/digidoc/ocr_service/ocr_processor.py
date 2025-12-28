"""
OCR Processor
Main OCR processing module using Tesseract.
"""

import os
import pytesseract
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional, Tuple
from .utils.image_preprocessing import ImagePreprocessor
from .formats.mead_clark_format1 import MeadClarkFormat1
# from .formats.mead_clark_format2 import MeadClarkFormat2  # Disabled for MVP


class OCRProcessor:
    """Processes receipt images using Tesseract OCR."""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize OCR processor.
        
        Args:
            tesseract_cmd: Path to tesseract executable (if not in PATH)
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            # Try to find tesseract in common locations
            self._find_tesseract()
        
        # Initialize format templates
        # For MVP: Only load Format1. Architecture supports multiple formats.
        self.formats = [
            MeadClarkFormat1(),
            # MeadClarkFormat2(),  # Disabled for MVP - will be enabled when needed
        ]
    
    def _find_tesseract(self):
        """Try to find tesseract executable."""
        # Common macOS locations
        common_paths = [
            '/usr/local/bin/tesseract',
            '/opt/homebrew/bin/tesseract',
            '/usr/bin/tesseract',
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return
    
    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process receipt image and extract text.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with OCR results:
            {
                'text': str,
                'conf': list of confidence scores,
                'data': Tesseract data dictionary
            }
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Preprocess image
        preprocessed = ImagePreprocessor.preprocess(image_path)
        
        # Resize if needed (for performance)
        preprocessed = ImagePreprocessor.resize_if_needed(preprocessed, max_dimension=2000)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(preprocessed)
        
        # Run OCR with detailed data
        try:
            # Get text
            text = pytesseract.image_to_string(pil_image)
            
            # Get detailed data with confidence scores
            data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
            
            # Extract confidence scores
            confidences = data.get('conf', [])
            
            return {
                'text': text,
                'conf': confidences,
                'data': data,
            }
        except Exception as e:
            raise RuntimeError(f"OCR processing failed: {str(e)}")
    
    def detect_format(self, text: str) -> Tuple[Optional[Any], float]:
        """
        Detect receipt format from OCR text.
        
        Args:
            text: OCR extracted text
            
        Returns:
            Tuple of (format_template, confidence)
        """
        best_format = None
        best_confidence = 0.0
        
        for format_template in self.formats:
            matches, confidence = format_template.detect_format(text)
            if matches and confidence > best_confidence:
                best_format = format_template
                best_confidence = confidence
        
        return best_format, best_confidence
    
    def extract_text_with_confidence(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text from image with confidence information.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with text and confidence data
        """
        return self.process_image(image_path)
