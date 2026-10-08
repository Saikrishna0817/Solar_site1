"""Inference service — Gate-3 residual model over the C0 physics baseline.

Serving contract (plan 5.1-5.4):
  * ML path: residual model from models/gate.json bundle ->
    cuf = c0_physics(district) + residual_pred, with a conformal 90% interval
    and a training-domain flag (distance to nearest labelled plant).
  * Site-scale features (5.2): the served model's inputs (GHI, max temp) are
    fetched per request coordinates from NASA POWER climatology (cached on disk);
    when the API is unreachable we fall back to the nearest-district row and say
    so (`features_source`).
  * Baseline path: when Gate 3 fails, serve C0 alone, labelled `kind=baseline_c0`
    and the withheld reason — never an unapproved artifact, never a heuristic.
  * Missing features raise (no silent zero-filling of absent columns).

ponytail ceilings: 5.6 site-scale exclusions (slope/WorldCover/protected areas)
need GEE + rasterio — not available here; the domain flag is distance-based
instead. Upgrade path: exclusion mask at candidate point when creds exist.
"""
import json
import logging
import math
import urllib.parse
import urllib.request
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.api.services.data import suitability_from_cuf
from src.api.services.gate import ModelNotServable, serving_artifact

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = PROJECT_ROOT / "models"
PROCESSED_DIR = PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed"
C0_PATH = PROCESSED_DIR / "c0_baseline.csv"
TRAIN_COORDS_PATH = PROJECT_ROOT / "data" / "plant_labels" / "plant_dataset.csv"
POWER_CACHE_DIR = PROJECT_ROOT / "data" / "cache" / "power_point"

POWER_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
# ANN values we map into feature names (subset of datasources/nasa_power_v2.PARAMETERS)
POWER_MAP = {
    "ALLSKY_SFC_SW_DWN": "avg_ghi_kwh_m2_day",
    "T2M_MAX": "max_temp_c",
    "T2M": "avg_temp_c",
    "ALLSKY_SFC_SW_DNI": "avg_dni_kwh_m2_day",
    "ALLSKY_SFC_SW_DIFF": "avg_dhi_kwh_m2_day",
}
POWER_TIMEOUT_S = 8  # one shot, no retry: API latency stays bounded; fallback below

# ponytail: 150 km is a round number, not a tuned one (n=13 labels).
# Upgrade path: k-nearest-label CV distance once TGTRANSCO capacity grows n.
DOMAIN_KM_MAX = 150.0

_model = None
_feature_names = None
_preprocessed_df = None
_raw_df = None
_scaler = None
_loaded_name = None
_conformal90 = None
_c0 = None
_train_coords = None
_withheld_reason = None


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _load_frame():
    """Load district feature frames + C0 table + training plant coords."""
    global _preprocessed_df, _raw_df, _c0, _train_coords

    prep_path = PROCESSED_DIR / "master_dataset_engineered.csv"
    if not prep_path.exists():
        prep_path = PROCESSED_DIR / "features_train.csv"  # narrower fallback frame
    if not prep_path.exists():
        raise ModelNotServable("processed features CSV missing — run the data pipeline first")
    _preprocessed_df = pd.read_csv(prep_path)
    _raw_df = _preprocessed_df

    if not C0_PATH.exists():
        raise ModelNotServable("c0_baseline.csv missing — run scripts/baseline_c0.py")
    c0 = pd.read_csv(C0_PATH)
    c0["district"] = c0["district"].str.strip().str.lower()
    _c0 = c0

    if TRAIN_COORDS_PATH.exists():
        coords = pd.read_csv(TRAIN_COORDS_PATH)[["district", "latitude", "longitude"]]
        coords["district"] = coords["district"].str.strip().str.lower()
        _train_coords = coords
    else:
        _train_coords = None


def _load_model():
    """Load the Gate-3-approved residual bundle; fall back to baseline-only.

    Raises ModelNotServable only for hard failures (no frame/C0 at all).
    A failed gate is not an error: it switches serving to C0 and records why.
    """
    global _model, _feature_names, _scaler, _loaded_name, _conformal90
    global _withheld_reason

    _load_frame()

    try:
        path = serving_artifact()
    except ModelNotServable as exc:
        logger.warning("Gate 3 not passed — serving C0 baseline only: %s", exc)
        _model, _feature_names, _scaler, _loaded_name, _conformal90 = None, None, None, None, None
        _withheld_reason = str(exc)
        return

    bundle = joblib.load(path)
    _model = bundle["model"]
    _scaler = bundle["scaler"]
    _feature_names = list(bundle["features"])
    _loaded_name = str(bundle.get("model_name", path.stem))
    _conformal90 = float(bundle.get("conformal90_halfwidth", 0.0))
    _withheld_reason = None


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


def _c0_for(district: str) -> float:
    if _c0 is None:
        raise ModelNotServable("C0 baseline table not loaded")
    rows = _c0[_c0["district"] == district]
    if rows.empty:
        raise LookupError(f"district '{district}' not in the C0 baseline table")
    return float(rows.iloc[0]["c0_cuf"])


def power_ann_features(latitude, longitude) -> dict | None:
    """NASA POWER climatology ANN values mapped to feature names (cached).

    None on any failure/timeout -> caller falls back to the district row.
    """
    cache = POWER_CACHE_DIR / f"{latitude:.2f}_{longitude:.2f}.json"
    if cache.exists():
        try:
            return json.loads(cache.read_text())
        except (OSError, ValueError):
            pass  # refetch below
    query = urllib.parse.urlencode({
        "parameters": ",".join(POWER_MAP), "community": "RE",
        "longitude": round(longitude, 4), "latitude": round(latitude, 4),
        "format": "JSON", "header": "false",
    })
    try:
        with urllib.request.urlopen(f"{POWER_URL}?{query}", timeout=POWER_TIMEOUT_S) as resp:
            props = json.load(resp).get("properties", {}).get("parameter", {})
    except Exception as exc:  # noqa: BLE001 — any network/parse failure = fallback
        logger.warning("NASA POWER point fetch failed (%s) — district-row fallback", exc)
        return None
    out = {}
    for param, name in POWER_MAP.items():
        val = props.get(param, {}).get("ANN")
        if isinstance(val, (int, float)) and val > -90:  # -999 quality flags
            out[name] = float(val)
    if not out:
        return None
    try:
        POWER_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(out))
    except OSError:
        pass  # uncached is fine
    return out


def _domain_flag(latitude, longitude) -> dict:
    """Distance from the requested point to the nearest labelled training plant."""
    if _train_coords is None or _train_coords.empty:
        return {"within_domain": None, "domain_distance_km": None}
    dists = _train_coords.apply(
        lambda r: _haversine_km(latitude, longitude, r["latitude"], r["longitude"]),
        axis=1,
    )
    min_km = float(dists.min())
    return {"within_domain": bool(min_km <= DOMAIN_KM_MAX),
            "domain_distance_km": round(min_km, 1)}


def shap_for_district(district: str, top_k: int = 10) -> dict:
    """Per-feature attributions for one district, from the Gate-3 model.

    Exact linear SHAP on the residual target: contribution_j = coef_j * (x_j - mean_j),
    means from the persisted scaler. Contributions are in residual CUF units
    (added on top of C0); C0 itself is constant per district and unattributed.
    """
    _load_model()
    if _model is None:
        raise ModelNotServable(
            f"Gate 3 not passed ({_withheld_reason}) — C0 baseline has no ML attributions"
        )
    if not hasattr(_model, "coef_"):
        raise ModelNotServable(
            f"SHAP attributions are linear-model only; serving model "
            f"'{_loaded_name}' exposes no coefficients"
        )

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
            "bundle scaler/model out of step"
        )
    contributions = coef * (x - mean)
    intercept = float(getattr(_model, "intercept_", 0.0))
    baseline = float(intercept + float(np.dot(coef, mean)))

    order = np.argsort(-np.abs(contributions))[:top_k]
    return {
        "district": target,
        "model": _loaded_name,
        "kind": "linear_residual",
        "units": "residual_cuf (added to C0)",
        "baseline_residual": round(baseline, 6),
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

    district = str(matched.get("district", "unknown")).strip().lower()
    state = str(raw_row.get("state", "unknown"))
    c0 = _c0_for(district)

    features_source = "district_row_nearest"
    inp = matched.to_dict() if hasattr(matched, "to_dict") else dict(matched)
    if _model is not None:
        site = power_ann_features(latitude, longitude)
        if site and all(f in site for f in _feature_names):
            inp.update(site)  # 5.2: site-scale inputs at request coords
            features_source = "nasa_power_point"

    ghi = float(inp.get("avg_ghi_kwh_m2_day", 5.0))
    temp = float(inp.get("avg_temp_c", 27.0))

    if _model is None:
        # Baseline-only serving (Gate 3 failed): honest C0, labelled as such.
        cuf = c0
        interval = None
        kind = "baseline_c0"
        serving_name = "c0_physics"
        features_source = "c0_physics_no_model"
    else:
        X = _extract_model_input(inp)
        X = _scaler.transform(X)
        try:
            residual = float(_model.predict(X)[0])
        except Exception as exc:
            # No heuristic fallback: a failed predict is a 500, not a made-up number.
            logger.exception(f"model '{_loaded_name}' failed for district {district}")
            raise
        cuf = c0 + residual  # C0 is the additive base (plan Phase 3.2)
        interval = [round(cuf - _conformal90, 4), round(cuf + _conformal90, 4)]
        kind = f"residual_{_loaded_name}"
        serving_name = _loaded_name

    # No clamp: report what the model said. Out-of-band values are a symptom
    # (bad features, extrapolation) and hiding them made it undiagnosable.
    if not 0.05 <= cuf <= 0.35:
        logger.warning(
            "Raw CUF prediction %.4f outside the plausible 0.05-0.35 band "
            "for district %s — reported unclamped", cuf, district,
        )

    score = suitability_from_cuf(cuf)

    if score >= 0.8:
        label = "Excellent"
    elif score >= 0.6:
        label = "Good"
    elif score >= 0.4:
        label = "Moderate"
    else:
        label = "Developing"

    out = {
        "district": district,
        "state": state,
        "cuf_predicted": round(cuf, 4),
        "c0_physics": round(c0, 4),
        "suitability_score": score,
        "suitability_label": label,
        "ghi": ghi,
        "temperature": temp,
        "interval_90": interval,
        "kind": kind,
        "features_source": features_source,
        "serving_model": serving_name,
        "model_version": "2.0.0",
    }
    out.update(_domain_flag(latitude, longitude))
    if _withheld_reason:
        out["ml_withheld_reason"] = _withheld_reason
    return out
