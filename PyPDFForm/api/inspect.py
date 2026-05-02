# -*- coding: utf-8 -*-
"""
This module defines web API routes for inspecting PDF form information.

It exposes `/inspect` endpoints that return JSON for form schemas, current
form values, generated sample data, and field rectangle metadata. Each endpoint
wraps read-only `PdfWrapper` properties for clients calling PyPDFForm over HTTP.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from .. import PdfWrapper
from .common import PdfWrapperOptions, pdf_wrapper_options

inspect_router = APIRouter(prefix="/inspect", tags=["inspect"])


@inspect_router.post("/schema", summary="Return the form schema as JSON.")
def schema(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    pdf: Annotated[UploadFile, File()],
) -> dict:
    """
    Return the form schema for an uploaded PDF.

    Args:
        options (PdfWrapperOptions): Common `PdfWrapper` construction options.
        pdf (UploadFile): Uploaded PDF file to inspect.

    Returns:
        dict: JSON-serializable form schema.
    """
    return PdfWrapper(pdf.file.read(), **options.as_kwargs()).schema


@inspect_router.post("/data", summary="Return current form data as JSON.")
def data(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    pdf: Annotated[UploadFile, File()],
) -> dict:
    """
    Return current form data for an uploaded PDF.

    Args:
        options (PdfWrapperOptions): Common `PdfWrapper` construction options.
        pdf (UploadFile): Uploaded PDF file to inspect.

    Returns:
        dict: JSON-serializable current form data.
    """
    return PdfWrapper(pdf.file.read(), **options.as_kwargs()).data


@inspect_router.post("/sample", summary="Return sample fill data as JSON.")
def sample(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    pdf: Annotated[UploadFile, File()],
) -> dict:
    """
    Return sample fill data for an uploaded PDF.

    Args:
        options (PdfWrapperOptions): Common `PdfWrapper` construction options.
        pdf (UploadFile): Uploaded PDF file to inspect.

    Returns:
        dict: JSON-serializable sample fill data.
    """
    return PdfWrapper(pdf.file.read(), **options.as_kwargs()).sample_data


@inspect_router.post(
    "/location", summary="Return a form field's location and size as JSON."
)
def location(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    pdf: Annotated[UploadFile, File()],
    field: Annotated[str, Form()],
) -> dict:
    """
    Return a form field's location and size for an uploaded PDF.

    Args:
        options (PdfWrapperOptions): Common `PdfWrapper` construction options.
        pdf (UploadFile): Uploaded PDF file to inspect.
        field (str): Name of the form field to locate.

    Returns:
        dict: JSON-serializable field page number, coordinates, and dimensions.
    """
    f = PdfWrapper(pdf.file.read(), **options.as_kwargs()).widgets[field]

    # pylint: disable=R0801
    return {
        "page_number": f.page_number,
        "x": f.x,
        "y": f.y,
        "width": f.width,
        "height": f.height,
    }
