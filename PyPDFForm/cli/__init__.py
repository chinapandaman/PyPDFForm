# -*- coding: utf-8 -*-
"""
This module provides the command-line interface for PyPDFForm.

It defines the CLI application using Typer, providing commands for
interacting with PyPDFForm functionality from the terminal.
"""

from typing import Annotated

import typer

from .. import __version__
from .get import get_cli

cli_app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True
)
cli_app.add_typer(get_cli, name="get")


def version_callback(value: bool):
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


@cli_app.command(hidden=True)
@cli_app.callback(invoke_without_command=True)
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show current version of the CLI.",
        ),
    ] = None,
):
    # pylint: disable=C0116
    if not version:
        pass


__all__ = ["cli_app"]
