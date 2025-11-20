# -*- coding: utf-8 -*-
"""
The `middleware` package provides intermediate classes used internally
to manage and manipulate PDF form widgets, abstracting away some of the
low-level PDF details.

These classes are typically used during the filling process to represent
the state and attributes of various form field types within the PDF.
"""

from dataclasses import dataclass

from .checkbox import Checkbox
from .dropdown import Dropdown
from .image import Image
from .radio import Radio
from .signature import Signature
from .text import Text


@dataclass
class Widgets:
    """
    A container class that provides convenient access to all available middleware widget classes.

    This class acts as a namespace for the various middleware classes defined in the
    `PyPDFForm.middleware` package, making it easier to reference them (e.g., `Widgets.Text`).
    """

    Text = Text
    Checkbox = Checkbox
    Radio = Radio
    Dropdown = Dropdown
    Signature = Signature
    Image = Image
