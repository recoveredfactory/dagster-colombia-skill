"""Pruebas de la plantilla: lógica pura (sin red) + un smoke test con cassette."""
import pandas as pd
import pytest

import etl  # contrib/_template/etl.py (pytest agrega esta carpeta al sys.path)


def test_clean_casts_to_int():
    raw = pd.DataFrame([{"anno": "2022", "valor": "100"}, {"anno": "2023", "valor": "120"}])
    out = etl.clean(raw)
    assert out["valor"].dtype.kind == "i"
    assert out["valor"].tolist() == [100, 120]


@pytest.mark.vcr
def test_dataset_exists():
    # Respuesta real grabada en cassettes/ y reproducida sin red en CI.
    import socrata

    assert socrata.count_rows(etl.DATASET_ID, domain=etl.DOMAIN) > 0
