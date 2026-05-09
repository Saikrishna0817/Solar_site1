"""Tests for solarpipeline.features."""

import pandas as pd
from solarpipeline.features import engineer_features, _safe_assign


def test_engineer_features_adds_columns():
    df = _make_minimal_df()
    result = engineer_features(df)
    expected = {
        "solar_variability", "solar_efficiency_index",
        "terrain_flatness_score", "infrastructure_accessibility_index",
        "forest_proximity_km", "dominant_land_use",
        "climate_stress_index", "humidity_temp_interaction",
    }
    # Check all expected columns exist
    assert expected.issubset(set(result.columns))
    # Check target_leaker is removed
    assert "installed_solar_capacity_mw" not in result.columns


def test_engineer_features_no_leaker_warning():
    """Should not crash if leaker column is missing."""
    df = _make_minimal_df().drop(columns=["installed_solar_capacity_mw"], errors="ignore")
    result = engineer_features(df)
    assert result is not None
    assert len(result) == 2


def test_safe_assign_success():
    df = _make_minimal_df()
    ok = _safe_assign(df, "ghi_dni_ratio", lambda d: d["avg_ghi_kwh_m2_day"] / d["avg_dni_kwh_m2_day"])
    assert ok
    assert len(df["ghi_dni_ratio"]) == 2


def test_safe_assign_failure():
    df = _make_minimal_df()
    ok = _safe_assign(df, "bad_col", lambda d: d["nonexistent"] / 0, fallback=0)
    assert not ok
    assert df["bad_col"].tolist() == [0, 0]


def _make_minimal_df() -> pd.DataFrame:
    return pd.DataFrame({
        "installed_solar_capacity_mw": [100, 200],
        "avg_dni_kwh_m2_day": [5.0, 6.0],
        "avg_dhi_kwh_m2_day": [2.0, 2.5],
        "avg_ghi_kwh_m2_day": [5.5, 6.2],
        "avg_temp_c": [28.0, 30.0],
        "max_temp_c": [35.0, 38.0],
        "avg_humidity_pct": [60.0, 55.0],
        "slope_deg": [2.0, 5.0],
        "dist_nearest_road_km": [1.0, 3.0],
        "dist_nearest_transmission_line_km": [2.0, 4.0],
        "dist_nearest_substation_km": [5.0, 8.0],
        "wasteland_pct": [10.0, 20.0],
        "builtup_pct": [5.0, 8.0],
        "tree_cover_pct": [15.0, 25.0],
    })
