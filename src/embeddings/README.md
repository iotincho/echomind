# Embeddings de claims

Esta fase hace recuperable semánticamente cada `Claim` extraído y validado. No
interpreta ni agrupa automáticamente el material: devuelve candidatos para que
el grafo, las fechas y la evidencia permitan revisar si existe un patrón real.

## Decisión actual

La unidad embebida es `Claim.text`, no el documento completo ni los conceptos.
Una búsqueda semántica debería encontrar afirmaciones cercanas de distintas
notas; desde cada claim se llega al documento y a su evidencia original.

```text
(:Claim)-[:HAS_EMBEDDING]->(:ClaimEmbedding)
(:Claim)-[:SUPPORTED_BY]->(:Evidence)-[:FROM_DOCUMENT]->(:Document)
```

`ClaimEmbedding` conserva `run_id`, `profile_name`, `prompt_version`, proveedor,
modelo, dimensiones y el hash del texto. Por eso una variante futura del
extractor no se mezcla silenciosamente con claims producidos por otro perfil.

## Conceptos: decisión pendiente

Los conceptos no reciben embeddings en esta fase. Sus nombres suelen ser cortos y todavía no existe una estrategia validada para determinar cuándo conceptos de dos corridas representan la misma idea. Relacionarlos y canonicalizarlos es una decisión central pendiente; debe evaluarse explícitamente antes de crear nodos globales o fusionar `Concept` entre documentos.

## Índices separados por modelo

Neo4j crea una etiqueta e índice vectorial específicos para cada combinación de
proveedor, modelo y dimensiones. Así, cambiar de modelo no compara vectores
incompatibles. Los vectores anteriores permanecen auditables con sus metadatos.

## Uso

Al completar una carga, el flujo es:

```text
ingesta → extracción → persistencia de grafo → embeddings de claims
```

Para buscar, enviá una consulta semántica sin LLM generativo:

```bash
curl -X POST http://localhost:8000/search/claims \
  -H 'content-type: application/json' \
  -d '{"query":"preocupación por perder libertad", "limit": 10}'
```

La respuesta contiene `score`, claim, versión de extracción y evidencias. Un
score no prueba un patrón: solo ordena material potencialmente relacionado.

La implementación OpenAI usa el endpoint de embeddings y `text-embedding-3-small`
con 1536 dimensiones por defecto. Consultá la [guía de embeddings de OpenAI](https://developers.openai.com/api/docs/guides/embeddings).
