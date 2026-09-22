"""Run one versioned structured extraction without graph persistence."""

import logging
from uuid import UUID

from app.extraction.contracts import (
    Claim,
    Concept,
    Entity,
    Evidence,
    ExtractionResult,
    Relationship,
)
from app.extraction.profiles import get_profile
from app.services.document_store import DocumentStore
from app.services.extraction_store import ExtractionRun, ExtractionStore, new_extraction_run
from app.services.structured_extractor import StructuredExtractor

logger = logging.getLogger(__name__)


class ExtractionRunFailedError(RuntimeError):
    """Signals that an auditable failed run was recorded."""

    def __init__(self, run_id: UUID) -> None:
        self.run_id = run_id
        super().__init__(f"Extraction run {run_id} failed")


class ExtractionEvidenceError(ValueError):
    """Raised when extracted evidence cannot be traced to the source document."""


class ExtractDocument:
    """Extract evidence-backed knowledge from a stored original document."""

    def __init__(
        self,
        document_store: DocumentStore,
        extraction_store: ExtractionStore,
        extractor: StructuredExtractor,
    ) -> None:
        self._document_store = document_store
        self._extraction_store = extraction_store
        self._extractor = extractor

    def execute(self, document_id: UUID, profile_name: str = "v3") -> ExtractionRun:
        document = self._document_store.get(document_id)
        profile = get_profile(profile_name)
        provider_extraction = None
        try:
            provider_extraction = self._extractor.extract(document, profile)
            result = resolve_evidence(document.content, provider_extraction.result)
            validate_evidence(document.content, result)
        except Exception as error:
            failed_run = new_extraction_run(
                document_id=document.id,
                profile_name=profile.name,
                schema_version=profile.schema_version,
                prompt_version=profile.prompt_version,
                provider=self._extractor.provider_name,
                model=self._extractor.model_name,
                status="failed",
                error=type(error).__name__,
            )
            logger.exception(
                "extraction_failed document_id=%s run_id=%s provider=%s model=%s profile=%s "
                "error_type=%s",
                document.id,
                failed_run.id,
                self._extractor.provider_name,
                self._extractor.model_name,
                profile.name,
                type(error).__name__,
            )
            if provider_extraction is not None:
                logger.error(
                    "extraction_failed_result document_id=%s run_id=%s result=%s",
                    document.id,
                    failed_run.id,
                    provider_extraction.result.model_dump_json(),
                )
            self._extraction_store.save(failed_run)
            raise ExtractionRunFailedError(failed_run.id) from error

        completed_run = new_extraction_run(
            document_id=document.id,
            profile_name=profile.name,
            schema_version=profile.schema_version,
            prompt_version=profile.prompt_version,
            provider=provider_extraction.provider,
            model=provider_extraction.model,
            status="completed",
            result=result,
            response_id=provider_extraction.response_id,
            usage=provider_extraction.usage,
        )
        self._extraction_store.save(completed_run)
        return completed_run

    def get_document(self, document_id: UUID):
        """Expose the preserved source only to composed application use cases."""
        return self._document_store.get(document_id)


def resolve_evidence(content: str, result: ExtractionResult) -> ExtractionResult:
    """Locate each exact model-generated quote once, without trusting model offsets."""

    def resolve(evidence: Evidence) -> Evidence:
        positions: list[int] = []
        start = content.find(evidence.quote)
        while start != -1:
            positions.append(start)
            start = content.find(evidence.quote, start + 1)

        if not positions:
            raise ExtractionEvidenceError("Evidence quote does not occur in the source document")
        if len(positions) > 1:
            raise ExtractionEvidenceError("Evidence quote is ambiguous in the source document")

        start_char = positions[0]
        end_char = start_char + len(evidence.quote)
        return Evidence(
            quote=evidence.quote,
            start_char=start_char,
            end_char=end_char,
            start_line=content.count("\n", 0, start_char) + 1,
            end_line=content.count("\n", 0, end_char - 1) + 1,
        )

    def resolved_items(items: list[Concept] | list[Entity] | list[Claim] | list[Relationship]):
        return [
            item.model_copy(
                update={"evidence": [resolve(evidence) for evidence in item.evidence]}
            )
            for item in items
        ]

    return ExtractionResult(
        concepts=resolved_items(result.concepts),
        entities=resolved_items(result.entities),
        claims=resolved_items(result.claims),
        relationships=resolved_items(result.relationships),
    )


def validate_evidence(content: str, result: ExtractionResult) -> None:
    """Reject outputs whose evidence or relationship references are not source-grounded."""
    items = [*result.concepts, *result.entities, *result.claims]
    known_references = {
        ("concept", item.id) for item in result.concepts
    } | {("entity", item.id) for item in result.entities} | {
        ("claim", item.id) for item in result.claims
    }

    for item in [*items, *result.relationships]:
        for evidence in item.evidence:
            if evidence.start_char is None or evidence.end_char is None:
                raise ExtractionEvidenceError("Evidence location was not resolved")
            if evidence.end_char > len(content) or evidence.start_char >= evidence.end_char:
                raise ExtractionEvidenceError("Evidence range is outside the source document")
            if content[evidence.start_char : evidence.end_char] != evidence.quote:
                raise ExtractionEvidenceError("Evidence quote does not match the source document")

    for relationship in result.relationships:
        source = (relationship.source.kind, relationship.source.id)
        target = (relationship.target.kind, relationship.target.id)
        if source not in known_references or target not in known_references:
            raise ExtractionEvidenceError("Relationship references an unknown extracted item")
