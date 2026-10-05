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

## F. Next (no code built yet)

1. Mandal centroids from ADM3 topojson (filter TG/AP) — pending go-ahead.
2. Fill 60-district + 101-plant features via NASA POWER + GEE + real OSM.
3. Hybrid training per locked scope (plant `annual_cuf` + district physics, `cuf_source` flag, ML-correctness first).
4. Validate vs NISE district potential + CEA state CUF + SRRA before 766-district expansion.
