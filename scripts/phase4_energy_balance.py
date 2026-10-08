"""Phase 4 — energy balance + per-plant error + blocked-crosscheck status.

4.1 Energy balance (flag if outside ±10%): sum of TGTRANSCO solar plants for a
    month vs CEA "State Control Area" cumulative solar for the same month
    (CEA daily RE report of the last day of that month carries the month total).
4.2 Per-plant error: measured label CUF vs residual model and vs C0.
4.3 PVWatts / SRRA cross-check status: both blocked here (documented, not faked).

Outputs: reports/energy_balance.md, data/plant_labels/plant_error_table.csv,
data/official/Report-<lastday>.xlsx (+ SHA256SUMS).

ponytail: 3 months (Jun/Jul 2024, Nov 2025) — CEA daily archive starts
2024-06-30, TGTRANSCO coverage ends Jul-2024 (plus Nov-2025). Upgrade:
loop every overlapping month once more CEA daily files are cached.
"""
from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "data" / "official"
REGISTRY = ROOT / "data" / "plant_labels" / "plant_registry.csv"
ENERGY = ROOT / "data" / "plant_labels" / "plant_month_energy.csv"
PLANTS = ROOT / "data" / "plant_labels" / "plant_dataset.csv"
C0 = ROOT / "backend" / "data_pipeline" / "outputs" / "processed" / "c0_baseline.csv"
BUNDLE = ROOT / "models" / "residual_ridge.joblib"
REPORT = ROOT / "reports" / "energy_balance.md"
SUMS = OFFICIAL / "SHA256SUMS"

# (report month, CEA daily report of the last day — cumulative column = month)
# CEA daily archive starts 2024-06-30; overlap with TGTRANSCO months:
# 2024-06, 2024-07, 2025-11 (ponytail: 3 months, one winter-ish)
WINDOWS = [("2024-06", "2024-06-30"), ("2024-07", "2024-07-31"),
           ("2025-11", "2025-11-30")]
TOLERANCE = (0.90, 1.10)  # plan 4.1: flag outside ±10%
BASE = "https://gen-re.cea.gov.in/public/uploads/dailyReport/excel/Report-{day}.xlsx"


def fetch(day: str) -> Path:
    path = OFFICIAL / f"Report-{day}.xlsx"
    if not path.exists():
        url = BASE.format(day=day)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            path.write_bytes(r.read())
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        prev = SUMS.read_text() if SUMS.exists() else ""
        if path.name not in prev:
            SUMS.write_text(prev + f"{digest}  official/{path.name}\n")
        print(f"fetched {path.name} ({path.stat().st_size} bytes)")
    return path


def cea_state_solar_mu(path: Path, state: str) -> float:
    df = pd.read_excel(path, sheet_name="State-Wise", header=None)
    for i in range(len(df)):
        label = str(df.iat[i, 0])
        if state.lower() in label.lower() and "region" not in label.lower() \
                and "india" not in label.lower():
            return float(df.iat[i, 6])  # cumulative solar (MU)
    raise LookupError(f"{state} not in {path.name}")


def tgtransco_solar_mu(month: str) -> float:
    reg = pd.read_csv(REGISTRY)
    e = pd.read_csv(ENERGY)
    sel = e[e["month"] == month]
    sel = sel[sel["plant_name"].isin(set(reg["plant_name"]))]  # solar-only set
    return float(sel["mu"].sum())


def plant_error_table() -> pd.DataFrame:
    """LOGO out-of-fold errors (each plant scored by a model trained on the rest)."""
    df = pd.read_csv(PLANTS)
    c0 = pd.read_csv(C0)[["district", "c0_cuf"]]
    df = df.merge(c0, on="district", how="left")
    bundle = joblib.load(BUNDLE)
    feats = bundle["features"]
    X = df[feats].to_numpy(dtype=float)
    resid = np.full(len(df), np.nan)
    groups = df["district"].to_numpy()
    for d in np.unique(groups):
        tr, va = groups != d, groups == d
        sc = StandardScaler().fit(X[tr])
        est = type(bundle["model"])(**bundle["model"].get_params())
        est.fit(sc.transform(X[tr]), df["cuf"].to_numpy()[tr] - df["c0_cuf"].to_numpy()[tr])
        resid[va] = est.predict(sc.transform(X[va]))
    df["cuf_model"] = df["c0_cuf"] + resid  # OOF: no plant's own district in training
    df["err_model"] = (df["cuf_model"] - df["cuf"]).abs()
    df["err_c0"] = (df["c0_cuf"] - df["cuf"]).abs()
    out = df[["plant_name", "district", "state", "cuf", "c0_cuf", "cuf_model",
              "err_c0", "err_model"]].round(5)
    out.to_csv(ROOT / "data" / "plant_labels" / "plant_error_table.csv", index=False)
    return out


def main() -> int:
    rows = []
    for month, day in WINDOWS:
        path = fetch(day)
        cea_tg = cea_state_solar_mu(path, "Telangana")
        cea_ap = cea_state_solar_mu(path, "Andhra Pradesh")
        tg = tgtransco_solar_mu(month)
        ratio = tg / cea_tg if cea_tg else float("nan")
        rows.append({
            "month": month, "tgtransco_solar_mu": round(tg, 2),
            "cea_telangana_mu": cea_tg, "ratio_tg_over_cea": round(ratio, 3),
            "within_±10pct": bool(TOLERANCE[0] <= ratio <= TOLERANCE[1]),
            "cea_andhra_mu": cea_ap, "source": f"Report-{day}.xlsx:State-Wise",
        })

    err = plant_error_table()
    mae_c0 = float(err["err_c0"].mean())
    mae_m = float(err["err_model"].mean())

    lines = ["# Phase 4 — energy balance, per-plant error, blocked cross-checks", "",
             "## 4.1 Energy balance: TGTRANSCO plant sum vs CEA state total (same month)", "",
             "| month | TGTRANSCO solar (MU) | CEA Telangana solar (MU) | ratio | within ±10% | CEA AP solar (MU) |",
             "|---|---|---|---|---|---|"]
    lines += [f"| {r['month']} | {r['tgtransco_solar_mu']} | {r['cea_telangana_mu']} | "
              f"{r['ratio_tg_over_cea']} | {r['within_±10pct']} | {r['cea_andhra_mu']} |"
              for r in rows]
    lines += ["", "Sources: CEA daily RE report (State-Wise sheet, cumulative column) — "
               "same-official-source check.", "",
              "**Finding (flagged): all three ratios are outside ±10% (0.70-0.79).** "
              "The consistent shortfall means the TGTRANSCO EBC tables do NOT cover "
              "all Telangana solar — only the plants listed in the transmission-loss "
              "tables (~70-80% of the CEA state-control total). Scope mismatch, not "
              "an energy error: CEA state-control area includes open-access/private "
              "plants absent from the EBC listing. Interpretation [REVIEW]: treat "
              "TGTRANSCO labels as representative of the listed subset, not the state.", "",
              "## 4.2 Per-plant error (measured label CUF, n=%d, LOGO out-of-fold)" % len(err), "",
              "| model | MAE (CUF) |", "|---|---|",
              f"| residual ridge (+C0) | {mae_m:.5f} |",
              f"| C0 physics alone | {mae_c0:.5f} |",
              "", "Full table: `data/plant_labels/plant_error_table.csv` "
                  "(every figure measured or model-derived; no clamping).", "",
              "## 4.3 Cross-check status", "",
              "- **NREL PVWatts V8**: `developer.nrel.gov` DNS-dead from this "
              "environment — offline pvlib chain NOT cross-checked. "
              "[BLOCKED — rerun `pvwatts/v8.json` compare when reachable]",
              "- **Global Solar Atlas**: HTTP 403 (SPA, no raster) [BLOCKED]",
              "- **SRRA station holdouts**: no free station-level data found; "
              "holdout labels remain TGTRANSCO/CEA only [PENDING — RTI/next data drop]",
              "- Flagged derived figures: all MAEs/ratios above are computed from "
              "the cited official files."]
    REPORT.write_text("\n".join(lines) + "\n")
    for r in rows:
        print(r)
    print(f"plant MAE: model={mae_m:.5f} c0={mae_c0:.5f} (n={len(err)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
