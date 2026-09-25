"""HTTP entrypoint for the El Espejo POC."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.router import api_router
from src.config import get_settings
from src.dependencies import close_graph_store
from src.logging import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(get_settings().log_level)
    try:
        yield
    finally:
        close_graph_store()


app = FastAPI(
    title="El Espejo",
    description="Personal AI-assisted introspection proof of concept.",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(api_router)
