# -*- coding: utf-8 -*-
"""
FastAPI application for the optional PyPDFForm web API.

The web API is intended to be PyPDFForm's third user-facing interface alongside
the Python library and CLI. As the API surface grows, its endpoints should
closely mirror the CLI workflows for creating, filling, inspecting, and updating
PDF forms, while exposing those operations over HTTP.
"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .root import root_router

app = FastAPI()

app.include_router(root_router)


@app.get("/", include_in_schema=False)
async def index():
    """Redirect the API root to the generated OpenAPI documentation."""
    return RedirectResponse(url="/docs")
