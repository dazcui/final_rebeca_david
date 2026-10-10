"""
Almacenamiento vectorial local mediante ChromaDB (modo embebido/persistente,
sin necesidad de levantar un servidor aparte).
"""
from dataclasses import dataclass

import chromadb

from config.settings import settings
from rag.chunking import Chunk
from rag.embeddings import embed_texts


@dataclass
class RetrievedChunk:
    text: str
    source: str
    page: int | None
    score: float  # similitud, 0 a 1 (más alto = más relevante)


class VectorStore:
    def __init__(self, persist_directory: str | None = None, collection_name: str | None = None):
        self.client = chromadb.PersistentClient(path=persist_directory or settings.VECTOR_DB_DIR)
        self.collection = self.client.get_or_create_collection(
            name=collection_name or settings.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: list[Chunk]) -> None:
        """Genera embeddings para los chunks dados y los inserta en la colección."""
        if not chunks:
            return
        embeddings = embed_texts([c.text for c in chunks])
        self.collection.add(
            ids=[c.chunk_id for c in chunks],
            embeddings=embeddings,
            documents=[c.text for c in chunks],
            metadatas=[
                {"source": c.source, "page": c.page or -1, "doc_type": c.doc_type}
                for c in chunks
            ],
        )

    def query(self, query_text: str, top_k: int = 4) -> list[RetrievedChunk]:
        """Búsqueda semántica: devuelve los `top_k` chunks más similares a la consulta."""
        if self.count() == 0:
            return []
        query_embedding = embed_texts([query_text])[0]
        resultados = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)

        chunks: list[RetrievedChunk] = []
        for texto, metadata, distancia in zip(
            resultados["documents"][0], resultados["metadatas"][0], resultados["distances"][0]
        ):
            similitud = max(0.0, 1.0 - distancia)  # distancia coseno -> similitud aprox.
            pagina = metadata.get("page")
            chunks.append(
                RetrievedChunk(
                    text=texto,
                    source=metadata.get("source", "desconocido"),
                    page=None if pagina in (None, -1) else pagina,
                    score=similitud,
                )
            )
        return chunks

    def get_all(self) -> list[dict]:
        """Devuelve todos los chunks almacenados (usado para construir el índice BM25)."""
        if self.count() == 0:
            return []
        resultado = self.collection.get(include=["documents", "metadatas"])
        registros = []
        for texto, metadata in zip(resultado["documents"], resultado["metadatas"]):
            pagina = metadata.get("page")
            registros.append(
                {
                    "text": texto,
                    "source": metadata.get("source", "desconocido"),
                    "page": None if pagina in (None, -1) else pagina,
                }
            )
        return registros

    def count(self) -> int:
        return self.collection.count()

    def reset(self) -> None:
        """Elimina todos los datos de la colección (útil para re-ingestar desde cero)."""
        nombre = self.collection.name
        self.client.delete_collection(nombre)
        self.collection = self.client.get_or_create_collection(
            name=nombre, metadata={"hnsw:space": "cosine"}
        )
