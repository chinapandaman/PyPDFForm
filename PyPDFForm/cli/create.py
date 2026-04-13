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

from .. import Fields, PdfWrapper

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
):
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

    with open(data, "r") as f:
        input_data = json.load(f)

    ungrouped_input = []
    for k, v in input_data.items():
        for each in v:
            ungrouped_input.append(field_map[k](**each))

    PdfWrapper(pdf, **ctx.obj).bulk_create_fields(ungrouped_input).write(output or pdf)
