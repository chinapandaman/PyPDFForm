# -*- coding: utf-8 -*-

from typing import Annotated

import typer

from .. import __version__

cli_app = typer.Typer()


def version_callback(value: bool):
    if value:
        print(f"v{__version__}")
        raise typer.Exit()


@cli_app.command()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
):
    if not version:
        print("Hello World!")


if __name__ == "__main__":
    cli_app()
