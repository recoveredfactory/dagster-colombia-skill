"""
The asset graph:  raw_dataset -> clean_dataset -> dashboard_data

  raw_dataset    pulls a server-side aggregate from datos.gov.co into data/raw/
  clean_dataset  casts text->int, drops non-departments, tidies names, into data/clean/
  dashboard_data writes the small JSON the web app reads (web/public/data/)

`no_de_accesos` is a STOCK (subscribers at the end of each quarter), so we keep the
`trimestre` dimension and report a point-in-time snapshot — summing quarters/years would
inflate the figures (a correct sum of the wrong unit is still wrong).

Run all three with `dagster dev` and one click, or headless:
    dagster asset materialize --select '*' -m colombia_pipeline.definitions

The transform (`clean_frame`) and shaping (`build_dashboard`) are plain functions so
they can be unit-tested without Dagster or the network.
"""
import json

import pandas as pd
from dagster import AssetExecutionContext, MetadataValue, asset

from . import config
from .acquisition import count_rows, query

# Keep `trimestre`: we want quarterly snapshots, not a sum across quarters.
RAW_SELECT = "anno,trimestre,cod_departamento,departamento,sum({col}::number) as accesos"
RAW_GROUP = "anno,trimestre,cod_departamento,departamento"


def _write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)


def clean_frame(raw: pd.DataFrame) -> pd.DataFrame:
    """Pure transform: text->int, drop non-department rows, tidy names."""
    df = raw.copy()

    # Real data is messy: the source mixes in national-total rows (departamento
    # "COLOMBIA") and rows with no department code. Drop anything that isn't a real
    # department so the ranking + map join stay clean.
    df = df[df["cod_departamento"].notna()]
    df = df[df["departamento"].str.upper() != "COLOMBIA"]

    # Everything arrives as text from Socrata — cast the numbers.
    df["anno"] = pd.to_numeric(df["anno"]).astype(int)
    df["trimestre"] = pd.to_numeric(df["trimestre"]).astype(int)
    df["accesos"] = pd.to_numeric(df["accesos"]).astype(int)
    # DIVIPOLA department code: keep as a zero-padded 2-char string (e.g. "05").
    df["cod_departamento"] = df["cod_departamento"].astype(str).str.zfill(2)
    df = df[df["cod_departamento"].str.fullmatch(r"\d{2}")]
    # "BOGOTÁ D.C." -> "Bogotá D.C." (nicer for display; keeps accents).
    df["departamento"] = df["departamento"].str.title()

    return df.sort_values(
        ["anno", "trimestre", "accesos"], ascending=[True, True, False]
    ).reset_index(drop=True)


def build_dashboard(clean: pd.DataFrame) -> dict:
    """Pure shaping: a point-in-time snapshot, not a cumulative sum."""
    # The latest reported quarter overall = the department snapshot ("subscribers now").
    latest_anno = int(clean["anno"].max())
    latest_tri = int(clean.loc[clean["anno"] == latest_anno, "trimestre"].max())
    snapshot = clean[(clean["anno"] == latest_anno) & (clean["trimestre"] == latest_tri)]

    by_dep = (
        snapshot.groupby(["cod_departamento", "departamento"], as_index=False)["accesos"]
        .sum()
        .sort_values("accesos", ascending=False)
    )
    by_dep_records = [
        {
            "cod_departamento": r.cod_departamento,
            "departamento": r.departamento,
            "accesos": int(r.accesos),
        }
        for r in by_dep.itertuples()
    ]

    # Yearly trend = subscriber level at each year's LAST reported quarter (a real
    # stock trend). The most recent year may be partial (its last quarter so far).
    year_end_tri = clean.groupby("anno")["trimestre"].transform("max")
    year_end = clean[clean["trimestre"] == year_end_tri]
    by_year = year_end.groupby("anno", as_index=False)["accesos"].sum().sort_values("anno")
    by_year_records = [
        {"anno": int(r.anno), "accesos": int(r.accesos)} for r in by_year.itertuples()
    ]

    meta = {
        "dataset_id": config.DATASET_ID,
        "dataset_name": config.DATASET_NAME,
        "source_url": config.SOURCE_URL,
        "domain": config.DOMAIN,
        "period": f"{int(clean['anno'].min())}–{latest_anno}",
        "latest_period": f"{latest_anno}-T{latest_tri}",
        "total_accesos": int(by_dep["accesos"].sum()),
        "metric": "Suscriptores de Internet fijo (stock) al último trimestre reportado.",
        "note": (
            "Foto de stock, no acumulado. La tendencia anual usa el último trimestre de "
            "cada año; el año más reciente puede ser parcial."
        ),
    }
    return {"by_year": by_year_records, "by_department": by_dep_records, "meta": meta}


@asset(description="Server-side aggregate pulled from datos.gov.co (raw, all text, per quarter).")
def raw_dataset(context: AssetExecutionContext) -> pd.DataFrame:
    # Sniff first: this dataset has ~2.8M rows. We DON'T download them — we ask the
    # server to aggregate to (year, quarter, department) and return only ~1k rows.
    n_source = count_rows(config.DATASET_ID, domain=config.DOMAIN)
    if n_source > config.POLARS_SUGGEST_ROWS:
        context.log.warning(
            f"Origen: {n_source:,} filas. Agregamos en el servidor con "
            f"$group — no se descargan las filas crudas (pandas sufriría)."
        )

    rows = query(
        config.DATASET_ID,
        domain=config.DOMAIN,
        select=RAW_SELECT.format(col=config.VALUE_COL),
        group=RAW_GROUP,
        order="anno,trimestre",
    )
    df = pd.DataFrame(rows)

    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.RAW_DIR / "internet_raw.csv", index=False)

    context.add_output_metadata({
        "source_rows": MetadataValue.int(n_source),
        "aggregated_rows": MetadataValue.int(len(df)),
        "columns": MetadataValue.text(", ".join(df.columns)),
        "preview": MetadataValue.md("```\n" + df.head().to_string(index=False) + "\n```"),
    })
    return df


@asset(description="Typed + tidied: text->int, real departments only, into data/clean/.")
def clean_dataset(context: AssetExecutionContext, raw_dataset: pd.DataFrame) -> pd.DataFrame:
    df = clean_frame(raw_dataset)

    config.CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.CLEAN_DIR / "internet_clean.csv", index=False)

    context.add_output_metadata({
        "rows": MetadataValue.int(len(df)),
        "years": MetadataValue.text(f"{df['anno'].min()}–{df['anno'].max()}"),
        "departments": MetadataValue.int(df["cod_departamento"].nunique()),
    })
    return df


@asset(description="Small JSON the web app reads: by_year, by_department, meta.")
def dashboard_data(context: AssetExecutionContext, clean_dataset: pd.DataFrame) -> dict:
    dash = build_dashboard(clean_dataset)

    _write_json(config.WEB_DATA_DIR / "by_year.json", dash["by_year"])
    _write_json(config.WEB_DATA_DIR / "by_department.json", dash["by_department"])
    _write_json(config.WEB_DATA_DIR / "meta.json", dash["meta"])

    context.add_output_metadata({
        "years": MetadataValue.int(len(dash["by_year"])),
        "departments": MetadataValue.int(len(dash["by_department"])),
        "latest_period": MetadataValue.text(dash["meta"]["latest_period"]),
        "total_accesos": MetadataValue.int(dash["meta"]["total_accesos"]),
        "wrote": MetadataValue.text("web/public/data/{by_year,by_department,meta}.json"),
    })
    return dash
