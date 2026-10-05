"""
Collect AlphaEarth Foundations Satellite Embeddings via GEE for district centroids.
GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL — 64 bands (A00..A63), 10 m, CC-BY-4.0
("produced by Google and Google DeepMind"). Mean over 500 m buffer, one
reduceRegion call for all bands. Same shape as gee_srtm.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
from datasources.gee_helper import gee_retry, init_gee  # noqa: E402
from utils.logging_helpers import get_logger  # noqa: E402

logger = get_logger(__name__)

COLLECTION = "GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL"
EMBEDDING_YEAR = 2024  # ponytail: single pinned year; annual refresh when change detection is wanted.


@gee_retry(max_attempts=3)
def _sample_point(image, lon, lat):
    import ee
    return image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=ee.Geometry.Point([lon, lat]).buffer(500),
        scale=10,
        maxPixels=1e9,
    ).getInfo()


def collect_alphaearth(centroids_csv, outdir, year=EMBEDDING_YEAR):
    import pandas as pd

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(centroids_csv)
    logger.info("Loaded %d centroids", len(df))

    import ee
    image = ee.ImageCollection(COLLECTION).filterDate(f"{year}-01-01", f"{year + 1}-01-01").first()
    bands = image.bandNames().getInfo()
    logger.info("AEF %d: %d bands", year, len(bands))

    results = []
    for idx, row in df.iterrows():
        try:
            vals = _sample_point(image, row["longitude"], row["latitude"])
            emb = {b.lower(): round(vals[b], 4) if vals.get(b) is not None else None for b in bands}
        except Exception as exc:
            logger.error("AEF error for %s: %s", row["district"], exc)
            emb = {b.lower(): None for b in bands}
        results.append({
            "district": row["district"], "state": row["state"],
            "latitude": row["latitude"], "longitude": row["longitude"], **emb,
        })
        logger.info("[%d/%d] %s — %d bands sampled", idx + 1, len(df), row["district"], len(bands))

    out_df = pd.DataFrame(results)
    outpath = outdir / "aef_districts.csv"
    out_df.to_csv(outpath, index=False)
    logger.info("Saved AlphaEarth to %s", outpath)
    return out_df


if __name__ == "__main__":
    root = Path(__file__).parent.parent.absolute()
    if init_gee():
        collect_alphaearth(
            root / "outputs" / "raw" / "shapefiles" / "telangana_ap_districts_centroids_final.csv",
            root / "outputs" / "raw" / "aef",
        )
