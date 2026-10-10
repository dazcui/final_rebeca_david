"""Consulta el manual con recuperación híbrida y generación local."""
import json
from pathlib import Path
from rag.retriever import Retriever
from rag.vector_store import VectorStore
from rag.augmentation import build_prompt
from rag.generator import generate_answer

root = Path(__file__).resolve().parents[2]
questions = json.loads((root / "preguntas_manual.json").read_text(encoding="utf-8"))
store = VectorStore()
if not store.count():
    raise SystemExit("Primero ejecuta python cli.py ingest")
retriever = Retriever(store)
output = root / "resultados" / "proyecto_2_respuestas.json"
output.parent.mkdir(exist_ok=True)
results = []
for question in questions:
    chunks = retriever.search(question, top_k=5)
    answer = generate_answer(build_prompt(question, chunks))
    results.append({"pregunta": question, "respuesta": answer,
                    "fragmentos": [vars(chunk) for chunk in chunks]})
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(question, "\n", answer, "\n", flush=True)
print(output)
