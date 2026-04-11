# -*- coding: utf-8 -*-
"""
This module provides the command-line interface for PyPDFForm.

It defines the CLI application using Typer, providing commands for
interacting with PyPDFForm functionality from the terminal.
"""

from typing import Annotated

import typer

from .. import __version__
from .coordinate import coordinate_cli
from .update import update_cli
from .inspect import inspect_cli

cli_app = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)
cli_app.add_typer(
    coordinate_cli,
    name="coordinate",
    help="Subcommands for interacting with PDF coordinates and dimensions.",
)
cli_app.add_typer(
    inspect_cli,
    name="inspect",
    help="Subcommands for inspecting PDF forms.",
)
cli_app.add_typer(
    update_cli,
    name="update",
    help="Subcommands for updating PDF files and their elements.",
)


def version_callback(value: bool) -> None:
    """
    Callback function to handle the version option.

    This is triggered when the --version or -v flag is passed to the CLI.
    It prints the current version of PyPDFForm and exits the application.

    Args:
        value (bool): The value passed to the version option. If True,
            the version information is displayed and the application exits.
    """
    if value:
        print(f"v{__version__}")
        raise typer.Exit


def need_appearances_callback(ctx: typer.Context, value: bool) -> None:
    """
    Callback function to handle the need_appearances option.

    This is triggered when the --need-appearances flag is passed to the CLI.
    It stores the value in the context object for use by subcommands.

    Args:
        ctx (typer.Context): The Typer context object used to pass data
            between callbacks and commands.
        value (bool): The value passed to the need_appearances option.
            If True, PDF viewers will be instructed to generate appearance
            streams for the output.
    """
    if not ctx.obj:
        ctx.obj = {}
    ctx.obj["need_appearances"] = value


def generate_appearance_streams_callback(ctx: typer.Context, value: bool) -> None:
    """
    Callback function to handle the generate_appearance_streams option.

    This is triggered when the --generate-appearance-streams flag is passed
    to the CLI. It stores the value in the context object for use by subcommands.

    Args:
        ctx (typer.Context): The Typer context object used to pass data
            between callbacks and commands.
        value (bool): The value passed to the generate_appearance_streams
            option. If True, appearance streams will be explicitly generated
            for all form fields in output PDFs using pikepdf.
    """
    if not ctx.obj:
        ctx.obj = {}
    ctx.obj["generate_appearance_streams"] = value


def preserve_metadata_callback(ctx: typer.Context, value: bool) -> None:
    """
    Callback function to handle the preserve_metadata option.

    This is triggered when the --preserve-metadata flag is passed to the CLI.
    It stores the value in the context object for use by subcommands.

    Args:
        ctx (typer.Context): The Typer context object used to pass data
            between callbacks and commands.
        value (bool): The value passed to the preserve_metadata option.
            If True, metadata will be preserved in output PDFs.
    """
    if not ctx.obj:
        ctx.obj = {}
    ctx.obj["preserve_metadata"] = value


def use_full_widget_name_callback(ctx: typer.Context, value: bool) -> None:
    """
    Callback function to handle the use_full_widget_name option.

    This is triggered when the --use-full-widget-name flag is passed to the CLI.
    It stores the value in the context object for use by subcommands.

    Args:
        ctx (typer.Context): The Typer context object used to pass data
            between callbacks and commands.
        value (bool): The value passed to the use_full_widget_name option.
            If True, fully qualified names (including parent field names)
            will be used when looking up form fields.
    """
    if not ctx.obj:
        ctx.obj = {}
    ctx.obj["use_full_widget_name"] = value


@cli_app.callback(invoke_without_command=True, help="PyPDFForm command-line interface.")
def main(
    version: Annotated[  # pylint: disable=W0613
        bool,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show the current version of the CLI and exit.",
        ),
    ] = False,
    need_appearances: Annotated[  # pylint: disable=W0613
        bool,
        typer.Option(
            "--need-appearances",
            callback=need_appearances_callback,
            help="Instruct PDF viewers to generate appearance streams for any output PDF.",
        ),
    ] = False,
    generate_appearance_streams: Annotated[  # pylint: disable=W0613
        bool,
        typer.Option(
            "--generate-appearance-streams",
            callback=generate_appearance_streams_callback,
            help="Generate appearance streams for any output PDF.",
        ),
    ] = False,
    preserve_metadata: Annotated[  # pylint: disable=W0613
        bool,
        typer.Option(
            "--preserve-metadata",
            callback=preserve_metadata_callback,
            help="Preserve PDF metadata in the output.",
        ),
    ] = False,
    use_full_widget_name: Annotated[  # pylint: disable=W0613
        bool,
        typer.Option(
            "--use-full-widget-name",
            callback=use_full_widget_name_callback,
            help="Use fully qualified names when accessing form fields.",
        ),
    ] = False,
) -> None:
    # pylint: disable=C0116
    ...


__all__ = ["cli_app"]
