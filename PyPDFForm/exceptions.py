# -*- coding: utf-8 -*-


class BaseException(Exception):
    """Base exception for PyPDFForm"""

    pass


class MergeError(BaseException):
    """Raised when attempting to merge none PyPDFForm typed object with PyPDFForm object"""

    pass
