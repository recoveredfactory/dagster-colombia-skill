"""Dagster entry point: `dagster dev` (or the CLI) loads this module."""
from dagster import Definitions, load_assets_from_modules

from . import assets

defs = Definitions(assets=load_assets_from_modules([assets]))
