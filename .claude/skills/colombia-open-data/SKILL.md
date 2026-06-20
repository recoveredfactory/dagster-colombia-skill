---
name: colombia-open-data
description: >-
  Acquire data from Colombia's open-data portal datos.gov.co (which runs on
  Socrata). Use when the user wants to find, inspect, or query Colombian public
  datasets — search by keyword, read a dataset's columns, or pull rows with SoQL
  filters/aggregations — then turn one into a small raw→clean→dashboard Dagster
  pipeline of their own. Covers any Socrata-based Colombian portal (domain is a
  parameter). NOT for DANE microdata (census/GEIH/ECV unit records) — see "Scope".
---

# colombia-open-data

A tiny, dependency-free toolkit for pulling data from **datos.gov.co** (Socrata).
The scripts use only the Python standard library, so they run under bare `python3`
with **no `pip install`**.

## Scope — read this first

**In scope:** anything published on datos.gov.co (and other Colombian Socrata
portals) — aggregated tables, public registries, indicators, contracts, etc.

**Out of scope: DANE microdata.** Most DANE microdata (CNPV census unit records,
GEIH, ECV, ENUT, …) lives on DANE's own portal / ANDA, **not** on Socrata. If a
request is really DANE microdata, **bail cleanly** — do not fake it or return junk.
Verify with:

```bash
python3 scripts/cli.py dane-check "<the user's request>"
```

If it reports `dane: true`, tell the user plainly that DANE microdata is out of
scope for this skill, suggest using regular Claude or another tool for now, and
point them to the open GitHub issue **"Agregar soporte para DANE"**. The verdict
JSON is on stdout and the human-readable bail message is on **stderr** — relay that
message. The bail logic lives in `scripts/dane.py` (`is_probably_dane`).

## Workflow

Steps 1–3 (the skill CLI) are written to run from the **skill root**
(`.claude/skills/colombia-open-data/`), using `scripts/cli.py`; from the repo root, use the
full path. Step 4 (the pipeline — `cp`, `pytest`, `dagster`, `git`) runs from the **repo
root**. JSON goes to **stdout**; size hints, warnings, and the DANE bail message go to
**stderr** (so you can pipe stdout safely).

1. **Discover** datasets by keyword:
   ```bash
   python3 scripts/cli.py search "internet por departamento" --limit 5
   ```
   Each result has `id` (the 4x4, e.g. `n48w-gutb`), `name`, `description`, `category`.

2. **Inspect** a dataset's columns and types (also prints a size sniff):
   ```bash
   python3 scripts/cli.py schema n48w-gutb
   ```

3. **Query** with SoQL (`$select`, `$where`, `$group`, `$order`, `$having`, `$q`,
   `$limit`, `$offset`). See `references/soql.md` for the cheat sheet.
   ```bash
   python3 scripts/cli.py query n48w-gutb \
     --select "anno,sum(no_de_accesos::number) as accesos" --group anno --order anno
   ```
   For a **top-N ranking**, add `--order "<col> desc" --limit N`.

4. **Make it their own pipeline** (the real goal — not just a one-off query): once the
   user likes a dataset, offer to scaffold a small **`raw → clean → dashboard`** Dagster
   pipeline for it. The scaffold already exists. **From the repo root:**
   - **Copy the template:** `cp -r contrib/_template contrib/<nombre>`, then
     `rm -rf contrib/<nombre>/cassettes` (the copied cassette is for the template's
     dataset — clearing it lets the test re-record against the new one on first run).
   - **Adapt it:** in `contrib/<nombre>/etl.py`, set `DATASET_ID` + the `raw` asset's SoQL
     query, and adapt `clean()` to their columns (Socrata sends everything as text — cast
     the numbers). It reuses this skill's `socrata.py` and writes a `dashboard.json`.
   - **Run it** — this needs the pipeline deps (Dagster/pandas), which the stdlib skill does
     *not* install; set them up once (README "Camino 1" paso 3 / "Camino 2" paso 2), then
     `source pipeline/.venv/bin/activate`. Quick headless check (no server, writes the JSON):
     `dagster asset materialize --select '*' -f contrib/<nombre>/etl.py`. For the visual UI
     instead: `dagster dev -f contrib/<nombre>/etl.py` (a server on :3000). Test:
     `pytest contrib/<nombre>`.
   - **Close the loop the way the class does (issue → rama → PR).** Merging student
     pipelines into the repo is out of scope, but offer to give them the real flow: put it
     on a branch (`git checkout -b contrib/<nombre>` and commit), and tell them they can open
     a Pull Request when ready (`CONTRIBUTING.md`; the `good first issue` "agrega tu pipeline").
     **Branch and commit for them; don't push or open the PR — that's their step.**

   Details: `contrib/README.md`.

## Guaranteed-working demo (verified live)

Dataset **`n48w-gutb`** — *Internet Fijo: Accesos por tecnología y segmento*
(MinTIC). Department-level, historical (2016–2023), with DIVIPOLA codes.

- It has **2.8M rows and every column is stored as `text`** — two realistic lessons:
  the size sniff will suggest aggregating server-side, and numbers need casting
  (`no_de_accesos::number` in SoQL, or `astype(int)` in pandas).
- Aggregate server-side so you only pull tens of rows:
  ```bash
  # accesos by department (map-ready: includes DIVIPOLA cod_departamento)
  python3 scripts/cli.py query n48w-gutb \
    --select "cod_departamento,departamento,sum(no_de_accesos::number) as accesos" \
    --group "cod_departamento,departamento" --order "accesos desc"
  ```
  Note: this `sum(...)` is cumulative across all years/quarters in the dataset. For a
  single year, add `--where "anno='2023'"`.

## Notes

- Default domain is `www.datos.gov.co`; pass `--domain` for other Colombian Socrata
  portals.
- Spanish field names and values keep their accents — `$where` values are
  accent- and case-sensitive. On an empty result, check spelling/casing.
- An optional `SODA_APP_TOKEN` env var lifts rate limits; everything works without one.
- A single SODA page returns at most 50,000 rows; use `--paginate` to fetch past it.
- The Dagster pipeline in `../../../pipeline/` imports `scripts/socrata.py` directly —
  the same acquisition code, one source of truth.
