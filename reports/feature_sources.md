# Phase 2 — feature rebuild: sources, attempts, ceilings

Gate 2 evidence: **no label-derived columns** in the feature tables
(`tests/test_phase_gates.py::test_feature_table_has_no_label_derived_columns`),
**every pre-registered feature has a source row** (table below), and the model
feature list is pre-registered in `models/pre_registered_features.json`
(authored before `scripts/phase3_residual_ci.py` first ran; the script reads
that file and never overwrites an existing one).

## 2.6 Pre-registered model features (n=13, n/10 = 1.3 → 2 features)

| Feature | Source | Grain / vintage | Flag |
|---|---|---|---|
| `avg_ghi_kwh_m2_day` | NASA POWER climatology (point API, wired in the pipeline) | district-centroid annual mean, not label year | `[OFFICIAL]` + temporal-mismatch disclosed (METHODOLOGY hard rules) |
| `max_temp_c` | NASA POWER climatology (point API) | same | `[OFFICIAL]` + same mismatch |

Rationale (also in the JSON): irradiance sets the ceiling, cell temperature
derates it. 2 > 1.3 is the documented n/10 rounding-up for an identifiable
linear model (`models/pre_registered_features.json` → `n_over_10`, `note`);
upgrade path: revisit at n ≥ 40 plants after TGTRANSCO capacity merge.

The full district frame (51 columns) is a **data** frame, not the served
model's feature set; its provenance rows live in `data/external_fetch/SOURCES.md`
§A–I and `docs/AUDIT_REPORT.md`.

## Attempt log — what we tried and where it stopped

| # | Plan task | Status | Evidence / ceiling | Upgrade path |
|---|---|---|---|---|
| 2.1 | GSA rasters (GHI/DNI/DIF/PVOUT/TEMP/OPTA) | **BLOCKED** | `api.globalsolaratlas.info` → `403 Missing Authentication Token`; web UI is an SPA (no raster URL) — same result as recorded in METHODOLOGY §7 | GSA token, or documented CSV export from the web UI; NASA POWER already serves as the independent GHI cross-check |
| 2.2 | Plant polygons + zonal statistics | **BLOCKED** | `rasterio`/`rasterstats` not installed; GEE credentials absent (`ee` importable, `~/.config/earthengine` missing); registry coords are district centroids (`coords_source=district_centroid`, flagged) | install `rasterio` + fetch polygons (Microsoft/TNC/TZ-SAM: `data/plant_labels/tz_sam_india.csv` on hand); or GEE `reduceRegions` once creds exist |
| 2.3 | Terrain + pre-construction land cover | **PARTIAL** | district `slope_deg`/`aspect_deg`/LULC % already in the frame (district means); "year before commissioning" impossible retroactively for commissioning years before the LULC epoch (2017/2021) | year-matched LULC via IO-ESRI annual stack (SOURCES §G) |
| 2.4 | Climate (NASA POWER, IMD) + aerosol | **DONE (district grain)** | NASA POWER wired; IMD rainfall validates `annual_rainfall_mm` (SOURCES §G); AOD column present (MOD08; daily MAIAC listed in SOURCES §E as not fetched) | MAIAC daily AOD (Earthdata login) |
| 2.5 | Validate GHI vs SRRA stations | **BLOCKED** | no free SRRA station-level series found; recorded in `reports/energy_balance.md` §4.3 | RTI/next data drop; holdout labels remain TGTRANSCO/CEA |
| 2.7 | Plant age / technology flags | **NOT AVAILABLE** | commissioning dates not documented in the TGTRANSCO tables or CEA register we hold | TGERC/RTI (see `reports/label_qa.md` open items) |
| 2.8 | WorldPop 2020 swap | **BLOCKED** | needs direct GeoTIFF fetch + `rasterio` (neither available here); population features remain Census-2011/2024-projected | download WorldPop India 1 km (SOURCES §G URL) once `rasterio` installs |

Flagged derived figures: none — every cell above is an observed status or an
existing flag elsewhere in the repo.
