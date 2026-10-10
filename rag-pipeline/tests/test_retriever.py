from rag.chunking import Chunk
from rag.retriever import Retriever


def _make_chunks() -> list[Chunk]:
    return [
        Chunk(chunk_id="1", text="El plazo de reembolso es de 30 días calendario.", source="politica.md", page=None, doc_type="markdown"),
        Chunk(chunk_id="2", text="La garantía cubre defectos de fábrica por 12 meses.", source="politica.md", page=None, doc_type="markdown"),
        Chunk(chunk_id="3", text="Reinicia el router desconectándolo 10 segundos.", source="soporte.html", page=None, doc_type="html"),
        Chunk(chunk_id="4", text="Los tickets se abren desde el portal web.", source="soporte.html", page=None, doc_type="html"),
    ]


def test_semantic_search_returns_top_k(temp_vector_store):
    temp_vector_store.add_chunks(_make_chunks())
    retriever = Retriever(temp_vector_store)

    resultados = retriever.semantic_search("¿Cómo soluciono un problema de wifi?", top_k=2)
    assert len(resultados) == 2


def test_keyword_search_finds_exact_word_match(temp_vector_store):
    temp_vector_store.add_chunks(_make_chunks())
    retriever = Retriever(temp_vector_store)

    resultados = retriever.keyword_search("reembolso plazo", top_k=4)
    assert len(resultados) > 0
    # El chunk que contiene literalmente "reembolso" y "plazo" debe quedar primero.
    assert "reembolso" in resultados[0].text.lower()


def test_keyword_search_on_empty_store_returns_empty_list(temp_vector_store):
    retriever = Retriever(temp_vector_store)
    assert retriever.keyword_search("algo", top_k=3) == []


def test_hybrid_search_combines_both_signals(temp_vector_store):
    temp_vector_store.add_chunks(_make_chunks())
    retriever = Retriever(temp_vector_store)

    resultados = retriever.hybrid_search("garantía de fábrica", top_k=3)
    assert 0 < len(resultados) <= 3
    assert all(r.score >= 0 for r in resultados)


def test_agentic_search_returns_rounds_trace(temp_vector_store):
    temp_vector_store.add_chunks(_make_chunks())
    retriever = Retriever(temp_vector_store)

    resultado = retriever.agentic_search("¿Cuánto dura la garantía?", top_k=2)

    assert isinstance(resultado.chunks, list)
    assert len(resultado.rounds) >= 1
    for ronda in resultado.rounds:
        assert {"round", "top_k", "avg_score", "n_results"} <= ronda.keys()


def test_agentic_search_stops_within_max_rounds(temp_vector_store):
    from config.settings import settings

    temp_vector_store.add_chunks(_make_chunks())
    retriever = Retriever(temp_vector_store)

    resultado = retriever.agentic_search("consulta cualquiera", top_k=2)
    assert len(resultado.rounds) <= settings.MAX_RETRIEVAL_ROUNDS
