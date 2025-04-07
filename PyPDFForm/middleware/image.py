# -*- coding: utf-8 -*-
"""Provides middleware for PDF image field widgets.

This module contains the Image class which handles:
- Image field processing
- Aspect ratio preservation
- PDF form field integration
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
