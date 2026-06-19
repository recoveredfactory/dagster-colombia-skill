"""Pipeline transform + offline Dagster materialization (no network)."""
import json

import pandas as pd
import pytest
from dagster import materialize

from colombia_pipeline import assets, config

# Raw-shaped fixture (as Socrata returns it: everything is text; includes a
# national-total "COLOMBIA" row and a null-code row that cleaning must drop).
FIXTURE = [
    {"anno": "2021", "cod_departamento": "11", "departamento": "BOGOTÁ D.C.", "accesos": "100"},
    {"anno": "2021", "cod_departamento": "05", "departamento": "ANTIOQUIA", "accesos": "50"},
    {"anno": "2022", "cod_departamento": "11", "departamento": "BOGOTÁ D.C.", "accesos": "120"},
    {"anno": "2022", "cod_departamento": "05", "departamento": "ANTIOQUIA", "accesos": "70"},
    {"anno": "2021", "cod_departamento": None, "departamento": "COLOMBIA", "accesos": "150"},
]


def test_clean_frame_casts_and_drops_non_departments():
    df = assets.clean_frame(pd.DataFrame(FIXTURE))
    assert df["anno"].dtype.kind == "i"
    assert df["accesos"].dtype.kind == "i"
    assert "COLOMBIA" not in set(df["departamento"].str.upper())
    assert set(df["cod_departamento"]) == {"11", "05"}
    assert "Bogotá D.C." in set(df["departamento"])  # title-cased, accent kept


def test_build_dashboard_shapes_and_sorts():
    dash = assets.build_dashboard(assets.clean_frame(pd.DataFrame(FIXTURE)))
    assert {"by_year", "by_department", "meta"} <= set(dash)
    accs = [r["accesos"] for r in dash["by_department"]]
    assert accs == sorted(accs, reverse=True)  # ranked desc
    assert all(r["cod_departamento"].isdigit() for r in dash["by_department"])
    assert dash["meta"]["dataset_id"] == config.DATASET_ID


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
    assert (tmp_path / "web" / "by_year.json").exists()
    assert (tmp_path / "web" / "meta.json").exists()


def test_definitions_import():
    from colombia_pipeline.definitions import defs
    assert defs is not None
