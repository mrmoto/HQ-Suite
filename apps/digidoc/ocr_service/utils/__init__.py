"""
Utility Functions
Image preprocessing, text processing, and helper functions.
"""

# Lazy imports to avoid requiring cv2 at module level
try:
    from .image_preprocessing import ImagePreprocessor
    __all__ = ['ImagePreprocessor']
except ImportError:
    # cv2 not available, ImagePreprocessor won't be importable
    __all__ = []

try:
    from .text_utils import TextUtils
    if 'TextUtils' not in __all__:
        __all__.append('TextUtils')
except ImportError:
    pass
