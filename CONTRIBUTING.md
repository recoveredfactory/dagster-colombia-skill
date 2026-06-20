# Cómo contribuir

Así trabajamos en clase: **issue → rama → PR → merge**. Nunca hacemos commit directo a
`main`. Cada cambio empieza con un issue (una tarea) y termina con un Pull Request que
alguien revisa y fusiona.

## El flujo, paso a paso

### 1. Toma o crea un issue

- Mira los issues abiertos: <https://github.com/recoveredfactory/dagster-colombia-skill/issues>
- Los marcados **`good-first-issue`** son buenos para empezar.
- ¿Vas a hacer algo nuevo? Crea un issue con la plantilla **Nueva tarea**.
- Comenta en el issue para avisar que lo estás tomando.

### 2. Crea una rama

Desde `main` actualizado, crea una rama con un nombre corto y descriptivo:

```bash
git checkout main
git pull
git checkout -b mapa-departamentos    # ej. para el issue del mapa
```

### 3. Haz tus cambios y pruébalos

```bash
uv run --project pipeline pytest -m "not live"   # pruebas (sin red)
cd web && npm run build                          # si tocaste la web
```

Haz commits pequeños y con mensajes claros:

```bash
git add -A
git commit -m "Agrega mapa coroplético por departamento"
```

### 4. Sube la rama y abre el PR

```bash
git push -u origin mapa-departamentos
```

GitHub te dará un enlace para abrir el Pull Request. Llena la plantilla y enlaza el
issue con `Closes #NÚMERO`. La integración continua (CI) correrá las pruebas y el build
de la web automáticamente.

### 5. Revisión y merge

- Alguien revisa tu PR y deja comentarios.
- Ajusta si hace falta (haz más commits en la misma rama).
- Cuando esté aprobado y el CI en verde ✅, se hace **merge** a `main`.
- Borra tu rama. ¡Listo! 🎉

## Reglas rápidas

- **No** hagas commit directo a `main`.
- Reutiliza el cliente del skill (`.claude/skills/colombia-open-data/scripts/socrata.py`); no
  dupliques código HTTP.
- Agrega o actualiza pruebas con tus cambios.
- No subas tokens, secretos ni datos pesados.
- Los issues y los PR se escriben en **español**.

¿Dudas? Abre un issue o pregunta en clase.
