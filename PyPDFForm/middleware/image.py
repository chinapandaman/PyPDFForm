# -*- coding: utf-8 -*-
"""Provides middleware for PDF image field widgets.

This module contains the Image class which handles:
- Image field processing for common formats (JPEG, PNG)
- Aspect ratio preservation when scaling
- PDF form field integration
- Image rotation and positioning

Supports image data from:
- Raw bytes
- File paths
- File-like objects

Note: Inherits core functionality from Signature middleware since
PDF image fields are technically signature fields with images.
"""

from .signature import Signature


class Image(Signature):
    """Middleware for PDF image field widgets.

    Handles all aspects of image field processing including:
    - Image data handling
    - Aspect ratio control
    - PDF form field integration

    Inherits from Signature class and extends it with image-specific features.
    """

    preserve_aspect_ratio = False
    """Whether to preserve the original image's aspect ratio when scaling."""
