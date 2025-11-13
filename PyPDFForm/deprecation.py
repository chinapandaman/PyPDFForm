# -*- coding: utf-8 -*-
"""
A module for handling deprecation notices within the PyPDFForm library.

This module provides utility functions to issue standard DeprecationWarning
messages, ensuring consistency across the library when notifying users of
deprecated features.
"""

from warnings import warn

from .constants import DEPRECATION_NOTICE


def deprecation_notice(to_deprecate: str, to_replace: str) -> None:
    """
    Issues a DeprecationWarning for a feature that is being deprecated.

    Args:
        to_deprecate (str): The name of the feature or function being deprecated.
        to_replace (str): The name of the feature or function that should be used instead.
    """
    warn(
        DEPRECATION_NOTICE.format(
            to_deprecate,
            to_replace,
        ),
        DeprecationWarning,  # noqa: PT030
        stacklevel=3,
    )
