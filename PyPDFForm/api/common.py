# -*- coding: utf-8 -*-
"""
This module provides shared helpers for PyPDFForm web API routes.

It defines the PDF response class and common query parameter parsing used by
endpoint groups that construct `PdfWrapper` instances from uploaded PDF files.
"""

from fastapi import Query, Response
from pydantic import BaseModel


class PdfResponse(Response):
    """
    FastAPI response class for PDF bytes.

    Attributes:
        media_type (str): Response media type for PDF content.
    """

    media_type = "application/pdf"


class PdfWrapperOptions(BaseModel):
    """
    Common `PdfWrapper` options accepted by web API endpoints.

    These fields mirror the constructor options exposed by the Python library
    and CLI so each route can opt into the same PDF handling behavior.

    Attributes:
        need_appearances (bool): Whether to set the PDF's NeedAppearances flag.
        generate_appearance_streams (bool): Whether to generate appearance
            streams for filled fields.
        preserve_metadata (bool): Whether to preserve source PDF metadata.
        use_full_widget_name (bool): Whether to use full widget names when
            reading fields.
    """

    need_appearances: bool = False
    generate_appearance_streams: bool = False
    preserve_metadata: bool = False
    use_full_widget_name: bool = False

    def as_kwargs(self) -> dict:
        """
        Convert options into `PdfWrapper` keyword arguments.

        Returns:
            dict: Mapping of option names to values accepted by `PdfWrapper`.
        """
        return self.model_dump()


def pdf_wrapper_options(
    need_appearances: bool = Query(False),
    generate_appearance_streams: bool = Query(False),
    preserve_metadata: bool = Query(False),
    use_full_widget_name: bool = Query(False),
) -> PdfWrapperOptions:
    """
    Build common `PdfWrapper` options from query parameters.

    FastAPI uses this function as a dependency so routes can share a
    consistent query parameter set.

    Args:
        need_appearances (bool): Whether to set the PDF's NeedAppearances flag.
        generate_appearance_streams (bool): Whether to generate appearance
            streams for filled fields.
        preserve_metadata (bool): Whether to preserve source PDF metadata.
        use_full_widget_name (bool): Whether to use full widget names when
            reading fields.

    Returns:
        PdfWrapperOptions: Parsed options for constructing a `PdfWrapper`.
    """
    return PdfWrapperOptions(
        need_appearances=need_appearances,
        generate_appearance_streams=generate_appearance_streams,
        preserve_metadata=preserve_metadata,
        use_full_widget_name=use_full_widget_name,
    )
