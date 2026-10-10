"""
embeddings.py
=============
Envoltorio (wrapper) sobre `sentence-transformers` para generar
embeddings 100% en local, sin llamadas a APIs de pago (Unidad 5).

Por defecto usa BAAI/bge-m3, recomendado en la diapositiva 20 para
contenido multilingüe / español. El modelo se descarga una sola vez
desde Hugging Face (gratis, licencia MIT) y luego queda cacheado
localmente en ~/.cache/huggingface.
"""

from __future__ import annotations

from typing import List, Union
import numpy as np

import config


class EmbeddingModel:
    def __init__(
        self,
        model_name: str = config.EMBEDDING_MODEL,
        device: str = config.EMBEDDING_DEVICE,
        normalize: bool = True,
    ):
        # Import perezoso: así config.py y chunking.py pueden usarse
        # sin forzar la descarga/carga del modelo si no hace falta.
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.normalize = normalize
        print(f"[embeddings] Cargando modelo '{model_name}' en dispositivo '{device}'...")
        self.model = SentenceTransformer(model_name, device=device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"[embeddings] Modelo cargado. Dimensión del vector: {self.dimension}")

    def embed_texts(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Genera embeddings para un texto o una lista de textos."""
        if isinstance(texts, str):
            texts = [texts]
        vectors = self.model.encode(
            texts,
            normalize_embeddings=self.normalize,
            show_progress_bar=len(texts) > 20,
            convert_to_numpy=True,
        )
        return vectors.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Genera el embedding de una consulta de búsqueda.

        Nota: algunos modelos (como BGE) recomiendan anteponer una
        instrucción al texto de la consulta para mejorar el retrieval
        asimétrico consulta-documento. bge-m3 funciona bien sin
        instrucción, pero se deja el gancho por si cambias de modelo.
        """
        return self.embed_texts(query)[0]
