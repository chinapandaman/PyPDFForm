# -*- coding: utf-8 -*-
"""
PyPDFForm is a pure Python library designed to streamline the process of filling PDF forms programmatically.

It provides a simple and intuitive API for interacting with PDF forms, allowing users to:

- Fill text fields with custom data.
- Check or uncheck checkboxes.
- Select radio button options.
- Add images to image fields.
- Flatten the filled form to prevent further modifications.

The library supports various PDF form features, including:

- Text field alignment (left, center, right).
- Font customization (size, color, family).
- Image field resizing and positioning.
- Handling of complex form structures.

PyPDFForm aims to simplify PDF form manipulation, making it accessible to developers of all skill levels.
"""

__version__ = "4.5.1"

from .annotations import Annotations
from .assets.blank import BlankPage
from .middleware import Widgets
from .raw import RawElements
from .types import PdfArray
from .widgets import Fields
from .wrapper import PdfWrapper

__all__ = [
    "PdfWrapper",
    "PdfArray",
    "Annotations",
    "Fields",
    "BlankPage",
    "RawElements",
    "Widgets",
]
