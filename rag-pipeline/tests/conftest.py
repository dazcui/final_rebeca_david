import hashlib
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))


def _fake_embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embebedor determinista y liviano, usado SOLO en pruebas, para no
    depender de la descarga del modelo real (~470MB desde Hugging Face)
    ni de una GPU/CPU intensiva durante el testing.

    No captura significado semántico real; solo garantiza que textos
    idénticos produzcan vectores idénticos y sirve para validar la
    "plomería" (almacenamiento, conteo, metadata) de forma rápida y
    100% offline.
    """
    vectores = []
    for texto in texts:
        digest = hashlib.md5(texto.encode("utf-8")).digest()
        vector = [b / 255.0 for b in digest[:16]]
        vectores.append(vector)
    return vectores


@pytest.fixture
def fake_embeddings(monkeypatch):
    """Reemplaza embed_texts en todos los módulos que ya lo importaron."""
    monkeypatch.setattr("rag.embeddings.embed_texts", _fake_embed_texts)
    monkeypatch.setattr("rag.vector_store.embed_texts", _fake_embed_texts)
    return _fake_embed_texts


@pytest.fixture
def temp_vector_store(fake_embeddings):
    """VectorStore respaldado por un directorio temporal, con embeddings falsos."""
    from rag.vector_store import VectorStore

    with tempfile.TemporaryDirectory() as tmpdir:
        store = VectorStore(persist_directory=tmpdir, collection_name="test_collection")
        try:
            yield store
        finally:
            # Libera los archivos HNSW antes de limpiar el directorio en Windows.
            store.client.close()
