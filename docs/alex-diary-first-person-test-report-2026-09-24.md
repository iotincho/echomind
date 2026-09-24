# Informe de resultados: diario sintético de Alex — preguntas en primera persona

**Fecha:** 2026-09-24  
**Plan:** [`alex-diary-test-plan.md`](alex-diary-test-plan.md), actualizado a primera persona  
**Resultado técnico:** 18/18 reflexiones completadas, sin errores HTTP. Al cierre, las 18 notas y sus 18 extracciones completadas están restauradas.

## Ejecución

- Se aisló la fase base: se eliminaron 16–18 por la API con su cascada de grafo, extracciones y embeddings; se ejecutaron 01–15; luego se recargaron 16–18 y se ejecutaron 16–18.
- Extractor: `v4`. Embeddings: `text-embedding-3-small`, 1536 dimensiones.
- Reflexión: perfil/prompt `v1`, proveedor `openai`, modelo `gpt-5.6-luna`.
- Estrategia: híbrida — recuperación vectorial de claims y contexto de relaciones Neo4j. Límite de 20 claims por reflexión y de 20 resultados para búsqueda mixta.
- Evidencia completa, incluyendo respuestas íntegras, UUID, notas recuperadas, claims citados y resultados vectoriales: [fase base](test-results/alex-diary-first-person-baseline.json) y [fase incremental](test-results/alex-diary-first-person-incremental.json).

## Resultado funcional

| Estado | Cantidad |
| --- | ---: |
| Aprobado | 9 |
| Parcial | 7 |
| Fallido | 2 |

| Test | Evidencia | Tiempo/relaciones | Interpretación | Inventó | Estado | Observación |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | Parcial | Sí | Parcial | No | Parcial | Recupera salario ~25 %, propuesta y flexibilidad, pero no el requisito de cuatro días de oficina ni una causa decisiva explícita. |
| 02 | No | N/A | No | No | Fallido | La respuesta visible quedó reducida al encabezado, aunque sí cita claims. No agrupa los temas pedidos. |
| 03 | Sí | Sí | Sí | No | Aprobado | Identifica autonomía, estabilidad, proyectos y dificultad para avanzar. |
| 04 | Sí | Sí | Sí | No | Aprobado | Explica estabilidad/autonomía, ideas/acción y planificación/experimentación con trazabilidad. |
| 05 | Sí | Parcial | Sí | No | Parcial | Reconstruye una evolución plausible, pero reconoce que no puede ordenar todas las notas por mes. |
| 06 | Sí | Sí | Sí | No | Aprobado | Mantiene el dinero como relevante y describe un equilibrio con autonomía. |
| 07 | Sí | Sí | Sí | No | Aprobado | Conecta trabajo, mudanza y proyectos por autonomía, sin inventar causalidad. |
| 08 | Sí | Parcial | Parcial | No | Parcial | Reconoce tensiones y niega contradicción lógica, pero no clasifica con precisión planificación/experimentación como cambio de enfoque. |
| 09 | Sí | Sí | Sí | No | Aprobado | Recupera entusiasmo, investigación, postergación, comienzo acotado y ajuste. |
| 10 | Sí | Sí | Sí | No | Aprobado | Presenta autonomía como hipótesis y conserva la incertidumbre. |
| 11 | Sí | Sí | Parcial | No | Parcial | Las citas están en el JSON, pero la respuesta visible no muestra números de nota ni fragmentos literales. |
| 12 | Sí | N/A | Sí | No | Aprobado | Declara correctamente ausencia del nombre de empresa. |
| 13 | Sí | Sí | Sí | No | Aprobado | Rechaza el diagnóstico y acota la inferencia a decisiones concretas. |
| 14 | Sí | Sí | Sí | No | Aprobado | En la fase base mantiene correctamente que la mudanza no estaba decidida. |
| 15 | Parcial | Sí | Parcial | No | Parcial | Matiza la frase, aunque conserva al dinero como motivo importante en vez de priorizar el giro hacia autonomía. |
| 16 | Parcial | Parcial | Parcial | No | Parcial | Ve una evolución del trabajo/emprendimiento, pero no recupera con seguridad la vía de empleo remoto mejor pago ni el orden enero–septiembre. |
| 17 | Sí | No | No | No | Fallido | Cita la mudanza de la nota 18, pero no la reconoce como estado actual y responde que depende de la fecha. |
| 18 | Parcial | Parcial | Parcial | No | Parcial | Recupera naturaleza y tranquilidad, pero no el contraste completo con extrañar amistades y construir comunidad. |

## Lectura del cambio a primera persona

La reformulación mejoró la calidad de varias respuestas interpretativas: los tests 04, 07, 09 y 13 presentan una voz coherente con las notas y límites explícitos de inferencia. No es una comparación estadística controlada contra la corrida anterior, porque la generación es no determinista. El test 02 evidencia que el perfil de reflexión aún necesita una regla de completitud: una respuesta estructuralmente válida puede ser semánticamente vacía.

## Comparación Vector RAG, Graph RAG e híbrido

El test 07 confirma que el modo híbrido recupera y cita las notas relevantes y formula la relación por autonomía sin inventar causalidad. La comparación solicitada no se pudo completar: el sistema expone búsqueda vectorial y reflexión híbrida, pero no una recuperación exclusivamente por grafo ni un selector de estrategia. Este apartado permanece **no ejecutable** hasta incorporar esos modos.

## Hallazgos accionables

1. Propagar `created_at` y `metadata.note_number` al contexto de reflexión, y pedir al modelo que priorice la evidencia más reciente. Resolvería 05, 16, 17 y 18.
2. Agregar una validación de completitud de la respuesta: listas solicitadas deben contener al menos un ítem con evidencia, para rechazar casos como el test 02.
3. Exigir en el perfil que la respuesta visible muestre nota y cita literal cuando la pregunta lo solicita. Resolvería el parcial del test 11.
4. Incorporar recuperación configurable `vector`, `graph` y `hybrid` para completar el experimento controlado del test 07.
