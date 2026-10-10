"""Buscador del manual de mantenimiento preventivo."""
import streamlit as st
from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore

st.set_page_config(page_title="Mantenimiento preventivo — Buscador", page_icon="🔎")
st.title("Buscador del manual de mantenimiento preventivo")
st.caption("SGT-800 y SST-400 · Fragmentos y fuentes del manual")

@st.cache_resource
def resources():
    return EmbeddingModel(), VectorStore()

embedder, store = resources()
st.sidebar.metric("Fragmentos indexados", store.count())
top_k = st.sidebar.slider("Fragmentos a mostrar", 1, 10, 5)
questions = [
    "¿Cuántos días duran las inspecciones A, B y C de las SGT-800?",
    "¿Qué diferencia hay entre los contratos Offshore y Onshore?",
    "¿A cuántas EOH se realizan las revisiones de las SST-400?",
    "¿Qué intervención está prevista para WAR42 en 2027?",
    "¿Qué significa la confiabilidad operativa de 96,89 %?",
]
selected = st.selectbox("Preguntas del manual", questions)
question = st.text_input("Pregunta", value=selected)
if st.button("Buscar", type="primary"):
    if not store.count():
        st.warning("Ejecuta primero la ingesta del manual.")
    elif question.strip():
        with st.spinner("Consultando el manual..."):
            hits = store.similarity_search(embedder.embed_query(question), top_k=top_k)
        for i, hit in enumerate(hits, 1):
            st.subheader(f"Fragmento {i}")
            st.caption(f"Fuente: {hit['metadata'].get('source')} · Similitud: {hit['similarity']:.3f}")
            st.markdown(hit["text"])
