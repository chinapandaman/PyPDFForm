# -*- coding: utf-8 -*-

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
):
    return PdfResponse(
        content=PdfWrapper(
            pdf.file.read(), title=new_title, **options.as_kwargs()
        ).read()
    )
