"""
SolarSite-India — NASA POWER data collector (v2, corrected key parsing)
Corrects the original bug where numeric month keys '01'..'12','13' were
used instead of NASA's three-letter abbreviations 'JAN'..'DEC','ANN'.
"""
import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Optional

import geopandas as gpd
import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
from utils.logging_helpers import get_logger

logger = get_logger(__name__)

# ─── Config ─────────────────────────────────────────────────────
NASA_CLIMATOLOGY_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
NASA_TIMEOUT = 60
NASA_RETRIES = 3
NASA_RETRY_DELAY = 2

PARAMETERS = [
    "ALLSKY_SFC_SW_DWN",   # GHI (kWh/m²/day)
    "ALLSKY_SFC_SW_DNI",   # DNI (kWh/m²/day)
    "ALLSKY_SFC_SW_DIFF", # DHI (kWh/m²/day)
    "CLOUD_AMT",            # Cloud cover (%)
    "T2M",                  # Temperature (°C)
    "T2M_MAX",             # Max temperature (°C)
    "WS10M",                # Wind speed at 10m (m/s)
    "RH2M",                 # Relative humidity (%)
    "PRECTOTCORR",         # Precipitation (mm/day)
    "AOD_55",              # Aerosol optical depth (unitless)
]
PARAMS_STR = ",".join(PARAMETERS)
MONTH_KEYS = ["JAN","FEB","MAR","APR","MAY","JUN",
              "JUL","AUG","SEP","OCT","NOV","DEC"]


def fetch_nasa_climatology(lat: float, lon: float) -> Optional[pd.DataFrame]:
    """
    Fetch climatological monthly means from NASA POWER for a single point.
    Uses three-letter abbreviations: JAN..DEC and ANN for annual.
    """
    params = {
        "parameters": PARAMS_STR,
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "format": "JSON",
        "header": "false",
    }

    data = None
    for attempt in range(1, NASA_RETRIES + 1):
        try:
            resp = requests.get(NASA_CLIMATOLOGY_URL, params=params, timeout=NASA_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            break
        except requests.exceptions.RequestException as exc:
            logger.error("NASA POWER error (attempt %d/%d): %s", attempt, NASA_RETRIES, exc)
            time.sleep(NASA_RETRY_DELAY * attempt)
    if data is None:
        return None

    properties = data.get("properties", {}).get("parameter", {})
    if not properties:
        logger.error("No 'properties.parameter' in NASA POWER response.")
        return None

    rows = []
    # Monthly rows (1..12)
    for i, key in enumerate(MONTH_KEYS, start=1):
        row = {"MONTH": i}
        for param in PARAMETERS:
            row[param] = properties.get(param, {}).get(key)
        rows.append(row)
    # Annual summary
    annual = {"MONTH": 13}
    for param in PARAMETERS:
        annual[param] = properties.get(param, {}).get("ANN")
    rows.append(annual)
    return pd.DataFrame(rows)


def collect_nasa_power(input_file, output_dir, save_inter=True, input_type="auto"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine input type if auto
    if input_type == "auto":
        if str(input_file).lower().endswith(".csv"):
            input_type = "csv"
        else:
            input_type = "shapefile"

    # Read input file
    if input_type == "csv":
        df_in = pd.read_csv(input_file)
        # Assume columns: district, state, latitude, longitude
        district_col = "district"
        state_col = "state"
        lat_col = "latitude"
        lon_col = "longitude"
    else:
        gdf = gpd.read_file(input_file)
        district_col = next((c for c in gdf.columns if "name" in c.lower() or "district" in c.lower()), None)
        state_col = "state"
        lat_col = "LATITUDE"
        lon_col = "LONGITUDE"
        gdf[lat_col] = gdf.geometry.centroid.y
        gdf[lon_col] = gdf.geometry.centroid.x
        df_in = gdf

    results = []
    for idx, row in df_in.iterrows():
        district = row.get(district_col, "Unknown")
        state = row.get(state_col, "Unknown")
        lat = row.get(lat_col, 0)
        lon = row.get(lon_col, 0)
        logger.info("[%d/%d] Fetching %s, %s (%.4f, %.4f)", idx+1, len(df_in), district, state, lat, lon)

        clim_df = fetch_nasa_climatology(lat, lon)
        if clim_df is None or clim_df.empty:
            logger.warning("No data for %s", district)
            continue

        if save_inter:
            inter = output_dir / "intermediate" / "nasa_power"
            inter.mkdir(parents=True, exist_ok=True)
            clim_df.to_csv(inter / f"{district.replace(' ', '_')}_nasa_power.csv", index=False)

        annual = clim_df[clim_df["MONTH"] == 13].iloc[0].to_dict()
        annual["DISTRICT_NAME"] = district
        annual["STATE_NAME"] = state
        annual["LATITUDE"] = lat
        annual["LONGITUDE"] = lon
        results.append(annual)

    final = pd.DataFrame(results)
    if "MONTH" in final.columns:
        final.drop(columns=["MONTH"], inplace=True)
    first = ["DISTRICT_NAME", "STATE_NAME", "LATITUDE", "LONGITUDE"]
    final = final[[c for c in first if c in final.columns] + [c for c in final.columns if c not in first]]

    out_csv = output_dir / "nasa_power_districts.csv"
    final.to_csv(out_csv, index=False)
    logger.info("Saved NASA POWER data to %s (%d districts)", out_csv, len(final))
    return final


def main():
    parser = argparse.ArgumentParser(description="Collect NASA POWER data for district centroids")
    parser.add_argument("--shapefile", type=Path, default="./outputs/raw/shapefiles/telangana_ap_districts.shp")
    parser.add_argument("--outdir", type=Path, default="./outputs/raw/nasa_power")
    args = parser.parse_args()

    collect_nasa_power(args.shapefile, args.outdir, save_inter=True)
    logger.info("Complete.")


if __name__ == "__main__":
    main()
