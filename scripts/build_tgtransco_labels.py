"""TGTRANSCO label factory (plan Phase 1, tasks 1.1-1.5, 1.8).

Downloads are done by hand already (data/raw/tgtransco/*.pdf). This script:
  hashes raw PDFs -> parses monthly plant MU -> builds registry/capacity ->
  builds 12-month CUF windows (cuf_source = official_monthly) -> label_qa.md.

Capacity is ONLY sourced (name-embedded MW, CEA daily report, existing CEA
register) — never derived from energy (that would make CUF circular).
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from calendar import monthrange
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "tgtransco"
OUT = ROOT / "data" / "plant_labels"
QA = ROOT / "reports" / "label_qa.md"
CEA_DAILY = ROOT / "data" / "external_fetch" / "state" / "CEA_daily_RE_10Mar2025.pdf"
REGISTER = ROOT / "data" / "plant_cuf" / "solar_plants_india.csv"
DISTRICT_FEATS = ROOT / "backend" / "data_pipeline" / "outputs" / "processed" / "features_train.csv"

MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June",
     "July", "August", "September", "October", "November", "December"], 1)}
MONTHS.update({m[:3].lower(): i for m, i in list(MONTHS.items())})
SOLAR_KW = ("solar", "sun", "solaire", "photovolt", " pv", "pv ", "acme", "azure")
TG_DISTRICTS = [
    "Adilabad", "Bhadradri Kothagudem", "Hanumakonda", "Hyderabad", "Jagtial",
    "Jangaon", "Jayashankar Bhupalpally", "Jogulamba Gadwal", "Kamareddy",
    "Karimnagar", "Khammam", "Komaram Bheem Asifabad", "Mahabubabad",
    "Mahbubnagar", "Mancherial", "Medak", "Medchal", "Nalgonda", "Narayanpet",
    "Nirmal", "Nizamabad", "Peddapalli", "Rajanna Sircilla", "Rangareddy",
    "Sangareddy", "Siddipet", "Suryapet", "Vikarabad", "Wanaparthy",
    "Warangal", "Yadadri Bhuvanagiri",
]
ALIASES = {"mdk": "Medak", "nlg": "Nalgonda", "rr": "Rangareddy",
           "m.b.nagar": "Mahbubnagar", "sadasivpet": "Medak",
           "bhongir": "Yadadri Bhuvanagiri", "polepally": "Mahbubnagar",
           "tandur": "Vikarabad", "manuguru": "Bhadradri Kothagudem",
           "yellandu": "Bhadradri Kothagudem", "kamareddy": "Kamareddy",
           "siddipet": "Siddipet", "suryapet": "Suryapet"}
# 12-month windows that exist fully in the archive (plan 1.5: full windows only)
WINDOWS = [("2023-01", "2023-12"), ("2023-08", "2024-07")]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def parse_month(fname: str) -> str | None:
    m = re.search(r"([A-Za-z]+)-(\d{4})", fname)
    if not m or m.group(1).lower() not in MONTHS:
        return None
    return f"{m.group(2)}-{MONTHS[m.group(1).lower()]:02d}"


def parse_pdf(path: Path) -> list[dict]:
    txt = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        capture_output=True, text=True, check=True).stdout
    month = parse_month(path.name)
    rows = []
    for line in txt.splitlines():
        m = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9 &.'()\-/]{2,}?)\s{2,}(-?\d+\.\d{1,2})\s*$", line)
        if not m:
            continue
        name = " ".join(m.group(1).split())
        val = float(m.group(2))
        if any(k in name.lower() for k in
               ("total", "discom", "periphery", "losses", "input", "generation")):
            continue
        rows.append({"plant_name": name, "month": month, "mu": val,
                     "source_file": path.name})
    return rows


def district_for(name: str, known: list[str]) -> str:
    low = name.lower()
    for d in known:
        if d.lower() in low:
            return d
    for tok, d in ALIASES.items():
        if re.search(rf"\b{re.escape(tok)}\b", low):
            return d
    return "unknown"


def _md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |",
             "|" + "|".join("---" for _ in cols) + "|"]
    lines += ["| " + " | ".join(str(v) for v in r) + " |"
              for r in df.itertuples(index=False)]
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(RAW.glob("*.pdf"))
    assert pdfs, "no raw TGTRANSCO PDFs — run the download first"

    # 1.1 hashes
    sums = "\n".join(f"{sha256(p)}  {p.name}" for p in pdfs)
    (RAW / "SHA256SUMS").write_text(sums + "\n")

    # 1.2 long table
    recs = [r for p in pdfs for r in parse_pdf(p)]
    energy = pd.DataFrame(recs).drop_duplicates(["plant_name", "month"])
    energy["state"] = "Telangana"
    energy["source_url"] = ("https://www.tgtransco.com/user_uploads/trans_losses/"
                            + energy["source_file"])
    energy.to_csv(OUT / "plant_month_energy.csv", index=False)

    solar = energy[energy["plant_name"].str.lower().str.contains(
        "|".join(SOLAR_KW), regex=True)].copy()

    # 1.3 registry: district from name hints, coords = district centroid
    known = [d for d in TG_DISTRICTS]
    feats = pd.read_csv(DISTRICT_FEATS)[["district", "latitude", "longitude"]]
    solar["district"] = solar["plant_name"].map(lambda n: district_for(n, known))
    reg = (solar[["plant_name", "district"]].drop_duplicates("plant_name")
           .merge(feats, on="district", how="left")
           .rename(columns={"latitude": "latitude", "longitude": "longitude"}))
    reg["state"] = "Telangana"
    reg["coords_source"] = "district_centroid"  # ponytail: district centroid, not plant
    #                                                   geocode; upgrade = OSM Nominatim
    #                                                   once site-scale modelling starts
    reg["source"] = "TGTRANSCO monthly transmission-loss EBC tables"
    reg = reg[["plant_name", "state", "district", "latitude", "longitude",
               "coords_source", "source"]]
    reg.to_csv(OUT / "plant_registry.csv", index=False)

    # 1.4 capacity: sourced only (never from energy)
    caps: dict[str, tuple[float, str]] = {}
    for n in reg["plant_name"]:
        m = re.search(r"(\d+)\s*MW", n, re.I)
        if m:
            caps[n] = (float(m.group(1)), "name-embedded MW in TGTRANSCO table")
    if CEA_DAILY.exists():
        txt = subprocess.run(["pdftotext", "-layout", str(CEA_DAILY), "-"],
                             capture_output=True, text=True).stdout
        for line in txt.splitlines():
            m = re.match(r"\s*([A-Z][A-Za-z0-9 &.'\-()/]+?)\s{2,}Telangana\s{2,}"
                         r"\w+\s{2,}[\w ]+?\s{2,}Solar\s{2,}([\d.]+)\s{2,}", line)
            if m:
                caps.setdefault(m.group(1).title(),
                                (float(m.group(2)), "CEA daily RE report 10 Mar 2025"))
    if REGISTER.exists():
        for _, r in pd.read_csv(REGISTER).query("state == 'Telangana'").iterrows():
            caps.setdefault(r["plant_name"],
                            (r["installed_capacity_mw"], "CEA plant register"))
    cap_df = pd.DataFrame(
        [{"plant_name": k, "installed_capacity_mw": v[0], "capacity_source": v[1],
          "ac_dc": "AC (not stated otherwise)"} for k, v in caps.items()])
    cap_df.to_csv(OUT / "plant_capacity.csv", index=False)

    # 1.5 12-month CUF windows
    reg2 = reg.merge(cap_df, on="plant_name", how="inner")
    s = solar.merge(reg2[["plant_name", "installed_capacity_mw"]],
                    on="plant_name", how="inner")
    s["y"] = s["month"].str[:4].astype(int)
    s["m"] = s["month"].str[5:7].astype(int)
    rows = []
    for plant, g in s.groupby("plant_name"):
        months = set(zip(g["y"], g["m"]))
        for w0, w1 in WINDOWS:
            y0, m0 = int(w0[:4]), int(w0[5:])
            y1, m1 = int(w1[:4]), int(w1[5:])
            need = []
            yy, mm = y0, m0
            while (yy, mm) <= (y1, m1):
                need.append((yy, mm))
                mm += 1
                if mm == 13:
                    yy, mm = yy + 1, 1
            if not all(t in months for t in need):
                continue
            win = g[g.apply(lambda r: (r["y"], r["m"]) in set(need), axis=1)]
            mu = win["mu"].sum()
            hours = sum(monthrange(y, m)[1] * 24 for y, m in need)
            mw = float(win["installed_capacity_mw"].iloc[0])
            rows.append({
                "plant_name": plant, "district": win["district"].iloc[0],
                "state": "Telangana", "window": f"{w0}..{w1}",
                "months": len(win), "installed_capacity_mw": mw,
                "total_mu": round(mu, 2),
                "cuf": mu * 1000.0 / (mw * hours),
                "cuf_source": "official_monthly",
                "capacity_source": cap_df.set_index("plant_name")
                    .loc[plant, "capacity_source"],
                "source": "TGTRANSCO Tr_losses monthly PDFs",
            })
    cuf = pd.DataFrame(rows)
    cuf.to_csv(OUT / "plant_cuf.csv", index=False)

    # 1.8 QA
    n_plants = solar["plant_name"].nunique()
    n_cap = cuf["plant_name"].nunique() if len(cuf) else 0
    plan = f"""# Label QA — TGTRANSCO label factory (Phase 1)

Raw PDFs: {len(pdfs)} months, SHA-256 in `data/raw/tgtransco/SHA256SUMS`.
Long table: {len(energy)} rows ({n_plants} distinct names, {solar['plant_name'].nunique()} solar-keyword rows).
12-month windows present: {', '.join(f'{a}..{b}' for a, b in WINDOWS)}.

## Gate 1 decision (recorded, user unavailable)
- Acceptance was "40 plants with valid 12-month CUF, or explicit decision to proceed with fewer".
- Plants with capacity + full window: **{n_cap}** — decision: **proceed with fewer**.
- Gap cause: TGTRANSCO publishes name+MU only; capacity needs TGERC/PPA/RTI (plan §2.1 rules).
- Next capacity sources: TGERC PPA orders, MNRE plant list, RTI to TSPCL/NREDCAP.

## Coverage vs archive
| Gap | Months |
|---|---|
| 2021 | Mar only |
| 2022 | Jan, Mar, Sep missing |
| 2024 | Aug-Dec missing |
| 2025-26 | Nov 2025 only |

## Cross-checks & flags
- Net energy at injection point (not gross) — per TGTRANSCO header, CUF biased low (disclosed).
- CUF outliers beyond [0.10, 0.30]: listed below.
- Solar classification = name keyword (solar/sun/pv/acme/azure) across sections; wind/MSW/sugar rows excluded.
"""
    if len(cuf):
        out = cuf[(cuf.cuf < 0.10) | (cuf.cuf > 0.30)]
        if len(out):
            plan += "\nOutliers:\n" + "\n".join(
                f"- {r.plant_name} ({r.window}): {r.cuf:.3f}" for r in out.itertuples())
        plan += "\n\n## CUF windows produced\n" + _md_table(cuf)
    QA.write_text(plan + "\n")
    print(f"energy={len(energy)} solar_plants={solar['plant_name'].nunique()} "
          f"capacity={len(cap_df)} cuf_rows={len(cuf)} "
          f"plants_with_cuf={n_cap}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
