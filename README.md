# IA Generativa — Unidad 2 — EcoMarket

Proyecto académico: **IA generativa para optimizar la atención al cliente** en EcoMarket (e-commerce).

## Contenido

| Entregable | Descripción |
|------------|-------------|
| [FASE1_seleccion_modelo.md](FASE1_seleccion_modelo.md) | Selección y justificación del modelo + arquitectura con BD |
| [FASE2_fortalezas_limitaciones_eticos.md](FASE2_fortalezas_limitaciones_eticos.md) | Fortalezas, limitaciones y riesgos éticos |
| [notebooks/fase3_prompts_ecomarket.ipynb](notebooks/fase3_prompts_ecomarket.ipynb) | Ejecución de prompts (Fase 3) |
| [run_fase3.py](run_fase3.py) | Misma lógica que el notebook, por terminal |

Los datos de ejemplo están en `data/` (simulan catálogo/pedidos/políticas).

## Requisitos

- Python 3.10+
- Cuenta OpenAI y variable de entorno `OPENAI_API_KEY`

```powershell
cd "C:\Users\bebes\Documents\MIAA\3. SEMESTRE\4. IA_GENERATIVA\unidad_2"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edita .env y coloca tu clave
jupyter notebook notebooks\fase3_prompts_ecomarket.ipynb
```

Alternativa sin Jupyter:

```powershell
python run_fase3.py
```

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
