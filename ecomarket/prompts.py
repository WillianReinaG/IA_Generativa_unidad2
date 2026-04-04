"""Plantillas de ingeniería de prompts — EcoMarket (Fase 3)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

__all__ = ["build_pedido_messages", "build_devolucion_messages"]

SYSTEM_ECOMARKET = """Eres un agente de atención al cliente de EcoMarket (e-commerce).
Reglas obligatorias:
- Usa SOLO la información factual proporcionada en el bloque >>>DATOS_VERIFICADOS<<<.
- Si falta algún dato en ese bloque, dilo con claridad y ofrece escalar a un agente humano.
- No inventes números de seguimiento, fechas, enlaces ni estados de pedido.
- Tono profesional, amable y empático, en español.
"""


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_pedido_messages(
    *,
    order_id: str,
    user_message: str,
    pedidos_path: Path | None = None,
) -> list[dict]:
    """Prompt (a): estado de pedido con contexto simulado desde 'base de datos'."""
    base = pedidos_path or Path(__file__).resolve().parent.parent / "data" / "pedidos_ejemplo.json"
    pedidos = _load_json(base)
    facts = pedidos.get(order_id)
    if facts is None:
        datos = {"error": f"No se encontró el pedido {order_id} en el sistema."}
    else:
        datos = facts

    datos_txt = json.dumps(datos, ensure_ascii=False, indent=2)
    instruction = f"""
>>>>>>DATOS_VERIFICADOS<<<<<<
{datos_txt}
>>>>>>FIN_DATOS<<<<<<

Instrucciones de respuesta:
1) Resume el estado actual del pedido (order_id: {order_id}).
2) Incluye número de seguimiento (tracking_number), estimación de entrega (estimated_delivery) y enlace de rastreo (tracking_url) si están en DATOS_VERIFICADOS.
3) Si delayed es true, ofrece disculpas y una breve explicación usando delay_reason si existe.
4) Si hubo error de pedido no encontrado, sé empático e indica que pueden verificar el número o hablar con un agente.
"""
    return [
        {"role": "system", "content": SYSTEM_ECOMARKET},
        {"role": "user", "content": instruction.strip()},
        {"role": "user", "content": user_message.strip()},
    ]


def build_devolucion_messages(
    *,
    producto: str,
    categoria: str,
    motivo: str,
    politica_path: Path | None = None,
) -> list[dict]:
    """Prompt (b): guía de devolución diferenciando productos permitidos vs no permitidos."""
    base = politica_path or Path(__file__).resolve().parent.parent / "data" / "politica_devoluciones.json"
    politica = _load_json(base)
    politica_txt = json.dumps(politica, ensure_ascii=False, indent=2)

    instruction = f"""
>>>>>>POLITICA_ECOMARKET<<<<<<
{politica_txt}
>>>>>>FIN_POLITICA<<<<<<

El cliente solicita información sobre devolución.
- Producto mencionado: {producto}
- Categoría declarada por el cliente: {categoria}
- Motivo: {motivo}

Instrucciones:
1) Determina si, según POLITICA_ECOMARKET, es probable que la devolución NO sea posible (perecederos, higiene personal, personalizados, etc.) o si encaja en devolución permitida.
2) Explica los pasos generales solo si aplica; si no aplica, explica con empatía por qué no y qué alternativas existen (garantía por defecto, contacto con soporte el mismo día de entrega para perecederos, etc.).
3) No inventes plazos ni condiciones que no estén en POLITICA_ECOMARKET; puedes usar lenguaje prudente ("según nuestras políticas habituales…") solo cuando el texto lo respalde.
"""
    return [
        {"role": "system", "content": SYSTEM_ECOMARKET},
        {"role": "user", "content": instruction.strip()},
    ]
