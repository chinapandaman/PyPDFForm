# -*- coding: utf-8 -*-
"""
This module defines the ImageWidget class, which is a subclass of the
SignatureWidget class. It represents an image field in a PDF document.
The ImageWidget leverages the SignatureWidget's functionality to handle
image insertion into PDF forms.
"""
# TODO: No obvious performance improvements in this file as it defines a simple class inheriting from `SignatureWidget` and sets a class-level attribute.

from .signature import SignatureWidget


class ImageWidget(SignatureWidget):
    """
    Represents an image widget in a PDF form.

    This class inherits from the SignatureWidget and is specifically designed
    for handling image fields in PDF forms. It reuses the signature widget's
    infrastructure for positioning and rendering, but instead of capturing
    a signature, it inserts a provided image.

    Attributes:
        BEDROCK_WIDGET_TO_COPY (str): The name of the bedrock widget to copy,
            set to "image".
    """

    BEDROCK_WIDGET_TO_COPY = "image"
