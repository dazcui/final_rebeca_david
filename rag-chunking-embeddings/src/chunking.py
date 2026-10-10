"""
chunking.py
===========
Implementa las estrategias de segmentación de texto (chunking) vistas
en la Unidad 4:

1. recursive_character_split  -> Estrategia por defecto (diapositiva 8)
2. semantic_split              -> Chunking semántico (diapositiva 9)
3. parent_child_split          -> Jerárquico / small-to-big (diapositiva 10)

Todas las funciones reciben texto plano y devuelven una lista de
diccionarios con la forma:
    {"text": str, "metadata": dict}

De esta manera, embeddings.py y vector_store.py pueden trabajar con
cualquiera de las tres estrategias de forma intercambiable.
"""

from __future__ import annotations

import re
from typing import List, Dict, Any, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter

import config


# -------------------------------------------------------------------------
# 1. Recursive Character Splitting (estrategia base, diapositiva 8)
# -------------------------------------------------------------------------
def recursive_character_split(
    text: str,
    chunk_size: int = config.CHUNK_SIZE,
    chunk_overlap: int = config.CHUNK_OVERLAP,
    metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Divide el texto probando separadores en orden de prioridad
    (párrafo -> línea -> oración -> palabra) hasta alcanzar el tamaño
    objetivo, preservando la estructura natural del documento.

    Nota: RecursiveCharacterTextSplitter mide en caracteres, no en
    tokens exactos. Para la mayoría de textos en español, 1 token
    equivale aproximadamente a 4 caracteres, por lo que aquí se
    multiplica chunk_size por ~4 para aproximar tokens -> caracteres.
    Si necesitas conteo exacto de tokens, integra un tokenizer como
    tiktoken o el tokenizer del propio modelo de embeddings.
    """
    metadata = metadata or {}
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size * 4,
        chunk_overlap=chunk_overlap * 4,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    return [
        {
            "text": chunk,
            "metadata": {**metadata, "strategy": "recursive", "chunk_index": i},
        }
        for i, chunk in enumerate(chunks)
    ]


# -------------------------------------------------------------------------
# 2. Chunking semántico (diapositiva 9)
# -------------------------------------------------------------------------
def _split_sentences(text: str) -> List[str]:
    """Segmentación simple de oraciones basada en signos de puntuación."""
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def semantic_split(
    text: str,
    embedder,  # instancia de src.embeddings.EmbeddingModel
    threshold: float = config.SEMANTIC_THRESHOLD,
    min_chunk_tokens: int = 40,
    metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Se embebe cada oración y se corta donde la similitud coseno entre
    oraciones consecutivas cae por debajo de `threshold`: ahí cambia
    el tema (ver diapositiva 9).

    Advertencia (según diapositiva 9 del material): si el umbral es
    muy sensible se generan fragmentos muy cortos (~40-50 tokens) que
    pierden contexto y bajan la precisión. Por eso se aplica un piso
    mínimo `min_chunk_tokens` para fusionar chunks demasiado pequeños.
    """
    import numpy as np

    metadata = metadata or {}
    sentences = _split_sentences(text)
    if len(sentences) <= 1:
        return [{"text": text, "metadata": {**metadata, "strategy": "semantic", "chunk_index": 0}}]

    embeddings = embedder.embed_texts(sentences)

    def cosine(a, b):
        a, b = np.array(a), np.array(b)
        return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

    groups: List[List[str]] = [[sentences[0]]]
    for i in range(1, len(sentences)):
        sim = cosine(embeddings[i - 1], embeddings[i])
        if sim < threshold:
            groups.append([sentences[i]])
        else:
            groups[-1].append(sentences[i])

    # Fusiona grupos demasiado pequeños con el siguiente para evitar
    # fragmentos que pierdan contexto (piso mínimo de tokens).
    merged: List[str] = []
    buffer = ""
    for group in groups:
        candidate = " ".join(group)
        buffer = f"{buffer} {candidate}".strip()
        if len(buffer.split()) >= min_chunk_tokens:
            merged.append(buffer)
            buffer = ""
    if buffer:
        if merged:
            merged[-1] = f"{merged[-1]} {buffer}".strip()
        else:
            merged.append(buffer)

    return [
        {"text": chunk, "metadata": {**metadata, "strategy": "semantic", "chunk_index": i}}
        for i, chunk in enumerate(merged)
    ]


# -------------------------------------------------------------------------
# 3. Jerárquico / Parent-Child (small-to-big, diapositiva 10)
# -------------------------------------------------------------------------
def parent_child_split(
    text: str,
    parent_size: int = config.PARENT_CHUNK_SIZE,
    child_size: int = config.CHILD_CHUNK_SIZE,
    child_overlap: int = config.CHILD_CHUNK_OVERLAP,
    metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Genera chunks "hijo" pequeños (los que se embeben e indexan para
    maximizar precisión de búsqueda) que apuntan a un chunk "padre"
    más grande (el que realmente se entrega al LLM como contexto).

    Devuelve una lista de chunks HIJOS. Cada uno incluye en su
    metadata el texto completo del PADRE bajo la clave "parent_text",
    para que el paso de retrieval pueda devolver el contexto amplio.
    """
    metadata = metadata or {}

    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=parent_size * 4,
        chunk_overlap=0,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    parents = parent_splitter.split_text(text)

    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=child_size * 4,
        chunk_overlap=child_overlap * 4,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    children: List[Dict[str, Any]] = []
    for p_idx, parent_text in enumerate(parents):
        child_texts = child_splitter.split_text(parent_text)
        for c_idx, child_text in enumerate(child_texts):
            children.append(
                {
                    "text": child_text,
                    "metadata": {
                        **metadata,
                        "strategy": "parent_child",
                        "parent_index": p_idx,
                        "child_index": c_idx,
                        "parent_text": parent_text,
                    },
                }
            )
    return children


# -------------------------------------------------------------------------
# Fábrica de estrategias
# -------------------------------------------------------------------------
STRATEGIES = {
    "recursive": recursive_character_split,
    "semantic": semantic_split,
    "parent_child": parent_child_split,
}


def chunk_text(strategy: str, text: str, **kwargs) -> List[Dict[str, Any]]:
    """Punto de entrada único: elige la estrategia por nombre."""
    if strategy not in STRATEGIES:
        raise ValueError(
            f"Estrategia '{strategy}' no reconocida. Opciones: {list(STRATEGIES)}"
        )
    return STRATEGIES[strategy](text, **kwargs)
