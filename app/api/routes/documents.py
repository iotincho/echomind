"""Document-ingestion HTTP endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.schemas.documents import (
    CreateDocumentRequest,
    DocumentResponse,
    ProcessedDocumentResponse,
)
from app.dependencies import get_ingest_and_extract_document, get_ingest_document_file
from app.domain.documents import NewDocument
from app.services.document_store import DocumentAlreadyExistsError
from app.use_cases.embed_claims import ClaimEmbeddingFailedError
from app.use_cases.extract_and_persist_document import GraphPersistenceFailedError
from app.use_cases.extract_document import ExtractionRunFailedError
from app.use_cases.ingest_and_extract_document import IngestAndExtractDocument
from app.use_cases.ingest_document_file import (
    IngestDocumentFile,
    InvalidDocumentEncodingError,
    UnsupportedDocumentFileError,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=ProcessedDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    request: CreateDocumentRequest,
    use_case: Annotated[IngestAndExtractDocument, Depends(get_ingest_and_extract_document)],
) -> ProcessedDocumentResponse:
    """Store and immediately extract knowledge from source material."""
    try:
        processed = use_case.execute(NewDocument(**request.model_dump()))
    except DocumentAlreadyExistsError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    except ExtractionRunFailedError as error:
        raise _extraction_failed_response(error) from error
    except GraphPersistenceFailedError as error:
        raise _graph_persistence_failed_response(error) from error
    except ClaimEmbeddingFailedError as error:
        raise _claim_embedding_failed_response(error) from error

    return ProcessedDocumentResponse(
        document=DocumentResponse(**processed.document.model_dump()),
        extraction=processed.extraction,
    )


@router.post(
    "/files",
    response_model=ProcessedDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_document_from_file(
    file: Annotated[UploadFile, File(description="UTF-8 Markdown or plain-text note")],
    file_use_case: Annotated[IngestDocumentFile, Depends(get_ingest_document_file)],
    use_case: Annotated[IngestAndExtractDocument, Depends(get_ingest_and_extract_document)],
) -> ProcessedDocumentResponse:
    """Store and immediately extract from an uploaded `.md` or `.txt` note."""
    try:
        new_document = file_use_case.build_new_document(file.filename, await file.read())
    except UnsupportedDocumentFileError as error:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(error),
        ) from error
    except InvalidDocumentEncodingError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    try:
        processed = use_case.execute(new_document)
    except DocumentAlreadyExistsError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    except ExtractionRunFailedError as error:
        raise _extraction_failed_response(error) from error
    except GraphPersistenceFailedError as error:
        raise _graph_persistence_failed_response(error) from error
    except ClaimEmbeddingFailedError as error:
        raise _claim_embedding_failed_response(error) from error

    return ProcessedDocumentResponse(
        document=DocumentResponse(**processed.document.model_dump()),
        extraction=processed.extraction,
    )


def _extraction_failed_response(error: ExtractionRunFailedError) -> HTTPException:
    """Tell callers the document was stored but did not finish processing."""
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail={
            "message": "Document was stored but extraction failed",
            "run_id": str(error.run_id),
        },
    )


def _graph_persistence_failed_response(error: GraphPersistenceFailedError) -> HTTPException:
    """Tell callers the source and extraction exist but are not queryable in Neo4j yet."""
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "message": "Document was extracted but graph persistence failed",
            "run_id": str(error.run_id),
        },
    )


def _claim_embedding_failed_response(error: ClaimEmbeddingFailedError) -> HTTPException:
    """Tell callers that a completed extraction is not yet semantically searchable."""
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "message": "Document was extracted but claim embeddings failed",
            "run_id": error.run_id,
        },
    )
