"""
Generation (Unidad 1): el LLM redacta la respuesta final, fundamentada en
el prompt aumentado construido por `rag/augmentation.py`.

Por defecto, la generación corre 100% local mediante **Ollama**
(https://ollama.com), sirviendo modelos open-weight (Llama 3.2, Qwen2.5,
Mistral, etc.) sin ninguna llamada a una API de pago ni consumo de
créditos/tokens facturables. El generador sigue siendo "un LLM estándar";
lo único que cambia es lo que recibe como entrada (tal como señala el
material del curso).
"""
import ollama

from config.settings import settings


class OllamaUnavailableError(RuntimeError):
    """Se lanza cuando Ollama no está corriendo o el modelo no está disponible."""


def generate_answer(prompt: str) -> str:
    """Envía el prompt aumentado al modelo local vía Ollama y devuelve la respuesta."""
    try:
        client = ollama.Client(host=settings.OLLAMA_HOST, timeout=180)
        respuesta = client.chat(
            model=settings.OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": (
                    "Responde en español y de forma breve, usando solo el contexto del manual. "
                    "No inventes expansiones de siglas, unidades ni cifras. "
                    "En la sección 3.1 del manual HGP = Hot Gas Path Inspection "
                    "(inspección de la trayectoria de gases calientes); MO = Major Overhaul "
                    "(inspección mayor); RMI = Remote Minor Inspection (inspección remota menor). "
                    "Estas son las únicas expansiones admitidas. Responde exactamente lo preguntado, "
                    "sin agregar temas distintos. "
                    "Si falta un dato, indica que no está en el contexto. EOH son horas equivalentes y EOC ciclos "
                    "equivalentes: no intercambies sus valores. Cita [Fragmento N] solo si ese "
                    "fragmento contiene el dato afirmado. No reproduzcas los puntajes de relevancia."
                )},
                {"role": "user", "content": prompt},
            ],
            options={"temperature": settings.GENERATION_TEMPERATURE, "num_predict": 300},
        )
        return respuesta["message"]["content"]
    except Exception as exc:  # noqa: BLE001 — se traduce a un error propio y explicativo
        raise OllamaUnavailableError(
            f"No se pudo generar una respuesta con Ollama (modelo '{settings.OLLAMA_MODEL}').\n"
            f"¿Está Ollama corriendo? Prueba: 'ollama serve' y 'ollama pull "
            f"{settings.OLLAMA_MODEL}'.\nDetalle técnico: {exc}"
        ) from exc
