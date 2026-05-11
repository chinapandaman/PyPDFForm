# -*- coding: utf-8 -*-
"""
Shared helpers used by multiple PyPDFForm interfaces.

These utilities contain behavior that should stay consistent across the CLI,
web API, and any future user-facing entry points.
"""

from collections.abc import Callable
from typing import NoReturn

from .. import PdfWrapper
from ..lib.middleware.base import Widget

WidgetKeyErrorHandler = Callable[[str, KeyError], NoReturn]


def get_widget(
    wrapper: PdfWrapper,
    field: str,
    key_error_handler: WidgetKeyErrorHandler,
) -> Widget:
    """
    Look up a widget by field name.

    Args:
        wrapper (PdfWrapper): PDF wrapper containing form widgets.
        field (str): Form field name to look up.
        key_error_handler (WidgetKeyErrorHandler, optional): Interface-specific
            error handler for missing field names. Defaults to None.

    Returns:
        Widget: The matching widget.

    Raises:
        KeyError: Raised when the widget name is not present and no handler is
            supplied.
    """
    try:
        return wrapper.widgets[field]
    except KeyError as exc:
        key_error_handler(f"Form field '{field}' does not exist.", exc)
