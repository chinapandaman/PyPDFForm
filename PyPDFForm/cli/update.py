# -*- coding: utf-8 -*-
"""
This module defines CLI commands for updating existing PDF files.

It exposes the `update` command group for metadata changes, PDF version
changes, field bounds edits, field renames, field property updates, and
document-level JavaScript actions. Commands in this module load command-line or
JSON input, apply the matching `PdfWrapper` operation, and write the modified
PDF to either the requested output path or the original file.
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
    """
    Document-level JavaScript events supported by the CLI.

    This enum constrains the `update script --event` option to events that can
    be mapped to `PdfWrapper` JavaScript attributes.

    Attributes:
        open (str): Run the script when the PDF document is opened.
    """

    open = "open"


@update_cli.command(no_args_is_help=True)
def title(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Input PDF path.")],
    new_title: Annotated[str, typer.Option("--title", "-t", help="New PDF title.")],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output PDF path. Overwrites the input when omitted.",
        ),
    ] = None,
) -> None:
    """Set the PDF title."""
    PdfWrapper(pdf, title=new_title, **ctx.obj).write(output or pdf)


@update_cli.command(no_args_is_help=True)
def version(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Input PDF path.")],
    pdf_version: Annotated[
        str,
        typer.Option("--version", "-v", help="New PDF version."),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output PDF path. Overwrites the input when omitted.",
        ),
    ] = None,
) -> None:
    """Set the PDF version."""
    PdfWrapper(pdf, **ctx.obj).change_version(pdf_version).write(output or pdf)


@update_cli.command(no_args_is_help=True)
def bounds(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Input PDF path.")],
    widget: Annotated[str, typer.Option("--field", help="Form field name.")],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output PDF path. Overwrites the input when omitted.",
        ),
    ] = None,
    x: Annotated[
        float,
        typer.Option(
            "--x",
            help="New x-coordinate in points.",
        ),
    ] = None,
    y: Annotated[
        float,
        typer.Option(
            "--y",
            help="New y-coordinate in points.",
        ),
    ] = None,
    width: Annotated[
        float,
        typer.Option(
            "--width",
            help="New field width in points.",
        ),
    ] = None,
    height: Annotated[
        float,
        typer.Option(
            "--height",
            help="New field height in points.",
        ),
    ] = None,
) -> None:
    """Update a form field's position and size."""
    obj = PdfWrapper(pdf, **ctx.obj)
    f = obj.widgets[widget]

    f.x = x if x is not None else f.x
    f.y = y if y is not None else f.y
    f.width = width if width is not None else f.width
    f.height = height if height is not None else f.height

    obj.write(output or pdf)


@update_cli.command(no_args_is_help=True)
def rename(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Input PDF path.")],
    data: Annotated[
        str,
        typer.Option(
            "--file",
            "-f",
            help="JSON file with form field renames.",
        ),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output PDF path. Overwrites the input when omitted.",
        ),
    ] = None,
) -> None:
    """Rename form fields from JSON."""
    with open(data, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    obj = PdfWrapper(pdf, **ctx.obj)
    for item in input_data:
        for k, v in item.items():
            obj.update_widget_key(k, v["new_key"], index=v.get("index", 0), defer=True)

    obj.commit_widget_key_updates().write(output or pdf)


@update_cli.command(no_args_is_help=True)
def field(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Input PDF path.")],
    data: Annotated[
        str,
        typer.Option(
            "--file",
            "-f",
            help="JSON file with form field property updates.",
        ),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output PDF path. Overwrites the input when omitted.",
        ),
    ] = None,
) -> None:
    """Update form field properties from JSON."""
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
    pdf: Annotated[str, typer.Argument(help="Input PDF path.")],
    js_script: Annotated[
        str,
        typer.Option(
            "--script",
            "-s",
            help="JavaScript file path or inline JavaScript.",
        ),
    ],
    event: Annotated[
        DocumentEvent,
        typer.Option(
            "--event",
            "-e",
            help="Document event that runs the script.",
        ),
    ] = DocumentEvent.open,
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output PDF path. Overwrites the input when omitted.",
        ),
    ] = None,
) -> None:
    """Add a document-level JavaScript action."""
    obj = PdfWrapper(pdf, **ctx.obj)
    setattr(obj, f"on_{event.value}_javascript", js_script)
    obj.write(output or pdf)
