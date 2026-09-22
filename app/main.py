"""HTTP entrypoint for the EchoMind POC."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.config import get_settings
from app.dependencies import close_graph_store
from app.logging import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(get_settings().log_level)
    try:
        yield
    finally:
        close_graph_store()


app = FastAPI(
    title="EchoMind",
    description="Personal AI-assisted introspection proof of concept.",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(api_router)
