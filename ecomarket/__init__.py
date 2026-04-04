"""EcoMarket — utilidades para prompts (Fase 3).

Para llamar al modelo: ``from ecomarket.client import get_chat_completion``.
"""

from .prompts import build_devolucion_messages, build_pedido_messages

__all__ = ["build_pedido_messages", "build_devolucion_messages"]
