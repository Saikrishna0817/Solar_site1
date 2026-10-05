# Next-Phases Plan — every decision backed by a paper (DEV, 2026-10-05)

Status quo (committed `adfe4c7`): Phase 0+1 done, AEF collector built, 190 mandals mapped
(186 to new districts), 60-frame validated (33 TG + 26 AP + Markapuram). No ML changes yet.
Papers on disk: `data/external_fetch/papers/`. Ponytail full — numbers below are gates, not wishes.

## Decision log (paper → our choice)

| # | Decision | Paper (file) | Evidence → choice |
|---|----------|--------------|-------------------|
| 1 | Target = measured `annual_cuf`, hybrid w/ `cuf_source` flag | Motiwala 2024 (abstract): utility CUF 19% benchmark; CERC 2011 (fetched ref): CUF = actual/maximum, drivers radiation/temp/design/inverter/degradation | Physics `GHI*PR/24` can only score ~fidelity to itself. Train on plant MU/MW; expect R² 0.75–0.90, not 0.99. |
| 2 | Features ≤8, keep: GHI, DNI, temp, humidity, wind, elevation/slope, LULC, grid/road dist | Chakraborty et al. 2023 (`ensemble_...pdf` §3.2.2): 40→18 (avg-only readings) →9 via Lasso+ElasticNet agreement + Pearson>0.95 drop-one (final: RH,AT,WS,WD,GR,DiffR,DirR,ISR,SA); ACRS 2024 (`solar_site_rajasthan...pdf` §3.1): 12 feats incl. NDVI/CO/pop/infra-dist | Our 39→RFE-8 mirrors their funnel. AEF embeddings cover the NDVI/LULC signal we lack (see §AEF). |
| 3 | Pearson >0.95 drop-one BEFORE training | Chakraborty §3.2.2 (pairs HSR/ISR, GR/GE, DiffR/DiffE removed) | Our 21 pairs r>0.9 get the same treatment; already started in `preprocess.py`. |
| 4 | Classical benchmark first (Ridge/LR), ensembles must beat it | Chakraborty §4.2: linear RMSE ~415 benchmark; Table 8 | Keep Ridge-HPO as the bar; promote only on CV gain. |
| 5 | Voting BEFORE stacking on real target | Chakraborty Table 8–9: Voting 0.96/313s ≈ Stacking 0.96/315s, but voting trains 192s vs stacking 981s (5×) | Our stacking R² 0.009 collapse was deterministic-target artifact, not proof stacking fails. Re-test voting-first on hybrid data; stacking only if CV gap >0.01. |
| 6 | RF/XGB heavily regularized; distrust train R² | ACRS Table 2: RFR train 0.958 → test 0.691 (overfit gap on n=755!); XGB sweep: colsample 0.8, gamma 0, lr 0.1, max_depth 9→(ours: ≤3 at n≈160), min_child_weight 3, subsample 0.8 | Gate on test/CV, never train. Start XGB from their hyperparams. |
| 7 | 80/20 split, RMSE+R², ~20 accuracy repeats | Chakraborty §4.2 + §4.3.1 (avg of 20 runs) | Adopt: 80/20 stratify state, report mean±std over 20 seeds for model comparison. |
| 8 | Mean-impute (not drop) sensor gaps; train-only stats | Chakraborty §3.2.1 (mean imputation keeps volume) | Already our rule; extend to AEF nulls (cloud-gap pixels → district median). |
| 9 | Suitability map = dense grid predict + 5 classes | ACRS §3.3: sample AOI at 0.0003° (~30m), per-point predict, meshgrid→tiff, 5 classes (not/less/moderate/high/most) | Mandals first (190 pts, cheap), 30m grid only for shortlisted districts (compute cost). |
| 10 | Validate vs existing/future plants (ROC / hit-rate) | Rane et al. 2024 (in ACRS refs): MIF map AUC 0.839 vs discovered farms; Almasad et al. 2023: 90.6% future projects fall in high-suitable zones | Gate: ≥85% of 101 plants in top-2 suitability classes, else reweight. |
| 11 | Weight priors: irradiation ≫ grid/substation > slope/land | Al Garni & Awasthi 2017 (50+ paper survey, via IOP review): irradiation #1, then power-line proximity, slope | Start Ridge/readout weights near 20/15/15/10 (solar/flatness/substation/grid), fit the rest. Recalibrate from NISE-2025 state tables. |
| 12 | Hard exclusions: slope, forest/water, road/grid distance | EPA decision tree + Arizona REOA (fetched excerpts): slope <6° (optimal <2%), grid/road <0.5 mi else uneconomic | Encode as pre-ML masks in `preprocess.py`, not learned features. |
| 13 | EML underestimates → conservative CUF | Chakraborty §4.3.1 (EML underestimates output) | Report lower-bound CUF to investors; matches PPA caution (PPAs signed above 19% design). |

## How AlphaEarth is used (mapped to Brown et al. 2025 claims)

AEF paper claims we rely on: (a) 64-dim annual embeddings compress Sentinel-1/2+Landsat+LiDAR time series;
(b) they "consistently outperform other featurizations without re-training"; (c) fit for
classification/regression/change-detection/similarity-search. Each use below cites one:

1. **Similarity search (build first, §AEF-c).** Cosine distance of every mandal/district to mean
   embedding of top-5 measured plants → "land like proven land" ranking. No training, no p≫n risk.
   Gate: top-10 must include Kurnool/Anantapur belt; else embedding year mismatch (try adjacent year).
2. **LULC/vegetation proxy (§AEF-b).** ACRS needed NDVI + Dynamic World + GHSL as separate fetches;
   one AEF vector replaces all three (no-retraining claim). Use cluster id (k-means, k=8) as a single
   categorical feature — costs 1 degree of freedom, not 64.
3. **Regression features, PCA-ablated (§AEF-b).** 64→3–5 PCs, keep only on CV gain (Chakraborty PCA
   precedent, Davò et al.). Never raw bands at n≈160.
4. **Change detection (§AEF-c).** 2017→latest embedding drift flags encroachment/new farms per site;
   feeds Phase-5 monitoring. Validated pattern: crop-type/disturbance demos in AEF paper.
5. **NOT used for:** CUF targets (embeddings describe surface, not generation), seasonal dynamics
   (annual), rooftop geometry (10m vs 0.1m DSM).

Collector `gee_alphaearth.py` (built, `--step aef`) is the only new fetch; everything else reuses
SRTM/WorldCover/MODIS buffers. `ponytail: per-band reducers if mean washes out quarry-vs-scrub texture.`

## Phase 3 — ML correctness (paper-gated) [CODE DONE on DEV, UNRUN here]

> Implemented: persisted `preprocessor.joblib` (both entrypoints) + `scaler_selected.joblib`
> (train/serve parity); `cuf_source_filter` wiring w/ graceful fallback; greedy Pearson>0.95
> drop-one in `trainer.train`; RFE default 8 (config + both CLIs); shared HPO ridge space
> 1e-6..100; `VotingModel` (RF+Ridge) in factory; `test_ml_leakage.py` (6 tests).
> Blocked: no pandas/sklearn in this shell — full suite + training run on data machine.
> Double-scale wart kept deliberately (preprocess tests assert scaled outputs).

1. Single scaler + persist `preprocessor.joblib` + `rfe_mask.json` (Chakraborty train-only stats rule).
2. `--use-real-cuf` → plant/hybrid/physics + sample weights; row-drop only power-equivalent empties
   (their <500W night-row drop ≈ our all-NaN districts).
3. RFE≤8 from Decision-2 list; Pearson>0.95 drop-one; shared HPO space; KFold5; 20-seed mean±std.
4. Model order: Ridge-bar → RF/XGB (ACRS hyperparams) → Voting → Stacking-iff-CV-gap>0.01.
   AdaBoost excluded up front (0.526, worst in Table 8 — no trial budget wasted).
5. `test_ml_leakage.py` + scaler round-trip + physics-fidelity assert (R² vs formula must DROP on
   real target — proves we stopped memorizing).
- Exit: hybrid test R² 0.75–0.90 with 20-seed std; ≥85% plants in top-2 classes; report reads like
  Chakraborty Table 8 (RMSE + R² + train time per model).

## Phase 4 — Serve + UI (platform patterns, not papers)

PVGIS-style `GET` tools + TMY for generation charts; Atlas site-card field parity
(GHI/DNI/DIF/GTI/OPTA/PVOUT); `api.js` with timeout/retry/loading/error; seeded SHAP
(real importances replace `Math.random`); `*`404 + ScrollToTop. Keep mock fallback.
Exit: Dashboard lists 60 live; `/predict` returns hybrid + `cuf_source` + model card link.

## Phase 5 — Validate → expand (gates)

1. NISE-2025 district tables + CEA state CUF + SRRA stations as holdout labels (never features).
2. Hit-rate gate (Decision 10); weight recalibration (Decision 11); exclusion masks (Decision 12).
3. Then 766 districts + 101→200+ plants (CEA daily template fetched); AEF annual refresh diff.
4. Rooftop module ONLY on demand: YOLOv8 pattern (ACRS §3.4: precision 0.972, 60-cell 1.66m²,
   1.5 kWh/day, 15% loss) — parked until utility pilot is green.

## Deliberately parked (with paper trigger to unpark)

- Transformers/LSTM forecasting (SolarTformer, Dhaked 2023): needs time series we don't collect.
  Unpark when hourly plant metering exists.
- Sunroof Solar API: BASE-quality residential India only; utility wasteland out of coverage.
  Unpark with rooftop module.
- sup3r GAN downscaling: unpark when district→mandal error >5%.
- PVGIS `iotools`/pvlib chain: unpark when physics-fallback error vs SRRA >3%.
