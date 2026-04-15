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

import logging

__version__ = "4.8.0"

from .lib.annotations import Annotations
from .lib.assets.blank import BlankPage
from .lib.middleware import Widgets
from .lib.raw import RawElements
from .lib.types import PdfArray
from .lib.widgets import Fields
from .lib.wrapper import PdfWrapper

# TODO: figure out why `Annotation sizes differ:`
for logger in [
    logging.getLogger(name) for name in getattr(logging.root.manager, "loggerDict")
]:
    if "pypdf" in logger.name:
        logger.setLevel(logging.ERROR)

__all__ = [
    "PdfWrapper",
    "PdfArray",
    "Annotations",
    "Fields",
    "BlankPage",
    "RawElements",
    "Widgets",
]
