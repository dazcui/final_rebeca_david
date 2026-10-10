# Validación de ejecución

- Python 3.12.15 instalado en `.runtime`; un entorno `.venv` por proyecto.
- Dependencias instaladas; versiones conservadas en `requirements-lock.txt` de cada proyecto.
- Embeddings multilingües reales: 384 dimensiones, modelo descargado en la caché compartida.
- Modelo Ollama `llama3.2:3b` descargado y generación comprobada en CPU.
- Proyecto 1: 58 fragmentos del manual, ocho consultas ejecutadas; interfaz comprobada mediante Streamlit AppTest, incluida una búsqueda con cinco resultados.
- Proyecto 2: 57 fragmentos del manual, ocho preguntas con generación local. La consulta HGP se repitió tras corregir la recuperación de la definición y la tabla EOH/EOC; la respuesta validada reemplaza la anterior en el JSON.
- Suite existente del proyecto 2: 26 pruebas aprobadas. Se corrigió la liberación de archivos temporales HNSW en Windows cerrando el cliente Chroma.
- Interfaz del proyecto 2: carga y selector de preguntas comprobados con Streamlit AppTest.
- Ambos servidores: respuesta HTTP 200 y estado `ok` en `/_stcore/health`.
- Comparación para WAR42: 4 fragmentos recuperados, 57 en el corpus; 865 tokens en RAG frente a 6.903 en contexto largo; ahorro del 87,5 % para esta consulta y configuración.

El documento `PREGUNTAS_Y_RESPUESTAS_VERIFICADAS.md` contiene respuestas contrastadas directamente con el manual. Los JSON conservan respuestas del modelo y evidencia recuperada; algunas respuestas del modelo son más breves que el detalle disponible en la fuente.
