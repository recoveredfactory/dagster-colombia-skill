"""
Plantilla de pipeline para datos.gov.co.

Copia esta carpeta a  contrib/<tu-nombre>/ , cambia DATASET_ID y la lógica de
limpieza, y abre un Pull Request. Reutiliza el MISMO cliente del skill (socrata.py),
así que no copies código HTTP.

Correr en local (desde la raíz del repo):
    uv run --project pipeline dagster dev -f contrib/_template/etl.py
Probar:
    uv run --project pipeline pytest contrib/_template -m "not live"
"""
import json
import sys
from pathlib import Path

import pandas as pd
from dagster import AssetExecutionContext, Definitions, MetadataValue, asset

# Reutiliza el cliente stdlib del skill (una sola fuente de verdad).
_SKILL = Path(__file__).resolve().parents[2] / "skill" / "colombia-open-data" / "scripts"
if str(_SKILL) not in sys.path:
    sys.path.insert(0, str(_SKILL))
import socrata  # noqa: E402

# --- 1) CONFIG: cambia esto por tu dataset -----------------------------------
DOMAIN = "www.datos.gov.co"
DATASET_ID = "n48w-gutb"  # TODO: pon aquí el 4x4 de TU dataset
OUT_DIR = Path(__file__).resolve().parent / "data"


# --- 2) LIMPIEZA: función pura y fácil de probar -----------------------------
def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    # TODO: ajusta a tus columnas. Recuerda: en Socrata casi todo llega como texto.
    df["valor"] = pd.to_numeric(df["valor"]).astype(int)
    return df


# --- 3) ASSETS: raw -> clean -> dashboard ------------------------------------
@asset
def raw(context: AssetExecutionContext) -> pd.DataFrame:
    rows = socrata.query(
        DATASET_ID,
        domain=DOMAIN,
        # TODO: tu consulta SoQL. Agrega en el servidor si el dataset es grande.
        select="anno,sum(no_de_accesos::number) as valor",
        group="anno",
        order="anno",
    )
    return pd.DataFrame(rows)


@asset
def clean_data(context: AssetExecutionContext, raw: pd.DataFrame) -> pd.DataFrame:
    return clean(raw)


@asset
def dashboard(context: AssetExecutionContext, clean_data: pd.DataFrame) -> dict:
    records = clean_data.to_dict("records")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "dashboard.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    context.add_output_metadata({"rows": MetadataValue.int(len(records))})
    return {"records": records}


defs = Definitions(assets=[raw, clean_data, dashboard])
