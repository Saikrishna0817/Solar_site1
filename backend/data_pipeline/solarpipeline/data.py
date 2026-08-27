"""
Data loading and merging module.
Reads validated source CSV files and merges them into a single district-level dataset.
"""

from typing import Any, Optional

import pandas as pd

from solarpipeline.utils import (
    RAW_DIR,
    SOURCE_SCHEMA,
    NASA_RENAMES,
    OSM_RENAMES,
    CENSUS_RENAMES,
    CONFIG,
    get_logger,
    normalize_district,
    safe_read_csv,
    compute_cuf_theoretical,
)

logger = get_logger(__name__)


def merge_sources() -> Optional[pd.DataFrame]:
    """Read, validate, and merge all 6 source datasets into one master DataFrame.

    Sources: NASA POWER, SRTM, OSM proximity, MODIS AOD, WorldCover, Census.
    Computes district-level CUF via :func:`compute_cuf_theoretical`.

    Returns
    -------
    pd.DataFrame or None
        Merged DataFrame with 60 rows (or None if any source fails).
    """
    logger.info("Phase 1: Building clean master dataset")

    # ── 1. NASA POWER ───────────────────────────────────────
    nasa = safe_read_csv(
        RAW_DIR / "nasa_power" / "nasa_power_districts.csv",
        "nasa", SOURCE_SCHEMA["nasa"], logger,
    )
    if nasa is None:
        return None
    nasa = nasa.rename(columns={
        "DISTRICT_NAME": "district", "STATE_NAME": "state",
        "LATITUDE": "latitude", "LONGITUDE": "longitude",
    })
    nasa["district"] = nasa["district"].apply(normalize_district)
    nasa = nasa.rename(columns=NASA_RENAMES)
    keep = ["district", "state", "latitude", "longitude"] + list(NASA_RENAMES.values())
    nasa = nasa[[c for c in keep if c in nasa.columns]]
    logger.info("NASA POWER: %d rows, %d cols", len(nasa), len(nasa.columns))

    # ── 2. SRTM ─────────────────────────────────────────────
    srtm = safe_read_csv(
        RAW_DIR / "gee_srtm" / "srtm_districts.csv",
        "srtm", SOURCE_SCHEMA["srtm"], logger,
    )
    if srtm is None:
        return None
    srtm["district"] = srtm["district"].apply(normalize_district)
    keep = ["district", "elevation_m", "slope_deg", "aspect_deg"]
    srtm = srtm[[c for c in keep if c in srtm.columns]]
    logger.info("SRTM: %d rows, %d cols", len(srtm), len(srtm.columns))

    # ── 3. OSM Proximity ────────────────────────────────────
    osm = safe_read_csv(
        RAW_DIR / "osm" / "osm_proximity_districts.csv",
        "osm", SOURCE_SCHEMA["osm"], logger,
    )
    if osm is None:
        return None
    osm["district"] = osm["district"].apply(normalize_district)
    osm = osm.rename(columns=OSM_RENAMES)
    keep = ["district", "dist_nearest_road_km", "dist_nearest_transmission_line_km",
            "dist_nearest_substation_km"]
    osm = osm[[c for c in keep if c in osm.columns]]
    logger.info("OSM: %d rows, %d cols", len(osm), len(osm.columns))

    # ── 4. MODIS AOD ────────────────────────────────────────
    aod = safe_read_csv(
        RAW_DIR / "gee_modis" / "modis_aod_2023_districts.csv",
        "aod", SOURCE_SCHEMA["aod"], logger,
    )
    if aod is None:
        return None
    aod["district"] = aod["district"].apply(normalize_district)
    # MOD08_M3 AOD is scaled x1000 -- divide to get true AOD
    aod["aod_2023"] = (aod["aod_2023"] / CONFIG.aod_scale_factor).round(4)
    keep = ["district", "aod_2023"]
    aod = aod[[c for c in keep if c in aod.columns]]
    logger.info("MODIS AOD: %d rows, %d cols  (scaled /1000)", len(aod), len(aod.columns))

    # ── 5. WorldCover ───────────────────────────────────────
    wc = safe_read_csv(
        RAW_DIR / "gee_worldcover" / "worldcover_districts.csv",
        "wc", SOURCE_SCHEMA["wc"], logger,
    )
    if wc is None:
        return None
    wc["district"] = wc["district"].apply(normalize_district)
    wc_cols = ["district"] + [c for c in wc.columns
                               if c not in ("district", "state", "latitude", "longitude")]
    wc = wc[wc_cols]
    logger.info("WorldCover: %d rows, %d cols", len(wc), len(wc.columns))

    # ── 6. Census ───────────────────────────────────────────
    census = safe_read_csv(
        RAW_DIR / "census_cea" / "census_districts.csv",
        "census", SOURCE_SCHEMA["census"], logger,
    )
    if census is None:
        return None
    census["district"] = census["district"].apply(normalize_district)
    census = census.rename(columns=CENSUS_RENAMES)

    # ── Census missing-data mitigation ──────────────────────
    # If pop_2011 is missing but projected pop_2024 exists, reverse-
    # project using the compound growth formula that generated pop_2024:
    #   pop_2024 = pop_2011 * (1 + r)^n  =>  pop_2011 = pop_2024 / (1 + r)^n
    if "census_pop_2011" in census.columns and "census_pop_2024_projected" in census.columns:
        missing_2011 = census["census_pop_2011"].isna() & census["census_pop_2024_projected"].notna()
        if missing_2011.any():
            factor = (1.01 ** 13)  # r=0.01, n=13 (2011->2024)
            census.loc[missing_2011, "census_pop_2011"] = (
                census.loc[missing_2011, "census_pop_2024_projected"] / factor
            ).round(0).astype(int)
            logger.info("Census: filled %d missing pop_2011 from pop_2024_projected "
                        "using reverse compound-growth (factor=%.4f)", missing_2011.sum(), factor)

    keep = ["district", "census_pop_2011", "census_pop_2024_projected",
            "district_area_sqkm", "population_density_per_sqkm", "source"]
    census = census[[c for c in keep if c in census.columns]]
    logger.info("Census: %d rows, %d cols", len(census), len(census.columns))

    # ── Merge ───────────────────────────────────────────────
    logger.info("Merging 6 sources ...")
    merged = nasa.copy()
    for right_df, label in [
        (srtm, "srtm"), (osm, "osm"), (aod, "modis"),
        (wc, "worldcover"), (census, "census"),
    ]:
        try:
            merged = merged.merge(right_df, on="district", how="outer")
        except Exception as exc:
            logger.error("Merge failure on %s: %s", label, exc)
            return None

    merged = merged.drop_duplicates(subset=["district"])
    merged = merged.dropna(how="all")

    # ── Merge quality diagnostics ───────────────────────────
    # Report districts present in NASA (base) but missing after outer-join.
    nasa_districts = set(nasa["district"])
    merged_districts = set(merged["district"])
    missing_after_merge = nasa_districts - merged_districts
    if missing_after_merge:
        logger.warning("Districts dropped during merge: %s", sorted(missing_after_merge))
    else:
        logger.info("All %d NASA districts preserved after merge.", len(nasa_districts))

    # Count how many districts have incomplete columns from each source.
    source_cols = {
        "nasa": [c for c in nasa.columns if c not in ("district", "state")],
        "srtm": [c for c in srtm.columns if c not in ("district",)],
        "osm": [c for c in osm.columns if c not in ("district",)],
        "aod": [c for c in aod.columns if c != "district"],
        "worldcover": [c for c in wc.columns if c != "district"],
        "census": [c for c in census.columns if c not in ("district", "source")],
    }
    for src_name, cols in source_cols.items():
        present = [c for c in cols if c in merged.columns]
        if not present:
            continue
        incomplete = merged[present].isna().any(axis=1).sum()
        if incomplete:
            logger.warning("Source '%s': %d/%d districts have missing columns.",
                           src_name, incomplete, len(merged))

    # ── Compute / Load CUF ──────────────────────────────────
    # Priority 1: Real plant CUF data (Option B — genuine ML target)
    # Priority 2: Physics formula (fallback for districts without plant data)
    real_cuf_path = (
        Path(__file__).resolve().parents[4] / "data" / "plant_cuf" / "solar_plants_india.csv"
    )
    if real_cuf_path.exists():
        logger.info("Loading real plant CUF data for ML training target ...")
        from solarpipeline.utils import load_real_cuf
        try:
            cuf_df = load_real_cuf(str(real_cuf_path))
            real_districts = set(cuf_df["district"])
            merged["cuf_real"] = None
            for idx, row in merged.iterrows():
                match = cuf_df[cuf_df["district"] == str(row.get("district", "")).strip().lower()]
                if not match.empty:
                    merged.at[idx, "cuf"] = match.iloc[0]["annual_cuf"]
                    merged.at[idx, "cuf_source"] = "cea_plant"
                else:
                    merged.at[idx, "cuf"] = compute_cuf_theoretical(
                        row["avg_ghi_kwh_m2_day"], row["avg_temp_c"]
                    )
                    merged.at[idx, "cuf_source"] = "physics"
            plant_count = (merged.get("cuf_source") == "cea_plant").sum()
            phys_count = (merged.get("cuf_source") == "physics").sum()
            logger.info("CUF source: %d real plants + %d physics-fallback (total %d)",
                        plant_count, phys_count, len(merged))
        except Exception as exc:
            logger.warning("Real CUF load failed: %s — falling back to physics formula", exc)
    else:
        logger.info("Real CUF dataset not found — using physics formula (fallback).")

    if "cuf" not in merged.columns or merged["cuf"].isna().all():
        if "avg_ghi_kwh_m2_day" in merged.columns and "avg_temp_c" in merged.columns:
            missing_solar = merged["avg_ghi_kwh_m2_day"].isna() | merged["avg_temp_c"].isna()
            if missing_solar.any():
                bad = merged.loc[missing_solar, "district"].tolist()
                logger.error("CUF input columns contain NaN for districts: %s", bad)
                return None
            merged["cuf"] = merged.apply(
                lambda r: compute_cuf_theoretical(r["avg_ghi_kwh_m2_day"], r["avg_temp_c"]),
                axis=1,
            )
        else:
            logger.error("Cannot compute CUF -- required columns missing.")
            return None

    if merged["cuf"].isna().any():
        bad = merged.loc[merged["cuf"].isna(), "district"].tolist()
        logger.error("Computed CUF is NaN for districts: %s", bad)
        return None
    logger.info("CUF: min=%.4f  max=%.4f  mean=%.4f",
                merged["cuf"].min(), merged["cuf"].max(), merged["cuf"].mean())

    logger.info("Merged dataset: %d rows x %d cols", len(merged), len(merged.columns))
    if len(merged) != CONFIG.expected_districts:
        logger.warning("Expected %d districts, got %d", CONFIG.expected_districts, len(merged))

    return merged