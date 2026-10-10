"""
El Retriever (Unidad 1): encuentra los fragmentos más relevantes para una
consulta dada.

Implementa dos mejoras señaladas como tendencias 2026 en el material:

  - Búsqueda híbrida: combina similitud vectorial (densa) con BM25
    (coincidencia de palabras clave), ponderando ambos puntajes.
  - Agentic RAG (versión simplificada): en vez de recuperar una sola vez,
    evalúa si la evidencia encontrada es suficientemente relevante y, si
    no lo es, reintenta ampliando la búsqueda — sin necesidad de un
    framework de agentes externo (LangGraph, CrewAI, etc. se mencionan en
    el material como alternativas más completas para flujos complejos).
"""
from dataclasses import dataclass
import re

from rank_bm25 import BM25Okapi

from config.settings import settings
from rag.vector_store import RetrievedChunk, VectorStore

# Expansiones documentadas en la sección 3.1 del manual. Ayudan a recuperar
# la definición y el cronograma cuando la consulta contiene solo la sigla.
ACRONYMS = {"HGP": "Hot Gas Path Inspection", "MO": "Major Overhaul",
            "RMI": "Remote Minor Inspection"}


def expand_query(query: str) -> str:
    words = set(re.findall(r"\b\w+\b", query.upper()))
    definitions = [definition for acronym, definition in ACRONYMS.items() if acronym in words]
    return " ".join([query, *definitions])


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+(?:-\w+)*", text.lower())


@dataclass
class AgenticSearchResult:
    chunks: list[RetrievedChunk]
    rounds: list[dict]  # traza de cada ronda de recuperación (para transparencia/debug)


class Retriever:
    def __init__(self, vector_store: VectorStore):
        self.store = vector_store
        self._bm25: BM25Okapi | None = None
        self._bm25_corpus: list[dict] = []

    # --- Búsqueda semántica pura -------------------------------------------

    def semantic_search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        return self.store.query(query, top_k=top_k)

    # --- Búsqueda por palabras clave (BM25) ---------------------------------

    def _ensure_bm25_index(self) -> None:
        if self._bm25 is not None:
            return
        self._bm25_corpus = self.store.get_all()
        corpus_tokenizado = [tokenize(r["text"]) for r in self._bm25_corpus]
        self._bm25 = BM25Okapi(corpus_tokenizado) if corpus_tokenizado else None

    def keyword_search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        self._ensure_bm25_index()
        if self._bm25 is None or not self._bm25_corpus:
            return []

        puntajes = self._bm25.get_scores(tokenize(query))
        maximo = max(puntajes) if len(puntajes) and max(puntajes) > 0 else 1.0

        ranking = sorted(
            zip(puntajes, self._bm25_corpus), key=lambda par: par[0], reverse=True
        )[:top_k]

        return [
            RetrievedChunk(text=r["text"], source=r["source"], page=r["page"], score=s / maximo)
            for s, r in ranking
        ]

    # --- Búsqueda híbrida ----------------------------------------------------

    def hybrid_search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        semantico = self.semantic_search(query, top_k=top_k * 2)
        por_palabra_clave = self.keyword_search(query, top_k=top_k * 2)

        combinados: dict[tuple[str, int | None, str], float] = {}
        for r in semantico:
            clave = (r.source, r.page, r.text)
            combinados[clave] = combinados.get(clave, 0.0) + settings.VECTOR_WEIGHT * r.score
        for r in por_palabra_clave:
            clave = (r.source, r.page, r.text)
            combinados[clave] = combinados.get(clave, 0.0) + settings.BM25_WEIGHT * r.score

        ranking = sorted(combinados.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
        return [
            RetrievedChunk(text=clave[2], source=clave[0], page=clave[1], score=puntaje)
            for clave, puntaje in ranking
        ]

    # --- Punto de entrada estándar --------------------------------------------

    def search(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        top_k = top_k or settings.TOP_K
        search = self.hybrid_search if settings.HYBRID_SEARCH else self.semantic_search
        chunks = search(query, top_k)
        expanded = expand_query(query)
        if expanded != query:
            # Conserva los hitos recuperados por la pregunta original y añade
            # la definición; expandir toda la consulta puede desplazar la tabla EOC.
            definitions = search(expanded, 1)
            for definition in definitions:
                if not any(c.text == definition.text for c in chunks):
                    chunks = chunks[: max(0, top_k - 1)] + [definition]
        return chunks

    # --- Agentic RAG (tendencia 2026) -----------------------------------------

    def agentic_search(self, query: str, top_k: int | None = None) -> AgenticSearchResult:
        """
        Bucle simplificado de "Analizar pregunta → ¿Necesito más datos? →
        Recuperar y evaluar → (reformular si la evidencia es débil)".

        La "reformulación" aquí es deliberadamente simple (amplía el número
        de resultados solicitados); en un sistema de producción se usaría
        un LLM o un framework de agentes para reformular semánticamente
        la consulta, tal como señala el material del curso.
        """
        top_k = top_k or settings.TOP_K
        current_k = top_k
        rounds: list[dict] = []
        results: list[RetrievedChunk] = []

        for numero_ronda in range(1, settings.MAX_RETRIEVAL_ROUNDS + 1):
            results = self.search(query, top_k=current_k)
            score_promedio = (
                sum(r.score for r in results) / len(results) if results else 0.0
            )
            rounds.append(
                {
                    "round": numero_ronda,
                    "top_k": current_k,
                    "avg_score": round(score_promedio, 3),
                    "n_results": len(results),
                }
            )

            evidencia_suficiente = score_promedio >= settings.MIN_RELEVANCE_SCORE
            es_ultima_ronda = numero_ronda == settings.MAX_RETRIEVAL_ROUNDS
            if evidencia_suficiente or es_ultima_ronda:
                break

            current_k += 2  # "reformulación": amplía la búsqueda

        return AgenticSearchResult(chunks=results, rounds=rounds)
