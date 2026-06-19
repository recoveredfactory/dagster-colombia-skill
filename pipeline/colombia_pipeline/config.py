"""Pipeline configuration — one place a student edits to point at another dataset."""
from pathlib import Path

# --- the ONE dataset this demo is wired to (swap the id to use another) -------
# Verified live: n48w-gutb = "Internet Fijo: Accesos por tecnología y segmento"
# (MinTIC). Department-level, historical 2016–2023, with DIVIPOLA codes.
DOMAIN = "www.datos.gov.co"
DATASET_ID = "n48w-gutb"
DATASET_NAME = "Internet Fijo: Accesos por tecnología y segmento"
SOURCE_URL = f"https://{DOMAIN}/d/{DATASET_ID}"

# Column holding the numeric value (stored as text in this dataset → we cast it).
VALUE_COL = "no_de_accesos"

# Above this row count, warn that pandas will hurt — aggregate server-side / polars.
POLARS_SUGGEST_ROWS = 1_000_000

# --- filesystem layout (relative to repo root) -------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "data" / "raw"
CLEAN_DIR = REPO_ROOT / "data" / "clean"
WEB_DATA_DIR = REPO_ROOT / "web" / "public" / "data"
