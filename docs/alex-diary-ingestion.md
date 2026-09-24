# Carga del diario sintético de Alex

El script [`scripts/ingest_alex_diary.py`](../scripts/ingest_alex_diary.py) envía cada fixture JSON a `POST /documents`, preservando su `created_at`, UUID y metadatos. Las solicitudes son secuenciales y una falla detiene la corrida.

Primero verificar la selección sin tocar la API:

```bash
python scripts/ingest_alex_diary.py --dry-run
```

Con la API disponible y una sesión válida, cargar las 15 notas base:

```bash
python scripts/ingest_alex_diary.py --api-url http://localhost:8000 --cookie 'echomind_session=...'
```

Luego de ejecutar la primera batería de pruebas, incorporar solo las notas 16–18:

```bash
python scripts/ingest_alex_diary.py --phase incremental --cookie 'echomind_session=...'
```

El script acepta `--username` y `--password` como alternativa al cookie para iniciar sesión mediante `POST /auth/login`. Para repetir una carga interrumpida sin fallar por los UUID estables, usar `--skip-existing`. `--phase all` carga las 18 notas, pero evita ese modo si se quiere medir la actualización temporal de forma controlada.
