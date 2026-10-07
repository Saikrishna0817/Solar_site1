#!/usr/bin/env python3
"""
Assign 190 GADM mandals to NEW districts using Wikipedia mandal lists.
Reconciled frame: TG 33 + AP 27 = 60 district rows (PipelineConfig.expected_districts).
The AP wiki list also carries Polavaram, so the *name* map covers 61 — Polavaram's
mandals are assigned but have no district data row yet.
Stdlib only (json/re/csv/difflib). Appends `district_new` to the mandal CSV.

Matching is by normalized mandal name within the same state; difflib fallback
(cutoff 0.80) with an unmatched/ambiguous report. Old GADM mandals predate splits,
so names persist 1:1 in the new district lists.

Usage:
    python scripts/assign_mandal_new_districts.py
"""
import csv
import difflib
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FETCH = PROJECT_ROOT / "data" / "external_fetch" / "mandal"
MANDAL_CSV = (
    PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "raw" / "shapefiles"
    / "telangana_ap_mandals_centroids.csv"
)


def _clean_mandal(text):
    text = re.sub(r"\[\[([^|\]]+\|)?([^\]]+)\]\]", r"\2", text)  # [[X|Y]] -> Y
    text = text.replace("_", " ")  # Khammam_Rural -> Khammam Rural (before splits below)
    text = re.sub(r"\s*\(.*?\)", "", text)  # drop (urban)/(rural)/(Pt)
    text = re.sub(r"\s+mandal\s*$", "", text, flags=re.I)
    text = re.sub(r"\s*\b(urban|rural)\b\s*$", "", text, flags=re.I)  # bare Urban/Rural splits
    text = re.sub(r"[^a-z0-9 ]", "", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def _clean_district(text):
    text = re.sub(r"\[\[([^|\]]+\|)?([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"<ref.*?(</ref>|/>)", "", text)  # cite footnotes on district cells
    text = re.sub(r"^rowspan\s*=\s*\"?\d+\"?\s*\|?", "", text).strip()  # rowspan carry cells
    text = re.sub(r"^style\s*=.*$", "", text).strip()
    text = re.sub(r"\s+district\s*$", "", text, flags=re.I).strip()
    return text


# Old (GADM) district -> new districts carved from it (TG GO 2016, AP Gazette Apr-2022).
OLD2NEW = {
    "adilabad": ["Adilabad", "Nirmal", "Mancherial", "Kumuram Bheem"],
    "karimnagar": ["Karimnagar", "Jagtial", "Peddapalli", "Rajanna Sircilla"],
    "nizamabad": ["Nizamabad", "Kamareddy"],
    "medak": ["Medak", "Sangareddy", "Siddipet"],
    "warangal": ["Warangal", "Hanamkonda", "Jangaon", "Mahabubabad", "Mulugu", "Jayashankar"],
    "khammam": ["Khammam", "Bhadradri", "Mulugu", "Mahabubabad"],
    "hyderabad": ["Hyderabad"],
    "mahbubnagar": ["Mahbubnagar", "Nagarkurnool", "Nagarukurnool", "Wanaparthy", "Narayanpet", "Jogulamba", "Rangareddy"],
    "nalgonda": ["Nalgonda", "Suryapet", "Yadadri"],
    "rangareddy": ["Rangareddy", "RangaReddy", "Medchal", "Vikarabad"],
    "srikakulam": ["Srikakulam", "Parvathipuram Manyam"],
    "vizianagaram": ["Vizianagaram", "Parvathipuram Manyam"],
    "visakhapatnam": ["Visakhapatnam", "Anakapalli", "Alluri Sitharama Raju"],
    "eastgodavari": ["Kakinada", "Konaseema", "East Godavari", "Polavaram"],
    "westgodavari": ["West Godavari", "Eluru", "East Godavari"],
    "krishna": ["Krishna", "NTR", "Eluru"],
    "guntur": ["Guntur", "Palnadu", "Bapatla"],
    "prakasam": ["Prakasam", "Markapuram", "Bapatla"],
    "nellore": ["Nellore", "Sri Potti Sri Ramulu Nellore", "Tirupati"],
    "chittoor": ["Chittoor", "Tirupati", "Annamayya"],
    "kadapa": ["YSR Kadapa", "Kadapa", "Y.S.R.", "Annamayya"],
    "ysr": ["YSR Kadapa", "Kadapa", "Y.S.R.", "Annamayya"],
    "kurnool": ["Kurnool", "Nandyal"],
    "anantapur": ["Anantapur", "Anantapuram", "Sri Sathya Sai"],
}

# Hand-verified GADM-old-name -> wiki-new-name aliases (transliteration only).
# Town mandals absent from the wiki lists (nandyal, ongole, jogipet, korangal,
# mahbubnagar-town, …) stay unmatched on purpose — centroids remain usable via
# district_gadm. No guessing.
ALIASES = {
    "vishakhapatnam": "visakhapatnam", "cuddapah": "kadapa", "utnur": "utnoor",
    "zahirabad": "zaheerabad", "borgampad": "burgampahad", "nagarkarnul": "nagarkurnool",
    "mahbubnagar": "mahabubnagar", "narsapur": "narasapuram", "suluru": "sullurpeta",
    "hyderabad": "amberpet",
    "guntur": "guntur east", "nizamabad": "nizamabad north",  # town halves; same district either way
    "chipurupalle": "cheepurupalli", "punganuru": "punganur",
    "suriapet": "suryapet", "wanparthy": "wanaparthy",
    "narayankher": "narayankhed", "sangareddi": "sangareddy",
    "atamkur": "atmakur",
}


def _district_in_row(row):
    """Return (display_name, rowspan) for a district link in its own table cell.

    Only cells without `*` qualify — mandal disambiguation links like
    [[Kamalapur, Warangal (urban) district|Kamalapur]] live inside `*` lines.
    """
    for cell in row.split("\n|"):
        if "*" in cell:
            continue
        m = re.search(r"\[\[([^\]]*district[^\]]*)\]\]", cell, flags=re.I)
        if m:
            disp = _clean_district(m.group(1).split("|")[-1])
            if re.match(r"^\d+\s", disp):  # lead-text links like [[List of districts|33 districts]]
                continue
            span = re.search(r"rowspan\s*=\s*\"?(\d+)\"?", cell)
            return disp, int(span.group(1)) if span else 1
    return None, 0


def parse_tg(wikitext):
    """TG wikitable mixes rowspan-first sections and trailing-link sections.
    rowspan=N claims the next N-1 mandal rows; unclaimed groups flush at the
    next district link."""
    mapping, current, pending, remaining = {}, None, [], 0
    for row in wikitext.split("|-"):
        mandals = [_clean_mandal(m) for m in re.findall(r"^\*\s*(.+)$", row, flags=re.M)]
        mandals = [m for m in mandals if m]
        district, span = _district_in_row(row)
        if district:
            current = district
            mapping.setdefault(current, []).extend(pending + mandals)
            pending, remaining = [], max(span - 1, 0)
        elif mandals and current is not None and remaining > 0:
            mapping.setdefault(current, []).extend(mandals)
            remaining -= 1
        else:
            pending.extend(mandals)
    if pending and current:
        mapping.setdefault(current, []).extend(pending)
    return mapping


def parse_ap(wikitext):
    """AP wikitable: |Mandal|Revenue Division|District rows (rowspan carry-forward)."""
    mapping, current = {}, None
    for row in wikitext.split("|-"):
        cells = [c.strip() for c in re.split(r"\n\|\s*", row) if c.strip()]
        if not cells:
            continue
        mandal = _clean_mandal(cells[0])
        if len(mandal) > 60:  # post-table junk (references/categories), never a mandal name
            continue
        for cell in cells[1:]:
            name = _clean_district(cell)
            if not name or len(name) > 60:  # post-table junk, never a district
                continue
            if not re.search(r"\[\[[^\]]+\]\]", cell):  # district always linked
                continue
            if "revenue" in name.lower() or "division" in name.lower():
                continue
            if "district" in cell.lower() or current is None:
                current = name
        if mandal and current:
            mapping.setdefault(current, []).append(mandal)
    return mapping


def main():
    tg_wt = json.load(open(FETCH / "wiki_mandals_TG.json"))["parse"]["wikitext"]["*"]
    ap_wt = json.load(open(FETCH / "wiki_mandals_AP.json"))["parse"]["wikitext"]["*"]
    tg, ap = parse_tg(tg_wt), parse_ap(ap_wt)
    print(f"TG: {len(tg)} districts, {sum(map(len, tg.values()))} mandals")
    print(f"AP: {len(ap)} districts, {sum(map(len, ap.values()))} mandals")

    lookup = {"Telangana": tg, "Andhra Pradesh": ap}
    rows = list(csv.DictReader(open(MANDAL_CSV)))
    unmatched, ambiguous = [], []
    for r in rows:
        dist_map = lookup[r["state"]]
        norm = _clean_mandal(r["mandal"])
        norm = ALIASES.get(norm, norm)
        old_key = re.sub(r"[^a-z]", "", r["district_gadm"].lower())
        allowed = OLD2NEW.get(old_key, [])
        allowed_n = [re.sub(r"[^a-z0-9]", "", a.lower()) for a in allowed]
        in_scope = {d for d in dist_map if not allowed or any(
            a in re.sub(r"[^a-z0-9]", "", d.lower()) or
            re.sub(r"[^a-z0-9]", "", d.lower()) in a for a in allowed_n)}
        hits = [d for d in in_scope if norm in dist_map[d]]
        if len(hits) == 1:
            r["district_new"], r["_method"] = hits[0], "exact"
            continue
        if len(hits) > 1:
            # Never write a guess: set order is arbitrary, so hits[0] was random.
            ambiguous.append((r["mandal"], r["state"], sorted(hits)))
            r["district_new"], r["_method"] = "", "ambiguous"
            continue
        pool = [(m, d) for d in in_scope for m in dist_map[d]]
        pool.sort()
        best = difflib.get_close_matches(norm, [m for m, _ in pool], n=1, cutoff=0.80)
        if best:
            r["district_new"] = next(d for m, d in pool if m == best[0])
            r["_method"] = "fuzzy"
        else:
            unmatched.append((r["mandal"], r["state"], r["district_gadm"]))
            r["district_new"], r["_method"] = "", "unmatched"

    with open(MANDAL_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["mandal", "district_gadm", "district_new",
                                          "state", "latitude", "longitude"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in w.fieldnames})

    print(f"Matched: {sum(1 for r in rows if r['district_new'])}/{len(rows)} "
          f"(fuzzy: {sum(1 for r in rows if r['_method'] == 'fuzzy')})")
    for m, s, hits in ambiguous:
        print(f"  AMBIGUOUS {m} ({s}): {hits}")
    for m, s, g in unmatched:
        print(f"  UNMATCHED {m} ({s}, gadm:{g})")


if __name__ == "__main__":
    main()
