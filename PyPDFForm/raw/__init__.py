# -*- coding: utf-8 -*-
"""
The `raw` package provides classes representing raw drawable elements
(like text and images) that can be rendered directly onto a PDF document.

It defines `RawTypes` as a Union of all supported raw element types, used for
type hinting in methods that handle drawing onto the PDF.
"""

from dataclasses import dataclass
from typing import Union

from .circle import RawCircle
from .image import RawImage
from .line import RawLine
from .rect import RawRectangle
from .text import RawText

RawTypes = Union[RawText, RawImage, RawLine, RawRectangle, RawCircle]


@dataclass
class RawElements:
    """
    A container class that provides convenient access to all available raw drawable elements.

    This class acts as a namespace for the various `Raw` classes defined in the
    `PyPDFForm.raw` package, making it easier to reference them (e.g., `RawElements.RawText`).
    """

    RawText = RawText
    RawImage = RawImage
    RawLine = RawLine
    RawRectangle = RawRectangle
    RawCircle = RawCircle
