#!/usr/bin/env python3
"""
Build the Telangana + Andhra Pradesh district choropleth for the frontend map.

Reads GADM 4.1 level-2 (district) boundaries for India, keeps only Telangana and
Andhra Pradesh, canonicalises district names through the pipeline's
DISTRICT_ALIASES / canonical_district() so frontend joins meet the data frame,
simplifies geometry, and writes frontend/public/data/tg_ap_districts.geojson
with each feature carrying properties `district` (canonical, lowercase) and
`state` (display name).

Usage:
    .venv/bin/python scripts/build_district_geojson.py

Output size target: < ~700 KB (simplified at 0.01 deg ~ 1.1 km).

ponytail: GADM 4.1 ADM2 predates the 2016/2022 reorgs, so this yields the
23 old districts (TG 10 + AP 13), not the project's 60-district post-reorg
frame — the count is printed below so the gap stays visible. Upgrade path:
dissolve gadm41_IND_3 mandals through the district_new crosswalk written by
scripts/assign_mandal_new_districts.py once its ~6 name variants
(Hanamkonda/Hanumakonda, Nagarukurnool/Nagarkurnool, Ranga Reddy, Medchal
en-dash, Sri Potti Sriramulu) are reconciled against the 60-district frame —
Mahbubnagar has no mandals assigned yet, so its polygon would be a hole.
"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GADM_ADM2 = PROJECT_ROOT / "data" / "external_fetch" / "mandal" / "gadm41_IND_2.json"
OUT_PATH = PROJECT_ROOT / "frontend" / "public" / "data" / "tg_ap_districts.geojson"

WANT_STATES = {
    "Telangana": "Telangana",
    "AndhraPradesh": "Andhra Pradesh",
}

SIMPLIFY_DEG = 0.01          # ~1.1 km tolerance
MIN_PART_AREA_DEG2 = 1e-4    # drop polygon parts smaller than ~1.2 km²
COORD_DECIMALS = 4           # ~11 m — no point keeping precision below simplify()

# GADM spells a few districts without spaces / abbreviated, so they miss
# DISTRICT_ALIASES (which keys on the pipeline's own spellings). Applied before
# canonical_district(), which then runs its own reorg aliases.
# ponytail: 4 hand-checked GADM spellings; upgrade path = a real GADM↔60-frame
# name crosswalk table in data/ once the ADM3 dissolve (see module docstring) lands.
GADM_SPELLINGS = {
    "rangareddy": "ranga reddy",
    "eastgodavari": "east godavari",
    "westgodavari": "west godavari",
    "y.s.r.": "kadapa",      # canonical_district() maps kadapa -> ysr kadapa
}


def _import_pipeline_district_api():
    """Import canonical_district/DISTRICT_ALIASES from the backend package."""
    sys.path.insert(0, str(PROJECT_ROOT / "backend" / "data_pipeline"))
    from solarpipeline.utils import DISTRICT_ALIASES, canonical_district  # noqa: F401
    return DISTRICT_ALIASES, canonical_district


def district_key(name, canonical_district):
    """canonical_district() + GADM-only spellings, so geojson keys == frame keys."""
    n = canonical_district(name)
    n = GADM_SPELLINGS.get(n, n)
    return canonical_district(n)


def _ring_area(ring):
    area2 = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        area2 += x0 * y1 - x1 * y0
    return abs(area2) / 2


def clean_geometry(geom, simplify_deg=SIMPLIFY_DEG):
    """Simplify + drop tiny parts/rings. Returns None if nothing usable remains."""
    from shapely.geometry import MultiPolygon, Polygon

    if not geom.is_valid:
        geom = geom.buffer(0)
    geom = geom.simplify(simplify_deg, preserve_topology=True)

    parts = list(getattr(geom, "geoms", [geom]))
    kept = []
    for part in parts:
        if not isinstance(part, (Polygon, MultiPolygon)) or part.is_empty:
            continue
        if part.area < MIN_PART_AREA_DEG2:
            continue
        if isinstance(part, Polygon):
            holes = [h for h in part.interiors if _ring_area(list(h.coords)) >= MIN_PART_AREA_DEG2]
            kept.append(Polygon(part.exterior.coords, holes))
        else:
            kept.append(part)
    if not kept:
        return None
    return kept[0] if len(kept) == 1 else MultiPolygon(kept)


def _round_coords(obj, ndigits=COORD_DECIMALS):
    if isinstance(obj[0], (int, float)):
        return [round(obj[0], ndigits), round(obj[1], ndigits)]
    return [_round_coords(o, ndigits) for o in obj]


def main():
    if not GADM_ADM2.exists():
        print(
            f"SKIP: GADM district boundaries not found at\n"
            f"  {GADM_ADM2}\n"
            f"Download gadm41_IND_2.json into data/external_fetch/mandal/ and re-run.\n"
            f"Nothing written; exiting 0."
        )
        return 0

    from shapely.geometry import mapping, shape

    _, canonical_district = _import_pipeline_district_api()

    with open(GADM_ADM2, encoding="utf-8") as fh:
        gadm = json.load(fh)

    features = []
    for feat in gadm.get("features", []):
        props = feat.get("properties") or {}
        state = WANT_STATES.get(props.get("NAME_1"))
        if not state:
            continue
        name = props.get("NAME_2")
        if not name:
            continue
        geom = clean_geometry(shape(feat["geometry"]))
        if geom is None:
            print(f"  drop (no usable geometry): {name}")
            continue
        features.append(
            {
                "type": "Feature",
                "properties": {"district": district_key(name, canonical_district), "state": state},
                "geometry": {
                    "type": geom.geom_type,
                    "coordinates": _round_coords(mapping(geom)["coordinates"]),
                },
            }
        )

    features.sort(key=lambda f: (f["properties"]["state"], f["properties"]["district"]))
    collection = {"type": "FeatureCollection", "features": features}

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(collection, fh, separators=(",", ":"), ensure_ascii=False)

    size_kb = OUT_PATH.stat().st_size / 1024
    states = {f["properties"]["state"] for f in features}
    print(f"wrote {OUT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"  size: {size_kb:.1f} KB")
    print(f"  districts: {len(features)} ({', '.join(sorted(states))})")
    # ponytail: see module docstring — 23 old districts, not the 60-district frame.
    print("  note: GADM 4.1 ADM2 is pre-reorg (TG 10 + AP 13), not the 60-district frame")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
