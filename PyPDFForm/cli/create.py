# -*- coding: utf-8 -*-
"""
This module defines CLI commands for creating PDF files and PDF content.

It exposes the `create` command group for blank PDFs, extracted page ranges,
merged PDFs, form fields, raw drawn elements, annotations, and coordinate grid
views. Commands in this module translate command-line arguments or grouped JSON
input into `PdfWrapper`, `BlankPage`, `Fields`, `RawElements`, and
`Annotations` operations.
"""

from typing import Annotated

import typer

from .. import (Annotations, BlankPage, Fields, PdfArray, PdfWrapper,
                RawElements)
from .common import create_elements_from_file

create_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


@create_cli.command(no_args_is_help=True)
def blank(
    ctx: typer.Context,
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output PDF path.",
        ),
    ],
    count: Annotated[
        int, typer.Option("--count", "-c", help="Number of blank pages to create.")
    ] = None,
    width: Annotated[
        float,
        typer.Option(
            "--width",
            help="Page width in points.",
        ),
    ] = None,
    height: Annotated[
        float, typer.Option("--height", help="Page height in points.")
    ] = None,
) -> None:
    """Create a new blank PDF."""
    params = {}
    if width is not None:
        params["width"] = width
    if height is not None:
        params["height"] = height

    obj = BlankPage(**params)
    if count is not None and count > 1:
        obj = BlankPage(**params) * count

    PdfWrapper(obj, **ctx.obj).write(output)


@create_cli.command(no_args_is_help=True)
def pages(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Input PDF path.")],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output PDF path.",
        ),
    ],
    start: Annotated[
        int,
        typer.Option(
            "--start",
            "-s",
            help="First page to extract, starting at 1.",
        ),
    ] = None,
    end: Annotated[
        int,
        typer.Option(
            "--end",
            "-e",
            help="Last page to extract, starting at 1.",
        ),
    ] = None,
) -> None:
    """Extract pages from an existing PDF."""
    PdfWrapper(pdf, **ctx.obj).pages[slice((start or 1) - 1, end)].write(output)


@create_cli.command(no_args_is_help=True)
def combine(
    ctx: typer.Context,
    pdfs: Annotated[
        list[str],
        typer.Argument(help="Input PDF paths in merge order."),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output PDF path.",
        ),
    ],
) -> None:
    """Merge multiple PDFs into one."""
    PdfArray([PdfWrapper(pdf, **ctx.obj) for pdf in pdfs]).merge().write(output)


@create_cli.command(no_args_is_help=True)
def field(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Input PDF path.")],
    data: Annotated[
        str,
        typer.Option(
            "--file",
            "-f",
            help="JSON file with form field definitions.",
        ),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output PDF path. Overwrites the input when omitted.",
        ),
    ] = None,
) -> None:
    """Add form fields to a PDF."""
    field_map = {
        "text": Fields.TextField,
        "check": Fields.CheckBoxField,
        "radio": Fields.RadioGroup,
        "dropdown": Fields.DropdownField,
        "image": Fields.ImageField,
        "signature": Fields.SignatureField,
    }
    create_elements_from_file(pdf, data, field_map, "bulk_create_fields", ctx, output)


@create_cli.command(no_args_is_help=True)
def raw(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Input PDF path.")],
    data: Annotated[
        str,
        typer.Option(
            "--file",
            "-f",
            help="JSON file with raw element definitions.",
        ),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output PDF path. Overwrites the input when omitted.",
        ),
    ] = None,
) -> None:
    """Draw text, images, and shapes on a PDF."""
    raw_element_map = {
        "text": RawElements.RawText,
        "image": RawElements.RawImage,
        "line": RawElements.RawLine,
        "rectangle": RawElements.RawRectangle,
        "circle": RawElements.RawCircle,
        "ellipse": RawElements.RawEllipse,
    }
    create_elements_from_file(pdf, data, raw_element_map, "draw", ctx, output)


@create_cli.command(no_args_is_help=True)
def annotation(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Input PDF path.")],
    data: Annotated[
        str,
        typer.Option(
            "--file",
            "-f",
            help="JSON file with annotation definitions.",
        ),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output PDF path. Overwrites the input when omitted.",
        ),
    ] = None,
) -> None:
    """Add annotations to a PDF."""
    annotation_map = {
        "text": Annotations.TextAnnotation,
        "link": Annotations.LinkAnnotation,
        "highlight": Annotations.HighlightAnnotation,
        "underline": Annotations.UnderlineAnnotation,
        "squiggly": Annotations.SquigglyAnnotation,
        "strikeout": Annotations.StrikeOutAnnotation,
        "stamp": Annotations.RubberStampAnnotation,
    }
    create_elements_from_file(pdf, data, annotation_map, "annotate", ctx, output)


@create_cli.command(no_args_is_help=True)
def grid(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Input PDF path.")],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output PDF path. Overwrites the input when omitted.",
        ),
    ] = None,
    red: Annotated[
        float,
        typer.Option(
            "--red",
            "-r",
            help="Grid red value, from 0 to 1.",
        ),
    ] = None,
    green: Annotated[
        float,
        typer.Option(
            "--green",
            "-g",
            help="Grid green value, from 0 to 1.",
        ),
    ] = None,
    blue: Annotated[
        float,
        typer.Option(
            "--blue",
            "-b",
            help="Grid blue value, from 0 to 1.",
        ),
    ] = None,
    margin: Annotated[
        float,
        typer.Option(
            "--margin",
            "-m",
            help="Grid margin in points.",
        ),
    ] = None,
) -> None:
    """Add a coordinate grid to a PDF."""
    params = {}
    if any(
        [
            red is not None,
            green is not None,
            blue is not None,
        ]
    ):
        params["color"] = (red or 0, green or 0, blue or 0)

    if margin is not None:
        params["margin"] = int(margin) if margin.is_integer() else margin
    PdfWrapper(pdf, **ctx.obj).generate_coordinate_grid(**params).write(output or pdf)
