# Label & Feature Methodology

**Scope:** Telangana + Andhra Pradesh only · 60-district frame (61 names; Polavaram pending) ·
dataset v2 locked. Anything flagged below is also carried into the limitations section.

## 1. The label

Only one definition is allowed:

```
CUF = annual actual generation (MWh) / installed capacity (MW) / 8760
    = annual_generation_mu * 1000 / (installed_capacity_mw * 8760)
```

- Recomputed from MU/MW in both places that produce a label
  (`solarpipeline/utils.py::load_real_cuf`, `scripts/build_plant_dataset.py`) so a
  pre-rounded `annual_cuf` column cannot drift from the definition. Current drift across
  the in-scope register: **0/13 plants differ by >0.002** (max 0.0005).
- `cuf_source` records provenance. Allowed values are exactly `cea_plant` and `physics`;
  `scripts/build_plant_dataset.py` asserts this on every run.

## 2. What may and may not train a model

| Label source | Rows | Trains a model? |
|---|---|---|
| `cea_plant` — CEA actual MU ÷ MW ÷ 8760 | 13 plants / 11 districts | **Yes** (default) |
| `physics` — `GHI × PR / 24`, a formula of the features themselves | 49 districts | **No** — ablation only |

Physics-derived CUF is the cause of the reported R² ≈ 0.996 circularity: it is computed
from `avg_ghi` and `avg_temp`, which are also features. `DataConfig.cuf_source_filter`
defaults to `cea_plant`; `--cuf-source all` exists only for ablation and must never be
quoted as a result.

**Not labels, ever:** TZ-SAM capacity/location, population-weighted district aggregates,
NISE/state potential scores, or any simulated P50 figure.

## 3. Plant-level dataset

- Built by `scripts/build_plant_dataset.py` → `data/plant_labels/plant_dataset.csv`
  (13 rows: Telangana 7, Andhra Pradesh 6).
- Plants are joined to **district** features from `master_dataset_engineered.csv`
  (60-district frame). Plant metadata that would reconstruct the label
  (`installed_capacity_mw`, `annual_generation_mu`) is excluded from the feature set.
- District reorganisation names are matched through
  `solarpipeline/utils.py::DISTRICT_ALIASES` (`anantapur → anantapuram`,
  `kadapa → ysr kadapa`, `mahbubnagar → mahabubnagar`) — these three aliases recover
  all 13 in-scope plants from 8.
- District-frame labels are the **capacity-weighted mean** of the plants in that
  district (previously: whichever plant sorted first).

### Ceiling: 13 plants, not 700

Offline, the only CEA sources available are this register (102 plants nationally) and
daily RE-report PDFs, whose single-day figures are seasonally biased. The CEA API
endpoints hang and the NREL/PVWatts endpoints do not resolve in this environment.
`ponytail:` marked in `scripts/build_plant_dataset.py` with the upgrade path: monthly
CEA RE-generation XLS per plant, then SECI/state DISCOM official registers.

## 4. Temporal mismatches (disclosed, not smoothed)

| Feature/label | Vintage | Mismatch |
|---|---|---|
| AP demand | FY 2022–23 | vs solar features dated **March 2024** |
| Population | Census **2011**; 37/60 districts reverse-estimated from a 2024 projection at ~1%/yr | 13-year gap on the census side |
| Plant register | Provenance **not recorded** — the file enters the repo in a single commit titled `changing values` (`c56a710`, 2026-08-27) | vintage unverified; cross-check against CEA monthly reports before publication |
| Weather/radiance | NASA POWER climatology | not a plant operating year |

No interpolation, back-casting, or alignment is applied across these; they are reported
as-is.

## 5. District frame

`config/settings.py` holds the 33 Telangana + 27 Andhra Pradesh frame = **60**.
Polavaram (61st AP district) is not present in the source data; the frame is deliberately
locked at 60 with `ponytail:` ceiling comments at the three places that would need to
change (`config/settings.py`, `solarpipeline/utils.py::PipelineConfig.expected_districts`,
`scripts/assign_mandal_new_districts.py`).

## 6. Features

- **Composite scores built from the label's own inputs are not features.**
  `effective_ghi` (GHI × temperature derate) and `solar_potential_score` (a hand-written
  4-term average of normalised GHI/DNI/temp/humidity) were removed in Phase 2: a model
  that selects them is reproducing the baked-in assumption (and, for the physics label,
  the formula) rather than learning site signal. Raw GHI/DNI/temp/humidity remain.
  `installed_solar_capacity_mw` is dropped as a target leaker (audit #3).
- Correlation filter: greedy Pearson > 0.95 drop-one, fitted on **training rows only**.
- **Feature selection is refit inside every CV fold** (`Trainer.fit_selector` called
  from `Trainer.cross_validate`), so the CV score cannot be propped up by a selector
  that has already seen the held-out rows. Collinear filtering is likewise re-fitted
  per fold. Selection for the final deployed model is fitted on all training rows.

### Phase 2 ceilings (environment-blocked)

| Plan item | What runs today | Upgrade path |
|---|---|---|
| Zonal statistics instead of centroid sampling | district centroid + 500 m/1 km buffer means | `rasterio`/`rasterstats` + the rasters — `rasterio` is not installed and the GEE credentials are absent (`ee` is installed, `~/.config/earthengine` is not) |
| WorldPop 2020 instead of Census 2011 | Census 2011, 37/60 districts reverse-estimated | direct GeoTIFF from data.worldpop.org + `rasterio` (no GEE needed) |
| Exclusion rules at site scale | district land-cover averages | GEE WorldCover/OSM sampled at candidate points — GEE credentials required |
| AlphaEarth embeddings | unused | only after PCA to ~8 dims, and only if the rows justify 8 more dimensions |

## 7. Validation

- **Held-out plants (Gate 3):** `scripts/phase3_residual_ci.py` splits the 13 labelled
  plants (20 %, seed 42) and scores the *same pre-registered model spec* the API serves
  against C0 → `models/gate.json`. Current result: **residual ridge wins** (0.0064 vs
  0.00785) and its LOGO district-bootstrap ΔMAE CI is [−0.00565, −0.00115] (excludes 0),
  so Gate 3 passes and ML serves. The earlier 43-feature artifact scored in
  `scripts/validate_heldout.py` → `reports/heldout_validation.md` **lost** there
  (C0 0.0079 vs 0.0101) — kept as history, not served.
- **Energy balance:** `scripts/phase4_energy_balance.py` compares TGTRANSCO solar plant
  sums against CEA state totals for the same month → `reports/energy_balance.md`
  (measured ratios 0.70–0.79: EBC tables cover a subset of state solar — flagged).
- **Baseline:** `scripts/baseline_c0.py` (pvlib PVWatts chain, daylength from SPA at
  each centroid) is the bar. `reports/ml_report.md` carries a "Beats C0?" column per
  model on the pooled out-of-fold predictions.
- **Serving rule:** `src/api/services/gate.py` reads `models/gate.json` (Gate 3 verdict +
  conformal interval) — if Gate 3 fails, only the C0 baseline serves, labelled as such.

### Validation ceilings

| Plan item | Status | Upgrade path |
|---|---|---|
| Benchmark vs NREL PVWatts V8 | blocked — `developer.nrel.gov` does not resolve from this environment (curl exit code 000), so the offline `pvlib` chain cannot be cross-checked against NREL's service | `pvwatts/v8.json` with an NREL api_key once the host is reachable; the local chain already implements the same model |
| Compare GHI with Global Solar Atlas | blocked — `api.globalsolaratlas.info` answers `403 Missing Authentication Token` for the point-query endpoints | register for a GSA token, or use the documented CSV export from the web UI; NASA POWER (already wired, reachable) is the independent cross-check available today |
