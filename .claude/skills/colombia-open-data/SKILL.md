---
name: colombia-open-data
description: >-
  Acquire data from Colombia's open-data portal datos.gov.co (which runs on
  Socrata). Use when the user wants to find, inspect, or query Colombian public
  datasets — search by keyword, read a dataset's columns, or pull rows with SoQL
  filters/aggregations. Covers any Socrata-based Colombian portal (domain is a
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

Run from the **skill root** (`.claude/skills/colombia-open-data/`); commands use the path
`scripts/cli.py`. JSON goes to **stdout**; size hints, warnings, and the DANE bail
message go to **stderr** (so you can pipe stdout safely).

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
