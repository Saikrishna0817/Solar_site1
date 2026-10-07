"""Phase 5 gates: the API only serves models that beat the C0 physics baseline."""
import json

import pandas as pd
import pytest

from src.api.services import gate
from src.api.services.gate import ModelNotServable

METRICS_OK = {
    "c0_mae": 0.0100,
    "c0_n_districts": 11,
    "threshold": "cv_mae < c0_mae",
    "models": [
        {"model_name": "ridge", "cv_mae": 0.0120, "cv_r2": -0.2, "beats_c0": False},
        {"model_name": "lasso", "cv_mae": 0.0090, "cv_r2": 0.1, "beats_c0": True},
        {"model_name": "elastic_net", "cv_mae": 0.0070, "cv_r2": 0.2, "beats_c0": True},
    ],
}


def _wire(tmp_path, monkeypatch, payload):
    path = tmp_path / "metrics.json"
    if payload is not None:
        path.write_text(json.dumps(payload))
    monkeypatch.setattr(gate, "METRICS_PATH", path)
    monkeypatch.setattr(gate, "MODELS_DIR", tmp_path)
    return path


def test_serving_model_picks_lowest_cv_mae_that_beats_c0(tmp_path, monkeypatch):
    _wire(tmp_path, monkeypatch, METRICS_OK)
    for name in ("lasso", "elastic_net"):
        (tmp_path / f"{name}.joblib").write_bytes(b"")
    assert gate.serving_model() == "elastic_net"


def test_model_that_beats_c0_but_has_no_artifact_is_rejected(tmp_path, monkeypatch):
    _wire(tmp_path, monkeypatch, METRICS_OK)
    (tmp_path / "lasso.joblib").write_bytes(b"")  # elastic_net artifact absent
    with pytest.raises(ModelNotServable, match="artifact is missing"):
        gate.serving_model()


def test_no_model_beats_c0_refuses(tmp_path, monkeypatch):
    payload = {**METRICS_OK, "models": [dict(m, beats_c0=False) for m in METRICS_OK["models"]]}
    _wire(tmp_path, monkeypatch, payload)
    with pytest.raises(ModelNotServable, match="no model beats"):
        gate.serving_model()


def test_missing_metrics_file_refuses(tmp_path, monkeypatch):
    _wire(tmp_path, monkeypatch, None)
    with pytest.raises(ModelNotServable, match="metrics.json missing"):
        gate.serving_model()


def test_gate_status_never_raises(tmp_path, monkeypatch):
    _wire(tmp_path, monkeypatch, None)
    status = gate.gate_status()
    assert status["metrics_ok"] is False
    assert status["serving_model"] is None
    assert "metrics.json" in status["reason"]


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
