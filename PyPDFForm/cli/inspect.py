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


@inspect_cli.command(no_args_is_help=True)
def schema(
    ctx: typer.Context,
    pdf: INPUT_PDF,
) -> None:
    """Print the form schema as JSON."""
    typer.echo(json.dumps(PdfWrapper(str(pdf), **ctx.obj).schema))


@inspect_cli.command(no_args_is_help=True)
def data(
    ctx: typer.Context,
    pdf: INPUT_PDF,
) -> None:
    """Print current form data as JSON."""
    typer.echo(json.dumps(PdfWrapper(str(pdf), **ctx.obj).data))


@inspect_cli.command(no_args_is_help=True)
def sample(
    ctx: typer.Context,
    pdf: INPUT_PDF,
) -> None:
    """Print sample fill data as JSON."""
    typer.echo(json.dumps(PdfWrapper(str(pdf), **ctx.obj).sample_data))


@inspect_cli.command(no_args_is_help=True)
def location(
    ctx: typer.Context,
    pdf: INPUT_PDF,
    field: FIELD_NAME,
) -> None:
    """Print a form field's location and size as JSON."""
    f = get_widget(PdfWrapper(str(pdf), **ctx.obj), field)

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
