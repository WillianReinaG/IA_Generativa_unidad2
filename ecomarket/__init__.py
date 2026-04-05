"""EcoMarket — utilidades para prompts (Fase 3).

Para llamar al modelo: ``from ecomarket.client import get_chat_completion``.
"""

from .estilos_prompt import (
    DEFAULT_PROMPT_ESTILOS_PATH,
    REGLAS_DATOS_CADENA_PEDIDO,
    REGLAS_DATOS_DEVOLUCION,
    cargar_estilos_prompt,
    componer_system_prompt_escalamiento,
    componer_system_prompt_principal,
    resolver_ruta_estilos_toml,
)
from .prompts import (
    PEDIDO_PROMPT_CHAIN_STEPS,
    build_devolucion_messages,
    build_pedido_messages,
)
from .registro_escalamiento import (
    REGISTRO_ESCALAMIENTO_DEFAULT,
    append_evento_escalamiento_humano,
    consultar_retraso_pedido,
    extraer_numero_pedido_desde_texto,
    registrar_escalamiento_humano,
    resolver_ruta_registro,
)
from .routing import (
    RutaAtencion,
    armar_mensajes_atencion_pedido,
    build_escalamiento_messages,
    clasificar_consulta_cliente,
)

__all__ = [
    "DEFAULT_PROMPT_ESTILOS_PATH",
    "resolver_ruta_estilos_toml",
    "cargar_estilos_prompt",
    "componer_system_prompt_principal",
    "componer_system_prompt_escalamiento",
    "REGLAS_DATOS_CADENA_PEDIDO",
    "REGLAS_DATOS_DEVOLUCION",
    "build_pedido_messages",
    "build_devolucion_messages",
    "PEDIDO_PROMPT_CHAIN_STEPS",
    "RutaAtencion",
    "clasificar_consulta_cliente",
    "build_escalamiento_messages",
    "armar_mensajes_atencion_pedido",
    "REGISTRO_ESCALAMIENTO_DEFAULT",
    "resolver_ruta_registro",
    "extraer_numero_pedido_desde_texto",
    "consultar_retraso_pedido",
    "append_evento_escalamiento_humano",
    "registrar_escalamiento_humano",
]
