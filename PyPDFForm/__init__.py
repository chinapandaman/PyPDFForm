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

__version__ = "3.8.1"

from .assets.blank import BlankPage
from .middleware import Widgets
from .middleware.text import Text  # TODO: deprecate in v4.0.0
from .raw import RawElements
from .widgets import Fields
from .wrapper import PdfWrapper

__all__ = ["PdfWrapper", "Text", "Fields", "BlankPage", "RawElements", "Widgets"]
