# -*- coding: utf-8 -*-
"""
This module defines the root command-line interface for PyPDFForm.

It creates the Typer application, attaches the `create`, `inspect`, and `update`
command groups, and exposes top-level options shared by those commands. The root
callback collects global flags in the Typer context so each subcommand can
initialize `PdfWrapper` with consistent settings.

Commands:
    - `fill`: Fill an existing PDF form from JSON data.
    - `create`: Create PDFs, fields, annotations, raw elements, and grid views.
    - `inspect`: Print form metadata and field data as JSON.
    - `update`: Modify PDF metadata, field names, properties, geometry, and scripts.
"""

from pathlib import Path
from typing import Annotated

import typer

from .. import PdfWrapper, Widgets, __version__
from .common import (INPUT_PDF, OPTIONAL_OUTPUT_PDF, json_file_option,
                     load_json_file)
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
        typer.echo(f"v{__version__}")
        raise typer.Exit


@cli_app.callback(
    invoke_without_command=True,
    help="Create, fill, inspect, and update PDF forms.",
)
def main(
    ctx: typer.Context,
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
    need_appearances: Annotated[
        bool,
        typer.Option(
            "--need-appearances",
            help="Ask PDF viewers to render form field appearances.",
        ),
    ] = False,
    generate_appearance_streams: Annotated[
        bool,
        typer.Option(
            "--generate-appearance-streams",
            help="Generate form field appearance streams.",
        ),
    ] = False,
    preserve_metadata: Annotated[
        bool,
        typer.Option(
            "--preserve-metadata",
            help="Preserve input PDF metadata.",
        ),
    ] = False,
    use_full_widget_name: Annotated[
        bool,
        typer.Option(
            "--use-full-widget-name",
            help="Use full form field names for lookup.",
        ),
    ] = False,
) -> None:
    """Create, fill, inspect, and update PDF forms."""
    ctx.obj = {
        "need_appearances": need_appearances,
        "generate_appearance_streams": generate_appearance_streams,
        "preserve_metadata": preserve_metadata,
        "use_full_widget_name": use_full_widget_name,
    }


@cli_app.command(no_args_is_help=True)
def fill(
    ctx: typer.Context,
    pdf: INPUT_PDF,
    data: Annotated[Path, json_file_option("JSON file with form field values.")],
    output: OPTIONAL_OUTPUT_PDF = None,
    flatten: Annotated[
        bool,
        typer.Option("--flatten", help="Flatten form fields after filling."),
    ] = None,
) -> None:
    """Fill a PDF form with JSON data."""
    obj = PdfWrapper(str(pdf), **ctx.obj)

    schema = obj.schema
    for key, widget in obj.widgets.items():
        if isinstance(widget, (Widgets.Image, Widgets.Signature)):
            schema["properties"][key] = {
                "anyOf": [
                    schema["properties"][key],
                    {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "preserve_aspect_ratio": {"type": "boolean"},
                        },
                        "required": ["path"],
                        "additionalProperties": False,
                    },
                ]
            }

    input_data = load_json_file(data, schema, "--file")
    for k, each in obj.widgets.items():
        if (
            k in input_data
            and isinstance(each, (Widgets.Image, Widgets.Signature))
            and isinstance(input_data[k], dict)
        ):
            each.preserve_aspect_ratio = input_data[k].get(
                "preserve_aspect_ratio", each.preserve_aspect_ratio
            )
            input_data[k] = input_data[k]["path"]

    obj.fill(input_data, flatten=flatten).write(output or pdf)


__all__ = ["cli_app"]
