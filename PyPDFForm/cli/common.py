# -*- coding: utf-8 -*-
"""
This module provides shared helpers for PyPDFForm CLI commands.

It contains utilities for loading JSON command input, registering custom fonts
once per command invocation, and converting grouped JSON element definitions
into the objects expected by `PdfWrapper` methods.
"""

import json
from pathlib import Path
from typing import Annotated, NoReturn

import typer

from .. import PdfWrapper
from ..lib.middleware.base import Widget

INPUT_PDF = Annotated[
    Path,
    typer.Argument(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Input PDF path.",
    ),
]
REQUIRED_OUTPUT_PDF = Annotated[
    Path,
    typer.Option(
        "--output",
        "-o",
        file_okay=True,
        dir_okay=False,
        writable=True,
        resolve_path=True,
        help="Output PDF path.",
    ),
]
OPTIONAL_OUTPUT_PDF = Annotated[
    Path | None,
    typer.Option(
        "--output",
        "-o",
        file_okay=True,
        dir_okay=False,
        writable=True,
        resolve_path=True,
        help="Output PDF path. Overwrites the input when omitted.",
    ),
]
FIELD_NAME = Annotated[str, typer.Option("--field", help="Form field name.")]


def json_file_option(help_text: str):
    """
    Creates the common validated JSON file option.

    Args:
        help_text (str): Help text to display for the option.

    Returns:
        typer.Option: A configured `--file` / `-f` option for JSON file input.
    """
    return typer.Option(
        "--file",
        "-f",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help=help_text,
    )


def cli_bad_parameter(
    message: str,
    param_hint: str,
    cause: BaseException,
) -> NoReturn:
    """
    Raises a Typer input error with a stable CLI message.

    Args:
        message (str): Error message to display to the CLI user.
        param_hint (str): CLI parameter associated with the error.
        cause (BaseException): Original exception that caused the CLI error.

    Raises:
        typer.BadParameter: Raised with the provided message and parameter hint.
    """
    raise typer.BadParameter(message, param_hint=param_hint) from cause


def get_widget(obj: PdfWrapper, field: str, param_hint: str) -> Widget:
    """
    Look up a widget and report missing names as CLI input errors.

    Args:
        obj (PdfWrapper): PDF wrapper containing form widgets.
        field (str): Form field name to look up.
        param_hint (str): CLI parameter associated with the field name.

    Returns:
        Widget: The matching widget.

    Raises:
        typer.BadParameter: Raised when the widget name is not present.
    """
    try:
        return obj.widgets[field]
    except KeyError as exc:
        cli_bad_parameter(
            f"Form field '{field}' does not exist.",
            param_hint=param_hint,
            cause=exc,
        )


def handle_font_registration(
    obj: PdfWrapper, params: dict, registered_font: dict
) -> None:
    """
    Registers a custom font referenced by CLI input.

    CLI JSON files may provide a file path in a `font` parameter. This helper
    registers each unique font path on the supplied `PdfWrapper` once, assigns
    it a generated internal font name, and mutates `params["font"]` to that
    registered name so downstream field or element constructors can use it.

    Args:
        obj (PdfWrapper): The wrapper for the PDF currently being modified.
        params (dict): The element or widget parameters loaded from JSON. This
            dictionary is mutated when it contains a `font` key.
        registered_font (dict): Mapping of source font paths to generated
            `PdfWrapper` font names for the current command invocation.
    """
    if "font" in params:
        if params["font"] not in registered_font:
            font_name = f"new_font_{len(registered_font)}"
            obj.register_font(font_name, params["font"])
            registered_font[params["font"]] = font_name
        params["font"] = registered_font[params["font"]]


def create_elements_from_file(
    pdf: Path,
    data: Path,
    element_map: dict,
    method_name: str,
    ctx: typer.Context,
    output: Path | None = None,
) -> None:
    """
    Creates PDF elements from grouped JSON definitions.

    The input JSON is expected to group element definitions by type, such as
    `text`, `image`, or `highlight`. Each group key is resolved through
    `element_map`, each item is constructed after optional font registration,
    and the resulting objects are passed to `method_name` on `PdfWrapper`.
    The modified PDF is written to `output` or back to the input path.

    Args:
        pdf (Path): The path to the input PDF file.
        data (Path): The path to the JSON file containing grouped element
            definitions.
        element_map (dict): Mapping from JSON group names to element classes or
            callables used to construct each object.
        method_name (str): Name of the `PdfWrapper` method that accepts the
            constructed elements, such as `bulk_create_fields`, `draw`, or
            `annotate`.
        ctx (typer.Context): Typer context containing global wrapper options in
            `ctx.obj`.
        output (Path, optional): Path where the modified PDF should be saved. If
            omitted, the input PDF is overwritten. Defaults to None.
    """
    with open(data, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    obj = PdfWrapper(str(pdf), **ctx.obj)
    ungrouped_input = []
    registered_font = {}
    for k, v in input_data.items():
        for each in v:
            handle_font_registration(obj, each, registered_font)
            ungrouped_input.append(element_map[k](**each))

    getattr(obj, method_name)(ungrouped_input).write(output or pdf)
