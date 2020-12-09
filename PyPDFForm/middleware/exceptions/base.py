# -*- coding: utf-8 -*-


class BasePyPDFFormException(Exception):
    """Base exception for PyPDFForm."""

    pass


class InvalidImageError(BasePyPDFFormException):
    """Raised when the image stream is an invalid image."""

    pass


class InvalidPageNumberError(BasePyPDFFormException):
    """Raised when page number input is not an int."""

    pass


class InvalidCoordinateError(BasePyPDFFormException):
    """Raised when x or y coordinate input is not a float or int."""

    pass


class InvalidImageDimensionError(BasePyPDFFormException):
    """Raised when width or height dimension input is not a float or int."""

    pass


class InvalidImageRotationAngleError(BasePyPDFFormException):
    """Raised when rotation angle input is not a float or int."""

    pass


class InvalidEditableParameterError(BasePyPDFFormException):
    """Raised when editable input is not a boolean."""

    pass


class InvalidTextError(BasePyPDFFormException):
    """Raised when text input is not a string."""

    pass
