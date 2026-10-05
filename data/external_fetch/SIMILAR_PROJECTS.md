# Similar Projects — intakes for SolarSite-India (DEV, 2026-10-05)

Note: live web search API was down during this pass, so this inventory is built from
direct doc fetches (GitHub topics, pvlib/sup3r/PySAM repos, PVGIS JRC page) plus the papers
and official portals already fetched under `data/external_fetch/`. Verify versions before adopting.

## A. Open-source modeling libraries (adopt code, not just ideas)

### 1. pvlib-python (1.7k stars, BSD-3, NumFOCUS) — https://github.com/pvlib/pvlib-python
What it is: community PV performance toolbox (clear-sky, transposition, cell temp, inverters, PR).
Intakes for us:
- Replace `compute_cuf_theoretical(ghi,temp)=ghi*PR/24` with `pvlib.clearsky`, `pvlib.temperature.pvsyst_cell`,
  `pvlib.pvsystem.pvwatts_dc` chain — validated, cited (JOSS 2023), same inputs we already fetch.
- Use `pvlib.iotools.get_pvgis_tmy` / `get_nasa_power` readers instead of hand-rolled NASA parsing.
- Copy their variable-naming convention + example gallery structure for our `src/ml` docs.

### 2. pvanalytics (pvlib org, 143 stars) — https://github.com/pvlib/pvanalytics
What it is: QC, filtering, feature labeling for PV plant time series.
Intakes:
- Borrow `pvanalytics.qc` + `features` for CEA daily/MU cleaning before CUF = MU*1000/(MW*8760).
- Borrow their ghi-limit + clear-sky outlier flags for SRRA validation step.

### 3. PySAM / NLR-pysam (150 stars, BSD-3) — https://github.com/NatLabRockies/pysam
What it is: Python wrapper for NREL System Advisor Model (techno-economic: LCOE, NPV, payback, degradation).
Intakes:
- Replace `frontend/src/services/calculations.js` toy economics (CRF 10%, NPV *12) with PySAM
  `Pvwattsv8 + Singleowner` defaults for LCOE/NPV/payback/annual generation + 25-yr degradation.
- Keep our UI, call PySAM server-side in FastAPI `/predict` (not client-side).

### 4. sup3r (NLR, 140 stars, GAN super-resolution) — https://github.com/NatLabRockies/sup3r
What it is: downscales coarse climate (100 km/day) → hyperlocal (0.5–4 km, 5–60 min), validated
Nature Energy 2024 + PNAS 2020.
Intakes:
- Pattern for mandal problem: train/validate downscaler from district GHI → mandal GHI using
  historical pairs, instead of naive centroid copy. Use their DataHandler + train/inference split as template.
- Don't run full GAN now — borrow validation protocol (bias + spatial-structure checks).

## B. Resource / screening platforms (adopt UX + data patterns)

### 5. Global Solar Atlas v2.13 (World Bank/Solargis) — https://globalsolaratlas.info
Site info card per point: DNI/GHI/DIF/GTI-opta/OPTA/TEMP/ELE + PVOUT + horizon/sunpath + printable reports.
Intakes:
- Copy SiteAnalysis layout: per-year cards + map data min-max + PV config (tilt/azimuth/kWp) → our
  `SiteDetail` already mirrors this, keep field names aligned (GHI/DNI/DIF/GTI/OPTA/PVOUT).
- Data parity: GHI/DIF 250 m, PVOUT/TEMP 1 km rasters — use as cross-check layer for NASA POWER.

### 6. EU PVGIS 5.3 / 6-beta (JRC, free, no registration, API + TMY + EC CODE Python backend)
Intakes:
- Copy API design: non-interactive `GET` tools + TMY download + horizon shading — model our
  `/v1/sites`, `/v1/predict`, `/v1/states` on PVGIS tools structure.
- Reuse PVGIS TMY concept for `monthlyGeneration`/`yearlyProjection` charts (replace random SHAP/monthly).

### 7. NREL NSRDB / RE Explorer / PVWatts (US DOE)
Intakes:
- RE Explorer exclusion-layer pattern (protected areas, slope, grid) → our EDA/preprocess masks.
- PVWatts hourly → monthly aggregation for GenerationChart; document assumptions like they do.

### 8. NIWE solar map + NISE potential maps (India govt)
- NIWE `maps.niwe.res.in` point query (GHI/DNI/DHI/GTI/AEP/CUF/P50) → parity target for our `/predict` response.
- NISE 2025 ground-mounted report (already fetched, 62 MB) → state Table 5 + district tables as validation labels.

## C. Farm-footprint mapping (labels, not CUF)

### 9. Ortiz et al. 2022 India 1363 solar farms (Nature Sci Data, arXiv:2202.01340, 92% acc, NRSC 60 m LULC)
Intakes: use polygons for land-cover conversion stats (74% on natural/agri land) + negative-sample strategy.
Don't use for CUF — no generation data.

### 10. Home-Assistant solar forecast projects (Zara-Toorox Solar-Forecast-ML 292 stars local transformer;
rany2 Open-Meteo integration 164 stars)
Intakes: local-inference pattern + Open-Meteo as free fallback met source when NASA POWER is down.
Don't copy home-automation scope.

## D. Academic site-selection (methods to borrow, metrics to distrust)

- Rajasthan ACRS2024 XGBoost, Anantapur E3S GIS-AHP, Kolkata ISPRS fuzzy-AHP, Punjab Sharma-2025 hybrid,
  Ranjgar-2026 review, Nazaripour-2026 Nevada (overfit warning), Guntupalli-2025 South-India ANN-AHP —
  all detailed in `data/external_fetch/SOURCES.md` §D.
- Intake: exclusion thresholds (slope <6°, grid/road <0.5 mi), weight priors (irradiance ~20%,
  flatness/substation ~15%), validation (90.6% future plants in high-suitable zones).
- Caution: inflated accuracies from random negatives / single sites — always re-validate on TS/AP + NISE.

## E. Commercial (don't clone, borrow checklists)

RatedPower / Aurora / PVcase: exclusion layers, cable-routing cost, yield + uncertainty (P50/P90) reports,
PDF export. Intake: add P50/P90 + exclusion reasons + PDF report to our Results page; keep MIT-compatible code only.

## F. Prioritized intakes for our locked scope (Hybrid / TS+AP pilot / ML-first)

1. pvlib chain for physics fallback + `iotools` NASA reader (kills custom formula risk).
2. PySAM economics server-side (kills toy LCOE/NPV).
3. pvanalytics QC for CEA MU cleaning (kills noisy CUF).
4. PVGIS-style API + TMY for predict/sites (kills mock lock-in).
5. Global Solar Atlas card parity for SiteAnalysis fields.
6. sup3r validation pattern for district→mandal downscale later (not full GAN now).
7. NISE/CEA/SRRA as validation labels (not training leaks).
