# -*- coding: utf-8 -*-
"""Contains exceptions for input validation."""

from .base import BasePyPDFFormException


class InvalidModeError(BasePyPDFFormException):
    """Raised when simple mode input is not a boolean."""


class InvalidFormDataError(BasePyPDFFormException):
    """Raised when form data input is not a dictionary with appropriate key value types."""


class InvalidEditableParameterError(BasePyPDFFormException):
    """Raised when editable input is not a boolean."""


class InvalidImageError(BasePyPDFFormException):
    """Raised when the image stream is an invalid image."""


class InvalidPageNumberError(BasePyPDFFormException):
    """Raised when page number input is not an int."""


class InvalidCoordinateError(BasePyPDFFormException):
    """Raised when x or y coordinate input is not a float or int."""


class InvalidImageDimensionError(BasePyPDFFormException):
    """Raised when width or height dimension input is not a float or int."""


class InvalidImageRotationAngleError(BasePyPDFFormException):
    """Raised when rotation angle input is not a float or int."""


class InvalidTextError(BasePyPDFFormException):
    """Raised when text input is not a string."""


class InvalidTTFFontError(BasePyPDFFormException):
    """Raised when attempting to register an invalid ttf font."""
