"""
SolarSite-India Data Pipeline
Driver script that orchestrates Phase-1 data collection steps.
Run after setting up the virtual environment and GEE authentication.

Usage:
    python main.py --step all             # Run everything
    python main.py --step nasa            # Only NASA POWER
    python main.py --step srtm            # Only SRTM DEM
"""

import argparse
import logging
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.absolute()))

from config.settings import RAW_DIR

# ─── Logging ──────────────────────────────────────────────────
LOG_FILE = Path(__file__).parent / "pipeline.log"

logger = logging.getLogger("solar_pipeline_main")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    fh = logging.FileHandler(LOG_FILE, mode="a")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)


# ─── Step Handlers ────────────────────────────────────────────

def _run_step(step_name, import_path, function_name, centroids_csv, *extra_args):
    """Generic step runner with error handling."""
    try:
        logger.info("[%s] Starting collection …", step_name)
        module = __import__(import_path, fromlist=[function_name])
        func = getattr(module, function_name)
        outdir = str(RAW_DIR / step_name.replace("_", ""))
        try:
            func(centroids_csv, outdir, *extra_args)
        except TypeError:
            # ponytail: 1-arg collectors (census_cea.process) fall back here; breaks if a
            # 2-arg collector raises TypeError internally (double-run) — unify signatures then.
            func(outdir, *extra_args)
        logger.info("[%s] ✓ Complete.", step_name)
    except ImportError as exc:
        logger.warning("[%s] Module not available — skipping: %s", step_name, exc)
    except Exception as exc:
        logger.error("[%s] ✗ Failed: %s\n%s", step_name, exc, traceback.format_exc())


def main():
    parser = argparse.ArgumentParser(description="SolarSite-India Data Pipeline")
    parser.add_argument(
        "--step",
        choices=["nasa", "srtm", "worldcover", "modis", "osm", "census", "aef", "all"],
        default="all",
        help="Which collection step to run (default: all)",
    )
    parser.add_argument(
        "--centroids",
        default=str(RAW_DIR / "shapefiles" / "telangana_ap_districts_centroids_final.csv"),
        help="Path to district centroids CSV",
    )
    args = parser.parse_args()

    centroids_csv = args.centroids

    logger.info("=" * 60)
    logger.info("SolarSite-India Data Pipeline — Phase 1 Collection")
    logger.info("Centroids: %s", centroids_csv)
    logger.info("Step: %s", args.step)
    logger.info("=" * 60)

    # Validate centroids file exists before proceeding
    if not Path(centroids_csv).exists():
        logger.critical("Centroids file not found: %s", centroids_csv)
        logger.critical("Run Phase 0 (boundary extraction) first.")
        sys.exit(1)

    steps = []

    if args.step in ("nasa", "all"):
        steps.append(("nasa", "datasources.nasa_power_v2", "collect_nasa_power"))

    if args.step in ("srtm", "all"):
        steps.append(("srtm", "datasources.gee_srtm", "collect_srtm"))

    if args.step in ("worldcover", "all"):
        steps.append(("worldcover", "datasources.gee_worldcover", "collect_worldcover"))

    if args.step in ("modis", "all"):
        steps.append(("modis", "datasources.gee_modis", "collect_modis_aod"))

    if args.step in ("osm", "all"):
        steps.append(("osm", "datasources.osm_proximity", "collect_osm_proximity"))

    if args.step in ("census", "all"):
        steps.append(("census", "datasources.census_cea", "process"))

    if args.step in ("aef", "all"):
        steps.append(("aef", "datasources.gee_alphaearth", "collect_alphaearth"))

    for step_name, module_path, func_name in steps:
        _run_step(step_name, module_path, func_name, centroids_csv)

    logger.info("=" * 60)
    logger.info("Phase 1 collection complete.")
    logger.info("Next: Run Phase 2+3 → python phase2_3_pipeline.py --step all")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()