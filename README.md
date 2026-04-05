# IA Generativa — Unidad 2 — EcoMarket

Proyecto académico: **IA generativa para optimizar la atención al cliente** en EcoMarket (e-commerce).

## Contenido

| Entregable | Descripción |
|------------|-------------|
| [FASE1_seleccion_modelo.md](FASE1_seleccion_modelo.md) | Selección y justificación del modelo + arquitectura con BD |
| [FASE2_fortalezas_limitaciones_eticos.md](FASE2_fortalezas_limitaciones_eticos.md) | Fortalezas, limitaciones y riesgos éticos |
| [notebooks/fase3_prompts_ecomarket.ipynb](notebooks/fase3_prompts_ecomarket.ipynb) | Ejecución de prompts (Fase 3) |
| [run_fase3.py](run_fase3.py) | Misma lógica que el notebook, por terminal |
| [chat_web.py](chat_web.py) | Chat en el navegador (Streamlit), sin editar código |
| [ecomarket/routing.py](ecomarket/routing.py) | Clasificación primer nivel vs escalamiento (reflejo en código del diseño 80/20) |
| [ecomarket/registro_escalamiento.py](ecomarket/registro_escalamiento.py) | Registro JSONL de escalamientos a humano (fecha, pedido, retraso) |
| [config/prompt_estilos.toml](config/prompt_estilos.toml) | Cuatro estilos de prompt (rol, contexto, tono, quejas) leídos al ejecutar |

Los datos de ejemplo están en `data/` (simulan catálogo/pedidos/políticas).

### Estilos de prompt (TOML)

El mensaje de **sistema** que recibe el modelo se compone desde **`config/prompt_estilos.toml`**: `rol_general`, `contexto_especifico`, `estilo_respuesta`, `manejo_quejas`, más reglas fijas de datos en código (`ecomarket/estilos_prompt.py`). Afecta a pedidos, devoluciones y escalamiento. Otra ruta: variable de entorno **`ECOMARKET_PROMPT_ESTILOS_TOML`**. En Python 3.10 hace falta el paquete **`tomli`** (`pip install -r requirements.txt`).

### Registro de escalamientos a humano

Cada vez que `armar_mensajes_atencion_pedido` toma la ruta de **escalamiento humano**, se añade una línea a **`data/registro_escalamientos_humanos.jsonl`** (formato [JSON Lines](https://jsonlines.org/)): `fecha_consulta` (UTC ISO), `numero_pedido` (parámetro o detectado como `ORD-#####` en el texto), `tiene_retraso` (`true` / `false` / `null` según `pedidos_ejemplo.json`), `motivo_clasificacion` y opcionalmente `categoria_consulta`. El archivo está en **`.gitignore`** para no subir datos locales al remoto. Otra ruta: variable de entorno `ECOMARKET_REGISTRO_ESCALAMIENTO`. Desactivar escritura: `armar_mensajes_atencion_pedido(..., registrar_escalamiento=False)`.

## Fortalezas y limitaciones del modelo (resumen)

El diseño del chat EcoMarket (Fase 3 + datos verificados) se apoya en un modelo **híbrido** (LLM + información de sistema). En términos de evaluación académica:

| Enfoque | Qué cabe esperar |
|--------|-------------------|
| **Fortalezas** | **Menor tiempo de primera respuesta** frente a colas humanas; **disponibilidad 24/7**; capacidad de absorber un **alto porcentaje de consultas repetitivas** (orientativo **~80 %**: seguimiento de pedido, políticas con texto fijo), alineado con `build_pedido_messages` / `build_devolucion_messages` y los JSON en `data/`. |
| **Limitaciones** | Un **~20 %** de casos **complejos** (reclamos graves, crisis, excepciones) sigue requiriendo **humano** con empatía y criterio; el modelo **no valida** la BD: si los datos son **erróneos o viejos**, puede **responder incorrectamente** aunque el texto suene coherente; persisten riesgos de **alucinación** si el contexto es pobre (mitigado en código con “solo datos verificados” y escalamiento). |

**¿Dónde está el 80/20 en el código?** No como un porcentaje que el programa imprima en cada respuesta: es un **objetivo operativo** que en producción se contrasta con métricas. En este repo la separación “primer nivel vs humano” está implementada en **`ecomarket/routing.py`**: `clasificar_consulta_cliente` + `armar_mensajes_atencion_pedido` (escalamiento con `build_escalamiento_messages` frente a la cadena de `build_pedido_messages`). Ver también `run_fase3.py` (bloque “Enrutamiento 80/20”).

El detalle argumentado, riesgos éticos y mitigaciones están en **[FASE2_fortalezas_limitaciones_eticos.md](FASE2_fortalezas_limitaciones_eticos.md)**.

## Requisitos

- Python 3.10+
- Cuenta OpenAI y variable de entorno `OPENAI_API_KEY` (nunca la subas al repositorio ni la pegues en el código)
- Por defecto se usa la **API Responses** (`gpt-5-nano`). Si tu cuenta no la soporta, en `.env` pon `ECOMARKET_USE_RESPONSES_API=false` y se usará Chat Completions (`ECOMARKET_CHAT_FALLBACK_MODEL`, por defecto `gpt-4o-mini`).

### Instalación (recomendada en Windows)

El archivo `requirements.txt` incluye el **notebook** en Cursor/VS Code, `run_fase3.py`, **Streamlit** (`chat_web.py`) y `ipykernel`, sin el metapaquete `jupyter` completo (evita rutas extremadamente largas bajo `.venv` que en Windows suelen superar el límite clásico de 260 caracteres).

```powershell
cd "C:\Users\bebes\Documents\MIAA\3. SEMESTRE\4. IA_GENERATIVA\unidad_2"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
# Edita .env y coloca tu clave
```

Abre `notebooks\fase3_prompts_ecomarket.ipynb` en **Cursor**, selecciona el kernel **Python del `.venv`** (`.venv\Scripts\python.exe`) y ejecuta las celdas.

Alternativa sin notebook:

```powershell
python run_fase3.py
```

### Chat web (Streamlit)

Interfaz en el navegador: eliges tipo de consulta y datos en la barra lateral y escribes en el chat (sin tocar código Python).

```powershell
streamlit run chat_web.py
```

Se abre una URL local (por defecto `http://localhost:8501`). Requiere `OPENAI_API_KEY` en `.env`.

### Si necesitas `jupyter notebook` en el navegador

1. **Habilitar rutas largas en Windows** (PowerShell **como administrador**), luego reinicia:

   ```powershell
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
     -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```

   Documentación: [pip — Enable long paths](https://pip.pypa.io/warnings/enable-long-paths).

2. **Acortar la ruta del proyecto** (por ejemplo `C:\MIAA\u2\`) y volver a crear el `.venv` allí.

3. Instalar: `pip install -r requirements-jupyter.txt` y usar `jupyter notebook` como antes.

### Si `pip install` ya falló a medias

Borra la carpeta `.venv`, aplica una de las soluciones anteriores y vuelve a crear el entorno e instalar.

## Repositorio remoto

Subir este contenido a: [https://github.com/WillianReinaG/IA_Generativa_unidad2](https://github.com/WillianReinaG/IA_Generativa_unidad2)

```powershell
git init
git remote add origin https://github.com/WillianReinaG/IA_Generativa_unidad2.git
git add .
git commit -m "Entrega Unidad 2: EcoMarket — documentación y prompts"
git branch -M main
git push -u origin main
```
