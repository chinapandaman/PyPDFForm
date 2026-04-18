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

import json
from enum import Enum
from typing import Annotated

import typer

from .. import PdfWrapper
from .common import handle_font_registration

update_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


class DocumentEvent(str, Enum):
    """Document-level JavaScript events."""

    open = "open"


@update_cli.command(no_args_is_help=True)
def title(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
    new_title: Annotated[
        str, typer.Option("--title", "-t", help="The new title for the PDF file.")
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PDF. Defaults to the original path if not specified.",
        ),
    ] = None,
) -> None:
    """
    Update the title of a PDF file.
    """
    PdfWrapper(pdf, title=new_title, **ctx.obj).write(output or pdf)


@update_cli.command(no_args_is_help=True)
def coordinate(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
    widget: Annotated[
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
    f = obj.widgets[widget]

    f.x = x if x is not None else f.x
    f.y = y if y is not None else f.y
    f.width = width if width is not None else f.width
    f.height = height if height is not None else f.height

    obj.write(output or pdf)


@update_cli.command(no_args_is_help=True)
def field(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
    data: Annotated[
        str,
        typer.Option(
            "--file",
            "-f",
            help="Path to the JSON file containing the updated parameters.",
        ),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PDF. Defaults to the original path if not specified.",
        ),
    ] = None,
) -> None:
    """
    Modify PDF form field styles.
    """
    with open(data, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    obj = PdfWrapper(pdf, **ctx.obj)
    registered_font = {}
    for k, each in input_data.items():
        handle_font_registration(obj, each, registered_font)
        for param, v in each.items():
            setattr(obj.widgets[k], param, v)

    obj.write(output or pdf)


@update_cli.command(no_args_is_help=True)
def script(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
    js_script: Annotated[
        str,
        typer.Option(
            "--script",
            "-s",
            help="Path to a JavaScript file or the JavaScript string to execute.",
        ),
    ],
    event: Annotated[
        DocumentEvent,
        typer.Option(
            "--event",
            "-e",
            help="The document-level event to trigger the script.",
        ),
    ] = DocumentEvent.open,
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PDF. Defaults to the original path if not specified.",
        ),
    ] = None,
) -> None:
    """
    Embed a document-level JavaScript action.
    """
    obj = PdfWrapper(pdf, **ctx.obj)
    setattr(obj, f"on_{event.value}_javascript", js_script)
    obj.write(output or pdf)


@update_cli.command(no_args_is_help=True)
def version(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
    pdf_version: Annotated[
        str,
        typer.Option("--version", "-v", help="The new PDF version."),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PDF. Defaults to the original path if not specified.",
        ),
    ] = None,
) -> None:
    """
    Change the PDF version of the document.
    """
    PdfWrapper(pdf, **ctx.obj).change_version(pdf_version).write(output or pdf)
