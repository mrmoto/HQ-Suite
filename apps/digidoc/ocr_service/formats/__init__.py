"""
Document Format Templates
Defines format templates for different document types.
"""

from .base_format import BaseDocumentFormat
from .mead_clark_format1 import MeadClarkFormat1
# from .mead_clark_format2 import MeadClarkFormat2  # Disabled for MVP

__all__ = ['BaseDocumentFormat', 'MeadClarkFormat1']
# __all__ = ['BaseDocumentFormat', 'MeadClarkFormat1', 'MeadClarkFormat2']  # Enable when Format2 is ready
