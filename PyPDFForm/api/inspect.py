# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from .. import PdfWrapper
from .common import PdfWrapperOptions, pdf_wrapper_options

inspect_router = APIRouter(prefix="/inspect")


@inspect_router.post("/schema")
def schema(
    pdf: Annotated[UploadFile, File()],
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
):
    return PdfWrapper(pdf.file.read(), **options.as_kwargs()).schema
