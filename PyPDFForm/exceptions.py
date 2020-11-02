# -*- coding: utf-8 -*-


class BasePyPDFFormException(Exception):
    """Base exception for PyPDFForm"""

    pass


class InvalidTemplateError(Exception):
    """Raised when the template stream is an invalid PDF stream"""

    pass


class InvalidFormDataError(Exception):
    """Raised when form data input is not a dictionary"""

    pass


class InvalidModeError(Exception):
    """Raised when simple mode input is not a boolean"""

    pass


class InvalidFontSizeError(Exception):
    """Raised when font size input is not a float"""

    pass


class InvalidWrapLengthError(Exception):
    """Raised when text wrap length input is not an int"""

    pass
