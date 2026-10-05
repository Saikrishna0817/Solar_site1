"""
SolarSite-India — geoBoundaries district filter for Telangana & AP
Downloads the 2021 geoBoundaries dataset, uses bounding boxes
to isolate Telangana & Andhra Pradesh districts.
"""
import requests
from io import BytesIO
from pathlib import Path
import geopandas as gpd

# ─── Config ───────────────────────────────────────────────────
URL = ("https://github.com/wmgeolab/geoBoundaries/raw/9469f09/"
       "releaseData/gbOpen/IND/ADM2/geoBoundaries-IND-ADM2_simplified.geojson")

# Bounding boxes (approx) for filtering by centroid
BOUNDS = {
    "Telangana":        {"minx": 76.5, "maxx": 81.5, "miny": 15.0, "maxy": 20.0},
    "AndhraPradesh":   {"minx": 76.5, "maxx": 85.0, "miny": 12.0, "maxy": 19.5},
}

# ─── Script ────────────────────────────────────────────────────

def download_and_filter():
    outdir = Path(__file__).parent.parent / "outputs" / "raw" / "shapefiles"
    outdir.mkdir(parents=True, exist_ok=True)

    print("Downloading geoBoundaries India ADM2 (735 districts)...")
    resp = requests.get(URL, timeout=120)
    gdf = gpd.read_file(BytesIO(resp.content))
    print(f"Downloaded {len(gdf)} districts")

    # Compute centroids in the same CRS (EPSG:4326 by default)
    gdf["centroid"] = gdf.geometry.centroid
    gdf["lon"] = gdf["centroid"].x
    gdf["lat"] = gdf["centroid"].y

    # Collect districts by bounding box
    results = []
    for state_name, bbox in BOUNDS.items():
        mask = (
            (gdf["lon"] >= bbox["minx"]) &
            (gdf["lon"] <= bbox["maxx"]) &
            (gdf["lat"] >= bbox["miny"]) &
            (gdf["lat"] <= bbox["maxy"])
        )
        subset = gdf[mask].copy()
        subset["assigned_state"] = state_name
        results.append(subset)
        print(f"  {state_name}: {len(subset)} districts")

    combined = gpd.GeoDataFrame(gpd.pd.concat(results, ignore_index=True))
    print(f"\nTotal districts matched: {len(combined)}")
    print(f"Unique names: {len(combined['shapeName'].unique())}")

    # Save
    combined_out = outdir / "telangana_ap_districts_geboundaries.shp"
    combined.to_file(combined_out, driver="ESRI Shapefile")
    print(f"Saved to {combined_out}")
    print("\nDistricts found:")
    print(combined[["shapeName", "assigned_state"]].sort_values(["assigned_state", "shapeName"]).to_string(index=False))


if __name__ == "__main__":
    download_and_filter()
