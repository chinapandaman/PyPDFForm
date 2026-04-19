# -*- coding: utf-8 -*-
"""
CLI module for creating PDF files and elements.

This module provides command-line interfaces to create PDF elements such as
coordinate grids, form fields (text fields, checkboxes, radio buttons, dropdowns,
signatures, and images), raw PDF elements, and blank PDFs.
"""

from typing import Annotated

import typer

from .. import Annotations, BlankPage, Fields, PdfWrapper, RawElements
from .common import create_elements_from_file

create_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


@create_cli.command(no_args_is_help=True)
def grid(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PDF. Defaults to the original path if not specified.",
        ),
    ] = None,
    red: Annotated[
        float,
        typer.Option(
            "--red",
            "-r",
            help="Red channel of the RGB color.",
        ),
    ] = None,
    green: Annotated[
        float,
        typer.Option(
            "--green",
            "-g",
            help="Green channel of the RGB color.",
        ),
    ] = None,
    blue: Annotated[
        float,
        typer.Option(
            "--blue",
            "-b",
            help="Blue channel of the RGB color.",
        ),
    ] = None,
    margin: Annotated[
        float,
        typer.Option(
            "--margin",
            "-m",
            help="Margin of the grid view in points.",
        ),
    ] = None,
) -> None:
    """
    Create a coordinate grid view for a PDF.
    """
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


@create_cli.command(no_args_is_help=True)
def field(
    ctx: typer.Context,
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
    data: Annotated[
        str,
        typer.Option(
            "--file",
            "-f",
            help="Path to the JSON file representing the field creation parameters.",
        ),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PDF. Defaults to the original path if not specified.",
        ),
    ] = None,
) -> None:
    """
    Create PDF form fields.
    """
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
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
    data: Annotated[
        str,
        typer.Option(
            "--file",
            "-f",
            help="Path to the JSON file representing the draw parameters.",
        ),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PDF. Defaults to the original path if not specified.",
        ),
    ] = None,
) -> None:
    """
    Draw raw PDF elements.
    """
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
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
    data: Annotated[
        str,
        typer.Option(
            "--file",
            "-f",
            help="Path to the JSON file representing the annotation parameters.",
        ),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PDF. Defaults to the original path if not specified.",
        ),
    ] = None,
) -> None:
    """
    Create PDF annotations.
    """
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
def blank(
    ctx: typer.Context,
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PDF.",
        ),
    ],
    count: Annotated[
        int, typer.Option("--count", "-c", help="Number of blank pages.")
    ] = None,
    width: Annotated[
        float,
        typer.Option(
            "--width",
            help="Width of the blank PDF.",
        ),
    ] = None,
    height: Annotated[
        float, typer.Option("--height", help="Height of the blank PDF.")
    ] = None,
) -> None:
    """
    Create a new blank PDF.
    """
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
    pdf: Annotated[str, typer.Argument(help="Path to the input PDF file.")],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PDF.",
        ),
    ],
    start: Annotated[
        int,
        typer.Option(
            "--start",
            "-s",
            help="One-based first page to extract. Defaults to the first page.",
        ),
    ] = None,
    end: Annotated[
        int,
        typer.Option(
            "--end",
            "-e",
            help="One-based last page to extract. Defaults to the final page.",
        ),
    ] = None,
) -> None:
    """
    Create a new PDF from selected pages.
    """
    PdfWrapper(pdf, **ctx.obj).pages[slice((start or 1) - 1, end)].write(output)
