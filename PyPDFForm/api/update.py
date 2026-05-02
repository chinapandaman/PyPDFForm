# -*- coding: utf-8 -*-
"""
This module defines web API routes for updating existing PDF files.

It exposes `/update` endpoints that accept uploaded PDFs, apply matching
`PdfWrapper` operations, and return modified PDF bytes to HTTP clients.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from .. import PdfWrapper
from .common import PdfResponse, PdfWrapperOptions, pdf_wrapper_options

update_router = APIRouter(prefix="/update", tags=["update"])


@update_router.post(
    "/title",
    summary="Set the PDF title.",
    response_class=PdfResponse,
    responses={
        200: {
            "content": {
                "application/pdf": {"schema": {"type": "string", "format": "binary"}}
            },
        }
    },
)
def title(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    pdf: Annotated[UploadFile, File()],
    new_title: Annotated[str, Form()],
) -> PdfResponse:
    """
    Set the title of an uploaded PDF.

    Args:
        options (PdfWrapperOptions): Common `PdfWrapper` construction options.
        pdf (UploadFile): Uploaded PDF file to update.
        new_title (str): New title to write into the PDF metadata.

    Returns:
        PdfResponse: PDF response containing the updated document bytes.
    """
    return PdfResponse(
        content=PdfWrapper(
            pdf.file.read(), title=new_title, **options.as_kwargs()
        ).read()
    )
