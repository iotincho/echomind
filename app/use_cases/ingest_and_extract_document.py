"""Process newly supplied material into an extracted, auditable document."""

import logging

from pydantic import BaseModel, ConfigDict

from app.domain.documents import Document, NewDocument
from app.services.extraction_store import ExtractionRun
from app.use_cases.extract_and_persist_document import ExtractAndPersistDocument
from app.use_cases.ingest_document import IngestDocument

logger = logging.getLogger(__name__)


class ProcessedDocument(BaseModel):
    """The stored original material and the extraction generated from it."""

    model_config = ConfigDict(frozen=True)

    document: Document
    extraction: ExtractionRun


class IngestAndExtractDocument:
    """Persist input, then immediately run the default extraction profile."""

    def __init__(
        self,
        ingest_document: IngestDocument,
        extract_document: ExtractAndPersistDocument,
    ) -> None:
        self._ingest_document = ingest_document
        self._extract_document = extract_document

    def execute(self, new_document: NewDocument) -> ProcessedDocument:
        document = self._ingest_document.execute(new_document)
        extraction = self._extract_document.execute(document.id)
        if extraction.result is not None:
            logger.info(
                "extraction_completed document_id=%s run_id=%s result=%s",
                document.id,
                extraction.id,
                extraction.result.model_dump_json(),
            )
        return ProcessedDocument(document=document, extraction=extraction)
