#!/usr/bin/env python3
"""
Mandal centroids for Telangana + Andhra Pradesh from GADM 4.1 level-3.
Stdlib only (json/csv/argparse) — runs without pandas/geopandas.

GADM 4.1 is pre-reorganization (TG 10 / AP 13 old districts); output keeps
`district_gadm` (old) for joins.
ponytail: new-district (60) assignment is one spatial join on the data machine
(geopandas available there) — not reimplemented here in stdlib.

Usage:
    python scripts/generate_mandal_centroids.py
    python scripts/generate_mandal_centroids.py --output <csv>
"""
import argparse
import csv
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GADM = PROJECT_ROOT / "data" / "external_fetch" / "mandal" / "gadm41_IND_3.json"
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "raw" / "shapefiles"
    / "telangana_ap_mandals_centroids.csv"
)

WANT_STATES = {"Telangana": "Telangana", "AndhraPradesh": "Andhra Pradesh"}


def _ring_centroid(ring):
    """Shoelace centroid of a linear ring; falls back to bbox center."""
    area2 = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        cross = x0 * y1 - x1 * y0
        area2 += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    if abs(area2) < 1e-12:
        xs = [p[0] for p in ring]
        ys = [p[1] for p in ring]
        return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return cx / (3 * area2), cy / (3 * area2)


def _feature_centroid(geom):
    """Centroid of the largest outer ring (Polygon/MultiPolygon)."""
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    best, best_area = None, -1.0
    for poly in polys:
        ring = poly[0]
        xs = [p[0] for p in ring]
        ys = [p[1] for p in ring]
        area = (max(xs) - min(xs)) * (max(ys) - min(ys))
        if area > best_area:
            best_area = area
            best = _ring_centroid(ring)
    return best[1], best[0]  # lat, lon


def main():
    parser = argparse.ArgumentParser(description="TG/AP mandal centroids from GADM L3")
    parser.add_argument("--gadm", type=str, default=str(DEFAULT_GADM))
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    with open(args.gadm) as f:
        features = json.load(f)["features"]

    rows, skipped = [], 0
    for feat in features:
        props = feat["properties"]
        if props.get("NAME_1") not in WANT_STATES:
            continue
        name = (props.get("NAME_3") or "").strip()
        if not name or name.lower().startswith("n.a."):
            skipped += 1
            continue
        lat, lon = _feature_centroid(feat["geometry"])
        rows.append({
            "mandal": name.lower(),
            "district_gadm": props.get("NAME_2", ""),
            "state": WANT_STATES[props["NAME_1"]],
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
        })

    rows.sort(key=lambda r: (r["state"], r["district_gadm"], r["mandal"]))
    outpath = Path(args.output)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with open(outpath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["mandal", "district_gadm", "state", "latitude", "longitude"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} mandal centroids to {outpath} (skipped {skipped} unnamed)")
    print("Next (data machine, geopandas): spatial-join to 60 new districts, then")
    print("  python main.py --step all --centroids <mandal csv>")


if __name__ == "__main__":
    main()
