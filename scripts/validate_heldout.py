#!/usr/bin/env python3
"""Held-out plant validation: score the plants the model never saw.

Reproduces the trainer's split (80/20, seed 42) over data/plant_labels/plant_dataset.csv,
predicts the held-out plants with the saved ridge artifact, and puts those errors next
to the pvlib C0 physics baseline for the same districts.

Writes reports/heldout_validation.md — the evidence that plant-level validation exists
(the "no plant-level validation" flaw).

ponytail: only the 3 plants the split holds out are scored, because that is all the
register gives us (13 in-scope). Upgrade path: the CEA monthly XLS per plant, then the
whole hold-out is 20+ sites instead of 3.

Usage: python scripts/validate_heldout.py [--model ridge]
"""
import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLANT_CSV = PROJECT_ROOT / "data" / "plant_labels" / "plant_dataset.csv"
C0_CSV = PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed" / "c0_baseline.csv"
MODELS = PROJECT_ROOT / "models"
OUT = PROJECT_ROOT / "reports" / "heldout_validation.md"


def _md_table(df: pd.DataFrame) -> str:
    """Markdown table without pulling in `tabulate` for one report."""
    cols = list(df.columns)
    head = "| " + " | ".join(cols) + " |\n"
    sep = "|" + "|".join(["---"] * len(cols)) + "|\n"
    rows = "".join("| " + " | ".join(str(v) for v in row) + " |\n"
                   for row in df.itertuples(index=False, name=None))
    return head + sep + rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="ridge")
    args = ap.parse_args()

    model_path = MODELS / f"{args.model}.joblib"
    if not model_path.exists() or not (MODELS / "scaler_selected.joblib").exists():
        raise SystemExit(f"missing artifacts in {MODELS} — run: python -m src.cli.train")

    df = pd.read_csv(PLANT_CSV)
    _, test = train_test_split(df, test_size=0.2, random_state=42, shuffle=True)

    feats = json.loads((MODELS / "feature_names.json").read_text())
    missing = [f for f in feats if f not in df.columns]
    assert not missing, f"model wants features absent from the plant dataset: {missing}"

    model = joblib.load(model_path)
    scaler = joblib.load(MODELS / "scaler_selected.joblib")
    pred = model.predict(scaler.transform(test[feats].values))

    c0 = pd.read_csv(C0_CSV)[["district", "c0_cuf"]] if C0_CSV.exists() else None
    out = test[["plant_name", "district", "state", "cuf"]].copy()
    out["model_cuf"] = pred
    out["model_err"] = out["model_cuf"] - out["cuf"]
    if c0 is not None:
        out = out.merge(c0, on="district", how="left")
        out["c0_err"] = out["c0_cuf"] - out["cuf"]

    lines = [
        "# Held-out plant validation\n",
        f"Model `{args.model}` · hold-out = 20% of 13 in-scope CEA plants "
        f"(split seed 42, same as training) · labels are CEA actual MU/MW/8760.\n",
        _md_table(out.round(4)), "",
        f"| Metric | Model | C0 physics baseline |\n|---|---|---|\n",
    ]
    m_mae = out["model_err"].abs().mean()
    m_bias = out["model_err"].mean()
    has_c0 = "c0_err" in out
    mae_c0 = f"{out['c0_err'].abs().mean():.4f}" if has_c0 else "n/a"
    bias_c0 = f"{out['c0_err'].mean():+.4f}" if has_c0 else "n/a"
    lines.append(f"| MAE (CUF) | {m_mae:.4f} | {mae_c0} |\n")
    lines.append(f"| Bias (pred − actual) | {m_bias:+.4f} | {bias_c0} |\n")
    if has_c0:
        verdict = ("model beats C0" if m_mae < out["c0_err"].abs().mean()
                   else "C0 beats model")
        lines.append(f"\n**Verdict:** {verdict} on this hold-out ({len(out)} plants, "
                     f"narrow target range {out.cuf.min():.3f}-{out.cuf.max():.3f}).\n")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(lines))
    print(OUT.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
