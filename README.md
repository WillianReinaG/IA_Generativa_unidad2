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

### Instalación (recomendada en Windows)

El archivo `requirements.txt` instala solo lo necesario para el **notebook en Cursor/VS Code** y para `run_fase3.py`, sin el metapaquete `jupyter` completo (evita rutas extremadamente largas bajo `.venv` que en Windows suelen superar el límite clásico de 260 caracteres).

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
