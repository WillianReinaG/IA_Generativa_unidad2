import os

from openai import OpenAI

__all__ = ["get_chat_completion"]


def _messages_to_responses_input(messages: list[dict]) -> list[dict]:
    """Convierte mensajes estilo Chat Completions al formato de la API Responses."""
    items: list[dict] = []
    for m in messages:
        role = m["role"]
        raw = m["content"]
        text = raw if isinstance(raw, str) else str(raw)
        items.append(
            {
                "role": role,
                "content": [{"type": "input_text", "text": text}],
            }
        )
    return items


def _complete_with_responses(
    client: OpenAI,
    messages: list[dict],
    model: str,
    temperature: float,
) -> str:
    store = os.getenv("ECOMARKET_OPENAI_STORE", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    response = client.responses.create(
        model=model,
        input=_messages_to_responses_input(messages),
        temperature=temperature,
        store=store,
    )
    out = getattr(response, "output_text", None)
    return (out or "").strip()


def _complete_with_chat(
    client: OpenAI,
    messages: list[dict],
    model: str,
    temperature: float,
) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


def get_chat_completion(
    messages: list[dict],
    *,
    model: str | None = None,
    temperature: float = 0.35,
) -> str:
    """
    Genera la respuesta del modelo.

    Por defecto usa la API **Responses** (como en el quickstart actual de OpenAI:
    ``client.responses.create`` y ``output_text``), con **gpt-5-nano** si no indicas otro modelo.

    Si el SDK es antiguo o la API devuelve error, hace **fallback** a Chat Completions
    (por defecto ``gpt-4o-mini``).
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Define la variable de entorno OPENAI_API_KEY (por ejemplo en un archivo .env). "
            "No pegues la clave en el código fuente."
        )

    client = OpenAI(api_key=api_key)
    use_responses = os.getenv("ECOMARKET_USE_RESPONSES_API", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    responses_model = model or os.getenv("ECOMARKET_OPENAI_MODEL", "gpt-5-nano")
    chat_fallback_model = os.getenv("ECOMARKET_CHAT_FALLBACK_MODEL", "gpt-4o-mini")

    if use_responses and getattr(client, "responses", None) is not None:
        try:
            return _complete_with_responses(
                client, messages, responses_model, temperature
            )
        except Exception:
            pass

    chat_model = model if model else chat_fallback_model
    return _complete_with_chat(client, messages, chat_model, temperature)
