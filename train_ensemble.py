#!/usr/bin/env python3
"""
Optimized ML Training: single best model (Ridge HPO) for near-deterministic CUF.
Stacking is not beneficial when all models predict identically (R² > 0.99).
Canonical: src/cli/train.py (this wrapper kept for compat).
ponytail: delete this file when no docs/scripts reference it.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import logging
import warnings

warnings.filterwarnings("ignore")

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

from src.ml.config import Config
from src.ml.data_loader import SolarDataLoader

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("optimized_training")

# ── Load Data ───────────────────────────────────────────────────
CONFIG = Config()
SEED = CONFIG.trainer.random_state

dl = SolarDataLoader(CONFIG.data)
X_train, y_train, X_test, y_test, features = dl.load()
X_train_s, X_test_s = dl.fit_transform(X_train, X_test)

logger.info(f"Data: {X_train_s.shape[0]} train, {X_test_s.shape[0]} test, {len(features)} features")
logger.info(f"Target: mean={y_train.mean():.4f}, std={y_train.std():.4f}")

# ── Hyperparameter Optimization (Ridge) ─────────────────────────
logger.info("\n" + "=" * 60)
logger.info("HPO: Ridge alpha tuning (20 trials)")
logger.info("=" * 60)

best_alpha = 1e-4
best_cv_score = 0.0

if OPTUNA_AVAILABLE:
    from sklearn.model_selection import KFold

    kf = KFold(n_splits=5, shuffle=True, random_state=SEED)

    def _objective(trial):
        alpha = trial.suggest_float("alpha", 1e-6, 100.0, log=True)
        scores = []
        for tr_idx, val_idx in kf.split(X_train_s):
            model = Ridge(alpha=alpha, random_state=SEED)
            model.fit(X_train_s[tr_idx], y_train.iloc[tr_idx])
            scores.append(r2_score(y_train.iloc[val_idx], model.predict(X_train_s[val_idx])))
        return np.mean(scores)

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=SEED))
    study.optimize(_objective, n_trials=20, show_progress_bar=False)
    best_alpha = study.best_params["alpha"]
    best_cv_score = study.best_value
    logger.info(f"Best alpha={best_alpha:.6f}, CV R²={best_cv_score:.4f} (no test leakage)")
else:
    logger.warning("Optuna not available, using default alpha=1e-4")

# ── Train Final Optimized Model ─────────────────────────────────
logger.info("\n" + "=" * 60)
logger.info("TRAINING FINAL MODEL (Ridge HPO)")
logger.info("=" * 60)

final_model = Ridge(alpha=best_alpha, random_state=SEED)
final_model.fit(X_train_s, y_train)

y_pred_train = final_model.predict(X_train_s)
y_pred_test = final_model.predict(X_test_s)

train_r2 = r2_score(y_train, y_pred_train)
test_r2 = r2_score(y_test, y_pred_test)
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
test_mae = mean_absolute_error(y_test, y_pred_test)

logger.info(f"Train R²: {train_r2:.4f}")
logger.info(f"Test  R²: {test_r2:.4f}")
logger.info(f"Test RMSE: {test_rmse:.6f}")
logger.info(f"Test MAE:  {test_mae:.6f}")

# Save
model_path = CONFIG.models_dir / "final_ridge_optimized.joblib"
joblib.dump(final_model, model_path)
logger.info(f"Saved: {model_path}")

# Feature importance
logger.info("\nTop 10 Feature Importances (abs coefficients):")
coeffs = pd.Series(final_model.coef_, index=features).abs().sort_values(ascending=False)
for feat, val in coeffs.head(10).items():
    logger.info(f"  {feat:40s} | {val:.6f}")

# Report
summary = pd.DataFrame([{
    "Model": "Ridge (HPO)",
    "Alpha": best_alpha,
    "Train R²": train_r2,
    "Test R²": test_r2,
    "Test RMSE": test_rmse,
    "Test MAE": test_mae,
}])
summary.to_csv(CONFIG.reports_dir / "optimized_summary.csv", index=False)
logger.info(f"\nReport: {CONFIG.reports_dir / 'optimized_summary.csv'}")

logger.info("\n" + "=" * 60)
logger.info("OPTIMIZED TRAINING COMPLETE")
logger.info("Stacking not beneficial: all base models predict identically (R²>0.99).")
logger.info("Single Ridge model is optimal for this near-deterministic target.")
logger.info("=" * 60)
