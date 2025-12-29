from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles

from app.services.ansi import get_ansi_content
from app.services.html import get_content
from app.views.routes import (
    internal_exception,
    not_found_exception,
    router,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_content()
    get_ansi_content()
    yield


app = FastAPI(
    openapi_url=None,
    lifespan=lifespan,
)

app.include_router(router)

app.mount("/static/", StaticFiles(directory="app/static/"), name="static")


@app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
async def internal_exception_handler(request: Request, _: Exception):
    return internal_exception(request)


@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def not_found_exception_handler(request: Request, _: Exception):
    return not_found_exception(request)
