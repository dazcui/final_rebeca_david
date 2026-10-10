# Pipeline de Chunking, Embeddings y Base de Datos Vectorial

## Adaptación al manual de mantenimiento preventivo

La fuente activa es `MANUAL_PROGRAMA_MANTENIMIENTO_PREVENTIVO.md` (SGT-800 y SST-400). El ejemplo RAG está conservado en `data/ejemplos` y queda fuera de la ingesta. La colección es `manual_mantenimiento_preventivo`; el modelo predeterminado es `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, con chunks de aproximadamente 128 tokens y solapamiento de 25.

Hay una interfaz Streamlit en `app.py` y preguntas de prueba en `consultas_manual.py`. Para las instrucciones específicas de Windows, consultar [LEEME_MANTENIMIENTO.md](../../LEEME_MANTENIMIENTO.md). Las secciones siguientes describen el material educativo original; sus ejemplos y el modelo BGE son alternativas, no la configuración activa.

Proyecto en Python que implementa el tramo de un sistema **RAG
(Retrieval-Augmented Generation)** correspondiente a las **Unidades 4,
5 y 6** del módulo *Arquitecturas RAG y Gestión del Conocimiento*:

```
Ingesta  →  Chunking (U4)  →  Embeddings (U5)  →  Vector DB (U6)  →  Retrieval
```

El objetivo es que puedas cargar tus propios documentos, dividirlos con
distintas estrategias de segmentación, convertirlos en vectores
semánticos y almacenarlos en una base de datos vectorial local para
luego recuperarlos mediante búsqueda por similitud.

> **100% open source y sin costo por token.** Todo el pipeline corre
> en tu computadora: el modelo de embeddings se descarga una sola vez
> desde Hugging Face y la base de datos vectorial (Chroma) es
> embebida y local. No necesitas ninguna API key ni consumir créditos
> de un proveedor de pago (OpenAI, Cohere, etc.).

---

## 1. Contenido y relación con la clase

| Módulo del proyecto | Unidad | Tema de la presentación |
|---|---|---|
| `src/chunking.py` | U4 | Recursive character splitting, chunking semántico, parent-child |
| `src/embeddings.py` | U5 | Generación de vectores con un modelo open source multilingüe |
| `src/vector_store.py` | U6 | Indexación HNSW y búsqueda por similitud coseno con Chroma |
| `src/ingest.py` | U4+U5+U6 | Orquesta todo el pipeline de ingesta |
| `src/query.py` | U6 | Retrieval: recupera los *k* chunks más relevantes para una pregunta |

Este proyecto **no incluye la etapa de Generación** (pasar los chunks
recuperados a un LLM para redactar una respuesta): esa parte
corresponde a la Unidad 7 (orquestación con LangChain / LlamaIndex),
mencionada como próximo paso en el cierre de la clase. La sección
["Próximos pasos"](#8-próximos-pasos-unidad-7) explica cómo extender
este proyecto para llegar a un RAG completo.

---

## 2. Estructura del proyecto

```
rag-chunking-embeddings-vectordb/
├── README.md                  <- este archivo
├── requirements.txt           <- dependencias (todas open source)
├── config.py                  <- configuración central (rutas, modelo, tamaños de chunk)
├── .gitignore
├── data/
│   └── documentos/            <- coloca aquí tus archivos .txt / .md / .pdf
│       └── ejemplo_rag.md     <- documento de ejemplo para probar el pipeline
├── vectorstore/                <- se genera automáticamente (base de datos Chroma)
└── src/
    ├── __init__.py
    ├── utils.py                <- carga de documentos (.txt, .md, .pdf)
    ├── chunking.py              <- estrategias de segmentación (U4)
    ├── embeddings.py            <- modelo de embeddings (U5)
    ├── vector_store.py          <- base de datos vectorial Chroma (U6)
    ├── ingest.py                <- script CLI: ingesta completa
    └── query.py                 <- script CLI: consulta / retrieval
```

---

## 3. Herramientas y librerías utilizadas

Todas son **open source** y se instalan con `pip`, sin necesidad de
registrarte en ningún servicio:

| Herramienta | Para qué se usa | Licencia |
|---|---|---|
| [`langchain-text-splitters`](https://pypi.org/project/langchain-text-splitters/) | `RecursiveCharacterTextSplitter` para el chunking base (U4) | MIT |
| [`sentence-transformers`](https://www.sbert.net/) | Cargar y ejecutar modelos de embeddings localmente (U5) | Apache 2.0 |
| [`BAAI/bge-m3`](https://huggingface.co/BAAI/bge-m3) (modelo) | Modelo de embeddings multilingüe, recomendado para español (diapositiva 20) | MIT |
| [`ChromaDB`](https://www.trychroma.com/) | Base de datos vectorial embebida y local (U6) | Apache 2.0 |
| [`pypdf`](https://pypi.org/project/pypdf/) | Extraer texto de archivos PDF | BSD |
| [`torch`](https://pytorch.org/) | Motor de cómputo para ejecutar el modelo de embeddings | BSD |

No se usa ninguna librería que requiera API key (ni OpenAI, ni
Cohere, ni Pinecone gestionado). Si en el futuro quieres comparar con
un modelo propietario, basta con cambiar `EMBEDDING_MODEL` en
`config.py`, pero **no es necesario** para que el proyecto funcione.

---

## 4. Requisitos previos

- **Python 3.10 o superior**.
- Al menos **4 GB de RAM libres** (el modelo `BAAI/bge-m3` ocupa
  ~2.3 GB en disco y algo más en memoria al cargarse). Si tu equipo
  tiene pocos recursos, revisa la sección
  [5.4 Usar un modelo más liviano](#54-opcional-usar-un-modelo-de-embeddings-más-liviano).
- Conexión a internet **solo la primera vez**, para descargar el
  modelo de embeddings desde Hugging Face. Luego queda cacheado en
  `~/.cache/huggingface` y el proyecto funciona sin internet.
- No se requiere GPU: el proyecto corre en CPU por defecto, aunque es
  más lento que con GPU.

---

## 5. Instalación

### 5.1. Clonar / descomprimir el proyecto

Descomprime la carpeta del proyecto (o clónala si la subes a un
repositorio Git) y entra a ella:

```bash
cd rag-chunking-embeddings-vectordb
```

### 5.2. Crear un entorno virtual (recomendado)

```bash
python3 -m venv .venv

# En Linux / macOS:
source .venv/bin/activate

# En Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

### 5.3. Instalar las dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

La primera vez que ejecutes el pipeline, `sentence-transformers`
descargará automáticamente el modelo `BAAI/bge-m3` (~2.3 GB). Esto
puede tardar varios minutos según tu conexión.

### 5.4. (Opcional) Usar un modelo de embeddings más liviano

Si tu equipo tiene pocos recursos, puedes usar un modelo mucho más
pequeño (~470 MB) definiendo una variable de entorno antes de
ejecutar los scripts:

```bash
# Linux / macOS
export EMBEDDING_MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Windows (PowerShell)
$env:EMBEDDING_MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

También puedes pasarlo directamente como argumento:
`python -m src.ingest --model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

---

## 6. Uso

### 6.1. Agregar tus documentos

Coloca tus archivos `.txt`, `.md` o `.pdf` dentro de
`data/documentos/`. El proyecto ya incluye `ejemplo_rag.md` para que
puedas probar el pipeline sin necesidad de agregar nada.

### 6.2. Ejecutar la ingesta (chunking + embeddings + indexación)

Estrategia por defecto: **recursive character splitting** (diapositiva 8,
la estrategia estándar de producción):

```bash
python -m src.ingest
```

Verás una salida similar a:

```
[ingest] Cargando documentos desde: data/documentos
[ingest] 1 documento(s) cargado(s).
[embeddings] Cargando modelo 'BAAI/bge-m3' en dispositivo 'cpu'...
[embeddings] Modelo cargado. Dimensión del vector: 1024
[ingest] Procesando 'ejemplo_rag.md' con estrategia 'recursive'...
[ingest]   -> 4 chunk(s) generado(s) e indexado(s).
[ingest] Listo. Total de chunks indexados en esta ejecución: 4
[ingest] Tamaño actual de la colección 'diplomado_rag': 4 chunks.
```

#### Probar otras estrategias de chunking (U4)

```bash
# Chunking semántico (diapositiva 9): corta donde cambia el tema
python -m src.ingest --strategy semantic

# Jerárquico / parent-child (diapositiva 10): indexa chunks pequeños
# pero conserva el chunk "padre" con contexto amplio en los metadatos
python -m src.ingest --strategy parent_child
```

#### Ajustar tamaño de chunk y overlap (diapositiva 12)

```bash
python -m src.ingest --chunk-size 512 --chunk-overlap 75
```

#### Reindexar desde cero

```bash
python -m src.ingest --reset
```

### 6.3. Consultar la base vectorial (retrieval)

```bash
python -m src.query "¿Cuáles son las etapas de un pipeline RAG?"
```

Salida esperada:

```
Pregunta: ¿Cuáles son las etapas de un pipeline RAG?
Top 5 resultado(s):

[1] similitud=0.8123  fuente=ejemplo_rag.md  estrategia=recursive
    Un pipeline RAG típico sigue estos pasos: primero se extraen y limpian
    los documentos originales (ingesta). Luego se dividen en fragmentos...
...
```

Puedes ajustar cuántos resultados quieres recibir:

```bash
python -m src.query "¿Qué modelo de embeddings conviene para español?" --top-k 3
```

---

## 7. Cómo se conecta esto con la presentación de clase

- **Chunking (U4):** `src/chunking.py` implementa las tres familias
  vistas en la diapositiva 7 (fija, semántica y avanzada/jerárquica).
  Los valores por defecto de tamaño y overlap en `config.py`
  corresponden a las reglas prácticas de las diapositivas 8 y 12
  (512 tokens, overlap ≈ 15%).
- **Embeddings (U5):** `src/embeddings.py` usa `BAAI/bge-m3`, el
  modelo open source recomendado en la diapositiva 20 para contenido
  multilingüe / español (líder en el benchmark MIRACL). La métrica de
  similitud utilizada es **coseno**, la estándar según la diapositiva 17.
- **Base de datos vectorial (U6):** `src/vector_store.py` usa
  **Chroma**, mencionada en la diapositiva 23 como la opción ideal
  para prototipado y desarrollo local por su curva de entrada mínima.
  Internamente usa indexación **HNSW** (diapositiva 25).
- **Metadatos y filtrado (diapositiva 26):** `VectorStore.similarity_search`
  acepta un parámetro `where` para combinar búsqueda semántica con
  filtros exactos por metadatos (por ejemplo, `{"source": "informe_2026.pdf"}`),
  sentando las bases de la búsqueda híbrida mencionada en el cierre
  de la clase.

---

## 8. Próximos pasos (Unidad 7)

Este proyecto cubre hasta el paso de **Retrieval**. Para completar un
sistema RAG (agregar la etapa de **Generación**), la siguiente clase
(U7) aborda la orquestación con frameworks como **LangChain** o
**LlamaIndex**, que permiten:

1. Tomar los chunks recuperados por `src/query.py`.
2. Construir un *prompt* que incluya esos chunks como contexto.
3. Enviarlo a un LLM (puede ser también open source, como Llama 3 o
   Qwen, ejecutado localmente con [Ollama](https://ollama.com/), para
   mantener el proyecto 100% libre de costos por token).
4. Devolver una respuesta final generada, citando las fuentes.

Este proyecto ya deja lista la interfaz de `similarity_search` para
que ese paso se pueda conectar directamente.

---

## 9. Solución de problemas (troubleshooting)

**La descarga del modelo es muy lenta o falla.**
Verifica tu conexión a internet. Si el problema persiste, prueba con
el modelo más liviano indicado en la sección
[5.4](#54-opcional-usar-un-modelo-de-embeddings-más-liviano).

**Error de memoria (`OOM` / `Killed`) al cargar el modelo.**
Usa el modelo liviano `paraphrase-multilingual-MiniLM-L12-v2` en lugar
de `BAAI/bge-m3`, o reduce el tamaño del lote cerrando otras
aplicaciones.

**`ModuleNotFoundError` al ejecutar `python -m src.ingest`.**
Asegúrate de ejecutar el comando desde la carpeta raíz del proyecto
(donde está `config.py`) y de haber activado el entorno virtual con
las dependencias instaladas.

**Quiero borrar todo y empezar de nuevo.**
Elimina la carpeta `vectorstore/` (o usa `python -m src.ingest --reset`)
y vuelve a ejecutar la ingesta.

---

## 10. Créditos

Proyecto elaborado como material de apoyo para el
**Diplomado en Desarrollo de Software con IA Generativa y Agentes
Inteligentes — Módulo 2: Arquitecturas RAG y Gestión del Conocimiento**,
en base a los contenidos de la Semana 2 (Unidades 4, 5 y 6).
