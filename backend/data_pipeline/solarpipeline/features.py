"""
Feature engineering module.
Derives composite and domain-specific features from raw merged data.
All magic numbers are read from the shared ``PipelineConfig``.

Phase 2: composite scores rebuilt from the label's own inputs are NOT created here
(``effective_ghi``, ``solar_potential_score`` — see docs/METHODOLOGY.md §6). Raw
GHI/DNI/temp/humidity stay; the model should fit those, not a hand-written proxy for them.
"""

from typing import Any, Callable

import numpy as np
import pandas as pd

from solarpipeline.utils import get_logger, CONFIG

logger = get_logger(__name__)


def _safe_assign(df: pd.DataFrame, col_name: str, fn: Callable, fallback: Any = None) -> bool:
    """Assign ``df[col_name] = fn(df)``; log warning and optionally set fallback on failure."""
    try:
        df[col_name] = fn(df)
        return True
    except Exception as exc:
        logger.warning("Feature '%s' failed: %s -- using fallback", col_name, exc)
        if fallback is not None:
            df[col_name] = fallback
        return False


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive composite features for solar-site suitability modelling.

    Removes known target-leaking columns, then computes ~15 derived features
    from existing raw columns.  Each derivation is wrapped in ``_safe_assign``
    so that a single failure never blocks the rest.

    Parameters
    ----------
    df : pd.DataFrame
        Merged dataset (output of ``merge_sources``).

    Returns
    -------
    pd.DataFrame
        Copy of input with additional engineered columns.
    """
    logger.info("Phase 2: Feature Engineering ...")
    df = df.copy()

    # Drop target-leaking columns (audit #3)
    df.drop(columns=[c for c in ["installed_solar_capacity_mw"] if c in df.columns],
            inplace=True, errors="ignore")

    # ── 1–2. Solar resource ratios ────────────────────────────
    _safe_assign(df, "solar_variability",
                 lambda d: d["avg_dni_kwh_m2_day"] / (d["avg_dhi_kwh_m2_day"] + 0.01))
    _safe_assign(df, "solar_efficiency_index",
                 lambda d: d["avg_dni_kwh_m2_day"] / (d["avg_ghi_kwh_m2_day"] + 0.01))

    # ── 3. Terrain flatness score ─────────────────────────────
    _safe_assign(df, "terrain_flatness_score",
                 lambda d: 1 / (1 + d["slope_deg"]))

    # ── 4. Infrastructure accessibility index ──────────────────
    def _infra_idx(d):
        w_r, w_g, w_s = (CONFIG.infra_road_weight,
                         CONFIG.infra_grid_weight,
                         CONFIG.infra_substation_weight)
        return (
            1 / (1 + d["dist_nearest_road_km"]) * w_r +
            1 / (1 + d["dist_nearest_transmission_line_km"]) * w_g +
            1 / (1 + d["dist_nearest_substation_km"]) * w_s
        )
    _safe_assign(df, "infrastructure_accessibility_index", _infra_idx)

    # ── 5. Forest proximity ───────────────────────────────────
    _safe_assign(df, "forest_proximity_km",
                 lambda d: CONFIG.forest_prox_scale / (d["tree_cover_pct"] + 1))

    # ── 6. Dominant land use (categorical) ────────────────────
    try:
        land_cols = [c for c in df.columns if c.endswith("_pct")
                     and c not in ("avg_cloud_cover_pct", "avg_humidity_pct")]
        if land_cols:
            df["dominant_land_use"] = df[land_cols].idxmax(axis=1).str.replace("_pct", "")
    except Exception as exc:
        logger.warning("dominant_land_use failed: %s", exc)

    # ── 7–8. Climate interaction indices ──────────────────────
    _safe_assign(df, "climate_stress_index",
                 lambda d: d["avg_temp_c"] * d["avg_humidity_pct"] / 1000)
    _safe_assign(df, "humidity_temp_interaction",
                 lambda d: d["avg_humidity_pct"] * d["max_temp_c"] / 1000)

    # ═══════════════ NEW FEATURES ═══════════════
    # 9. Effective GHI / 13. Solar potential score — REMOVED (Phase 2).
    # Both are hand-built re-encodings of the physics label's inputs (GHI, temp):
    # effective_ghi = GHI * temp_derate, solar_potential_score = a 4-term average of
    # normalised GHI/DNI/temp/humidity. A model that picks them up is learning that
    # baked-in assumption (and the physics formula), not site signal — and both were
    # already collinear-dropped at |r|>0.95. Raw GHI/DNI/temp/humidity stay as inputs.

    # 10. Slope-aspect interaction
    _safe_assign(df, "slope_aspect_interaction",
                 lambda d: d["slope_deg"] * np.cos(np.radians(d["aspect_deg"])))

    # 11. Built-up + wasteland (urbanisation / barren land)
    if "builtup_pct" in df.columns and "wasteland_pct" in df.columns:
        _safe_assign(df, "builtup_wasteland_pct",
                     lambda d: d["builtup_pct"] + d["wasteland_pct"])

    # 12. Aridity index (rainfall vs temperature)
    _safe_assign(df, "aridity_index",
                 lambda d: d["annual_rainfall_mm"] / (d["avg_temp_c"] + 1))

    # 13. Solar potential score — see the Phase 2 note above: removed, not silently kept.

    # 14. Cloud cover penalty
    _safe_assign(df, "cloud_cover_penalty",
                 lambda d: 1 - d["avg_cloud_cover_pct"] / 100.0)

    # 15. Population pressure on land use
    if "census_pop_2024_projected" in df.columns and "district_area_sqkm" in df.columns:
        _safe_assign(df, "population_pressure",
                     lambda d: np.log1p(d["census_pop_2024_projected"] / d["district_area_sqkm"]))

    logger.info("Feature engineering complete. Total columns: %d", len(df.columns))
    return df