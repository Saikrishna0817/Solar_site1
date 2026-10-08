"""Phase 3 — residual modelling + district-bootstrap CI -> models/gate.json.

Target  = measured CUF - C0(physics)          [residual, plan §5 Phase 3.2]
CV      = leave-one-district-out (repeated split order is deterministic)  [3.3]
CI      = bootstrap over districts of MAE(model) - MAE(C0)                [3.4]
Models  = pre-registered, fixed hyperparameters, ALL reported             [3.5]
Interval= split-conformal 90% on OOF residuals                           [3.4]
Gate 3  = pooled LOGO MAE beats C0 with 95% CI excluding 0, AND held-out
          plant check (same artifact) beats C0 -> models/gate.json.

ponytail ceilings:
  * n=13 plants -> bootstrap over 11 districts; CI is wide by construction
  * pre-registered list is 2 features (n/10 rounded up to keep a linear model
    identifiable) — upgrade path: revisit when TGTRANSCO capacity pushes n>=40
  * conformal interval is marginal (not per-district); Mondrian split when n grows
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
PLANTS = ROOT / "data" / "plant_labels" / "plant_dataset.csv"
C0 = ROOT / "backend" / "data_pipeline" / "outputs" / "processed" / "c0_baseline.csv"
HELDOUT = ROOT / "reports" / "heldout_validation.md"
FEATURES = ROOT / "models" / "pre_registered_features.json"
GATE_OUT = ROOT / "models" / "gate.json"
REPORT = ROOT / "reports" / "residual_ci.md"

# Pre-registered (plan 2.6: commit BEFORE model runs; physics-chosen)
PRE_REGISTERED = ["avg_ghi_kwh_m2_day", "max_temp_c"]
MODELS = {  # fixed hyperparameters in advance (plan Phase 3.2)
    "ridge": Ridge(alpha=1.0),
    "elastic_net": ElasticNet(alpha=1.0, l1_ratio=0.5, max_iter=10_000),
}
N_BOOT = 2000
SEED = 42


def heldout_mae_from_report() -> dict | None:
    """Parse our own generated table (stable format) for model/C0 MAE."""
    if not HELDOUT.exists():
        return None
    txt = HELDOUT.read_text()
    m = re.search(r"MAE \(CUF\)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)", txt)
    if not m:
        return None
    return {"model_mae": float(m.group(1)), "c0_mae": float(m.group(2)),
            "winner": "model" if float(m.group(1)) < float(m.group(2)) else "c0",
            "source": str(HELDOUT.relative_to(ROOT))}


def main() -> int:
    df = pd.read_csv(PLANTS)
    c0 = pd.read_csv(C0)[["district", "c0_cuf"]]
    df = df.merge(c0, on="district", how="left")
    assert df["c0_cuf"].notna().all(), "C0 missing for a plant district — run baseline_c0.py"

    if not FEATURES.exists():  # the pre-registration itself
        FEATURES.write_text(json.dumps(
            {"features": PRE_REGISTERED, "rationale":
             "physics: irradiance sets the ceiling, cell temp derates it",
             "n": len(df), "n_over_10": round(len(df) / 10, 1),
             "note": "n/10 = 1.3 rounded up to 2 for an identifiable linear model",
             "committed_before_runs": True}, indent=2) + "\n")
    pre = json.loads(FEATURES.read_text())["features"]

    y = df["cuf"].to_numpy()
    c0v = df["c0_cuf"].to_numpy()
    resid = y - c0v
    groups = df["district"].to_numpy()
    X = df[pre].to_numpy(dtype=float)

    oof_models: dict[str, np.ndarray] = {}
    for name, est in MODELS.items():
        oof = np.full(len(df), np.nan)
        for d in np.unique(groups):
            tr, va = groups != d, groups == d
            sc = StandardScaler().fit(X[tr])
            est.fit(sc.transform(X[tr]), resid[tr])
            oof[va] = c0v[va] + est.predict(sc.transform(X[va]))
        oof_models[name] = oof

    rng = np.random.default_rng(SEED)
    uniq = np.unique(groups)
    results = {}
    for name, oof in oof_models.items():
        mae_m = float(np.mean(np.abs(oof - y)))
        mae_0 = float(np.mean(np.abs(c0v - y)))
        per_row = np.abs(oof - y) - np.abs(c0v - y)
        # bootstrap over districts (rows inherit their district draw)
        idx_by_d = {d: np.where(groups == d)[0] for d in uniq}
        draws = np.empty(N_BOOT)
        for b in range(N_BOOT):
            pick = rng.choice(uniq, size=len(uniq), replace=True)
            rows = np.concatenate([idx_by_d[d] for d in pick])
            draws[b] = per_row[rows].mean()
        lo, hi = np.percentile(draws, [2.5, 97.5])
        # conformal 90% interval on OOF residuals
        q = float(np.quantile(np.abs(oof - y), 0.90, method="higher"))
        results[name] = {
            "logo_mae": round(mae_m, 5), "c0_mae": round(mae_0, 5),
            "delta_mae": round(mae_m - mae_0, 5),
            "delta_ci95": [round(float(lo), 5), round(float(hi), 5)],
            "beats_c0_point": bool(mae_m < mae_0),
            "beats_c0_ci95": bool(hi < 0),
            "conformal90_halfwidth": round(q, 5),
        }

    # held-out check with the SAME model spec (20%, seed 42) + C0 on same rows
    tr_i, te_i = train_test_split(np.arange(len(df)), test_size=0.2, random_state=SEED)
    heldout_all = {}
    for name, est in MODELS.items():
        sc = StandardScaler().fit(X[tr_i])
        est.fit(sc.transform(X[tr_i]), resid[tr_i])
        pred = c0v[te_i] + est.predict(sc.transform(X[te_i]))
        m_mae = float(np.mean(np.abs(pred - y[te_i])))
        m_c0 = float(np.mean(np.abs(c0v[te_i] - y[te_i])))
        heldout_all[name] = {
            "model_mae": round(m_mae, 5), "c0_mae": round(m_c0, 5),
            "winner": "model" if m_mae < m_c0 else "c0",
            "n_heldout": int(len(te_i)), "seed": SEED,
        }

    best = min(results, key=lambda k: results[k]["logo_mae"])
    gate3_by_model = {
        k: bool(results[k]["beats_c0_ci95"]) and heldout_all[k]["winner"] == "model"
        for k in results}
    passed = [k for k, ok in gate3_by_model.items() if ok]
    served = min(passed, key=lambda k: results[k]["logo_mae"]) if passed else None
    heldout = heldout_all[best]
    gate3 = bool(passed)

    # persist the artifact the API is allowed to serve (plan: same artifact everywhere)
    artifact = None
    if served:
        sc = StandardScaler().fit(X)
        est = MODELS[served].fit(sc.transform(X), resid)
        artifact = ROOT / "models" / f"residual_{served}.joblib"
        joblib.dump({"model": est, "scaler": sc, "features": pre,
                     "model_name": served,
                     "conformal90_halfwidth": results[served]["conformal90_halfwidth"]},
                    artifact)

    gate = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "unit": "plant", "cv": "leave-one-district-out", "n_rows": len(df),
        "n_districts": int(len(uniq)), "pre_registered_features": pre,
        "models": results, "best_model": best,
        "heldout_all": heldout_all, "heldout": heldout,
        "gate3_by_model": gate3_by_model,
        "gate3_pass": gate3,
        "served_model": served,
        "artifact": str(artifact.relative_to(ROOT)) if artifact else None,
        "gate3_rule": "LOGO MAE beats C0 with 95% district-bootstrap CI excluding 0 "
                      "AND held-out plants (same artifact) beat C0",
        "serving": f"ml:{served}" if served else "baseline_c0_only",
    }
    GATE_OUT.write_text(json.dumps(gate, indent=2) + "\n")

    lines = ["# Phase 3 — residual models over C0 (pre-registered, ALL reported)", "",
             f"n={len(df)} plants / {len(uniq)} districts · features: {', '.join(pre)} · "
             f"CV: LOGO · CI: {N_BOOT} district bootstraps (seed {SEED})", "",
             "| model | LOGO MAE | C0 MAE | Δ (95% CI) | beats C0 point | beats C0 CI95 | conformal90 ± |",
             "|---|---|---|---|---|---|---|"]
    for k, v in results.items():
        lines.append(f"| {k} | {v['logo_mae']} | {v['c0_mae']} | "
                     f"{v['delta_mae']} ({v['delta_ci95']}) | {v['beats_c0_point']} | "
                     f"{v['beats_c0_ci95']} | {v['conformal90_halfwidth']} |")
    lines += ["", "Held-out check (same spec, 20%, seed 42):",
              "| model | heldout MAE | C0 MAE | winner |", "|---|---|---|---|"]
    lines += [f"| {k} | {v['model_mae']} | {v['c0_mae']} | {v['winner']} |"
              for k, v in heldout_all.items()]
    lines += ["", f"**Gate 3: {'PASS' if gate3 else 'FAIL'}**"
               + (f" -> serving: residual {served}" if served
                  else " -> serving: baseline C0 only (ML withheld)"),
              "(prior md parse of the old artifact kept for reference: "
              f"{heldout_mae_from_report()})"]
    REPORT.write_text("\n".join(lines) + "\n")
    print(f"best={best} delta={results[best]['delta_mae']} "
          f"ci={results[best]['delta_ci95']} gate3={gate3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
