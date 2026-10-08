"""Serving gate — Phase 5.1: reads Phase 3 results (models/gate.json), not only CV MAE.

Gate 3 rule (scripts/phase3_residual_ci.py):
  * residual model beats C0 on pooled leave-one-district-out MAE with the 95%
    district-bootstrap interval excluding zero, AND
  * the same model spec beats C0 on held-out plants (20%, seed 42).
Only then is an ML artifact served; otherwise the API serves the C0 physics
baseline alone and says so.

ponytail: one JSON, one rule, no policy engine. When Gate 3 ever needs grades
(warn vs block), add numbers to gate.json — don't grow this file.
"""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = PROJECT_ROOT / "models"
METRICS_PATH = MODELS_DIR / "metrics.json"
GATE_PATH = MODELS_DIR / "gate.json"


class ModelNotServable(Exception):
    """No trained model clears the serving gate."""


def load_metrics() -> dict:
    if not METRICS_PATH.exists():
        raise ModelNotServable(
            "models/metrics.json missing — train first: python -m src.cli.train"
        )
    try:
        return json.loads(METRICS_PATH.read_text())
    except (OSError, ValueError) as exc:
        raise ModelNotServable(f"models/metrics.json unreadable: {exc}")


def load_gate() -> dict:
    if not GATE_PATH.exists():
        raise ModelNotServable(
            "models/gate.json missing — run scripts/phase3_residual_ci.py"
        )
    try:
        return json.loads(GATE_PATH.read_text())
    except (OSError, ValueError) as exc:
        raise ModelNotServable(f"models/gate.json unreadable: {exc}")


def serving_artifact() -> Path:
    """Path of the Gate-3-approved artifact — the only ML bundle /predict loads.

    Raises ModelNotServable when Gate 3 failed: callers must fall back to the
    C0 baseline (or refuse), never to an unapproved artifact.
    """
    gate = load_gate()
    if not gate.get("gate3_pass") or not gate.get("served_model"):
        raise ModelNotServable(
            f"Gate 3 failed (held-out or LOGO-CI): {gate.get('gate3_by_model')} — "
            "serving baseline C0 only"
        )
    artifact = gate.get("artifact")
    path = PROJECT_ROOT / str(artifact) if artifact else None
    if path is None or not path.exists():
        raise ModelNotServable(
            f"gate-approved artifact missing ({artifact}) — re-run "
            "scripts/phase3_residual_ci.py"
        )
    return path


def serving_model() -> str:
    """Name of the Gate-3-approved model ('ridge' etc.)."""
    gate = load_gate()
    if not gate.get("gate3_pass") or not gate.get("served_model"):
        raise ModelNotServable("Gate 3 failed — no ML model is served")
    return str(gate["served_model"])


def gate_status() -> dict:
    """For /api/health — the verdict, interval and held-out check; never raises."""
    out: dict = {"metrics_ok": False, "serving_model": None}
    try:
        gate = load_gate()
    except ModelNotServable as exc:
        out["reason"] = str(exc)
        return out
    out.update({
        "gate3_pass": bool(gate.get("gate3_pass")),
        "gate3_rule": gate.get("gate3_rule"),
        "heldout": gate.get("heldout"),
        "conformal90_halfwidth": (gate.get("models", {})
                                  .get(gate.get("served_model") or "", {})
                                  .get("conformal90_halfwidth")),
        "serving": gate.get("serving"),
        "best_model": gate.get("best_model"),
        "delta_ci95": (gate.get("models", {})
                       .get(gate.get("served_model") or gate.get("best_model") or "", {})
                       .get("delta_ci95")),
    })
    if gate.get("gate3_pass"):
        out["serving_model"] = gate.get("served_model")
    try:
        metrics = load_metrics()
        out["metrics_ok"] = True
        out["c0_mae"] = metrics.get("c0_mae")
        out["threshold"] = gate.get("gate3_rule")
    except ModelNotServable as exc:
        out["reason"] = str(exc)
    return out
