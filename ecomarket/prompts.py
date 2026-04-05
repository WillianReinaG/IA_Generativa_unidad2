"""Plantillas de ingeniería de prompts — EcoMarket (Fase 3).

Cadena de prompts (atención por pedido o categoría)
==================================================
``build_pedido_messages`` arma varios mensajes de usuario consecutivos: (1) datos
verificados, (2) reglas y **información base del retraso** si aplica, (3) rúbrica,
(4) consulta del cliente. El **system** se arma desde ``config/prompt_estilos.toml``
(rol general, contexto, estilo, quejas) vía ``estilos_prompt``. La consulta puede
resolverse por ``order_id`` o por ``categoria``.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any

from .estilos_prompt import (
    REGLAS_DATOS_CADENA_PEDIDO,
    REGLAS_DATOS_DEVOLUCION,
    componer_system_prompt_principal,
)

__all__ = [
    "build_pedido_messages",
    "build_devolucion_messages",
    "PEDIDO_PROMPT_CHAIN_STEPS",
]

# Nombres de los pasos de la cadena (documentación y trazabilidad en código).
PEDIDO_PROMPT_CHAIN_STEPS = (
    "paso_1_datos_verificados",
    "paso_2_reglas_contexto_pedido",
    "paso_3_rubrica_calidad",
    "paso_4_consulta_cliente",
)

def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _fold_text(s: str) -> str:
    """Compara categorías sin distinguir mayúsculas, acentos ni guiones bajos."""
    t = unicodedata.normalize("NFD", s.strip().lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return t.replace("_", " ").replace("-", " ")


def _pedidos_por_categoria(pedidos: dict[str, Any], categoria: str) -> list[tuple[str, dict[str, Any]]]:
    want = _fold_text(categoria)
    out: list[tuple[str, dict[str, Any]]] = []
    for oid, row in pedidos.items():
        if not isinstance(row, dict):
            continue
        cat = row.get("categoria")
        if cat is None:
            continue
        if _fold_text(str(cat)) == want:
            out.append((oid, row))
    out.sort(key=lambda x: x[1].get("consecutivo", 0) or 0)
    return out


def _delay_base_payload(facts: dict[str, Any]) -> dict[str, Any]:
    """Subconjunto factual para explicar el retraso (Paso 2)."""
    return {
        "delayed": facts.get("delayed"),
        "demora": facts.get("demora"),
        "razon_demora": facts.get("razon_demora"),
        "delay_reason": facts.get("delay_reason"),
        "fecha_entrega": facts.get("fecha_entrega"),
        "estimated_delivery": facts.get("estimated_delivery"),
        "estatus": facts.get("estatus") or facts.get("status"),
        "carrier": facts.get("carrier"),
        "tracking_number": facts.get("tracking_number"),
    }


def _pedido_context_rules(*, consulta_ref: str, datos: dict[str, Any]) -> str:
    """Instrucciones del Paso 2, ramificadas según hechos (un pedido o varios por categoría)."""
    if datos.get("error"):
        return f"""Consulta: {consulta_ref}
No hay resultados válidos en DATOS_VERIFICADOS (error en los datos).
- No inventes pedidos, categorías ni estados.
- Explica con empatía y sugiere revisar el número de pedido o la categoría, o contactar a un agente humano."""

    if datos.get("tipo_consulta") == "por_categoria":
        n = int(datos.get("total_coincidencias") or 0)
        cat = datos.get("categoria_buscada") or ""
        lines = [
            f"Consulta por categoría: «{cat}» ({n} pedido(s) en DATOS_VERIFICADOS).",
            "Aplica estas prioridades:",
            "- Resume o enumera los pedidos según lo que pida el cliente; cada ítem debe basarse solo en los datos listados.",
            "- Si hay varios pedidos, indica order_id de cada uno al que te refieras.",
            "- Para pedidos con delayed=true, explica el retraso usando SOLO el bloque «informacion_base_retraso» incluido abajo para ese pedido (y el JSON del Paso 1). No inventes causas.",
            "- Si el cliente necesita detalle de un solo pedido, pide amablemente el número de orden concreto.",
        ]
        bloques_retraso: list[dict[str, Any]] = []
        for p in datos.get("pedidos") or []:
            if not isinstance(p, dict) or p.get("delayed") is not True:
                continue
            pay = _delay_base_payload(p)
            pay["order_id"] = p.get("order_id")
            bloques_retraso.append(pay)
        if bloques_retraso:
            lines.append("")
            lines.append("--- Información base de retrasos (solo pedidos retrasados) ---")
            lines.append(json.dumps(bloques_retraso, ensure_ascii=False, indent=2))
        return "\n".join(lines)

    # Un solo pedido
    order_id = str(datos.get("order_id") or consulta_ref)
    lines = [
        f"Pedido identificado: {order_id}.",
        "Aplica las siguientes prioridades según el contexto real de los datos:",
    ]
    delayed = datos.get("delayed") is True
    status = datos.get("estatus") or datos.get("status") or ""
    tipo = datos.get("tipo_material") or ""

    if delayed:
        lines.append(
            "- Hay demora (delayed=true): disculpa breve; comunica la magnitud de la demora y la fecha de entrega "
            "según los datos; explica el motivo del retraso usando ÚNICAMENTE el bloque JSON de «información base del retraso» "
            "de este paso (y el Paso 1). No añadas causas que no aparezcan ahí."
        )
        lines.append("")
        lines.append("--- Información base del retraso (obligatoria para explicar el porqué al cliente) ---")
        lines.append(json.dumps(_delay_base_payload(datos), ensure_ascii=False, indent=2))
    else:
        lines.append(
            "- Sin demora registrada: no afirmes retrasos; comunica estado y ventana de entrega según los datos."
        )

    if tipo == "perecedero":
        lines.append(
            "- Contiene producto perecedero: sé prudente con garantías de tiempo; si hay retraso, "
            "menciona manejo prioritario / cadena de frío solo si los datos lo respaldan explícitamente."
        )

    st = str(status).lower()
    if "entregado" in st:
        lines.append("- Estado entregado: no prometas una nueva fecha de entrega futura; orienta a revisar comprobante o incidencias post-entrega si el cliente lo pide.")
    elif "recoger" in st:
        lines.append("- Listo para recoger: indica claramente que debe acudir al punto acordado si los datos lo permiten; no inventes dirección.")

    lines.append(
        "- Incluye siempre que existan en datos: tracking_number, carrier, tracking_url, "
        "fecha_entrega o estimated_delivery, estatus o status, y materias (resumen breve)."
    )
    return "\n".join(lines)


def _pedido_quality_rubric(*, consulta_ref: str, listado_por_categoria: bool) -> str:
    """Paso 3: criterios explícitos para una respuesta óptima al cliente."""
    if listado_por_categoria:
        foco = f"el listado de pedidos de la categoría «{consulta_ref}»"
    else:
        foco = f"la consulta sobre «{consulta_ref}»"
    return f"""Rúbrica (Paso 3) — calidad de la respuesta al cliente sobre {foco}:
1) Primera frase: reconoce la consulta (pedido concreto o categoría).
2) Cuerpo: estado(s) en lenguaje claro; fechas relevantes; transportista y seguimiento si aplican.
3) Si hubo demora en algún pedido citado: tono empático y causa tomada solo de «información base del retraso» / resumen de retrasos del Paso 2 (sin causas nuevas).
4) Cierre: acción concreta (enlace de rastreo, indicar order_id para más detalle, o soporte).
5) Longitud: concisa; sin datos que no aparezcan en el Paso 1."""


def build_pedido_messages(
    *,
    user_message: str,
    order_id: str | None = None,
    categoria: str | None = None,
    pedidos_path: Path | None = None,
    estilos_path: Path | None = None,
) -> list[dict]:
    """Arma la cadena de prompts: por ``order_id`` o, si no se pasa pedido, por ``categoria``.

    El mensaje de sistema se compone desde ``config/prompt_estilos.toml`` (cuatro estilos)
    más reglas fijas de datos. Otra ruta: ``ECOMARKET_PROMPT_ESTILOS_TOML`` o ``estilos_path``.
    """
    oid = (order_id or "").strip()
    cat = (categoria or "").strip()
    if not oid and not cat:
        raise ValueError("Indica order_id (número de pedido) y/o categoria (búsqueda por categoría).")

    base = pedidos_path or Path(__file__).resolve().parent.parent / "data" / "pedidos_ejemplo.json"
    pedidos = _load_json(base)
    if not isinstance(pedidos, dict):
        raise TypeError("pedidos_ejemplo.json debe ser un objeto JSON (diccionario).")

    datos: dict[str, Any]
    consulta_ref: str

    if oid:
        row = pedidos.get(oid)
        if row is None:
            datos = {"error": f"No se encontró el pedido {oid} en el sistema."}
            consulta_ref = oid
        else:
            datos = dict(row) if isinstance(row, dict) else {"error": "Formato de pedido inválido."}
            consulta_ref = oid
    else:
        matches = _pedidos_por_categoria(pedidos, cat)
        if not matches:
            datos = {
                "error": f"No hay pedidos registrados en la categoría «{cat}». "
                "Prueba con: electronicos, insumos, repuestos, alimentos perecederos, "
                "alimentos no perecederos, ropa, equipo deporte, otros.",
            }
            consulta_ref = cat
        else:
            datos = {
                "tipo_consulta": "por_categoria",
                "categoria_buscada": cat,
                "total_coincidencias": len(matches),
                "pedidos": [{"order_id": poid, **dict(prow)} for poid, prow in matches],
            }
            consulta_ref = cat

    datos_txt = json.dumps(datos, ensure_ascii=False, indent=2)

    paso_1 = f"""[Paso 1/4 — {PEDIDO_PROMPT_CHAIN_STEPS[0]}]
>>>>>>DATOS_VERIFICADOS<<<<<<
{datos_txt}
>>>>>>FIN_DATOS<<<<<<"""

    paso_2 = f"""[Paso 2/4 — {PEDIDO_PROMPT_CHAIN_STEPS[1]}]
{_pedido_context_rules(consulta_ref=consulta_ref, datos=datos)}"""

    listado = datos.get("tipo_consulta") == "por_categoria"
    paso_3 = f"""[Paso 3/4 — {PEDIDO_PROMPT_CHAIN_STEPS[2]}]
{_pedido_quality_rubric(consulta_ref=consulta_ref, listado_por_categoria=listado)}"""

    paso_4 = f"""[Paso 4/4 — {PEDIDO_PROMPT_CHAIN_STEPS[3]}]
Consulta del cliente (responde solo a esto en tu mensaje de salida, cumpliendo los pasos anteriores):
{user_message.strip()}"""

    system = componer_system_prompt_principal(
        reglas_datos=REGLAS_DATOS_CADENA_PEDIDO,
        estilos_path=estilos_path,
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": paso_1},
        {"role": "user", "content": paso_2},
        {"role": "user", "content": paso_3},
        {"role": "user", "content": paso_4},
    ]


def build_devolucion_messages(
    *,
    producto: str,
    categoria: str,
    motivo: str,
    politica_path: Path | None = None,
    estilos_path: Path | None = None,
) -> list[dict]:
    """Prompt (b): guía de devolución diferenciando productos permitidos vs no permitidos.

    Usa los mismos estilos TOML que ``build_pedido_messages`` con reglas de datos para políticas.
    """
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
    system = componer_system_prompt_principal(
        reglas_datos=REGLAS_DATOS_DEVOLUCION,
        estilos_path=estilos_path,
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": instruction.strip()},
    ]
