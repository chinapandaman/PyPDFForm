# -*- coding: utf-8 -*-

from .base import BasePyPDFFormException


class InvalidModeError(BasePyPDFFormException):
    """Raised when simple mode input is not a boolean."""

    pass


class InvalidFormDataError(BasePyPDFFormException):
    """Raised when form data input is not a dictionary."""

    pass
