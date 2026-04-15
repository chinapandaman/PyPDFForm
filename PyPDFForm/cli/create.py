# -*- coding: utf-8 -*-
"""
CLI module for creating PDF form fields.

This module provides command-line interfaces to create various types of PDF form fields
(such as text fields, checkboxes, radio buttons, dropdowns, signatures, and images)
in an existing PDF. It aims to mimic the field creation features available via the
Python API as described in the preparation documentation.
"""

import json
from typing import Annotated

import typer

from .. import BlankPage, Fields, PdfWrapper, RawElements

create_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


def _create_elements_from_file(
    pdf: str,
    data: str,
    element_map: dict,
    method_name: str,
    ctx: typer.Context,
    output: str = None,
) -> None:
    """
    Create PDF elements from a JSON file.

    Args:
        pdf: Path to the input PDF file.
        data: Path to the JSON file containing element parameters.
        element_map: Mapping of element type names to element classes.
        method_name: Name of the method to call on PdfWrapper (e.g., "bulk_create_fields", "draw").
        ctx: Typer context containing configuration options.
        output: Path to save the output PDF. Defaults to the original path if not specified.
    """
    with open(data, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    obj = PdfWrapper(pdf, **ctx.obj)
    ungrouped_input = []
    registered_font = {}
    for k, v in input_data.items():
        for each in v:
            if "font" in each:
                if each["font"] not in registered_font:
                    font_name = f"new_font_{len(registered_font)}"
                    obj.register_font(font_name, each["font"])
                    registered_font[each["font"]] = font_name
                each["font"] = registered_font[each["font"]]
            ungrouped_input.append(element_map[k](**each))

    getattr(obj, method_name)(ungrouped_input).write(output or pdf)


@create_cli.command(no_args_is_help=True)
def field(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
    data: Annotated[
        str,
        typer.Option(
            "--file",
            "-f",
            help="Path to the JSON file representing the field creation parameters.",
        ),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PDF. Defaults to the original path if not specified.",
        ),
    ] = None,
) -> None:
    """
    Create PDF form fields.
    """
    field_map = {
        "text": Fields.TextField,
        "check": Fields.CheckBoxField,
        "radio": Fields.RadioGroup,
        "dropdown": Fields.DropdownField,
        "image": Fields.ImageField,
        "signature": Fields.SignatureField,
    }
    _create_elements_from_file(pdf, data, field_map, "bulk_create_fields", ctx, output)


@create_cli.command(no_args_is_help=True)
def raw(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
    data: Annotated[
        str,
        typer.Option(
            "--file",
            "-f",
            help="Path to the JSON file representing the draw parameters.",
        ),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PDF. Defaults to the original path if not specified.",
        ),
    ] = None,
) -> None:
    """
    Draw raw PDF elements.
    """
    raw_element_map = {
        "text": RawElements.RawText,
        "image": RawElements.RawImage,
        "line": RawElements.RawLine,
        "rectangle": RawElements.RawRectangle,
        "circle": RawElements.RawCircle,
        "ellipse": RawElements.RawEllipse,
    }
    _create_elements_from_file(pdf, data, raw_element_map, "draw", ctx, output)


@create_cli.command(no_args_is_help=True)
def blank(
    ctx: typer.Context,
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PDF.",
        ),
    ],
    count: Annotated[
        int, typer.Option("--count", "-c", help="Number of blank pages.")
    ] = None,
    width: Annotated[
        float,
        typer.Option(
            "--width",
            help="Width of the blank PDF.",
        ),
    ] = None,
    height: Annotated[
        float, typer.Option("--height", help="Height of the blank PDF.")
    ] = None,
) -> None:
    """
    Create a new blank PDF.
    """
    params = {}
    if width is not None:
        params["width"] = width
    if height is not None:
        params["height"] = height

    obj = BlankPage(**params)
    if count is not None and count > 1:
        obj = BlankPage(**params) * count

    PdfWrapper(obj, **ctx.obj).write(output)
