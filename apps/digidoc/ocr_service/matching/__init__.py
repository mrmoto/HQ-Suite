"""
Template Matching Module

Provides structural fingerprint matching for document template identification.
"""

try:
    from .structural import compute_structural_fingerprint, compare_fingerprints
    __all__ = ['compute_structural_fingerprint', 'compare_fingerprints']
except ImportError:
    # cv2 not available
    __all__ = []
