# AlphaEarth (AEF) setup — Phase A

**Status: [PENDING — NOT RUN in this environment]** (no GEE credentials: `ee`/`earthengine-api`
1.7.46 is installed in `.venv`, but `~/.config/earthengine` does not exist). No AEF-derived number
is claimed anywhere in this repo until a run is logged here.

## Enable Google Earth Engine (free)

1. Sign up free at `https://earthengine.google.com/` (non-commercial/research tier) and create a
   Google Cloud project; set its project id via env `GEE_PROJECT_ID`
   (repo default in `backend/data_pipeline/config/settings.py:68` → `solar-site-495511`).
2. `pip install earthengine-api` (already present in `.venv`, pinned in `requirements.lock.txt`).
3. One-time auth: `earthengine authenticate`, then verify `init_gee()` in
   `backend/data_pipeline/datasources/gee_helper.py` returns True.
4. Run the collector: `python -m ... --step aef` → `backend/data_pipeline/datasources/gee_alphaearth.py`,
   collection id **`GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL`** (64 bands A00..A63, 10 m, pinned year 2024).

## Plan rules (hard gates — do not relax)

- **Year-before-commissioning:** the embedding year must predate the labelled plant's
  commissioning/label period — no post-period imagery into features (leakage).
- **PCA ≤ 8 inside CV folds:** 64 dims → ≤8 PCs, fitted per-fold with all other feature selection
  (fix plan: "Add AlphaEarth only after PCA (~8 dims)"; "Keep all feature selection inside CV folds").
- **Never in labels:** embeddings describe surface, not generation — CUF labels stay
  measured MWh ÷ MW ÷ 8760 only (`docs/NEXT_PHASES_PLAN.md` §AEF item 5).
- **n ≥ 100 gate:** no embedding regressor ships until ≥100 labelled rows; below that AEF is
  similarity-search / LULC-proxy only (today: 13 CEA plants → gate closed).

## Licence / attribution

`[VERIFY BEFORE PUBLICATION: confirm AEF dataset licence terms at the GEE data catalog page]` —
current in-repo note (`data/external_fetch/LICENSE_REGISTER.md`) says CC-BY-4.0, "produced by
Google and Google DeepMind" (v1.1, model v2.1); re-check at
`https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_SATELLITE_EMBEDDING_V1_ANNUAL`
before citing.
