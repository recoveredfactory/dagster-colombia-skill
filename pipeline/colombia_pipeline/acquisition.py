"""
acquisition.py — the pipeline's bridge to the SKILL's acquisition code.

One source of truth: instead of duplicating any HTTP code, we import the exact
stdlib module the Claude Skill uses (`skill/colombia-open-data/scripts/socrata.py`)
by putting its folder on sys.path. If you fix a bug in the skill's fetch code, the
pipeline gets it too.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SKILL_SCRIPTS = (
    Path(__file__).resolve().parents[2]
    / "skill" / "colombia-open-data" / "scripts"
)
if str(_SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SKILL_SCRIPTS))

# Re-export the pieces the assets use. (Imported after the sys.path insert.)
import socrata  # noqa: E402

query = socrata.query
columns = socrata.columns
count_rows = socrata.count_rows
sniff = socrata.sniff
estimate_size = socrata.estimate_size
SocrataError = socrata.SocrataError

__all__ = ["query", "columns", "count_rows", "sniff", "estimate_size", "SocrataError"]
