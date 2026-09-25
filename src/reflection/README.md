# Resolución reflexiva

La resolución responde una pregunta usando únicamente claims recuperados,
relaciones directas del grafo y la evidencia ya validada en la extracción.
No reemplaza el juicio de la persona ni diagnostica: propone una lectura
acotada, explicita incertidumbres y puede sugerir preguntas de seguimiento.

```text
pregunta → claims semánticos → relaciones del grafo → LLM estructurado → ReflectionRun
```

## Garantías actuales

- Cada observación debe incluir `source_claim_ids`.
- La aplicación rechaza una respuesta que cite un ID fuera de los candidatos
  recuperados.
- La evidencia retornada pertenece a los claims y documentos originales, no al
  texto generado por el LLM.
- Cada intento queda en `data/reflections/<run_id>.json`, con candidatos,
  relaciones, perfil, prompt, proveedor, modelo y uso.
- Si la recuperación no devuelve candidatos, no se invoca el LLM: se persiste
  una respuesta explícita de evidencia insuficiente.

El perfil `v1` es deliberadamente conservador. Cambiar instrucciones o contrato
requiere crear un perfil nuevo; las corridas existentes permanecen comparables.

## Uso

```bash
curl -X POST http://localhost:8000/resolve \
  -H 'content-type: application/json' \
  -d '{"question":"¿Qué tensiones aparecen alrededor de mi familia?", "limit":10}'
```

`OPENAI_REFLECTION_MODEL` permite elegir un modelo para la resolución distinto
de `OPENAI_MODEL`; si no se define, usa este último. `REFLECTION_PROVIDER` es
la frontera para incorporar un proveedor local posteriormente.
