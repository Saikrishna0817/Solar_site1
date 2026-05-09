"""
SolarSite-India Data Pipeline — Boundary Shapefile Fetcher
Fetches district boundary shapefiles for Telangana and Andhra Pradesh
from GADM (Database of Global Administrative Areas).

Usage:
    python datasources/gadm_boundaries.py --states Telangana AndhraPradesh --outdir ./outputs/raw/shapefiles
"""
import argparse
import json
import logging
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from typing import List, Optional
import time

import geopandas as gpd
import requests

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
from config import settings
from utils.logging_helpers import get_logger

logger = get_logger(__name__)

# ─── Constants ────────────────────────────────────
GADM_BASE_URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_IND_shp.zip"
GADM_COUNTRY_LEVELS = {
    "states": "gadm41_IND_1.shp",  # State boundaries
    "districts": "gadm41_IND_2.shp",  # District boundaries
}
VALID_STATES = {"Telangana", "AndhraPradesh"}


def download_gadm_zip(output_dir: Path) -> Path:
    """
    Download the full GADM India shapefile archive.
    
    Args:
        output_dir: Directory to save the downloaded zip.
    
    Returns:
        Path to the downloaded zip file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / "gadm41_IND_shp.zip"

    if zip_path.exists():
        logger.info("GADM zip already exists at %s", zip_path)
        return zip_path

    logger.info("Downloading GADM India shapefile...")
    resp = requests.get(GADM_BASE_URL, stream=True, timeout=120)
    resp.raise_for_status()

    with open(zip_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    logger.info("Downloaded GADM zip to %s", zip_path)
    return zip_path


def extract_district_shapefile(zip_path: Path, output_dir: Path) -> Path:
    """
    Extract district-level shapefile from the GADM zip.
    
    Args:
        zip_path: Path to the GADM zip archive.
        output_dir: Directory to extract shapefile contents.
    
    Returns:
        Path to the extracted .shp file.
    """
    district_shp = None
    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()
        for member in names:
            z.extract(member, output_dir)
            if member.endswith("gadm41_IND_2.shp"):
                district_shp = output_dir / member

    if district_shp is None:
        raise RuntimeError("District shapefile (gadm41_IND_2.shp) not found in GADM zip.")

    logger.info("Extracted district shapefile to %s", district_shp)
    return district_shp


def filter_districts(shapefile_path: Path, states: List[str], output_dir: Path) -> Path:
    """
    Filter GADM district shapefile to selected states and save.
    
    Args:
        shapefile_path: Path to the full GADM district shapefile.
        states: List of state names to filter (e.g., ['Telangana', 'AndhraPradesh']).
        output_dir: Directory to write the filtered shapefile.
    
    Returns:
        Path to the filtered shapefile.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    gdf = gpd.read_file(shapefile_path)
    logger.info("Loaded %d districts from full India shapefile", len(gdf))

    # GADM uses various name fields; try common ones
    possible_name_fields = ["NAME_1", "VARNAME_1", "ENGTYPE_1", "name"]
    name_field = None
    for field in possible_name_fields:
        if field in gdf.columns:
            name_field = field
            break

    if name_field is None:
        raise ValueError(
            f"Could not find a suitable state name field. Available columns: {list(gdf.columns)}"
        )

    # Standardise state names for matching
    state_filter = [s.strip().replace(" ", "").title() for s in states]
    mask = gdf[name_field].str.strip().str.replace(" ", "").str.title().isin(state_filter)
    filtered = gdf[mask].copy()

    if filtered.empty:
        logger.warning("No districts matched for states %s. Returning empty GeoDataFrame.", states)
    else:
        logger.info("Filtered to %d districts for states %s", len(filtered), states)

    out_path = output_dir / "telangana_ap_districts.shp"
    filtered.to_file(out_path, driver="ESRI Shapefile")
    logger.info("Saved filtered shapefile to %s", out_path)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Fetch district boundary shapefiles for TS & AP")
    parser.add_argument(
        "--states",
        nargs="+",
        default=["Telangana", "AndhraPradesh"],
        help="Space-separated list of state names to filter",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("./outputs/raw/shapefiles"),
        help="Output directory for shapefiles",
    )
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Fetching district boundary shapefiles for: %s", ", ".join(args.states))
    logger.info("Output directory: %s", args.outdir.resolve())
    logger.info("=" * 60)

    try:
        zip_path = download_gadm_zip(args.outdir)
        shapefile_path = extract_district_shapefile(zip_path, args.outdir)
        out_path = filter_districts(shapefile_path, args.states, args.outdir)
        logger.info("SUCCESS: Filtered shapefile saved to %s", out_path)
    except Exception as e:
        logger.error("FAILED: %s", e)
        raise


if __name__ == "__main__":
    main()
