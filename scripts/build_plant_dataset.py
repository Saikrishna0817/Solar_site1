#!/usr/bin/env python3
"""Build plant-level CEA labels joined to the district feature frame.

Also audits `cuf_source` in the master dataset and exports TG/AP site LOCATIONS
from TZ-SAM. TZ-SAM carries capacity + coordinates only, never a CUF, so it may
supply locations and must never be used as a label (CC BY-NC, see
data/external_fetch/LICENSE_REGISTER.md).

in : data/plant_cuf/solar_plants_india.csv                    CEA annual generation
     backend/.../outputs/processed/master_dataset_engineered.csv   district features
out: data/plant_labels/plant_dataset.csv       one row per in-scope CEA plant
     data/plant_labels/tz_sam_tg_ap.csv        TZ-SAM locations, no labels

Usage:
    python scripts/build_plant_dataset.py
"""
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "data_pipeline"))

from solarpipeline.utils import canonical_district  # noqa: E402

MASTER = (PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed"
          / "master_dataset_engineered.csv")
PLANTS = PROJECT_ROOT / "data" / "plant_cuf" / "solar_plants_india.csv"
# ponytail: 102 plants nationally / 13 in TG+AP, not the ~700 the plan wants. Offline the
# only CEA sources are this register + daily RE-report PDFs (single-day, seasonally biased);
# the CEA API endpoints hang and PVWatts/NREL DNS does not resolve here.
# Upgrade path: pull the CEA monthly RE generation XLS per plant, then official-plant
# registers from SECI/State DISCOMs, and re-run this script.
TZ_SAM = PROJECT_ROOT / "data" / "plant_labels" / "tz_sam_india.csv"
OUT_PLANTS = PROJECT_ROOT / "data" / "plant_labels" / "plant_dataset.csv"
OUT_TZ = PROJECT_ROOT / "data" / "plant_labels" / "tz_sam_tg_ap.csv"

SCOPE_STATES = ("Telangana", "Andhra Pradesh")
# Never features: label provenance, provenance strings, and the all-NaN leftover.
NON_FEATURES = {"district", "state", "source", "cuf", "cuf_source", "cuf_real",
                "excluded", "exclusion_reason"}
# ponytail: TG+AP drawn as one bounding box (lat 12.6-20.1, lon 76.7-85.1) instead of a
# point-in-polygon against GADM; a handful of sites near the border leak in or out.
# Upgrade path: geopandas sjoin against gadm41_IND_2 when polygons become a dependency.
TG_AP_BBOX = dict(lat=(12.6, 20.1), lon=(76.7, 85.1))


def audit_labels(master: pd.DataFrame) -> None:
    """Assert every cuf_source is a known provenance value; print the breakdown."""
    known = {"cea_plant", "physics"}
    found = set(master["cuf_source"].dropna().unique())
    unknown = found - known
    assert not unknown, f"Unknown cuf_source values in master dataset: {sorted(unknown)}"

    print("\n== cuf_source audit (master_dataset_engineered) ==")
    for src, n in master["cuf_source"].value_counts().items():
        print(f"  {src:10} {n:3d} rows")
    cea = master[master.cuf_source == "cea_plant"]
    print(f"  cea_plant districts ({len(cea)}): {', '.join(sorted(cea.district))}")


def build_plant_dataset(master: pd.DataFrame) -> pd.DataFrame:
    plants = pd.read_csv(PLANTS)
    plants = plants[plants["state"].isin(SCOPE_STATES)].copy()
    plants["district"] = [canonical_district(d) for d in plants["district"]]

    # Hard rule, recomputed here too so the CSV cannot drift from the label definition.
    mw = pd.to_numeric(plants["installed_capacity_mw"], errors="coerce")
    mu = pd.to_numeric(plants["annual_generation_mu"], errors="coerce")
    plants["cuf"] = (mu * 1000.0 / (mw * 8760.0)).where(mw > 0, pd.NA)
    drift = (plants["cuf"] - plants["annual_cuf"]).abs()
    print(f"\n== label check: cuf = MU*1000/(MW*8760) ==")
    print(f"  {int((drift > 0.002).sum())}/{len(plants)} plants differ from the stored "
          f"annual_cuf by >0.002 (max {drift.max():.4f})")

    feats = [c for c in master.columns if c not in NON_FEATURES]
    frame = master[["district"] + feats].copy()
    frame["district"] = [canonical_district(d) for d in frame["district"]]
    assert not frame["district"].duplicated().any(), "District frame has duplicate names"

    out = plants[["plant_name", "district", "state", "cuf"]].merge(
        frame, on="district", how="left"
    )
    out["cuf_source"] = "cea_plant"
    # plant metadata that would reconstruct the label stays out of the feature columns
    # (installed_capacity_mw + annual_generation_mu == cuf by definition).
    out = out[["plant_name", "district", "state", "cuf", "cuf_source"] + feats]

    missing = out[out[feats[0]].isna()]["district"].tolist()
    assert not missing, f"In-scope plants with no district feature row: {missing}"
    assert out["cuf"].notna().all(), "Plant label is NaN"

    print(f"\n== plant dataset: {len(out)} plants x {len(out.columns)} cols "
          f"({out.state.value_counts().to_dict()}) ==")
    print(f"  districts: {sorted(out.district.unique())}")
    OUT_PLANTS.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PLANTS, index=False)
    print(f"  wrote {OUT_PLANTS.relative_to(PROJECT_ROOT)}")
    return out


def export_tz_sam_locations() -> None:
    """TZ-SAM in-scope site locations — no CUF column, by construction."""
    tz = pd.read_csv(TZ_SAM)
    loc = tz[
        tz["latitude"].between(*TG_AP_BBOX["lat"]) & tz["longitude"].between(*TG_AP_BBOX["lon"])
    ][["cluster_id", "latitude", "longitude", "capacity_mw"]].copy()
    loc["state_scope"] = "TG+AP(bbox)"
    loc.to_csv(OUT_TZ, index=False)
    print(f"\n== TZ-SAM locations: {len(loc)} sites / {loc.capacity_mw.sum():.0f} MW "
          f"(locations only, no labels) -> {OUT_TZ.relative_to(PROJECT_ROOT)}")


def main() -> int:
    master = pd.read_csv(MASTER)
    audit_labels(master)
    build_plant_dataset(master)
    export_tz_sam_locations()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
