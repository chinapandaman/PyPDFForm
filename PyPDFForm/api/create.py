# -*- coding: utf-8 -*-

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
