"""
Augmentation (Unidad 1): construye el prompt aumentado que se envía al LLM,
siguiendo exactamente la estructura de tres partes vista en el material
del curso: INSTRUCCIONES / CONTEXTO RECUPERADO / PREGUNTA DEL USUARIO.

El LLM nunca accede a la base vectorial directamente: solo recibe el
texto que el Retriever seleccionó.
"""
from rag.vector_store import RetrievedChunk

SYSTEM_INSTRUCTIONS = (
    "Responde en español sobre el Manual del Programa de Mantenimiento Preventivo "
    "de turbinas SGT-800 y SST-400. Distingue EOH de EOC, "
    "duraciones de referencia de fechas y datos de interpretaciones editoriales. "
    "No deduzcas métodos de seguridad, criterios NDT ni fórmulas de confiabilidad "
    "si el manual no los especifica. "
    "Responde la pregunta usando ÚNICAMENTE la información del CONTEXTO "
    "recuperado a continuación. Si la respuesta no se encuentra en el "
    "contexto, dilo explícitamente: no inventes información. "
    "Cuando sea posible, menciona de qué fragmento (archivo y página, si "
    "aplica) proviene cada afirmación."
)


def format_context(chunks: list[RetrievedChunk]) -> str:
    """Numera y etiqueta cada fragmento recuperado con su fuente, para
    permitir respuestas con citas verificables."""
    partes = []
    for i, chunk in enumerate(chunks, start=1):
        ubicacion = chunk.source + (f", página {chunk.page}" if chunk.page else "")
        partes.append(f"[Fragmento {i} — {ubicacion} | relevancia={chunk.score:.2f}]\n{chunk.text}")
    return "\n\n".join(partes)


def build_prompt(query: str, chunks: list[RetrievedChunk]) -> str:
    """Ensambla el prompt aumentado final."""
    if not chunks:
        contexto = "(No se encontró ningún fragmento relevante en la base de conocimiento.)"
    else:
        contexto = format_context(chunks)

    return (
        f"INSTRUCCIONES\n{SYSTEM_INSTRUCTIONS}\n\n"
        f"CONTEXTO RECUPERADO\n{contexto}\n\n"
        f"PREGUNTA DEL USUARIO\n{query}"
    )
