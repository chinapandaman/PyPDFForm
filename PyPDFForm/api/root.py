# -*- coding: utf-8 -*-
"""
Root router for the PyPDFForm web API.

This router owns the top-level API routes that make PyPDFForm available over
HTTP. Finished endpoint groups should stay aligned with the CLI's behavior so
users can choose between the Python library, command line, or web API without
learning a different workflow model.
"""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

root_router = APIRouter()


@root_router.get("/", include_in_schema=False)
def index() -> RedirectResponse:
    """Redirect the API root to the generated OpenAPI documentation."""
    return RedirectResponse(url="/docs")
