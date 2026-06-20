#!/usr/bin/env python3
"""
cli.py — stdlib CLI for the colombia-open-data acquisition skill.

Subcommands:
  search <keywords>        Discover datasets on datos.gov.co (Discovery API)
  schema <4x4>             List a dataset's columns + types (and a size sniff)
  query  <4x4> [SoQL...]   Run a SoQL query, printing JSON rows (sniffs size first)
  html   <rows.json>       Render query JSON as a one-file HTML page (bar chart + table)
  scaffold <name>          Copy the Dagster pipeline template into contrib/<name> + print run steps
  dane-check <text>        Report whether a request is out-of-scope DANE microdata

Runs under bare `python3` with no pip install (stdlib only). JSON goes to stdout;
hints, sniff warnings, and bail messages go to stderr — so you can pipe stdout.

Examples:
  python3 cli.py search "internet por departamento"
  python3 cli.py schema n48w-gutb
  python3 cli.py query n48w-gutb \\
      --select "anno,sum(no_de_accesos::number) as accesos" --group anno --order anno
  python3 cli.py dane-check "microdatos de la GEIH 2022"
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

import dane
import render
import socrata


def _print_json(obj):
    json.dump(obj, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def _err(msg):
    print(msg, file=sys.stderr)


def cmd_search(args):
    is_dane, reason = dane.is_probably_dane(args.keywords)
    if is_dane:
        _err(dane.BAIL_MESSAGE)
        _err(f"\n(razón: {reason})")
        return 2
    results = socrata.discover(args.keywords, domain=args.domain, limit=args.limit)
    if not results:
        _err("Sin resultados. Revisa palabras clave (acentos/mayúsculas) o el dominio.")
    _print_json(results)
    return 0


def cmd_schema(args):
    cols = socrata.columns(args.dataset_id, domain=args.domain)
    if not args.no_sniff:
        est = socrata.sniff(args.dataset_id, domain=args.domain)
        _err(f"# {est['rows']:,} filas · {est['cols']} columnas · ~{est['est_mb']} MB est.")
        if est["message"]:
            _err(est["message"])
    _print_json(cols)
    return 0


def cmd_query(args):
    # Sniff only when pulling raw rows. If the query already aggregates server-side
    # (--group), the "this dataset is huge" hint is just noise.
    if not args.no_sniff and not args.group:
        est = socrata.sniff(args.dataset_id, domain=args.domain, where=args.where)
        if est["message"]:
            _err(est["message"])
    rows = socrata.query(
        args.dataset_id, domain=args.domain,
        select=args.select, where=args.where, group=args.group, order=args.order,
        having=args.having, q=args.q, limit=args.limit, offset=args.offset,
        paginate=args.paginate,
    )
    if not rows and args.where:
        _err("Resultado vacío. Los VALORES en español distinguen acentos y "
             "mayúsculas — revisa la ortografía del $where.")
    _print_json(rows)
    return 0


def cmd_html(args):
    # Read query JSON from a file or stdin, so you can pipe:  query ... | html ...
    raw = sys.stdin.read() if args.input in (None, "-") else open(args.input, encoding="utf-8").read()
    try:
        records = json.loads(raw)
    except json.JSONDecodeError as exc:
        _err(f"No pude leer el JSON de entrada: {exc}")
        return 1
    if not isinstance(records, list):
        _err("Se esperaba una LISTA de filas JSON (la salida de `query`).")
        return 1
    doc = render.bar_chart_html(
        records, label_key=args.label, value_key=args.value,
        title=args.title, subtitle=args.subtitle, source=args.source,
    )
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(doc)
        _err(f"# página escrita en {args.out} ({len(records)} filas) — ábrela en el navegador")
    else:
        sys.stdout.write(doc)
    return 0


def _repo_root():
    # cli.py lives at <repo>/.claude/skills/colombia-open-data/scripts/cli.py
    return Path(__file__).resolve().parents[4]


def cmd_scaffold(args):
    root = _repo_root()
    template = root / "contrib" / "_template"

    # The Dagster pipeline step needs the cloned class repo (Claude Code, or the manual
    # README path). Running standalone — a skill installed by itself in Claude Desktop —
    # the template just isn't here. Say so plainly instead of silently degrading to
    # "only search/query works".
    if not template.is_dir():
        _err(
            "No encuentro contrib/_template, así que el paso de pipeline Dagster NO está "
            "disponible aquí.\n"
            "Ese paso necesita el REPOSITORIO de la clase clonado (Claude Code, o el camino "
            "manual del README). Un skill suelto (p. ej. en Claude Desktop) no lo trae.\n"
            "Aquí sí funcionan: search / schema / query, y `html` para una página compartible.\n"
            "Para el pipeline, clona el repo y ábrelo en Claude Code:\n"
            "  git clone https://github.com/recoveredfactory/dagster-colombia-skill\n"
            "  cd dagster-colombia-skill && claude"
        )
        return 2

    dest = root / "contrib" / args.name
    if dest.exists():
        _err(f"Ya existe contrib/{args.name}/ — elige otro nombre o bórralo primero.")
        return 1

    # Copy WITHOUT cassettes/data/caches: a new dataset records its own cassette on the
    # first test run, and data/ is generated output (gitignored).
    shutil.copytree(
        template, dest,
        ignore=shutil.ignore_patterns("cassettes", "data", "__pycache__", "*.pyc"),
    )

    # Pin the student's dataset (and domain, if non-default) into the fresh etl.py so
    # they start from their data, not the template's.
    etl = dest / "etl.py"
    text = etl.read_text(encoding="utf-8")
    if args.dataset:
        text = re.sub(r'^DATASET_ID = "[^"]*"',
                      f'DATASET_ID = "{args.dataset}"', text, count=1, flags=re.M)
    if args.domain and args.domain != socrata.DEFAULT_DOMAIN:
        text = re.sub(r'^DOMAIN = "[^"]*"',
                      f'DOMAIN = "{args.domain}"', text, count=1, flags=re.M)
    etl.write_text(text, encoding="utf-8")

    rel = f"contrib/{args.name}"
    # The run instructions are the whole point of this command. Human steps to stderr
    # (like every other hint here); machine-readable summary to stdout.
    _err(
        f"\n✓ Creé {rel}/ a partir de la plantilla.\n"
        f"  dataset: {args.dataset or 'n48w-gutb (el de la plantilla — cámbialo)'}\n\n"
        f"1) Edita {rel}/etl.py: la consulta SoQL del asset `raw`, la función `clean()` "
        f"y LABEL_COL/VALUE_COL/TITLE.\n\n"
        f"2) Córrelo (desde la raíz del repo). Activa primero el entorno del pipeline\n"
        f"   (instálalo una vez — README «Camino 2» paso 2):\n"
        f"     source pipeline/.venv/bin/activate     # Windows: pipeline\\.venv\\Scripts\\activate\n"
        f"   Sin servidor (escribe el JSON y la página HTML):\n"
        f"     dagster asset materialize --select '*' -f {rel}/etl.py\n"
        f"   …o la interfaz visual de Dagster (http://localhost:3000):\n"
        f"     dagster dev -f {rel}/etl.py\n\n"
        f"3) Pruébalo (la 1.ª vez graba el cassette por red; luego corre sin red):\n"
        f"     pytest {rel}\n\n"
        f"Resultados en {rel}/data/: dashboard.json e index.html (ábrela en el navegador).\n"
        f"Cuando te guste: crea una rama y haz commit (git checkout -b {args.name}); "
        f"el PR es tu paso.\n"
    )
    _print_json({
        "created": rel,
        "dataset_id": args.dataset or "n48w-gutb",
        "etl": f"{rel}/etl.py",
        "run": [
            "source pipeline/.venv/bin/activate",
            f"dagster asset materialize --select '*' -f {rel}/etl.py",
            f"pytest {rel}",
        ],
    })
    return 0


def cmd_dane_check(args):
    is_dane, reason = dane.is_probably_dane(args.text)
    if is_dane:
        _err(dane.BAIL_MESSAGE)
        _print_json({"dane": True, "reason": reason})
        return 2
    _print_json({"dane": False, "reason": ""})
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="cli.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--domain", default=socrata.DEFAULT_DOMAIN,
                   help=f"Socrata domain (default: {socrata.DEFAULT_DOMAIN})")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", help="discover datasets")
    s.add_argument("keywords")
    s.add_argument("--limit", type=int, default=10)
    s.set_defaults(func=cmd_search)

    sc = sub.add_parser("schema", help="list a dataset's columns")
    sc.add_argument("dataset_id")
    sc.add_argument("--no-sniff", action="store_true")
    sc.set_defaults(func=cmd_schema)

    q = sub.add_parser("query", help="run a SoQL query")
    q.add_argument("dataset_id")
    q.add_argument("--select")
    q.add_argument("--where")
    q.add_argument("--group")
    q.add_argument("--order")
    q.add_argument("--having")
    q.add_argument("--q", help="$q full-text search")
    q.add_argument("--limit", type=int)
    q.add_argument("--offset", type=int)
    q.add_argument("--paginate", action="store_true",
                   help="fetch every matching row past the 50k page cap")
    q.add_argument("--no-sniff", action="store_true")
    q.set_defaults(func=cmd_query)

    h = sub.add_parser("html", help="render query JSON as a one-file HTML page (bar chart + table)")
    h.add_argument("input", nargs="?", default="-",
                   help="JSON file from `query` (default: - = stdin, so you can pipe)")
    h.add_argument("--label", required=True, help="column for the row label (e.g. departamento)")
    h.add_argument("--value", required=True, help="numeric column for the bar (e.g. accesos)")
    h.add_argument("--title", default="Tablero — datos.gov.co")
    h.add_argument("--subtitle")
    h.add_argument("--source", help="data source note for the footer (e.g. 'datos.gov.co (n48w-gutb)')")
    h.add_argument("--out", help="write the page to this file (default: stdout)")
    h.set_defaults(func=cmd_html)

    sca = sub.add_parser("scaffold",
                         help="copy the Dagster pipeline template into contrib/<name> and print run steps")
    sca.add_argument("name", help="folder name under contrib/ (e.g. tu-nombre)")
    sca.add_argument("--dataset", help="4x4 dataset id to pin into etl.py (e.g. n48w-gutb)")
    sca.set_defaults(func=cmd_scaffold)

    d = sub.add_parser("dane-check", help="is this request out-of-scope DANE microdata?")
    d.add_argument("text")
    d.set_defaults(func=cmd_dane_check)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except socrata.SocrataError as exc:
        _err(f"Error de Socrata: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
