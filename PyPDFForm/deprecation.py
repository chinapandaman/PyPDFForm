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
    Can also be called directly within a method to emit deprecation warnings conditionally.

    Args:
        to_replace: The name of the method to use instead.
        param: Optional parameter name to include in the deprecation notice.

    Returns:
        callable: A decorator function, or a function to emit notice directly when param is provided.

    Examples:
        As a decorator (emits on every call)::

            @deprecation_notice(to_replace="new_method")
            def old_method(self):
                pass

        As a decorator with a parameter (emits on every call)::

            @deprecation_notice(to_replace="old_method.new_param.", param="old_param")
            def old_method(self, old_param=None):
                pass

        Conditionally within a method body::

            def my_method(self, use_legacy=False):
                if use_legacy:
                    deprecation_notice(to_replace="", param="use_legacy").emit_notice(self, "my_method")
                    # legacy logic here
    """

    def _emit(class_name: str, method_name: str):
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

    def decorator(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            _emit(args[0].__class__.__name__, func.__name__)
            return func(*args, **kwargs)

        return wrapper

    def emit_notice(obj, method_name: str):
        _emit(obj.__class__.__name__, method_name)

    decorator.emit_notice = emit_notice
    return decorator
