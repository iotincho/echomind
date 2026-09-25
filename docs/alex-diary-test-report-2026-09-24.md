# Informe de resultados: diario sintético de Alex

**Fecha:** 2026-09-24  
**Plan ejecutado:** [`alex-diary-test-plan.md`](alex-diary-test-plan.md)  
**Resultado técnico:** 18/18 reflexiones completadas; API y Nginx saludables al cierre.

## Configuración y método

- Se ejecutó primero el corpus base (notas 01–15). Las notas 16–18 se eliminaron por la API, incluyendo su subgrafo, extracciones y embeddings, y luego se recargaron para la fase incremental.
- Extractor de las notas: perfil `v4`; embeddings `text-embedding-3-small`, 1536 dimensiones.
- Reflexiones: perfil/prompt `v1`, proveedor `openai`, modelo `gpt-5.6-luna`.
- Estrategia efectiva: **híbrida**. Recuperación vectorial de claims y contexto de relaciones desde Neo4j. Para prevenir bloqueos del proveedor, se usaron 20 claims por reflexión; la búsqueda mixta vectorial también usó límite 20.
- Los JSON de evidencia guardan la respuesta íntegra, candidatos, citas, UUID, documentos recuperados y resultados vectoriales: [fase base](test-results/alex-diary-baseline.json) y [fase incremental](test-results/alex-diary-incremental.json).

## Resumen de aceptación

| Estado | Cantidad |
| --- | ---: |
| Aprobado | 9 |
| Parcial | 8 |
| Fallido | 1 |

| Test | Evidencia | Tiempo/relaciones | Interpretación | Inventó | Estado | Observación |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | Parcial | Sí | Parcial | No | Parcial | Identifica rechazo por flexibilidad, pero omite 25 % y cuatro días de oficina. |
| 02 | Parcial | N/A | Parcial | No | Parcial | Recupera autonomía, proyectos y trabajo; residencia/naturaleza y vínculos quedan débiles. |
| 03 | Sí | Sí | Sí | No | Aprobado | Explica autonomía, estabilidad y dificultad para avanzar. |
| 04 | Sí | Sí | Sí | No | Aprobado | Distingue opciones/acción, estabilidad/autonomía y anticipación/experiencia. |
| 05 | Sí | Parcial | Parcial | No | Parcial | Ve la evolución de proyectos, pero no reconstruye la cronología enero–julio porque la fecha no llega al contexto. |
| 06 | Sí | Sí | Sí | No | Aprobado | Describe equilibrio entre dinero, estabilidad y autonomía sin negar el valor del dinero. |
| 07 | Sí | Sí | Sí | No | Aprobado | Vincula trabajo, mudanza y proyectos mediante autonomía, con límites explícitos. |
| 08 | Parcial | Parcial | Parcial | No | Parcial | Reconoce ambivalencias, pero no clasifica con claridad contradicción frente a cambio de enfoque. |
| 09 | Sí | Sí | Sí | No | Aprobado | Recupera entusiasmo, investigación, postergación, práctica y ajuste. |
| 10 | Sí | Sí | Sí | No | Aprobado | Formula autonomía como hipótesis y evita afirmar causalidad. |
| 11 | Sí | Sí | Parcial | No | Parcial | La trazabilidad de citas existe en el JSON, pero la respuesta no muestra números de nota ni fragmentos. |
| 12 | Sí | N/A | Sí | No | Aprobado | Declara correctamente que no hay nombre de empresa. |
| 13 | Sí | Sí | Sí | No | Aprobado | Rechaza el diagnóstico y describe indecisiones con cautela. |
| 14 | Sí | Sí | Sí | No | Aprobado | En el corpus base mantiene correctamente la incertidumbre sobre la mudanza. |
| 15 | Parcial | Sí | Parcial | No | Parcial | Matiza la afirmación, pero aún presenta el dinero como motivación importante en vez de priorizar el cambio hacia autonomía. |
| 16 | Parcial | Parcial | Parcial | No | Parcial | Ve una vía laboral más flexible, pero no reconstruye con seguridad empleo remoto mejor pago ni la secuencia enero–septiembre. |
| 17 | Sí | No | No | No | Fallido | Cita la nota 18 pero la trata como contradictoria; debía reconocer que el estado actual es que ya se mudó. |
| 18 | Parcial | Parcial | Parcial | No | Parcial | Recupera naturaleza y tranquilidad, pero omite extrañar amistades y la construcción de comunidad. |

## Experimento del test 07

La ruta vectorial mixta recuperó, entre sus primeros resultados, las notas 01, 05, 07, 09, 11, 12 y 15. La reflexión híbrida citó 01, 02, 04, 05, 07, 10, 11, 12 y 15 y produjo la conexión común de autonomía sin inventar causalidad.

No fue posible completar la comparación controlada **vector vs. graph vs. hybrid**: la aplicación expone búsqueda vectorial y reflexión híbrida, pero no un modo de recuperación exclusivamente por grafo ni un selector de estrategia. Por tanto, este apartado queda **no ejecutable** y no se debe interpretar el resultado híbrido como comparación de rendimiento.

## Hallazgos y próximos pasos

1. La fecha `created_at` y el orden temporal de las notas se conservan en documentos, pero no forman parte del contexto de claims entregado al modelo. Esto causa el fallo 17 y los parciales 05, 16 y 18.
2. El perfil de reflexión no fuerza que la respuesta visible incluya número de nota y cita literal, aunque la trazabilidad queda disponible en los candidatos y observaciones persistidos. Ajustarlo resolvería el parcial del test 11.
3. Con límite 20, las respuestas son estables y la API no queda bloqueada, pero algunas preguntas panorámicas pierden cobertura (01 y 02). Conviene recuperar por diversidad temporal/por documento, no sólo por similitud de claims.
4. Para cerrar la batería, incorporar estrategias `vector`, `graph` y `hybrid` configurables, propagar fecha y `note_number` al contexto de reflexión y repetir los tests 01, 02, 05, 08, 11, 15–18.
