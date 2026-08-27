"""Inference service — loads trained model, applies preprocessing, and predicts CUF."""
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = PROJECT_ROOT / "models"
PROCESSED_DIR = PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed"

_model = None
_feature_names = None
_preprocessed_df = None
_raw_df = None


def _load_model():
    global _model, _feature_names, _preprocessed_df, _raw_df
    if _model is not None:
        return

    model_path = MODELS_DIR / "ridge.joblib"
    feature_path = MODELS_DIR / "feature_names.json"

    if model_path.exists():
        _model = joblib.load(model_path)
        if feature_path.exists():
            with open(feature_path) as f:
                _feature_names = json.load(f)

    if not _feature_names:
        _feature_names = ["avg_ghi_kwh_m2_day", "avg_temp_c", "elevation_m", "slope_deg"]

    prep_path = PROCESSED_DIR / "features_train.csv"
    raw_path = PROCESSED_DIR / "master_dataset_engineered.csv"
    if not prep_path.exists():
        prep_path = raw_path
    if not raw_path.exists():
        raw_path = prep_path

    _preprocessed_df = pd.read_csv(prep_path)
    _raw_df = pd.read_csv(raw_path)


def _extract_model_input(row) -> np.ndarray:
    values = []
    for feat in _feature_names:
        val = row.get(feat)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            val = 0.0
        values.append(float(val))
    return np.array([values])


def predict_cuf(latitude, longitude):
    _load_model()

    matched = None
    if _raw_df is not None and "latitude" in _raw_df.columns:
        _raw_df["_dist"] = np.sqrt(
            (_raw_df["latitude"] - latitude) ** 2 + (_raw_df["longitude"] - longitude) ** 2
        )
        nearest_idx = _raw_df["_dist"].idxmin()
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

    if _model is not None:
        X = _extract_model_input(matched)
        try:
            cuf = float(_model.predict(X)[0])
            cuf = max(0.05, min(0.35, cuf))
        except (ValueError, IndexError):
            cuf = round(ghi * 0.8 / 24.0, 4)
    else:
        cuf = round(ghi * 0.8 / 24.0, 4)

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
        "model_version": "1.0.0",
    }