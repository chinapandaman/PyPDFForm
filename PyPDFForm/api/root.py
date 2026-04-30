# -*- coding: utf-8 -*-

from fastapi import APIRouter

root_router = APIRouter()


@root_router.post("/fill")
async def fill():
    return "fill"
