# License Register (blueprint L1–L3; E8 companion)

One row per dataset. `NC` = non-commercial only — drop before any commercial use.
// ponytail: single register; add a row only when a dataset is actually fetched.

| Dataset | License | Commercial? | Attribution (exact) | Local path / URL | Version + date |
|---|---|---|---|---|---|
| AlphaEarth Satellite Embedding | CC BY 4.0 | Yes | The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind. | GEE `GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL` | v1.1, model v2.1, fetched Oct 2026 |
| GEM Global Solar Power Tracker | CC BY 4.0 | Yes | Global Energy Monitor | _pending fetch §B_ | version + download date TBD |
| Global Solar Atlas (GHI/DNI/PVOUT) | CC BY 4.0 | Yes | World Bank / Solargis; footer + paper | GSA v2 download URLs | v2, fetched Oct 2026 |
| Global Renewables Watch | TBD (verify) | TBD | TBD | _pending fetch §B_ | TBD |
| TransitionZero SAM | **CC BY-NC 4.0** | **NO** | TransitionZero Solar Asset Mapper, TransitionZero, May 2024 release. | `data/plant_labels/tz_sam_Q12024_analysis.csv` (global) + `tz_sam_india.csv` (2540 assets, 54 GW) via Zenodo 11368204, fetched Oct 2026. CAVEAT: constructed_before/after columns in CSV are Excel-mangled durations, unusable as dates — use GEE `tz_solar` asset or xlsx for temporal validation. | Q1 2024 |
| Kruitwagen 2018 inventory | Zenodo (verify terms) | Verify | Kruitwagen et al., Nature 2021 | _pending fetch §B_ | end-2018 snapshot |
| Ortiz 2022 India polygons | Paper terms (verify) | Verify | Ortiz et al., arXiv 2202.01340 | paper in `data/external_fetch/papers/` | 1363 farms |
| ESA WorldCover 2021 | CC BY 4.0 | Yes | Zanaga et al. 2022 + ESA | GEE / AWS `s3://esa-worldcover` | v200 |
| OpenStreetMap power/infra | ODbL 1.0 | Share-alike | © OpenStreetMap contributors | Geofabrik India PBF / Overpass | 2026-09-29 extract noted |
| gridfinder predicted grid | CC BY 4.0 | Yes | gridfinder authors | _Phase C_ | — |
| WorldPop density | CC BY 4.0 | Yes | WorldPop, Univ. of Southampton | hub.worldpop.org id=41746 | 2020 |
| GHSL built-up/pop | Open (JRC) | Yes | EC JRC GHSL | HDX / JRC FTP | R2023/R2025 |
| NASA POWER | Open (US Govt) | Yes | NASA POWER acknowledgement | API | note merge discontinuities |
| MCD19A2 AOD | Open (US Govt) | Yes | LP DAAC citation | Earthdata login required | V061 |
| SRTM 30m | Open (US public domain) | Yes | USGS/NASA | EarthExplorer / LP DAAC | v3 |
| IMD gridded rain/normals | Govt open | Yes | IMD citation (Pai et al. 2014 for 0.25°) | imdpune / data.gov.in | 1901–2024 |
| Census 2011 | Govt open | Yes | Registrar General & Census Commissioner | censusindia / data.gov.in PCA | 2011 |
| CEA/MNRE/NISE/SECI/Grid-India | Govt open | Yes | Publisher + report date | `data/official/` + `data/external_fetch/state/` | per-file dates |
| CPCB AQI | Govt open | Yes | CPCB + contributing agencies | portal / Kaggle mirrors | 2015–2025 |
| NISE open datasets (GHI/inverter) | Form-gated, research use | Verify | NISE | _not submitted_ | — |

Rules in force: L1 (this file), L2/L3 attribution strings are already in §7 of the blueprint
footer spec, L4 (62 MB NISE PDF + 13 MB topojson stay untracked; DVC later), L5 (version+date
column above doubles as the pin log).
