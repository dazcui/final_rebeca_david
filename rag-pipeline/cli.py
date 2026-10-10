"""
CLI principal del proyecto RAG aplicado.

Comandos:
    python cli.py ingest [--source data/raw] [--reset]
    python cli.py ask "pregunta" [--top-k 4] [--agentic] [--no-generate]
    python cli.py compare "pregunta" [--top-k 4]
"""
import argparse
import json

from comparison.rag_vs_long_context import compare as compare_costs
from ingestion.pipeline import run_pipeline
from rag.augmentation import build_prompt
from rag.generator import OllamaUnavailableError, generate_answer
from rag.retriever import Retriever
from rag.vector_store import VectorStore


def cmd_ingest(args: argparse.Namespace) -> None:
    resumen = run_pipeline(source_dir=args.source, reset=args.reset)
    print(json.dumps(resumen, indent=2, ensure_ascii=False))


def cmd_ask(args: argparse.Namespace) -> None:
    store = VectorStore()
    if store.count() == 0:
        print("La base de conocimiento está vacía. Ejecuta primero: python cli.py ingest")
        return

    retriever = Retriever(store)

    if args.agentic:
        resultado = retriever.agentic_search(args.query, top_k=args.top_k)
        chunks = resultado.chunks
        print("--- Trazabilidad de recuperación (Agentic RAG) ---")
        for ronda in resultado.rounds:
            print(
                f"  Ronda {ronda['round']}: top_k={ronda['top_k']}, "
                f"score_promedio={ronda['avg_score']}, resultados={ronda['n_results']}"
            )
    else:
        chunks = retriever.search(args.query, top_k=args.top_k)

    print(f"\n--- {len(chunks)} fragmento(s) recuperado(s) ---")
    for i, c in enumerate(chunks, start=1):
        ubicacion = c.source + (f" (p.{c.page})" if c.page else "")
        print(f"  [{i}] {ubicacion} | score={c.score:.3f}")

    prompt = build_prompt(args.query, chunks)

    if args.no_generate:
        print("\n--- Prompt aumentado (modo solo-recuperación) ---")
        print(prompt)
        return

    print("\n--- Generando respuesta con Ollama... ---")
    try:
        respuesta = generate_answer(prompt)
        print(f"\n{respuesta}")
    except OllamaUnavailableError as exc:
        print(f"\n{exc}")
        print("\nMostrando el prompt aumentado como alternativa (modo solo-recuperación):\n")
        print(prompt)


def cmd_compare(args: argparse.Namespace) -> None:
    resultado = compare_costs(args.query, top_k=args.top_k)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sistema RAG aplicado — CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_ingest = subparsers.add_parser("ingest", help="Ejecuta el pipeline de ingesta de documentos")
    p_ingest.add_argument("--source", type=str, default=None, help="Carpeta de documentos (default: data/raw)")
    p_ingest.add_argument("--reset", action="store_true", help="Reinicia la colección antes de ingerir")
    p_ingest.set_defaults(func=cmd_ingest)

    p_ask = subparsers.add_parser("ask", help="Realiza una pregunta al sistema RAG")
    p_ask.add_argument("query", type=str, help="Pregunta en lenguaje natural")
    p_ask.add_argument("--top-k", type=int, default=None, help="Número de fragmentos a recuperar")
    p_ask.add_argument("--agentic", action="store_true", help="Usa el modo Agentic RAG (recuperación iterativa)")
    p_ask.add_argument(
        "--no-generate", action="store_true", help="Solo recupera y muestra el prompt, sin llamar al LLM"
    )
    p_ask.set_defaults(func=cmd_ask)

    p_compare = subparsers.add_parser(
        "compare", help="Compara el costo de contexto: RAG vs. contexto largo (Unidad 2)"
    )
    p_compare.add_argument("query", type=str)
    p_compare.add_argument("--top-k", type=int, default=None)
    p_compare.set_defaults(func=cmd_compare)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
