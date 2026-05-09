"""
SolarSite-India Pipeline Entry Point (Stage 2, Refactored).

Usage
-----
    python phase2_3_pipeline.py [--step {merge,eda,preprocess,all}]

This is a thin wrapper around the `solarpipeline` package.
For programmatic use, import and call the modules directly:

    from solarpipeline import merge_sources, engineer_features, run_eda, preprocess
"""

import sys
from pathlib import Path

# Ensure the parent of data_pipeline is on sys.path so solarpipeline resolves
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from solarpipeline.core import main  # noqa: E402

if __name__ == "__main__":
    main()