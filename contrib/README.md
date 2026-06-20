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

2. **Copia la plantilla** a una carpeta con tu nombre:
   ```bash
   cp -r contrib/_template contrib/tu-nombre
   ```

3. **Edita `contrib/tu-nombre/etl.py`**: cambia `DATASET_ID`, la consulta SoQL y la
   función `clean()`. El cliente HTTP (`socrata.py`) se reutiliza — no lo copies.

4. **Pruébalo** (graba el cassette la primera vez, luego se reproduce sin red):
   ```bash
   uv run --project pipeline pytest contrib/tu-nombre
   ```

5. **Míralo en Dagster** (opcional):
   ```bash
   uv run --project pipeline dagster dev -f contrib/tu-nombre/etl.py
   ```

6. **Abre un PR** con la lista de verificación de la plantilla de PR.

## Reglas

- Reutiliza `.claude/skills/colombia-open-data/scripts/socrata.py`; no dupliques código HTTP.
- Verifica tu `DATASET_ID` en vivo (que la consulta devuelva filas).
- Agrega al menos una prueba (la plantilla ya trae dos).
- Si tu dataset es enorme, **agrega en el servidor** (`$group`) en vez de descargar
  todo. Si es realmente microdato del DANE, está fuera de alcance (ver el skill).
- No incluyas tokens ni datos pesados; `contrib/**/data/` está en `.gitignore`.
