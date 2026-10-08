"""API data access layer — loads processed pipeline outputs into memory."""
import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DIR = PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed"

_sites_cache = None


def suitability_from_cuf(cuf, reference_cufs=None):
    """Suitability score = percentile rank of `cuf` among the in-scope
    districts' CUF values (0-1).

    The old `cuf / 0.22` divided by a fixed assumed CUF, which invented a
    scale no source supports. This is a documented relative scale instead:
    1.0 = at or above the best in-scope district, 0.5 ≈ median, 0 = below all.
    With no reference distribution to rank against there is no relative
    position to report, hence 0.5.
    """
    if reference_cufs is None:
        reference_cufs = [s["cuf_predicted"] for s in load_processed_sites()]
    vals = sorted(reference_cufs)
    if not vals:
        return 0.5
    return round(sum(1 for v in vals if v <= cuf) / len(vals), 3)


def _normalize_row(row, idx, cufs):
    cuf = float(row.get("cuf", 0.15))
    return {
        "district": str(row.get("district", f"site_{idx}")),
        "state": str(row.get("state", "Unknown")),
        "cuf_predicted": cuf,
        "suitability_score": suitability_from_cuf(cuf, cufs),
        "ghi": float(row.get("avg_ghi_kwh_m2_day", 5.0)),
        "temperature": float(row.get("avg_temp_c", 27.0)),
        "elevation": float(row.get("elevation_m", 300)),
    }


def load_processed_sites():
    global _sites_cache
    if _sites_cache is not None:
        return _sites_cache

    features_path = PROCESSED_DIR / "master_dataset_engineered.csv"
    if not features_path.exists():
        features_path = PROCESSED_DIR / "features_train.csv"

    if not features_path.exists():
        _sites_cache = [_get_fallback_sites()]
        return _sites_cache

    df = pd.read_csv(features_path)
    cufs = [float(v) for v in df["cuf"].dropna()] if "cuf" in df.columns else []
    sites = []
    for idx, row in df.iterrows():
        sites.append(_normalize_row(row, idx, cufs))
    _sites_cache = sites
    return sites


def load_site_detail(district_id):
    sites = load_processed_sites()
    for site in sites:
        if site["district"].lower() == district_id.lower():
            return {
                **site,
                "suitability_label": _suitability_label(site["suitability_score"]),
                "latitude": 20.0,
                "longitude": 78.0,
                "dni": site.get("avg_dni_kwh_m2_day", 4.5),
                "slope": site.get("slope_deg", 2.0),
                "land_use": site.get("dominant_land_use", "unknown"),
                "grid_distance": site.get("dist_nearest_substation_km", 10),
            }
    return None


def load_state_summary():
    import pandas as pd

    sites = load_processed_sites()
    df = pd.DataFrame(sites)
    if df.empty or "state" not in df.columns:
        return [{"state": "Rajasthan", "count": 33, "avg_suitability": 0.85}]

    summary = df.groupby("state").agg(
        count=("district", "count"),
        avg_suitability=("suitability_score", "mean"),
        avg_ghi=("ghi", "mean"),
    ).reset_index()
    summary["avg_suitability"] = summary["avg_suitability"].round(3)
    summary["avg_ghi"] = summary["avg_ghi"].round(1)
    return summary.to_dict(orient="records")


def _suitability_label(score):
    if score >= 0.8:
        return "Excellent"
    if score >= 0.6:
        return "Good"
    if score >= 0.4:
        return "Moderate"
    return "Developing"


def _get_fallback_sites():
    return {
        "district": "bhadla solar park",
        "state": "Rajasthan",
        "cuf_predicted": 0.239,
        "suitability_score": 0.94,
        "ghi": 5.72,
        "temperature": 28.5,
        "elevation": 220.0,
    }