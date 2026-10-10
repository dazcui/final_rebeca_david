from rag.chunking import Chunk


def _make_chunks() -> list[Chunk]:
    return [
        Chunk(chunk_id="1", text="El plazo de reembolso es de 30 días.", source="politica.md", page=None, doc_type="markdown"),
        Chunk(chunk_id="2", text="La garantía cubre defectos de fábrica.", source="politica.md", page=None, doc_type="markdown"),
        Chunk(chunk_id="3", text="Reinicia el router 10 segundos.", source="soporte.html", page=None, doc_type="html"),
    ]


def test_add_and_count(temp_vector_store):
    assert temp_vector_store.count() == 0
    temp_vector_store.add_chunks(_make_chunks())
    assert temp_vector_store.count() == 3


def test_query_returns_expected_structure(temp_vector_store):
    temp_vector_store.add_chunks(_make_chunks())
    resultados = temp_vector_store.query("¿Cuál es el plazo de reembolso?", top_k=2)

    assert len(resultados) == 2
    for r in resultados:
        assert hasattr(r, "text")
        assert hasattr(r, "source")
        assert hasattr(r, "score")
        assert 0.0 <= r.score <= 1.0


def test_query_on_empty_store_returns_empty_list(temp_vector_store):
    assert temp_vector_store.query("cualquier cosa", top_k=3) == []


def test_get_all_preserves_metadata(temp_vector_store):
    temp_vector_store.add_chunks(_make_chunks())
    registros = temp_vector_store.get_all()

    assert len(registros) == 3
    fuentes = {r["source"] for r in registros}
    assert fuentes == {"politica.md", "soporte.html"}


def test_reset_clears_the_collection(temp_vector_store):
    temp_vector_store.add_chunks(_make_chunks())
    assert temp_vector_store.count() == 3

    temp_vector_store.reset()
    assert temp_vector_store.count() == 0
