# -*- coding: utf-8 -*-
"""
CLI commands for updating PDFs.

This module provides command-line interface commands for modifying
PDF files, such as updating metadata or other elements.
These commands allow users to update PDF documents directly from
the terminal without needing to write Python code.

The commands in this module wrap the functionality provided by
the PdfWrapper class, exposing it through a Typer-based CLI for
ease of use.
"""

from typing import Annotated

import typer

from .. import PdfWrapper

update_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


@update_cli.command(no_args_is_help=True)
def title(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="The local path to a PDF file.")],
    new_title: Annotated[
        str, typer.Option("--title", "-t", help="The new title for the PDF file.")
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="The location to save the output PDF to. Defaults to the original path if not specified.",
        ),
    ] = None,
) -> None:
    """
    Update the title of a PDF file.
    """
    PdfWrapper(pdf, title=new_title, **ctx.obj).write(output or pdf)
