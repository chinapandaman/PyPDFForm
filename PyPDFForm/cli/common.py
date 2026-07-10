# -*- coding: utf-8 -*-
"""
This module provides shared helpers for PyPDFForm CLI commands.

It contains utilities for loading structured command input, registering custom
fonts once per command invocation, and converting grouped element definitions
into the objects expected by `PdfWrapper` methods.
"""

import json
from pathlib import Path
from typing import Annotated, Any, NoReturn

import typer
import yaml
from jsonschema import ValidationError, validate

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
FIELD_NAMES = Annotated[
    list[str],
    typer.Option(
        "--field",
        help="Form field name. Repeat this option to select multiple fields.",
    ),
]


def data_file_option(help_text: str):
    """
    Creates the common validated structured data file option.

    Args:
        help_text (str): Help text to display for the option.

    Returns:
        typer.Option: A configured `--file` / `-f` option for file input.
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
    cause: BaseException | None = None,
) -> NoReturn:
    """
    Raises a Typer input error with a stable CLI message.

    Args:
        message (str): Error message to display to the CLI user.
        param_hint (str): CLI parameter associated with the error.
        cause (BaseException, optional): Original exception that caused the CLI
            error. Defaults to None.

    Raises:
        typer.BadParameter: Raised with the provided message and parameter hint.
    """
    if cause is None:
        raise typer.BadParameter(message, param_hint=param_hint)

    raise typer.BadParameter(message, param_hint=param_hint) from cause


def _validation_error_path(exc: ValidationError) -> str:
    """
    Builds a dotted input data path for a validation error.

    Args:
        exc (ValidationError): The JSON schema validation error.

    Returns:
        str: Dotted path for the failing instance location.
    """
    return ".".join(str(each) for each in exc.absolute_path)


def _input_file_kind(data: Path) -> str:
    """
    Gets the structured data format to use for a CLI input file.

    Args:
        data (Path): Input file path.

    Returns:
        str: The upper-case format name for user-facing messages.
    """
    if data.suffix.lower() in {".yaml", ".yml"}:
        return "YAML"

    return "JSON"


def _validate_input_data(
    input_data: Any,
    schema: dict,
    source: str,
    param_hint: str,
) -> Any:
    """
    Validates parsed CLI input against a JSON schema.

    Args:
        input_data (Any): Parsed input data to validate.
        schema (dict): JSON schema to validate against.
        source (str): User-facing description of the input source.
        param_hint (str): CLI parameter associated with the input.

    Returns:
        Any: The validated input data.

    Raises:
        typer.BadParameter: Raised when validation fails.
    """
    try:
        validate(instance=input_data, schema=schema)
    except ValidationError as exc:
        error_path = _validation_error_path(exc)
        location = f" at {error_path}" if error_path else ""
        cli_bad_parameter(
            f"Invalid {source}{location}: {exc.message}",
            param_hint=param_hint,
            cause=exc,
        )

    return input_data


def load_data_file(data: Path, schema: dict, param_hint: str) -> Any:
    """
    Loads a YAML or JSON CLI input file and validates it against a schema.

    Args:
        data (Path): YAML or JSON file path.
        schema (dict): JSON schema to validate against.
        param_hint (str): CLI parameter associated with the input file.

    Returns:
        Any: Parsed and validated input data.

    Raises:
        typer.BadParameter: Raised when the file cannot be loaded or validation
            fails.
    """
    input_kind = _input_file_kind(data)
    try:
        with open(data, "r", encoding="utf-8") as f:
            input_data = yaml.safe_load(f) if input_kind == "YAML" else json.load(f)
    except (OSError, json.JSONDecodeError, yaml.YAMLError) as exc:
        cli_bad_parameter(
            f"Invalid {input_kind} file: {exc}",
            param_hint=param_hint,
            cause=exc,
        )

    return _validate_input_data(
        input_data,
        schema,
        f"{input_kind} file",
        param_hint,
    )


def load_data_options(options: list[str], schema: dict) -> Any:
    """
    Loads dynamic form field options and validates them against a schema.

    Dynamic options use ``--name value`` syntax. Each value is parsed with
    :func:`yaml.safe_load`.

    Args:
        options (list[str]): Unrecognized command arguments captured by Typer.
        schema (dict): JSON schema to validate the resulting field mapping
            against.

    Returns:
        Any: Parsed and validated field data.

    Raises:
        typer.BadParameter: Raised when the options cannot be parsed or the
            resulting mapping fails validation.
    """
    try:
        input_data = {
            option[2:]: yaml.safe_load(value)
            for option, value in zip(options[::2], options[1::2], strict=True)
        }
    except (ValueError, yaml.YAMLError) as exc:
        cli_bad_parameter(
            "Use '--name value' pairs with valid values.",
            param_hint="form field options",
            cause=exc,
        )

    return _validate_input_data(input_data, schema, "CLI options", "form field options")


def get_widget(wrapper: PdfWrapper, field: str, param_hint: str) -> Widget:
    """
    Look up a widget and report missing names as CLI input errors.

    Args:
        wrapper (PdfWrapper): PDF wrapper containing form widgets.
        field (str): Form field name to look up.
        param_hint (str): CLI parameter associated with the field name.

    Returns:
        Widget: The matching widget.

    Raises:
        typer.BadParameter: Raised when the widget name is not present.
    """
    try:
        return wrapper.widgets[field]
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

    CLI input files may provide a file path in a `font` parameter. This helper
    registers each unique font path on the supplied `PdfWrapper` once, assigns
    it a generated internal font name, and mutates `params["font"]` to that
    registered name so downstream field or element constructors can use it.

    Args:
        obj (PdfWrapper): The wrapper for the PDF currently being modified.
        params (dict): The element or widget parameters loaded from the input
            file. This dictionary is mutated when it contains a `font` key.
        registered_font (dict): Mapping of resolved source font paths to
            generated `PdfWrapper` font names for the current command
            invocation.
    """
    if "font" in params:
        font_path = str(Path(params["font"]).resolve())
        if font_path not in registered_font:
            font_name = f"new_font_{len(registered_font)}"
            obj.register_font(font_name, font_path)
            registered_font[font_path] = font_name
        params["font"] = registered_font[font_path]


def create_elements_from_file(
    pdf: Path,
    data: Path,
    element_map: dict,
    schema: dict,
    method_name: str,
    ctx: typer.Context,
    param_hint: str,
    output: Path | None = None,
) -> None:
    """
    Creates PDF elements from grouped file definitions.

    The input data is expected to group element definitions by type, such as
    `text`, `image`, or `highlight`. Each group key is resolved through
    `element_map`, each item is constructed after optional font registration,
    and the resulting objects are passed to `method_name` on `PdfWrapper`.
    The modified PDF is written to `output` or back to the input path.

    Args:
        pdf (Path): The path to the input PDF file.
        data (Path): The path to the input file containing grouped element
            definitions.
        element_map (dict): Mapping from input group names to element classes
            or callables used to construct each object.
        schema (dict): JSON schema used to validate the grouped definitions.
        method_name (str): Name of the `PdfWrapper` method that accepts the
            constructed elements, such as `bulk_create_fields`, `draw`, or
            `annotate`.
        ctx (typer.Context): Typer context containing global wrapper options in
            `ctx.obj`.
        param_hint (str): CLI parameter associated with the input file.
        output (Path, optional): Path where the modified PDF should be saved. If
            omitted, the input PDF is overwritten. Defaults to None.
    """
    input_data = load_data_file(data, schema, param_hint)

    obj = PdfWrapper(str(pdf), **ctx.obj)
    ungrouped_input = []
    registered_font = {}
    for k, v in input_data.items():
        for each in v:
            handle_font_registration(obj, each, registered_font)
            ungrouped_input.append(element_map[k](**each))

    getattr(obj, method_name)(ungrouped_input).write(output or pdf)
