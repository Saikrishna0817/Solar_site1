"""
MODIS AOD — using MODIS/061/MOD08_M3 collection.
This product includes Aerosol Optical Depth (AOD) at 550nm (Dark Target + Deep Blue).
"""
import ee
import pandas as pd
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
from utils.logging_helpers import get_logger

logger = get_logger(__name__)


def collect_modis_aod(centroids_csv, outdir, year=2023):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(centroids_csv)
    logger.info("Loaded %d districts for MODIS AOD", len(df))

    # MODIS M3 Monthly collection (includes AOD)
    # We'll use the mean AOD over 1 year
    modis = ee.ImageCollection("MODIS/061/MOD08_M3").select("Aerosol_Optical_Depth_Land_Ocean_Mean_Mean")
    mean_aod = modis.filterDate(f"{year}-01-01", f"{year}-12-31").mean()

    results = []
    for idx, row in df.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        district = row["district"]
        state = row["state"]

        try:
            # Small buffer for fast sampling
            buffer = ee.Geometry.Point([lon, lat]).buffer(500)  # 500m

            val = mean_aod.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=buffer,
                scale=1000,
                maxPixels=1e9
            ).get("Aerosol_Optical_Depth_Land_Ocean_Mean_Mean")

            if val is not None:
                raw = val.getInfo()
                val_float = round(raw, 4) if raw is not None else None
            else:
                val_float = None

        except Exception as e:
            logger.warning("MODIS error for %s: %s", district, e)
            val_float = None

        results.append({
            "district": district,
            "state": state,
            "latitude": lat,
            "longitude": lon,
            f"aod_{year}": val_float,
        })

        if (idx + 1) % 10 == 0:
            logger.info("[%d/%d] %s — AOD=%s", idx+1, len(df), district, val_float)

    out_df = pd.DataFrame(results)
    outpath = outdir / f"modis_aod_{year}_districts.csv"
    out_df.to_csv(outpath, index=False)
    logger.info("Saved MODIS AOD to %s", outpath)
    return out_df


if __name__ == "__main__":
    import ee
    from datasources.gee_helper import init_gee
    init_gee()
    collect_modis_aod(
        "/home/krishna/Desktop/Projects/AAC/Solar_site/backend/data_pipeline/outputs/raw/shapefiles/telangana_ap_districts_centroids_final.csv",
        "/home/krishna/Desktop/Projects/AAC/Solar_site/backend/data_pipeline/outputs/raw/gee_modis"
    )
