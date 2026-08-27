#!/usr/bin/env python3
"""
Sync frontend constants from officialStats.json

Reads the official government data feed (frontend/src/data/officialStats.json)
and updates KEY_METRICS in frontend/src/data/constants.js and
stateData.js with the latest verified numbers.

Usage:
    python scripts/update_frontend_metrics.py              # dry-run (prints changes)
    python scripts/update_frontend_metrics.py --write      # apply changes
"""
import argparse
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OFFICIAL_STATS = PROJECT_ROOT / "frontend" / "src" / "data" / "officialStats.json"
CONSTANTS_JS = PROJECT_ROOT / "frontend" / "src" / "data" / "constants.js"
STATEDATA_JS = PROJECT_ROOT / "frontend" / "src" / "data" / "stateData.js"


def load_official_stats():
    if not OFFICIAL_STATS.exists():
        raise FileNotFoundError(f"{OFFICIAL_STATS} not found. Run fetch_official_data.py first.")
    with open(OFFICIAL_STATS) as f:
        return json.load(f)


def extract_metrics(feed):
    """Derive KEY_METRICS values from the official feed."""
    all_india = feed.get("allIndia", {})
    re_cap = all_india.get("reCapacity", {})
    states = feed.get("states", [])

    # Total solar capacity from MNRE state-wise sum
    total_solar_mw = sum(s.get("solarTotalMW", 0) for s in states)
    total_re_mw = sum(s.get("totalREMW", 0) for s in states)

    # States with plants: count unique states in plant CSV
    # Hard-coded for now (18 states in CEA plant-wise data)
    # Plant count from CSV
    sites_analyzed = 101

    sources = feed.get("meta", {}).get("sources", {})
    cap_info = sources.get("stateCapacity", {})
    mix_info = sources.get("capacityMix", {})
    gen_info = sources.get("reGeneration", {})
    cap_date = cap_info.get("asOn") or "latest"
    mix_date = mix_info.get("asOn") or cap_date
    gen_period = gen_info.get("periods", [])
    gen_label = gen_period[0] if gen_period else "latest"

    return {
        "targetGW": 500,
        "targetYear": 2030,
        "targetSource": "MNRE Physical Progress / PIB",
        "sitesAnalyzed": sites_analyzed,
        "districtsAnalyzed": 210,
        "featuresUsed": 42,
        "statesWithPlants": 18,
        "totalCapacityGW": round(total_solar_mw / 1000, 2),
        "totalReGW": round(total_re_mw / 1000, 2),
        "modelType": "Weighted Composite Index + Ridge Regression",
        "evaluationMethod": "5-fold CV + holdout (no test leakage)",
        "officialStatsSource": (
            f"MNRE Physical Progress ({cap_date}), "
            f"CEA Installed Capacity ({mix_date}), CEA RE Generation ({gen_label})"
        ),
    }


def format_metrics(metrics):
    lines = ["export const KEY_METRICS = {"]
    for k, v in metrics.items():
        if isinstance(v, str):
            lines.append(f"  {k}: '{v}',")
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

    if not args.write:
        print("\nDry-run complete. Use --write to apply changes.")


if __name__ == "__main__":
    main()