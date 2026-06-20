# Datos abiertos de Colombia — proyecto de clase

*An end-to-end teaching project: acquire data from datos.gov.co (Socrata), process it
with Dagster, and visualize it with Next.js. Docs for students are in Spanish; code is
in English.*

Un proyecto **de extremo a extremo** para aprender el flujo de datos abiertos:

```
datos.gov.co ──(skill)──▶  raw ──(Dagster)──▶ clean ──▶ dashboard.json ──(Next.js)──▶ tablero
   Socrata        adquirir            procesar / limpiar            visualizar
```

Está anclado a **un** dataset real y verificado: `n48w-gutb` —
*Internet Fijo: Accesos por tecnología y segmento* (MinTIC), por departamento y año.

---

## Requisitos

- **Python 3.10+** — lo único imprescindible.
- **Node.js 20+** (probado con 22) — solo para la web (paso 4).
- Las dependencias de Python se instalan por **uno** de dos caminos (paso 2):
  - **pip + venv** — estándar, funciona en cualquier máquina (no necesitas uv).
  - **[uv](https://docs.astral.sh/uv/)** — opcional, más rápido:
    `curl -LsSf https://astral.sh/uv/install.sh | sh`

> 💡 **¿Sin ganas de instalar nada?** Abre el taller en **Google Colab** — todo corre
> en el navegador: [`docs/colab_taller.ipynb`](docs/colab_taller.ipynb).

---

## Runbook del sábado (paso a paso)

### 0. Clonar

```bash
git clone https://github.com/recoveredfactory/dagster-colombia-skill.git
cd dagster-colombia-skill
```

### 1. Verificar que todo funciona (sin instalar nada)

El skill usa solo la librería estándar, así que corre con `python3` a secas. Un solo
comando lo prueba en vivo contra datos.gov.co (también sirve para confirmar tu
instalación más adelante):

```bash
python3 scripts/smoke.py
```

O llama al skill directamente:

```bash
cd skill/colombia-open-data/scripts
python3 cli.py search "internet por departamento" --limit 5
python3 cli.py schema n48w-gutb
python3 cli.py query n48w-gutb \
  --select "anno,sum(no_de_accesos::number) as accesos" --group anno --order anno
cd ../../..
```

### 2. Instalar las dependencias del pipeline (elige A o B)

**Opción A — pip + venv** (sin uv, funciona en cualquier parte):

```bash
cd pipeline
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Opción B — uv** (más rápido, si lo tienes):

```bash
cd pipeline
uv sync --extra dev
```

> Los comandos siguientes usan el prefijo `uv run`. Si instalaste con **pip + venv**
> (Opción A), mantén el entorno activado y **omite `uv run`**: corre `dagster …` y
> `pytest …` directamente.

### 3. Correr el pipeline → genera el JSON

Opción A — **sin servidor** (rápido, headless):

```bash
uv run dagster asset materialize --select '*' -m colombia_pipeline.definitions
```

Opción B — **interfaz de Dagster** (recomendada para la clase):

```bash
uv run dagster dev
```

Abre <http://localhost:3000>, y haz clic en **Materialize all**. Verás el grafo
`raw_dataset → clean_dataset → dashboard_data`. Esto escribe los archivos JSON en
`web/public/data/`.

### 4. Correr la web → ver el tablero

En **otra terminal** (Dagster usa el puerto 3000, así que la web va en el 3001):

```bash
cd web
npm install
npm run dev -- -p 3001
```

Abre <http://localhost:3001>: una **tabla** de accesos por departamento y una
**gráfica** histórica por año.

> 🔁 **La idea clave:** cambia el JSON (vuelve a materializar en Dagster) → recarga la
> web → el tablero cambia. Datos → tablero, sin base de datos en medio.

### 5. Correr las pruebas

```bash
# uv (desde la raíz del repo):
uv run --project pipeline pytest -m "not live"

# pip + venv (con el entorno activado, desde pipeline/):
pytest -m "not live"
```

Las pruebas usan **cassettes** (respuestas reales grabadas con vcrpy) y corren sin red.
Para probar contra la API real, cambia a `-m live`.

---

## Las tres capas

| Capa | Carpeta | Qué hace |
|------|---------|----------|
| **Adquisición (skill)** | `skill/colombia-open-data/` | CLI stdlib (`urllib`) para `search` / `schema` / `query` en Socrata. Avisa si el dataset es muy grande (sugiere agregar en el servidor o usar polars). |
| **Procesamiento (Dagster)** | `pipeline/` | Tres assets: `raw_dataset` → `clean_dataset` (texto→entero, departamentos válidos) → `dashboard_data` (JSON). Reutiliza el `socrata.py` del skill. |
| **Visualización (Next.js)** | `web/` | Una página que lee el JSON y muestra tabla + gráfica. Sin backend ni base de datos. |

---

## Fuera de alcance: microdatos del DANE

La mayoría de los **microdatos del DANE** (censo CNPV, GEIH, ECV…) viven en el portal
del DANE / **ANDA**, no en Socrata. El skill **lo detecta y se detiene** limpiamente.
¿Quieres agregar soporte para DANE? Hay un issue `good-first-issue` para eso (la lógica
está en `skill/colombia-open-data/scripts/dane.py`).

## Tus propios pipelines

¿Tienes otro dataset? Agrega tu pipeline en [`contrib/`](contrib/README.md): copia la
plantilla, cambia el `DATASET_ID`, y abre un PR. Ver [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licencia

[MIT](LICENSE).
