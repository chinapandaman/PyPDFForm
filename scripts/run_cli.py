# -*- coding: utf-8 -*-
"""
Entry point script for running the PyPDFForm command-line interface.

This module serves as a convenient wrapper that allows the CLI to be
executed directly as a script. When run, it imports and invokes the
main CLI application from PyPDFForm.cli.root.
"""

from PyPDFForm.cli.root import cli_app

if __name__ == "__main__":
    cli_app()
