# -*- coding: utf-8 -*-
"""
CLI commands for inspecting PDF form field data.

This module provides command-line interface commands for extracting
information from PDF forms. Features include generating a JSON schema
describing the form fields, inspecting the current filled data of a
PDF form, and generating sample data for filling a form.
"""

import json
from typing import Annotated

import typer

from .. import PdfWrapper

read_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


@read_cli.command(no_args_is_help=True)
def schema(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
) -> None:
    """
    Generate a JSON schema that describes a PDF form.
    """
    print(json.dumps(PdfWrapper(pdf, **ctx.obj).schema))


@read_cli.command(no_args_is_help=True)
def data(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
) -> None:
    """
    Inspect the current filled data of a PDF form.
    """
    print(json.dumps(PdfWrapper(pdf, **ctx.obj).data))


@read_cli.command(no_args_is_help=True)
def sample(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
) -> None:
    """
    Generate sample data for filling a PDF form.
    """
    print(json.dumps(PdfWrapper(pdf, **ctx.obj).sample_data))
