# -*- coding: utf-8 -*-

import typer

from .. import PdfWrapper

get_cli = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


@get_cli.command()
def title(pdf: str):
    print(PdfWrapper(pdf).title)
