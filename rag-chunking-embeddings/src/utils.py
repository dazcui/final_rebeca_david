"""
utils.py
========
Funciones auxiliares para cargar documentos desde disco (Paso 1 del
pipeline: Ingesta, ver diapositiva 3).
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


def load_documents(folder: Path) -> List[Dict[str, Any]]:
    """
    Recorre `folder` y carga todos los documentos soportados (.txt,
    .md, .pdf). Devuelve una lista de diccionarios:
        {"text": str, "metadata": {"source": <ruta relativa>}}
    """
    folder = Path(folder)
    if not folder.exists():
        raise FileNotFoundError(f"La carpeta '{folder}' no existe.")

    documents = []
    paths = sorted(p for p in folder.rglob("*") if p.suffix.lower() in SUPPORTED_EXTENSIONS)

    if not paths:
        print(f"[utils] Aviso: no se encontraron documentos soportados en '{folder}'.")

    for path in paths:
        text = _read_file(path)
        if text and text.strip():
            documents.append(
                {
                    "text": text,
                    "metadata": {"source": str(path.relative_to(folder))},
                }
            )
    return documents


def _read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        return _read_pdf(path)
    raise ValueError(f"Extensión no soportada: {suffix}")


def _read_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages_text = []
    for page in reader.pages:
        pages_text.append(page.extract_text() or "")
    return "\n\n".join(pages_text)
