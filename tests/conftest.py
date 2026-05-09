"""Pytest configuration: ensure solarpipeline is importable."""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1] / "backend" / "data_pipeline"
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
