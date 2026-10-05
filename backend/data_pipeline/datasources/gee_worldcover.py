"""
WorldCover via GEE — with getInfo() calls to extract actual numeric values.
"""
import ee
import pandas as pd
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
from utils.logging_helpers import get_logger

logger = get_logger(__name__)

LULC_CLASSES = {
    10: "tree_cover_pct",
    20: "shrubland_pct",
    30: "grassland_pct",
    40: "cropland_pct",
    50: "builtup_pct",
    60: "wasteland_pct",
    80: "water_pct",
    90: "wetland_pct",
}


def collect_worldcover(centroids_csv, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(centroids_csv)
    logger.info("Loaded %d districts", len(df))

    wc = ee.ImageCollection("ESA/WorldCover/v200").first().select("Map")

    results = []
    for idx, row in df.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        district = row["district"]
        state = row["state"]

        row_data = {"district": district, "state": state, "latitude": lat, "longitude": lon}

        try:
            buffer = ee.Geometry.Point([lon, lat]).buffer(2000)

            # Total pixel count
            total = wc.reduceRegion(
                reducer=ee.Reducer.count(),
                geometry=buffer,
                scale=10,
                maxPixels=1e9
            ).get("Map")

            total_val = total.getInfo() if total else 0

            for class_val, col_name in LULC_CLASSES.items():
                mask = wc.eq(class_val)
                count = mask.reduceRegion(
                    reducer=ee.Reducer.sum(),
                    geometry=buffer,
                    scale=10,
                    maxPixels=1e9
                ).get("Map")

                if count and total_val:
                    c = count.getInfo()
                    pct = round(c / total_val * 100, 2) if c and total_val else 0.0
                else:
                    pct = 0.0

                row_data[col_name] = pct

        except Exception as e:
            logger.warning("WC error for %s: %s", district, e)
            for col_name in LULC_CLASSES.values():
                row_data.setdefault(col_name, 0.0)

        results.append(row_data)

        if (idx + 1) % 10 == 0:
            vals = {k: v for k, v in row_data.items() if isinstance(v, float)}
            logger.info("[%d/%d] %s — %s", idx+1, len(df), district, vals)

    out_df = pd.DataFrame(results)
    outpath = outdir / "worldcover_districts.csv"
    out_df.to_csv(outpath, index=False)
    logger.info("Saved WorldCover to %s", outpath)
    return out_df


if __name__ == "__main__":
    from datasources.gee_helper import init_gee
    init_gee()
    root = Path(__file__).parent.parent
    collect_worldcover(
        root / "outputs" / "raw" / "shapefiles" / "telangana_ap_districts_centroids_final.csv",
        root / "outputs" / "raw" / "gee_worldcover"
    )