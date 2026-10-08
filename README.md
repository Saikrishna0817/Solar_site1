# SolarSite-India

AI-powered solar energy site selection platform for India.

## Overview

SolarSite-India is a data-driven solar site suitability platform that uses a machine learning ensemble to rank potential solar deployment locations. The project is being developed in stages, beginning with Telangana and Andhra Pradesh (60 districts) as the initial pilot region before scaling to national coverage.

**Current scope**: 60 districts (33 Telangana + 27 Andhra Pradesh: 26 Apr-2022 districts + Markapuram, real since Dec-2025; Polavaram pending data → 61st), 39 district-frame features (25 raw + 14 derived); the plant-level model trains on 43 features.

**Status**: Data pipeline complete; models **are** trained (`python -m src.cli.train`) and reported honestly. Labels are CEA-actual only — the earlier R² = 0.996 came from physics-derived labels that duplicated the features, and has been retrained away. Paper draft material (limitations, sources, scenarios) lives in [`docs/PAPER.md`](docs/PAPER.md).

### Aspirational Scope (Documented in `/docs`)
The full project documentation describes a national-scale system with:
- 30,000+ sites across 28 states
- 43 features per site (see `/docs` for full feature descriptions)
- ML ensemble (Random Forest + XGBoost + Gradient Boosting)
- FastAPI backend + React dashboard
- R² = 0.88 claimed (not yet implemented)

**Note**: The current codebase reflects the initial TS+AP pilot. All aspirational claims (national scale, specific model metrics, deployed API) are documented goals, not current capabilities. See `/docs/PROJECT_MEMORY.md` for the full vision.

---

## Architecture

```
backend/data_pipeline/
├── solarpipeline/          ← Modular data pipeline package
│   ├── utils.py            ← Logging, paths, CONFIG (all magic numbers here)
│   ├── data.py             ← Merges 6 source datasets + computes CUF
│   ├── features.py         ← Engineers 15 composite/domain features
│   ├── eda.py              ← Generates EDA visualisations
│   ├── preprocess.py       ← Train/test split, impute, winsorize, scale
│   └── core.py             ← Orchestrator + pipeline metadata export
├── phase2_3_pipeline.py      ← Thin CLI entrypoint (--step all)
├── main.py                   ← Phase-1 data collection driver
└── config/settings.py        ← Shared paths & constants

frontend/                    ← React + Vite + Tailwind + Framer Motion
├── src/pages/              ← Dashboard, SiteAnalysis, etc.
└── src/services/           ← API client (mock mode by default)

src/api/                     ← FastAPI server (5 endpoints; not wired to the frontend yet)
src/cli/train.py             ← Canonical ML training entrypoint

tests/                       ← pytest suite (52/52 passing)
```

---

## Key Design Decisions

| Topic | Decision |
|-------|----------|
| **Target variable** | CUF = actual CEA generation ÷ installed MW ÷ 8760. Physics-derived CUF exists in the data (`cuf_source = "physics"`) but is **never** used as a training label. |
| **Training data** | CEA-actual labels only. District frame 60 rows (48 train / 12 test); plant-level labels currently 13 CEA plants (700+ needs the CEA monthly registers — ceiling in `docs/METHODOLOGY.md`). |
| **Features** | District frame: 39 (25 raw + 14 derived). Plant frame: 43. Label-derived composites are never created (Phase 2). |
| **Census gap** | 37/60 districts missing 2011 census; reverse-estimated from 2024 projection using 1%/yr compound growth |
| **Infrastructure distances** | Heuristic placeholder (real OSMnx integration is a future step) |
| **Leakage-free** | All preprocessing stats (imputation, scaling, encoding) computed on train split only |
| **Serving gate (Gate 3)** | ML serves only if a residual model beats pvlib C0 on both the district-bootstrap LOGO CI (95 %) and held-out plants — verdict in `models/gate.json`; fail ⇒ the API serves C0 only with `kind=baseline_c0`. Predictions carry a conformal 90 % interval. |

---

## Quick Start

### 1. Clone & Install Dependencies

```bash
git clone <repo-url>
cd Solar_site
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/data_pipeline/requirements.txt
```

### 2. Set Environment (Optional)

```bash
# Copy the example and edit GEE_PROJECT_ID, etc.
cp .env.example .env
```

### 3. Run the Data Pipeline

```bash
cd backend/data_pipeline
python phase2_3_pipeline.py --step all
```

### 4. Run Tests

```bash
python3 -m pytest tests/ -v
```

### 5. Start the Frontend (Optional)

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173/
```

---

## Test Results

| Suite | Result |
|-------|--------|
| Unit (utils, features, leakage, pipeline, phase gates, serving gate) | ✅ 52/52 passing |
| End-to-end pipeline | ✅ Passes on full 60-district dataset |

---

## Configurable Pipeline

```bash
cd backend/data_pipeline

# Phase 1: collect raw data
python main.py --step all

# Phase 2/3: merge, EDA, preprocess
python phase2_3_pipeline.py --step all

# Or run specific steps
python phase2_3_pipeline.py --step preprocess
```

---

## Train the Models

Labels default to CEA actual only (`--cuf-source cea_plant`); physics-derived CUF is
excluded from every run and may only be requested for ablation. See
[`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).

```bash
# Canonical entrypoint (root main.py / train_ensemble.py wrappers deleted)
# Default unit = plant (data/plant_labels/plant_dataset.csv, 13 CEA plants)
python -m src.cli.train --models ridge lasso --feature-selection rfe --n-features 8
python -m src.cli.train --hpo --hpo-trials 30        # HPO inside CV only
python -m src.cli.train --unit district --cuf-source all   # ablation only
```

---

## Serving Gate (Gate 3)

```bash
python scripts/phase3_residual_ci.py     # writes models/gate.json + residual_ridge.joblib
python -m src.api.main                   # serves cuf = c0_physics + residual, ±90% interval
```

A residual model is served only when it beats the C0 physics baseline on the
district-bootstrap LOGO CI **and** on held-out plants (pre-registered rule,
features in `models/pre_registered_features.json`). Gate 3 fail ⇒ C0-only
responses labelled `kind=baseline_c0` with `ml_withheld_reason` — never a silent
fallback. Regenerate the district CUF choropleth data with
`scripts/export_district_cuf_frontend.py`; keep frontend constants in sync with
`scripts/update_frontend_metrics.py --write`.

---

## Outputs

- `data/plant_labels/plant_dataset.csv` — plant rows × district features + `cuf_source`
- `backend/data_pipeline/outputs/processed/features_train.csv` — (48 × 40, incl. `district` id)
- `backend/data_pipeline/outputs/processed/features_test.csv` — (12 × 40, incl. `district` id)
- `backend/data_pipeline/outputs/processed/labels_train.csv` — CUF + `cuf_source` provenance
- `backend/data_pipeline/outputs/reports/*.png` — EDA plots
- `requirements.lock.txt` — exact pins from `.venv` (`pip freeze`), reproducible CI/install input

---

## License

MIT
