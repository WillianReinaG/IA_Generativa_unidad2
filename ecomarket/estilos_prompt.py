"""Carga y composición de estilos de prompt desde TOML (config/prompt_estilos.toml)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

__all__ = [
    "DEFAULT_PROMPT_ESTILOS_PATH",
    "resolver_ruta_estilos_toml",
    "cargar_estilos_prompt",
    "componer_system_prompt_principal",
    "componer_system_prompt_escalamiento",
    "REGLAS_DATOS_CADENA_PEDIDO",
]

DEFAULT_PROMPT_ESTILOS_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "prompt_estilos.toml"
)

# Reglas técnicas fijas (no sustituyen el TOML; lo complementan).
REGLAS_DATOS_CADENA_PEDIDO = """Reglas obligatorias de datos (siempre activas):
- Usa SOLO la información factual de los bloques de la cadena de mensajes.
- No inventes números de seguimiento, fechas, enlaces ni estados de pedido.
- Si falta un dato, dilo y ofrece escalar a un agente humano.

Sobre la cadena de mensajes:
- Varios mensajes de usuario consecutivos forman un flujo numerado (Paso 1…4).
- Asimila el Paso 1 (hechos) y el Paso 2 (reglas según ese pedido) antes de redactar.
- Tu respuesta final debe cumplir el Paso 3 y responder al Paso 4 (consulta del cliente)."""

REGLAS_DATOS_DEVOLUCION = """Reglas obligatorias de datos (siempre activas):
- Usa SOLO la política y datos del bloque POLITICA_ECOMARKET y el mensaje del cliente.
- No inventes plazos, condiciones ni excepciones que no aparezcan en la política inyectada.
- Si falta información, dilo con claridad y ofrece canal humano."""

SUFIJO_ESCALAMIENTO = """Contexto adicional de esta conversación:
- La consulta fue clasificada para ESCALAMIENTO a un agente humano (caso sensible o fuera de autoresolución con datos simples).
- No inventes números de pedido, fechas, enlaces, teléfonos ni correos concretos.
- No resuelvas reclamaciones legales, médicas ni conflictos graves: traslada a un especialista humano.
- Sé breve; ofrece que un agente continuará por el canal oficial (sin inventar datos de contacto)."""


def resolver_ruta_estilos_toml(override: Path | None = None) -> Path:
    if override is not None:
        return override
    env = os.getenv("ECOMARKET_PROMPT_ESTILOS_TOML", "").strip()
    if env:
        return Path(env)
    return DEFAULT_PROMPT_ESTILOS_PATH


def cargar_estilos_prompt(path: Path | None = None) -> dict[str, str]:
    """Lee las cuatro secciones del TOML y devuelve textos normalizados."""
    p = resolver_ruta_estilos_toml(path)
    with p.open("rb") as f:
        raw: dict[str, Any] = tomllib.load(f)
    out: dict[str, str] = {}
    for key in ("rol_general", "estilo_respuesta", "contexto_especifico", "manejo_quejas"):
        block = raw.get(key)
        if not isinstance(block, dict):
            raise ValueError(f"En {p}: falta la tabla [{key}] o no es un objeto TOML.")
        texto = block.get("texto")
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError(f"En {p}: [{key}] debe definir una clave 'texto' no vacía.")
        out[key] = texto.strip()
    return out


def componer_system_prompt_principal(
    *,
    reglas_datos: str,
    estilos_path: Path | None = None,
) -> str:
    """
    Ensambla rol, contexto, estilo, quejas y las reglas fijas de datos para pedidos o devoluciones.
    """
    e = cargar_estilos_prompt(estilos_path)
    partes = [
        "### Rol general\n" + e["rol_general"],
        "### Contexto específico\n" + e["contexto_especifico"],
        "### Estilo de respuesta\n" + e["estilo_respuesta"],
        "### Manejo de quejas\n" + e["manejo_quejas"],
        "### Reglas de datos y flujo\n" + reglas_datos.strip(),
    ]
    return "\n\n".join(partes)


def componer_system_prompt_escalamiento(*, estilos_path: Path | None = None) -> str:
    """Mismos cuatro estilos + reglas acotadas para conversaciones escaladas."""
    e = cargar_estilos_prompt(estilos_path)
    partes = [
        "### Rol general\n" + e["rol_general"],
        "### Contexto específico\n" + e["contexto_especifico"],
        "### Estilo de respuesta\n" + e["estilo_respuesta"],
        "### Manejo de quejas\n" + e["manejo_quejas"],
        "### Modo escalamiento\n" + SUFIJO_ESCALAMIENTO.strip(),
    ]
    return "\n\n".join(partes)
