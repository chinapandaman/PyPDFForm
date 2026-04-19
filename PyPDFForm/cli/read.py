# -*- coding: utf-8 -*-
"""
This module defines CLI commands for reading PDF form information.

It exposes the `read` command group, which prints JSON for form schemas,
current form values, generated sample data, and field rectangle metadata.
Each command wraps read-only `PdfWrapper` properties so users can inspect forms
from the terminal without writing Python code.
"""

import json
from typing import Annotated

import typer

from .. import PdfWrapper

read_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


@read_cli.command(no_args_is_help=True)
def schema(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
) -> None:
    """Retrieve a JSON schema that describes a PDF form."""
    print(json.dumps(PdfWrapper(pdf, **ctx.obj).schema))


@read_cli.command(no_args_is_help=True)
def data(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
) -> None:
    """Read the current filled data of a PDF form."""
    print(json.dumps(PdfWrapper(pdf, **ctx.obj).data))


@read_cli.command(no_args_is_help=True)
def sample(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
) -> None:
    """Generate sample data for filling a PDF form."""
    print(json.dumps(PdfWrapper(pdf, **ctx.obj).sample_data))


@read_cli.command(no_args_is_help=True)
def location(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
    field: Annotated[
        str, typer.Option("--field", "-f", help="Name of the form field to read.")
    ],
) -> None:
    """Retrieve a form field's page number, coordinates, and dimensions."""
    f = PdfWrapper(pdf, **ctx.obj).widgets[field]

    print(
        json.dumps(
            {
                "page_number": f.page_number,
                "x": f.x,
                "y": f.y,
                "width": f.width,
                "height": f.height,
            }
        )
    )
