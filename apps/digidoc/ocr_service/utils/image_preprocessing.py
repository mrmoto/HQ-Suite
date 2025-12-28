"""
Image Preprocessing Utilities
Handles image enhancement, deskewing, denoising, and contrast adjustment.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional
from ..config import get_config


class ImagePreprocessor:
    """Preprocess images for better OCR accuracy."""
    
    @staticmethod
    def preprocess(image_path: str) -> np.ndarray:
        """
        Preprocess image for OCR.
        
        Loads all preprocessing parameters from config.
        Pipeline order per MASTER_ARCHITECTURE.md:
        Deskew → Denoise → Binarize → Scale Normalization → Border Removal
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image as numpy array
        """
        # Load config
        config = get_config()
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply preprocessing steps in correct order (per MASTER_ARCHITECTURE.md)
        # All methods load their parameters from config
        gray = ImagePreprocessor._deskew(gray)           # Step 1: Deskew
        gray = ImagePreprocessor._denoise(gray)          # Step 2: Denoise
        gray = ImagePreprocessor._binarize(gray)         # Step 3: Binarize
        gray = ImagePreprocessor._normalize_scale(gray)  # Step 4: Scale Normalization
        gray = ImagePreprocessor._remove_borders(gray)   # Step 5: Border Removal
        
        return gray
    
    @staticmethod
    def _denoise(image: np.ndarray) -> np.ndarray:
        """
        Remove noise from image using fastNlMeansDenoising.
        
        Uses non-local means denoising which is more effective than bilateral filter
        for document images with text.
        """
        # Load denoise level from config
        config = get_config()
        denoise_level = config.preprocessing.denoise_level.lower()
        
        # Map denoise level to parameters
        # h: Filter strength (higher = more denoising, but slower)
        # templateWindowSize: Size of template patch (typically 7)
        # searchWindowSize: Size of search window (typically 21)
        denoise_params = {
            'low': {'h': 3, 'templateWindowSize': 7, 'searchWindowSize': 21},
            'medium': {'h': 5, 'templateWindowSize': 7, 'searchWindowSize': 21},
            'high': {'h': 7, 'templateWindowSize': 7, 'searchWindowSize': 21},
        }
        
        # Default to medium if level not recognized
        params = denoise_params.get(denoise_level, denoise_params['medium'])
        
        # Apply fastNlMeansDenoising
        denoised = cv2.fastNlMeansDenoising(
            image,
            h=params['h'],
            templateWindowSize=params['templateWindowSize'],
            searchWindowSize=params['searchWindowSize']
        )
        
        return denoised
    
    @staticmethod
    def _enhance_contrast(image: np.ndarray) -> np.ndarray:
        """
        Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization).
        
        Note: This step is not in the final 5-step pipeline per MASTER_ARCHITECTURE.md.
        Will be removed or made optional in Phase 3 when full pipeline is implemented.
        """
        # TODO: Make these parameters configurable in future
        # For MVP, using reasonable defaults
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        return enhanced
    
    @staticmethod
    def _binarize(image: np.ndarray) -> np.ndarray:
        """
        Binarize image using adaptive thresholding.
        
        Converts grayscale image to binary (black and white) for better OCR accuracy.
        Loads binarization method from config (otsu or gaussian).
        
        Args:
            image: Grayscale image
            
        Returns:
            Binary image (0 or 255)
        """
        # Load binarization method from config
        config = get_config()
        method = config.preprocessing.binarization_method.lower()
        
        if method == 'otsu':
            # Otsu's method: automatically determines optimal threshold
            _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == 'gaussian':
            # Gaussian adaptive threshold: adapts to local image characteristics
            binary = cv2.adaptiveThreshold(
                image,
                255,                                    # Max value
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,        # Adaptive method
                cv2.THRESH_BINARY,                     # Threshold type
                11,                                     # Block size (must be odd)
                2                                       # Constant subtracted from mean
            )
        else:
            # Default to Otsu if method not recognized
            _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    @staticmethod
    def _normalize_scale(image: np.ndarray) -> np.ndarray:
        """
        Normalize image scale to target DPI.
        
        Resizes image to match target DPI (typically 300 DPI for OCR).
        If current DPI cannot be detected, estimates based on image dimensions
        and typical scanner resolutions.
        
        Args:
            image: Grayscale or binary image
            
        Returns:
            Image normalized to target DPI
        """
        # Load target DPI from config
        config = get_config()
        target_dpi = config.preprocessing.target_dpi
        
        # Estimate current DPI
        # For MVP: Assume typical scanner resolution if not in metadata
        # Common scanner DPIs: 150, 200, 300, 400, 600
        # Default assumption: 200 DPI (common for document scanners)
        estimated_current_dpi = 200
        
        # TODO: In future, extract DPI from image metadata (EXIF, etc.)
        # For now, use estimated DPI
        
        # Calculate scale factor
        if estimated_current_dpi == target_dpi:
            return image  # No scaling needed
        
        scale_factor = target_dpi / estimated_current_dpi
        
        # Calculate new dimensions
        h, w = image.shape[:2]
        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)
        
        # Resize using cubic interpolation for better quality
        normalized = cv2.resize(
            image,
            (new_w, new_h),
            interpolation=cv2.INTER_CUBIC
        )
        
        return normalized
    
    @staticmethod
    def _remove_borders(image: np.ndarray) -> np.ndarray:
        """
        Remove white borders from image using contour analysis.
        
        Detects white borders around document content and crops to content area.
        Useful for scanned documents that have white margins.
        
        Args:
            image: Grayscale or binary image
            
        Returns:
            Image with borders removed (cropped to content)
        """
        # Check if border removal is enabled in config
        config = get_config()
        if not config.preprocessing.border_removal_enabled:
            return image
        
        # For binary images, find non-white content
        # For grayscale, threshold to find content vs borders
        if len(image.shape) == 2:
            # Binary or grayscale image
            # Invert if needed (assuming white borders, dark content)
            # For binary images, content is typically black (0) and borders white (255)
            # For grayscale, we'll threshold to find content
            
            # Create a mask: find areas that are not pure white
            # Threshold: pixels darker than 240 (out of 255) are considered content
            _, mask = cv2.threshold(image, 240, 255, cv2.THRESH_BINARY_INV)
        else:
            # Color image (shouldn't happen in preprocessing pipeline, but handle it)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours of content areas
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            # No content found, return original
            return image
        
        # Find bounding box of all content
        # Combine all contours to get overall bounding box
        all_points = np.concatenate(contours)
        x, y, w, h = cv2.boundingRect(all_points)
        
        # Add small padding to avoid cutting content (5% of dimension, min 10px)
        h_img, w_img = image.shape[:2]
        pad_x = max(10, int(w * 0.05))
        pad_y = max(10, int(h * 0.05))
        
        # Ensure we don't go outside image bounds
        x = max(0, x - pad_x)
        y = max(0, y - pad_y)
        w = min(w_img - x, w + 2 * pad_x)
        h = min(h_img - y, h + 2 * pad_y)
        
        # Crop to content area
        cropped = image[y:y+h, x:x+w]
        
        return cropped
    
    @staticmethod
    def _deskew(image: np.ndarray) -> np.ndarray:
        """
        Deskew image by detecting and correcting rotation using HoughLinesP.
        
        Uses line detection to find dominant text lines and calculate rotation angle.
        
        Args:
            image: Grayscale image
            
        Returns:
            Deskewed image
        """
        # Check if deskew is enabled in config
        config = get_config()
        if not config.preprocessing.deskew_enabled:
            return image
        
        # Apply edge detection to find lines
        # TODO: Make Canny parameters configurable in future
        # For MVP, using reasonable defaults
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        
        # Detect lines using HoughLinesP
        # TODO: Make HoughLinesP parameters configurable in future
        # For MVP, using reasonable defaults
        lines = cv2.HoughLinesP(
            edges,
            rho=1,              # Distance resolution in pixels
            theta=np.pi/180,    # Angular resolution in radians (1 degree)
            threshold=100,      # Minimum votes for a line
            minLineLength=100,  # Minimum line length
            maxLineGap=10       # Maximum gap between line segments
        )
        
        if lines is None or len(lines) == 0:
            return image
        
        # Calculate angles from detected lines
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Calculate angle in degrees
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            # Normalize to -45 to 45 degrees (typical text rotation range)
            if angle > 45:
                angle = angle - 90
            elif angle < -45:
                angle = angle + 90
            angles.append(angle)
        
        if len(angles) == 0:
            return image
        
        # Use median angle to be robust against outliers
        median_angle = np.median(angles)
        
        # Only correct if angle is significant (> 0.5 degrees)
        if abs(median_angle) > 0.5:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            rotated = cv2.warpAffine(
                image, 
                M, 
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            return rotated
        
        return image
    
    @staticmethod
    def resize_if_needed(image: np.ndarray, max_dimension: int = 2000) -> np.ndarray:
        """
        Resize image if it's too large (to improve OCR speed).
        
        Args:
            image: Image array
            max_dimension: Maximum width or height
            
        Returns:
            Resized image if needed, original otherwise
        """
        h, w = image.shape[:2]
        
        if max(h, w) > max_dimension:
            if h > w:
                scale = max_dimension / h
            else:
                scale = max_dimension / w
            
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            return resized
        
        return image
