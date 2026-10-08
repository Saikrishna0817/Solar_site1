"""Phase 5 gates: only a Gate-3-passing residual model is served; else C0 only.

Gate 3 (models/gate.json, written by scripts/phase3_residual_ci.py):
LOGO MAE beats C0 with 95% district-bootstrap CI excluding 0 AND the same spec
beats C0 on held-out plants. Both checks + the interval must be readable.
"""
import json

import pandas as pd
import pytest

from src.api.services import gate
from src.api.services.gate import ModelNotServable

GATE_PASS = {
    "gate3_pass": True,
    "served_model": "ridge",
    "artifact": "models/residual_ridge.joblib",
    "best_model": "ridge",
    "gate3_by_model": {"ridge": True, "elastic_net": False},
    "heldout": {"model_mae": 0.0064, "c0_mae": 0.00785, "winner": "model"},
    "models": {"ridge": {"logo_mae": 0.0104, "delta_mae": -0.00359,
                         "delta_ci95": [-0.00565, -0.00115],
                         "conformal90_halfwidth": 0.00945}},
    "serving": "ml:ridge",
}


def _wire(tmp_path, monkeypatch, payload, artifact=True):
    path = tmp_path / "gate.json"
    if payload is not None:
        path.write_text(json.dumps(payload))
    monkeypatch.setattr(gate, "GATE_PATH", path)
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)
    if payload is not None and artifact:
        art = tmp_path / str(payload["artifact"])
        art.parent.mkdir(parents=True, exist_ok=True)
        art.write_bytes(b"")
    return path


def test_gate3_pass_serves_the_residual_artifact(tmp_path, monkeypatch):
    _wire(tmp_path, monkeypatch, GATE_PASS)
    assert gate.serving_model() == "ridge"
    assert gate.serving_artifact().name == "residual_ridge.joblib"


def test_gate3_failed_refuses_ml_serving(tmp_path, monkeypatch):
    payload = {**GATE_PASS, "gate3_pass": False, "served_model": None,
               "artifact": None, "serving": "baseline_c0_only"}
    _wire(tmp_path, monkeypatch, payload, artifact=False)
    with pytest.raises(ModelNotServable, match="Gate 3"):
        gate.serving_model()
    with pytest.raises(ModelNotServable, match="Gate 3"):
        gate.serving_artifact()


def test_missing_gate_file_refuses(tmp_path, monkeypatch):
    _wire(tmp_path, monkeypatch, None)
    with pytest.raises(ModelNotServable, match="gate.json missing"):
        gate.serving_model()


def test_gate_approved_artifact_missing_refuses(tmp_path, monkeypatch):
    _wire(tmp_path, monkeypatch, GATE_PASS, artifact=False)
    with pytest.raises(ModelNotServable, match="artifact missing"):
        gate.serving_artifact()


def test_gate_status_never_raises(tmp_path, monkeypatch):
    _wire(tmp_path, monkeypatch, None)
    status = gate.gate_status()
    assert status["serving_model"] is None
    assert "gate.json" in status["reason"]


def test_gate_status_exposes_heldout_and_interval(tmp_path, monkeypatch):
    _wire(tmp_path, monkeypatch, GATE_PASS)
    monkeypatch.setattr(gate, "METRICS_PATH", tmp_path / "absent_metrics.json")
    status = gate.gate_status()
    assert status["gate3_pass"] is True
    assert status["heldout"]["winner"] == "model"
    assert status["conformal90_halfwidth"] == 0.00945
    assert status["delta_ci95"][1] < 0  # CI excludes zero


def test_repo_gate_json_passes_and_artifact_exists():
    """The real gate.json must satisfy Gate 3 and ship its artifact.

    models/*.joblib is gitignored (regenerable), so a fresh clone skips the
    artifact half — the API fail-opens to C0 until phase3_residual_ci.py runs.
    """
    g = gate.load_gate()
    assert g["gate3_pass"] is True
    assert g["heldout"]["winner"] == "model"
    assert g["models"][g["served_model"]]["delta_ci95"][1] < 0
    if not gate.serving_artifact().exists():
        pytest.skip("models/*.joblib gitignored — run scripts/phase3_residual_ci.py")
    assert gate.serving_artifact().exists()


def test_linear_shap_never_fills_missing_features_with_zero():
    """A selected feature absent from the row must fail, not silently become 0."""
    from src.api.services import inference

    inference._feature_names = ["ghi", "missing_column"]
    try:
        row = pd.Series({"ghi": 5.0})
        with pytest.raises(ModelNotServable, match="missing from the serving feature table"):
            inference._extract_model_input(row)
    finally:
        inference._feature_names = None  # leave the module clean for other tests
