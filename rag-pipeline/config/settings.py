"""
Configuración centralizada del proyecto RAG.

Todo corre localmente por defecto: el modelo de embeddings se descarga
una vez desde Hugging Face (open source, gratuito) y la generación usa
Ollama en tu propia máquina (modelos open-weight, sin costo por token).
No se requiere ninguna clave de API para el funcionamiento por defecto.
"""
import os
from pathlib import Path
from dataclasses import dataclass, field

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
os.environ.setdefault("TIKTOKEN_CACHE_DIR", str(BASE_DIR / ".cache" / "tiktoken"))


@dataclass(frozen=True)
class Settings:
    # --- Rutas ---
    RAW_DATA_DIR: str = os.getenv("RAW_DATA_DIR", str(BASE_DIR / "data/raw"))
    PROCESSED_DATA_DIR: str = os.getenv("PROCESSED_DATA_DIR", str(BASE_DIR / "data/processed"))
    VECTOR_DB_DIR: str = os.getenv("VECTOR_DB_DIR", str(BASE_DIR / "data/chroma_db"))
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "manual_mantenimiento_preventivo")

    # --- Chunking (Unidad 3) ---
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))         # caracteres por chunk
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "80"))

    # --- Embeddings (Unidad 1) ---
    # Modelo local, multilingüe, liviano (~470MB, se descarga una sola vez).
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2"
    )

    # --- Retrieval (Unidad 1) ---
    TOP_K: int = int(os.getenv("TOP_K", "4"))
    HYBRID_SEARCH: bool = os.getenv("HYBRID_SEARCH", "true").lower() == "true"
    VECTOR_WEIGHT: float = float(os.getenv("VECTOR_WEIGHT", "0.6"))  # peso búsqueda semántica
    BM25_WEIGHT: float = float(os.getenv("BM25_WEIGHT", "0.4"))      # peso búsqueda por palabras clave

    # --- Agentic RAG (Unidad 2 · tendencias 2026) ---
    AGENTIC_MODE: bool = os.getenv("AGENTIC_MODE", "true").lower() == "true"
    MIN_RELEVANCE_SCORE: float = float(os.getenv("MIN_RELEVANCE_SCORE", "0.35"))
    MAX_RETRIEVAL_ROUNDS: int = int(os.getenv("MAX_RETRIEVAL_ROUNDS", "2"))

    # --- Generación (Ollama, local y gratuito) ---
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    GENERATION_TEMPERATURE: float = float(os.getenv("GENERATION_TEMPERATURE", "0"))


settings = Settings()
