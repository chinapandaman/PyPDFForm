# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from .. import PdfWrapper
from .common import PdfWrapperOptions, pdf_wrapper_options

inspect_router = APIRouter(prefix="/inspect", tags=["inspect"])


@inspect_router.post("/schema", summary="Return the form schema as JSON.")
def schema(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    pdf: Annotated[UploadFile, File()],
):
    """Return the form schema as JSON."""
    return PdfWrapper(pdf.file.read(), **options.as_kwargs()).schema
