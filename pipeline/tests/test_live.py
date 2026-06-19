"""Opt-in test that hits the real datos.gov.co API.

Skipped in normal runs / CI. Run it on purpose with:  pytest -m live
"""
import pytest

import socrata


@pytest.mark.live
def test_live_query_returns_rows():
    rows = socrata.query(
        "n48w-gutb",
        select="anno,sum(no_de_accesos::number) as accesos",
        group="anno",
        order="anno",
        limit=3,
    )
    assert rows
    assert {"anno", "accesos"} <= set(rows[0])
