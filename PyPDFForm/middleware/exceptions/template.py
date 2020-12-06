# -*- coding: utf-8 -*-

from .base import BasePyPDFFormException


class InvalidTemplateError(BasePyPDFFormException):
    """Raised when the template stream is an invalid PDF stream."""

    pass
