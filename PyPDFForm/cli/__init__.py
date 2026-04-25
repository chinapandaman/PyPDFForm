# -*- coding: utf-8 -*-
"""
Lazy exports for the optional PyPDFForm CLI.
"""

from typing import Any


def __getattr__(name: str) -> Any:
    if name == "cli_app":
        from .root import cli_app  # pylint: disable=C0415

        return cli_app

    raise AttributeError(name)
