# SolarSite-India

AI-powered solar energy site selection platform for India.

## Overview

SolarSite-India is a data-driven solar site suitability platform that uses a machine learning ensemble to rank potential solar deployment locations. The project is being developed in stages, beginning with Telangana and Andhra Pradesh (60 districts) as the initial pilot region before scaling to national coverage.

**Current scope**: 60 districts (33 Telangana + 27 Andhra Pradesh: 26 Apr-2022 districts + Markapuram, real since Dec-2025; Polavaram pending data → 61st), 42 engineered features.

**Status**: Data pipeline complete; models **are** trained (`python -m src.cli.train`) and reported honestly. Labels are CEA-actual only — the earlier R² = 0.996 came from physics-derived labels that duplicated the features, and has been retrained away. Next is the paper, not training.

### Aspirational Scope (Documented in `/docs`)
The full project documentation describes a national-scale system with:
- 30,000+ sites across 28 states
- 42 features per site (see `/docs` for full feature descriptions)
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

tests/                       ← pytest suite (35/35 passing)
```

---

## Key Design Decisions

| Topic | Decision |
|-------|----------|
| **Target variable** | CUF = actual CEA generation ÷ installed MW ÷ 8760. Physics-derived CUF exists in the data (`cuf_source = "physics"`) but is **never** used as a training label. |
| **Training data** | CEA-actual labels only. District frame 60 rows (48 train / 12 test); plant-level labels are being built toward 700+ CEA plants. |
| **Features** | 42 total: 27 raw source features + 15 engineered composite features |
| **Census gap** | 37/60 districts missing 2011 census; reverse-estimated from 2024 projection using 1%/yr compound growth |
| **Infrastructure distances** | Heuristic placeholder (real OSMnx integration is a future step) |
| **Leakage-free** | All preprocessing stats (imputation, scaling, encoding) computed on train split only |

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
| Unit (utils, features, leakage, pipeline) | ✅ 35/35 passing |
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

```bash
# Canonical entrypoint (root main.py / train_ensemble.py wrappers deleted)
python -m src.cli.train --models ridge,lasso --feature-selection rfe --n-features 12
python -m src.cli.train --hpo --hpo-trials 30        # HPO inside CV only
```

---

## Outputs

- `backend/data_pipeline/outputs/processed/features_train.csv` — (48 × 43)
- `backend/data_pipeline/outputs/processed/features_test.csv` — (12 × 43)
- `backend/data_pipeline/outputs/processed/labels_train.csv` — CUF + `cuf_source` provenance
- `backend/data_pipeline/outputs/reports/*.png` — EDA plots

---

## License

MIT
