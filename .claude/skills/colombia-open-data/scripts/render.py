"""
render.py — turn query results into ONE self-contained HTML page (bar chart + table).

Stdlib only, no framework, no build step: a single file you can open in a browser
or send to someone. This is the "visualize + publish" step, scaled down. Imported by
the contrib pipelines (one source of truth, like socrata.py) and exposed as `cli.py html`.

    import render
    html_doc = render.bar_chart_html(
        rows, label_key="departamento", value_key="accesos",
        title="Acceso a internet fijo por departamento", source="datos.gov.co (n48w-gutb)",
    )
    open("index.html", "w", encoding="utf-8").write(html_doc)
"""
from __future__ import annotations

import html as _html


def to_number(value):
    """Socrata sends everything as text — coerce to int/float for sorting + bar widths.
    Returns None when a value isn't numeric (those rows are skipped in the chart)."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return value
    s = str(value).strip().replace(",", "")
    if not s:
        return None
    try:
        f = float(s)
    except ValueError:
        return None
    return int(f) if f.is_integer() else f


def format_number(value):
    """Thousands grouping the Colombian/European way: 2251960 -> '2.251.960'."""
    if value is None:
        return ""
    if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
        return f"{int(value):,}".replace(",", ".")
    # comma decimal, dot thousands: 1234.5 -> '1.234,50'
    return f"{value:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")


_PAGE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{ color-scheme: light; }}
  html, body {{ margin: 0; }}
  body {{
    font-family: -apple-system, system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1a1a1a; background: #fff;
    max-width: 720px; margin: 0 auto; padding: 34px 38px 30px;
  }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  p.sub {{ color: #6b7280; margin: 0 0 22px; font-size: 13px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  td {{ padding: 7px 0; vertical-align: middle; }}
  td.label {{ width: 38%; font-size: 14px; padding-right: 12px; }}
  td.num {{ width: 116px; text-align: right; font-variant-numeric: tabular-nums;
            font-size: 14px; color: #374151; padding-left: 14px; }}
  .track {{ background: #eef1f5; border-radius: 4px; }}
  .bar {{ height: 20px; background: #2563eb; border-radius: 4px; min-width: 2px; }}
  footer {{ margin-top: 20px; color: #9aa1ad; font-size: 11px; }}
</style>
</head>
<body>
  <h1>{title}</h1>
  {subtitle}
  <table>
{rows}
  </table>
  <footer>{footer}</footer>
</body>
</html>
"""

_ROW = ('    <tr><td class="label">{label}</td>'
        '<td><div class="track"><div class="bar" style="width:{pct:.1f}%"></div></div></td>'
        '<td class="num">{num}</td></tr>')


def bar_chart_html(records, *, label_key, value_key, title,
                   subtitle=None, source=None, max_rows=25):
    """Build a standalone HTML page (horizontal bar chart + table) from `records`
    (a list of dicts, e.g. the output of `cli.py query`). Rows are sorted by value
    descending; bars scale to the largest value. Returns the HTML as a string."""
    pairs = []
    for r in records:
        n = to_number(r.get(value_key))
        if n is None:
            continue
        pairs.append((str(r.get(label_key, "")), n))
    pairs.sort(key=lambda x: x[1], reverse=True)
    pairs = pairs[:max_rows]
    top = pairs[0][1] if pairs else 0

    rows = "\n".join(
        _ROW.format(label=_html.escape(label), pct=(n / top * 100 if top else 0),
                    num=format_number(n))
        for label, n in pairs
    )
    sub = f'<p class="sub">{_html.escape(subtitle)}</p>' if subtitle else ""
    footer = "Generado con el skill colombia-open-data · una sola página, sin framework"
    if source:
        footer = f"Fuente: {_html.escape(source)} · " + footer

    return _PAGE.format(title=_html.escape(title), subtitle=sub, rows=rows, footer=footer)
