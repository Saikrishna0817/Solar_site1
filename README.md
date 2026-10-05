# SolarSite-India

AI-powered solar energy site selection platform for India.

## Overview

SolarSite-India is a data-driven solar site suitability platform that uses a machine learning ensemble to rank potential solar deployment locations. The project is being developed in stages, beginning with Telangana and Andhra Pradesh (60 districts) as the initial pilot region before scaling to national coverage.

**Current scope**: 60 districts (33 Telangana + 27 Andhra Pradesh: 26 Apr-2022 districts + Markapuram, real since Dec-2025; Polavaram pending data), 42 engineered features, 48 training samples.

**Status**: Data pipeline (Stages 1–3) is complete and production-ready. The ML model training scripts are next on the roadmap.

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
└── src/services/           ← API layer (mock mode by default — no backend yet)

tests/                       ← pytest suite (29/29 passing)
```

---

## Key Design Decisions

| Topic | Decision |
|-------|----------|
| **Target variable** | CUF computed from physics: `GHI × PR(T_cell) / 24` (not actual plant generation data — see `/docs`) |
| **Training data** | 60 district-level records (48 train / 12 test). ML model training is next step. |
| **Features** | 42 total: 27 raw source features + 15 engineered composite features |
| **Census gap** | 37/60 districts missing 2011 census; reverse-estimated from 2024 projection using 1%/yr compound growth |
| **Infrastructure distances** | Heuristic placeholder (real OSMnx integration is a future step) |
| **Leakage-free** | All preprocessing stats (imputation, scaling, encoding) computed on train split only |

---

## Architecture

```
backend/data_pipeline/
├── solarpipeline/          ← Modular data pipeline package
│   ├── data.py             ← Merges 6 source datasets + computes CUF
│   ├── features.py         ← Engineers composite features
│   ├── eda.py              ← Generates EDA visualisations
│   ├── preprocess.py         ← Train/test split, impute, scale (leakage-free)
│   └── core.py             ← Orchestrator entrypoint
├── phase2_3_pipeline.py      ← Thin CLI entrypoint ( --step all )
├── main.py                   ← Phase-1 data collection driver
└── config/settings.py        ← Shared paths & constants

frontend/                    ← React + Vite + Tailwind + Framer Motion
├── src/pages/              ← Dashboard, SiteAnalysis, etc.
└── src/services/           ← API layer (mock mode by default)

tests/                       ← pytest suite
```

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
| Unit (utils, features, pipeline) | ✅ 29/29 passing |
| End-to-end pipeline | ✅ Passes on full 60-district dataset |

---

## Configurable Pipeline

```bash
# Phase 1: collect raw data
python main.py --step all

# Phase 2/3: merge, EDA, preprocess
python phase2_3_pipeline.py --step all

# Or run specific steps
python phase2_3_pipeline.py --step preprocess
```

---

## Outputs

- `backend/data_pipeline/outputs/processed/features_train.csv` — (48 × 36)
- `backend/data_pipeline/outputs/processed/features_test.csv` — (12 × 36)
- `backend/data_pipeline/outputs/processed/labels_train.csv` — CUF + state labels
- `backend/data_pipeline/outputs/reports/*.png` — EDA plots

---

## License

MIT
