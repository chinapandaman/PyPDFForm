# -*- coding: utf-8 -*-
"""
Root router for the PyPDFForm web API.

This router owns the top-level API routes that make PyPDFForm available over
HTTP. Finished endpoint groups should stay aligned with the CLI's behavior so
users can choose between the Python library, command line, or web API without
learning a different workflow model.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse

from .. import PdfWrapper, Widgets
from ..shared.utils import load_json
from .common import (PdfResponse, PdfWrapperOptions, api_json_error,
                     pdf_wrapper_options)

root_router = APIRouter()


@root_router.get("/", include_in_schema=False)
def index() -> RedirectResponse:
    """Redirect the API root to the generated OpenAPI documentation."""
    return RedirectResponse(url="/docs")


@root_router.post(
    "/fill",
    summary="Fill a PDF form with JSON data.",
    response_class=PdfResponse,
    responses={
        200: {
            "content": {
                "application/pdf": {"schema": {"type": "string", "format": "binary"}}
            },
        }
    },
)
def fill(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    pdf: Annotated[UploadFile, File()],
    data: Annotated[str, Form()],
    flatten: Annotated[bool, Form()] = None,
) -> PdfResponse:
    """
    Upload a PDF form and JSON field data, then return the filled PDF.

    `data` must be a JSON object keyed by form field name. Image and signature
    fields may also be provided as an object with `path` and optional
    `preserve_aspect_ratio` values. Use `flatten` to make filled fields
    read-only in the returned PDF.

    \f

    Args:
        options (PdfWrapperOptions): Common `PdfWrapper` construction options.
        pdf (UploadFile): Uploaded PDF form to fill.
        data (str): JSON string containing form field values.
        flatten (bool): Whether to flatten form fields after filling.

    Returns:
        PdfResponse: PDF response containing the filled document bytes.
    """
    obj = PdfWrapper(pdf.file.read(), **options.as_kwargs())

    schema = obj.schema
    for key, widget in obj.widgets.items():
        if isinstance(widget, (Widgets.Image, Widgets.Signature)):
            schema["properties"][key] = {
                "anyOf": [
                    schema["properties"][key],
                    {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "preserve_aspect_ratio": {"type": "boolean"},
                        },
                        "required": ["path"],
                        "additionalProperties": False,
                    },
                ]
            }

    input_data = load_json(data, schema, api_json_error)
    for k, each in obj.widgets.items():
        if (
            k in input_data
            and isinstance(each, (Widgets.Image, Widgets.Signature))
            and isinstance(input_data[k], dict)
        ):
            each.preserve_aspect_ratio = input_data[k].get(
                "preserve_aspect_ratio", each.preserve_aspect_ratio
            )
            input_data[k] = input_data[k]["path"]

    obj.fill(input_data, flatten=flatten)

    return PdfResponse(obj.read())
