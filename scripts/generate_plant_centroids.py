#!/usr/bin/env python3
"""
Generate centroids CSV from the solar_plants_india.csv dataset.
Used to run the data pipeline for real plant locations instead of district centroids.

Usage:
    python scripts/generate_plant_centroids.py
    python scripts/generate_plant_centroids.py --output data/plant_centroids.csv
"""
import argparse
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLANTS = PROJECT_ROOT / "data" / "plant_cuf" / "solar_plants_india.csv"
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "raw" / "shapefiles"
    / "solar_plant_centroids.csv"
)


def main():
    parser = argparse.ArgumentParser(description="Generate plant centroids CSV")
    parser.add_argument("--plants", type=str, default=str(DEFAULT_PLANTS))
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    plants_df = pd.read_csv(args.plants)
    print(f"Loaded {len(plants_df)} plants from {args.plants}")

    centroids = pd.DataFrame({
        "district": plants_df["plant_name"].str.strip().str.lower(),
        "state": plants_df["state"],
        "latitude": plants_df["latitude"],
        "longitude": plants_df["longitude"],
    })

    outpath = Path(args.output)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    centroids.to_csv(outpath, index=False)
    print(f"Saved {len(centroids)} plant centroids to {outpath}")
    print("\nNext: Run the data pipeline on these centroids:")
    print(f"  cd backend/data_pipeline")
    print(f"  python main.py --step all --centroids {outpath}")
    print(f"  python phase2_3_pipeline.py --step all")


if __name__ == "__main__":
    main()