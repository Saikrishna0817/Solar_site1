"""Serving gate — the API only serves models that beat the C0 physics baseline.

Threshold is the same bar the report prints: CV MAE < C0 MAE (see
src/ml/evaluation/core.py::write_metrics). Nothing else is checked: no free-form
thresholds to tune, no per-model exceptions.

ponytail: one file, one rule. If the project ever needs graded serving (e.g. warn
below 1.0x C0, block above 1.2x), move the rule into metrics.json as numbers and
read it here — do not grow a policy engine.
"""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = PROJECT_ROOT / "models"
METRICS_PATH = MODELS_DIR / "metrics.json"


class ModelNotServable(Exception):
    """No trained model clears the serving threshold."""


def load_metrics() -> dict:
    if not METRICS_PATH.exists():
        raise ModelNotServable(
            "models/metrics.json missing — train first: python -m src.cli.train"
        )
    try:
        return json.loads(METRICS_PATH.read_text())
    except (OSError, ValueError) as exc:
        raise ModelNotServable(f"models/metrics.json unreadable: {exc}")


def serving_model() -> str:
    """Name of the best model that beats C0 — the one /predict will load."""
    metrics = load_metrics()
    c0_mae = metrics.get("c0_mae")
    if not c0_mae:
        raise ModelNotServable(
            "C0 baseline score unavailable — run scripts/baseline_c0.py, then retrain"
        )

    passing = [m for m in metrics.get("models", []) if m.get("beats_c0")]
    if not passing:
        raise ModelNotServable(
            f"no model beats the C0 physics baseline (c0_mae={c0_mae:.4f}) — "
            "refusing to serve; improve the model or raise the baseline honestly"
        )

    best = min(passing, key=lambda m: m["cv_mae"])
    name = str(best["model_name"])
    if not (MODELS_DIR / f"{name}.joblib").exists():
        raise ModelNotServable(f"model '{name}' passes the gate but its artifact is missing")
    return name


def gate_status() -> dict:
    """For /api/health — reports the verdict without ever raising."""
    try:
        name = serving_model()
        metrics = load_metrics()
        best = next(m for m in metrics["models"] if m["model_name"] == name)
        return {
            "metrics_ok": True,
            "serving_model": name,
            "cv_mae": best["cv_mae"],
            "cv_r2": best["cv_r2"],
            "c0_mae": metrics["c0_mae"],
            "threshold": metrics.get("threshold", "cv_mae < c0_mae"),
        }
    except ModelNotServable as exc:
        return {"metrics_ok": False, "serving_model": None, "reason": str(exc)}
