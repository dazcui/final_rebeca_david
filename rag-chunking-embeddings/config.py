"""
config.py
=========
Configuración centralizada del proyecto. Todos los valores pueden
sobreescribirse mediante variables de entorno (ver archivo .env.example),
o pasando argumentos por línea de comandos en ingest.py / query.py.

No se requiere ninguna API key: todo el pipeline corre 100% en local
con modelos y bases de datos open source.
"""

import os
from pathlib import Path

# -----------------------------------------------------------------------
# Rutas del proyecto
# -----------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = Path(os.getenv("DOCS_DIR", BASE_DIR / "data" / "documentos"))
PERSIST_DIR = Path(os.getenv("PERSIST_DIR", BASE_DIR / "vectorstore"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "manual_mantenimiento_preventivo")

# -----------------------------------------------------------------------
# Modelo de embeddings (U5 de la presentación)
# -----------------------------------------------------------------------
# BAAI/bge-m3 es el modelo recomendado en la diapositiva 20 para
# contenido multilingüe / español (líder en el benchmark MIRACL) y es
# completamente open source (licencia MIT). Requiere ~2.3 GB de descarga
# y algo más de RAM/CPU que un modelo ligero.
#
# Si tu equipo tiene pocos recursos, puedes cambiar la variable de
# entorno EMBEDDING_MODEL por una alternativa más liviana, por ejemplo:
#   sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2  (~470 MB)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Dispositivo de cómputo: "cpu", "cuda" o "mps" (Apple Silicon).
# "cpu" funciona en cualquier equipo, aunque es más lento.
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")

# -----------------------------------------------------------------------
# Parámetros de chunking (U4 de la presentación)
# -----------------------------------------------------------------------
# Valores por defecto según la diapositiva 8 (recursive character
# splitting) y la regla práctica de la diapositiva 12: overlap ≈ 15%.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 128))          # en tokens aprox.
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 25))

# Umbral de similitud para chunking semántico (diapositiva 9).
# Si la similitud coseno entre oraciones consecutivas cae por debajo de
# este valor, se considera un cambio de tema y se corta ahí.
SEMANTIC_THRESHOLD = float(os.getenv("SEMANTIC_THRESHOLD", 0.75))

# Parámetros para chunking jerárquico / parent-child (diapositiva 10).
PARENT_CHUNK_SIZE = int(os.getenv("PARENT_CHUNK_SIZE", 1500))
CHILD_CHUNK_SIZE = int(os.getenv("CHILD_CHUNK_SIZE", 200))
CHILD_CHUNK_OVERLAP = int(os.getenv("CHILD_CHUNK_OVERLAP", 30))

# -----------------------------------------------------------------------
# Parámetros de indexación / búsqueda vectorial (U6 de la presentación)
# -----------------------------------------------------------------------
# Chroma usa HNSW por defecto (diapositiva 25). "cosine" es la métrica
# estándar para embeddings de texto (diapositiva 17).
DISTANCE_METRIC = os.getenv("DISTANCE_METRIC", "cosine")
TOP_K = int(os.getenv("TOP_K", 5))
