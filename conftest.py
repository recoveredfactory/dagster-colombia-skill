"""Repo-wide pytest setup: put the skill's stdlib scripts on the path + VCR config.

Loaded for both pipeline/tests and contrib/ (rootdir is the repo root). The skill's
socrata.py / dane.py live outside any installed package, so tests import them by path.
"""
import sys
from pathlib import Path

import pytest

SKILL_SCRIPTS = (
    Path(__file__).resolve().parent / ".claude" / "skills" / "colombia-open-data" / "scripts"
)
sys.path.insert(0, str(SKILL_SCRIPTS))


@pytest.fixture(scope="module")
def vcr_config():
    # Don't bake any app token into committed cassettes; record once, then replay.
    return {
        "filter_headers": ["x-app-token", "authorization"],
        "record_mode": "once",
    }
