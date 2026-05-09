"""Merge all collected data sources into master dataset."""
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
from utils.logging_helpers import get_logger

logger = get_logger(__name__)

DATA_DIR = Path("/home/krishna/Desktop/Projects/AAC/Solar_site/backend/data_pipeline/outputs/raw")
MASTER_DIR = DATA_DIR.parent / "processed"
MASTER_DIR.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "nasa": DATA_DIR / "nasa_power" / "nasa_power_districts.csv",
    "srtm": DATA_DIR / "gee_srtm" / "srtm_districts.csv",
    "wc": DATA_DIR / "gee_worldcover" / "worldcover_districts.csv",
    "aod": DATA_DIR / "gee_modis" / "modis_aod_2023_districts.csv",
    "osm": DATA_DIR / "osm" / "osm_proximity_districts.csv",
    "census": DATA_DIR / "census_cea" / "census_districts.csv",
}

def normalize_key_cols(df, prefix):
    """Rename DISTRICT_NAME → district, STATE_NAME → state, prefix other cols."""
    rename = {}
    keep = set()
    for c in df.columns:
        low = c.lower().strip()
        if low in ("district_name", "district"):
            rename[c] = "district"
            keep.add("district")
        elif low in ("state_name", "state"):
            rename[c] = "state"
            keep.add("state")
    df = df.rename(columns=rename)
    # Normalize district names to use regular hyphens
    if "district" in df.columns:
        df["district"] = df["district"].str.replace("\u2013", "-").str.replace("\u2014", "-")
    # Prefix all non-key columns
    new_cols = {}
    for c in df.columns:
        if c not in ("district", "state"):
            new_cols[c] = f"{prefix}_{c}"
    df = df.rename(columns=new_cols)
    return df

def merge_all():
    dfs = []
    for prefix, path in SOURCES.items():
        if not path.exists():
            logger.warning("Missing: %s", path)
            continue
        df = pd.read_csv(path)
        df = normalize_key_cols(df, prefix)
        logger.info("%s: %d rows, %d cols", prefix, len(df), len(df.columns))
        dfs.append(df)

    # Merge sequentially on district, dropping duplicate state columns
    merged = dfs[0]
    for i, df in enumerate(dfs[1:], 1):
        if "state" in df.columns:
            df = df.drop(columns=["state"])
        merged = pd.merge(merged, df, on="district", how="outer")

    # Drop fully empty rows
    merged = merged.dropna(how="all")
    merged = merged.drop_duplicates(subset=["district"])

    cols = sorted(merged.columns.tolist(), key=lambda x: (x != "district", x != "state", x))
    merged = merged[cols]

    outpath = MASTER_DIR / "master_dataset.csv"
    merged.to_csv(outpath, index=False)
    logger.info("Saved %d rows × %d cols → %s", len(merged), len(merged.columns), outpath)
    return merged

if __name__ == "__main__":
    merge_all()