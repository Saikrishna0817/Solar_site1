"""
SolarSite-India — CEA Monthly Generation + Installed Capacity → Capacity Utilisation Factor (CUF)
NOTE: These are STATE-LEVEL figures.  District-level CUF is an approximation.
"""
import pandas as pd
from pathlib import Path

# State-level CEA figures (FY 2023-24)
DATA = [
    ("Telangana", "Solar", 4116, 74.56),
    ("Andhra Pradesh", "Solar", 7024, 135.40),
]

def compute_cuf():
    df = pd.DataFrame(DATA, columns=["state", "fuel", "installed_mw", "annual_generation_mu"])
    df["annual_generation_mwh"] = df["annual_generation_mu"] * 1000  # MU → MWh
    df["capacity_utilisation_factor"] = (
        df["annual_generation_mwh"] / (df["installed_mw"] * 8760)
    ).round(4)
    df["cuf_percent"] = (df["capacity_utilisation_factor"] * 100).round(2)
    out = Path(__file__).parent.parent / "outputs" / "raw" / "cea" / "cuf_state_level.csv"
    df.to_csv(out, index=False)
    print(df[["state", "installed_mw", "annual_generation_mu", "cuf_percent"]].to_string(index=False))
    print(f"Saved to {out}")
    return df

if __name__ == "__main__":
    compute_cuf()
