# -*- coding: utf-8 -*-
"""
This module defines CLI commands for removing PDF form content.

It exposes the `remove` command group for deleting existing form fields.
Commands in this module load the target PDF, validate requested form field
names, apply the matching `PdfWrapper` operation, and write the modified PDF to
either the requested output path or the original file.
"""

from typing import Annotated

import typer

from .. import PdfWrapper
from .common import INPUT_PDF, OPTIONAL_OUTPUT_PDF, get_widget

remove_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


@remove_cli.command(no_args_is_help=True)
def field(
    ctx: typer.Context,
    pdf: INPUT_PDF,
    keys: Annotated[
        list[str],
        typer.Option(
            "--key",
            "-k",
            help="Form field key to remove. Repeat this option to remove multiple fields.",
        ),
    ],
    output: OPTIONAL_OUTPUT_PDF = None,
) -> None:
    """Remove form fields from a PDF."""
    obj = PdfWrapper(str(pdf), **ctx.obj)
    for key in keys:
        get_widget(obj, key, "--key")

    obj.remove_fields(keys).write(output or pdf)
