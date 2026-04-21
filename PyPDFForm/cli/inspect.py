# -*- coding: utf-8 -*-
"""
This module defines CLI commands for inspecting PDF form information.

It exposes the `inspect` command group, which prints JSON for form schemas,
current form values, generated sample data, and field rectangle metadata.
Each command wraps read-only `PdfWrapper` properties so users can inspect forms
from the terminal without writing Python code.
"""

import json
from pathlib import Path
from typing import Annotated

import typer

from .. import PdfWrapper

inspect_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


@inspect_cli.command(no_args_is_help=True)
def schema(
    ctx: typer.Context,
    pdf: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Input PDF path.",
        ),
    ],
) -> None:
    """Print the form schema as JSON."""
    print(json.dumps(PdfWrapper(str(pdf), **ctx.obj).schema))


@inspect_cli.command(no_args_is_help=True)
def data(
    ctx: typer.Context,
    pdf: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Input PDF path.",
        ),
    ],
) -> None:
    """Print current form data as JSON."""
    print(json.dumps(PdfWrapper(str(pdf), **ctx.obj).data))


@inspect_cli.command(no_args_is_help=True)
def sample(
    ctx: typer.Context,
    pdf: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Input PDF path.",
        ),
    ],
) -> None:
    """Print sample fill data as JSON."""
    print(json.dumps(PdfWrapper(str(pdf), **ctx.obj).sample_data))


@inspect_cli.command(no_args_is_help=True)
def location(
    ctx: typer.Context,
    pdf: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Input PDF path.",
        ),
    ],
    field: Annotated[str, typer.Option("--field", help="Form field name.")],
) -> None:
    """Print a form field's location and size as JSON."""
    f = PdfWrapper(str(pdf), **ctx.obj).widgets[field]

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
