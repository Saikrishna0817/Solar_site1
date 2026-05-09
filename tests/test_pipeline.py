"""Integration tests for the solarpipeline core functions with mock DataFrames."""

import numpy as np
import pandas as pd
import pytest

from solarpipeline import (
    engineer_features,
    preprocess,
    compute_cuf_theoretical,
)


def _make_base_df(n=4):
    """Return a minimal DataFrame that mimics ``merge_sources()`` output."""
    return pd.DataFrame({
        "district": [f"d{i}" for i in range(n)],
        "state": ["TS", "TS", "AP", "AP"][:n],
        "latitude": [17.0] * n,
        "longitude": [78.0] * n,
        "avg_ghi_kwh_m2_day": [5.2] * n,
        "avg_dni_kwh_m2_day": [4.0] * n,
        "avg_dhi_kwh_m2_day": [2.0] * n,
        "avg_temp_c": [28.0] * n,
        "max_temp_c": [34.0] * n,
        "avg_wind_speed_m_s": [3.0] * n,
        "avg_humidity_pct": [60.0] * n,
        "annual_rainfall_mm": [1000.0] * n,
        "avg_cloud_cover_pct": [30.0] * n,
        "elevation_m": [500.0] * n,
        "slope_deg": [2.0] * n,
        "aspect_deg": [180.0] * n,
        "dist_nearest_road_km": [1.0] * n,
        "dist_nearest_transmission_line_km": [2.0] * n,
        "dist_nearest_substation_km": [5.0] * n,
        "aod_2023": [0.45] * n,
        "tree_cover_pct": [10.0] * n,
        "shrubland_pct": [10.0] * n,
        "grassland_pct": [20.0] * n,
        "cropland_pct": [30.0] * n,
        "builtup_pct": [5.0] * n,
        "wasteland_pct": [10.0] * n,
        "water_pct": [5.0] * n,
        "wetland_pct": [5.0] * n,
        "census_pop_2011": [1_000_000] * n,
        "census_pop_2024_projected": [1_200_000] * n,
        "district_area_sqkm": [100.0] * n,
        "population_density_per_sqkm": [10_000.0] * n,
        "source": ["census"] * n,
        "cuf": [0.1500, 0.1510, 0.1520, 0.1530][:n],
    })


class TestEngineerFeatures:
    def test_adds_engineered_columns(self):
        df = _make_base_df()
        result = engineer_features(df)
        expected = {
            "solar_variability", "solar_efficiency_index",
            "terrain_flatness_score", "infrastructure_accessibility_index",
            "forest_proximity_km", "dominant_land_use",
            "climate_stress_index", "humidity_temp_interaction",
        }
        assert expected.issubset(set(result.columns))

    def test_removes_target_leaker(self):
        df = _make_base_df()
        df["installed_solar_capacity_mw"] = [100, 200, 300, 400]
        result = engineer_features(df)
        assert "installed_solar_capacity_mw" not in result.columns

    def test_no_leaker_column_no_crash(self):
        df = _make_base_df()
        # already no leaker column present
        result = engineer_features(df)
        assert result is not None
        assert len(result) == 4


class TestPreprocess:
    def test_split_outputs_correct_shape(self):
        df = _make_base_df()
        features, labels = preprocess(df)
        assert features is not None
        assert labels is not None
        # With 4 rows and 20% test, random split gives train=3 test=1
        assert len(features) == 3  # X_train after split
        assert "cuf" in labels.columns

    def test_no_target_leakage_in_features(self):
        df = _make_base_df()
        features, _ = preprocess(df)
        assert "installed_solar_capacity_mw" not in features.columns
        assert "aerosol_optical_depth" not in features.columns

    def test_cuf_range_reasonable(self):
        df = _make_base_df()
        _, labels = preprocess(df)
        assert labels["cuf"].min() > 0.10
        assert labels["cuf"].max() < 0.20


class TestComputeCuf:
    def test_cuf_basic(self):
        cuf = compute_cuf_theoretical(5.5, 28.0)
        assert 0.10 < cuf < 0.25

    def test_cuf_temperature_penalty(self):
        # Hotter temp -> lower PR -> lower CUF
        cuf_hot = compute_cuf_theoretical(5.0, 40.0)
        cuf_cool = compute_cuf_theoretical(5.0, 20.0)
        assert cuf_hot < cuf_cool

    def test_cuf_reproducible(self):
        assert compute_cuf_theoretical(5.2, 27.5) == compute_cuf_theoretical(5.2, 27.5)

    def test_cuf_zero_ghi(self):
        assert compute_cuf_theoretical(0.0, 25.0) == 0.0
