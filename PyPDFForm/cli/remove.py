# -*- coding: utf-8 -*-
"""
This module defines CLI commands for removing PDF form content.

It exposes the `remove` command group for deleting existing form fields.
Commands in this module load the target PDF, validate requested form field
names, apply the matching `PdfWrapper` operation, and write the modified PDF to
either the requested output path or the original file.
"""

import typer

from .. import PdfWrapper
from ..lib.field_tree import get_field_keys
from .common import FIELD_NAMES, INPUT_PDF, OPTIONAL_OUTPUT_PDF, get_widget

remove_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


@remove_cli.command(
    no_args_is_help=True,
    help="Remove form fields from a PDF.",
)
def field(
    ctx: typer.Context,
    pdf: INPUT_PDF,
    fields: FIELD_NAMES,
    output: OPTIONAL_OUTPUT_PDF = None,
) -> None:
    """
    Remove one or more named form fields from an existing PDF.

    The command loads the PDF with the global CLI options stored in `ctx.obj`,
    validates that each requested name matches a form field, including fields
    without a widget on any page, before changing the document, removes the
    fields through `PdfWrapper.remove_fields`, which also updates the form
    actions that name them, and writes the modified PDF to the requested
    output path or back to the input file.

    Args:
        ctx (typer.Context): Typer context containing global `PdfWrapper`
            options in `ctx.obj`.
        pdf (Path): Input PDF path.
        fields (list[str]): Form field names to remove.
        output (Path, optional): Output PDF path. If omitted, the input PDF is
            overwritten. Defaults to None.

    Raises:
        typer.BadParameter: Raised when any requested field does not exist.
    """
    obj = PdfWrapper(str(pdf), **ctx.obj)
    missing = [field_name for field_name in fields if field_name not in obj.widgets]
    if missing:
        field_keys = get_field_keys(
            pdf.read_bytes(), getattr(obj, "use_full_widget_name")
        )
        for field_name in missing:
            if field_name not in field_keys:
                get_widget(obj, field_name, "--field")

    obj.remove_fields(fields).write(output or pdf)
