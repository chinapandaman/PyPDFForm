# -*- coding: utf-8 -*-
"""
This module defines CLI commands for inspecting PDF form information.

It exposes the `inspect` command group, which prints JSON for form schemas,
current form values, generated sample data, and field rectangle metadata.
Each command wraps read-only `PdfWrapper` properties so users can inspect forms
from the terminal without writing Python code.
"""

import json

import typer

from .. import PdfWrapper
from .common import FIELD_NAME, INPUT_PDF, get_widget

inspect_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


@inspect_cli.command(
    no_args_is_help=True,
    help="Print the form schema as JSON.",
)
def schema(
    ctx: typer.Context,
    pdf: INPUT_PDF,
) -> None:
    """
    Print the JSON schema for filling an existing PDF form.

    The command loads the PDF with the global CLI options stored in `ctx.obj`,
    reads `PdfWrapper.schema`, serializes it as JSON, and writes it to standard
    output.

    Args:
        ctx (typer.Context): Typer context containing global `PdfWrapper`
            options in `ctx.obj`.
        pdf (Path): Input PDF path.
    """
    typer.echo(json.dumps(PdfWrapper(str(pdf), **ctx.obj).schema))


@inspect_cli.command(
    no_args_is_help=True,
    help="Print current form data as JSON.",
)
def data(
    ctx: typer.Context,
    pdf: INPUT_PDF,
) -> None:
    """
    Print the current field values from an existing PDF form.

    The command loads the PDF with the global CLI options stored in `ctx.obj`,
    reads `PdfWrapper.data`, serializes it as JSON, and writes it to standard
    output.

    Args:
        ctx (typer.Context): Typer context containing global `PdfWrapper`
            options in `ctx.obj`.
        pdf (Path): Input PDF path.
    """
    typer.echo(json.dumps(PdfWrapper(str(pdf), **ctx.obj).data))


@inspect_cli.command(
    no_args_is_help=True,
    help="Print sample fill data as JSON.",
)
def sample(
    ctx: typer.Context,
    pdf: INPUT_PDF,
) -> None:
    """
    Print generated sample data for filling an existing PDF form.

    The command loads the PDF with the global CLI options stored in `ctx.obj`,
    reads `PdfWrapper.sample_data`, serializes it as JSON, and writes it to
    standard output.

    Args:
        ctx (typer.Context): Typer context containing global `PdfWrapper`
            options in `ctx.obj`.
        pdf (Path): Input PDF path.
    """
    typer.echo(json.dumps(PdfWrapper(str(pdf), **ctx.obj).sample_data))


@inspect_cli.command(
    no_args_is_help=True,
    help="Print a form field's location and size as JSON.",
)
def location(
    ctx: typer.Context,
    pdf: INPUT_PDF,
    field: FIELD_NAME,
) -> None:
    """
    Print geometry metadata for a single form field.

    The command loads the PDF with the global CLI options stored in `ctx.obj`,
    resolves the requested widget name, and prints a JSON object containing the
    page number, x-coordinate, y-coordinate, width, and height.

    Args:
        ctx (typer.Context): Typer context containing global `PdfWrapper`
            options in `ctx.obj`.
        pdf (Path): Input PDF path.
        field (str): Form field name to inspect.

    Raises:
        typer.BadParameter: Raised when the requested field does not exist.
    """
    f = get_widget(PdfWrapper(str(pdf), **ctx.obj), field, "--field")

    typer.echo(
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
