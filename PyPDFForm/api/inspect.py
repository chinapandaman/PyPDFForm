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
from ..shared.utils import get_widget
from .common import (PdfWrapperOptions, api_widget_key_error,
                     pdf_wrapper_options)

inspect_router = APIRouter(prefix="/inspect", tags=["inspect"])


@inspect_router.post("/schema", summary="Return the form schema as JSON.")
def schema(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    pdf: Annotated[UploadFile, File()],
) -> dict:
    """
    Upload a PDF form and return the JSON schema PyPDFForm detects for its
    fields.

    Use this response to discover field names, value types, and validation
    constraints before filling or updating a form.

    \f

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
    Upload a PDF form and return the values currently stored in its fields.

    Empty fields are included in the response so clients can distinguish
    missing form fields from blank values.

    \f

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
    Upload a PDF form and return example data matching the detected schema.

    Use this response as a starting payload when testing form filling or when
    building a client-side editor for a PDF form.

    \f

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
    Upload a PDF form and field name, then return that field's page number,
    coordinates, width, and height.

    Use this endpoint when placing overlays, annotations, or generated content
    relative to an existing form field.

    \f

    Args:
        options (PdfWrapperOptions): Common `PdfWrapper` construction options.
        pdf (UploadFile): Uploaded PDF file to inspect.
        field (str): Name of the form field to locate.

    Returns:
        dict: JSON-serializable field page number, coordinates, and dimensions.
    """
    f = get_widget(
        PdfWrapper(pdf.file.read(), **options.as_kwargs()), field, api_widget_key_error
    )

    return {
        "page_number": f.page_number,
        "x": f.x,
        "y": f.y,
        "width": f.width,
        "height": f.height,
    }
