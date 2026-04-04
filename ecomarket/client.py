import os

from openai import OpenAI

__all__ = ["get_chat_completion"]


def get_chat_completion(
    messages: list[dict],
    *,
    model: str | None = None,
    temperature: float = 0.35,
) -> str:
    """Envía mensajes al endpoint de chat completions (misma familia que el ejemplo de Real Python)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Define la variable de entorno OPENAI_API_KEY antes de ejecutar el notebook o run_fase3.py."
        )
    client = OpenAI(api_key=api_key)
    use_model = model or os.getenv("ECOMARKET_OPENAI_MODEL", "gpt-4o-mini")
    response = client.chat.completions.create(
        model=use_model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""
