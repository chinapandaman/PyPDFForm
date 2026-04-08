# -*- coding: utf-8 -*-
# TODO: fix this docstring
"""
CLI commands for updating PDF metadata.

This module provides command-line interface commands for modifying
PDF file metadata such as title, author, subject, and other properties.
These commands allow users to update PDF documents directly from
the terminal without needing to use Python code.

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
    pdf: Annotated[str, typer.Argument(help="The local path to a PDF.")],
    new_title: Annotated[
        str, typer.Option("--title", "-t", help="The new title for the PDF.")
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="The location to save the PDF to. Defaults to the original path if unspecified.",
        ),
    ] = None,
):
    """
    Update the title of a PDF.
    """
    PdfWrapper(pdf, title=new_title).write(output or pdf)
