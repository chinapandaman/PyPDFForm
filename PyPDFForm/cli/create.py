# -*- coding: utf-8 -*-
"""
This module defines CLI commands for creating PDF files and PDF content.

It exposes the `create` command group for blank PDFs, extracted page ranges,
merged PDFs, form fields, raw drawn elements, annotations, and coordinate grid
views. Commands in this module translate command-line arguments or grouped JSON
input into `PdfWrapper`, `BlankPage`, `Fields`, `RawElements`, and
`Annotations` operations.
"""

from pathlib import Path
from typing import Annotated

import typer

from .. import Annotations, BlankPage, Fields, PdfArray, PdfWrapper, RawElements
from .common import (
    INPUT_PDF,
    OPTIONAL_OUTPUT_PDF,
    REQUIRED_OUTPUT_PDF,
    cli_bad_parameter,
    create_elements_from_file,
    json_file_option,
)
from .schemas.create import ANNOTATION_SCHEMA, FIELD_SCHEMA, RAW_SCHEMA

create_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


@create_cli.command(
    no_args_is_help=True,
    help="Create a new blank PDF.",
)
def blank(
    ctx: typer.Context,
    output: REQUIRED_OUTPUT_PDF,
    count: Annotated[
        int,
        typer.Option(
            "--count",
            "-c",
            min=1,
            help="Number of blank pages to create.",
        ),
    ] = None,
    width: Annotated[
        float,
        typer.Option(
            "--width",
            min=0.0,
            help="Page width in points.",
        ),
    ] = None,
    height: Annotated[
        float,
        typer.Option(
            "--height",
            min=0.0,
            help="Page height in points.",
        ),
    ] = None,
) -> None:
    """
    Create a blank PDF with optional page size and page count.

    The command builds a `BlankPage` using the supplied dimensions, duplicates
    it when multiple pages are requested, wraps the result with the global CLI
    options stored in `ctx.obj`, and writes the new PDF to the required output
    path.

    Args:
        ctx (typer.Context): Typer context containing global `PdfWrapper`
            options in `ctx.obj`.
        output (Path): Output PDF path.
        count (int, optional): Number of blank pages to create. Defaults to
            None.
        width (float, optional): Page width in points. Defaults to None.
        height (float, optional): Page height in points. Defaults to None.
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


@create_cli.command(
    no_args_is_help=True,
    help="Extract pages from an existing PDF.",
)
def extract(
    ctx: typer.Context,
    pdf: INPUT_PDF,
    output: REQUIRED_OUTPUT_PDF,
    start: Annotated[
        int,
        typer.Option(
            "--start",
            "-s",
            min=1,
            help="First page to extract, starting at 1.",
        ),
    ] = None,
    end: Annotated[
        int,
        typer.Option(
            "--end",
            "-e",
            min=1,
            help="Last page to extract, starting at 1.",
        ),
    ] = None,
) -> None:
    """
    Extract a page range from an existing PDF.

    The command validates that the requested end page does not precede the
    start page, converts the 1-based CLI page numbers into the slice expected
    by `PdfWrapper.pages`, and writes the extracted pages to the required
    output path.

    Args:
        ctx (typer.Context): Typer context containing global `PdfWrapper`
            options in `ctx.obj`.
        pdf (Path): Input PDF path.
        output (Path): Output PDF path.
        start (int, optional): First page to extract, starting at 1. Defaults
            to None.
        end (int, optional): Last page to extract, starting at 1. Defaults to
            None.

    Raises:
        typer.BadParameter: Raised when both page bounds are supplied and the
            start page is after the end page.
    """
    if start is not None and end is not None and start > end:
        message = "End page must be greater than or equal to start page."
        cli_bad_parameter(
            message,
            param_hint="--end",
        )

    PdfWrapper(str(pdf), **ctx.obj).pages[slice((start or 1) - 1, end)].write(output)


@create_cli.command(
    no_args_is_help=True,
    help="Merge multiple PDFs into one.",
)
def merge(
    ctx: typer.Context,
    pdfs: Annotated[
        list[Path],
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Input PDF paths in merge order.",
        ),
    ],
    output: REQUIRED_OUTPUT_PDF,
) -> None:
    """
    Merge input PDFs in the order provided on the command line.

    Each path is loaded into a `PdfWrapper` with the global CLI options, passed
    to `PdfArray`, merged into one document, and written to the required output
    path.

    Args:
        ctx (typer.Context): Typer context containing global `PdfWrapper`
            options in `ctx.obj`.
        pdfs (list[Path]): Input PDF paths in merge order.
        output (Path): Output PDF path.
    """
    PdfArray([PdfWrapper(str(pdf), **ctx.obj) for pdf in pdfs]).merge().write(output)


@create_cli.command(
    no_args_is_help=True,
    help="Add form fields to a PDF.",
)
def field(
    ctx: typer.Context,
    pdf: INPUT_PDF,
    data: Annotated[Path, json_file_option("JSON file with form field definitions.")],
    output: OPTIONAL_OUTPUT_PDF = None,
) -> None:
    """
    Add form fields described by grouped JSON definitions.

    The command maps JSON groups such as `text`, `check`, and `signature` to
    PyPDFForm field classes, validates the input file against the CLI field
    schema, creates the corresponding field objects, and calls
    `PdfWrapper.bulk_create_fields` before writing the modified PDF.

    Args:
        ctx (typer.Context): Typer context containing global `PdfWrapper`
            options in `ctx.obj`.
        pdf (Path): Input PDF path.
        data (Path): JSON file containing grouped form field definitions.
        output (Path, optional): Output PDF path. If omitted, the input PDF is
            overwritten. Defaults to None.
    """
    field_map = {
        "text": Fields.TextField,
        "check": Fields.CheckBoxField,
        "radio": Fields.RadioGroup,
        "dropdown": Fields.DropdownField,
        "image": Fields.ImageField,
        "signature": Fields.SignatureField,
    }
    create_elements_from_file(
        pdf=pdf,
        data=data,
        element_map=field_map,
        schema=FIELD_SCHEMA,
        method_name="bulk_create_fields",
        ctx=ctx,
        param_hint="--file",
        output=output,
    )


@create_cli.command(
    no_args_is_help=True,
    help="Draw text, images, and shapes on a PDF.",
)
def raw(
    ctx: typer.Context,
    pdf: INPUT_PDF,
    data: Annotated[Path, json_file_option("JSON file with raw element definitions.")],
    output: OPTIONAL_OUTPUT_PDF = None,
) -> None:
    """
    Draw raw elements described by grouped JSON definitions.

    The command maps JSON groups such as `text`, `image`, and `rectangle` to
    raw element classes, validates the input file against the CLI raw element
    schema, creates the corresponding drawable objects, and calls
    `PdfWrapper.draw` before writing the modified PDF.

    Args:
        ctx (typer.Context): Typer context containing global `PdfWrapper`
            options in `ctx.obj`.
        pdf (Path): Input PDF path.
        data (Path): JSON file containing grouped raw element definitions.
        output (Path, optional): Output PDF path. If omitted, the input PDF is
            overwritten. Defaults to None.
    """
    raw_element_map = {
        "text": RawElements.RawText,
        "image": RawElements.RawImage,
        "line": RawElements.RawLine,
        "rectangle": RawElements.RawRectangle,
        "circle": RawElements.RawCircle,
        "ellipse": RawElements.RawEllipse,
    }
    create_elements_from_file(
        pdf=pdf,
        data=data,
        element_map=raw_element_map,
        schema=RAW_SCHEMA,
        method_name="draw",
        ctx=ctx,
        param_hint="--file",
        output=output,
    )


@create_cli.command(
    no_args_is_help=True,
    help="Add annotations to a PDF.",
)
def annotation(
    ctx: typer.Context,
    pdf: INPUT_PDF,
    data: Annotated[Path, json_file_option("JSON file with annotation definitions.")],
    output: OPTIONAL_OUTPUT_PDF = None,
) -> None:
    """
    Add annotations described by grouped JSON definitions.

    The command maps JSON groups such as `text`, `link`, and `highlight` to
    annotation classes, validates the input file against the CLI annotation
    schema, creates the corresponding annotation objects, and calls
    `PdfWrapper.annotate` before writing the modified PDF.

    Args:
        ctx (typer.Context): Typer context containing global `PdfWrapper`
            options in `ctx.obj`.
        pdf (Path): Input PDF path.
        data (Path): JSON file containing grouped annotation definitions.
        output (Path, optional): Output PDF path. If omitted, the input PDF is
            overwritten. Defaults to None.
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
    create_elements_from_file(
        pdf=pdf,
        data=data,
        element_map=annotation_map,
        schema=ANNOTATION_SCHEMA,
        method_name="annotate",
        ctx=ctx,
        param_hint="--file",
        output=output,
    )


@create_cli.command(
    no_args_is_help=True,
    help="Add a coordinate grid to a PDF.",
)
def grid(
    ctx: typer.Context,
    pdf: INPUT_PDF,
    output: OPTIONAL_OUTPUT_PDF = None,
    red: Annotated[
        float,
        typer.Option(
            "--red",
            "-r",
            min=0.0,
            max=1.0,
            help="Grid red value, from 0 to 1.",
        ),
    ] = None,
    green: Annotated[
        float,
        typer.Option(
            "--green",
            "-g",
            min=0.0,
            max=1.0,
            help="Grid green value, from 0 to 1.",
        ),
    ] = None,
    blue: Annotated[
        float,
        typer.Option(
            "--blue",
            "-b",
            min=0.0,
            max=1.0,
            help="Grid blue value, from 0 to 1.",
        ),
    ] = None,
    margin: Annotated[
        float,
        typer.Option(
            "--margin",
            "-m",
            min=0.0,
            help="Grid margin in points.",
        ),
    ] = None,
) -> None:
    """
    Overlay a coordinate grid on an existing PDF.

    The command collects optional RGB color components and margin values,
    normalizes whole-number margins to integers for stable output, generates a
    coordinate grid through `PdfWrapper.generate_coordinate_grid`, and writes
    the result to the requested output path or back to the input file.

    Args:
        ctx (typer.Context): Typer context containing global `PdfWrapper`
            options in `ctx.obj`.
        pdf (Path): Input PDF path.
        output (Path, optional): Output PDF path. If omitted, the input PDF is
            overwritten. Defaults to None.
        red (float, optional): Grid red value from 0 to 1. Defaults to None.
        green (float, optional): Grid green value from 0 to 1. Defaults to
            None.
        blue (float, optional): Grid blue value from 0 to 1. Defaults to None.
        margin (float, optional): Grid margin in points. Defaults to None.
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
    PdfWrapper(str(pdf), **ctx.obj).generate_coordinate_grid(**params).write(
        output or pdf
    )
