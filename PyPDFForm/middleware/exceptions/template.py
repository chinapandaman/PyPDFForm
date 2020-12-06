# -*- coding: utf-8 -*-

from middleware.exceptions.base import BasePyPDFFormException


class InvalidTemplateError(BasePyPDFFormException):
    """Raised when the template stream is an invalid PDF stream."""

    pass
