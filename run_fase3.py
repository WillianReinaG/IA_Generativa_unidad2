"""
Ejecuta los prompts de la Fase 3 sin Jupyter (misma lógica que el notebook).

Uso (desde la carpeta unidad_2):
  set OPENAI_API_KEY=tu_clave
  python run_fase3.py
"""

from __future__ import annotations

from ecomarket.client import get_chat_completion
from ecomarket.prompts import build_devolucion_messages, build_pedido_messages


def main() -> None:
    print("=== (a) Estado de pedido — ejemplo básico ===\n")
    msg_basic = 'Dame el estado del pedido ORD-12345.'
    out_a1 = get_chat_completion(
        build_pedido_messages(order_id="ORD-12345", user_message=msg_basic)
    )
    print(out_a1)

    print("\n=== (a) Estado de pedido — ejemplo mejorado (retraso) ===\n")
    msg_improved = (
        "Actúa como un agente de servicio al cliente amable. "
        "Proporciona el estado actual del pedido con el número de seguimiento indicado en los datos. "
        "Incluye estimación de entrega y enlace de rastreo en tiempo real. "
        "Si el pedido está retrasado, ofrece una disculpa y una breve explicación."
    )
    out_a2 = get_chat_completion(
        build_pedido_messages(order_id="ORD-99999", user_message=msg_improved)
    )
    print(out_a2)

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
