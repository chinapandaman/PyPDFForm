# -*- coding: utf-8 -*-

from fastapi import Query
from pydantic import BaseModel


class PdfWrapperOptions(BaseModel):
    need_appearances: bool = False
    generate_appearance_streams: bool = False
    preserve_metadata: bool = False
    use_full_widget_name: bool = False

    def as_kwargs(self) -> dict:
        return self.model_dump()


def pdf_wrapper_options(
    need_appearances: bool = Query(False),
    generate_appearance_streams: bool = Query(False),
    preserve_metadata: bool = Query(False),
    use_full_widget_name: bool = Query(False),
) -> PdfWrapperOptions:
    return PdfWrapperOptions(
        need_appearances=need_appearances,
        generate_appearance_streams=generate_appearance_streams,
        preserve_metadata=preserve_metadata,
        use_full_widget_name=use_full_widget_name,
    )
