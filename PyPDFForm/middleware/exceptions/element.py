# -*- coding: utf-8 -*-
"""Contains exceptions for element middleware."""

from .base import BasePyPDFFormException


class InvalidElementNameError(BasePyPDFFormException):
    """Raised when an element's name is not a string."""


class InvalidElementTypeError(BasePyPDFFormException):
    """Raised when an element's type is not an ElementType object."""


class InvalidElementValueError(BasePyPDFFormException):
    """Raised when an element's value has the wrong type."""


class InvalidFontColorError(BasePyPDFFormException):
    """Raised when font color input is not a tuple of three numerical values"""


class InvalidFontSizeError(BasePyPDFFormException):
    """Raised when font size input is not a float."""


class InvalidTextOffsetError(BasePyPDFFormException):
    """Raised when x or y text offset input is not a float or int."""


class InvalidWrapLengthError(BasePyPDFFormException):
    """Raised when text wrap length input is not an int."""


class InvalidFontError(BasePyPDFFormException):
    """Raised when font input is not a string."""
