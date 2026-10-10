"""Ejecuta las preguntas del manual y conserva evidencia de recuperación."""
import json
from pathlib import Path
from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore

root = Path(__file__).resolve().parents[2]
questions = json.loads((root / "preguntas_manual.json").read_text(encoding="utf-8"))
embedder, store = EmbeddingModel(), VectorStore()
if not store.count():
    raise SystemExit("Primero ejecuta python -m src.ingest")
results = []
for question in questions:
    hits = store.similarity_search(embedder.embed_query(question), top_k=5)
    results.append({"pregunta": question, "fragmentos": hits})
    print(question, "->", hits[0]["metadata"]["source"])
output = root / "resultados" / "proyecto_1_consultas.json"
output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(output)
