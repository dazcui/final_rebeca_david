# Proyectos adaptados al manual de mantenimiento preventivo

Los dos proyectos consultan exclusivamente `MANUAL_PROGRAMA_MANTENIMIENTO_PREVENTIVO.md`, de (SGT-800 y SST-400). El ejemplo sobre RAG se conserva fuera de la carpeta de ingesta, en `data/ejemplos` del proyecto 1.

## Abrir las interfaces

Desde esta carpeta, en PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\ejecutar-proyecto-1.ps1
powershell -ExecutionPolicy Bypass -File .\ejecutar-proyecto-2.ps1
```

Ejecutar cada comando en una terminal distinta. Proyecto 1: http://127.0.0.1:8501 (fragmentos del manual). Proyecto 2: http://127.0.0.1:8502 (respuestas generadas y fuentes). Detener cada servidor con Ctrl+C.

## Reconstruir las bases al actualizar el manual

En la carpeta interna de cada proyecto, usar su propio entorno virtual:

```powershell
# Proyecto 1
.venv\Scripts\python.exe -m src.ingest --reset
.venv\Scripts\python.exe -m src.query "¿Qué diferencia hay entre Offshore y Onshore?"

# Proyecto 2
.venv\Scripts\python.exe cli.py ingest --reset
.venv\Scripts\python.exe cli.py ask "¿Qué intervención está prevista para WAR42 en 2027?"
```

Antes de estos comandos, definir la caché compartida con una ruta absoluta a `.cache/huggingface` dentro de esta carpeta:

```powershell
$env:HF_HOME = 'C:\Users\Usuario\Desktop\TrabFin ModII\.cache\huggingface'
$env:PYTHONUTF8 = '1'
```

El modelo de embeddings es `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, multilingüe y ejecutado localmente. El proyecto 2 usa Ollama con `llama3.2:3b`. Ollama debe estar en ejecución. Sin generación, consultar con `cli.py ask "pregunta" --no-generate`.

## Preguntas y evidencia

Las ocho preguntas están en `preguntas_manual.json`. En cada proyecto ejecutar `.venv\Scripts\python.exe consultas_manual.py` para registrar fragmentos y, en el segundo, respuestas. Los resultados se guardan en la carpeta `resultados` de este directorio.

Se incluyen preguntas sobre tiempos de inspección, contratos, hitos EOH/EOC, SST-400, WAR42, colores de cronograma, ensayos NDT y confiabilidad. El manual no especifica una fórmula de cálculo para el 96,89 %: las respuestas deben respetar esa ausencia de datos.
