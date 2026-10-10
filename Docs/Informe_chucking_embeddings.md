# Informe del proyecto de fragmentación, embeddings y base vectorial

**Proyecto:** `rag-chunking-embeddings-vectordb`  
**Fuente aplicada:** Manual del Programa de Mantenimiento Preventivo de turbinas SGT-800 y SST-400  
**Fecha de documentación:** 10 de octubre de 2026  
**Entorno:** Windows, Python 3.12.15 y ejecución local en CPU

## 1. Introducción

El proyecto organiza el contenido del Manual del Programa de Mantenimiento Preventivo para permitir su consulta mediante preguntas escritas. Lee el documento, lo divide en partes, representa cada parte con números y guarda esas representaciones en una base local. Cuando una persona pregunta, el programa busca las partes del manual que tienen mayor relación con esa pregunta.

La aplicación muestra fragmentos y su fuente. Su alcance termina en la recuperación de información: no utiliza un modelo de lenguaje para redactar una respuesta nueva. Esta diferencia permite revisar directamente el texto del manual antes de interpretar sus datos.

La adaptación realizada utiliza el manual como fuente activa, cambia la configuración del modelo de vectores, crea una colección específica y añade una aplicación web con preguntas sobre mantenimiento. Este informe explica el funcionamiento y presenta evidencia de la ejecución.

## 2. Objetivos

### 2.1. Objetivo general

Implementar y documentar una aplicación local que recupere información del manual de mantenimiento preventivo mediante la búsqueda de fragmentos relacionados con una pregunta.

### 2.2. Objetivos específicos

1. Preparar un entorno de Python separado para el proyecto.
2. Leer el manual y conservar el archivo de origen de cada fragmento.
3. Dividir el contenido con un tamaño y un solapamiento definidos.
4. Crear vectores mediante un modelo multilingüe ejecutado localmente.
5. Guardar los vectores en Chroma y consultar la colección del manual.
6. Presentar los resultados en una aplicación web y en la terminal.
7. Registrar capturas, resultados y consumo medido del modelo.

## 3. Marco Teórico

### 3.1. Ingesta de documentos

La ingesta es la lectura y preparación de archivos para su uso en la aplicación. En este proyecto se admiten archivos de texto, Markdown y PDF. Markdown es un formato de texto que permite escribir títulos, listas y tablas. El manual utilizado está en ese formato.

### 3.2. Fragmentación del texto

La fragmentación, denominada *chunking* en el código, consiste en dividir un documento en partes. El solapamiento repite una porción del texto anterior en el fragmento siguiente. Su propósito es conservar información que podría quedar separada en un corte.

La estrategia principal prueba separadores de párrafo, línea, oración y palabra. También existen funciones para separar por cambios de tema y para guardar fragmentos pequeños con un texto mayor relacionado. La ejecución documentada utiliza la estrategia principal, llamada `recursive`.

### 3.3. Embeddings o vectores de texto

Un embedding es una lista de números calculada por un modelo a partir del texto. Estos números permiten comparar preguntas y fragmentos. El modelo utilizado es multilingüe y puede procesar el contenido en español. En esta ejecución cada vector tiene 384 valores. La normalización ajusta la longitud numérica del vector para facilitar su comparación con otros vectores.

Los documentos y las preguntas deben utilizar el mismo modelo. Si se cambia el modelo, se debe volver a crear la base. El manual se utiliza como contenido de consulta; no se realizó entrenamiento del modelo con sus datos.

### 3.4. Base vectorial y similitud

Chroma almacena los vectores, el texto y datos de origen. En este caso conserva los datos en archivos locales para reutilizarlos después de cerrar la aplicación. La comparación utiliza la distancia de coseno; el código muestra la similitud como uno menos esa distancia.

El valor de similitud sirve para ordenar resultados. No representa la probabilidad de que una afirmación sea correcta. El parámetro `top_k` indica cuántos fragmentos se devuelven.

### 3.5. Relación con RAG

RAG es una forma de preparar respuestas mediante recuperación de información y generación de texto. Este proyecto implementa la lectura, fragmentación, creación de vectores, almacenamiento y recuperación. La generación se realiza en el otro proyecto, denominado `rag-knowledge-pipeline`.

## 4. Implementación Aplicada
### 4.1. Entorno de trabajo en Visual Studio Code

El directorio de trabajo es `C:\Users\Usuario\Desktop\TrabFin ModII`. En Visual Studio Code se debe seleccionar **Archivo > Abrir carpeta** y abrir este directorio. El proyecto de este informe se encuentra en `rag-chunking-embeddings-vectordb\rag-chunking-embeddings-vectordb`. La carpeta exterior contiene la carpeta interna del proyecto; los comandos deben ejecutarse en la carpeta interna, donde está el archivo de configuración.

Los archivos se modificaron y las aplicaciones se ejecutaron mediante herramientas de archivos y PowerShell. Esta sección documenta cómo revisar y reproducir ese trabajo en Visual Studio Code. Las imágenes del código son vistas documentales de archivos reales; no se presentan como capturas nativas del editor. Las imágenes de la aplicación sí corresponden a su ejecución real en un navegador de prueba.

Para revisar el código, abrir el archivo desde el panel **Explorador**. Usar **Ctrl+G** para ir a la línea indicada en cada evidencia. Para ejecutar los comandos, abrir **Terminal > Nueva terminal**. Para revisar este informe con sus imágenes, abrir `Docs/Informe.md` y usar **Ctrl+Shift+V**.

El equipo tenía Python 3.14. Se instaló Python 3.12.15 en `.runtime`, dentro del directorio de trabajo, para usar una versión compatible con las dependencias. Cada proyecto tiene su propio entorno `.venv`. Desde la raíz del trabajo, la instalación realizada se puede reproducir con:

```powershell
python -m pip install --target .tools uv
$env:UV_PYTHON_INSTALL_DIR = Join-Path $PWD '.runtime'
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
& '.tools/bin/uv.exe' python install 3.12
& '.tools/bin/uv.exe' venv --python '.runtime/cpython-3.12.15-windows-x86_64-none/python.exe' 'rag-chunking-embeddings-vectordb\rag-chunking-embeddings-vectordb/.venv'
& '.tools/bin/uv.exe' pip install --python 'rag-chunking-embeddings-vectordb\rag-chunking-embeddings-vectordb/.venv/Scripts/python.exe' -r 'rag-chunking-embeddings-vectordb\rag-chunking-embeddings-vectordb/requirements-lock.txt'
```

`uv` es la herramienta utilizada para instalar Python y las bibliotecas. `requirements.txt` establece las dependencias admitidas. `requirements-lock.txt` registra las versiones instaladas. La primera instalación necesita conexión a Internet.

En Visual Studio Code, abrir **Ctrl+Shift+P > Python: Select Interpreter** y seleccionar el archivo `.venv\Scripts\python.exe` de este proyecto. Esta opción requiere la extensión Python del editor. Si la extensión no está disponible, los comandos siguientes siguen indicando de forma expresa el archivo de Python que deben utilizar.

Antes de ejecutar las consultas, ubicar la terminal en la carpeta del proyecto y definir la ubicación del modelo descargado:

```powershell
Set-Location 'C:\Users\Usuario\Desktop\TrabFin ModII\rag-chunking-embeddings-vectordb\rag-chunking-embeddings-vectordb'
$env:HF_HOME = 'C:\Users\Usuario\Desktop\TrabFin ModII\.cache\huggingface'
$env:HF_HUB_OFFLINE = '1'
$env:PYTHONUTF8 = '1'
```

El modo sin conexión indicado funciona porque el modelo ya fue descargado. Para una primera descarga se debe quitar esa variable con `Remove-Item Env:HF_HUB_OFFLINE -ErrorAction SilentlyContinue`. Esta instrucción elimina la variable de la terminal, no archivos del proyecto.

Las bibliotecas principales instaladas fueron Sentence Transformers 6.1.0, PyTorch 2.14.1, Chroma 1.5.9 y Streamlit 1.65.0. Las versiones exactas y las demás dependencias están en [requirements-lock.txt](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/requirements-lock.txt).

### 4.2. Organización y cambios realizados

| Archivo o carpeta | Función aplicada |
|---|---|
| `data/documentos/` | Contiene el manual usado por la ingesta. |
| `data/ejemplos/` | Conserva el ejemplo sobre RAG fuera de la fuente activa. |
| `config.py` | Define rutas, modelo, colección, tamaños y cantidad de resultados. |
| `src/utils.py` | Lee los documentos y registra su fuente. |
| `src/chunking.py` | Implementa las tres estrategias de división del texto. |
| `src/embeddings.py` | Carga el modelo y obtiene vectores normalizados. |
| `src/vector_store.py` | Guarda y consulta los fragmentos en Chroma. |
| `src/ingest.py` | Ejecuta la ingesta completa desde la terminal. |
| `src/query.py` | Recupera fragmentos para una pregunta. |
| `app.py` | Presenta el buscador web. |
| `consultas_manual.py` | Ejecuta las ocho preguntas y guarda resultados. |

La colección se cambió a `manual_mantenimiento_preventivo`. El modelo activo se cambió de la opción original BGE a `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Se añadieron Streamlit y `app.py`, las preguntas aplicadas al mantenimiento, los accesos de ejecución y el registro de resultados. Referencias: [config.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/config.py), líneas 18–46 y [app.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/app.py), líneas 1–35.

El tamaño configurado es 128 tokens aproximados y el solapamiento 25. La función multiplica esos valores por cuatro: trabaja con 512 caracteres y 100 caracteres de solapamiento. Este cálculo no cuenta tokens exactos del modelo. Referencia: [src/chunking.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/chunking.py), líneas 43–56.

### 4.3. Funcionamiento paso a paso

1. **Leer la carpeta de documentos.** `load_documents` busca archivos admitidos y lee su contenido. Para cada documento guarda el texto y la ruta de origen. Referencia: [src/utils.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/utils.py), líneas 16–47.
2. **Cargar el modelo.** `EmbeddingModel` crea una instancia de Sentence Transformer en CPU. La primera ejecución descarga el modelo; las siguientes usan la caché local. Referencia: [src/embeddings.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/embeddings.py), líneas 22–37.
3. **Dividir el manual.** La estrategia `recursive` genera fragmentos con separadores de texto y conserva la fuente, el nombre de la estrategia y un índice. Referencia: [src/chunking.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/chunking.py), líneas 32–63.
4. **Calcular los vectores.** `embed_texts` envía los fragmentos al modelo y normaliza los vectores obtenidos. Referencia: [src/embeddings.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/embeddings.py), líneas 39–49.
5. **Guardar los datos.** `add_chunks` asigna identificadores y almacena textos, vectores y datos de origen en Chroma. Referencia: [src/vector_store.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/vector_store.py), líneas 36–55.
6. **Recibir una pregunta.** La terminal o la aplicación web obtiene el texto escrito por la persona. Referencia: [src/query.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/query.py), líneas 29–34 y [app.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/app.py), líneas 24–26.
7. **Convertir la pregunta en un vector.** `embed_query` aplica el mismo modelo utilizado para el manual. Referencia: [src/embeddings.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/embeddings.py), líneas 51–60.
8. **Buscar los resultados.** Chroma compara el vector de la pregunta con los almacenados y devuelve la cantidad solicitada. Referencia: [src/vector_store.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/vector_store.py), líneas 68–100.
9. **Mostrar texto y fuente.** La aplicación presenta los fragmentos completos, la fuente y su similitud. La terminal muestra una vista de los primeros 300 caracteres de cada fragmento. Referencia: [app.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/app.py), líneas 30–35 y [src/query.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/query.py), líneas 48–58.

El código también contiene `semantic_split`, que compara oraciones para detectar cambios de tema, y `parent_child_split`, que conserva un texto mayor junto a fragmentos pequeños. Son opciones disponibles en la ingesta; no fueron las estrategias utilizadas en las capturas ni en la medición de este informe. Sus tamaños deben revisarse antes de usarlas con el modelo activo.

### 4.4. Ejecución en la terminal de Visual Studio Code

Con la terminal situada en la carpeta interna del proyecto, crear o reemplazar la colección del manual:

```powershell
& '.venv/Scripts/python.exe' -m src.ingest --reset
```

El argumento `--reset` reemplaza el contenido de la colección seleccionada. Para documentar una ejecución sin cambiar la aplicación activa se puede usar una base separada:

```powershell
$env:PERSIST_DIR = Join-Path $PWD 'Docs/evidencias/base_validacion'
& '.venv/Scripts/python.exe' -m src.ingest --reset
& '.venv/Scripts/python.exe' -m src.query '¿Cuántos días duran las inspecciones A, B y C de las SGT-800?' --top-k 5
Remove-Item Env:PERSIST_DIR
```

La última instrucción quita la variable de la terminal. La base de validación permanece guardada. La evidencia de ingesta está en [ingesta.txt](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/evidencias/ingesta.txt) y la consulta en [consulta.txt](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/evidencias/consulta.txt).

Para repetir las ocho preguntas, ejecutar:

```powershell
& '.venv/Scripts/python.exe' consultas_manual.py
```

El archivo de preguntas común está en [preguntas_manual.json](../preguntas_manual.json). Los resultados se guardan en [resultados/proyecto_1_consultas.json](../resultados/proyecto_1_consultas.json), dentro del directorio general del trabajo. Referencia: [consultas_manual.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/consultas_manual.py), líneas 1–20.

### 4.5. Ejecución y uso de la aplicación web

Desde la carpeta del proyecto:

```powershell
& '.venv/Scripts/python.exe' -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --browser.gatherUsageStats false
```

También existe el acceso [ejecutar-proyecto-1.ps1](../ejecutar-proyecto-1.ps1) en la raíz del trabajo. Al iniciar el servidor se debe abrir `http://127.0.0.1:8501`. Si ya está ejecutándose en ese puerto, se utiliza la instancia abierta.

La persona selecciona una pregunta sugerida o escribe otra, elige la cantidad de fragmentos y pulsa **Buscar**. La aplicación carga el modelo y la base una vez por proceso mediante `st.cache_resource`. Después reutiliza esos recursos en las consultas. Para cerrar una instancia iniciada en la terminal, pulsar Ctrl+C en esa terminal.
### 4.6. Consumo de los modelos de IA

Los modelos se ejecutan localmente. El modelo de vectores se descarga una vez desde Hugging Face y se reutiliza desde `.cache/huggingface`. La consulta y la ingesta consumen tiempo de CPU, memoria RAM y espacio en disco. En esta ejecución no se usó una API de pago ni se enviaron preguntas a un servicio externo de generación.

La medición se realizó el **10 de octubre de 2026**, con horario de Bolivia. Se utilizó la pregunta «¿Qué significa HGP y en qué hitos EOH y EOC está previsto?». Los tiempos corresponden al estado del equipo en esa ejecución. La carga del modelo incluye la importación de sus bibliotecas. La memoria indicada corresponde al proceso Python completo, no solamente a los pesos del modelo.

| Medida | Resultado registrado |
|---|---|
| Modelo de vectores | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| Dimensión de cada vector | 384 |
| Carga del modelo y sus bibliotecas | 13,84 s |
| Memoria de Python con el modelo cargado | 1.175,1 MiB |
| Memoria máxima de Python durante la medición | 1.439,6 MiB |
| Fragmentos de la base activa | 58 |
| Fragmentos de la consulta medida | 5 |
| Consulta con el modelo ya cargado | 0,116 s |
| Modelo generativo | No se utiliza |

La suma del tamaño de los archivos de la caché de Hugging Face fue de **457,5 MiB**. Esta cifra corresponde a los archivos guardados en la caché, incluidos los archivos de configuración; no mide solamente los pesos ni todo el espacio ocupado por Python y sus dependencias. Las dimensiones y tiempos se registraron sin modificar el código de los modelos ni entrenarlos con el manual.

El registro completo está en [consumo_modelos.json](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/evidencias/consumo_modelos.json) y su selección de campos en [consumo_resumen.json](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/evidencias/consumo_resumen.json). La medición se puede repetir desde la carpeta del proyecto con:

```powershell
& '.venv/Scripts/python.exe' -u '../../Docs/medir_ejecucion.py' 1
```

El archivo de medición se encuentra en [Docs/medir_ejecucion.py](medir_ejecucion.py), dentro del directorio general del trabajo. Usa una base de validación separada para registrar la ingesta.

El modelo transforma el texto en números. No redacta respuestas de chat. Esta implementación no registra un contador de tokens de entrada ni produce tokens de salida de una respuesta de chat. Cambiar el tamaño de los fragmentos modifica la cantidad de vectores y el trabajo necesario para crearlos.

### 4.7. Resultados de la implementación

La ingesta de comprobación procesó un documento y almacenó 58 fragmentos con vectores reales. La consulta de terminal devolvió cinco resultados con el archivo de origen. La aplicación web permitió consultar inspecciones, contratos y confiabilidad. El registro de ocho preguntas realizado previamente se conserva en la carpeta general `resultados`.

Se verificó el funcionamiento de la aplicación mediante una prueba de carga y búsqueda con Streamlit AppTest y mediante las capturas actuales del navegador. Este proyecto no tiene una suite propia de 26 pruebas; esa suite corresponde al segundo proyecto. La calidad de la recuperación debe evaluarse revisando el conjunto de resultados, no solamente el primer fragmento.

Entre las respuestas documentales contrastadas se encuentran: inspecciones A, B y C con 3, 26 y 31 días de referencia; revisión parcial SST-400 a 25.000 EOH; revisión total a 50.000 EOH; y confiabilidad informada de 96,89 %, sin fórmula de cálculo visible.
### 4.8. Registro detallado de capturas

Se registran **12 capturas** de este proyecto. Cada imagen tiene su archivo PNG, su origen y una referencia verificable al código. Las vistas documentales se obtuvieron leyendo los archivos reales y abriendo una vista HTML local. Las capturas de aplicación proceden de Chromium en una sesión aislada de prueba. No se usaron imágenes generadas por IA.

Para repetir una captura del código en Visual Studio Code, abrir el archivo indicado, ir a la línea con Ctrl+G y capturar el área del editor con Herramienta Recortes. Para repetir una captura de aplicación, realizar la acción descrita en el navegador y capturar la pantalla después de terminar la consulta. Las imágenes ya registradas están en `Docs/capturas` de este proyecto.

#### Captura 01. Documento utilizado como fuente

**Acción para obtenerla:** Abrir el manual en el Explorador de Visual Studio Code y comprobar su título y contenido.

**Origen registrado:** `data/documentos/MANUAL_PROGRAMA_MANTENIMIENTO_PREVENTIVO.md`. **Ruta de la imagen:** `Docs/capturas/01_manual.png`.

**Código relacionado:** [src/utils.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/utils.py), líneas 16–41.

**Vista utilizada para la captura:** [capturas/01_manual.html](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/01_manual.html). El archivo de origen se muestra desde la línea 1 hasta la 30.

**Explicación de la evidencia:** El documento reúne información de las turbinas SGT-800 y SST-400. La carpeta de ingesta contiene el manual; el ejemplo sobre RAG se conserva en `data/ejemplos`, fuera de esa carpeta.

![Documento utilizado como fuente](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/01_manual.png)

#### Captura 02. Dependencias instaladas y necesarias

**Acción para obtenerla:** Abrir `requirements.txt` y revisar cada grupo de bibliotecas.

**Origen registrado:** `requirements.txt`. **Ruta de la imagen:** `Docs/capturas/02_dependencias.png`.

**Código relacionado:** [requirements.txt](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/requirements.txt), líneas 1–22.

**Vista utilizada para la captura:** [capturas/02_dependencias.html](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/02_dependencias.html). El archivo de origen se muestra desde la línea 1 hasta la 22.

**Explicación de la evidencia:** Se observa la separación entre lectura de documentos, división del texto, creación de vectores, almacenamiento y aplicación web. Streamlit fue añadido para disponer de una interfaz de consulta.

![Dependencias instaladas y necesarias](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/02_dependencias.png)

#### Captura 03. Rutas, modelo y tamaño de fragmentos

**Acción para obtenerla:** Abrir `config.py` y usar Ctrl+G para revisar las rutas y los valores de trabajo.

**Origen registrado:** `config.py`. **Ruta de la imagen:** `Docs/capturas/03_configuracion.png`.

**Código relacionado:** [config.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/config.py), líneas 18–64.

**Vista utilizada para la captura:** [capturas/03_configuracion.html](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/03_configuracion.html). El archivo de origen se muestra desde la línea 18 hasta la 64.

**Explicación de la evidencia:** La configuración selecciona el modelo multilingüe, la colección del manual y los tamaños de fragmentación. Los comentarios sobre BGE describen una alternativa del material original; el valor ejecutado está en la asignación `EMBEDDING_MODEL`.

![Rutas, modelo y tamaño de fragmentos](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/03_configuracion.png)

#### Captura 04. División del manual por separadores

**Acción para obtenerla:** Abrir `src/chunking.py` en la función `recursive_character_split`.

**Origen registrado:** `src/chunking.py`. **Ruta de la imagen:** `Docs/capturas/04_fragmentacion.png`.

**Código relacionado:** [src/chunking.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/chunking.py), líneas 32–63.

**Vista utilizada para la captura:** [capturas/04_fragmentacion.html](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/04_fragmentacion.html). El archivo de origen se muestra desde la línea 32 hasta la 63.

**Explicación de la evidencia:** El código multiplica por cuatro el tamaño aproximado en tokens para trabajar con caracteres. Se prueban separadores de párrafo, línea, oración y palabra. Cada fragmento conserva su fuente, estrategia y posición.

![División del manual por separadores](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/04_fragmentacion.png)

#### Captura 05. Carga del modelo y creación de vectores

**Acción para obtenerla:** Abrir `src/embeddings.py` y revisar la creación de `SentenceTransformer` y la llamada `encode`.

**Origen registrado:** `src/embeddings.py`. **Ruta de la imagen:** `Docs/capturas/05_embeddings.png`.

**Código relacionado:** [src/embeddings.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/embeddings.py), líneas 21–60.

**Vista utilizada para la captura:** [capturas/05_embeddings.html](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/05_embeddings.html). El archivo de origen se muestra desde la línea 21 hasta la 60.

**Explicación de la evidencia:** El modelo se carga en CPU y genera vectores normalizados. Los vectores del manual y de la pregunta usan el mismo modelo. La dimensión observada fue de 384 valores por vector.

![Carga del modelo y creación de vectores](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/05_embeddings.png)

#### Captura 06. Registro real de la ingesta del manual

**Acción para obtenerla:** Ejecutar `.venv\Scripts\python.exe -m src.ingest --reset` en la terminal del proyecto.

**Origen registrado:** `Docs/evidencias/ingesta.txt`. **Ruta de la imagen:** `Docs/capturas/06_ingesta.png`.

**Código relacionado:** [src/ingest.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/ingest.py), líneas 44–86.

**Vista utilizada para la captura:** [capturas/06_ingesta.html](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/06_ingesta.html). El archivo de origen se muestra desde la línea 1 hasta la 23.

**Explicación de la evidencia:** La evidencia muestra un documento leído, el modelo cargado y 58 fragmentos almacenados. Para esta comprobación se utilizó una base separada en `Docs/evidencias/base_validacion`, por lo que no se reemplazó la base de la aplicación abierta.

![Registro real de la ingesta del manual](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/06_ingesta.png)

#### Captura 07. Consulta real y fuentes recuperadas

**Acción para obtenerla:** Ejecutar `.venv\Scripts\python.exe -m src.query "¿Cuántos días duran las inspecciones A, B y C de las SGT-800?" --top-k 5`.

**Origen registrado:** `Docs/evidencias/consulta.txt`. **Ruta de la imagen:** `Docs/capturas/07_consulta_terminal.png`.

**Código relacionado:** [src/query.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/query.py), líneas 37–58.

**Vista utilizada para la captura:** [capturas/07_consulta_terminal.html](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/07_consulta_terminal.html). El archivo de origen se muestra desde la línea 1 hasta la 42.

**Explicación de la evidencia:** Se muestran cinco fragmentos, su similitud y el archivo de origen. La salida es texto recuperado del manual; el programa no crea una respuesta con un modelo generativo.

![Consulta real y fuentes recuperadas](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/07_consulta_terminal.png)

#### Captura 08. Inicio del buscador y base indexada

**Acción para obtenerla:** Abrir `http://127.0.0.1:8501` con el servidor iniciado.

**Origen registrado:** `http://127.0.0.1:8501/`. **Ruta de la imagen:** `Docs/capturas/08_aplicacion_inicio.png`.

**Código relacionado:** [app.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/app.py), líneas 6–24.

**Explicación de la evidencia:** La pantalla contiene el número de fragmentos indexados, el control de cantidad, las preguntas sugeridas, el campo de pregunta y el botón Buscar. El número mostrado corresponde a la base activa.

![Inicio del buscador y base indexada](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/08_aplicacion_inicio.png)

#### Captura 09. Resultados reales sobre inspecciones A, B y C

**Acción para obtenerla:** Seleccionar la pregunta sobre inspecciones A, B y C y pulsar Buscar.

**Origen registrado:** `http://127.0.0.1:8501/`. **Ruta de la imagen:** `Docs/capturas/09_busqueda_inspecciones.png`.

**Código relacionado:** [app.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/app.py), líneas 26–35.

**Explicación de la evidencia:** La aplicación presenta los fragmentos recuperados, el nombre del manual y los valores de similitud. Los tiempos de referencia que deben verificarse en el manual son 3, 26 y 31 días.

![Resultados reales sobre inspecciones A, B y C](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/09_busqueda_inspecciones.png)

#### Captura 10. Comparación documental de Offshore y Onshore

**Acción para obtenerla:** Escribir la pregunta sobre Offshore y Onshore en el campo Pregunta y pulsar Buscar.

**Origen registrado:** `http://127.0.0.1:8501/`. **Ruta de la imagen:** `Docs/capturas/10_busqueda_contratos.png`.

**Código relacionado:** [app.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/app.py), líneas 26–35.

**Explicación de la evidencia:** Los resultados permiten revisar el suministro de partes y soporte del contrato Offshore, y la mano de obra calificada del contrato Onshore. La consulta cambia; los vectores de los documentos permanecen almacenados.

![Comparación documental de Offshore y Onshore](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/10_busqueda_contratos.png)

#### Captura 11. Recuperación del indicador y sus límites

**Acción para obtenerla:** Escribir la pregunta sobre el 96,89 % y pulsar Buscar.

**Origen registrado:** `http://127.0.0.1:8501/`. **Ruta de la imagen:** `Docs/capturas/11_busqueda_confiabilidad.png`.

**Código relacionado:** [app.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/app.py), líneas 26–35.

**Explicación de la evidencia:** La aplicación recupera el indicador y las aclaraciones del manual. El documento no aporta período, población de equipos, fuente de datos ni fórmula de cálculo; esos datos no deben deducirse del porcentaje.

![Recuperación del indicador y sus límites](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/11_busqueda_confiabilidad.png)

#### Captura 12. Consumo medido del modelo de embeddings

**Acción para obtenerla:** Abrir `Docs/evidencias/consumo_resumen.json` en Visual Studio Code.

**Origen registrado:** `Docs/evidencias/consumo_resumen.json`. **Ruta de la imagen:** `Docs/capturas/12_consumo_modelos.png`.

**Código relacionado:** [src/embeddings.py](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/src/embeddings.py), líneas 22–49.

**Vista utilizada para la captura:** [capturas/12_consumo_modelos.html](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/12_consumo_modelos.html). El archivo de origen se muestra desde la línea 1 hasta la 14.

**Explicación de la evidencia:** La evidencia registra tiempos, memoria del proceso Python, tamaño de los vectores y cantidad de fragmentos. Los valores pertenecen a una ejecución concreta; no son límites garantizados para otros equipos.

![Consumo medido del modelo de embeddings](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/12_consumo_modelos.png)

El archivo [manifest.json](../rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb/Docs/capturas/manifest.json) registra el origen, el tipo de imagen y las líneas de cada captura.

## 5. Conclusiones

El proyecto cumple la función de leer el manual, dividirlo, crear vectores y recuperar partes relacionadas con una pregunta. La configuración aplicada conserva la fuente de cada resultado y permite ejecutar las consultas de manera local.

La ingesta comprobada generó 58 fragmentos y la búsqueda devolvió texto del manual con sus datos de origen. El modelo multilingüe permitió comparar preguntas en español con el contenido del documento. La memoria medida corresponde al proceso completo y confirma que la ejecución local requiere recursos del equipo.

La aplicación facilita la revisión documental, pero no redacta respuestas nuevas ni valida por sí sola una decisión de mantenimiento. La similitud organiza la búsqueda y debe acompañarse de la lectura de los fragmentos y del manual vigente.

## 6. Recomendaciones

1. Mantener una versión identificada del manual y reconstruir la colección cuando cambie su contenido.
2. Revisar las rutas y seleccionar el entorno `.venv` de este proyecto en Visual Studio Code.
3. Medir tokens con el método del modelo antes de cambiar los tamaños de fragmentación; la relación de cuatro caracteres por token es aproximada.
4. Usar una colección separada para comparar estrategias y evitar mezclar vectores de modelos distintos.
5. Revisar varios resultados y confirmar cifras, unidades, fechas y alcances contra el manual.
6. Conservar la caché del modelo, los archivos de versiones y las evidencias para repetir la ejecución.
7. Si se requiere una respuesta redactada, utilizar el sistema RAG del segundo proyecto y revisar sus fuentes.
8. Verificar tiempos y memoria en el equipo de destino; los valores registrados describen una sola ejecución.
