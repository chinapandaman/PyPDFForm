# -*- coding: utf-8 -*-
"""
This module defines web API routes for creating PDF files and PDF content.

It exposes `/create` endpoints that accept uploaded PDFs, apply matching
`PdfWrapper` creation operations, and return generated PDF bytes to HTTP
clients.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel

from .. import BlankPage, PdfWrapper
from .common import PdfResponse, PdfWrapperOptions, pdf_wrapper_options

create_router = APIRouter(prefix="/create", tags=["create"])


class BlankBody(BaseModel):
    """
    Options for the blank PDF to create.

    All fields are optional. Omit dimensions to use the default page size and
    omit count to create a single page.
    """

    count: int | None = None
    width: float | None = None
    height: float | None = None


@create_router.post(
    "/blank",
    summary="Create a new blank PDF.",
    response_class=PdfResponse,
    responses={
        200: {
            "content": {
                "application/pdf": {"schema": {"type": "string", "format": "binary"}}
            },
        }
    },
)
def blank(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    body: BlankBody,
) -> PdfResponse:
    """
    Create and return a new PDF containing one or more blank pages.

    Use the optional dimensions to size each page and `count` to request
    multiple pages.

    \f

    Args:
        options (PdfWrapperOptions): Common `PdfWrapper` construction options.
        body (BlankBody): Blank page count and page dimension options.

    Returns:
        PdfResponse: PDF response containing the generated blank document.
    """
    params = {}
    if body.width is not None:
        params["width"] = body.width
    if body.height is not None:
        params["height"] = body.height

    obj = BlankPage(**params)
    if body.count is not None and body.count > 1:
        print(body.count)
        obj = BlankPage(**params) * body.count

    return PdfResponse(PdfWrapper(obj, **options.as_kwargs()).read())


@create_router.post(
    "/grid",
    summary="Add a coordinate grid to a PDF.",
    response_class=PdfResponse,
    responses={
        200: {
            "content": {
                "application/pdf": {"schema": {"type": "string", "format": "binary"}}
            },
        }
    },
)
def grid(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    pdf: Annotated[UploadFile, File()],
    red: Annotated[float, Form()] = None,
    green: Annotated[float, Form()] = None,
    blue: Annotated[float, Form()] = None,
    margin: Annotated[float, Form()] = None,
) -> PdfResponse:
    """
    Upload a PDF and return a copy with a coordinate grid overlaid on each page.

    Use the optional RGB components to choose the grid color and `margin` to
    adjust the grid spacing from the page edges.

    \f

    Args:
        options (PdfWrapperOptions): Common `PdfWrapper` construction options.
        pdf (UploadFile): Uploaded PDF file to annotate with a grid.
        red (float): Red component of the grid color, from 0 to 1.
        green (float): Green component of the grid color, from 0 to 1.
        blue (float): Blue component of the grid color, from 0 to 1.
        margin (float): Grid margin in points.

    Returns:
        PdfResponse: PDF response containing the document with a coordinate grid.
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
    return PdfResponse(
        PdfWrapper(pdf.file.read(), **options.as_kwargs())
        .generate_coordinate_grid(**params)
        .read()
    )
