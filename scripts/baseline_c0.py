#!/usr/bin/env python3
"""C0 physics baseline rung (blueprint §8.2): pvlib PVWatts-chain CUF per district.

Reads master_dataset_clean.csv, writes c0_baseline.csv (district, c0_cuf, physics_cuf).
Standalone script (not pipeline-wired) so feature shapes and tests stay untouched.
ponytail: DAYLIGHT_H=12 and flat 0.85 derate are placeholders; per-site sun-hours
from NSRDB/CAMS time series when the L2 time-series upgrade lands.
"""
from pathlib import Path

import pandas as pd
from pvlib.pvsystem import pvwatts_dc
from pvlib.temperature import pvsyst_cell

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MASTER = PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed" / "master_dataset_clean.csv"
OUT = PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed" / "c0_baseline.csv"

DAYLIGHT_H = 12.0
DERATE = 0.85


def main():
    df = pd.read_csv(MASTER)
    poa_day = df["avg_ghi_kwh_m2_day"] * 1000 / DAYLIGHT_H
    tcell = pvsyst_cell(poa_day, df["avg_temp_c"], df["avg_wind_speed_m_s"])
    kw_per_kwp = pvwatts_dc(poa_day, tcell, 1000.0, -0.004) / 1000 * DERATE
    out = pd.DataFrame({
        "district": df["district"],
        "state": df["state"],
        "c0_cuf": (kw_per_kwp * DAYLIGHT_H * 365 / 8760).round(4),
        "physics_cuf": df["cuf"],
    })
    out.to_csv(OUT, index=False)
    print(f"Saved {len(out)} rows to {OUT}")
    print(f"C0 mean={out['c0_cuf'].mean():.4f} physics mean={out['physics_cuf'].mean():.4f} "
          f"rank-corr={out['c0_cuf'].corr(out['physics_cuf'], method='spearman'):.4f}")


if __name__ == "__main__":
    main()
