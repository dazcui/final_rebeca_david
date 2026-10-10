"""
vector_store.py
================
Envoltorio sobre ChromaDB (Unidad 6): base de datos vectorial open
source, embebida (no requiere servidor externo) e ideal para
prototipado local, tal como se menciona en la diapositiva 23.

Usa persistencia en disco (PersistentClient) para que la colección
sobreviva entre ejecuciones, e indexación HNSW con métrica coseno
(diapositivas 17 y 25).
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
import uuid

import config


class VectorStore:
    def __init__(
        self,
        persist_dir: str = str(config.PERSIST_DIR),
        collection_name: str = config.COLLECTION_NAME,
        distance_metric: str = config.DISTANCE_METRIC,
    ):
        import chromadb

        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": distance_metric},  # coseno por defecto
        )

    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> None:
        """
        Inserta chunks + sus vectores + metadatos en la colección.
        `chunks` debe tener la forma [{"text": ..., "metadata": {...}}, ...]
        producida por src/chunking.py.
        """
        ids = [str(uuid.uuid4()) for _ in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [self._clean_metadata(c.get("metadata", {})) for c in chunks]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    @staticmethod
    def _clean_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Chroma solo acepta str/int/float/bool en metadatos."""
        clean = {}
        for k, v in metadata.items():
            if isinstance(v, (str, int, float, bool)):
                clean[k] = v
            else:
                clean[k] = str(v)
        return clean

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = config.TOP_K,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda por similitud (ANN). `where` permite filtrado por
        metadatos, p. ej. {"strategy": "recursive"} (diapositiva 26:
        búsqueda híbrida = similitud semántica + reglas exactas).
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )
        hits = []
        for doc, meta, dist, _id in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
            results["ids"][0],
        ):
            hits.append(
                {
                    "id": _id,
                    "text": doc,
                    "metadata": meta,
                    "distance": dist,
                    "similarity": 1 - dist,  # válido para métrica coseno
                }
            )
        return hits

    def count(self) -> int:
        return self.collection.count()

    def reset_collection(self) -> None:
        """Borra y vuelve a crear la colección (útil para reindexar)."""
        name = self.collection.name
        metadata = self.collection.metadata
        self.client.delete_collection(name)
        self.collection = self.client.get_or_create_collection(name=name, metadata=metadata)
