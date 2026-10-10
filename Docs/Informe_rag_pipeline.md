# Informe del sistema RAG aplicado al mantenimiento preventivo

**Proyecto:** `rag-knowledge-pipeline`  
**Fuente aplicada:** Manual del Programa de Mantenimiento Preventivo de turbinas SGT-800 y SST-400  
**Fecha de documentación:** 10 de octubre de 2026  
**Entorno:** Windows, Python 3.12.15, Chroma y Ollama local

## 1. Introducción

Este proyecto permite formular preguntas sobre el Manual del Programa de Mantenimiento Preventivo y recibir respuestas preparadas con información recuperada de ese documento. Primero lee y limpia el texto, después lo divide y guarda sus vectores. Para cada pregunta, busca fragmentos relacionados, construye un contexto y lo envía a un modelo de lenguaje ejecutado con Ollama.

La aplicación incluye un chat y un panel de fuentes para revisar el contenido utilizado en la respuesta. Su objetivo es apoyar la consulta documental de inspecciones, contratos, cronogramas y datos de confiabilidad. El manual utilizado no se convierte en un procedimiento operativo nuevo mediante este sistema.

La adaptación realizada reemplaza los ejemplos generales por el manual, ajusta la fragmentación, añade preguntas del mantenimiento y refuerza el tratamiento de siglas y unidades. Este informe documenta los archivos, los pasos de ejecución y el consumo real de los modelos.

## 2. Objetivos

### 2.1. Objetivo general

Implementar y documentar un sistema RAG local que responda preguntas sobre mantenimiento preventivo utilizando información recuperada del manual y fuentes que puedan revisarse.

### 2.2. Objetivos específicos

1. Preparar un entorno de Python propio para el proyecto.
2. Extraer, limpiar y dividir el manual con datos de origen.
3. Generar vectores y guardarlos en una base local.
4. Combinar la búsqueda por significado con la búsqueda por palabras.
5. Construir el contexto e instrucciones para el modelo generativo.
6. Ejecutar la generación mediante Ollama sin una API de pago.
7. Mostrar las respuestas y sus fragmentos de apoyo en un chat.
8. Comprobar las pruebas, los resultados y el consumo de recursos.

## 3. Marco Teórico

### 3.1. Sistema RAG

RAG utiliza información recuperada para preparar una respuesta. En esta implementación, la recuperación selecciona fragmentos; la preparación del contexto añade instrucciones y la pregunta; y la generación produce texto a partir de esos datos. El modelo generativo recibe los fragmentos seleccionados, no consulta directamente la base Chroma.

### 3.2. Extracción, limpieza y fragmentación

La extracción obtiene texto de archivos PDF, HTML o Markdown. La limpieza corrige caracteres, quita marcas de formato, organiza espacios y elimina repeticiones exactas. La fragmentación divide el texto para procesarlo y recuperarlo en partes. Cada fragmento conserva el nombre del archivo, su tipo y la página cuando la fuente es un PDF.

El manual aplicado está en Markdown. Por ello, sus fragmentos no tienen números de página de PDF. Los números de fragmento que aparecen en el contexto son identificadores de la consulta, no números de sección del manual.

### 3.3. Vectores y búsqueda híbrida

El modelo de embeddings convierte texto en listas de 384 números. La comparación por vectores permite encontrar textos relacionados aunque la pregunta no repita todas las palabras del manual. La normalización ajusta la longitud numérica del vector para facilitar esa comparación. La búsqueda por palabras utiliza BM25, un método que da prioridad a términos presentes en los documentos.

La búsqueda híbrida combina ambos puntajes. En este proyecto el peso de la búsqueda por vectores es 0,6 y el de la búsqueda por palabras es 0,4. Los resultados se ordenan por el puntaje combinado. Ese puntaje no equivale a una probabilidad de respuesta correcta.

### 3.4. Recuperación iterativa

El modo llamado Agentic RAG en el código revisa el puntaje promedio de los resultados. Si es menor que el umbral, aumenta la cantidad de fragmentos y repite la búsqueda. Esta implementación permite hasta dos rondas y aumenta `top_k` en dos. No ejecuta órdenes de mantenimiento ni transforma la pregunta mediante otro modelo.

### 3.5. Contexto, tokens y generación local

El contexto es el texto seleccionado para que el modelo pueda responder. Un token es una unidad de texto que el modelo procesa; no siempre corresponde a una palabra completa. Un contexto más largo requiere más trabajo de procesamiento.

Ollama ejecuta el modelo generativo en el equipo. La aplicación utiliza `llama3.2:3b`. La temperatura configurada en cero reduce la variación entre respuestas, pero no garantiza exactitud. El límite de salida es de 300 tokens. Los modelos no se entrenaron ni se ajustaron con el manual.

## 4. Implementación Aplicada
### 4.1. Entorno de trabajo en Visual Studio Code

El directorio de trabajo es `C:\Users\Usuario\Desktop\TrabFin ModII`. En Visual Studio Code se debe seleccionar **Archivo > Abrir carpeta** y abrir este directorio. El proyecto de este informe se encuentra en `rag-knowledge-pipeline (1)\rag-knowledge-pipeline`. La carpeta exterior contiene la carpeta interna del proyecto; los comandos deben ejecutarse en la carpeta interna, donde está el archivo de configuración.

Los archivos se modificaron y las aplicaciones se ejecutaron mediante herramientas de archivos y PowerShell. Esta sección documenta cómo revisar y reproducir ese trabajo en Visual Studio Code. Las imágenes del código son vistas documentales de archivos reales; no se presentan como capturas nativas del editor. Las imágenes de la aplicación sí corresponden a su ejecución real en un navegador de prueba.

Para revisar el código, abrir el archivo desde el panel **Explorador**. Usar **Ctrl+G** para ir a la línea indicada en cada evidencia. Para ejecutar los comandos, abrir **Terminal > Nueva terminal**. Para revisar este informe con sus imágenes, abrir `Docs/Informe.md` y usar **Ctrl+Shift+V**.

El equipo tenía Python 3.14. Se instaló Python 3.12.15 en `.runtime`, dentro del directorio de trabajo, para usar una versión compatible con las dependencias. Cada proyecto tiene su propio entorno `.venv`. Desde la raíz del trabajo, la instalación realizada se puede reproducir con:

```powershell
python -m pip install --target .tools uv
$env:UV_PYTHON_INSTALL_DIR = Join-Path $PWD '.runtime'
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
& '.tools/bin/uv.exe' python install 3.12
& '.tools/bin/uv.exe' venv --python '.runtime/cpython-3.12.15-windows-x86_64-none/python.exe' 'rag-knowledge-pipeline (1)\rag-knowledge-pipeline/.venv'
& '.tools/bin/uv.exe' pip install --python 'rag-knowledge-pipeline (1)\rag-knowledge-pipeline/.venv/Scripts/python.exe' -r 'rag-knowledge-pipeline (1)\rag-knowledge-pipeline/requirements-lock.txt'
```

`uv` es la herramienta utilizada para instalar Python y las bibliotecas. `requirements.txt` establece las dependencias admitidas. `requirements-lock.txt` registra las versiones instaladas. La primera instalación necesita conexión a Internet.

En Visual Studio Code, abrir **Ctrl+Shift+P > Python: Select Interpreter** y seleccionar el archivo `.venv\Scripts\python.exe` de este proyecto. Esta opción requiere la extensión Python del editor. Si la extensión no está disponible, los comandos siguientes siguen indicando de forma expresa el archivo de Python que deben utilizar.

Antes de ejecutar las consultas, ubicar la terminal en la carpeta del proyecto y definir la ubicación del modelo descargado:

```powershell
Set-Location 'C:\Users\Usuario\Desktop\TrabFin ModII\rag-knowledge-pipeline (1)\rag-knowledge-pipeline'
$env:HF_HOME = 'C:\Users\Usuario\Desktop\TrabFin ModII\.cache\huggingface'
$env:HF_HUB_OFFLINE = '1'
$env:PYTHONUTF8 = '1'
```

El modo sin conexión indicado funciona porque el modelo ya fue descargado. Para una primera descarga se debe quitar esa variable con `Remove-Item Env:HF_HUB_OFFLINE -ErrorAction SilentlyContinue`. Esta instrucción elimina la variable de la terminal, no archivos del proyecto.

Las bibliotecas principales instaladas fueron Sentence Transformers 6.1.0, PyTorch 2.14.1, Chroma 1.5.9 y Streamlit 1.65.0. Las versiones exactas y las demás dependencias están en [requirements-lock.txt](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/requirements-lock.txt).

### 4.2. Organización y cambios realizados

| Archivo o carpeta | Función aplicada |
|---|---|
| `data/raw/` | Contiene el manual utilizado como fuente. |
| `config/settings.py` | Define rutas, fragmentación, búsqueda y modelos. |
| `ingestion/extractors.py` | Extrae texto y datos de origen. |
| `ingestion/cleaners.py` | Corrige y limpia el contenido. |
| `ingestion/pipeline.py` | Ejecuta las cuatro etapas de ingesta. |
| `rag/chunking.py` | Divide el texto limpio y agrega solapamiento. |
| `rag/embeddings.py` | Carga el modelo multilingüe y calcula vectores. |
| `rag/vector_store.py` | Guarda, consulta y enumera fragmentos en Chroma. |
| `rag/retriever.py` | Implementa búsqueda semántica, por palabras, híbrida e iterativa. |
| `rag/augmentation.py` | Construye instrucciones, contexto y pregunta. |
| `rag/generator.py` | Llama al modelo mediante el cliente Ollama. |
| `cli.py` | Proporciona los comandos ingest, ask y compare. |
| `app/streamlit_app.py` | Presenta el chat, configuración y fuentes. |
| `consultas_manual.py` | Ejecuta las ocho preguntas y guarda respuestas y fragmentos. |
| `tests/` | Comprueba limpieza, fragmentación, contexto, base y búsqueda. |

La colección se cambió a `manual_mantenimiento_preventivo`. Las rutas se resolvieron desde el archivo de configuración para no depender del lugar desde el que se abre el editor. Se usa un tamaño de 500 caracteres con 80 de solapamiento. El modelo de generación se fijó en `llama3.2:3b`, con temperatura cero. Referencia: [config/settings.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/config/settings.py), líneas 16–55.

Se añadieron las preguntas sugeridas del manual, el registro de consultas, el acceso de ejecución y las instrucciones para responder sobre SGT-800 y SST-400. Se corrigió el uso de `OLLAMA_HOST` creando un cliente explícito con ese valor y un tiempo máximo de espera de 180 segundos. Referencia: [rag/generator.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/generator.py), líneas 21–44.

En las pruebas se detectó un bloqueo de archivos temporales de la base Chroma en Windows. Se corrigió el cierre del cliente Chroma en la preparación de pruebas. Referencia: [tests/conftest.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/tests/conftest.py), líneas 40–49.

Durante la comprobación se observaron respuestas incorrectas o incompletas al desarrollar HGP. Se añadió un conjunto de definiciones del manual y una búsqueda adicional para incluir la definición junto con los principales datos recuperados por la pregunta original. Las instrucciones del generador también separan EOH de EOC. Estas medidas mejoran el contexto y las reglas, pero la respuesta debe seguir revisándose. Referencia: [rag/retriever.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/retriever.py), líneas 25–36, [rag/retriever.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/retriever.py), líneas 104–116 y [rag/generator.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/generator.py), líneas 28–42.

### 4.3. Funcionamiento paso a paso

1. **Extraer el documento.** `extract_directory` revisa archivos admitidos y aplica el lector correspondiente. Para Markdown se conserva el texto y se simplifican enlaces. Referencia: [ingestion/extractors.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/ingestion/extractors.py), líneas 70–108.
2. **Limpiar el texto.** `clean_corpus` aplica corrección de caracteres, eliminación de marcas, orden de espacios y eliminación de párrafos repetidos. Referencia: [ingestion/cleaners.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/ingestion/cleaners.py), líneas 124–142.
3. **Dividir el contenido.** `chunk_documents` crea fragmentos con identificadores y datos de origen. La función agrega al siguiente fragmento hasta 80 caracteres del anterior. El tamaño final puede superar los 500 caracteres nominales por ese agregado. Referencia: [rag/chunking.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/chunking.py), líneas 66–104.
4. **Crear los vectores.** `get_embedding_model` carga el modelo una vez y `embed_texts` obtiene vectores normalizados. Referencia: [rag/embeddings.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/embeddings.py), líneas 15–36.
5. **Guardar los fragmentos.** Chroma conserva identificador, vector, texto, fuente, página y tipo de documento. Referencia: [rag/vector_store.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/vector_store.py), líneas 23–42.
6. **Recibir la pregunta.** La terminal o el chat obtiene la pregunta y la cantidad de resultados. Referencia: [cli.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/cli.py), líneas 25–43 y [app/streamlit_app.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/app/streamlit_app.py), líneas 57–73.
7. **Recuperar información.** El buscador combina vectores y BM25. Si hay una sigla conocida, recupera también su definición. Si está activo el modo iterativo, revisa la evidencia y puede repetir con más resultados. Referencia: [rag/retriever.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/retriever.py), líneas 84–156.
8. **Preparar el contexto.** Se escriben instrucciones, fragmentos con fuentes y la pregunta. Referencia: [rag/augmentation.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/augmentation.py), líneas 25–46.
9. **Generar la respuesta.** El cliente Ollama recibe un mensaje de sistema y el contexto como mensaje de usuario. El modelo devuelve texto, que la aplicación presenta en pantalla. Referencia: [rag/generator.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/generator.py), líneas 21–44.
10. **Conservar el historial.** El chat guarda las preguntas y respuestas en la sesión del navegador. Los fragmentos aparecen en un panel separado. El historial de la interfaz no sustituye el archivo JSON de las consultas de prueba. Referencia: [app/streamlit_app.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/app/streamlit_app.py), líneas 50–55 y [app/streamlit_app.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/app/streamlit_app.py), líneas 87–107.

Si Ollama no puede responder, la interfaz muestra un mensaje y fragmentos recuperados. La terminal también dispone del argumento `--no-generate`, que permite consultar y revisar el contexto sin llamar al modelo generativo. Referencia: [cli.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/cli.py), líneas 50–64.

### 4.4. Ejecución en la terminal de Visual Studio Code

Ollama ya estaba instalado en el equipo. Se descargó el modelo con:

```powershell
ollama pull llama3.2:3b
ollama list
```

Ollama debe estar en ejecución en `http://localhost:11434`. Si no se encuentra activo, se puede iniciar con `ollama serve` en otra terminal. Desde la carpeta interna del proyecto, los comandos principales son:

```powershell
& '.venv/Scripts/python.exe' cli.py ingest --reset
& '.venv/Scripts/python.exe' cli.py ask '¿Qué significa HGP y en qué hitos EOH y EOC está previsto?' --top-k 5
& '.venv/Scripts/python.exe' cli.py ask '¿Qué intervención está prevista para WAR42 en 2027?' --agentic
& '.venv/Scripts/python.exe' cli.py ask '¿Qué incluye el contrato Onshore?' --no-generate
& '.venv/Scripts/python.exe' cli.py compare '¿Qué intervención está prevista para WAR42 en 2027?'
& '.venv/Scripts/python.exe' -m pytest -q
```

El argumento `--reset` reemplaza la colección seleccionada. En la comprobación de este informe se estableció `VECTOR_DB_DIR` en `Docs/evidencias/base_validacion` antes de ejecutar la ingesta. Así se registró una base separada sin reemplazar la de la aplicación abierta. Al quitar esa variable, el programa vuelve a la ruta configurada para la base activa.

Los registros reales están en [ingesta.txt](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/evidencias/ingesta.txt), [consulta_sin_generacion.txt](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/evidencias/consulta_sin_generacion.txt) y [pruebas.txt](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/evidencias/pruebas.txt). Para repetir las ocho preguntas, ejecutar `.venv\Scripts\python.exe consultas_manual.py`. La lista está en [preguntas_manual.json](../preguntas_manual.json) y los resultados generales en [proyecto_2_respuestas.json](../resultados/proyecto_2_respuestas.json).

### 4.5. Ejecución y uso de la aplicación web

Desde la carpeta del proyecto:

```powershell
& '.venv/Scripts/python.exe' -m streamlit run app/streamlit_app.py --server.port 8502 --server.address 127.0.0.1 --browser.gatherUsageStats false
```

El acceso [ejecutar-proyecto-2.ps1](../ejecutar-proyecto-2.ps1) de la raíz del trabajo prepara la carpeta y la caché antes de iniciar Streamlit. La aplicación se abre en `http://127.0.0.1:8502`. Si ya hay una instancia abierta en ese puerto, se usa esa instancia.

El panel lateral permite activar o desactivar el modo iterativo y cambiar la cantidad de fragmentos. La persona elige una pregunta sugerida y pulsa **Consultar pregunta sugerida**, o escribe una pregunta en el campo de chat y la envía con Enter. El programa recupera el contexto, genera la respuesta y muestra el texto final. El panel de fuentes permite revisar fragmentos y puntajes.

La base y el buscador se conservan mediante `st.cache_resource`. El modelo de vectores también se guarda en memoria con `lru_cache`. Si se reconstruye la colección mientras la aplicación está abierta, se debe reiniciar la aplicación para actualizar el índice de palabras que el buscador mantiene en memoria.
### 4.6. Consumo de los modelos de IA

Los modelos se ejecutan localmente. El modelo de vectores se descarga una vez desde Hugging Face y se reutiliza desde `.cache/huggingface`. La consulta y la ingesta consumen tiempo de CPU, memoria RAM y espacio en disco. En esta ejecución no se usó una API de pago ni se enviaron preguntas a un servicio externo de generación.

La medición se realizó el **10 de octubre de 2026**, con horario de Bolivia. Se utilizó la pregunta «¿Qué significa HGP y en qué hitos EOH y EOC está previsto?». Los tiempos corresponden al estado del equipo en esa ejecución. La carga del modelo incluye la importación de sus bibliotecas. La memoria indicada corresponde al proceso Python completo, no solamente a los pesos del modelo.

| Medida | Resultado registrado |
|---|---|
| Modelo de vectores | paraphrase-multilingual-MiniLM-L12-v2 |
| Dimensión de cada vector | 384 |
| Carga del modelo y sus bibliotecas | 11,49 s |
| Memoria de Python con el modelo cargado | 1.205,7 MiB |
| Memoria máxima de Python durante la medición | 1.471,3 MiB |
| Fragmentos de la base activa | 57 |
| Fragmentos de la consulta medida | 5 |
| Recuperación con el modelo ya cargado | 0,108 s |
| Modelo generativo | llama3.2:3b |
| Tiempo de la llamada de generación | 41,15 s |
| Tokens de entrada informados por Ollama | 1286 |
| Tokens generados informados por Ollama | 52 |
| Velocidad durante la generación de tokens | 8,90 tokens/s |
| Límite configurado de salida | 300 tokens |
| Temperatura | 0.0 |
| Tamaño del modelo cargado informado por Ollama | 2,39 GiB |
| Memoria GPU informada por Ollama | 0 bytes |
| Ventana de contexto informada por Ollama | 4096 tokens |

La suma del tamaño de los archivos de la caché de Hugging Face fue de **457,5 MiB**. Esta cifra corresponde a los archivos guardados en la caché, incluidos los archivos de configuración; no mide solamente los pesos ni todo el espacio ocupado por Python y sus dependencias. Las dimensiones y tiempos se registraron sin modificar el código de los modelos ni entrenarlos con el manual.

El registro completo está en [consumo_modelos.json](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/evidencias/consumo_modelos.json) y su selección de campos en [consumo_resumen.json](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/evidencias/consumo_resumen.json). La medición se puede repetir desde la carpeta del proyecto con:

```powershell
& '.venv/Scripts/python.exe' -u '../../Docs/medir_ejecucion.py' 2
```

El archivo de medición se encuentra en [Docs/medir_ejecucion.py](medir_ejecucion.py), dentro del directorio general del trabajo. Usa una base de validación separada para registrar la ingesta.

Ollama entrega el número real de tokens procesados y generados por su modelo. El límite de 300 tokens es un máximo configurado, no una cantidad consumida en todas las respuestas. En la consulta medida se generaron 52 tokens. Las duraciones originales se expresan en nanosegundos; para obtener segundos se dividen entre 1.000.000.000.

La velocidad de 8,90 tokens por segundo se calcula solamente durante la producción de tokens. No incluye todo el tiempo de carga ni de lectura del contexto. La memoria del proceso Python no incluye la memoria del proceso que ejecuta el modelo dentro de Ollama. La API de Ollama informó un modelo cargado de 2,39 GiB y cero bytes de memoria GPU.

Para la pregunta sobre WAR42 en 2027, el comando `compare` registró 860 tokens en el contexto RAG frente a 6903 al reunir todos los fragmentos almacenados. El ahorro calculado fue de 87,5 %. Este conteo usa `tiktoken` con `cl100k_base` como referencia; no es el contador de Llama. El contexto largo se construye con todos los fragmentos, incluidos sus solapamientos, y no con una copia única del documento original. Por ello, la comparación describe esta implementación y no una reducción garantizada del tiempo de respuesta.

### 4.7. Resultados y revisión de respuestas

La ingesta actual de comprobación procesó un archivo, obtuvo un documento limpio y almacenó 57 fragmentos. Las 26 pruebas del proyecto finalizaron correctamente. Las pruebas utilizan un generador de vectores de prueba, mientras que la ingesta y las consultas de este informe utilizaron el modelo real descargado.

Las preguntas cubren duraciones A/B/C, alcances Offshore/Onshore, hitos SST-400, HGP, WAR42, colores de cronograma, ensayos NDT y confiabilidad. Las respuestas verificadas directamente con el manual están en [PREGUNTAS_Y_RESPUESTAS_VERIFICADAS.md](../resultados/PREGUNTAS_Y_RESPUESTAS_VERIFICADAS.md).

Se comprobó que el modelo puede omitir parte de una pregunta, incluso con contexto disponible. Por ejemplo, una respuesta breve sobre HGP puede incluir su definición y horas, pero no todos los ciclos equivalentes. Los resultados del modelo se conservan como evidencia; las respuestas contrastadas con el manual se presentan por separado. Tener temperatura cero y fuentes recuperadas no elimina la necesidad de revisar el contenido.

La comparación de tokens mostró una reducción del contexto enviado en la consulta de WAR42. Ese resultado se limita al método de conteo y al conjunto de fragmentos de esta implementación; no se realizaron mediciones para afirmar una mejora general del tiempo de generación.
### 4.8. Registro detallado de capturas

Se registran **14 capturas** de este proyecto. Cada imagen tiene su archivo PNG, su origen y una referencia verificable al código. Las vistas documentales se obtuvieron leyendo los archivos reales y abriendo una vista HTML local. Las capturas de aplicación proceden de Chromium en una sesión aislada de prueba. No se usaron imágenes generadas por IA.

Para repetir una captura del código en Visual Studio Code, abrir el archivo indicado, ir a la línea con Ctrl+G y capturar el área del editor con Herramienta Recortes. Para repetir una captura de aplicación, realizar la acción descrita en el navegador y capturar la pantalla después de terminar la consulta. Las imágenes ya registradas están en `Docs/capturas` de este proyecto.

#### Captura 01. Manual utilizado por el sistema RAG

**Acción para obtenerla:** Abrir el manual de `data/raw` en Visual Studio Code.

**Origen registrado:** `data/raw/MANUAL_PROGRAMA_MANTENIMIENTO_PREVENTIVO.md`. **Ruta de la imagen:** `Docs/capturas/01_manual.png`.

**Código relacionado:** [ingestion/extractors.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/ingestion/extractors.py), líneas 70–81.

**Vista utilizada para la captura:** [capturas/01_manual.html](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/01_manual.html). El archivo de origen se muestra desde la línea 1 hasta la 30.

**Explicación de la evidencia:** El documento es la fuente aplicada de conocimiento. La consulta utiliza fragmentos de este archivo y no una base de ejemplos de reembolsos o soporte técnico.

![Manual utilizado por el sistema RAG](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/01_manual.png)

#### Captura 02. Configuración de recuperación y modelos

**Acción para obtenerla:** Abrir `config/settings.py` y revisar las rutas, los pesos de búsqueda y los modelos.

**Origen registrado:** `config/settings.py`. **Ruta de la imagen:** `Docs/capturas/02_configuracion.png`.

**Código relacionado:** [config/settings.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/config/settings.py), líneas 16–55.

**Vista utilizada para la captura:** [capturas/02_configuracion.html](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/02_configuracion.html). El archivo de origen se muestra desde la línea 16 hasta la 55.

**Explicación de la evidencia:** Se observan 500 caracteres por fragmento, 80 de solapamiento, cuatro resultados por defecto, pesos de 0,6 y 0,4, y el modelo `llama3.2:3b`. La configuración permite cambiar estos valores mediante variables del entorno.

![Configuración de recuperación y modelos](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/02_configuracion.png)

#### Captura 03. Etapas de extracción, limpieza e ingesta

**Acción para obtenerla:** Abrir `ingestion/pipeline.py` en `run_pipeline`.

**Origen registrado:** `ingestion/pipeline.py`. **Ruta de la imagen:** `Docs/capturas/03_ingestion_codigo.png`.

**Código relacionado:** [ingestion/pipeline.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/ingestion/pipeline.py), líneas 26–63.

**Vista utilizada para la captura:** [capturas/03_ingestion_codigo.html](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/03_ingestion_codigo.html). El archivo de origen se muestra desde la línea 26 hasta la 69.

**Explicación de la evidencia:** La función registra cuatro etapas: extracción, limpieza, fragmentación y almacenamiento de vectores. El resumen final permite comprobar cuántos archivos y fragmentos fueron procesados.

![Etapas de extracción, limpieza e ingesta](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/03_ingestion_codigo.png)

#### Captura 04. Solapamiento y división del texto limpio

**Acción para obtenerla:** Abrir `rag/chunking.py` y revisar `split_text` y `_add_overlap`.

**Origen registrado:** `rag/chunking.py`. **Ruta de la imagen:** `Docs/capturas/04_fragmentacion.png`.

**Código relacionado:** [rag/chunking.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/chunking.py), líneas 66–104.

**Vista utilizada para la captura:** [capturas/04_fragmentacion.html](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/04_fragmentacion.html). El archivo de origen se muestra desde la línea 66 hasta la 104.

**Explicación de la evidencia:** El programa divide el texto limpio y añade parte del fragmento anterior al siguiente. Los 500 caracteres son el tamaño previo a añadir hasta 80 caracteres de solapamiento y un espacio.

![Solapamiento y división del texto limpio](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/04_fragmentacion.png)

#### Captura 05. Búsqueda híbrida y tratamiento de siglas

**Acción para obtenerla:** Abrir `rag/retriever.py` en `hybrid_search` y `search`.

**Origen registrado:** `rag/retriever.py`. **Ruta de la imagen:** `Docs/capturas/05_recuperacion.png`.

**Código relacionado:** [rag/retriever.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/retriever.py), líneas 84–116.

**Vista utilizada para la captura:** [capturas/05_recuperacion.html](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/05_recuperacion.html). El archivo de origen se muestra desde la línea 84 hasta la 116.

**Explicación de la evidencia:** La recuperación combina semejanza de vectores y coincidencia de palabras. En preguntas con HGP, MO o RMI, se realiza una búsqueda adicional para incluir la definición sin retirar los principales hitos de la consulta original.

![Búsqueda híbrida y tratamiento de siglas](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/05_recuperacion.png)

#### Captura 06. Consumo de Ollama y reglas de respuesta

**Acción para obtenerla:** Abrir `rag/generator.py` en `generate_answer`.

**Origen registrado:** `rag/generator.py`. **Ruta de la imagen:** `Docs/capturas/06_generacion.png`.

**Código relacionado:** [rag/generator.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/generator.py), líneas 21–50.

**Vista utilizada para la captura:** [capturas/06_generacion.html](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/06_generacion.html). El archivo de origen se muestra desde la línea 21 hasta la 50.

**Explicación de la evidencia:** La aplicación crea un cliente Ollama local, envía instrucciones y contexto, y recibe el texto de la respuesta. Las reglas contienen las definiciones del manual, separan EOH de EOC y establecen un máximo de 300 tokens de salida.

![Consumo de Ollama y reglas de respuesta](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/06_generacion.png)

#### Captura 07. Registro real de la base de validación

**Acción para obtenerla:** Ejecutar `.venv\Scripts\python.exe cli.py ingest --reset` desde la terminal del proyecto.

**Origen registrado:** `Docs/evidencias/ingesta.txt`. **Ruta de la imagen:** `Docs/capturas/07_ingesta.png`.

**Código relacionado:** [ingestion/pipeline.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/ingestion/pipeline.py), líneas 26–63.

**Vista utilizada para la captura:** [capturas/07_ingesta.html](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/07_ingesta.html). El archivo de origen se muestra desde la línea 1 hasta la 26.

**Explicación de la evidencia:** La comprobación procesó un archivo, obtuvo un documento limpio y guardó 57 fragmentos. Se utilizó `Docs/evidencias/base_validacion` como base separada para conservar la aplicación abierta.

![Registro real de la base de validación](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/07_ingesta.png)

#### Captura 08. Chat, modelos y base de conocimiento

**Acción para obtenerla:** Abrir `http://127.0.0.1:8502` con Ollama y Streamlit en ejecución.

**Origen registrado:** `http://127.0.0.1:8502/`. **Ruta de la imagen:** `Docs/capturas/08_aplicacion_inicio.png`.

**Código relacionado:** [app/streamlit_app.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/app/streamlit_app.py), líneas 22–68.

**Explicación de la evidencia:** El panel lateral muestra 57 fragmentos, el modelo de vectores, el modelo de generación y los controles de recuperación. La parte central permite elegir una pregunta sugerida o escribir una nueva.

![Chat, modelos y base de conocimiento](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/08_aplicacion_inicio.png)

#### Captura 09. Respuesta generada sobre las inspecciones

**Acción para obtenerla:** Pulsar Consultar pregunta sugerida para la pregunta sobre inspecciones.

**Origen registrado:** `http://127.0.0.1:8502/`. **Ruta de la imagen:** `Docs/capturas/09_respuesta_inspecciones.png`.

**Código relacionado:** [app/streamlit_app.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/app/streamlit_app.py), líneas 70–107.

**Explicación de la evidencia:** La aplicación recupera información, prepara el contexto y genera una respuesta. La captura se toma después de recibir el texto final. Los valores deben revisarse contra el manual, que indica 3, 26 y 31 días.

![Respuesta generada sobre las inspecciones](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/09_respuesta_inspecciones.png)

#### Captura 10. Fuentes y fragmentos que sustentan la respuesta

**Acción para obtenerla:** Abrir el panel de fragmentos recuperados debajo de la pregunta.

**Origen registrado:** `http://127.0.0.1:8502/`. **Ruta de la imagen:** `Docs/capturas/10_fuentes_recuperadas.png`.

**Código relacionado:** [app/streamlit_app.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/app/streamlit_app.py), líneas 87–94.

**Explicación de la evidencia:** El panel muestra el nombre del manual, el puntaje de cada fragmento y una vista de su texto. La interfaz limita esa vista a 400 caracteres; el contexto enviado al generador utiliza el fragmento completo.

![Fuentes y fragmentos que sustentan la respuesta](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/10_fuentes_recuperadas.png)

#### Captura 11. Consulta de HGP con horas y ciclos equivalentes

**Acción para obtenerla:** Escribir la pregunta sobre HGP, EOH y EOC en el campo de chat y enviar con Enter.

**Origen registrado:** `http://127.0.0.1:8502/`. **Ruta de la imagen:** `Docs/capturas/11_respuesta_hgp.png`.

**Código relacionado:** [rag/retriever.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/retriever.py), líneas 104–116.

**Explicación de la evidencia:** La definición que debe respetarse es Hot Gas Path Inspection. Los hitos HGP del manual son 30.000 EOH/500 EOC y 90.000 EOH/1.500 EOC. La evidencia permite comprobar si la respuesta cubre toda la pregunta.

![Consulta de HGP con horas y ciclos equivalentes](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/11_respuesta_hgp.png)

#### Captura 12. Tiempo, memoria y tokens medidos

**Acción para obtenerla:** Abrir `Docs/evidencias/consumo_resumen.json`.

**Origen registrado:** `Docs/evidencias/consumo_resumen.json`. **Ruta de la imagen:** `Docs/capturas/12_consumo_modelos.png`.

**Código relacionado:** [rag/generator.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/generator.py), líneas 24–44.

**Vista utilizada para la captura:** [capturas/12_consumo_modelos.html](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/12_consumo_modelos.html). El archivo de origen se muestra desde la línea 1 hasta la 45.

**Explicación de la evidencia:** El archivo reúne tiempo de recuperación y generación, memoria de Python, tokens de entrada y salida informados por Ollama y comparación de contexto. Las duraciones originales de Ollama están en nanosegundos.

![Tiempo, memoria y tokens medidos](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/12_consumo_modelos.png)

#### Captura 13. Resultado real de las pruebas del proyecto

**Acción para obtenerla:** Ejecutar `.venv\Scripts\python.exe -m pytest -q` en la terminal del proyecto.

**Origen registrado:** `Docs/evidencias/pruebas.txt`. **Ruta de la imagen:** `Docs/capturas/13_pruebas.png`.

**Código relacionado:** [tests/conftest.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/tests/conftest.py), líneas 32–49.

**Vista utilizada para la captura:** [capturas/13_pruebas.html](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/13_pruebas.html). El archivo de origen se muestra desde la línea 1 hasta la 6.

**Explicación de la evidencia:** El resultado registrado fue de 26 pruebas aprobadas. Estas pruebas usan vectores de prueba para revisar la lógica sin descargar modelos; la ejecución real de los modelos se comprobó por separado.

![Resultado real de las pruebas del proyecto](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/13_pruebas.png)

#### Captura 14. Construcción del contexto enviado al modelo

**Acción para obtenerla:** Abrir `rag/augmentation.py` y revisar `format_context` y `build_prompt`.

**Origen registrado:** `rag/augmentation.py`. **Ruta de la imagen:** `Docs/capturas/14_contexto.png`.

**Código relacionado:** [rag/augmentation.py](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/rag/augmentation.py), líneas 11–46.

**Vista utilizada para la captura:** [capturas/14_contexto.html](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/14_contexto.html). El archivo de origen se muestra desde la línea 11 hasta la 46.

**Explicación de la evidencia:** Se construyen tres partes: instrucciones, contexto recuperado y pregunta. Cada fragmento incluye su fuente y un número para facilitar la revisión de las afirmaciones de la respuesta.

![Construcción del contexto enviado al modelo](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/14_contexto.png)

El archivo [manifest.json](../rag-knowledge-pipeline%20%281%29/rag-knowledge-pipeline/Docs/capturas/manifest.json) registra el origen, el tipo de imagen y las líneas de cada captura.

## 5. Conclusiones

El proyecto implementa la lectura, limpieza, fragmentación, almacenamiento, recuperación y generación de respuestas sobre el manual. La búsqueda híbrida combina información por significado y por palabras, y la aplicación permite revisar los fragmentos utilizados.

La ingesta comprobada produjo 57 fragmentos y las 26 pruebas finalizaron correctamente. La generación local mediante Ollama funcionó con el modelo `llama3.2:3b`, sin una API de pago. La medición mostró que la generación consume más tiempo que la recuperación en la consulta registrada.

Las correcciones de siglas y unidades mejoraron la preparación del contexto. Sin embargo, se observaron respuestas que requieren revisión o que no incluyen todos los datos solicitados. El resultado debe contrastarse con el manual antes de utilizarlo como información de mantenimiento.

## 6. Recomendaciones

1. Mantener el manual vigente e identificar su versión antes de reconstruir la base.
2. Usar el entorno Python del proyecto y conservar `requirements-lock.txt`.
3. Revisar los datos de EOH y EOC, las siglas y las duraciones contra los fragmentos originales.
4. Reiniciar la aplicación después de modificar la base para renovar la búsqueda por palabras.
5. Medir tokens con el método del modelo para ajustar fragmentos y contexto sin perder información.
6. Confirmar que Ollama y el modelo configurado estén disponibles antes de consultar.
7. Mantener el modo `--no-generate` para revisar recuperación y contexto cuando la generación falle o sea incompleta.
8. Conservar registros de preguntas, respuestas, fuentes y consumo para comparar cambios.
9. Revisar manualmente respuestas sobre mantenimiento; los puntajes y la temperatura no prueban su exactitud.
10. Repetir las mediciones en el equipo de uso, porque los tiempos y la memoria dependen del estado del sistema y del modelo cargado.
