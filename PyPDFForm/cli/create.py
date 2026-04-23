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

from .. import (Annotations, BlankPage, Fields, PdfArray, PdfWrapper,
                RawElements)
from .common import (INPUT_PDF, OPTIONAL_OUTPUT_PDF, REQUIRED_OUTPUT_PDF,
                     create_elements_from_file, json_file_option)

create_cli = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]}, no_args_is_help=True
)


@create_cli.command(no_args_is_help=True)
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
    """Extract pages from an existing PDF."""
    PdfWrapper(str(pdf), **ctx.obj).pages[slice((start or 1) - 1, end)].write(output)


@create_cli.command(no_args_is_help=True)
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
    """Merge multiple PDFs into one."""
    PdfArray([PdfWrapper(str(pdf), **ctx.obj) for pdf in pdfs]).merge().write(output)


@create_cli.command(no_args_is_help=True)
def field(
    ctx: typer.Context,
    pdf: INPUT_PDF,
    data: Annotated[Path, json_file_option("JSON file with form field definitions.")],
    output: OPTIONAL_OUTPUT_PDF = None,
) -> None:
    """Add form fields to a PDF."""
    schema = {
        "type": "object",
        "properties": {
            "text": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "required": {"type": "boolean"},
                        "tooltip": {"type": "string"},
                        "width": {"type": "number"},
                        "height": {"type": "number"},
                        "font": {"type": "string"},
                        "font_size": {"type": "number"},
                        "font_color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "bg_color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "border_color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "border_width": {"type": "number"},
                        "max_length": {"type": "integer", "minimum": 1},
                        "comb": {"type": "boolean"},
                        "alignment": {"type": "integer", "minimum": 0},
                        "multiline": {"type": "boolean"},
                    },
                    "required": ["name", "page_number", "x", "y"],
                    "additionalProperties": False,
                },
            },
            "check": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "required": {"type": "boolean"},
                        "tooltip": {"type": "string"},
                        "size": {"type": "number"},
                        "button_style": {"type": "string"},
                        "tick_color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "bg_color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "border_color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "border_width": {"type": "number"},
                    },
                    "required": ["name", "page_number", "x", "y"],
                    "additionalProperties": False,
                },
            },
            "radio": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 1,
                        },
                        "y": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 1,
                        },
                        "required": {"type": "boolean"},
                        "tooltip": {"type": "string"},
                        "size": {"type": "number"},
                        "button_style": {"type": "string"},
                        "tick_color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "bg_color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "border_color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "border_width": {"type": "number"},
                        "shape": {"type": "string"},
                    },
                    "required": ["name", "page_number", "x", "y"],
                    "additionalProperties": False,
                },
            },
            "dropdown": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "required": {"type": "boolean"},
                        "tooltip": {"type": "string"},
                        "width": {"type": "number"},
                        "height": {"type": "number"},
                        "font": {"type": "string"},
                        "font_size": {"type": "number"},
                        "font_color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "bg_color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "border_color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "border_width": {"type": "number"},
                        "options": {
                            "type": "array",
                            "items": {
                                "anyOf": [
                                    {"type": "string"},
                                    {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "minItems": 2,
                                        "maxItems": 2,
                                    },
                                ]
                            },
                            "minItems": 1,
                        },
                    },
                    "required": ["name", "page_number", "x", "y"],
                    "additionalProperties": False,
                },
            },
            "image": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "required": {"type": "boolean"},
                        "tooltip": {"type": "string"},
                        "width": {"type": "number"},
                        "height": {"type": "number"},
                    },
                    "required": ["name", "page_number", "x", "y"],
                    "additionalProperties": False,
                },
            },
            "signature": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "required": {"type": "boolean"},
                        "tooltip": {"type": "string"},
                        "width": {"type": "number"},
                        "height": {"type": "number"},
                    },
                    "required": ["name", "page_number", "x", "y"],
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    }
    field_map = {
        "text": Fields.TextField,
        "check": Fields.CheckBoxField,
        "radio": Fields.RadioGroup,
        "dropdown": Fields.DropdownField,
        "image": Fields.ImageField,
        "signature": Fields.SignatureField,
    }
    create_elements_from_file(
        pdf, data, field_map, schema, "bulk_create_fields", ctx, output
    )


@create_cli.command(no_args_is_help=True)
def raw(
    ctx: typer.Context,
    pdf: INPUT_PDF,
    data: Annotated[Path, json_file_option("JSON file with raw element definitions.")],
    output: OPTIONAL_OUTPUT_PDF = None,
) -> None:
    """Draw text, images, and shapes on a PDF."""
    schema = {
        "type": "object",
        "properties": {
            "text": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "font": {"type": "string"},
                        "font_size": {"type": "number"},
                        "font_color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                    },
                    "required": ["text", "page_number", "x", "y"],
                    "additionalProperties": False,
                },
            },
            "image": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "image": {"type": "string"},
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "width": {"type": "number"},
                        "height": {"type": "number"},
                        "rotation": {"type": "number"},
                    },
                    "required": [
                        "image",
                        "page_number",
                        "x",
                        "y",
                        "width",
                        "height",
                    ],
                    "additionalProperties": False,
                },
            },
            "line": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "page_number": {"type": "integer", "minimum": 1},
                        "src_x": {"type": "number"},
                        "src_y": {"type": "number"},
                        "dest_x": {"type": "number"},
                        "dest_y": {"type": "number"},
                        "color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                    },
                    "required": ["page_number", "src_x", "src_y", "dest_x", "dest_y"],
                    "additionalProperties": False,
                },
            },
            "rectangle": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "width": {"type": "number"},
                        "height": {"type": "number"},
                        "color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "fill_color": {
                            "anyOf": [
                                {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "minItems": 3,
                                    "maxItems": 4,
                                },
                                {"type": "null"},
                            ]
                        },
                    },
                    "required": ["page_number", "x", "y", "width", "height"],
                    "additionalProperties": False,
                },
            },
            "circle": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "page_number": {"type": "integer", "minimum": 1},
                        "center_x": {"type": "number"},
                        "center_y": {"type": "number"},
                        "radius": {"type": "number"},
                        "color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "fill_color": {
                            "anyOf": [
                                {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "minItems": 3,
                                    "maxItems": 4,
                                },
                                {"type": "null"},
                            ]
                        },
                    },
                    "required": ["page_number", "center_x", "center_y", "radius"],
                    "additionalProperties": False,
                },
            },
            "ellipse": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "page_number": {"type": "integer", "minimum": 1},
                        "x1": {"type": "number"},
                        "y1": {"type": "number"},
                        "x2": {"type": "number"},
                        "y2": {"type": "number"},
                        "color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "fill_color": {
                            "anyOf": [
                                {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "minItems": 3,
                                    "maxItems": 4,
                                },
                                {"type": "null"},
                            ]
                        },
                    },
                    "required": ["page_number", "x1", "y1", "x2", "y2"],
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    }
    raw_element_map = {
        "text": RawElements.RawText,
        "image": RawElements.RawImage,
        "line": RawElements.RawLine,
        "rectangle": RawElements.RawRectangle,
        "circle": RawElements.RawCircle,
        "ellipse": RawElements.RawEllipse,
    }
    create_elements_from_file(pdf, data, raw_element_map, schema, "draw", ctx, output)


@create_cli.command(no_args_is_help=True)
def annotation(
    ctx: typer.Context,
    pdf: INPUT_PDF,
    data: Annotated[Path, json_file_option("JSON file with annotation definitions.")],
    output: OPTIONAL_OUTPUT_PDF = None,
) -> None:
    """Add annotations to a PDF."""
    schema = {
        "type": "object",
        "properties": {
            "text": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "width": {"type": "number"},
                        "height": {"type": "number"},
                        "contents": {"type": "string"},
                        "title": {"type": "string"},
                        "icon": {"type": "string"},
                    },
                    "required": ["page_number", "x", "y"],
                    "additionalProperties": False,
                },
            },
            "link": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "width": {"type": "number"},
                        "height": {"type": "number"},
                        "contents": {"type": "string"},
                        "uri": {"type": "string"},
                        "page": {"type": "integer", "minimum": 1},
                    },
                    "required": ["page_number", "x", "y"],
                    "additionalProperties": False,
                },
            },
            "highlight": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "width": {"type": "number"},
                        "height": {"type": "number"},
                        "contents": {"type": "string"},
                    },
                    "required": ["page_number", "x", "y"],
                    "additionalProperties": False,
                },
            },
            "underline": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "width": {"type": "number"},
                        "height": {"type": "number"},
                        "contents": {"type": "string"},
                    },
                    "required": ["page_number", "x", "y"],
                    "additionalProperties": False,
                },
            },
            "squiggly": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "width": {"type": "number"},
                        "height": {"type": "number"},
                        "contents": {"type": "string"},
                    },
                    "required": ["page_number", "x", "y"],
                    "additionalProperties": False,
                },
            },
            "strikeout": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "width": {"type": "number"},
                        "height": {"type": "number"},
                        "contents": {"type": "string"},
                    },
                    "required": ["page_number", "x", "y"],
                    "additionalProperties": False,
                },
            },
            "stamp": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "page_number": {"type": "integer", "minimum": 1},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "width": {"type": "number"},
                        "height": {"type": "number"},
                        "contents": {"type": "string"},
                        "name": {"type": "string"},
                    },
                    "required": ["page_number", "x", "y"],
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    }
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
        pdf, data, annotation_map, schema, "annotate", ctx, output
    )


@create_cli.command(no_args_is_help=True)
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
    PdfWrapper(str(pdf), **ctx.obj).generate_coordinate_grid(**params).write(
        output or pdf
    )
