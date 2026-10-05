#!/usr/bin/env python3
"""
SolarSite-India — Unified ML Training Entrypoint.
Consolidates train_ensemble.py + main.py. Fixes test-set leakage and
collinear feature drops. Supports real CUF targets.

Usage:
    python -m src.cli.train --models ridge,lasso --feature-selection rfe --n-features 12
    python -m src.cli.train --hpo --hpo-trials 30
    python -m src.cli.train --models ridge --use-real-cuf
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
from src.ml.evaluation import generate_report, plot_feature_importance, plot_model_comparison

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
    parser.add_argument("--use-real-cuf", action="store_true",
                        help="Use real plant CUF data as target")
    args = parser.parse_args()

    config = Config()
    config.trainer.random_state = args.seed
    config.trainer.feature_selection_method = args.feature_selection
    config.trainer.n_features_to_select = args.n_features
    if args.use_real_cuf:
        config.data.cuf_source_filter = "cea_plant"
    setup_logging(config.logs_dir)

    logger.info("=" * 60)
    logger.info("SolarSite-India ML Training")
    logger.info(f"Models: {args.models}")
    if args.use_real_cuf:
        logger.info("Target: Real plant CUF from CEA data")
    logger.info("=" * 60)

    dl = SolarDataLoader(config.data)
    X_train, y_train, X_test, y_test, feature_names = dl.load()
    X_train_scaled, X_test_scaled = dl.fit_transform(X_train, X_test)
    # Persist the ONE scaler inference must reuse (kills train/serve skew).
    dl.save_preprocessor(str(config.models_dir / "preprocessor.joblib"))

    logger.info(f"Train: {X_train_scaled.shape[0]} rows × {X_train_scaled.shape[1]} features")
    logger.info(f"Test:  {X_test_scaled.shape[0]} rows")
    logger.info(f"Target range: [{y_train.min():.4f}, {y_train.max():.4f}]")

    X_train_df = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
    X_test_df = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)

    trainer = Trainer(config)
    results = []

    for model_name in args.models:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Training: {model_name.upper()}")
        logger.info(f"{'=' * 60}")
        try:
            res, model = trainer.train(
                X_train_df, y_train, X_test_df, y_test, feature_names,
                model_name=model_name,
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

    if args.hpo:
        logger.info(f"\n{'=' * 60}")
        logger.info("HYPERPARAMETER OPTIMIZATION (CV on train only)")
        logger.info(f"{'=' * 60}")
        from src.ml.optimization import optimize_hyperparameters

        for model_name in args.models:
            try:
                hpo_result = optimize_hyperparameters(
                    model_name,
                    X_train_scaled,
                    y_train.values,
                    X_test_scaled,
                    y_test.values,
                    config,
                    n_trials=args.hpo_trials,
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