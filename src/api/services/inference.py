"""Inference service — loads trained model, applies preprocessing, and predicts CUF."""
import json
import logging
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.api.services.gate import ModelNotServable, serving_model

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = PROJECT_ROOT / "models"
PROCESSED_DIR = PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed"

_model = None
_feature_names = None
_preprocessed_df = None
_raw_df = None
_scaler = None
_loaded_name = None


def _load_model():
    """Load the gate-approved model, or raise ModelNotServable.

    There is no heuristic fallback here on purpose: serving a hand-rolled
    `ghi * 0.8 / 24` "prediction" when artifacts are missing is exactly the
    placeholder behaviour this phase removes.
    """
    global _model, _feature_names, _preprocessed_df, _raw_df, _scaler, _loaded_name

    name = serving_model()
    if _model is not None and _loaded_name == name:
        return

    model_path = MODELS_DIR / f"{name}.joblib"
    feature_path = MODELS_DIR / "feature_names.json"
    scaler_path = MODELS_DIR / "scaler_selected.joblib"
    missing = [p.name for p in (model_path, feature_path, scaler_path) if not p.exists()]
    if missing:
        raise ModelNotServable(f"artifacts missing for '{name}': {', '.join(missing)}")

    _model = joblib.load(model_path)
    _loaded_name = name
    with open(feature_path) as f:
        _feature_names = json.load(f)
    _scaler = joblib.load(scaler_path)  # train/serve parity: same transform as training

    prep_path = PROCESSED_DIR / "master_dataset_engineered.csv"
    raw_path = prep_path
    if not prep_path.exists():
        # fallback: the narrower district frame. It lacks some engineered columns
        # (e.g. aerosol_optical_depth), which _extract_model_input now refuses
        # rather than silently feeding the model a 0.
        prep_path = PROCESSED_DIR / "features_train.csv"
        raw_path = prep_path
    if not prep_path.exists():
        raise ModelNotServable(
            "processed features CSV missing — run the data pipeline first"
        )

    _preprocessed_df = pd.read_csv(prep_path)
    _raw_df = pd.read_csv(raw_path)


def _extract_model_input(row) -> np.ndarray:
    values = []
    for feat in _feature_names:
        val = row.get(feat) if hasattr(row, "get") else None
        if val is None:
            # Silent zero-filling hid a train/serve mismatch (aerosol_optical_depth
            # is absent from features_train.csv). Fail loudly instead.
            raise ModelNotServable(
                f"feature '{feat}' missing from the serving feature table — "
                "regenerate the pipeline outputs"
            )
        if isinstance(val, float) and np.isnan(val):
            val = 0.0
        values.append(float(val))
    return np.array([values])


def shap_for_district(district: str, top_k: int = 10) -> dict:
    """Per-feature attributions for one district, from the gate-approved model.

    Exact linear SHAP: contribution_j = coef_j * (x_j - mean_j), with mean_j the
    training means carried by the persisted scaler (so baseline == expected
    prediction over the training distribution).

    ponytail: only linear models get attributions — the serving gate prefers
    elastic_net, so that is what ships. Upgrade path: shap.TreeExplainer for the
    tree models, once a tree model honestly beats the C0 baseline.
    """
    _load_model()
    if not hasattr(_model, "coef_"):
        raise ModelNotServable(
            f"SHAP attributions are linear-model only; serving model "
            f"'{_loaded_name}' exposes no coefficients"
        )
    if _scaler is None:
        raise ModelNotServable("scaler missing — cannot attribute against training means")

    target = str(district).strip().lower()
    if _preprocessed_df is None or "district" not in _preprocessed_df.columns:
        raise ModelNotServable("processed features CSV has no district column")
    rows = _preprocessed_df[_preprocessed_df["district"].str.strip().str.lower() == target]
    if rows.empty:
        raise LookupError(f"district '{district}' not in the feature table")

    row = rows.iloc[0]
    x = _extract_model_input(row).ravel()
    coef = np.asarray(_model.coef_, dtype=float).ravel()
    mean = np.asarray(_scaler.mean_, dtype=float).ravel()
    if coef.shape != x.shape or mean.shape != x.shape:
        raise ModelNotServable(
            f"coef/scale mismatch ({coef.shape}, {mean.shape}, {x.shape}) — "
            "feature_names.json is out of step with the artifact"
        )
    contributions = coef * (x - mean)
    intercept = float(getattr(_model, "intercept_", 0.0))
    baseline = float(intercept + float(np.dot(coef, mean)))

    order = np.argsort(-np.abs(contributions))[:top_k]
    return {
        "district": target,
        "model": _loaded_name,
        "kind": "linear",
        "baseline": round(baseline, 6),
        "values": [
            {"feature": str(_feature_names[i]), "value": round(float(contributions[i]), 6)}
            for i in order
        ],
    }


def predict_cuf(latitude, longitude):
    _load_model()

    matched = None
    if _raw_df is not None and "latitude" in _raw_df.columns:
        dists = np.sqrt(  # local Series: never mutate the cached frame (race-safe)
            (_raw_df["latitude"] - latitude) ** 2 + (_raw_df["longitude"] - longitude) ** 2
        )
        nearest_idx = dists.idxmin()
        nearest_district = str(_raw_df.loc[nearest_idx, "district"]).strip().lower()
    else:
        nearest_district = None

    if nearest_district and _preprocessed_df is not None and "district" in _preprocessed_df.columns:
        mask = _preprocessed_df["district"].str.strip().str.lower() == nearest_district
        if mask.any():
            matched = _preprocessed_df[mask].iloc[0]

    if matched is None:
        matched = _preprocessed_df.iloc[0] if _preprocessed_df is not None else {}

    raw_row = _raw_df[_raw_df["district"].str.strip().str.lower() == nearest_district].iloc[0] \
        if nearest_district and _raw_df is not None and "district" in _raw_df.columns \
        else matched

    district = str(matched.get("district", "unknown"))
    state = str(raw_row.get("state", "unknown"))
    ghi = float(raw_row.get("avg_ghi_kwh_m2_day", 5.0))
    temp = float(raw_row.get("avg_temp_c", 27.0))

    X = _extract_model_input(matched)
    if _scaler is not None:
        X = _scaler.transform(X)
    try:
        cuf = float(_model.predict(X)[0])
    except Exception as exc:
        # No heuristic fallback: a failed predict is a 500, not a made-up number.
        logger.exception(f"model '{_loaded_name}' failed for district {district}")
        raise
    # No clamp: report what the model said. Out-of-band values are a symptom
    # (bad features, extrapolation) and hiding them made it undiagnosable.
    if not 0.05 <= cuf <= 0.35:
        logger.warning(
            "Raw CUF prediction %.4f outside the plausible 0.05-0.35 band "
            "for district %s — reported unclamped", cuf, district,
        )

    score = round(cuf / 0.22, 3)
    score = max(0.0, min(1.0, score))

    if score >= 0.8:
        label = "Excellent"
    elif score >= 0.6:
        label = "Good"
    elif score >= 0.4:
        label = "Moderate"
    else:
        label = "Developing"

    return {
        "district": district,
        "state": state,
        "cuf_predicted": round(cuf, 4),
        "suitability_score": score,
        "suitability_label": label,
        "ghi": ghi,
        "temperature": temp,
        "serving_model": _loaded_name,
        "model_version": "1.0.0",
    }