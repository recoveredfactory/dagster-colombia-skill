# contrib/ — tus propios pipelines

Aquí cada estudiante agrega su **propio** pipeline para un dataset de
[datos.gov.co](https://www.datos.gov.co), siguiendo el flujo de la clase:
**issue → rama → PR → merge** (ver [`../CONTRIBUTING.md`](../CONTRIBUTING.md)).

## Cómo agregar el tuyo

1. **Elige un dataset** con el skill (desde la raíz del repo):
   ```bash
   python3 .claude/skills/colombia-open-data/scripts/cli.py search "tu tema" --limit 5
   ```
   Anota el `id` (el 4x4, por ejemplo `n48w-gutb`).

2. **Crea tu carpeta** con un comando — copia la plantilla, fija tu dataset e **imprime los
   pasos para correrlo** (desde la raíz del repo):
   ```bash
   python3 .claude/skills/colombia-open-data/scripts/cli.py scaffold tu-nombre --dataset <4x4>
   ```
   (Omite el cassette de la plantilla, así tu prueba lo graba contra tu dataset la 1.ª vez.
   ¿Prefieres a mano? `cp -r contrib/_template contrib/tu-nombre && rm -rf contrib/tu-nombre/cassettes`.)

3. **Edita `contrib/tu-nombre/etl.py`**: la consulta SoQL (tu `DATASET_ID` ya quedó fijado),
   la función `clean()` y `LABEL_COL`/`VALUE_COL`/`TITLE` (para la página). El cliente HTTP
   (`socrata.py`) y el render HTML (`render.py`) se reutilizan — no los copies.

4. **Pruébalo.** Necesitas las dependencias del pipeline (Dagster, pandas); si aún no las
   instalaste, hazlo primero (ver el README, *Camino 2* paso 2). Luego, desde la raíz del repo:
   ```bash
   source pipeline/.venv/bin/activate     # Windows: pipeline\.venv\Scripts\activate
   pytest contrib/tu-nombre               # 1.ª vez: graba el cassette por red; luego va sin red
   ```
   > Con **uv** en vez de venv: `uv run --project pipeline pytest contrib/tu-nombre`.

5. **Míralo correr** (opcional, con el entorno activado):
   ```bash
   # headless — escribe el JSON, sin levantar servidor:
   dagster asset materialize --select '*' -f contrib/tu-nombre/etl.py
   # o la interfaz visual de Dagster (servidor en http://localhost:3000):
   dagster dev -f contrib/tu-nombre/etl.py
   ```
   Escribe dos archivos en `contrib/tu-nombre/data/`: `dashboard.json` y una página
   **`index.html`** autocontenida (gráfica de barras + tabla) que puedes abrir o compartir.
   ¿Quieres una página a partir de cualquier consulta, sin pipeline? Usa
   `python3 .claude/skills/colombia-open-data/scripts/cli.py html` (ver el `SKILL.md`).

6. **Abre un PR** (crea primero tu rama — ver [`../CONTRIBUTING.md`](../CONTRIBUTING.md)) y
   llena la lista de verificación de la plantilla de PR.

## Reglas

- Reutiliza `.claude/skills/colombia-open-data/scripts/socrata.py`; no dupliques código HTTP.
- Verifica tu `DATASET_ID` en vivo (que la consulta devuelva filas).
- Agrega al menos una prueba (la plantilla ya trae dos).
- Si tu dataset es enorme, **agrega en el servidor** (`$group`) en vez de descargar
  todo. Si es realmente microdato del DANE, está fuera de alcance (ver el skill).
- No incluyas tokens ni datos pesados; `contrib/**/data/` está en `.gitignore`.
