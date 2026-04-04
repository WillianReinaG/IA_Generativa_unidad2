"""Enrutamiento primer nivel (LLM + datos) vs escalamiento humano — EcoMarket.

El reparto **80 % / 20 %** descrito en FASE2 y README **no es un porcentaje que este
programa calcule en tiempo de ejecución**: en producción se obtiene midiendo cuántos
contactos se resuelven solo con el asistente frente a los que pasan a un agente.

En **código** lo que sí existe es una **separación explícita de flujos**:

- **Primer nivel automatizable:** consultas acotadas a datos verificados (pedido,
  categoría, políticas) → ``build_pedido_messages`` / ``build_devolucion_messages``.
- **Escalamiento sugerido:** heurística por palabras clave en el mensaje del cliente
  (vía ``clasificar_consulta_cliente``) → ``build_escalamiento_messages``, sin inyectar
  JSON de pedido para no dar respuestas “seguras” sobre un caso que requiere criterio humano.

La heurística es **orientativa** (falso positivo/negativo posible); en un sistema real
se complementaría con clasificador entrenado, colas y métricas.
"""

from __future__ import annotations

import unicodedata
from enum import Enum
from pathlib import Path

from .prompts import build_pedido_messages
from .registro_escalamiento import registrar_escalamiento_humano

__all__ = [
    "RutaAtencion",
    "clasificar_consulta_cliente",
    "build_escalamiento_messages",
    "armar_mensajes_atencion_pedido",
]

# Patrones en texto normalizado (minúsculas, sin acentos). Ampliar con cuidado.
_ESCALAMIENTO_SUBCADENAS = (
    "demanda",
    "demandar",
    "judicial",
    "tribunal",
    "juez",
    "abogado",
    "accion legal",
    "difamacion",
    "supervisor",
    "hablar con un humano",
    "agente humano",
    "operador humano",
    "persona real",
    "defensa del consumidor",
    "profeco",
    "denuncia penal",
    "fraude grave",
    "urgencia medica",
    "intoxicacion",
    "efectos adversos graves",
)


class RutaAtencion(str, Enum):
    """Qué flujo de mensajes conviene armar antes de llamar al modelo."""

    PRIMER_NIVEL_AUTOMATIZABLE = "primer_nivel_automatizable"
    """Consulta típica de FAQ + datos de sistema (objetivo ~80 % en operación)."""

    ESCALAMIENTO_HUMANO_SUGERIDO = "escalamiento_humano_sugerido"
    """Casos que no deben cerrarse solo con el LLM (perfil típico del ~20 % en operación)."""


def _normalizar_mensaje(texto: str) -> str:
    t = unicodedata.normalize("NFD", texto.strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def clasificar_consulta_cliente(user_message: str) -> tuple[RutaAtencion, str | None]:
    """
    Clasificación barata por subcadenas. No sustituye analítica del 80/20.

    Returns:
        (ruta, motivo_escalamiento) donde motivo es None si la ruta es primer nivel.
    """
    norm = _normalizar_mensaje(user_message)
    if not norm:
        return RutaAtencion.PRIMER_NIVEL_AUTOMATIZABLE, None

    for sub in _ESCALAMIENTO_SUBCADENAS:
        if sub in norm:
            return RutaAtencion.ESCALAMIENTO_HUMANO_SUGERIDO, f"coincidencia: «{sub}»"
    return RutaAtencion.PRIMER_NIVEL_AUTOMATIZABLE, None


SYSTEM_ESCALAMIENTO_ECOMARKET = """Eres un agente de primera línea de EcoMarket (e-commerce).
Esta conversación fue marcada para ESCALAMIENTO a un agente humano (caso sensible o fuera de autoresolución con datos simples).

Reglas:
- No inventes números de pedido, fechas, enlaces, teléfonos ni correos concretos.
- No resuelvas reclamaciones legales, médicas ni conflictos graves: traslada con claridad a un especialista humano.
- Sé breve, empático y profesional en español.
- Ofrece que un agente continuará por el canal oficial de soporte (sin inventar datos de contacto).
"""


def build_escalamiento_messages(*, user_message: str) -> list[dict]:
    """Cadena mínima para el ~20 %: respuesta de acogida y traslado, sin datos de pedido."""
    bloque = f"""[Contexto operativo]
El sistema clasificó esta consulta como candidata a escalamiento humano (no usar flujo de pedido con JSON).

[Consulta del cliente]
{user_message.strip()}"""
    return [
        {"role": "system", "content": SYSTEM_ESCALAMIENTO_ECOMARKET},
        {"role": "user", "content": bloque},
    ]


def armar_mensajes_atencion_pedido(
    *,
    user_message: str,
    order_id: str | None = None,
    categoria: str | None = None,
    pedidos_path: Path | None = None,
    ignorar_clasificacion: bool = False,
    registrar_escalamiento: bool = True,
    registro_path: Path | None = None,
) -> tuple[list[dict], RutaAtencion, str | None]:
    """
    Punto único: o bien cadena de prompts de pedido, o bien escalamiento.

    Si ``ignorar_clasificacion`` es True, siempre se usa ``build_pedido_messages``
    (útil para pruebas o cuando el canal ya filtró la intención).

    Si la ruta es escalamiento y ``registrar_escalamiento`` es True, se añade una
    línea al archivo JSONL (véase ``ecomarket.registro_escalamiento``): fecha,
    número de pedido (parámetro o extraído del texto), retraso según JSON si aplica.

    Returns:
        (messages, ruta, motivo_escalamiento)
    """
    if not ignorar_clasificacion:
        ruta, motivo = clasificar_consulta_cliente(user_message)
        if ruta is RutaAtencion.ESCALAMIENTO_HUMANO_SUGERIDO:
            if registrar_escalamiento:
                base_pedidos = pedidos_path or Path(__file__).resolve().parent.parent / "data" / "pedidos_ejemplo.json"
                registrar_escalamiento_humano(
                    user_message=user_message,
                    motivo_clasificacion=motivo,
                    order_id=order_id,
                    categoria=categoria,
                    pedidos_path=base_pedidos if base_pedidos.is_file() else None,
                    registro_path=registro_path,
                )
            return build_escalamiento_messages(user_message=user_message), ruta, motivo

    msgs = build_pedido_messages(
        user_message=user_message,
        order_id=order_id,
        categoria=categoria,
        pedidos_path=pedidos_path,
    )
    return msgs, RutaAtencion.PRIMER_NIVEL_AUTOMATIZABLE, None
