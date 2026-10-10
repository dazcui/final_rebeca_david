"""
query.py
========
Script de consulta (retrieval). Toma una pregunta en lenguaje natural,
la convierte en un embedding y busca los chunks más similares en la
base vectorial (Unidad 6, diapositiva 22: "dame los k vectores más
parecidos a este").

Este proyecto cubre el tramo Ingesta -> Chunking -> Embeddings ->
Vector DB -> Retrieval. La Generación (pasar estos chunks a un LLM
para redactar una respuesta) corresponde a la Unidad 7 (orquestación
con LangChain / LlamaIndex), fuera del alcance de esta sesión -- ver
la sección "Próximos pasos" del README.

Uso:
    python -m src.query "¿Qué es el chunking semántico?"
    python -m src.query "¿Cuándo usar Qdrant?" --top-k 3
"""

from __future__ import annotations

import argparse

import config
from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore


def parse_args():
    parser = argparse.ArgumentParser(description="Consulta la base vectorial.")
    parser.add_argument("question", type=str, help="Pregunta en lenguaje natural")
    parser.add_argument("--top-k", type=int, default=config.TOP_K)
    parser.add_argument("--model", type=str, default=config.EMBEDDING_MODEL)
    return parser.parse_args()


def run(args):
    embedder = EmbeddingModel(model_name=args.model)
    store = VectorStore()

    if store.count() == 0:
        print("[query] La colección está vacía. Ejecuta primero: python -m src.ingest")
        return

    query_vector = embedder.embed_query(args.question)
    hits = store.similarity_search(query_vector, top_k=args.top_k)

    print(f"\nPregunta: {args.question}")
    print(f"Top {len(hits)} resultado(s):\n")
    for rank, hit in enumerate(hits, 1):
        source = hit["metadata"].get("source", "desconocido")
        strategy = hit["metadata"].get("strategy", "?")
        print(f"[{rank}] similitud={hit['similarity']:.4f}  fuente={source}  estrategia={strategy}")
        print(f"    {hit['text'][:300].strip()}...\n")


if __name__ == "__main__":
    run(parse_args())
