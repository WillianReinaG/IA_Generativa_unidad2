"""
Ejecuta los prompts de la Fase 3 sin Jupyter (misma lógica que el notebook).

Carga automáticamente ``.env`` en la raíz de ``unidad_2`` si existe (variable
``OPENAI_API_KEY``). También puedes definir la clave en la sesión:

- PowerShell: ``$env:OPENAI_API_KEY = "sk-..."``
- CMD: ``set OPENAI_API_KEY=sk-...``
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")

from ecomarket.client import get_chat_completion
from ecomarket.prompts import build_devolucion_messages, build_pedido_messages


def main() -> None:
    print("=== (a) Estado de pedido — cadena de prompts (ejemplo sin retraso) ===\n")
    msg_basic = "Dame el estado de mi pedido y cuándo lo recibiré."
    out_a1 = get_chat_completion(
        build_pedido_messages(order_id="ORD-00001", user_message=msg_basic)
    )
    print(out_a1)

    print("\n=== (a) Estado de pedido — cadena de prompts (ejemplo con retraso) ===\n")
    msg_improved = (
        "Necesito el seguimiento, la fecha de entrega y el enlace para rastrear el paquete. "
        "Si hay algún problema, explícamelo con claridad."
    )
    out_a2 = get_chat_completion(
        build_pedido_messages(order_id="ORD-00005", user_message=msg_improved)
    )
    print(out_a2)

    print("\n=== (a) Pedidos por categoría (sin order_id) ===\n")
    msg_cat = "Lista mis pedidos de esta categoría y señala si alguno va retrasado y por qué."
    out_a3 = get_chat_completion(
        build_pedido_messages(categoria="ropa", user_message=msg_cat)
    )
    print(out_a3)

    print("\n=== (b) Devolución — producto higiene (no usualmente retornable) ===\n")
    out_b1 = get_chat_completion(
        build_devolucion_messages(
            producto="Cepillo dental eléctrico",
            categoria="Higiene personal",
            motivo="No me gustó el color después de abrirlo.",
        )
    )
    print(out_b1)

    print("\n=== (b) Devolución — electrónica sin abrir ===\n")
    out_b2 = get_chat_completion(
        build_devolucion_messages(
            producto="Auriculares Bluetooth marca EcoSound",
            categoria="Electrónica",
            motivo="Compré dos por error; la caja está sin abrir.",
        )
    )
    print(out_b2)


if __name__ == "__main__":
    main()
