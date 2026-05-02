# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import APIRouter, Body, Depends, File, Response, UploadFile

from .. import PdfWrapper
from .common import PdfWrapperOptions, pdf_wrapper_options

update_router = APIRouter(prefix="/update", tags=["update"])


@update_router.post("/title", summary="Set the PDF title.")
def title(
    options: Annotated[PdfWrapperOptions, Depends(pdf_wrapper_options)],
    pdf: Annotated[UploadFile, File()],
    new_title: Annotated[str, Body()],
):
    return Response(
        content=PdfWrapper(
            pdf.file.read(), title=new_title, **options.as_kwargs()
        ).read(),
        media_type="application/pdf",
    )
