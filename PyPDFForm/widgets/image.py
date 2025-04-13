# -*- coding: utf-8 -*-
"""
This module provides the ImageWidget class for creating and customizing
image fields in PDF forms. It extends SignatureWidget to enable placement
of image widgets on specified pages and coordinates, using an image field
template instead of a signature field template.
"""

from .signature import SignatureWidget


class ImageWidget(SignatureWidget):
    """
    A widget for adding an image field to a PDF form.

    Inherits from SignatureWidget, but uses an image widget template
    instead of a signature field template. All initialization parameters
    and methods are inherited from SignatureWidget.

    Attributes:
        BEDROCK_WIDGET_TO_COPY (str): The widget type to copy from the bedrock template ("image").
    """

    BEDROCK_WIDGET_TO_COPY = "image"
