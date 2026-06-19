"""Tests for the stdlib Socrata client.

The HTTP tests are backed by vcrpy cassettes (recorded once from the real
datos.gov.co, then replayed offline). The rest are pure logic, no network.
"""
import pytest

import socrata

DATASET = "n48w-gutb"


# --- cassette-backed (real responses, replayed offline) ----------------------
@pytest.mark.vcr
def test_discover_finds_the_internet_dataset():
    results = socrata.discover("internet por departamento", limit=5)
    assert DATASET in [r["id"] for r in results]
    assert all({"id", "name", "description", "category"} <= set(r) for r in results)


@pytest.mark.vcr
def test_columns_are_all_text():
    cols = socrata.columns(DATASET)
    names = {c["field_name"] for c in cols}
    assert {"anno", "departamento", "no_de_accesos"} <= names
    # The teaching wart: numbers are stored as text, so they need casting.
    assert all(c["type"] == "text" for c in cols)


@pytest.mark.vcr
def test_query_by_year_returns_typed_aggregate():
    rows = socrata.query(
        DATASET,
        select="anno,sum(no_de_accesos::number) as accesos",
        group="anno",
        order="anno",
    )
    assert len(rows) >= 5
    assert {"anno", "accesos"} <= set(rows[0])


@pytest.mark.vcr
def test_count_rows_is_over_a_million():
    assert socrata.count_rows(DATASET) > 1_000_000


# --- pure logic (no network) -------------------------------------------------
def test_estimate_size_suggests_polars_when_big():
    est = socrata.estimate_size(2_000_000, 12)
    assert est["suggest_polars"] is True
    assert socrata.hint_message(est)  # non-empty Spanish hint


def test_estimate_size_quiet_when_small():
    est = socrata.estimate_size(300, 4)
    assert est["suggest_polars"] is False
    assert socrata.hint_message(est) is None


def test_url_keeps_soql_readable():
    url = socrata._url(
        "https://x/resource/abcd-1234.json",
        {"$select": "anno,sum(no_de_accesos::number) as accesos", "$group": "anno"},
    )
    assert "$select=anno,sum(no_de_accesos::number)" in url
    assert "$group=anno" in url
    assert "%24" not in url  # the $ stays literal


def test_url_drops_none_params():
    url = socrata._url("https://x/y.json", {"$select": "a", "$where": None})
    assert "$where" not in url
