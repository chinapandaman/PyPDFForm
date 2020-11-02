# -*- coding: utf-8 -*-


class BasePyPDFFormException(Exception):
    """Base exception for PyPDFForm"""

    pass


class InvalidTemplateError(Exception):
    """Raised when the template stream is an invalid PDF stream"""

    pass
