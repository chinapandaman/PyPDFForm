# -*- coding: utf-8 -*-
"""
This module defines the `ImageField` and `ImageWidget` classes, which are used
to represent and manipulate image form fields within PDF documents.

The `ImageField` class is a dataclass that encapsulates the properties of an
image field, inheriting from `SignatureField` for its dimensional attributes.

The `ImageWidget` class extends the base `SignatureWidget` class to provide
specific functionality for interacting with image form fields in PDFs,
leveraging the existing infrastructure for positioning and rendering.
"""

from dataclasses import dataclass
from typing import Type

from .signature import SignatureField, SignatureWidget


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


@dataclass
class ImageField(SignatureField):
    """
    Represents an image field in a PDF document.

    This dataclass extends the `SignatureField` base class and defines the
    specific attributes for an image input field. It inherits `width` and
    `height` from `SignatureField` as images also have dimensions.

    Attributes:
        _field_type (str): The type of the field, fixed as "image".
        _widget_class (Type[ImageWidget]): The widget class associated with this field type.
    """

    _field_type: str = "image"
    _widget_class: Type[ImageWidget] = ImageWidget
