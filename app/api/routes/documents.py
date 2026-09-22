"""Document-ingestion HTTP endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.schemas.documents import CreateDocumentRequest, DocumentResponse
from app.dependencies import get_ingest_document, get_ingest_document_file
from app.domain.documents import NewDocument
from app.services.document_store import DocumentAlreadyExistsError
from app.use_cases.ingest_document import IngestDocument
from app.use_cases.ingest_document_file import (
    IngestDocumentFile,
    InvalidDocumentEncodingError,
    UnsupportedDocumentFileError,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    request: CreateDocumentRequest,
    use_case: Annotated[IngestDocument, Depends(get_ingest_document)],
) -> DocumentResponse:
    """Store source material exactly once, before extraction or inference."""
    try:
        document = use_case.execute(NewDocument(**request.model_dump()))
    except DocumentAlreadyExistsError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error

    return DocumentResponse(**document.model_dump())


@router.post("/files", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document_from_file(
    file: Annotated[UploadFile, File(description="UTF-8 Markdown or plain-text note")],
    use_case: Annotated[IngestDocumentFile, Depends(get_ingest_document_file)],
) -> DocumentResponse:
    """Store an uploaded `.md` or `.txt` note without interpreting its contents."""
    try:
        document = use_case.execute(file.filename, await file.read())
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

    return DocumentResponse(**document.model_dump())
