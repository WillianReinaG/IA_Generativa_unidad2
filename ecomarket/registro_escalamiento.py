"""Registro persistente de consultas escaladas a atención humana — EcoMarket.

Cada evento se añade como una línea JSON (JSONL) en ``data/registro_escalamientos_humanos.jsonl``
por defecto. Ruta alternativa: variable de entorno ``ECOMARKET_REGISTRO_ESCALAMIENTO``.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

__all__ = [
    "REGISTRO_ESCALAMIENTO_DEFAULT",
    "resolver_ruta_registro",
    "extraer_numero_pedido_desde_texto",
    "consultar_retraso_pedido",
    "append_evento_escalamiento_humano",
    "registrar_escalamiento_humano",
]

REGISTRO_ESCALAMIENTO_DEFAULT = (
    Path(__file__).resolve().parent.parent / "data" / "registro_escalamientos_humanos.jsonl"
)

_ORD_PATTERN = re.compile(r"\b(ORD-\d+)\b", re.IGNORECASE)


def resolver_ruta_registro(override: Path | None = None) -> Path:
    if override is not None:
        return override
    env = os.getenv("ECOMARKET_REGISTRO_ESCALAMIENTO", "").strip()
    if env:
        return Path(env)
    return REGISTRO_ESCALAMIENTO_DEFAULT


def extraer_numero_pedido_desde_texto(texto: str) -> str | None:
    """Localiza el primer ``ORD-#####`` en el mensaje del cliente (mayúsculas normalizadas)."""
    m = _ORD_PATTERN.search(texto or "")
    if not m:
        return None
    return m.group(1).upper()


def _load_pedidos(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def consultar_retraso_pedido(
    numero_pedido: str | None,
    *,
    pedidos_path: Path | None = None,
) -> bool | None:
    """
    ``True`` / ``False`` según ``delayed`` en el JSON de pedidos; ``None`` si no aplica.
    """
    if not numero_pedido or not pedidos_path or not pedidos_path.is_file():
        return None
    try:
        pedidos = _load_pedidos(pedidos_path)
    except (OSError, json.JSONDecodeError):
        return None
    row = pedidos.get(numero_pedido)
    if not isinstance(row, dict):
        return None
    d = row.get("delayed")
    if d is True:
        return True
    if d is False:
        return False
    return None


def append_evento_escalamiento_humano(evento: dict[str, Any], *, registro_path: Path | None = None) -> Path:
    """
    Añade un objeto JSON como una línea al archivo de registro (crea directorio si hace falta).

    Returns:
        Ruta del archivo usado.
    """
    path = resolver_ruta_registro(registro_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(evento, ensure_ascii=False) + "\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(line)
    return path


def registrar_escalamiento_humano(
    *,
    user_message: str,
    motivo_clasificacion: str | None,
    order_id: str | None = None,
    categoria: str | None = None,
    pedidos_path: Path | None = None,
    registro_path: Path | None = None,
) -> tuple[dict[str, Any], Path]:
    """
    Construye el evento y lo escribe en el JSONL.

    Campos guardados:
    - ``fecha_consulta``: ISO 8601 (UTC).
    - ``numero_pedido``: explícito, o extraído del texto, o ``null``.
    - ``tiene_retraso``: según datos del pedido si se conoce ``numero_pedido`` y existe en JSON; si no, ``null``.
    - ``motivo_clasificacion``: p. ej. heurística de ``routing``.
    - ``categoria_consulta`` (opcional): si se pasó búsqueda por categoría.

    Returns:
        (evento_escrito, ruta_del_archivo)
    """
    oid = (order_id or "").strip() or extraer_numero_pedido_desde_texto(user_message)
    fecha = datetime.now(timezone.utc).isoformat()
    tiene_retraso = consultar_retraso_pedido(oid, pedidos_path=pedidos_path)

    evento: dict[str, Any] = {
        "fecha_consulta": fecha,
        "numero_pedido": oid,
        "tiene_retraso": tiene_retraso,
        "motivo_clasificacion": motivo_clasificacion,
    }
    cat = (categoria or "").strip()
    if cat:
        evento["categoria_consulta"] = cat

    path = append_evento_escalamiento_humano(evento, registro_path=registro_path)
    return evento, path

