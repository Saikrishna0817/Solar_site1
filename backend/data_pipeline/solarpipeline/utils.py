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


# ═════════════════════════════════════════════════════════════
#  Centralised Pipeline Configuration
# ═════════════════════════════════════════════════════════════

class PipelineConfig:
    """All tunable constants used across the pipeline.  Override via env vars or kwargs."""

    # ── Data ──
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
    """
    t_cell = temp_c + 25.0
    pr = 0.80 - 0.0045 * max(0, t_cell - 25.0)
    pr = max(0.65, min(0.85, pr))
    return round(ghi * pr / 24.0, 4)
