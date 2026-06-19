<!-- Gracias por tu PR 🎉  Llena lo siguiente. -->

## Qué hace este PR
<!-- Resumen en 1–2 frases. -->

## Issue relacionado
Closes #

## Lista de verificación
- [ ] La rama sale de `main` y el PR apunta a `main` (no commit directo a `main`).
- [ ] `uv run --project pipeline pytest -m "not live"` pasa en local.
- [ ] Si toqué la web: `cd web && npm run build` pasa.
- [ ] Si agregué un pipeline en `contrib/`: verifiqué el `DATASET_ID` en vivo,
      reutilicé `socrata.py` (no dupliqué HTTP) y agregué al menos una prueba.
- [ ] No incluyo tokens, secretos ni datos pesados.
