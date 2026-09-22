"""Document-ingestion HTTP endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.documents import CreateDocumentRequest, DocumentResponse
from app.dependencies import get_ingest_document
from app.domain.documents import NewDocument
from app.services.document_store import DocumentAlreadyExistsError
from app.use_cases.ingest_document import IngestDocument

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
