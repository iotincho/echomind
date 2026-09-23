"""Assemble HTTP routes without putting application logic in the entrypoint."""

from fastapi import APIRouter

from app.api.routes import documents, extractions, search, system

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(documents.router)
api_router.include_router(extractions.router)
api_router.include_router(search.router)
