"""Routes that trigger experimental, evidence-backed extraction runs."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.extractions import CreateExtractionRequest
from app.dependencies import get_extract_and_persist_document
from app.extraction.profiles import UnknownExtractionProfileError
from app.services.document_store import DocumentNotFoundError
from app.services.extraction_store import ExtractionRun
from app.use_cases.extract_and_persist_document import (
    ExtractAndPersistDocument,
    GraphPersistenceFailedError,
)
from app.use_cases.extract_document import ExtractionRunFailedError

router = APIRouter(prefix="/documents", tags=["extractions"])


@router.post(
    "/{document_id}/extractions",
    response_model=ExtractionRun,
    status_code=status.HTTP_201_CREATED,
)
async def create_extraction(
    document_id: UUID,
    request: CreateExtractionRequest,
    use_case: Annotated[
        ExtractAndPersistDocument,
        Depends(get_extract_and_persist_document),
    ],
) -> ExtractionRun:
    """Run a selected profile and persist its validated result in Neo4j."""
    try:
        return use_case.execute(document_id, request.profile)
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except UnknownExtractionProfileError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except ExtractionRunFailedError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"message": "Extraction failed", "run_id": str(error.run_id)},
        ) from error
    except GraphPersistenceFailedError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": "Extraction completed but graph persistence failed",
                "run_id": str(error.run_id),
            },
        ) from error
