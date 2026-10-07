# SolarSite-India — Paper Draft Material (target: Applied Energy)

Working document for Phase 7 (plan: `/home/saikrishna/Downloads/SolarSite_Fix_Plan-1.md`).
Everything below is written **before** the manuscript itself, per the plan's instruction
("write the limitations section first").

**Provenance flags used on every figure**

| Flag | Meaning |
|------|---------|
| `[OFFICIAL]` | verbatim from a government/agency file already in this repo |
| `[MEASURED]` | computed from repo data (CEA actual labels / tracked artifacts) |
| `[DERIVED]` | arithmetic on flagged inputs only; no new assumptions |
| `[ASSUMPTION]` | modelling choice or value **not yet sourced** — pending primary source |
| `[MODEL OUTPUT]` | produced by `scripts`/`src/ml` in this repo; reproducible via pytest + train CLI |
| `[PENDING]` | fetch blocked in this environment (network/credentials); upgrade path stated |

---

## 1. Limitations — the eight documented flaws (severity-rated, status-labelled)

These are the eight flaws named in the plan (seven "Known Issues From DEV Review" plus the
"No plant-level validation" flaw closed in Phase 4). Severity = impact on the paper's central
claim if the flaw were left unaddressed. Status = what this repo has already done about it.

| # | Flaw | Severity | Status | Evidence / where it lives now |
|---|------|----------|--------|-------------------------------|
| L1 | Honest retrain collapsed the circular score: CV R² negative for 4 of 6 models (target range only 0.1781–0.2080 CUF, n=13 plants, n_train_rows=10) `[MEASURED]` | **High** — bounds any generalisation claim | **OPEN** (inherent to label scarcity; disclosed, not hidden) | `models/metrics.json` (elastic_net CV R² +0.1953 is the only positive), `reports/ml_report.md` |
| L2 | `trainer.py` double-scaling wart (features scaled twice) | **Critical** — silent feature distortion | **FIXED** (Phase 3) | single persisted scaler `scaler_selected.joblib`, `test_ml_leakage.py` |
| L3 | `inference.py` clamped CUF silently | **High** — silent wrong outputs | **FIXED** (Phase 3) | clamp now logs a warning; missing features raise `ModelNotServable` |
| L4 | `main.py` (pipeline) fragile `except TypeError` fallback | **Medium** — masked real bugs | **REMOVED** (Phase 0: stale wrapper deleted) | `grep -r "except TypeError"` returns nothing; no root `main.py`/`train_ensemble.py` |
| L5 | `assign_mandal_new_districts.py` picked the first match on ambiguity | **High** — wrong district labels poison grouping | **FIXED** (Phase 0) | ambiguous rows get `district_new=""`, `_method="ambiguous"`, reported (`scripts/assign_mandal_new_districts.py:187`) |
| L6 | `baseline_c0.py` used placeholder daylight hours and derate | **High** — the serving gate depends on C0 being real | **FIXED** (Phase 3) | real pvlib SPA daylength + 14 % derate; C0 MAE **0.0074678** over 11 districts, Spearman ρ 0.9091 `[MODEL OUTPUT]` |
| L7 | AlphaEarth adds 64 dimensions against few rows (p ≫ n) | **High** — would reintroduce the overfit trap | **OPEN / NOT USED** (deliberate ceiling, METHODOLOGY §6) | `docs/NEXT_PHASES_PLAN.md` §AEF: embeddings allowed only after PCA to ~8 dims and only on CV gain |
| L8 | No plant-level validation | **High** — district averages can hide plant error | **MITIGATED** (Phase 4), not closed | `reports/heldout_validation.md`: on 3 held-out plants **C0 beats model** (MAE 0.0079 vs 0.0101) `[MEASURED]` |

**Claim-bearing reading of the table.** Two of eight flaws are still open (L1, L7), one is only
mitigated (L8). The paper's central claim must therefore be written as *"a leakage-audited,
CEA-label-only baseline for district/plant CUF in Telangana + AP, with a physics baseline that
still wins on held-out plants"* — not as a performance claim.

### 1.1 Additional disclosed limitations (beyond the eight)

- **Temporal mismatches** (hard rule): AP demand FY 2022-23 vs solar labels March 2024; NASA POWER
  is a climatology, not a plant-matched year. Every join of demand to generation carries this offset.
- **District frame is locked at 60** (TS 33 + AP 27), not 61 — Polavaram reorganisation not yet in
  frame; `ponytail:` ceiling comments record the upgrade path.
- **Choropleth geometry covers 23 of 60 districts** (GADM 4.1 ADM2 predates 2016/2022 re-orgs);
  frontend map data is honestly labelled *Demo data* until live mode (`VITE_USE_MOCK=false`).
- **GEE-dependent features are absent**: zonal statistics, WorldPop 2020, site-scale exclusion masks
  (METHODOLOGY §6 ceilings). No GEE credentials in this environment `[PENDING]`.
- **Independent cross-checks pending**: NREL PVWatts V8 and Global Solar Atlas comparisons
  (NREL DNS unresolvable; GSA returns 403) — METHODOLOGY §7 ceilings `[PENDING]`.
- **Baseline C0 is competitive**: it beats 4 of 6 models on CV and beats the model on the 3-plant
  hold-out. Any ablation must report against C0, not against zero.

---

## 2. Sources — explicit citation blocks

Each block is the form we will use in the manuscript's Data/Methods references. `[PENDING]`
marks a source we cite but could not fetch here.

### 2.1 Official statistics (in-repo, primary)

```
CENTRAL ELECTRICITY AUTHORITY (India).
Installed Capacity (in MW) of Power Stations located in the regions of Main Land and Islands,
as on 31.07.2026 (Utilities, including allocated shares).
File: data/official/IC_July2026.xlsx
Access: https://cea.nic.in/ (Monthly installed capacity report), downloaded 2026-07
Licence: Government of India, public.
Used for: state coal/lignite and RES capacity in the coal-to-solar scenario (§4).
```

```
CENTRAL ELECTRICITY AUTHORITY (India).
Monthly Renewable Energy Generation Report — July 2026.
File: data/official/RE_Monthly_Generation_report_July_2026.xlsx
Access: https://cea.nic.in/ , downloaded 2026-07.
Used for: state-wise RE generation cross-checks; CUF = MU x 1000 / (MW x 8760).
```

```
MNRE. State-wise installed renewable capacity, as on 31.07.2026.
File: data/official/mnre_statewise_31.07.2026.pdf
Access: https://mnre.gov.in/en/physical-progress/ (page snapshot also at
data/external_fetch/state/MNRE_physical_progress_page.html).
Used for: national/state solar split (ground / rooftop / hybrid / off-grid) context only.
```

```
CEA. Daily RE Generation Report, 10 March 2025.
File: data/external_fetch/state/CEA_daily_RE_10Mar2025.pdf
Used for: plant-level daily MU template (growth path from 13 in-scope plants).
```

```
NISE / MNRE. Solar PV Potential — Ground Mounted, 2025 (62 MB).
File: data/external_fetch/state/NISE_Solar_PV_Potential_GroundMounted_2025.pdf
Access: https://cdnbbsr.s3waas.gov.in/ (open).
Used for: district potential priors; replaces the 2014 748 GWp figure.
```

```
CEA CO2 Baseline Database for the Power Sector (latest edition).
Access: https://cea.nic.in/ (CO2 baseline database section).  [PENDING — not fetched]
Used for: grid/coal emission factor in §4. Until fetched, §4 quotes only a clearly
labelled assumption band; no CEA emission number is asserted in this repo.
```

### 2.2 Earth observation / geospatial (open licences)

```
NASA POWER Climatology (daily/decadal). Access: https://power.larc.nasa.gov/ , no key.
Accessed: 2026-10 (HTTP 200 verified in Phase 4). Licence: NASA, public domain.
Used for: GHI/DNI/temp/wind/humidity features; independent cross-check of satellite GHI.
Caveat: climatological — disclosed as temporal mismatch (§1.1).
```

```
ESA WorldCover 100 m land-cover, v200 (2021). Licence: CC-BY 4.0. [in-repo or URL-only]
SRTM elevation. Licence: public domain (NASA/USGS).
OpenStreetMap road/grid distances. Licence: ODbL 1.0.
Census of India 2011 PCA (village/town). Licence: Open Government Data (NDSAP).
GADM v4.1 / geoBoundaries IND ADM2-ADM3. Licence: non-commercial (GADM) / CC-BY 4.0.
Source register: data/external_fetch/SOURCES.md (URL, licence, access date per row).
```

### 2.3 Literature the method leans on (evidence → decision log)

```
Chakraborty et al. (2023). Ensemble ML for solar power, eastern India.
arXiv:2301.10159. File: data/external_fetch/papers/ensemble_solar_eastern_india_2301.10159.pdf
Used for: feature-reduction funnel (Pearson > 0.95 drop-one, Lasso/ElasticNet agreement),
train-only scaling, "beat the linear benchmark" gate. NOT used for: its ~96 % scores
(single rooftop, East India, different target).
```

```
ACRS 2024 (AB0011). XGBoost + GEE solar site suitability, Rajasthan.
File: data/external_fetch/papers/solar_site_rajasthan_ACRS2024_AB0011.pdf
Used for: GEE feature list and hyperparameter priors. NOT used for: its accuracy numbers
(random negative sampling inflates classification accuracy; classification != CUF regression).
```

```
Motiwala (2024). Utility-scale Indian solar CUF benchmark (~19 %).
URL-only in data/external_fetch/SOURCES.md §D. Used for: scale sanity-check of our
CEA-actual mean CUF 0.1917 [MEASURED, n=13].
```

```
CERC (2011) solar performance regulations; Chaudhari et al. (2016) climate-CUF correlations
(CWE2016.html, in-repo). Used for: CUF driver priors (radiation >> humidity > temperature)
and the decision to treat correlations as non-causal.
```

```
Brown et al. (2025), AlphaEarth Foundation Model / Annual Embeddings (AEF).
[abstract-level use; claims mapped in docs/NEXT_PHASES_PLAN.md §AEF]
Used for: novelty positioning (§3) — similarity search and PCA-ablated features ONLY.
```

---

## 3. Novelty & positioning (AlphaEarth) — honest status

**Claim we intend to make.** The novelty is *methodological discipline*, not accuracy:
CEA-only labels, a physics baseline that is allowed to win, group CV by district, and a
serving gate that refuses to deploy a model the baseline beats — demonstrated on a
deliberately label-poor region (13 plants, 60 districts) where most published pipelines
report inflated random-split scores.

**Where AlphaEarth fits.** Per `docs/NEXT_PHASES_PLAN.md` §AEF (three Brown et al. 2025
claims mapped to concrete uses):

1. **Similarity search (build first).** Cosine distance from each district/mandal to the
   mean embedding of the top-5 measured plants — no training, so no p ≫ n risk.
2. **LULC/vegetation proxy.** One AEF vector (or k=8 cluster id) replaces separate
   NDVI/Dynamic-World/GHSL fetches — costs 1 degree of freedom, not 64.
3. **Regression features, PCA-ablated.** 64 → 3–5 PCs, retained only on LOGO-CV gain.

**Evidence status (do not overstate).** The GEE collector exists
(`backend/data_pipeline/datasources/gee_alphaearth.py`) but **has never been run**: no GEE
credentials in this environment `[PENDING]`. Therefore:

- We claim *no* AlphaEarth-derived result in this revision.
- §3 of the manuscript must read "planned extension" until the collector runs and the
  PCA ablation beats the current 43-feature set on LOGO-CV.
- Hard ceiling already recorded in METHODOLOGY §6: embeddings never enter without PCA to
  ≲8 dims, and never at n≈13 rows.

**Positioning statement for the target venue (draft).**
> Prior Indian solar-siting work scores sites against simulated or classification labels and
> reports 0.9+ accuracies. We instead publish a *negative-result-tolerant* pipeline on real
> CEA generation: a physics baseline (pvlib SPA + 14 % derate) that still beats our best
> regularised model on held-out plants, and a serving gate that will not deploy a weaker
> model. The contribution is the auditable protocol (labels, exclusions, group CV, gate) and
> the release of a 60-district, plant-level CUF frame for Telangana + AP.

---

## 4. Scenarios — coal-to-solar and CO₂ reduction

All inputs flagged. No emission factor is asserted as sourced (§2.1 `[PENDING]`).

**Inputs**

| Quantity | Value | Flag |
|---|---|---|
| AP coal + lignite capacity (State+Private+Central) | 12,911.1 MW (12,730.8 + 180.2) | `[OFFICIAL]` IC_July2026.xlsx row 169, as on 31.07.2026 |
| TG coal + lignite capacity | 13,997.6 MW (13,936.3 + 61.3) | `[OFFICIAL]` row 173 |
| Combined coal + lignite | **26,908.7 MW** | `[DERIVED]` sum of the two above |
| Combined RES (MNRE) capacity | 19,010.4 MW (AP 13,385.4 + TG 5,625.0) | `[OFFICIAL]` rows 169/173 |
| All-source installed capacity TG+AP | 53,804.8 MW (AP 31,114.9 + TG 22,690.0) | `[OFFICIAL]` rows 169/173 |
| Plant CUF used for displaced generation | **0.1917** (mean of 13 in-scope CEA plants, range 0.1781–0.2080) | `[MEASURED]` `data/plant_labels/plant_dataset.csv` |
| Emission factor for coal generation | **0.9–1.05 t CO₂/MWh — assumption band only** | `[ASSUMPTION]` pending CEA CO₂ Baseline Database fetch |

**Method.** Replace a fraction *f* of combined coal+lignite capacity with solar at the
measured CUF: `generation = f × 26,908.7 MW × 8,760 h × 0.1917`;
`CO₂ avoided = generation × EF`.

| Replaced share *f* | Solar MW | Annual generation | CO₂ avoided (EF 0.9–1.05) |
|---|---|---|---|
| 10 % | 2,691 MW | 4.52 TWh `[DERIVED]` | 4.07–4.74 Mt/yr `[DERIVED, ASSUMPTION EF]` |
| 25 % | 6,727 MW | 11.30 TWh `[DERIVED]` | 10.17–11.86 Mt/yr `[DERIVED, ASSUMPTION EF]` |
| 50 % | 13,454 MW | 22.59 TWh `[DERIVED]` | 20.33–23.72 Mt/yr `[DERIVED, ASSUMPTION EF]` |

**Explicitly excluded from the arithmetic (state in the paper):** transmission/distribution
limits, curtailment, land availability, storage, seasonal mismatch between solar output and
the coal plants' generation profile, and embedded carbon of the replacement plant. These are
why the table is a *capacity-equivalent bound*, not a forecast.

---

## 5. Storage optimisation (REopt) — status

Plan item: "Add REopt storage optimisation after the model is stable." Status: **not run**
`[PENDING]` — the NREL developer endpoints are unreachable from this environment (same DNS
failure as PVWatts V8), and the free REopt Lite API requires that endpoint.

- **Ceiling recorded:** do not fabricate storage sizing; add it only when the API is reachable
  or a local re-implementation (rule-based 2 h / 4 h storage on the scenario in §4) is agreed.
- **Trigger to unpark:** model gate stays green (elastic_net still beats C0) **and** NREL
  endpoint resolves.
- `ponytail:` — no local storage model written now; upgrade path = REopt Lite API call in
  `scripts/` behind the same `--scenario` CLI shape as §4.

---

## 6. What the manuscript must never claim (guard list)

1. Any accuracy that is not in `models/metrics.json` / `reports/heldout_validation.md`.
2. That the model beats the physics baseline on held-out plants (it does not; C0 wins 0.0079 vs 0.0101).
3. AlphaEarth-derived features (collector never ran).
4. A CEA CO₂ emission factor before §2.1's `[PENDING]` source is fetched.
5. 700+ plant labels, 42/43-feature demos, "5-fold CV", or 101-plant coverage as *model* facts.
6. Random or seeded-fake SHAP as real attributions (live `/shap` only).
