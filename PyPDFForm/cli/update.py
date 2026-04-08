# -*- coding: utf-8 -*-

from typing import Annotated

import typer

from .. import PdfWrapper

update_cli = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True
)


@update_cli.command(no_args_is_help=True)
def title(
    pdf: Annotated[str, typer.Argument(help="The local path to a PDF.")],
    title: Annotated[
        str, typer.Option("--title", "-t", help="The title to change to for the PDF.")
    ],
    output: Annotated[
        str, typer.Option("--output", "-o", help="The location to save the PDF to.")
    ] = None,
):
    """
    Update the title of a PDF.
    """
    PdfWrapper(pdf, title=title).write(output or pdf)
