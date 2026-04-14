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

from .. import Fields, PdfWrapper, RawElements

create_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


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

    with open(data, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    obj = PdfWrapper(pdf, **ctx.obj)
    font_tracker = 0
    ungrouped_input = []
    for k, v in input_data.items():
        for each in v:
            if "font" in each:
                obj.register_font(f"new_font_{font_tracker}", each["font"])
                each["font"] = f"new_font_{font_tracker}"
                font_tracker += 1
            ungrouped_input.append(field_map[k](**each))

    obj.bulk_create_fields(ungrouped_input).write(output or pdf)


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

    with open(data, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    ungrouped_input = []
    for k, v in input_data.items():
        # TODO: figure out what to do for fonts
        ungrouped_input.extend([raw_element_map[k](**each) for each in v])

    PdfWrapper(pdf, **ctx.obj).draw(ungrouped_input).write(output or pdf)
