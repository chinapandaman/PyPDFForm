# -*- coding: utf-8 -*-
"""
This module defines web API routes for creating PDF files and PDF content.

It exposes `/create` endpoints that accept uploaded PDFs, apply matching
`PdfWrapper` creation operations, and return generated PDF bytes to HTTP
clients.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from .. import PdfWrapper
from .common import PdfResponse, PdfWrapperOptions, pdf_wrapper_options

create_router = APIRouter(prefix="/create", tags=["create"])


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
    Add a coordinate grid to an uploaded PDF.

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
