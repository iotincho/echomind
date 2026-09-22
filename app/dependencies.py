"""Composition root for infrastructure adapters and application use cases."""

from functools import lru_cache

from app.config import get_settings
from app.graph.neo4j_store import Neo4jGraphStore
from app.services.document_store import FileDocumentStore
from app.services.extraction_store import FileExtractionStore
from app.services.graph_store import GraphStore
from app.services.openai_extractor import OpenAIExtractor
from app.services.structured_extractor import (
    StructuredExtractor,
    UnavailableStructuredExtractor,
)
from app.use_cases.extract_and_persist_document import ExtractAndPersistDocument
from app.use_cases.extract_document import ExtractDocument
from app.use_cases.ingest_and_extract_document import IngestAndExtractDocument
from app.use_cases.ingest_document import IngestDocument
from app.use_cases.ingest_document_file import IngestDocumentFile


@lru_cache
def get_document_store() -> FileDocumentStore:
    """Provide the local development adapter for original documents."""
    return FileDocumentStore(get_settings().documents_path)


@lru_cache
def get_extraction_store() -> FileExtractionStore:
    """Provide local, auditable storage for experimental extraction runs."""
    return FileExtractionStore(get_settings().extractions_path)


@lru_cache
def get_structured_extractor() -> StructuredExtractor:
    """Select a provider adapter without exposing it to routes or use cases."""
    settings = get_settings()
    if settings.llm_provider == "openai":
        return OpenAIExtractor(settings.openai_api_key, settings.openai_model)
    return UnavailableStructuredExtractor(settings.llm_provider)


@lru_cache
def get_graph_store() -> GraphStore:
    """Provide the Neo4j adapter while keeping Cypher out of application use cases."""
    settings = get_settings()
    return Neo4jGraphStore(
        settings.neo4j_uri,
        settings.neo4j_username,
        settings.neo4j_password,
    )


def close_graph_store() -> None:
    """Release the Neo4j driver when the API process stops."""
    graph_store = get_graph_store()
    close = getattr(graph_store, "close", None)
    if close is not None:
        close()
    get_graph_store.cache_clear()


async def get_ingest_document() -> IngestDocument:
    """Build the application operation used by any delivery interface."""
    return IngestDocument(get_document_store())


async def get_ingest_document_file() -> IngestDocumentFile:
    """Build the file-upload operation used by HTTP or a future CLI."""
    return IngestDocumentFile(get_document_store())


async def get_extract_document() -> ExtractDocument:
    """Build the extraction operation shared by HTTP and future CLI adapters."""
    return ExtractDocument(get_document_store(), get_extraction_store(), get_structured_extractor())


async def get_extract_and_persist_document() -> ExtractAndPersistDocument:
    """Build the extraction flow that also makes completed runs queryable in Neo4j."""
    return ExtractAndPersistDocument(await get_extract_document(), get_graph_store())


async def get_ingest_and_extract_document() -> IngestAndExtractDocument:
    """Build the default processing flow triggered by every new document."""
    return IngestAndExtractDocument(
        IngestDocument(get_document_store()),
        await get_extract_and_persist_document(),
    )
