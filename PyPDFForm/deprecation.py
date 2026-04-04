# -*- coding: utf-8 -*-
"""
A module for handling deprecation notices within the PyPDFForm library.

This module provides utility functions to issue standard DeprecationWarning
messages, ensuring consistency across the library when notifying users of
deprecated features.
"""

from functools import wraps
from warnings import warn

from .constants import DEPRECATION_NOTICE, DEPRECATION_REPLACE_NOTICE


def deprecation_notice(to_replace: str, param: str = "") -> callable:
    """
    A decorator that issues a DeprecationWarning when a deprecated method is called.

    Args:
        to_replace: The name of the method to use instead.
        param: Optional parameter name to include in the deprecation notice.

    Returns:
        callable: A decorator function.
    """

    def decorator(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            class_name = args[0].__class__.__name__
            method_name = func.__name__
            to_deprecate = (
                f"{class_name}.{method_name}.{param}"
                if param
                else f"{class_name}.{method_name}"
            )
            notice = DEPRECATION_NOTICE.format(to_deprecate)
            if to_replace:
                replacement = f"{class_name}.{to_replace}"
                notice = f"{notice} {DEPRECATION_REPLACE_NOTICE.format(replacement)}"
            warn(notice, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator
