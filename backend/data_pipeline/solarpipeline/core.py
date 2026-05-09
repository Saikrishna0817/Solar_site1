"""Pipeline orchestrator.  Ties data loading, feature engineering, EDA, and preprocessing."""

import argparse
import sys
import time

import pandas as pd
import yaml

from solarpipeline.utils import (
    PROCESSED_DIR, get_logger, CONFIG,
)
from solarpipeline.data import merge_sources
from solarpipeline.features import engineer_features
from solarpipeline.eda import run_eda
from solarpipeline.preprocess import preprocess

logger = get_logger("solar_pipeline_main")


def _export_pipeline_metadata(config: dict, timestamp: str) -> None:
    """Write reproducibility metadata to PROCESSED_DIR."""
    meta = {
        "run_timestamp": timestamp,
        **config,
    }
    path = PROCESSED_DIR / "pipeline_metadata.yaml"
    try:
        with open(path, "w") as fh:
            yaml.dump(meta, fh, default_flow_style=False, sort_keys=False)
        logger.info("Saved: pipeline_metadata.yaml")
    except Exception as exc:
        logger.warning("Could not save pipeline_metadata.yaml: %s", exc)


def run_pipeline(step: str = "all", export_metadata: bool = True) -> None:
    """Execute the configured pipeline step.

    Parameters
    ----------
    step : str, optional
        One of ``"merge"``, ``"eda"``, ``"preprocess"``, ``"all"`` (default).
    export_metadata : bool, optional
        If True, write ``pipeline_metadata.yaml`` after the run.
    """
    start_ts = time.strftime("%Y%m%d_%H%M%S")
    logger.info("SolarSite-India Data Pipeline (Stage 2 - Refactored) -- step=%s", step)

    df = None
    metadata: dict = {"step": step, "config": CONFIG.__dict__.copy()}

    if step in ("merge", "all"):
        df = merge_sources()
        if df is None:
            logger.critical("Merge failed -- aborting pipeline.")
            sys.exit(1)
        df.to_csv(str(PROCESSED_DIR / "master_dataset_clean.csv"), index=False)
        logger.info("Saved: master_dataset_clean.csv")
        metadata["merge_shape"] = df.shape
    else:
        df = pd.read_csv(str(PROCESSED_DIR / "master_dataset_clean.csv"))

    if step in ("eda", "all"):
        if df is None:
            df = pd.read_csv(str(PROCESSED_DIR / "master_dataset_clean.csv"))
        df = engineer_features(df)
        run_eda(df)
        df.to_csv(str(PROCESSED_DIR / "master_dataset_engineered.csv"), index=False)
        logger.info("Saved: master_dataset_engineered.csv")
        metadata["engineered_shape"] = df.shape

    if step in ("preprocess", "all"):
        if df is None:
            df = pd.read_csv(str(PROCESSED_DIR / "master_dataset_engineered.csv"))
        result = preprocess(df)
        if result[0] is None:
            logger.critical("Preprocessing failed.")
        metadata["preprocess_output"] = "success" if result[0] is not None else "failed"

    if export_metadata:
        _export_pipeline_metadata(metadata, start_ts)

    logger.info("Pipeline complete. Outputs in %s", PROCESSED_DIR)


def main() -> None:
    """CLI entry point.  Parses ``--step`` and calls ``run_pipeline``."""
    parser = argparse.ArgumentParser(description="SolarSite-India Pipeline v2")
    parser.add_argument("--step", choices=["merge", "eda", "preprocess", "all"],
                        default="all")
    args = parser.parse_args()
    run_pipeline(step=args.step)


if __name__ == "__main__":
    main()
