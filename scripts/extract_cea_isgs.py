"""Phase 1.7 — extract TG/AP solar rows from CEA monthly RE ISGS report.

Writes data/plant_labels/cea_isgs_month_energy.csv (plant-month energy labels,
MU -> MWh) and appends the QA note to reports/label_qa.md.

ponytail ceilings:
  * one report month on hand (July 2026) — a 12-month CUF window needs 12
    monthly reports (download cadence: CEA publishes monthly; extend the loop)
  * ISGS covers only central/state/private ISGS plants, not every TG/AP plant
  * station names differ from the TGERC register (alias map below), duplicates
    flagged with `alias_of` when we can match them
Upgrade path: iterate months, expand alias map, join capacities from Phase 1.3.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "official" / "RE_Monthly_Generation_report_July_2026.xlsx"
OUT = ROOT / "data" / "plant_labels" / "cea_isgs_month_energy.csv"
QA = ROOT / "reports" / "label_qa.md"

MONTH = "2026-07"
STATES = ("Telangana", "Andhra Pradesh")
# observed name differences vs data/plant_labels/plant_registry.csv (flag, don't merge)
ALIAS = {
    "ntpc_ramagundam_fsp": "ramangundam solar",
    "rstps_fsp": None,      # no register match — keep as ISGS-only
    "greenko_kurnool_s": None,
    "sael1_kurnool": None,
    "sael2_kurnool": None,
    "simhadri_fsp": None,
    "amgreen_kurnool_s": None,
}


def main() -> int:
    if not SRC.exists():
        print(f"missing {SRC}", file=sys.stderr)
        return 1
    df = pd.read_excel(SRC, sheet_name="ISGS", header=4)
    df.columns = [str(c).strip() for c in df.columns]
    state_col = next(c for c in df.columns if c.startswith("State"))
    type_col = next(c for c in df.columns if c.startswith("Type"))
    gen_col = next(c for c in df.columns if c.startswith("Actual"))

    sel = df[df[state_col].astype(str).str.strip().isin(STATES)
             & df[type_col].astype(str).str.contains("Solar", case=False, na=False)].copy()
    sel = sel.rename(columns={
        "Station": "station", state_col: "state",
        "Sector (Central/State/Private)": "sector",
        type_col: "fuel", gen_col: "generation_mu",
    })
    sel["station_key"] = sel["station"].str.strip().str.lower().str.replace(" ", "_")
    sel["generation_mwh"] = (pd.to_numeric(sel["generation_mu"], errors="coerce") * 1000).round(2)
    sel["month"] = MONTH
    sel["source"] = f"{SRC.name}:ISGS"
    sel["alias_of"] = sel["station_key"].map(ALIAS)
    sel["label_scope"] = "isgs_subset_not_exhaustive"
    sel = sel[["station", "state", "sector", "fuel", "month", "generation_mu",
               "generation_mwh", "alias_of", "label_scope", "source"]]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sel.to_csv(OUT, index=False)

    note = [
        "",
        "## CEA ISGS monthly energy (Phase 1.7)",
        "",
        f"- Source: `{SRC.name}` sheet `ISGS`, month `{MONTH}`.",
        f"- Rows: {len(sel)} TG/AP solar ISGS plants -> `{OUT.relative_to(ROOT)}`.",
        "- CAVEAT: ISGS subset only (central/state/private ISGS), not all TG/AP plants; "
        "one month on hand — a 12-mo CUF window needs 12 monthly CEA reports.",
        "- CAVEAT: station names differ from the TGERC register "
        "(`Ntpc_Ramagundam_Fsp` ~ `Ramangundam Solar`); matches flagged in "
        "`alias_of`, never silently merged.",
    ]
    qa = QA.read_text() if QA.exists() else "# Label QA (Gate 1)\n"
    if "## CEA ISGS monthly energy" not in qa:
        qa = qa.rstrip() + "\n" + "\n".join(note) + "\n"
        QA.write_text(qa)
    print(f"rows={len(sel)} -> {OUT.relative_to(ROOT)}")
    print(sel[["station", "state", "generation_mu"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
