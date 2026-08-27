"""Pytest configuration: ensure solarpipeline is importable and protect pipeline outputs."""

import shutil
import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[1] / "backend" / "data_pipeline"
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# ── Protect pipeline outputs ───────────────────────────────────────
# The preprocess() function writes directly to PROCESSED_DIR.
# We save and restore the real processed files so tests don't
# overwrite production data.

_PROCESSED = _root / "outputs" / "processed"
_FILES_TO_PROTECT = [
    "features_train.csv",
    "features_test.csv",
    "labels_train.csv",
    "labels_test.csv",
]


def _backup():
    backups = {}
    for f in _FILES_TO_PROTECT:
        src = _PROCESSED / f"{f}"
        if src.exists():
            backups[f] = src.read_text()
    return backups


def _restore(backups):
    for f, content in backups.items():
        dst = _PROCESSED / f"{f}"
        dst.write_text(content)


@pytest.fixture(autouse=True, scope="session")
def protect_pipeline_data():
    backups = _backup()
    yield
    _restore(backups)
