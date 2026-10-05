"""
SolarSite-India — OSM Infrastructure Proximity Collector
Fetches distance to nearest road, HV transmission line, and substation
for each district centroid.
"""
import argparse, time, sys
from pathlib import Path
from typing import Tuple, List

import geopandas as gpd
import osmnx as ox
import pandas as pd
import numpy as np
from scipy.spatial import KDTree

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
from utils.logging_helpers import get_logger

logger = get_logger(__name__)

# ─── Constants ───────────────────────────────────────────────────
DOWNLOAD_TIMEOUT = 180
SEARCH_RADIUS_DEG = 0.5   # initial search radius in degrees for osmnx


def get_district_centroids(shp: Path) -> pd.DataFrame:
    gdf = gpd.read_file(shp)
    gdf["lat"] = gdf.geometry.centroid.y
    gdf["lon"] = gdf.geometry.centroid.x
    name_col = next((c for c in gdf.columns if "shapeName" in c or "name" in c.lower()), "NAME_2")
    state_col = next((c for c in gdf.columns if "assigned_state" in c or "state" in c.lower()), "NAME_1")
    return pd.DataFrame({"district": gdf[name_col], "state": gdf.get(state_col, "Unknown"),
                          "lat": gdf["lat"], "lon": gdf["lon"]})


def fetch_osm_infrastructure(north, south, east, west) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Download roads, power lines, and substations from OSM.
    Returns three GeoDataFrames: roads, power_lines, substations.
    """
    # 1. Roads (function roads only)
    logger.info("    → OSM: downloading roads...")
    roads = ox.geometries.geometries_from_bbox(north, south, east, west,
                                               tags={"highway": ["primary", "secondary", "trunk", "motorway"]})
    # 2. HV Power lines
    logger.info("    → OSM: downloading power lines...")
    power_lines = ox.geometries.geometries_from_bbox(north, south, east, west,
                                                        tags={"power": "line", "voltage": True})
    # 3. Substations
    logger.info("    → OSM: downloading substations...")
    substations = ox.geometries.geometries_from_bbox(north, south, east, west,
                                                      tags={"power": "substation"})

    return roads[["geometry"]], power_lines[["geometry"]], substations[["geometry"]]


def compute_proximities(df: pd.DataFrame, roads: gpd.GeoDataFrame,
                       power_lines: gpd.GeoDataFrame, substations: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Compute min distance (km) from each district centroid to each infrastructure type.
    """
    from pyproj import Transformer
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32644", always_xy=True)  # UTM 44 for TS+AP

    def to_utm(x, y):
        return transformer.transform(x, y)

    # Reproject everything
    for gdf, label in [(roads, "roads"), (power_lines, "power"), (substations, "sub")]:
        gdf["x_utm"], gdf["y_utm"] = to_utm(gdf.geometry.centroid.x.values, gdf.geometry.centroid.y.values)

    # District centroids
    df["x_utm"], df["y_utm"] = to_utm(df["lon"].values, df["lat"].values)

    # Build KD-trees for fast nearest-neighbor
    def min_dist_kdtree(points: np.ndarray, tree_points: np.ndarray) -> float:
        tree = KDTree(tree_points)
        dists, _ = tree.query(points, k=1)
        return dists[0] / 1000  # convert m → km

    results = df.copy()
    # Column names match SOURCE_SCHEMA["osm"] so merge_sources + OSM_RENAMES work unchanged.
    for infra_name, infra_df in [("road", roads), ("power_line", power_lines), ("substation", substations)]:
        infra_pts = np.column_stack([infra_df["x_utm"].values, infra_df["y_utm"].values])
        tree = KDTree(infra_pts)
        district_pts = np.column_stack([results["x_utm"].values, results["y_utm"].values])
        dists, _ = tree.query(district_pts, k=1)
        results[f"dist_{infra_name}_km"] = (dists / 1000).round(3)

    return results[["district", "state", "lat", "lon",
                     "dist_road_km", "dist_power_line_km", "dist_substation_km"]]


def collect_osm_proximity(shapefile_path: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    df = get_district_centroids(shapefile_path)
    logger.info("OSM Infrastructure Proximity — %d districts", len(df))

    # Get overall bounding box for the states
    buffer = 0.5
    north = df["lat"].max() + buffer
    south = df["lat"].min() - buffer
    east = df["lon"].max() + buffer
    west = df["lon"].min() - buffer

    logger.info("Bounding box: N=%.2f, S=%.2f, E=%.2f, W=%.2f", north, south, east, west)

    roads, power, subs = fetch_osm_infrastructure(north, south, east, west)
    result = compute_proximities(df, roads, power, subs)
    out_csv = output_dir / "osm_infrastructure_proximity.csv"
    result.to_csv(out_csv, index=False)
    logger.info("Saved OSM proximity data for %d districts to %s", len(result), out_csv)


def main():
    parser = argparse.ArgumentParser(description="Collect OSM infrastructure proximity data")
    parser.add_argument("--shapefile", type=Path, default="./outputs/raw/shapefiles/telangana_ap_districts.shp")
    parser.add_argument("--outdir", type=Path, default="./outputs/raw/osm")
    args = parser.parse_args()
    collect_osm_proximity(args.shapefile, args.outdir)


if __name__ == "__main__":
    main()
