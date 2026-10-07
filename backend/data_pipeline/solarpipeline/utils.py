"""
Shared utilities for the SolarSite-India pipeline.
Logging setup, path resolution, column schema, safe I/O, physics-based CUF,
and a centralized configuration class for all tunable pipeline constants.
"""

import logging
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

# ── Path resolution ───────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[3]
DATA_PIPELINE_DIR = BASE_DIR / "backend" / "data_pipeline"
RAW_DIR = DATA_PIPELINE_DIR / "outputs" / "raw"
PROCESSED_DIR = DATA_PIPELINE_DIR / "outputs" / "processed"
REPORTS_DIR = DATA_PIPELINE_DIR / "outputs" / "reports"
for _dir in (PROCESSED_DIR, REPORTS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

LOG_FILE = PROCESSED_DIR / "solarpipeline.log"

# Blueprint E8: every stage writes a data card (rows, columns, NaN rates, source, date).
def write_data_card(df, name: str, extra: dict = None) -> None:
    """Write <name>.data_card.json next to pipeline outputs. Stdlib only."""
    import json

    card = {
        "artifact": name,
        "date": time.strftime("%Y-%m-%d"),
        "rows": len(df),
        "columns": list(df.columns),
        "nan_rates": {c: round(float(df[c].isna().mean()), 4) for c in df.columns},
        **(extra or {}),
    }
    with open(PROCESSED_DIR / f"{name}.data_card.json", "w") as fh:
        json.dump(card, fh, indent=2)

# Single source for the real-plant CUF dataset path (both merge + loader use this).
# ponytail: one constant, not per-callsite parents[N] math; add env override when paths vary by machine.
PLANT_CUF_CSV = BASE_DIR / "data" / "plant_cuf" / "solar_plants_india.csv"


# ═════════════════════════════════════════════════════════════
#  Centralised Pipeline Configuration
# ═════════════════════════════════════════════════════════════

class PipelineConfig:
    """All tunable constants used across the pipeline.  Override via env vars or kwargs."""

    # ── Data ──
    # Single source of truth for the district frame. Checked by data.py and the tests.
    # ponytail: 60 = TS 33 + AP 27; bump to 61 (AP 28) when Polavaram's centroid and
    # NASA POWER/SRTM/WorldCover rows land — add the row, then change this one number.
    expected_districts: int = 60
    census_growth_rate: float = 0.01  # 1% annual compound growth
    census_projection_years: int = 13  # 2011 -> 2024
    aod_scale_factor: float = 1000.0  # MODIS AOD is x1000 scaled

    # ── Feature engineering ──
    infra_road_weight: float = 0.4
    infra_grid_weight: float = 0.4
    infra_substation_weight: float = 0.2
    infra_weights_sum: float = 1.0
    forest_prox_scale: float = 100.0
    temp_coefficient: float = -0.0045

    # ── CUF computation ──
    cuf_pr_base: float = 0.80
    cuf_temp_offset: float = 25.0
    cuf_tcell_offset: float = 25.0  # T_module = T_amb + 25C
    cuf_pr_min: float = 0.65
    cuf_pr_max: float = 0.85
    cuf_denom: float = 24.0

    # ── Preprocessing ──
    test_size: float = 0.20
    random_state: int = 42
    skew_threshold: float = 3.0
    winsor_lower_q: float = 0.05
    winsor_upper_q: float = 0.95

    @property
    def census_compound_factor(self) -> float:
        """ (1 + growth_rate) ^ years, used for reverse-projection. """
        return (1 + self.census_growth_rate) ** self.census_projection_years


# Global singleton for easy access (env-var overrides could be added later)
CONFIG = PipelineConfig()


# ──────────────────────────────────────────────────────────────

def get_logger(name: str) -> logging.Logger:
    """Return a configured logger (file + console) shared across the package."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(module)s | %(message)s")
        fh = logging.FileHandler(LOG_FILE, mode="a")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.INFO)
        sh.setFormatter(fmt)
        logger.addHandler(fh)
        logger.addHandler(sh)
    return logger


# ── Column rename maps ──────────────────────────────────────
NASA_RENAMES = {
    "ALLSKY_SFC_SW_DWN": "avg_ghi_kwh_m2_day",
    "ALLSKY_SFC_SW_DNI": "avg_dni_kwh_m2_day",
    "ALLSKY_SFC_SW_DIFF": "avg_dhi_kwh_m2_day",
    "T2M": "avg_temp_c",
    "T2M_MAX": "max_temp_c",
    "WS10M": "avg_wind_speed_m_s",
    "RH2M": "avg_humidity_pct",
    "PRECTOTCORR": "annual_rainfall_mm",
    "CLOUD_AMT": "avg_cloud_cover_pct",
    "AOD_55": "aerosol_optical_depth",
}

OSM_RENAMES = {
    "dist_road_km": "dist_nearest_road_km",
    "dist_power_line_km": "dist_nearest_transmission_line_km",
    "dist_substation_km": "dist_nearest_substation_km",
}

CENSUS_RENAMES = {
    "population_density_per_sqkm": "population_density_per_sqkm",
    "area_sqkm": "district_area_sqkm",
    "pop_2011": "census_pop_2011",
    "pop_2024_projected": "census_pop_2024_projected",
}

# ── Source validation schemas ────────────────────────────────
SOURCE_SCHEMA = {
    "nasa":   ["DISTRICT_NAME", "STATE_NAME", "LATITUDE", "LONGITUDE",
                "ALLSKY_SFC_SW_DWN", "ALLSKY_SFC_SW_DNI", "ALLSKY_SFC_SW_DIFF",
                "T2M", "T2M_MAX", "WS10M", "RH2M", "PRECTOTCORR", "CLOUD_AMT", "AOD_55"],
    "srtm":   ["district", "state", "latitude", "longitude", "elevation_m", "slope_deg", "aspect_deg"],
    "osm":    ["district", "state", "latitude", "longitude",
                "dist_road_km", "dist_power_line_km", "dist_substation_km"],
    "aod":    ["district", "state", "latitude", "longitude", "aod_2023"],
    "wc":     ["district", "state", "latitude", "longitude",
                "tree_cover_pct", "shrubland_pct", "grassland_pct", "cropland_pct",
                "builtup_pct", "wasteland_pct", "water_pct", "wetland_pct"],
    "census": ["district", "state", "pop_2011", "pop_2024_projected",
                "area_sqkm", "population_density_per_sqkm", "source"],
}


# ── I/O helpers ─────────────────────────────────────────────

def normalize_district(name) -> Optional[str]:
    """Strip whitespace, lowercase, replace en/em dashes with hyphens."""
    if pd.isna(name):
        return None
    return str(name).strip().lower().replace("\u2013", "-").replace("\u2014", "-")


def safe_read_csv(filepath: Path, name: str, expected_cols: List[str], logger: logging.Logger) -> Optional[pd.DataFrame]:
    """Read and validate a CSV.  Returns None on any failure after logging an error."""
    if not filepath.exists():
        logger.error("File not found [%s]: %s", name, filepath)
        return None
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            logger.error("Empty CSV [%s]: %s", name, filepath)
            return None
        missing = [c for c in expected_cols if c not in df.columns]
        if missing:
            logger.error("Missing columns in %s: %s", name, missing)
            return None
        logger.debug("%s: %d rows x %d cols ok", name, len(df), len(df.columns))
        return df
    except Exception:
        logger.error("Failed reading %s: %s", name, traceback.format_exc())
        return None


def compute_cuf_theoretical(ghi: float, temp_c: float) -> float:
    """
    Theoretical CUF from GHI and ambient temperature.

    CUF = GHI x PR_effective / 24

    PR_effective  = 0.80 - 0.0045 * max(0, T_cell - 25)
    where T_cell = T_ambient + 25 (module temp under irradiance).

    Result clamped to [0.65, 0.85] before CUF computation.
    Reference: IEC 61724, typical c-Si temp coefficient.

    DEPRECATED: Use load_real_cuf() for training with actual plant CUF data.
    This physics formula produces near-deterministic CUF (R² > 0.99 with GHI).
    It is retained for fallback / inference on locations without real CUF data.
    """
    t_cell = temp_c + 25.0
    pr = 0.80 - 0.0045 * max(0, t_cell - 25.0)
    pr = max(0.65, min(0.85, pr))
    return round(ghi * pr / 24.0, 4)


def load_real_cuf(cuf_csv_path: str = None) -> "pd.DataFrame":
    """
    Load real solar plant CUF data for use as training target.

    Replaces the physics-derived CUF with actual plant-level CUF from
    CEA monthly generation reports. Returns a DataFrame with columns:
    plant_name, state, district, latitude, longitude, installed_capacity_mw,
    annual_cuf, annual_generation_mu.

    If no path is provided, looks for the default dataset at:
        data/plant_cuf/solar_plants_india.csv
    """
    if cuf_csv_path is None:
        cuf_csv_path = str(PLANT_CUF_CSV)
    cuf_path = Path(cuf_csv_path)
    if not cuf_path.exists():
        raise FileNotFoundError(
            f"Real CUF dataset not found at {cuf_path}. "
            "Run: python scripts/generate_plant_centroids.py first."
        )
    import pandas as pd

    cuf_df = pd.read_csv(cuf_path)
    cuf_df["district"] = cuf_df["district"].str.strip().str.lower()
    cuf_df["state"] = cuf_df["state"].str.strip()
    return cuf_df
