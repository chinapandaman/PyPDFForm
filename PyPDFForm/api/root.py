# -*- coding: utf-8 -*-

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()


@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse(url="/docs")
