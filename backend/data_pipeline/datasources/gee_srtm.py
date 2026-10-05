"""
Collect SRTM DEM (Elevation, Slope, Aspect) via GEE for district centroids.
Uses reduceRegion with a 1km buffer around each centroid.
"""
import ee
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
from utils.logging_helpers import get_logger

logger = get_logger(__name__)


def collect_srtm(centroids_csv, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(centroids_csv)
    logger.info("Loaded %d district centroids", len(df))

    srtm = ee.Image("USGS/SRTMGL1_003")
    slope = ee.Terrain.slope(srtm)
    aspect = ee.Terrain.aspect(srtm)

    results = []
    for idx, row in df.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        district = row["district"]
        state = row["state"]

        try:
            # Using a 500m buffer around centroid for robust sampling
            buffer = ee.Geometry.Point([lon, lat]).buffer(500)

            elev_region = srtm.reduceRegion(
                reducer=ee.Reducer.median(),
                geometry=buffer,
                scale=30,
                maxPixels=1e9
            )
            slope_region = slope.reduceRegion(
                reducer=ee.Reducer.median(),
                geometry=buffer,
                scale=30,
                maxPixels=1e9
            )
            aspect_region = aspect.reduceRegion(
                reducer=ee.Reducer.median(),
                geometry=buffer,
                scale=30,
                maxPixels=1e9
            )

            elev = elev_region.getInfo().get("elevation")
            slp = slope_region.getInfo().get("slope")
            asp = aspect_region.getInfo().get("aspect")

        except Exception as e:
            logger.error("SRTM error for %s: %s", district, e)
            elev, slp, asp = None, None, None

        results.append({
            "district": district,
            "state": state,
            "latitude": lat,
            "longitude": lon,
            "elevation_m": round(elev, 1) if elev is not None else None,
            "slope_deg": round(slp, 2) if slp is not None else None,
            "aspect_deg": round(asp, 1) if asp is not None else None,
        })

        logger.info("[%d/%d] %s — elev=%s slope=%s aspect=%s",
                     idx+1, len(df), district,
                     results[-1]["elevation_m"],
                     results[-1]["slope_deg"],
                     results[-1]["aspect_deg"])

    out_df = pd.DataFrame(results)
    outpath = outdir / "srtm_districts.csv"
    out_df.to_csv(outpath, index=False)
    logger.info("Saved SRTM to %s", outpath)
    return out_df


if __name__ == "__main__":
    from datasources.gee_helper import init_gee
    init_gee()
    root = Path(__file__).parent.parent
    collect_srtm(
        root / "outputs" / "raw" / "shapefiles" / "telangana_ap_districts_centroids_final.csv",
        root / "outputs" / "raw" / "gee_srtm"
    )