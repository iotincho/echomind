"""Assemble HTTP routes without putting application logic in the entrypoint."""

from fastapi import APIRouter

from app.api.routes import documents, system

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(documents.router)
