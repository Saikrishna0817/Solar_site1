#!/usr/bin/env python3
"""
Sync frontend constants from REAL outputs

Sources (in priority order):
  * models/metrics.json      — written by `python -m src.cli.train` (features,
                               training rows, unit, label provenance, CV method)
  * data/plant_labels/plant_dataset.csv — the CEA plants actually in scope
  * processed feature table  — how many districts have model features
  * frontend/src/data/officialStats.json — MNRE/CEA published totals (unchanged)

Usage:
    python scripts/update_frontend_metrics.py              # dry-run (prints changes)
    python scripts/update_frontend_metrics.py --write      # apply changes
"""
import argparse
import json
import re

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OFFICIAL_STATS = PROJECT_ROOT / "frontend" / "src" / "data" / "officialStats.json"
CONSTANTS_JS = PROJECT_ROOT / "frontend" / "src" / "data" / "constants.js"
STATEDATA_JS = PROJECT_ROOT / "frontend" / "src" / "data" / "stateData.js"
GATE_JSON = PROJECT_ROOT / "frontend" / "src" / "data" / "gateMetrics.json"
MODEL_METRICS = PROJECT_ROOT / "models" / "metrics.json"
PLANT_DATASET = PROJECT_ROOT / "data" / "plant_labels" / "plant_dataset.csv"
PROCESSED = PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed"


def load_official_stats():
    if not OFFICIAL_STATS.exists():
        raise FileNotFoundError(f"{OFFICIAL_STATS} not found. Run fetch_official_data.py first.")
    with open(OFFICIAL_STATS) as f:
        return json.load(f)


def load_model_metrics() -> dict:
    if not MODEL_METRICS.exists():
        raise FileNotFoundError(
            f"{MODEL_METRICS} not found — train first: python -m src.cli.train"
        )
    return json.loads(MODEL_METRICS.read_text())


def count_plants() -> tuple[int, int, int]:
    """(plants, states, districts-with-features) from the real artifacts."""
    if not PLANT_DATASET.exists():
        raise FileNotFoundError(f"{PLANT_DATASET} not found — run scripts/build_plant_dataset.py")
    df = pd.read_csv(PLANT_DATASET)
    plants = len(df)
    states = df["state"].nunique() if "state" in df.columns else 0

    districts = 0
    for name in ("master_dataset_engineered.csv", "features_train.csv"):
        path = PROCESSED / name
        if path.exists():
            districts = len(pd.read_csv(path, usecols=["district"]))
            break
    return plants, states, districts


def extract_metrics(feed):
    """Derive KEY_METRICS from model training output + official feeds."""
    all_india = feed.get("allIndia", {})
    states = feed.get("states", [])

    # Total solar capacity from MNRE state-wise sum (official, not modeled)
    total_solar_mw = sum(s.get("solarTotalMW", 0) for s in states)
    total_re_mw = sum(s.get("totalREMW", 0) for s in states)

    trained = load_model_metrics()
    plants, states_with_plants, districts = count_plants()

    passing = [m for m in trained.get("models", []) if m.get("beats_c0")]
    if not passing:
        raise SystemExit(
            "No model beats the C0 physics baseline (models/metrics.json) — "
            "the frontend would publish a model that has not earned its numbers. "
            "Retrain before syncing metrics."
        )
    best = min(passing, key=lambda m: m["cv_mae"])
    unit = trained.get("unit", "district")

    sources = feed.get("meta", {}).get("sources", {})
    cap_date = sources.get("stateCapacity", {}).get("asOn") or "latest"
    mix_date = sources.get("capacityMix", {}).get("asOn") or cap_date
    gen_period = sources.get("reGeneration", {}).get("periods", [])
    gen_label = gen_period[0] if gen_period else "latest"

    return {
        "targetGW": 500,
        "targetYear": 2030,
        "targetSource": "MNRE Physical Progress / PIB",
        "sitesAnalyzed": plants,
        "districtsAnalyzed": districts,
        "featuresUsed": trained.get("n_features", 0),
        "statesWithPlants": states_with_plants,
        "totalCapacityGW": round(total_solar_mw / 1000, 2),
        "totalReGW": round(total_re_mw / 1000, 2),
        "modelType": f"{best['model_name']} ({unit}-level CUF)",
        "evaluationMethod": trained.get("evaluation_method", "unknown"),
        "officialStatsSource": (
            f"MNRE Physical Progress ({cap_date}), "
            f"CEA Installed Capacity ({mix_date}), CEA RE Generation ({gen_label})"
        ),
    }


def format_metrics(metrics):
    lines = ["export const KEY_METRICS = {"]
    for k, v in metrics.items():
        if isinstance(v, str):
            # escape for a single-quoted JS literal (gen labels carry apostrophes)
            escaped = v.replace("\\", "\\\\").replace("'", "\\'")
            lines.append(f"  {k}: '{escaped}',")
        else:
            lines.append(f"  {k}: {v},")
    lines.append("};")
    return "\n".join(lines)


def update_constants_js(metrics_str, dry_run=False):
    content = CONSTANTS_JS.read_text()
    pattern = r"export const KEY_METRICS = \{[\s\S]*?\n\};"
    new_content = re.sub(pattern, metrics_str, content)
    if dry_run:
        print("--- constants.js (KEY_METRICS block would become) ---")
        print(metrics_str)
        return
    if new_content == content:
        print("constants.js: no change needed")
    else:
        CONSTANTS_JS.write_text(new_content)
        print(f"Updated {CONSTANTS_JS}")


def update_state_data_js(feed, dry_run=False):
    """Update stateData.js with latest installed capacity from official feed."""
    content = STATEDATA_JS.read_text()
    states_by_name = {s["state"]: s for s in feed.get("states", [])}

    def repl(match):
        state_name = match.group(1)
        if state_name in states_by_name:
            s = states_by_name[state_name]
            installed = round(s.get("solarTotalMW", 0) / 1000, 2)
            total_re = round(s.get("totalREMW", 0) / 1000, 2)
            # Keep potentialGW, avgGHI, etc. from original; only replace installedGW
            return re.sub(
                r"installedGW: [\d.]+",
                f"installedGW: {installed}",
                match.group(0)
            )
        return match.group(0)

    pattern = r"\{\s*state:\s*'([^']+)',\s*potentialGW:[\s\S]*?color:\s*'[^']*'"
    new_content = re.sub(pattern, repl, content)

    if dry_run:
        print("--- stateData.js (first few states updated preview) ---")
        for s in feed.get("states", [])[:3]:
            installed = round(s.get("solarTotalMW", 0) / 1000, 2)
            print(f"  {s['state']}: installedGW -> {installed} GW")
        return

    if new_content == content:
        print("stateData.js: no change needed")
    else:
        STATEDATA_JS.write_text(new_content)
        print(f"Updated {STATEDATA_JS}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Apply changes (default: dry-run)")
    args = parser.parse_args()

    feed = load_official_stats()
    metrics = extract_metrics(feed)
    metrics_str = format_metrics(metrics)

    print(f"Source: {OFFICIAL_STATS}")
    print(f"Generated: {feed['meta']['generatedAt']}")

    update_constants_js(metrics_str, dry_run=not args.write)
    update_state_data_js(feed, dry_run=not args.write)

    # The per-model gate table (Methodology page) rides the same sync surface,
    # as a JSON file inside frontend/src — no cross-directory build dependency.
    trained = load_model_metrics()
    gate = {k: trained[k] for k in ("c0_mae", "c0_n_districts", "threshold", "models")
            if k in trained}
    if dry_run := (not args.write):
        print(f"--- {GATE_JSON.name} would be regenerated ({len(gate['models'])} models) ---")
    else:
        GATE_JSON.write_text(json.dumps(gate, indent=2))
        print(f"Updated {GATE_JSON}")

    if not args.write:
        print("\nDry-run complete. Use --write to apply changes.")


if __name__ == "__main__":
    main()