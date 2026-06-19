"""
socrata.py — stdlib-only client for Socrata open-data portals (e.g. datos.gov.co).

No third-party dependencies: it uses urllib, so the Skill runs anywhere Claude has
a Python interpreter, with zero `pip install`. This SAME module is imported by the
Dagster pipeline (one source of truth — the HTTP code is never duplicated).

Endpoints used:
  - Discovery:  https://api.us.socrata.com/api/catalog/v1?domains=...&q=...
  - Schema:     https://{domain}/api/views/{4x4}.json
  - SODA/SoQL:  https://{domain}/resource/{4x4}.json?$select=...&$where=...

A 4x4 is the dataset id, e.g. "n48w-gutb".
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_DOMAIN = "www.datos.gov.co"
DISCOVERY_URL = "https://api.us.socrata.com/api/catalog/v1"
USER_AGENT = "colombia-open-data-skill/0.1 (+recoveredfactory/dagster-colombia-skill)"

# Socrata serves at most 50k rows in a single SODA page; paginate past it with $offset.
SODA_PAGE_MAX = 50_000

# --- size sniff thresholds (tweakable; explained in SKILL.md) -----------------
# Above these, pandas starts to hurt on a student laptop; suggest aggregating
# server-side or reaching for polars. This is NOT the 50k pagination cap.
POLARS_SUGGEST_ROWS = 1_000_000
POLARS_SUGGEST_BYTES = 250 * 1024 * 1024  # ~250 MB
BYTES_PER_CELL_EST = 100  # rough avg for mixed Socrata text/number cells

# SoQL operators/punctuation we keep literal so URLs stay readable for students.
_SAFE = "$,():*'="


class SocrataError(RuntimeError):
    """Raised when a Socrata endpoint errors or returns an unexpected payload."""


def _headers():
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    # Optional app token lifts rate limits; everything works without one.
    token = os.environ.get("SODA_APP_TOKEN")
    if token:
        headers["X-App-Token"] = token
    return headers


def _get_json(url, *, timeout=60, retries=3, backoff=1.5):
    """GET + parse JSON, retrying transient failures (5xx / network) with backoff.
    Socrata occasionally returns a 500 on aggregate queries — a couple of retries
    keeps a live demo from breaking."""
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=_headers())
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
            return json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code >= 500 and attempt < retries:
                time.sleep(backoff * attempt)
                continue
            body = exc.read().decode("utf-8", "replace")[:600]
            raise SocrataError(f"HTTP {exc.code} from {url}\n{body}") from exc
        except urllib.error.URLError as exc:
            if attempt < retries:
                time.sleep(backoff * attempt)
                continue
            raise SocrataError(f"Network error for {url}: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise SocrataError(f"Non-JSON response from {url}: {raw[:200]!r}") from exc


def _url(base, params):
    """Build a URL, dropping None params and keeping SoQL punctuation readable."""
    clean = {k: v for k, v in params.items() if v is not None}
    query = urllib.parse.urlencode(clean, safe=_SAFE, quote_via=urllib.parse.quote)
    return f"{base}?{query}" if query else base


# --- Discovery ----------------------------------------------------------------
def discover(query, *, domain=DEFAULT_DOMAIN, limit=10):
    """Search a Socrata domain for datasets. Returns a list of dicts:
    {id, name, description, category}."""
    url = _url(DISCOVERY_URL, {
        "domains": domain,
        "q": query,
        "only": "dataset",
        "limit": str(limit),
    })
    payload = _get_json(url)
    out = []
    for item in payload.get("results", []):
        res = item.get("resource", {}) or {}
        cls = item.get("classification", {}) or {}
        out.append({
            "id": res.get("id"),
            "name": res.get("name"),
            "description": (res.get("description") or "").strip(),
            "category": cls.get("domain_category"),
        })
    return out


# --- Schema -------------------------------------------------------------------
def columns(dataset_id, *, domain=DEFAULT_DOMAIN):
    """Return a dataset's columns: [{field_name, name, type}]. Spanish names/accents
    are preserved as published."""
    url = f"https://{domain}/api/views/{dataset_id}.json"
    payload = _get_json(url)
    return [
        {
            "field_name": c.get("fieldName"),
            "name": c.get("name"),
            "type": c.get("dataTypeName"),
        }
        for c in payload.get("columns", [])
    ]


# --- SODA query ---------------------------------------------------------------
def query(dataset_id, *, domain=DEFAULT_DOMAIN, select=None, where=None, group=None,
          order=None, having=None, q=None, limit=None, offset=None, paginate=False):
    """Run a SoQL query against a dataset and return a list of row dicts.

    Pass paginate=True to fetch every matching row past the 50k page cap (loops on
    $offset). When paginate=False, `limit`/`offset` are passed straight through.
    On an empty result with a $where, callers should hint to check spelling/casing —
    Spanish field VALUES are accent- and case-sensitive.
    """
    base = f"https://{domain}/resource/{dataset_id}.json"

    def _page(page_limit, page_offset):
        return _get_json(_url(base, {
            "$select": select, "$where": where, "$group": group, "$order": order,
            "$having": having, "$q": q,
            "$limit": None if page_limit is None else str(page_limit),
            "$offset": None if page_offset is None else str(page_offset),
        }))

    if not paginate:
        rows = _page(limit, offset)
        if not isinstance(rows, list):
            raise SocrataError(f"Expected a list of rows, got: {str(rows)[:200]}")
        return rows

    rows, off, remaining = [], offset or 0, limit
    while True:
        want = SODA_PAGE_MAX if remaining is None else min(SODA_PAGE_MAX, remaining)
        if want <= 0:
            break
        batch = _page(want, off)
        if not isinstance(batch, list):
            raise SocrataError(f"Expected a list of rows, got: {str(batch)[:200]}")
        rows.extend(batch)
        if remaining is not None:
            remaining -= len(batch)
        if len(batch) < want:  # last page
            break
        off += len(batch)
    return rows


def count_rows(dataset_id, *, domain=DEFAULT_DOMAIN, where=None):
    """Exact row count via $select=count(*). One cheap call — does NOT pull the data."""
    res = query(dataset_id, domain=domain, select="count(*) as count", where=where)
    if res and isinstance(res, list):
        first = res[0]
        return int(first.get("count") or next(iter(first.values())))
    return 0


# --- Size sniff ---------------------------------------------------------------
def estimate_size(n_rows, n_cols):
    """Estimate in-memory size and decide whether to suggest polars / server-side
    aggregation. Returns a dict; see POLARS_SUGGEST_* thresholds above."""
    est_bytes = n_rows * max(n_cols, 1) * BYTES_PER_CELL_EST
    suggest = n_rows > POLARS_SUGGEST_ROWS or est_bytes > POLARS_SUGGEST_BYTES
    return {
        "rows": n_rows,
        "cols": n_cols,
        "est_bytes": est_bytes,
        "est_mb": round(est_bytes / 1024 / 1024, 1),
        "suggest_polars": suggest,
    }


def sniff(dataset_id, *, domain=DEFAULT_DOMAIN, where=None):
    """Combine count_rows + columns into a size estimate with a human-readable hint."""
    cols = columns(dataset_id, domain=domain)
    n_rows = count_rows(dataset_id, domain=domain, where=where)
    est = estimate_size(n_rows, len(cols))
    est["message"] = hint_message(est)
    return est


def hint_message(est):
    """Return a Spanish hint string when a dataset is large, else None."""
    if not est.get("suggest_polars"):
        return None
    return (
        f"⚠ El dataset tiene {est['rows']:,} filas (~{est['est_mb']} MB estimados). "
        "Es grande para pandas en un portátil. Opciones:\n"
        "  1) Agregar en el servidor con $select=...sum(...)...&$group=... "
        "(traes solo el resultado, no las filas crudas).\n"
        "  2) Usar polars para el procesamiento local.\n"
        f"No necesitas descargar todas las filas para una gráfica. "
        f"(Recuerda: una página SODA trae máximo {SODA_PAGE_MAX:,} filas; "
        "para más, se pagina con $offset.)"
    )
