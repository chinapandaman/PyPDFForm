# -*- coding: utf-8 -*-

from .base import BasePyPDFFormException


class InvalidElementNameError(BasePyPDFFormException):
    """Raised when an element's name is not a string."""

    pass


class InvalidElementTypeError(BasePyPDFFormException):
    """Raised when an element's type is not an ElementType object."""

    pass


class InvalidElementValueError(BasePyPDFFormException):
    """Raised when an element's value has the wrong type."""

    pass


class InvalidFontColorError(BasePyPDFFormException):
    """Raised when font color input is not a tuple of three numerical values"""

    pass


class InvalidFontSizeError(BasePyPDFFormException):
    """Raised when font size input is not a float."""

    pass


class InvalidTextOffsetError(BasePyPDFFormException):
    """Raised when x or y text offset input is not a float or int."""

    pass


class InvalidWrapLengthError(BasePyPDFFormException):
    """Raised when text wrap length input is not an int."""

    pass
