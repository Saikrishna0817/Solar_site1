#!/usr/bin/env python3
"""
SolarSite-India — Unified ML Training Entrypoint.
Canonical entrypoint (the root main.py / train_ensemble.py wrappers are deleted).
Fixes test-set leakage and collinear feature drops. Supports real CUF targets.

Usage:
    python -m src.cli.train --models ridge lasso --feature-selection rfe --n-features 8
    python -m src.cli.train --hpo --hpo-trials 30
    python -m src.cli.train --unit district --cuf-source all    # ablation only
"""
import argparse
import logging
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.ml.config import Config
from src.ml.data_loader import SolarDataLoader
from src.ml.trainer import Trainer
from src.ml.models import get_model
from src.ml.evaluation import generate_report, plot_feature_importance, plot_model_comparison, write_metrics

logger = logging.getLogger("solar_train")


def setup_logging(log_dir):
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
    fh = logging.FileHandler(log_dir / "training.log")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler, fh]


def main():
    parser = argparse.ArgumentParser(description="SolarSite-India ML Training (Consolidated)")
    parser.add_argument("--models", nargs="+", default=["ridge", "lasso"],
                        help="Models: ridge, lasso, elastic_net, random_forest, xgboost, voting "
                             "(paper order ridge-first, voting before stacking; defaults stay cheap)")
    parser.add_argument("--feature-selection", default="rfe",
                        choices=["none", "rfe", "lasso"])
    parser.add_argument("--n-features", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--hpo", action="store_true",
                        help="Run HPO (CV on train only, no test leakage)")
    parser.add_argument("--hpo-trials", type=int, default=30)
    parser.add_argument("--unit", default="plant", choices=["plant", "district"],
                        help="Unit of analysis (default: plant-level CEA labels)")
    parser.add_argument("--cuf-source", default="cea_plant", dest="cuf_source",
                        choices=["cea_plant", "all"],
                        help="Label provenance. cea_plant (default) = CEA actual only; "
                             "all adds physics-derived labels for ablation, never for reporting")
    args = parser.parse_args()

    config = Config()
    config.trainer.random_state = args.seed
    config.trainer.feature_selection_method = args.feature_selection
    config.trainer.n_features_to_select = args.n_features
    config.data.unit = args.unit
    config.data.cuf_source_filter = args.cuf_source
    setup_logging(config.logs_dir)

    logger.info("=" * 60)
    logger.info("SolarSite-India ML Training")
    logger.info(f"Models: {args.models}")
    logger.info(f"Unit: {args.unit} | Labels: {args.cuf_source}")
    logger.info("=" * 60)

    dl = SolarDataLoader(config.data)
    X_train, y_train, X_test, y_test, feature_names = dl.load()
    # District per row — the trainer holds whole districts out together.
    groups = dl.train_groups

    logger.info(f"Train: {X_train.shape[0]} rows × {X_train.shape[1]} features")
    logger.info(f"Test:  {X_test.shape[0]} rows")
    logger.info(f"Target range: [{y_train.min():.4f}, {y_train.max():.4f}]")

    trainer = Trainer(config)
    results = []

    for model_name in args.models:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Training: {model_name.upper()}")
        logger.info(f"{'=' * 60}")
        try:
            res, model = trainer.train(
                X_train, y_train, X_test, y_test, feature_names,
                model_name=model_name, groups=groups,
            )
            results.append(res)
            logger.info(f"[{model_name}] Train R²={res['train_r2']:.4f} | Test R²={res['test_r2']:.4f} | CV R²={res.get('cv_r2_mean', 0):.4f}±{res.get('cv_r2_std', 0):.4f}")

            if res.get("feature_importances") is not None:
                plot_feature_importance(
                    res["feature_importances"],
                    save_path=config.reports_dir / "figures" / f"{model_name}_importance.png",
                )
        except Exception as e:
            logger.error(f"[{model_name}] Failed: {e}", exc_info=True)

    if len(results) > 1:
        plot_model_comparison(
            pd.DataFrame(results),
            save_path=config.reports_dir / "figures" / "model_comparison.png",
        )

    generate_report(results, save_path=config.reports_dir / "ml_report.md")

    # Machine-readable metrics for the API serving gate (src/api/services/gate.py).
    write_metrics(results, config.models_dir / "metrics.json", extra={
        "n_features": len(feature_names),
        "n_train_rows": int(len(y_train)),
        "unit": config.data.unit,
        "cuf_source": config.data.cuf_source_filter,
        "evaluation_method": "leave-one-district-out CV (pooled out-of-fold)",
        "generated_at": pd.Timestamp.utcnow().isoformat(timespec="seconds"),
    })

    if args.hpo:
        logger.info(f"\n{'=' * 60}")
        logger.info("HYPERPARAMETER OPTIMIZATION (CV on train only)")
        logger.info(f"{'=' * 60}")
        from src.ml.optimization import optimize_hyperparameters

        # ponytail: best params are REPORTED, not written back into the saved model —
        # serving still uses Trainer's defaults. Upgrade path: apply study.best_params
        # to config.model and retrain before the API loads the artifact.
        for model_name in args.models:
            try:
                hpo_result = optimize_hyperparameters(
                    model_name,
                    X_train.values,
                    y_train.values,
                    X_test.values,
                    y_test.values,
                    config,
                    n_trials=args.hpo_trials,
                    groups=groups,
                )
                cv_score = hpo_result.get("best_cv_score", 0)
                test_score = hpo_result.get("test_r2", 0)
                logger.info(
                    f"[{model_name}] CV R²={cv_score:.4f} | Test R²={test_score:.4f} | "
                    f"Params: {hpo_result['best_params']}"
                )
            except Exception as e:
                logger.error(f"[{model_name}] HPO failed: {e}")

    logger.info(f"\n{'=' * 60}")
    logger.info("TRAINING COMPLETE")
    logger.info(f"Reports:  {config.reports_dir}")
    logger.info(f"Models:   {config.models_dir}")
    logger.info(f"Logs:     {config.logs_dir}")
    logger.info(f"{'=' * 60}")


if __name__ == "__main__":
    main()