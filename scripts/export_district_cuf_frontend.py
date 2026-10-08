"""Export per-district CUF (C0, model prediction, conformal 90% interval, measured
label where it exists) to frontend/src/data/districtCuf.json for the Phase 5.8
choropleth (measured vs predicted CUF with uncertainty).

Regenerate after any retrain: .venv/bin/python scripts/export_district_cuf_frontend.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "backend" / "data_pipeline" / "outputs" / "processed" / "master_dataset_engineered.csv"
C0 = ROOT / "backend" / "data_pipeline" / "outputs" / "processed" / "c0_baseline.csv"
BUNDLE = ROOT / "models" / "residual_ridge.joblib"
GATE = ROOT / "models" / "gate.json"
PLANTS = ROOT / "data" / "plant_labels" / "plant_dataset.csv"
OUT = ROOT / "frontend" / "src" / "data" / "districtCuf.json"


def main() -> int:
    master = pd.read_csv(MASTER)
    c0 = pd.read_csv(C0)
    bundle = joblib.load(BUNDLE)
    gate = json.loads(GATE.read_text())
    halfwidth = float(gate["models"][gate["served_model"]]["conformal90_halfwidth"])

    plants = pd.read_csv(PLANTS)
    measured = plants.groupby("district")["cuf"].mean().round(5).to_dict()

    df = master.merge(c0[["district", "c0_cuf"]], on="district", how="left")
    X = df[bundle["features"]].to_numpy(dtype=float)
    pred = df["c0_cuf"].to_numpy() + bundle["model"].predict(bundle["scaler"].transform(X))

    rows = []
    for (_, row), p in zip(df.iterrows(), pred):
        d = str(row["district"]).strip().lower()
        rows.append({
            "district": d,
            "state": str(row.get("state", "")),
            "cuf_predicted": round(float(p), 5),
            "c0_physics": round(float(row["c0_cuf"]), 5),
            "interval_90": [round(float(p) - halfwidth, 5), round(float(p) + halfwidth, 5)],
            "measured_cuf": measured.get(d),  # None for the 49 districts without labels
        })
    rows.sort(key=lambda r: r["district"])
    OUT.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "served_model": gate["served_model"],
        "gate3_pass": gate["gate3_pass"],
        "conformal90_halfwidth": halfwidth,
        "note": "interval = split-conformal 90% from models/gate.json; "
                "measured_cuf = mean of CEA/TGTRANSCO plant labels in that district; "
                "district-level prediction (nearest-centroid features), flag on API for site scale",
        "districts": rows,
    }, indent=2) + "\n")
    n_meas = sum(1 for r in rows if r["measured_cuf"] is not None)
    print(f"{len(rows)} districts, {n_meas} with measured labels -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
