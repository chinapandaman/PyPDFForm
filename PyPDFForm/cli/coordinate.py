# -*- coding: utf-8 -*-

from typing import Annotated

import typer

from .. import PdfWrapper

coordinate_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


@coordinate_cli.command(no_args_is_help=True)
def grid(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="The local path to a PDF.")],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="The location to save the PDF to. Defaults to the original path if unspecified.",
        ),
    ] = None,
    red: Annotated[
        float,
        typer.Option(
            "--red", "-r", help="Red channel of the RGB color of the grid view."
        ),
    ] = None,
    green: Annotated[
        float,
        typer.Option(
            "--green", "-g", help="Green channel of the RGB color of the grid view."
        ),
    ] = None,
    blue: Annotated[
        float,
        typer.Option(
            "--blue", "-b", help="Blue channel of the RGB color of the grid view."
        ),
    ] = None,
    margin: Annotated[
        float,
        typer.Option(
            "--margin",
            "-m",
            help="Margin of the grid view in points.",
        ),
    ] = None,
) -> None:
    """
    Generate a coordinate grid view for a PDF.
    """
    params = {}
    if any(
        [
            red is not None,
            green is not None,
            blue is not None,
        ]
    ):
        params["color"] = (red or 0, green or 0, blue or 0)

    if margin is not None:
        params["margin"] = int(margin) if margin.is_integer() else margin
    PdfWrapper(pdf, **ctx.obj).generate_coordinate_grid(**params).write(output or pdf)
