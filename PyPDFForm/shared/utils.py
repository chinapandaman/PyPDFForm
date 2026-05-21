# -*- coding: utf-8 -*-
"""
Shared helpers used by multiple PyPDFForm interfaces.

These utilities contain behavior that should stay consistent across the CLI,
web API, and any future user-facing entry points.
"""

import json
from collections.abc import Callable
from os import PathLike
from pathlib import Path
from typing import Any, NoReturn

from jsonschema import ValidationError, validate

from .. import PdfWrapper
from ..lib.middleware.base import Widget

WidgetKeyErrorHandler = Callable[[str, KeyError], NoReturn]
JsonErrorHandler = Callable[[str, BaseException], NoReturn]


def _validation_error_path(exc) -> str:
    """
    Builds a dotted JSON path for a validation error.

    Args:
        exc: The JSON schema validation error.

    Returns:
        str: Dotted path for the failing instance location.
    """
    return ".".join(str(each) for each in exc.absolute_path)


def _is_json_file(data: str | PathLike[str]) -> bool:
    """
    Determines whether JSON input should be loaded from disk.

    Args:
        data (str | PathLike[str]): Possible JSON input.

    Returns:
        bool: Whether the input points to a file.
    """
    if isinstance(data, PathLike):
        return True

    return Path(data).is_file()


def load_json(
    data: str | PathLike[str],
    schema: dict,
    json_error_handler: JsonErrorHandler,
) -> Any:
    """
    Loads JSON from a file path or JSON string and validates it against a schema.

    Args:
        data (str | PathLike[str]): JSON file path or stringified JSON.
        schema (dict): JSON schema to validate against.
        json_error_handler (JsonErrorHandler): Interface-specific error handler
            for parse, read, and validation failures.

    Returns:
        Any: Parsed and validated JSON input.
    """
    is_json_file = _is_json_file(data)
    source = "JSON file" if is_json_file else "JSON"
    try:
        if is_json_file:
            with open(data, "r", encoding="utf-8") as f:
                input_data = json.load(f)
        else:
            input_data = json.loads(data)
    except (OSError, TypeError, json.JSONDecodeError) as exc:
        json_error_handler(f"Invalid {source}: {exc}", exc)

    try:
        validate(instance=input_data, schema=schema)
    except ValidationError as exc:
        error_path = _validation_error_path(exc)
        location = f" at {error_path}" if error_path else ""
        json_error_handler(f"Invalid {source}{location}: {exc.message}", exc)

    return input_data


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
        return key_error_handler(f"Form field '{field}' does not exist.", exc)
