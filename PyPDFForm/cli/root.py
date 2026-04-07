# -*- coding: utf-8 -*-
"""
This module provides the command-line interface for PyPDFForm.

It defines the CLI application using Typer, providing commands for
interacting with PyPDFForm functionality from the terminal.
"""

from typing import Annotated

import typer

from .. import __version__

cli_app = typer.Typer()


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


@cli_app.command()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
):
    """
    Main entry point for the PyPDFForm CLI.

    This command is executed when running the CLI application. By default,
    it prints a greeting message. When the --version or -v flag is provided,
    it displays the current version of PyPDFForm instead.

    Args:
        version (bool | None): Optional version flag. If provided, the version
            information is displayed and the application exits.
    """
    if not version:
        print("Hello World!")


if __name__ == "__main__":
    cli_app()
