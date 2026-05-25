# -*- coding: utf-8 -*-
"""
PyPDFForm provides Python APIs and CLI commands for working with PDF forms.

It helps users create, inspect, update, and fill PDF forms, plus handle common
PDF utilities such as extracting pages and merging documents.

The project supports PDF form features including:

- Text, checkbox, radio, dropdown, signature, and image fields.
- Field styling, sizing, positioning, visibility, and editability.
- Form data inspection and JSON schema generation.
- PDF annotations, raw drawing elements, metadata, scripts, and versions.

PyPDFForm aims to make PDF form automation straightforward whether it is used
from Python code or from the command line.
"""

import logging

__version__ = "5.1.0"

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
