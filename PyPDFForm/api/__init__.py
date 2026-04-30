# -*- coding: utf-8 -*-

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .root import root_router

app = FastAPI()

app.include_router(root_router)


@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse(url="/docs")
