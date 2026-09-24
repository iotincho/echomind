# Informe de resultados: diario sintético de Alex — contexto con metadata estructurada

**Fecha:** 2026-09-24  
**Cambio evaluado:** metadata completa de documentos, definiciones de campos y `created_at` en el contexto de reflexión.  
**Resultado técnico:** 18/18 reflexiones completadas, sin errores HTTP. Las 18 notas y sus extracciones completadas quedaron restauradas al cierre.

## Configuración

- Se ejecutó la fase base 01–15 aislada; luego se recargaron 16–18 para la fase incremental.
- Extractor: `v4`. Embeddings: `text-embedding-3-small`, 1536 dimensiones.
- Reflexión: perfil/prompt `v1`, proveedor `openai`, modelo `gpt-5.6-luna`.
- Estrategia: recuperación vectorial de claims + relaciones de Neo4j. Se entregaron 20 claims como máximo.
- El contexto contiene por documento `id`, `source`, `created_at`, metadata completa y `metadata_definitions`. En particular, `created_at` se define como fecha en que se expresó la nota.
- Evidencia íntegra: [fase base](test-results/alex-diary-metadata-context-baseline.json) y [fase incremental](test-results/alex-diary-metadata-context-incremental.json).

## Resultado funcional

| Estado | Cantidad |
| --- | ---: |
| Aprobado | 12 |
| Parcial | 6 |
| Fallido | 0 |

| Test | Estado | Observación |
| --- | --- | --- |
| 01 | Parcial | Recupera propuesta, salario ~25 % y flexibilidad; sigue omitiendo el requisito de cuatro días en oficina. |
| 02 | Parcial | Agrupa autonomía, trabajo, proyectos, ejecución y estabilidad; residencia/naturaleza y vínculos aparecen con cobertura limitada. |
| 03 | Aprobado | Identifica autonomía, proyecto propio, estabilidad y dificultad para avanzar. |
| 04 | Aprobado | Explica estabilidad/autonomía, ideas/acción y planificación/experimentación con evidencia. |
| 05 | Aprobado | Reconstruye el pasaje de imaginar a construir, iterar y completar una segunda versión entre enero y julio. |
| 06 | Aprobado | Describe equilibrio entre dinero, estabilidad y autonomía sin negar el valor del dinero. |
| 07 | Aprobado | Conecta trabajo, mudanza y proyectos por autonomía, sin afirmar causalidad inexistente. |
| 08 | Parcial | Distingue que no hay contradicción lógica y aporta evolución temporal, pero no cubre todas las clasificaciones pedidas. |
| 09 | Aprobado | Recupera entusiasmo, investigación, postergación, reducción de alcance y ajuste. |
| 10 | Aprobado | Formula autonomía como hipótesis y preserva incertidumbre. |
| 11 | Parcial | Explica el sentido de autonomía, pero no muestra números de nota o citas literales en la respuesta visible. |
| 12 | Aprobado | Declara correctamente que no hay nombre de empresa. |
| 13 | Aprobado | Rechaza el diagnóstico y limita la lectura a decisiones concretas. |
| 14 | Aprobado | Para el corpus base, usa la fecha de 22 de julio y mantiene correctamente la incertidumbre. |
| 15 | Parcial | Matiza la relación entre dinero y renuncia, pero no prioriza con suficiente claridad el desplazamiento hacia autonomía. |
| 16 | Aprobado con salvedad | Reconoce empleo remoto como vía de autonomía y proyecto propio no obligatorio. Advierte correctamente que las notas 16–17 llegan a agosto; la evidencia de septiembre está en la nota 18, que este caso no solicita. |
| 17 | Aprobado | Corrige el fallo previo: usa la nota 18 como la más reciente y concluye que ya se mudó. |
| 18 | Parcial | Recupera expectativa de naturaleza/tranquilidad y mudanza, pero no el contraste completo con amistades y comunidad. |

## Efecto observado

Frente a la corrida anterior en primera persona, el resultado pasó de **9 aprobados, 7 parciales y 2 fallidos** a **12 aprobados, 6 parciales y 0 fallidos**.

La mejora temporal es concreta:

- Test 14 ahora identifica explícitamente que la última nota del corpus base es del 22 de julio.
- Test 16 ubica el cambio laboral de agosto y detecta de forma correcta que no tiene evidencia de septiembre dentro de su conjunto recuperado.
- Test 17 pasó de fallido a aprobado: contrasta julio con la nota más reciente de septiembre y concluye que la mudanza ya ocurrió.

La generación no es determinista, por lo que esta ejecución no prueba causalidad estadística por sí sola. Sin embargo, los cambios están alineados con la información nueva disponible: fechas, fase y referencias de documento en el contexto.

## Pendientes priorizados

1. Incluir recuperación por diversidad temporal o forzar la nota más reciente cuando la pregunta contiene “todavía”, “actualmente”, “finalmente” o un rango temporal. Esto cubriría mejor 16 y 18.
2. Ajustar la extracción de la nota 18 o la recuperación de sus claims para incorporar amistades y construcción de comunidad.
3. Agregar al perfil de reflexión una obligación de mostrar `note_number` y cita literal cuando la pregunta pide notas, para cerrar el test 11.
4. Agregar una estrategia seleccionable `vector`, `graph` y `hybrid` para completar el experimento controlado del test 07.
