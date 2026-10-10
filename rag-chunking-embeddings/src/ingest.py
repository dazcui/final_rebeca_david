"""
ingest.py
=========
Script principal del pipeline de ingesta. Implementa el tramo
completo que se ve en la diapositiva 3:

    Ingesta -> Chunking (U4) -> Embeddings (U5) -> Vector DB (U6)

Uso:
    python -m src.ingest
    python -m src.ingest --input data/documentos --strategy semantic
    python -m src.ingest --strategy parent_child --reset

Ejecuta `python -m src.ingest --help` para ver todas las opciones.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import config
from src import utils, chunking
from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore


def parse_args():
    parser = argparse.ArgumentParser(description="Ingesta documentos al vector store.")
    parser.add_argument("--input", type=str, default=str(config.DOCS_DIR),
                         help="Carpeta con documentos .txt/.md/.pdf")
    parser.add_argument("--strategy", type=str, default="recursive",
                         choices=list(chunking.STRATEGIES.keys()),
                         help="Estrategia de chunking (U4)")
    parser.add_argument("--chunk-size", type=int, default=config.CHUNK_SIZE)
    parser.add_argument("--chunk-overlap", type=int, default=config.CHUNK_OVERLAP)
    parser.add_argument("--model", type=str, default=config.EMBEDDING_MODEL,
                         help="Nombre del modelo de embeddings (Hugging Face)")
    parser.add_argument("--reset", action="store_true",
                         help="Borra la colección antes de indexar (reindexado limpio)")
    return parser.parse_args()


def run(args):
    print(f"[ingest] Cargando documentos desde: {args.input}")
    documents = utils.load_documents(Path(args.input))
    print(f"[ingest] {len(documents)} documento(s) cargado(s).")

    if not documents:
        print("[ingest] No hay documentos para procesar. Agrega archivos a data/documentos/.")
        return

    embedder = EmbeddingModel(model_name=args.model)
    store = VectorStore()

    if args.reset:
        print("[ingest] Reseteando colección existente...")
        store.reset_collection()

    total_chunks = 0
    for doc in documents:
        source = doc["metadata"]["source"]
        print(f"[ingest] Procesando '{source}' con estrategia '{args.strategy}'...")

        kwargs = {"metadata": doc["metadata"]}
        if args.strategy == "recursive":
            kwargs["chunk_size"] = args.chunk_size
            kwargs["chunk_overlap"] = args.chunk_overlap
            chunks = chunking.chunk_text("recursive", doc["text"], **kwargs)
        elif args.strategy == "semantic":
            kwargs["embedder"] = embedder
            chunks = chunking.chunk_text("semantic", doc["text"], **kwargs)
        else:  # parent_child
            chunks = chunking.chunk_text("parent_child", doc["text"], **kwargs)

        if not chunks:
            continue

        texts = [c["text"] for c in chunks]
        vectors = embedder.embed_texts(texts)
        store.add_chunks(chunks, vectors)
        total_chunks += len(chunks)
        print(f"[ingest]   -> {len(chunks)} chunk(s) generado(s) e indexado(s).")

    print(f"[ingest] Listo. Total de chunks indexados en esta ejecución: {total_chunks}")
    print(f"[ingest] Tamaño actual de la colección '{config.COLLECTION_NAME}': {store.count()} chunks.")


if __name__ == "__main__":
    run(parse_args())
