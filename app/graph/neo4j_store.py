"""Neo4j adapter for the evidence-backed extraction graph."""

import json
from typing import Any

from app.domain.documents import Document
from app.extraction.contracts import ExtractionResult
from app.services.extraction_store import ExtractionRun
from app.services.graph_store import GraphPersistenceError, GraphStore


class Neo4jGraphStore(GraphStore):
    """Persist each immutable extraction run without canonicalizing knowledge yet."""

    def __init__(self, uri: str, username: str, password: str, driver: Any | None = None) -> None:
        self._uri = uri
        self._username = username
        self._password = password
        self._driver = driver
        self._schema_initialized = False

    def persist(self, document: Document, extraction: ExtractionRun) -> None:
        if extraction.status != "completed" or extraction.result is None:
            raise GraphPersistenceError("Only completed extractions can be persisted in Neo4j")

        driver = self._get_driver()
        try:
            with driver.session() as session:
                self._initialize_schema(session)
                session.execute_write(self._write_extraction, document, extraction)
        except GraphPersistenceError:
            raise
        except Exception as error:
            raise GraphPersistenceError("Neo4j graph persistence failed") from error

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()

    def _get_driver(self) -> Any:
        if self._driver is None:
            from neo4j import GraphDatabase

            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._username, self._password),
            )
        return self._driver

    def _initialize_schema(self, session: Any) -> None:
        if self._schema_initialized:
            return
        for query in (
            (
                "CREATE CONSTRAINT document_id IF NOT EXISTS "
                "FOR (node:Document) REQUIRE node.id IS UNIQUE"
            ),
            (
                "CREATE CONSTRAINT extraction_run_id IF NOT EXISTS "
                "FOR (node:ExtractionRun) REQUIRE node.id IS UNIQUE"
            ),
            (
                "CREATE CONSTRAINT concept_id IF NOT EXISTS "
                "FOR (node:Concept) REQUIRE node.id IS UNIQUE"
            ),
            (
                "CREATE CONSTRAINT entity_id IF NOT EXISTS "
                "FOR (node:Entity) REQUIRE node.id IS UNIQUE"
            ),
            (
                "CREATE CONSTRAINT claim_id IF NOT EXISTS "
                "FOR (node:Claim) REQUIRE node.id IS UNIQUE"
            ),
            (
                "CREATE CONSTRAINT evidence_id IF NOT EXISTS "
                "FOR (node:Evidence) REQUIRE node.id IS UNIQUE"
            ),
        ):
            session.run(query).consume()
        self._schema_initialized = True

    @staticmethod
    def _write_extraction(transaction: Any, document: Document, extraction: ExtractionRun) -> None:
        result = extraction.result
        assert result is not None
        document_id = str(document.id)
        run_id = str(extraction.id)
        transaction.run(
            """
            MERGE (document:Document {id: $id})
            SET document.source = $source,
                document.metadata_json = $metadata_json,
                document.created_at = $created_at
            MERGE (run:ExtractionRun {id: $run_id})
            SET run.document_id = $document_id,
                run.profile_name = $profile_name,
                run.schema_version = $schema_version,
                run.prompt_version = $prompt_version,
                run.provider = $provider,
                run.model = $model,
                run.created_at = $run_created_at
            MERGE (document)-[:HAS_EXTRACTION]->(run)
            """,
            id=document_id,
            source=document.source,
            metadata_json=json.dumps(document.metadata, ensure_ascii=False, sort_keys=True),
            created_at=document.created_at.isoformat(),
            run_id=run_id,
            document_id=document_id,
            profile_name=extraction.profile_name,
            schema_version=extraction.schema_version,
            prompt_version=extraction.prompt_version,
            provider=extraction.provider,
            model=extraction.model,
            run_created_at=extraction.created_at.isoformat(),
        )
        Neo4jGraphStore._write_items(transaction, "Concept", result.concepts, run_id, document_id)
        Neo4jGraphStore._write_items(transaction, "Entity", result.entities, run_id, document_id)
        Neo4jGraphStore._write_items(transaction, "Claim", result.claims, run_id, document_id)
        Neo4jGraphStore._write_relationships(transaction, result, run_id, document_id)

    @staticmethod
    def _write_items(
        transaction: Any,
        label: str,
        items: list[Any],
        run_id: str,
        document_id: str,
    ) -> None:
        rows = []
        evidence_rows = []
        for item in items:
            item_id = f"{run_id}:{label.lower()}:{item.id}"
            row = {
                "id": item_id,
                "local_id": item.id,
                "run_id": run_id,
                "document_id": document_id,
                "name": getattr(item, "name", None),
                "text": getattr(item, "text", None),
                "type": getattr(item, "type", None),
            }
            rows.append(row)
            for index, evidence in enumerate(item.evidence):
                evidence_rows.append(
                    Neo4jGraphStore._evidence_row(
                        f"{item_id}:evidence:{index}",
                        item_id,
                        evidence,
                        run_id,
                        document_id,
                    )
                )

        if rows:
            transaction.run(
                f"""
                UNWIND $rows AS row
                MERGE (item:{label} {{id: row.id}})
                SET item.local_id = row.local_id,
                    item.run_id = row.run_id,
                    item.document_id = row.document_id,
                    item.name = row.name,
                    item.text = row.text,
                    item.type = row.type
                WITH item, row
                MATCH (run:ExtractionRun {{id: row.run_id}})
                MERGE (run)-[:EXTRACTED]->(item)
                """,
                rows=rows,
            )
        Neo4jGraphStore._write_evidence(transaction, evidence_rows)

    @staticmethod
    def _write_relationships(
        transaction: Any,
        result: ExtractionResult,
        run_id: str,
        document_id: str,
    ) -> None:
        rows_by_type: dict[str, list[dict[str, Any]]] = {}
        for index, relationship in enumerate(result.relationships):
            relation_type = relationship.type.value
            rows_by_type.setdefault(relation_type, []).append(
                {
                    "id": f"{run_id}:relationship:{index}",
                    "run_id": run_id,
                    "document_id": document_id,
                    "source_id": f"{run_id}:{relationship.source.kind}:{relationship.source.id}",
                    "target_id": f"{run_id}:{relationship.target.kind}:{relationship.target.id}",
                    "evidence_json": json.dumps(
                        [evidence.model_dump() for evidence in relationship.evidence],
                        ensure_ascii=False,
                    ),
                }
            )

        for relation_type, rows in rows_by_type.items():
            transaction.run(
                f"""
                UNWIND $rows AS row
                MATCH (source {{id: row.source_id}}), (target {{id: row.target_id}})
                MERGE (source)-[relationship:{relation_type} {{id: row.id}}]->(target)
                SET relationship.run_id = row.run_id,
                    relationship.document_id = row.document_id,
                    relationship.evidence_json = row.evidence_json
                """,
                rows=rows,
            )

    @staticmethod
    def _evidence_row(
        evidence_id: str,
        owner_id: str,
        evidence: Any,
        run_id: str,
        document_id: str,
    ) -> dict[str, Any]:
        return {
            "id": evidence_id,
            "owner_id": owner_id,
            "run_id": run_id,
            "document_id": document_id,
            "quote": evidence.quote,
            "start_char": evidence.start_char,
            "end_char": evidence.end_char,
            "start_line": evidence.start_line,
            "end_line": evidence.end_line,
        }

    @staticmethod
    def _write_evidence(transaction: Any, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        transaction.run(
            """
            UNWIND $rows AS row
            MERGE (evidence:Evidence {id: row.id})
            SET evidence.run_id = row.run_id,
                evidence.document_id = row.document_id,
                evidence.quote = row.quote,
                evidence.start_char = row.start_char,
                evidence.end_char = row.end_char,
                evidence.start_line = row.start_line,
                evidence.end_line = row.end_line
            WITH evidence, row
            MATCH (item {id: row.owner_id}), (document:Document {id: row.document_id})
            MERGE (item)-[:SUPPORTED_BY]->(evidence)
            MERGE (evidence)-[:FROM_DOCUMENT]->(document)
            """,
            rows=rows,
        )
