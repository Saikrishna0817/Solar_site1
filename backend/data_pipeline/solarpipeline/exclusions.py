"""L1 exclusion rules (blueprint §D1/§8.2 rung C1).

Pure rules on columns the pipeline already produces. Applied post-engineering in
core.py; `excluded`/`exclusion_reason` are labels-only (dropped from features like
cuf_source). Thresholds: EPA slope screen + MoEFCC/TNC land guidance (see blueprint §2E).
"""
import pandas as pd

# (column, operator, threshold, reason) — first match wins, order matters least first.
RULES = [
    ("slope_deg", ">", 6.0, "slope>6deg"),
    ("water_pct", ">", 20.0, "water-body"),
    ("wetland_pct", ">", 30.0, "wetland-ecosensitive"),
    ("tree_cover_pct", ">", 50.0, "forest-cover"),
    ("builtup_pct", ">", 50.0, "built-up"),
    ("cropland_pct", ">", 75.0, "prime-agriculture"),
]


def apply_exclusions(df: pd.DataFrame) -> pd.DataFrame:
    """Add `excluded` (bool) + `exclusion_reason` (str, C2: shown, never hidden)."""
    df = df.copy()
    df["excluded"] = False
    df["exclusion_reason"] = ""
    for col, op, thresh, reason in RULES:
        if col not in df.columns:
            continue
        hit = (df[col] > thresh) if op == ">" else (df[col] < thresh)
        hit = hit.fillna(False) & ~df["excluded"]
        df.loc[hit, "excluded"] = True
        df.loc[hit, "exclusion_reason"] = reason
    return df
