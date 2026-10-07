#!/usr/bin/env python3
"""C0 physics baseline rung (blueprint §8.2): pvlib PVWatts chain per district.

Reads master_dataset_clean.csv, writes c0_baseline.csv
(district, state, c0_cuf, label_cuf, cuf_source).

Daylength is derived per district from pvlib SPA sunrise/sunset at the centroid,
averaged over the year — this replaces the old placeholder of a flat 12 h.
CUF = daily DC energy (kWh per kWp) / 24 h.

Standalone script (not pipeline-wired) so feature shapes and tests stay untouched.

ponytail ceilings — each one lifts a rung, in this order:
  * POA = GHI: no tilt/azimuth, so no incidence-angle or row-shading loss
  * flat PVWatts system-loss derate (14%, the NREL default) instead of per-site
    soiling/availability/snow
  * no AC/inverter model (`pvwatts_ac` + inverter specs) and no tracking
  * daily-average irradiance only — no sub-hourly variability or clipping
"""
from pathlib import Path

import pandas as pd
from pvlib.pvsystem import pvwatts_dc
from pvlib.solarposition import sun_rise_set_transit_spa
from pvlib.temperature import pvsyst_cell

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MASTER = PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed" / "master_dataset_clean.csv"
OUT = PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "processed" / "c0_baseline.csv"

DERATE = 1 - 0.14  # PVWatts default system losses (14%)
YEAR = 2024        # any non-leap year: only daylength matters, not the date itself


def mean_daylength_hours(lat: float, lon: float) -> float:
    """Annual mean sunrise->sunset hours at one point (pvlib SPA, altitude 0)."""
    times = pd.date_range(f"{YEAR}-01-01", f"{YEAR}-12-31", freq="D", tz="UTC")
    sun = sun_rise_set_transit_spa(times, lat, lon, how="numpy")
    return float((sun["sunset"] - sun["sunrise"]).dt.total_seconds().mean() / 3600.0)


def main():
    df = pd.read_csv(MASTER)
    dl = [mean_daylength_hours(r.latitude, r.longitude) for r in df.itertuples()]

    poa_day = df["avg_ghi_kwh_m2_day"] * 1000 / dl  # W/m2, averaged over daylight
    tcell = pvsyst_cell(poa_day, df["avg_temp_c"], df["avg_wind_speed_m_s"])
    kw_avg_daylight = pvwatts_dc(poa_day, tcell, 1000.0, -0.004) / 1000 * DERATE

    out = pd.DataFrame({
        "district": df["district"],
        "state": df["state"],
        "daylength_h": [round(x, 3) for x in dl],
        "c0_cuf": (kw_avg_daylight * pd.Series(dl, index=df.index) / 24).round(4),
        "label_cuf": df["cuf"],
        "cuf_source": df.get("cuf_source", "physics"),
    })
    out.to_csv(OUT, index=False)

    cea = out[out["cuf_source"] == "cea_plant"]
    print(f"Saved {len(out)} rows to {OUT}")
    print(f"daylength: {min(dl):.2f}-{max(dl):.2f} h (placeholder was 12.00)")
    print(f"C0 mean={out['c0_cuf'].mean():.4f}  label mean={out['label_cuf'].mean():.4f}")
    print(f"vs physics label: rho={out['c0_cuf'].corr(out['label_cuf'], method='spearman'):.4f}")
    if len(cea) >= 3:
        print(f"vs CEA-actual ({len(cea)} districts): "
              f"rho={cea['c0_cuf'].corr(cea['label_cuf'], method='spearman'):.4f}  "
              f"MAE={abs(cea['c0_cuf'] - cea['label_cuf']).mean():.4f}")
    else:
        print("vs CEA-actual: too few districts to score")


if __name__ == "__main__":
    main()
