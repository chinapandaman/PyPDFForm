# -*- coding: utf-8 -*-
"""
Root router for the PyPDFForm web API.

This router owns the top-level API routes that make PyPDFForm available over
HTTP. Finished endpoint groups should stay aligned with the CLI's behavior so
users can choose between the Python library, command line, or web API without
learning a different workflow model.
"""

from fastapi import APIRouter

root_router = APIRouter()
