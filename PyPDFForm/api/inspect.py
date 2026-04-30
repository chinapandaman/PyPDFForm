# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from .. import PdfWrapper
from .common import PdfWrapperOptions, pdf_wrapper_options

inspect_router = APIRouter(prefix="/inspect", tags=["inspect"])


@inspect_router.post("/schema", summary="Return the form schema as JSON.")
def schema(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    pdf: Annotated[UploadFile, File()],
):
    return PdfWrapper(pdf.file.read(), **options.as_kwargs()).schema


@inspect_router.post("/data", summary="Return current form data as JSON.")
def data(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    pdf: Annotated[UploadFile, File()],
):
    return PdfWrapper(pdf.file.read(), **options.as_kwargs()).data


@inspect_router.post("/sample", summary="Return sample fill data as JSON.")
def sample(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    pdf: Annotated[UploadFile, File()],
):
    return PdfWrapper(pdf.file.read(), **options.as_kwargs()).sample_data


@inspect_router.post(
    "/location", summary="Return a form field's location and size as JSON."
)
def location(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    pdf: Annotated[UploadFile, File()],
    field: Annotated[str, Form()],
):
    f = PdfWrapper(pdf.file.read(), **options.as_kwargs()).widgets[field]

    return {
        "page_number": f.page_number,
        "x": f.x,
        "y": f.y,
        "width": f.width,
        "height": f.height,
    }
