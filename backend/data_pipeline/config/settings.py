"""
SolarSite-India Data Pipeline Configuration
MC: Project-wide directory layout, API keys, GEE credentials,
     and feature-to-dataset mapping.
"""
import os
from pathlib import Path

# ─── Resolve project root relative to this file ───────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Sub-directories
RAW_DIR = BASE_DIR / "backend" / "data_pipeline" / "outputs" / "raw"
PROCESSED_DIR = BASE_DIR / "backend" / "data_pipeline" / "outputs" / "processed"
REPORTS_DIR = BASE_DIR / "backend" / "data_pipeline" / "outputs" / "reports"

# Create dirs if missing (safe guard-rails)
for d in (RAW_DIR, PROCESSED_DIR, REPORTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ─── Data Sources ──────────────────────────────────────────────────
DISTRICTS = {
    "Telangana": 33,  # 33 districts
    "AndhraPradesh": 13,  # 26 districts in real, using 13 for pilot
}

# ─── API / Service Config ────────────────────────────────────────
NASA_POWER_BASE = "https://power.larc.nasa.gov/api/temporal/climatology/point"
NASA_POWER_TIMEOUT = 60  # seconds
NASA_POWER_MAX_RETRIES = 3
NASA_POWER_RETRY_DELAY = 2  # seconds between retries

OSM_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OSM_TIMEOUT = 120

# ─── GEE ───────────────────────────────────────────────────────
GEE_PROJECT_ID = os.getenv("GEE_PROJECT_ID", "solar-site-495511")

GEE_COLLECTIONS = {
    "srtm": "USGS/SRTMGL1_003",
    "worldcover": "ESA/WorldCover/v200",
    "modis_aod": "MODIS/061/MOD08_M3",
    # Add AlphaEarth or other custom collections here as needed
}

GEE_SCALE = {
    "srtm": 30,    # 30m native
    "worldcover": 10,  # 10m
    "modis_aod": 1000,  # 1km
}

# ─── Feature Mapping (source → required variables) ───────────────
FEATURES = {
    "NASA_POWER": [
        "ALLSKY_SFC_SW_DWN",  # GHI
        "ALLSKY_SFC_SW_DNI",  # DNI
        "ALLSKY_SFC_SW_DIFF", # DHI
        "CLOUD_AMT",            # Cloud Cover
        "T2M",                  # Temperature
        "T2M_MAX",
        "WS10M",                # Wind Speed
        "RH2M",                 # Humidity
        "PRECTOTCORR",          # Rainfall
        "AOD_55",               # Optical Depth
    ],
    "GEE_SRTM": ["elevation", "slope", "aspect"],
    "GEE_WORLDCOVER": ["land_use", "wasteland_pct", "forest_proximity"],
    "GEE_MODIS": ["aerosol_optical_depth"],
    "OSM": ["road_distance", "grid_distance", "substation_distance"],
    "CENSUS": ["population_density"],
    "CEA": ["cuf", "installed_capacity_mw"],
}

# ─── Output Schema ───────────────────────────────────────────────
OUTPUT_COLUMNS = [
    "district_name",
    "state",
    "latitude",
    "longitude",
    # Solar
    "avg_ghi_kwh_m2_day",
    "avg_dni_kwh_m2_day",
    "avg_dhi_kwh_m2_day",
    # Climate
    "avg_temp_c",
    "max_temp_c",
    "avg_wind_speed_m_s",
    "avg_humidity_pct",
    "annual_rainfall_mm",
    "avg_cloud_cover_pct",
    "aerosol_optical_depth",
    # Terrain
    "elevation_m",
    "slope_deg",
    "aspect_deg",
    # Land
    "dominant_land_use",
    "wasteland_pct",
    "forest_proximity_km",
    # Infrastructure
    "dist_nearest_road_km",
    "dist_nearest_transmission_line_km",
    "dist_nearest_substation_km",
    # Socioeconomic
    "population_density_per_sqkm",
    # Target
    "capacity_utilization_factor",
    "installed_solar_capacity_mw",
]
