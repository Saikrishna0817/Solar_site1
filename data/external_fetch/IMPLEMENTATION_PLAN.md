# SolarSite-India — Start-to-End Implementation Plan (DEV, 2026-10-05)

Locked scope: **Hybrid plant+district · TS+AP pilot first · ML-correctness first**. `main` untouched.
Ponytail full: shortest path, YAGNI enforced, upgrade points marked `ponytail:`.

## Codemap (reuse — don't rebuild)

```
backend/data_pipeline/solarpipeline/{utils,data,features,eda,preprocess,core}.py  # keep, fix only
backend/data_pipeline/{main.py,phase2_3_pipeline.py,config/settings.py,datasources/* (+gee_alphaearth.py Phase 2)}
src/{ml/{config,data_loader,trainer,models/sk_models,optimization,pipelines/ml_pipeline,evaluation/core},api/{main,services/{inference,data}},cli/train.py}
frontend/src/{pages/*,services/api.js(dead),data/mockSites.js,hooks/useMapData.js}
data/{plant_cuf/solar_plants_india.csv(101),official/*,external_fetch/*}  # real target + validation
models/*.joblib + reports/*.csv  # artifacts, gitignored Phase 0
tests/test_{pipeline,features,utils}.py (29 pass, pipeline only)
```

## Phase 0 — Hygiene (½ day) [IN PROGRESS]

- Canonical entry: `src/cli/train.py`. `main.py`, `train_ensemble.py` get header pointers (not rewrites).
- `.gitignore` add: `models/*.joblib`, `ml_logs/`, `reports/*.csv`, `reports/figures/`.
- Root `.env.example` (`GEE_PROJECT_ID, VITE_API_URL, VITE_USE_MOCK`); prop-types import deleted (not added).
- `vite.config.js` `server.proxy /api → :8000`.
- Exit: `pytest tests/ -v` still 29/29.
- Skipped: MLflow, Docker, CI, TS migration.

## Phase 1 — Refactor-clean, minimal diffs (1 day)

1. `solarpipeline/utils.py` + `data.py`: `parents[4]→[3]` via shared helper.
2. `backend/data_pipeline/main.py` sys.path + `census_cea.process(outdir)` signature in caller.
3. `osm_infrastructure.py` outputs → `dist_nearest_*`; delete heuristic after real OSM runs.
4. Remove `/home/krishna/...` absolutes → `PROJECT_ROOT`; `districts_available` from CSV count.
5. Unify census growth to `CONFIG.census_compound_factor`.
- Exit: `phase2_3_pipeline.py --step all` runs fresh-clone on 60 districts.

## Phase 2 — Data mandal→district→state (2–3 days, one new collector)

1. Mandal centroids from fetched ADM3 topojson (filter TG/AP) — reuse `generate_all_india_centroids.py`.
   DONE (DEV): `scripts/generate_mandal_centroids.py` (stdlib-only, GADM L3) →
   `outputs/raw/shapefiles/telangana_ap_mandals_centroids.csv`, 190 rows (120 AP + 70 TG).
   GADM is pre-reorg: `district_gadm` is old (10+13); new-district join = spatial join on data machine.
   DONE (DEV): `scripts/assign_mandal_new_districts.py` (stdlib-only, Wikipedia TG-33/AP-28
   lists) → `district_new` column, 186/190 matched (4 genuinely absent from source lists:
   chipurupalle, korangal, mahbubnagar-town, jogipet — centroids usable via district_gadm).
   Frame validated: 60 = 33 TG + 26 AP + Markapuram (real since Dec-2025, data already collected);
   Polavaram (28th) pending data.
2. Fill via existing collectors only (`--centroids <csv>`).
3. NEW: `datasources/gee_alphaearth.py` — sample `GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL`
   (64 bands, 10 m, version-pinned in `PipelineConfig`, same `gee_helper.gee_retry` auth/buffer
   pattern as `gee_srtm.py`) → mean 64-vector per centroid → `aef_districts.csv`.
   Reuses buffer-median flow; ~40 lines. CC-BY-4.0, attribution in reports.
4. Hybrid targets with `cuf_source` flag; state CUF + NISE + SRRA as validation only.
- Exit: `master_engineered` 162 rows with source counts + `aef_districts.csv` present.
- Skipped: sup3r GAN, Bhuvan 1:10k pull — `ponytail: add when district→mandal error >5%`.

## Phase 3 — ML correctness (2–3 days)

1. Single `StandardScaler`, persist `preprocessor.joblib + rfe_mask.json`.
2. Wire `--use-real-cuf` → `plant|hybrid|physics`, sample-weighted loss.
3. `RFE≤8 feats`, shared HPO `ridge 1e-6..100 log`, KFold5 train-only; per-source metrics.
4. Physics fallback keeps simple formula + honest model card —
   `ponytail: pvlib chain when formula error vs SRRA >3%`; simple economics —
   `ponytail: PySAM server-side when bankable LCOE requested`.
5. One `test_ml_leakage.py` + scaler round-trip assert.
6. AlphaEarth usage, in this order (stop at first that works):
   a. Similarity search (no model): cosine distance of every site to top-5 plants' mean
      embedding → "find land like proven land" ranking; eyeball vs Kurnool/Anantapur.
   b. Cluster check: k-means on embeddings vs WorldCover barren% — replaces heuristic
      wasteland eyeballing.
   c. Regression features last: PCA 64→3–5 comps + ablation (with/without); keep only on CV gain.
      Never 64 raw bands on n≈160.
- Exit: per-source R² honest; `predict_cuf` reproduces training transform.

## Phase 4 — Backend + API live (1–2 days)

- FastAPI loads hybrid + preprocessor; point-inference; logging + rate-limit stub
  (`ponytail: auth when deployed beyond localhost`).
- Frontend consumes `api.js` (timeout/Abort/retry, loading/empty/error, debounce, pagination);
  `*`404 + ScrollToTop; seeded SHAP; fix `.sort()` mutation; memo list. Keep mock fallback.
- Exit: Dashboard lists 60 from API; `POST /v1/predict` returns hybrid + `cuf_source`.

## Phase 5 — Validate then expand (1–2 wks, only after pilot green)

- Validate vs NISE + CEA + SRRA; recalibrate weights to paper priors.
- Annual AEF refresh → change detection (2017→latest) flags sites with new construction/farms.
- Then 766-district + 101→200+ plants. Model card + PDF export.
- Still skipped: auth, PWA, i18n, rooftop, heatmaps, MLflow — each gets `ponytail:` when requested.
