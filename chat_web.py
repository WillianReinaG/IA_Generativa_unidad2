"""
Chat web EcoMarket — Streamlit.

Uso (desde la raíz del proyecto, con .venv activado):
    streamlit run chat_web.py

Requiere OPENAI_API_KEY en .env o en el entorno.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

import streamlit as st

from ecomarket.client import get_chat_completion
from ecomarket.prompts import build_devolucion_messages, build_pedido_messages
from ecomarket.routing import armar_mensajes_atencion_pedido

PEDIDOS_JSON = ROOT / "data" / "pedidos_ejemplo.json"
POLITICA_JSON = ROOT / "data" / "politica_devoluciones.json"


def _armar_mensajes(tipo: str, prompt: str, cfg: dict) -> list[dict]:
    if tipo == "Pedido o seguimiento (con enrutamiento)":
        oid = (cfg.get("order_id") or "").strip()
        if not oid:
            raise ValueError("Indica el número de pedido en la barra lateral (ej. ORD-00001).")
        return armar_mensajes_atencion_pedido(
            user_message=prompt,
            order_id=oid,
            pedidos_path=PEDIDOS_JSON,
        )[0]
    if tipo == "Pedido directo (sin clasificar escalamiento)":
        oid = (cfg.get("order_id") or "").strip()
        if not oid:
            raise ValueError("Indica el número de pedido.")
        return armar_mensajes_atencion_pedido(
            user_message=prompt,
            order_id=oid,
            pedidos_path=PEDIDOS_JSON,
            ignorar_clasificacion=True,
        )[0]
    if tipo == "Pedidos por categoría":
        cat = (cfg.get("categoria") or "").strip()
        if not cat:
            raise ValueError("Indica la categoría (ej. ropa, electronicos).")
        return build_pedido_messages(
            user_message=prompt,
            categoria=cat,
            pedidos_path=PEDIDOS_JSON,
        )
    if tipo == "Devolución":
        p = (cfg.get("producto") or "").strip()
        c = (cfg.get("categoria_producto") or "").strip()
        m = (cfg.get("motivo") or "").strip()
        if not p or not c or not m:
            raise ValueError("Completa producto, categoría del producto y motivo en la barra lateral.")
        return build_devolucion_messages(
            producto=p,
            categoria=c,
            motivo=m,
            politica_path=POLITICA_JSON,
        )
    raise ValueError(f"Tipo desconocido: {tipo}")


def main() -> None:
    st.set_page_config(page_title="EcoMarket — Atención al cliente", page_icon="🛒", layout="centered")
    st.title("EcoMarket — Chat de atención")
    st.caption(
        "El pedido, categoría o datos de devolución se toman de la barra lateral. "
        "Cada envío llama al modelo con datos actualizados; el historial sirve como referencia visual."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("Configuración")
        tipo = st.selectbox(
            "Tipo de consulta",
            [
                "Pedido o seguimiento (con enrutamiento)",
                "Pedido directo (sin clasificar escalamiento)",
                "Pedidos por categoría",
                "Devolución",
            ],
            index=0,
        )
        order_id = st.text_input("Número de pedido", value="ORD-00001", help="Para modos de pedido.")
        categoria = st.text_input("Categoría", value="ropa", help="Solo para «Pedidos por categoría».")
        st.subheader("Devolución (si aplica)")
        producto = st.text_input("Producto", value="Auriculares Bluetooth")
        categoria_producto = st.text_input("Categoría del producto", value="Electrónica")
        motivo = st.text_area("Motivo", value="Llegó con la caja dañada.", height=80)
        temp = st.slider("Temperatura del modelo", 0.0, 1.0, 0.35, 0.05)
        if st.button("Borrar conversación en pantalla"):
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.markdown(
            "Los estilos del asistente salen de `config/prompt_estilos.toml`. "
            "Datos de pedido: `data/pedidos_ejemplo.json`."
        )

    cfg = {
        "order_id": order_id,
        "categoria": categoria,
        "producto": producto,
        "categoria_producto": categoria_producto,
        "motivo": motivo,
    }

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Escribe tu mensaje como cliente…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                msgs = _armar_mensajes(tipo, prompt, cfg)
            except ValueError as e:
                st.error(str(e))
                st.session_state.messages.append({"role": "assistant", "content": f"*{e}*"})
                st.stop()
            except EnvironmentError as e:
                st.error(str(e))
                st.session_state.messages.append({"role": "assistant", "content": f"*Error de configuración: {e}*"})
                st.stop()
            with st.spinner("Generando respuesta…"):
                try:
                    reply = get_chat_completion(msgs, temperature=temp)
                except Exception as e:
                    st.error(f"Error al llamar al modelo: {e}")
                    reply = f"No se pudo obtener respuesta: {e}"
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
