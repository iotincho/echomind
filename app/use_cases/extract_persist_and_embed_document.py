"""Default processing flow: extraction, graph persistence, then claim embeddings."""

import logging
from uuid import UUID

from app.services.extraction_store import ExtractionRun
from app.use_cases.embed_claims import ClaimEmbeddingFailedError, EmbedClaims
from app.use_cases.extract_and_persist_document import ExtractAndPersistDocument

logger = logging.getLogger(__name__)


class ExtractPersistAndEmbedDocument:
    """Make every successful extracted claim semantically searchable."""

    def __init__(
        self,
        extract_and_persist: ExtractAndPersistDocument,
        embed_claims: EmbedClaims,
    ) -> None:
        self._extract_and_persist = extract_and_persist
        self._embed_claims = embed_claims

    def execute(self, document_id: UUID, profile_name: str = "v3") -> ExtractionRun:
        extraction = self._extract_and_persist.execute(document_id, profile_name)
        document = self._extract_and_persist.get_document(document_id)
        try:
            count = self._embed_claims.execute(document, extraction)
        except ClaimEmbeddingFailedError:
            logger.exception(
                "claim_embedding_failed document_id=%s run_id=%s",
                document_id,
                extraction.id,
            )
            raise
        logger.info(
            "claims_embedded document_id=%s run_id=%s count=%s",
            document_id,
            extraction.id,
            count,
        )
        return extraction
