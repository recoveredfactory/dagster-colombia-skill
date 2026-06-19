"""Pipeline transform + offline Dagster materialization (no network)."""
import json

import pandas as pd
import pytest
from dagster import materialize

from colombia_pipeline import assets, config

# Raw-shaped fixture (as Socrata returns it: everything is text; per quarter; includes a
# national-total "COLOMBIA" row and a null-code row that cleaning must drop).
FIXTURE = [
    {"anno": "2021", "trimestre": "1", "cod_departamento": "11", "departamento": "BOGOTÁ D.C.", "accesos": "90"},
    {"anno": "2021", "trimestre": "2", "cod_departamento": "11", "departamento": "BOGOTÁ D.C.", "accesos": "100"},
    {"anno": "2021", "trimestre": "2", "cod_departamento": "05", "departamento": "ANTIOQUIA", "accesos": "50"},
    {"anno": "2022", "trimestre": "3", "cod_departamento": "11", "departamento": "BOGOTÁ D.C.", "accesos": "110"},
    {"anno": "2022", "trimestre": "4", "cod_departamento": "11", "departamento": "BOGOTÁ D.C.", "accesos": "120"},
    {"anno": "2022", "trimestre": "4", "cod_departamento": "05", "departamento": "ANTIOQUIA", "accesos": "70"},
    {"anno": "2022", "trimestre": "4", "cod_departamento": None, "departamento": "COLOMBIA", "accesos": "190"},
]


def test_clean_frame_casts_and_drops_non_departments():
    df = assets.clean_frame(pd.DataFrame(FIXTURE))
    assert df["anno"].dtype.kind == "i"
    assert df["trimestre"].dtype.kind == "i"
    assert df["accesos"].dtype.kind == "i"
    assert "COLOMBIA" not in set(df["departamento"].str.upper())
    assert set(df["cod_departamento"]) == {"11", "05"}
    assert "Bogotá D.C." in set(df["departamento"])  # title-cased, accent kept


def test_by_department_is_latest_quarter_snapshot_not_a_sum():
    dash = assets.build_dashboard(assets.clean_frame(pd.DataFrame(FIXTURE)))
    # Latest period is 2022-T4; snapshot values are NOT summed across quarters/years.
    assert dash["meta"]["latest_period"] == "2022-T4"
    by_dep = {r["departamento"]: r["accesos"] for r in dash["by_department"]}
    assert by_dep == {"Bogotá D.C.": 120, "Antioquia": 70}
    # ranked desc + total = sum of the snapshot only (not 90+100+110+120+...)
    assert [r["accesos"] for r in dash["by_department"]] == [120, 70]
    assert dash["meta"]["total_accesos"] == 190


def test_by_year_uses_each_years_last_quarter():
    dash = assets.build_dashboard(assets.clean_frame(pd.DataFrame(FIXTURE)))
    by_year = {r["anno"]: r["accesos"] for r in dash["by_year"]}
    # 2021 last quarter = T2 -> 100 (Bogotá) + 50 (Antioquia) = 150
    # 2022 last quarter = T4 -> 120 + 70 = 190  (COLOMBIA row dropped)
    assert by_year == {2021: 150, 2022: 190}


def test_materialize_offline(tmp_path, monkeypatch):
    # Feed the raw asset from the fixture instead of the network, and redirect all
    # outputs into tmp so we don't clobber the committed web/public/data snapshot.
    monkeypatch.setattr(assets, "query", lambda *a, **k: FIXTURE)
    monkeypatch.setattr(assets, "count_rows", lambda *a, **k: 2_795_052)
    monkeypatch.setattr(config, "RAW_DIR", tmp_path / "raw")
    monkeypatch.setattr(config, "CLEAN_DIR", tmp_path / "clean")
    monkeypatch.setattr(config, "WEB_DATA_DIR", tmp_path / "web")

    result = materialize([assets.raw_dataset, assets.clean_dataset, assets.dashboard_data])
    assert result.success

    by_dep = json.loads((tmp_path / "web" / "by_department.json").read_text(encoding="utf-8"))
    assert by_dep and all(r["cod_departamento"].isdigit() for r in by_dep)
    assert by_dep[0]["accesos"] == 120  # snapshot, not a sum
    meta = json.loads((tmp_path / "web" / "meta.json").read_text(encoding="utf-8"))
    assert meta["latest_period"] == "2022-T4"
    assert (tmp_path / "web" / "by_year.json").exists()


def test_definitions_import():
    from colombia_pipeline.definitions import defs
    assert defs is not None
