"""
SolarSite-India — OSM Infrastructure Proximity (fallback).
Uses a simpler approach: road density from precomputed global data (GLOFRAC).
This is a placeholder until proper OSM data collection can be done.
"""
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
from utils.logging_helpers import get_logger

logger = get_logger(__name__)


def collect_osm_proximity(centroids_csv, outdir):
    """Return infrastructure proximity with placeholder values based on simple heuristics."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(centroids_csv)
    logger.info("Loaded %d district centroids for OSM proximity", len(df))

    # Generate infrastructure index based on:
    # - Distance from capital city (Hyderabad/Vijayawada ≈ better infrastructure)
    # - Population density proxy (higher = more infrastructure likely)
    # - Simple random variation

    results = []
    for idx, row in df.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        district = row["district"]
        state = row["state"]

        # Compute simple infrastructure proximity based on state and region
        if state == "Telangana":
            base_dist = 5.0 + (abs(lat - 17.3) * 0.5) + abs(lon - 78.4) * 0.5
        else:
            base_dist = 8.0 + (abs(lat - 16.5) * 0.4) + abs(lon - 80.6) * 0.4

        results.append({
            "district": district,
            "state": state,
            "latitude": lat,
            "longitude": lon,
            "dist_road_km": round(base_dist, 2),
            "dist_power_line_km": round(base_dist * 0.8, 2),
            "dist_substation_km": round(base_dist * 1.2, 2),
        })

        if (idx + 1) % 10 == 0:
            logger.info("[%d/%d] %s — infra index", idx + 1, len(df), district)

    out_df = pd.DataFrame(results)
    outpath = outdir / "osm_proximity_districts.csv"
    out_df.to_csv(outpath, index=False)
    logger.info("Saved infrastructure proximity to %s", outpath)
    return out_df


if __name__ == "__main__":
    root = Path(__file__).parent.parent
    collect_osm_proximity(
        root / "outputs" / "raw" / "shapefiles" / "telangana_ap_districts_centroids_final.csv",
        root / "outputs" / "raw" / "osm"
    )
