# -*- coding: utf-8 -*-
"""
This module defines the root command-line interface for PyPDFForm.

It creates the Typer application, attaches the `create`, `inspect`, and `update`
command groups, and exposes top-level options shared by those commands. The
callbacks in this module collect global flags in the Typer context so each
subcommand can initialize `PdfWrapper` with consistent settings.

Commands:
    - `fill`: Fill an existing PDF form from JSON data.
    - `create`: Create PDFs, fields, annotations, raw elements, and grid views.
    - `inspect`: Print form metadata and field data as JSON.
    - `update`: Modify PDF metadata, field names, properties, geometry, and scripts.
"""

import json
from pathlib import Path
from typing import Annotated

import typer

from .. import PdfWrapper, Widgets, __version__
from .create import create_cli
from .inspect import inspect_cli
from .update import update_cli

cli_app = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)
cli_app.add_typer(
    create_cli,
    name="create",
    help="Create PDFs and PDF elements.",
)
cli_app.add_typer(
    inspect_cli,
    name="inspect",
    help="Inspect PDF form information.",
)
cli_app.add_typer(
    update_cli,
    name="update",
    help="Update PDF metadata, fields, and scripts.",
)


def version_callback(value: bool) -> None:
    """
    Handles the global version option.

    This callback is invoked eagerly by Typer when `--version` or `-v` is
    passed. When the option is enabled, it prints the current PyPDFForm version
    and exits before command parsing continues.

    Args:
        value (bool): Whether the version flag was supplied.

    Raises:
        typer.Exit: Raised after printing the version so the CLI exits without
            running another command.
    """
    if value:
        print(f"v{__version__}")
        raise typer.Exit


def need_appearances_callback(ctx: typer.Context, value: bool) -> None:
    """
    Stores the global `NeedAppearances` setting in the Typer context.

    Subcommands read this value from `ctx.obj` and pass it to `PdfWrapper`.
    When enabled, output PDFs ask compatible PDF viewers to synthesize widget
    appearances for form fields.

    Args:
        ctx (typer.Context): The Typer context used to share global options
            with subcommands.
        value (bool): Whether `NeedAppearances` should be enabled for output
            PDFs.
    """
    if not ctx.obj:
        ctx.obj = {}
    ctx.obj["need_appearances"] = value


def generate_appearance_streams_callback(ctx: typer.Context, value: bool) -> None:
    """
    Stores the global appearance stream generation setting.

    Subcommands pass this option to `PdfWrapper` so filled or modified PDFs can
    explicitly regenerate appearance streams for form fields instead of relying
    only on viewer behavior.

    Args:
        ctx (typer.Context): The Typer context used to share global options
            with subcommands.
        value (bool): Whether form field appearance streams should be generated
            for output PDFs.
    """
    if not ctx.obj:
        ctx.obj = {}
    ctx.obj["generate_appearance_streams"] = value


def preserve_metadata_callback(ctx: typer.Context, value: bool) -> None:
    """
    Stores the global metadata preservation setting.

    Subcommands pass this value to `PdfWrapper` so output PDFs can preserve the
    source document metadata when the library writes the modified file.

    Args:
        ctx (typer.Context): The Typer context used to share global options
            with subcommands.
        value (bool): Whether output PDFs should preserve input PDF metadata.
    """
    if not ctx.obj:
        ctx.obj = {}
    ctx.obj["preserve_metadata"] = value


def use_full_widget_name_callback(ctx: typer.Context, value: bool) -> None:
    """
    Stores the global form field name lookup setting.

    Subcommands pass this setting to `PdfWrapper` so form fields can be looked
    up by their fully qualified widget names instead of short names.

    Args:
        ctx (typer.Context): The Typer context used to share global options
            with subcommands.
        value (bool): Whether fully qualified widget names should be used.
    """
    if not ctx.obj:
        ctx.obj = {}
    ctx.obj["use_full_widget_name"] = value


@cli_app.callback(
    invoke_without_command=True,
    help="Create, fill, inspect, and update PDF forms.",
)
def main(
    version: Annotated[  # pylint: disable=W0613
        bool,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show the PyPDFForm version and exit.",
        ),
    ] = False,
    need_appearances: Annotated[  # pylint: disable=W0613
        bool,
        typer.Option(
            "--need-appearances",
            callback=need_appearances_callback,
            help="Ask PDF viewers to render form field appearances.",
        ),
    ] = False,
    generate_appearance_streams: Annotated[  # pylint: disable=W0613
        bool,
        typer.Option(
            "--generate-appearance-streams",
            callback=generate_appearance_streams_callback,
            help="Generate form field appearance streams.",
        ),
    ] = False,
    preserve_metadata: Annotated[  # pylint: disable=W0613
        bool,
        typer.Option(
            "--preserve-metadata",
            callback=preserve_metadata_callback,
            help="Preserve input PDF metadata.",
        ),
    ] = False,
    use_full_widget_name: Annotated[  # pylint: disable=W0613
        bool,
        typer.Option(
            "--use-full-widget-name",
            callback=use_full_widget_name_callback,
            help="Use full form field names for lookup.",
        ),
    ] = False,
) -> None:
    """Create, fill, inspect, and update PDF forms."""


@cli_app.command(no_args_is_help=True)
def fill(
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
    data: Annotated[
        Path,
        typer.Option(
            "--file",
            "-f",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="JSON file with form field values.",
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            file_okay=True,
            dir_okay=False,
            writable=True,
            resolve_path=True,
            help="Output PDF path. Overwrites the input when omitted.",
        ),
    ] = None,
    flatten: Annotated[
        bool,
        typer.Option("--flatten", help="Flatten form fields after filling."),
    ] = None,
) -> None:
    """Fill a PDF form with JSON data."""
    with open(data, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    obj = PdfWrapper(str(pdf), **ctx.obj)
    for k, each in obj.widgets.items():
        if k in input_data and isinstance(each, (Widgets.Image, Widgets.Signature)):
            each.preserve_aspect_ratio = input_data.get(k, {}).get(
                "preserve_aspect_ratio", each.preserve_aspect_ratio
            )
            input_data[k] = input_data[k]["path"]

    obj.fill(input_data, flatten=flatten).write(output or pdf)


__all__ = ["cli_app"]
