# -*- coding: utf-8 -*-
"""Contains exceptions for template middleware."""

from .base import BasePyPDFFormException


class InvalidTemplateError(BasePyPDFFormException):
    """Raised when the template stream is an invalid PDF stream."""
