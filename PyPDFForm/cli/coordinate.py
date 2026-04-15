# -*- coding: utf-8 -*-
"""
CLI commands for interacting with PDF coordinates.

This module provides command-line interface commands for working with
PDF coordinates and dimensions, such as generating a coordinate grid view.
"""

from typing import Annotated

import typer

from .. import PdfWrapper

coordinate_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


@coordinate_cli.command(no_args_is_help=True)
def modify(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
    field: Annotated[
        str, typer.Option("--field", "-f", help="Name of the form field to modify.")
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PDF. Defaults to the original path if not specified.",
        ),
    ] = None,
    x: Annotated[
        float,
        typer.Option(
            "--x",
            help="New x coordinate.",
        ),
    ] = None,
    y: Annotated[
        float,
        typer.Option(
            "--y",
            help="New y coordinate.",
        ),
    ] = None,
    width: Annotated[
        float,
        typer.Option(
            "--width",
            help="New width.",
        ),
    ] = None,
    height: Annotated[
        float,
        typer.Option(
            "--height",
            help="New height.",
        ),
    ] = None,
) -> None:
    """
    Modify the coordinates and dimensions of a form field's rectangular bounding box.
    """
    obj = PdfWrapper(pdf, **ctx.obj)
    f = obj.widgets[field]

    f.x = x if x is not None else f.x
    f.y = y if y is not None else f.y
    f.width = width if width is not None else f.width
    f.height = height if height is not None else f.height

    obj.write(output or pdf)
