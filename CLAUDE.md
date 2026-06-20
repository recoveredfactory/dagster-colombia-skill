# CLAUDE.md — guía para Claude Code en este repo

Teaching repo for a live, **Spanish-language** open-data class in Colombia. It walks
students end-to-end: acquire open data → process it → visualize it.

```
datos.gov.co ──(skill)──▶ raw ──(Dagster)──▶ clean ──▶ dashboard.json ──(Next.js)──▶ tablero
```

## Idioma

- **Responde a los estudiantes en español.** This is a Spanish-language class; default to
  Spanish for any student-facing explanation. (If the user clearly writes in English — e.g.
  the maintainer — match them.)
- Keep **code, identifiers, comments, and commit messages in English.** Student-facing prose
  (README, CONTRIBUTING, issues, PRs) is in Spanish.

## The fastest path for a student

The whole point of using Claude Code here is to skip setup friction and get to real data fast.
A student opens Claude **in this repo** and just asks, in Spanish:

```
> busca datasets de internet por departamento en datos.gov.co
> ¿qué columnas tiene el dataset n48w-gutb?
> dame los accesos a internet por departamento en 2023, de mayor a menor
```

When they ask for data from **datos.gov.co** (or another Colombian Socrata portal), use the
**`colombia-open-data`** skill in [`.claude/skills/`](.claude/skills/colombia-open-data/) — it
auto-loads here. The skill is stdlib-only, so it runs under bare `python3` with no install.
Read its `SKILL.md` for the `search` / `schema` / `query` workflow and SoQL tips.

After they've seen real data, help them build the rest when they ask — install deps, run the
pipeline, launch the web (commands below).

## The three layers

| Capa | Carpeta | Qué hace |
|------|---------|----------|
| Adquisición (skill) | `.claude/skills/colombia-open-data/` | CLI stdlib para `search`/`schema`/`query` en Socrata |
| Procesamiento (Dagster) | `pipeline/` | `raw_dataset → clean_dataset → dashboard_data` (escribe JSON) |
| Visualización (Next.js) | `web/` | Una página: lee el JSON, muestra tabla + gráfica |

**One source of truth:** the pipeline imports the skill's `socrata.py` directly (via sys.path
in `pipeline/colombia_pipeline/acquisition.py`). Fix acquisition bugs in the skill, not in a copy.

## Anchored dataset

Everything is anchored to **`n48w-gutb`** — *Internet Fijo: Accesos por tecnología y segmento*
(MinTIC), department-level, 2016–2023, DIVIPOLA codes. It has **2.8M rows and every column is
stored as `text`** — two real lessons: aggregate **server-side** (`$group`) so you pull tens of
rows, and **cast** numbers (`no_de_accesos::number` in SoQL, `astype(int)` in pandas).

## Running it (manual, for when a student wants the steps)

```bash
# verify the skill live (stdlib only, no install):
python3 scripts/smoke.py

# pipeline deps (no uv needed):
cd pipeline && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
#   (uv users: `uv sync --extra dev`, then prefix commands with `uv run`)

# generate the JSON, then view it:
dagster dev                       # http://localhost:3000 → "Materialize all"
cd web && npm install && npm run dev -- -p 3001   # http://localhost:3001 (Dagster owns 3000)

# tests (offline cassettes; `-m live` hits the real API):
pytest -m "not live"
```

## Gotchas worth flagging to students

- **Stock vs. flow.** The dashboard metric is a quarterly **stock snapshot** (latest quarter),
  not a cumulative `sum` across quarters — a right sum of the wrong unit is still wrong. Verify
  both the arithmetic *and* the semantics of an aggregation.
- **Spanish accents/casing** in `$where` are sensitive — empty result usually means a spelling/
  casing mismatch, not "no data."
- **DANE microdata is out of scope.** Most DANE microdata (CNPV census, GEIH, ECV…) lives on
  DANE/ANDA, not Socrata. The skill detects this and **bails cleanly** — don't fake it; relay the
  bail message and point to the open `good first issue`.
- **Big datasets:** prefer server-side aggregation; the skill warns when a pull would be large.
</content>
