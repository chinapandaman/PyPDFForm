# -*- coding: utf-8 -*-


class BasePyPDFFormException(Exception):
    """Base exception for PyPDFForm."""

    pass


class InvalidTemplateError(BasePyPDFFormException):
    """Raised when the template stream is an invalid PDF stream."""

    pass


class InvalidFormDataError(BasePyPDFFormException):
    """Raised when form data input is not a dictionary."""

    pass


class InvalidModeError(BasePyPDFFormException):
    """Raised when simple mode input is not a boolean."""

    pass


class InvalidFontSizeError(BasePyPDFFormException):
    """Raised when font size input is not a float."""

    pass


class InvalidFontColorError(BasePyPDFFormException):
    """Raised when font color input is not a tuple of three numerical values"""

    pass


class InvalidWrapLengthError(BasePyPDFFormException):
    """Raised when text wrap length input is not an int."""

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


class InvalidTextOffsetError(BasePyPDFFormException):
    """Raised when x or y text offset input is not a float or int."""

    pass


class InvalidEditableParameterError(BasePyPDFFormException):
    """Raised when editable input is not a boolean."""

    pass


class InvalidTextError(BasePyPDFFormException):
    """Raised when text input is not a string."""

    pass


class InvalidElementNameError(BasePyPDFFormException):
    """Raised when an element's name is not a string."""

    pass


class InvalidElementTypeError(BasePyPDFFormException):
    """Raised when an element's type is not an ElementType object."""

    pass


class InvalidElementValueError(BasePyPDFFormException):
    """Raised when an element's value has the wrong type."""

    pass
