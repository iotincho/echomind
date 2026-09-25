# Persistencia en Neo4j

La fase de grafo persiste únicamente una extracción que ya fue validada contra el
contenido original. La escritura ocurre después de que el `ExtractionRun` se
guarda localmente; si Neo4j falla, el documento y la corrida siguen disponibles,
pero la API responde `503` con el `run_id` para permitir reintento y diagnóstico.

`Neo4jGraphStore` es un adaptador de infraestructura. Los casos de uso dependen
del puerto `GraphStore`, no del driver ni de Cypher.

## Modelo inicial

```text
(:Document)-[:HAS_EXTRACTION]->(:ExtractionRun)
(:ExtractionRun)-[:EXTRACTED]->(:Concept | :Entity | :Claim)
(:Concept | :Entity | :Claim)-[:SUPPORTED_BY]->(:Evidence)-[:FROM_DOCUMENT]->(:Document)
(:Claim)-[:ABOUT | :RELATES_TO | :SUPPORTS | :CONTRADICTS]->(:Concept | :Entity | :Claim)
```

Todos los nodos extraídos están acotados al `run_id`: por ahora `autonomía` de
dos corridas distintas son dos nodos distintos. La canonicalización entre
documentos es una decisión futura y no debe mezclarse con la fidelidad de la
extracción inicial.

`Evidence` conserva la cita literal y su posición calculada por el backend.
Las relaciones semánticas contienen `run_id`, `document_id` y `evidence_json`;
esto permite inspeccionar su respaldo sin perder que la arista nativa representa
la relación (`ABOUT`, por ejemplo).

## Idempotencia y restricciones

El adaptador usa `MERGE` con IDs estables y crea restricciones únicas para
`Document`, `ExtractionRun`, `Concept`, `Entity`, `Claim` y `Evidence`. Repetir
la escritura de una misma corrida no duplica el subgrafo.

## Inspección manual

Abrí Neo4j Browser en `http://localhost:7474` y ejecutá, por ejemplo:

```cypher
MATCH (document:Document)-[:HAS_EXTRACTION]->(run:ExtractionRun)
RETURN document.id, document.source, run.id, run.profile_name, run.model
ORDER BY run.created_at DESC;
```

```cypher
MATCH (claim:Claim)-[relationship:ABOUT]->(concept:Concept)
RETURN claim.text, concept.name, relationship.evidence_json;
```

```cypher
MATCH (item)-[:SUPPORTED_BY]->(evidence:Evidence)-[:FROM_DOCUMENT]->(document:Document)
RETURN labels(item), item.local_id, evidence.quote, evidence.start_line, document.id;
```
