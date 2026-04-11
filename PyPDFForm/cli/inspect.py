# -*- coding: utf-8 -*-

import json
from typing import Annotated

import typer

from .. import PdfWrapper

inspect_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


@inspect_cli.command(no_args_is_help=True)
def schema(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
) -> None:
    """
    Generate a JSON schema that describes a PDF form.
    """
    print(
        json.dumps(PdfWrapper(pdf, **ctx.obj).schema)
    )
