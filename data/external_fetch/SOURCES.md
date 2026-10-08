# External Data & Research Sources — DEV fetch (2026-10-05)

Branch: `DEV` (main untouched). This folder is **fetched raw material only** — no pipeline code built.
Local files under `data/external_fetch/`; everything else is URL-only with access notes.

## A. Mandal / sub-district (ADM3)

| Item | Local file | Source URL | Access / license | Use in project |
|------|------------|------------|------------------|----------------|
| geoBoundaries IND ADM3 topojson (~13 MB) | `mandal/geoBoundaries-IND-ADM3.topojson` | https://raw.githubusercontent.com/srisbalyan/India-Administrative-Maps/main/geoBoundaries-IND-ADM3.topojson | Open, CC-BY-4.0, direct curl OK | Mandal/tehsil/taluk polygons → mandal centroids for TS (~594) + AP (~670) |
| geoBoundaries IND ADM2 simplified (82 KB) | `mandal/geoBoundaries-IND-ADM2_simplified.json` | https://raw.githubusercontent.com/srisbalyan/India-Administrative-Maps/main/geoBoundaries-IND-ADM2_simplified.json | Open, CC-BY-4.0 | Light district overview; full 46 MB ADM2 skipped (slow) |
| GADM v4.1 India shapefile | — URL-only | https://gadm.org/data.html → `gadm41_IND_shp.zip`; https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_IND_shp.zip | Open, direct download | Handled by `backend/.../datasources/gadm_boundaries.py`; ADM2 district + ADM3 where available |
| Census 2011 mandal PCA (village/town-wise) | — URL-only | https://censusindia.gov.in/census.website/data/census-tables ; https://www.data.gov.in/catalog/villagetown-wise-primary-census-abstract-2011-andhra-pradesh | Open (data.gov.in NDSAP), per-district XLS (e.g. Kurnool) | Households, pop, 0-6, SC/ST, literate, workers at mandal/village grain; DCHB Part-B PDFs per district (e.g. `DH_2011_2818_PART_B_DCHB_PRAKASAM.pdf`) |
| Bhuvan Panchayat SIS-DP LULC 1:10k (5.8 m LISS-IV) | — URL-only, login | https://bhuvan-app1.nrsc.gov.in/thematic/thematic/index.php | ISRO/NRSC, login required | Mandal land-use (replaces coarse WorldCover at mandal scale) |
| Dharani (TG) / AP Bhulekh land records | — portal-only | State revenue portals | No bulk download | Mandal parcel fragmentation / tenancy — manual field check only |

## B. District

| Item | Local file | Source URL | Access / license | Use |
|------|------------|------------|------------------|-----|
| NIWE SRRA brochure (world's largest ground network) | `district/NIWE_SRRA_brochure.pdf` (2.8 MB) | https://niwe.res.in/static/pdf/training/special_ITC_SRA_brochure.pdf (curl `-k`, self-signed cert) | Govt (MNRE/NIWE), open | 111 SRRA stations (51 ph-1 + 60 ph-2, 29 states/3 UTs), 1-sec→1-min, WRC/WRR + WMO traceable, BSRN QC — ground truth to validate satellite GHI |
| NREL India GHI/DNI page pointer | `district/NREL_India_GHI_page.html` | https://data.openei.org/submissions/343 | CC-BY, page OK; zip links expire | 10-km METEOSAT 2002-2011 GHI/DNI GIS zips — download manually from page |
| Global Solar Atlas rasters | — URL-only | https://globalsolaratlas.info/download ; https://datacatalog.worldbank.org/search/dataset/0038641/... | Open (Solargis/World Bank) | GHI/DIF 250 m, PVOUT/TEMP 1 km, OPTA 4 km; cross-check vs NASA POWER |
| NASA POWER | — API, no key | https://power.larc.nasa.gov/data-access-viewer | Open API | Already used in `nasa_power_v2.py`; climatology + daily point/regional |
| IMD Pune gridded rain/temp + data.gov.in | — URL-only | https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_Bin.html (0.25° 1901-2024) ; https://dsp.imdpune.gov.in/home_gridded_climatology.php ; https://www.data.gov.in/catalog/rainfall (daily district rainfall CSV+API) | Govt open, some via NDC request `data.service@imd.gov.in` | District rainfall/temperature normals; replaces coarse PRECTOTCORR at district scale |
| NRSC LULC 1:50k / 1:250k + ALanCRIT DEM | — login | https://www.nrsc.gov.in/.../Dataproducts_Thematic_overview.php ; https://bhuvan-app1.nrsc.gov.in/2dresources/datadownload | ISRO, login | District LULC + wasteland + DEM |
| NISE open datasets (GHI, 475 kWp inverter, district potential) | — form-gated | https://nise.res.in/page/open-data-section ; https://nise.res.in/open-data/2 | Govt, form (name/email/org/purpose) — not submitted | Request GHI + inverter XLSX (21-27 June 2026) + ground-mounted district potential for training features |

## C. State / national

| Item | Local file | Source URL | Access | Use |
|------|------------|------------|--------|-----|
| NISE Solar PV Potential Ground-Mounted 2025 (62 MB) | `state/NISE_Solar_PV_Potential_GroundMounted_2025.pdf` | https://cdnbbsr.s3waas.gov.in/.../1759223689.pdf | Govt (NISE/MNRE), open | Methodology Fig.4 p13 (Solargis + OSM validated), State Table 5 p31, district tables; replaces 2014 748 GWp; recalibrate weights from this, not ad-hoc |
| CEA installed capacity Mar 2026 (576 KB) | `state/CEA_installed_capacity_Mar2026.pdf` | https://cea.nic.in/wp-content/uploads/installed/2026/03/Website.pdf | Govt open | All-India 532.7 GW (solar 150.2 GW); refresh May/Aug 2026 (`.../installed/2026/05/website.pdf`, `.../08/IC_Aug_2026.pdf` 554.5 GW) |
| CEA RE generation overview May 2026 (3 MB) | `state/CEA_RE_generation_May2026_overview.pdf` | https://cea.nic.in/wp-content/uploads/2021/03/Broad_Overview_of_RE_Generation_May_2026.pdf | Govt open | State + ISGS plant MU → CUF = MU*1000/(MW*8760) |
| CEA daily RE 10 Mar 2025 (898 KB) | `state/CEA_daily_RE_10Mar2025.pdf` | https://cea.nic.in/wp-content/uploads/daily_reports/10_March_2025_Daily_RE_Generation_Report.pdf | Govt open | Plant-level daily MU + capacity template to grow 101→200+ plants |
| CEA API catalog pointer | `state/CEA_API_catalog.html` | https://cea.nic.in/api-for-central-electricity-authority-data?lang=en | Govt open | Installed capacity / supply / transmission / RE composition APIs |
| MNRE physical progress page pointer | `state/MNRE_physical_progress_page.html` | https://mnre.gov.in/en/physical-progress/ ; https://mnre.gov.in/physical-progress | Govt open | Monthly solar 157.05 GW split (ground 118.79 / rooftop 27.88 / hybrid 4.06 / off-grid 6.31 as of May 2026); state-wise PDF link inside page |
| CEA RE generation portal (live dashboard) | — URL-only | https://gen-re.cea.gov.in/ | Govt open dashboard | Daily solar/wind MU, ISGS %, 12-mo trends — scrape or manual for CUF cross-check |

## D. Research papers

Downloaded to `papers/` (open access). Paywalled items are URL-only — read abstract/methods, do not blindly trust metrics.

| File | Topic | What to take | What NOT to trust blindly |
|------|-------|--------------|---------------------------|
| `ensemble_solar_eastern_india_2301.10159.pdf` (2 MB, Chakraborty et al., BITS/TCS, arxiv) | Ensemble (Bagging/Boosting/Stacking/Voting) on 10 kWp IIEST Shibpur field + SRRA weather, ~96% stacking/voting | Test-bed + feature selection/reduction pipeline; stacking needs real generation data | Single rooftop, East-India climate only; not transferable to TS/AP utility scale |
| `solar_site_rajasthan_ACRS2024_AB0011.pdf` (1.1 MB, ACRS 2024) | Rajasthan XGBoost suitability (acc 0.982 train / 0.934 test), GEE (elev/wind/temp/LULC/NDVI/CO/irradiation/pop/dist-residential) + OSM + QGIS, 80/20 | GEE+OSM feature list + suitability-map flow | Binary solar/non-solar random negatives inflate accuracy; classification ≠ CUF regression |
| `solar_Kolkata_ISPRS_2022.pdf` (8.3 MB, Bhanja/Roychowdhury) | Kolkata metro fuzzy-AHP GIS-MCDA | Exclusion masks + weight audit trail | Metro rooftop logic ≠ wasteland utility |
| `GIS_AHP_IJSAT2025.pdf` (1.5 MB, 12 p) | GIS+AHP 5-criteria solar farm tool | 5-criteria minimal viable AHP for pilot | Small case study; validate weights locally |
| `solar_power_ML_arxiv2303.07875.pdf` (439 KB) | KNN/DNN/RF/LGBM stacking, claimed 99% AUC | Stacking + meta-learner pattern | 99% AUC on private data, no benchmark; AUC wrong metric for regression — treat as cautionary |
| `SolarTformer_IMD_2026.pdf` (877 KB, Basu et al., IMD Kolkata + Jadavpur) | Transformer short-term PV forecasting, cyclic time encoding | Attention for time-series; IMD authors = credible met input | China-station data in paper; re-train on SRRA, not copy weights |
| `CUF_climate_CWE2016.html` (pointer, Chaudhari et al.) | Gujarat PV CUF 16.96-22.41% vs climate; corr solar-CUF 0.96, humidity -0.67, ambient-temp +0.76 | Correlation priors: radiation ≫ humidity(neg) > temp; seasonal Dec-vs-Mar spread | Single plant Oct-Mar only; correlations ≠ causal |
| URL-only: Motiwala 2024 (CUF 19% benchmark, tariffs ₹2.51-3.92), CERC 2011 solar performance (CUF drivers: radiation/temp/design/inverter/degradation), Sharma 2025 Punjab hybrid AHP-TOPSIS/MLP, Ranjgar 2026 GIS-MCDM review, Nazaripour 2026 Nevada fuzzy-AHP (warns ML overfits local patterns — directly relevant to our physics R² trap), Guntupalli 2025 South-India ANN-AHP (Vizag/Guntur top), Ortiz 2022 India 1363 farms mapping (92%, NRSC LULC), Anantapur E3S 2023 GIS-AHP (Srikanth/Sajja, VRSEC Vijayawada — same Rayalaseema geology as AP pilot), Esri India Bhadla/Pavagada/Kurnool GIS case | — | Use for weight priors (irradiance ~20%, flatness/substation ~15%), validation protocol (90.6% future plants in high-suitable), exclusion rules (slope <6°, grid/road <0.5 mi) | Each has region/tech bias; re-validate on TS/AP + NISE 2025 before adopting any weight |

## E. Authoritative portal checklist (bookmark, all govt)

MNRE physical progress · CEA installed-capacity / RE-generation / API / gen-re dashboard · NISE open-data + potential reports/maps · NIWE resource map (`https://maps.niwe.res.in/resource_map/map/solar` point GHI/DNI/DHI/GTI/AEP/CUF/P50) + SRRA · IMD Pune gridded + data.gov.in rainfall/IMD catalogs · NRSC Bhuvan thematic/NOEDA/ALanCRIT · Census censusindia + data.gov.in PCA · GADM + geoBoundaries (CC-BY) · Global Solar Atlas/Solargis + NREL OEDI (CC-BY) · SECI/IREDA/Grid India for plant lists/PPA CUF benchmarks.

## G. Second sweep (2026-10-05, direct + indirect)

| Item | Local file / URL | Access | Use |
|------|------------------|--------|-----|
| IMD 0.25° daily rainfall 1901-2024 + district normals + DSP gridded climatology | URL-only: `https://www.imdpune.gov.in/cmpg/Griddata/Rainfall_25_Bin.html`, `https://dsp.imdpune.gov.in/home_gridded_climatology.php`, `https://ckandev.indiadataportal.com/dataset/climate-data` (district CSVs) | Open (some via NDC request) | Validates `annual_rainfall_mm`; district normals as cross-check |
| ESA WorldCover 10m 2021 (S1+S2, CC-BY-4.0) + IO-ESRI 10m annual LULC 2017-2024 | URL-only (AWS open buckets, no account): `s3://esa-worldcover`, `s3://io-10m-annual-lulc` | Open | Independent LULC check vs GEE WorldCover; IO time series for change detection |
| WorldPop India 1km density 2020 (17 MB) + GHSL built-up/pop 100m | URL-only: `https://hub.worldpop.org/geodata/summary?id=41746`, JRC FTP via HDX | CC-BY-4.0 / open | Replaces census-only density with gridded population_pressure |
| OSM power (Geofabrik energy schema, India PBF 1.6 GB, Overpass live, earth-osm CLI) | `district/Geofabrik_OSM_Energy_Schema.pdf` ✅ + URLs | ODbL | Real substation/line distances (replaces heuristic); India has 3951 plants + 473,956 km lines mapped |
| MCD19A2 MAIAC AOD daily 1km V061 (Stage-3 validated) | URL-only (Earthdata login): `https://doi.org/10.5067/MODIS/MCD19A2.061` | Open w/ login | Upgrades MOD08 monthly AOD to daily dust/soiling signal |
| SRTM 1-arcsec global (DOI 10.5066/F7PR7TFT) | `district/SRTM_Quick_Guide_LPDAAC.pdf` ✅ + EarthExplorer/LP DAAC | Open | Offline DEM backup when GEE unavailable |
| Grid India NLDC daily PSP (solar MU) + Kaggle mirror (2018+, auto-updated) | `state/GRIDINDIA_PSP_26Feb2024.pdf` ✅ + kaggle URL | Open | Daily solar generation time series → CUF trends, complement to CEA monthly |
| SECI own-projects + JVs (11820 MW parks) + CEA solar-parks status Apr-2024 | `state/CEA_SolarParks_Status_Apr2024.pdf` ✅ (51p, park/village/district/MW/land) | Open | Ground-truth park locations (Tadipatri, Mylavaram, Ramagiri) for validation + plant-list growth |
| CPCB AQI/PM (portal + archive-downloader GitHub + Kaggle 2015-2020/2023-2025) | URL-only | Open | PM2.5/PM10 soiling proxy where AOD gaps exist |

## F. Next (no code built yet)

1. Mandal centroids from ADM3 topojson (filter TG/AP) — pending go-ahead.
2. Fill 60-district + 101-plant features via NASA POWER + GEE + real OSM.
3. Hybrid training per locked scope (plant `annual_cuf` + district physics, `cuf_source` flag, ML-correctness first).
4. Validate vs NISE district potential + CEA state CUF + SRRA before 766-district expansion.

## H. Label sources (Phase 1)

| Item | Local path | Source URL | Access / licence | Use |
|------|------------|------------|------------------|-----|
| TGTRANSCO monthly transmission-loss PDFs (29 months, Mar-2021 … Nov-2025, gapped) | `data/raw/tgtransco/Tr_losses_*.pdf` + `data/raw/tgtransco/SHA256SUMS` | `https://www.tgtransco.com/user_uploads/trans_losses/Tr_losses_<Mon>-<YYYY>.pdf` | Downloaded 2026-10-08; Indian govt publication, licence not stated (treat as public, attribution: TGTRANSCO) | Label factory `scripts/build_tgtransco_labels.py` → `data/plant_labels/plant_month_energy.csv`, `plant_registry.csv`, `plant_capacity.csv`, `plant_cuf.csv`; QA `reports/label_qa.md` |

**Naming gotcha:** the month token in the URL/filename is *not* normalised — both full and
abbreviated forms exist in the archive (`Tr_losses_May-2024.pdf` alongside `Tr_losses_Aug-2023.pdf`;
also `Tr_losses_April-2022.pdf`/`Tr_losses_April-2024.pdf` vs `Tr_losses_Apr-2023.pdf`). Any fetch
loop must try both `<FullMonth>` and `<Abb>` before concluding a month is missing. Parser already
accepts both (`scripts/build_tgtransco_labels.py`, `MONTHS` map).

## I. Phase 4 / Phase 6 fetches (2026-10-08)

| Item | Local path | Source URL | Access / licence | Use |
|------|------------|------------|------------------|-----|
| CEA daily RE report (State-Wise cumulative month totals), 3 files: 2024-06-30, 2024-07-31, 2025-11-30 | `data/official/Report-*.xlsx` + `data/official/SHA256SUMS` | `https://gen-re.cea.gov.in/public/uploads/dailyReport/excel/Report-<YYYY-MM-DD>.xlsx` | Open (Indian govt, licence not stated); archive starts 2024-06-30 (older dates 404) | Phase 4 energy balance: CEA state solar (MU) same-month vs TGTRANSCO plant sums |
| CEA CO2 Baseline Database v20.0 (data year 2023-24, dated 2024-12-01) | `data/official/CO2_Database_Version_20.0_2023_24.xlsx` (sha256 in `data/official/SHA256SUMS`) | `https://cea.nic.in/wp-content/uploads/2021/03/CO2_Database_Version_20.0_2023_24.xlsx` (from `https://cea.nic.in/cdm-co2-baseline-database/?lang=en`) | Open | Phase 6: SOM 0.9615 / CM 0.7568 / WAvg 0.7275 tCO2/MWh → PAPER §4 scenario EF band |
| AP plant-wise monthly generation search (tried apspdcl/aptransco/apsldc/nredcap/CEA/Wikipedia/NREL/GSA) | `data/external_fetch/state/AP_monthly_data_memo.md` | see memo | — | Phase 1.6: source log + RTI draft [PENDING RTI] |
