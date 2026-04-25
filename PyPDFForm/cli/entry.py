# -*- coding: utf-8 -*-
"""
Console script entry point for the optional PyPDFForm CLI.

The CLI implementation depends on the optional ``cli`` extra. This lightweight
wrapper lets the ``pypdfform`` command fail with installation guidance instead
of an import traceback when those optional dependencies are absent.
"""

import importlib
import sys

CLI_DEPENDENCIES = {"jsonschema", "typer"}
CLI_INSTALL_HINT = "pip install 'PyPDFForm[cli]'"


def main() -> None:
    """
    Run the PyPDFForm CLI.

    Raises:
        SystemExit: Raised with exit code 1 when optional CLI dependencies are
            missing.
    """
    try:
        cli_module = importlib.import_module("PyPDFForm.cli.root")
    except ModuleNotFoundError as exc:
        if exc.name in CLI_DEPENDENCIES:
            print(
                "PyPDFForm CLI dependencies are not installed. "
                f"Install them with: {CLI_INSTALL_HINT}",
                file=sys.stderr,
            )
            raise SystemExit(1) from None
        raise

    getattr(cli_module, "cli_app")()
