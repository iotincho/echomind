# ruff: noqa: E501
"""Build self-describing document metadata for reflective model context."""

from src.embeddings.contracts import SimilarClaim
from src.reflection.contracts import MetadataFieldDefinition, ReflectionDocument

CORE_FIELD_DEFINITIONS = {
    "id": MetadataFieldDefinition(description="Stable El Espejo document identifier.", value_type="string"),
    "source": MetadataFieldDefinition(description="Ingestion provenance supplied with the document.", value_type="string"),
    "created_at": MetadataFieldDefinition(
        description="When the note was expressed, preserving its timezone offset. Use it to order events and identify the latest known state; it is not the extraction or upload time.",
        value_type="ISO-8601 datetime with timezone",
    ),
}

KNOWN_METADATA_FIELD_DEFINITIONS = {
    "dataset": MetadataFieldDefinition(description="Named source dataset used to group related documents.", value_type="string"),
    "dataset_version": MetadataFieldDefinition(description="Version of the source dataset.", value_type="string"),
    "note_number": MetadataFieldDefinition(description="Stable human reference for a note; use it when the answer requests notes.", value_type="string"),
    "phase": MetadataFieldDefinition(description="Dataset phase in which the note was introduced, such as baseline or incremental.", value_type="string"),
    "title": MetadataFieldDefinition(description="Human-readable title supplied for the document.", value_type="string"),
    "language": MetadataFieldDefinition(description="Language or locale of the document content.", value_type="string"),
    "author": MetadataFieldDefinition(description="Author or provenance label supplied by the dataset.", value_type="string"),
    "filename": MetadataFieldDefinition(description="Original uploaded filename when available.", value_type="string"),
    "format": MetadataFieldDefinition(description="Original document format when available.", value_type="string"),
}


def build_document_context(
    claims: list[SimilarClaim],
) -> tuple[list[ReflectionDocument], dict[str, MetadataFieldDefinition]]:
    """Return each retrieved document once, plus definitions for every included field."""
    documents: dict[str, ReflectionDocument] = {}
    metadata_keys: set[str] = set()
    for claim in claims:
        metadata_keys.update(claim.document_metadata)
        documents.setdefault(
            claim.document_id,
            ReflectionDocument(
                id=claim.document_id,
                source=claim.document_source,
                created_at=claim.document_created_at,
                metadata=claim.document_metadata,
            ),
        )
    definitions = dict(CORE_FIELD_DEFINITIONS)
    for key in sorted(metadata_keys):
        definitions[key] = KNOWN_METADATA_FIELD_DEFINITIONS.get(
            key,
            MetadataFieldDefinition(
                description="User-supplied document metadata. Interpret only its literal field name and value; do not infer an undocumented meaning.",
                value_type="string",
            ),
        )
    return list(documents.values()), definitions
