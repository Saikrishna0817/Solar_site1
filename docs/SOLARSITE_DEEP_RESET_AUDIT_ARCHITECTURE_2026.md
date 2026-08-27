# SolarSite-India — Deep Reset Audit, Architecture & Implementation Plan

**Version**: 1.0
**Date**: 2026-05-13
**Author**: Principal Full-Stack AI Engineer
**Status**: COMPREHENSIVE EXECUTIVE DOCUMENT — Source of Truth for all future implementation

---

# 1. EXECUTIVE SUMMARY

SolarSite-India is a machine-learning-driven solar energy site selection platform targeting India’s 500 GW renewable goal by 2030. The project has two distinct realities:

1. **What exists**: A solid proof-of-concept with 60 districts (Telangana + Andhra Pradesh), a working data pipeline (6 data sources), 15 engineered features on top of 27 raw features, a basic sklearn training loop (MLPipeline), and a visually polished React frontend operating entirely on mock data.

2. **What is documented**: An aspirational national-scale platform with 30,000+ sites, 28 states, an R² = 0.88 ensemble model, a FastAPI backend, SHAP explainability, and an interactive dashboard.

**Critical gap**: The frontend (mock data, national map) and backend (60 districts, physics-formula CUF) are completely disconnected. The "ML model" is fitting to a near-deterministic physics equation (`CUF = GHI × PR / 24`), making the high R² values misleading. The project lacks a functioning API server, CI/CD, environment management, or any deployment infrastructure. There are 40+ pairs of collinear features, VIF values of infinity, and only 60 training samples for 39 features — a severe overfitting risk.

**My recommendation**: Execute a structured, phased rebuild that bridges aspiration to implementation without discarding the genuine engineering progress already made.

---

# 2. REPOSITORY AUDIT REPORT

## 2.1 Repository-Wide Audit

### Architecture Problems

| Severity | Issue | Location | Impact |
|----------|-------|----------|--------|
| **CRITICAL** | Frontend operates entirely on mock data; no backend API exists | `frontend/src/services/api.js:7` (USE_MOCK=true), `frontend/src/data/mockSites.js` | Entire frontend is disconnected from reality |
| **CRITICAL** | Target variable (CUF) is a physics formula, not learned from real data | `backend/data_pipeline/solarpipeline/utils.py:167-182` | ML pipeline is fitting to deterministic function; R² is meaningless |
| **CRITICAL** | No FastAPI server implemented despite documented API endpoints | Entire `backend/` tree — only data pipeline exists, no web server | Cannot serve model predictions |
| **HIGH** | Perfect multicollinearity — 21 pairs with r > 0.9, VIF = ∞ | `docs/AUDIT_REPORT.md:98-108` | Linear model coefficients are unreliable; all models overfit |
| **HIGH** | 60 training samples for 39 features — classic n << p problem | `docs/AUDIT_REPORT.md:12-17` | Severe overfitting risk for any model |
| **HIGH** | `configs/` directory is empty | `/configs/` | Configuration management is ad-hoc |
| **MEDIUM** | `src/ml/training/` directory has only empty `__init__.py` | `src/ml/training/__init__.py` | Dead/placeholder code |
| **MEDIUM** | `src/ml/utils/` directory is completely empty | `src/ml/utils/` | Dead/placeholder code |
| **MEDIUM** | Two separate training entry points with overlapping functionality | `main.py` (96 lines) and `train_ensemble.py` (116 lines) | Duplicate code, unclear which is canonical |
| **MEDIUM** | Frontend claims 30,000+ sites, 28 states; backend has 60 districts | Frontend constants vs. backend config | Aspirations documented as facts |
| **MEDIUM** | No `.gitignore` entries for `models/`, `reports/`, `ml_logs/` directories that contain runtime artifacts | `.gitignore` | Generated model files and reports may be committed accidentally |
| **MEDIUM** | Duplicate architecture descriptions in README (lines 27-44 and 65-81) | `README.md` | README has copy-pasted content |
| **LOW** | `backend/data_pipeline/main.py` (Phase 1 collector) vs. `phase2_3_pipeline.py` (Phase 2-3 pipeline) — unclear naming | `backend/data_pipeline/` | Confusing entrypoints for new contributors |

### Code Quality Issues

| Severity | Issue | Location |
|----------|-------|----------|
| **HIGH** | `train_ensemble.py:54-66` — Objective function uses test set for HPO (massive data leakage) | `train_ensemble.py:54-63` |
| **HIGH** | `src/ml/optimization.py:42-66` — Same test-set leakage pattern in HPO objective | `src/ml/optimization.py:42-66` |
| **MEDIUM** | `src/ml/trainer.py:72-73` — `cross_validate` uses `y.iloc[train_idx]` but `y` is a `pd.Series` — works but fragile | `src/ml/trainer.py:75-76` |
| **MEDIUM** | `main.py:77-78` — Uses `pd` without importing it in the HPO branch | `main.py:77-78` (NameError at runtime) |
| **MEDIUM** | `src/ml/pipelines/ml_pipeline.py:9` — Unnecessary `sys.path.insert` with hardcoded path | `src/ml/pipelines/ml_pipeline.py:9` |
| **MEDIUM** | `backup/restore` in `conftest.py` reads/writes text but CSVs can be large — should be `shutil.copy2` | `tests/conftest.py:28-39` |
| **LOW** | `train_ensemble.py:23-26` — Optuna import error uses `return None` as fallback without proper error handling | `train_ensemble.py:23-26` |
| **LOW** | `src/ml/evaluation/core.py:133` — Bug: duplicate `cv_` prefix (`cv_r2_mean` vs `cv_cv_r2_mean`) | `src/ml/evaluation/core.py:132-133` |
| **LOW** | No proper typing anywhere in the Python code — all function signatures use basic types | Throughout `src/ml/` |
| **LOW** | `src/ml/data_loader.py:56-57` — `X_test` parameter is untyped, could be DataFrame or ndarray | `src/ml/data_loader.py:51` |

### ML Engineering Issues

| Severity | Issue | Detail |
|----------|-------|--------|
| **CRITICAL** | Target is computed, not measured | CUF = `GHI × PR(T_cell) / 24`. The model learns this formula, achieving near-perfect R². This is not ML — it's a function approximator memorizing a known equation. |
| **CRITICAL** | Test set used for hyperparameter optimization | Both `train_ensemble.py:54-63` and `src/ml/optimization.py:42-66` optimize hyperparameters directly on the test set. This is textbook data leakage. |
| **HIGH** | Only 60 samples total (48 train / 12 test) | Not enough data for ensemble methods, stacking, or any non-linear model to learn meaningful patterns. Tree depth must be capped to 2-3 to avoid memorization. |
| **HIGH** | No cross-validation during model comparison | `main.py` uses `Trainer.cross_validate()` which does k-fold CV on training data, but the final performance reported is purely on the 12-sample test set — high variance. |
| **HIGH** | No experiment tracking | No MLflow, Weights & Biases, or even manual CSV logging of experiments. |
| **HIGH** | 40+ collinear feature pairs | Linear models will have unstable coefficients. Tree models will arbitrarily use one of two identical features. |
| **MEDIUM** | No proper model registry | Models saved as `.joblib` files with ad-hoc naming. No model ID, version, or metadata. |
| **MEDIUM** | No inference pipeline | Only training code exists. No code for serving predictions, loading the model, or applying preprocessing. |
| **MEDIUM** | No retraining strategy | Pipeline is designed for one-shot training. No incremental update, no data versioning. |

### Frontend/UI Issues

| Severity | Issue | Detail |
|----------|-------|--------|
| **HIGH** | Entirely mock-data-driven | 50 hardcoded sites in `mockSites.js`. No connection to real ML pipeline or backend. |
| **HIGH** | Inflated metric claims | Landing page shows "88% model accuracy", "30,000+ sites", "127 training plants" — none of these are implemented. |
| **MEDIUM** | Chart components have no error/loading/empty states | `ScatterPlot.jsx`, `SHAPWaterfall.jsx`, etc. — no loading skeletons, error boundaries, or empty state handling. |
| **MEDIUM** | `USE_MOCK` toggle is misleading | Even with `USE_MOCK=false`, there's no backend to connect to — it will simply fail. |
| **MEDIUM** | No TypeScript | Entire frontend uses plain JSX. No type safety for data structures, API responses, or component props. |
| **LOW** | Three.js chunk is ~800KB gzipped | SolarGlobe is lazy-loaded but still adds significant bundle weight. |
| **LOW** | No accessibility | No ARIA labels, keyboard navigation, screen reader support, or focus management. |
| **LOW** | No testing | Zero frontend tests (Jest, React Testing Library, Cypress). |

---

## 2.2 Conflict & Redundancy Analysis

### Documented vs. Reality Contradictions

| Document Claim | Reality | Severity |
|---------------|---------|----------|
| R² = 0.88, MAPE = 11.5%, RMSE = 0.065 | Models fit a physics formula; near-perfect R² is meaningless | CRITICAL |
| 30,000+ sites, 28 states, 127 training plants | 60 districts, 48/12 split, TS+AP only | HIGH |
| RF (30%) + XGBoost (50%) + GBM (20%) ensemble | `train_ensemble.py:114` says "Stacking not beneficial" and uses single Ridge | HIGH |
| FastAPI backend designed | No server code exists in repository | HIGH |
| Feature radar, SHAP waterfall, generation charts | All use mock data with randomized SHAP values | MEDIUM |
| "42 features" | After dropping leakers, collinear pairs, and AOD, it's ~30 usable features | MEDIUM |
| Census data for 60 districts | 37/60 districts missing 2011 census (reverse-estimated) | MEDIUM |
| Infrastructure distances from OSM | "Heuristic placeholder" — not real OSMnx integration | MEDIUM |

### Redundant Files & Modules

| File/Directory | Why Redundant | Action |
|---------------|---------------|--------|
| `configs/` (empty) | Placeholder, never used | DELETE |
| `src/ml/training/` (empty init) | Placeholder, never used | MERGE into `src/ml/trainer.py` or DELETE |
| `src/ml/utils/` (empty) | Placeholder | MOVE shared utilities here from random modules |
| `backend/data_pipeline/main.py` (Phase 1) | Confusing — Phase 1 entry vs. `phase2_3_pipeline.py` | RENAME to `phase1_collect.py` |
| `train_ensemble.py` (root level) | Overlaps with `main.py` | CONSOLIDATE into single entrypoint |
| `main.py` (root level) | Overlaps with `train_ensemble.py` | CONSOLIDATE |
| `reports/` directory (artifacts) | Generated outputs — shouldn't be in git | ADD to `.gitignore` |
| `models/` directory (artifacts) | Generated .joblib files | ADD to `.gitignore` |
| `audit_outputs/` directory (artifacts) | Generated audit artifacts | ADD to `.gitignore` or move to `reports/audit/` |
| Duplicate architecture block in README | Lines 27-44 and 65-81 are identical | DELETE one |
| `docs/SolarSite_India_Complete_Documentation_v3.docx` | Binary, should be auto-generated | CONVERT to `.md` or link externally |

### Temporary/Debug Artifacts

- `backend/data_pipeline/pipeline.log` — in `.gitignore`, so OK
- `ml_logs/ml_training.log` — runtime artifact, not in `.gitignore` → ADD
- `reports/optimized_summary.csv`, `reports/ensemble_summary.csv` — generated artifacts → ADD to `.gitignore`

---

## 2.3 Structural Purge & Reorganization

### Files to DELETE

```
configs/                                    # Empty, never used
src/ml/training/                            # Only empty __init__.py
reports/ensemble_summary.csv               # Generated artifact
reports/optimized_summary.csv              # Generated artifact
reports/figures/                            # Generated artifacts (or preserve as reference)
audit_outputs/                              # Move to reports/audit/, then remove
```

### Files to MERGE

```
train_ensemble.py + main.py  →  src/cli/train.py          # Single training entrypoint
src/ml/data_loader.py        →  src/ml/pipelines/data.py  # Move to pipelines subpackage
src/ml/optimization.py       →  src/ml/training/hpo.py    # New home
```

### Files to RENAME

```
backend/data_pipeline/main.py             →  backend/data_pipeline/phase1_collect.py
backend/data_pipeline/phase2_3_pipeline.py  →  backend/data_pipeline/run_pipeline.py
```

### Directory Restructuring Plan

New target structure:

```
Solar_site/
├── src/                          # Python source (unified ML + data)
│   ├── cli/
│   │   ├── __init__.py
│   │   └── train.py              # Single `python -m src.cli.train` entrypoint
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── config.py             # YAML-based config (Pydantic Settings)
│   │   ├── models/
│   │   │   ├── __init__.py       # Model factory
│   │   │   ├── base.py           # BaseModel ABC
│   │   │   ├── linear.py         # Ridge, Lasso, ElasticNet
│   │   │   └── tree.py           # RandomForest, XGBoost
│   │   ├── pipelines/
│   │   │   ├── __init__.py
│   │   │   ├── data.py           # Data loading, splitting, scaling
│   │   │   └── training.py       # Training orchestration
│   │   ├── evaluation/
│   │   │   ├── __init__.py
│   │   │   ├── metrics.py        # Regression metrics
│   │   │   ├── plots.py          # Matplotlib visualization
│   │   │   └── report.py         # Markdown report generator
│   │   ├── optimization/
│   │   │   ├── __init__.py
│   │   │   └── hpo.py            # Optuna hyperparameter optimization
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logging.py        # Shared logging setup
│   │       └── io.py             # File I/O helpers
│   ├── data_pipeline/            # Data collection & preprocessing
│   │   ├── __init__.py
│   │   ├── config/               # Data pipeline settings
│   │   ├── datasources/          # Data collection modules (GEE, NASA, OSM)
│   │   ├── pipeline/
│   │   │   ├── __init__.py
│   │   │   ├── merge.py
│   │   │   ├── features.py
│   │   │   ├── eda.py
│   │   │   └── preprocess.py
│   │   ├── utils/                # Shared utilities
│   │   ├── run_pipeline.py       # CLI entrypoint
│   │   └── outputs/              # Runtime outputs (in .gitignore)
│   └── api/                      # FastAPI server (NEW)
│       ├── __init__.py
│       ├── main.py               # FastAPI app
│       ├── routers/
│       │   ├── sites.py
│       │   ├── predictions.py
│       │   └── analytics.py
│       ├── schemas/
│       │   └── models.py
│       └── services/
│           ├── inference.py
│           └── data.py
├── frontend/                     # React application (existing, needs refactor)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/                # NEW: Zustand/Jotai state management
│   │   ├── types/                # NEW: TypeScript type definitions
│   │   └── ...
│   └── ...
├── tests/                        # All tests (Python + JS)
│   ├── unit/
│   │   ├── test_ml_models.py
│   │   ├── test_preprocessing.py
│   │   └── test_api.py
│   ├── integration/
│   │   └── test_pipeline.py
│   └── e2e/                      # Playwright/Cypress
├── docs/                         # All documentation
│   ├── architecture/
│   │   ├── system_overview.md
│   │   ├── ml_pipeline.md
│   │   └── api_design.md
│   ├── product/
│   │   ├── prd.md
│   │   └── user_flows.md
│   ├── development/
│   │   ├── setup.md
│   │   ├── contributing.md
│   │   └── conventions.md
│   └── governance/
│       ├── ml_standards.md
│       └── code_review_checklist.md
├── data/                         # Raw data (in .gitignore for large files)
│   ├── raw/                      # Immutable raw datasets
│   ├── processed/                # Pipeline outputs
│   └── external/                 # External reference data
├── models/                       # Trained model artifacts
├── infrastructure/               # Docker, K8s, Terraform (NEW)
│   ├── docker/
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.frontend
│   │   └── docker-compose.yml
│   └── scripts/
│       └── deploy.sh
├── .gitignore
├── .env.example
├── pyproject.toml                # NEW: Single Python project config
├── Makefile                      # NEW: Task runner
├── README.md
└── LICENSE
```

---

## 2.4 Dependency Cleanup

### Existing Python Dependencies (`backend/data_pipeline/requirements.txt`)

**KEEP**:
- `numpy`, `pandas`, `scikit-learn`, `matplotlib`, `seaborn` — core ML stack
- `fastapi`, `uvicorn`, `pydantic` — needed for server
- `geopandas`, `shapely`, `pyproj` — geospatial
- `requests`, `python-dotenv` — essentials

**REMOVE** (not actively used):
- `tqdm` — no progress bars in current code, add back when needed
- `geemap` — heavy dependency, not used in pipeline code
- `osmnx` — heavy dependency, OSM data is placeholder
- `sqlalchemy` — no database yet
- `plotly` — not used; Recharts handles frontend charts

**ADD**:
- `mlflow` — experiment tracking
- `pyyaml` — config management (already imported in `core.py` but not in requirements)
- `joblib` — model serialization (already used but not in requirements)
- `pytest`, `pytest-cov` — testing (move from implicit to explicit)
- `black`, `isort`, `ruff` — formatting & linting
- `pre-commit` — git hooks
- `optuna` — already used but not in requirements

### Frontend Dependencies

**KEEP**: All existing. React, Framer Motion, Recharts, Leaflet, React Three Fiber.

**ADD**:
- `typescript` — type safety
- `@types/react`, `@types/react-dom`, `@types/leaflet` — TypeScript types
- `zustand` — lightweight state management (replace custom hooks for global state)
- `@tanstack/react-query` — server state management
- `vitest` + `@testing-library/react` — testing
- `axe-core` + `@axe-core/react` — accessibility testing

---

# 3. ARCHITECTURAL DOCUMENTATION ("SOURCE OF TRUTH")

## 3.1 Product Requirements Document (PRD)

### Product Vision

SolarSite-India is an AI-powered geospatial intelligence platform that identifies, ranks, and economically evaluates optimal locations for utility-scale solar energy deployment across India. It replaces the traditional 6-12 month manual site assessment process with instant, data-driven recommendations.

**Core mission**: Accelerate India's renewable energy transition by making solar site selection scientific, transparent, and accessible to developers, policymakers, and researchers.

**Strategic value proposition**:
- **Speed**: Reduce site assessment from months to minutes
- **Cost**: Eliminate the ₹50-100 lakh survey cost per site
- **Quality**: Data-driven decisions reduce project failure rate from 70% to near zero
- **Scale**: Screen entire country (30K+ grid cells) in a single run
- **Transparency**: SHAP-based explainability for every prediction

**Competitive differentiation**: No other platform in India combines satellite data (GEE), climate data (NASA POWER), terrain (SRTM), infrastructure (OSM), census data, and ML ensemble modeling into a single unified site selection tool.

### Long-term Product Vision (3-5 years)
1. **National coverage**: All 28 states, 750+ districts, 30,000+ sites
2. **Real-time data**: Live satellite imagery, weather forecasts, and grid status
3. **Rooftop analysis**: 300M+ building-level solar potential assessment
4. **Hybrid renewable**: Wind + solar co-location optimization
5. **Marketplace**: Connect solar developers with landowners and investors
6. **Policy simulation**: Model impact of tariff changes, subsidy programs, land-use policies

### Problem Definition

**Core problem**: Utility-scale solar projects have a 70% failure rate during the pre-construction phase due to poor site selection. The current process involves:
- Manual surveys that cost ₹50-100 lakh and take 6-12 months
- Subjective assessments without quantitative rigor
- No unified view of solar resource, terrain, infrastructure, and environmental constraints
- Decision-making based on incomplete or outdated data

**Market pain points**:
- Solar developers lose millions on sites that fail permitting or underperform
- Policymakers lack data-driven tools to prioritize regions for grid investment
- Researchers cannot systematically evaluate solar potential at national scale
- Financial institutions cannot reliably assess project risk pre-construction

**Existing solution gaps**:
- NREL's PVWatts — global but country-level resolution, ignores local infrastructure
- MNRE's solar atlas — outdated (2015), no ML, no economic analysis
- Commercial tools (SolarGIS, 3E) — expensive ($10K+ / user / year), closed-source, no India-specific data
- Academic models — not productionized, no UI, no ongoing updates

### User Personas

| Persona | Role | Motivation | Technical Level | Primary Use Case |
|---------|------|------------|-----------------|------------------|
| **Solar Developer (Priya)** | Project Developer at a renewable energy company | Find viable sites for 500 MW pipeline within budget and timeline | Medium — understands solar metrics but not ML | Filter sites by state, budget; download site reports; compare top candidates |
| **Government Planner (Rajesh)** | Joint Secretary, MNRE | Identify priority zones for grid infrastructure investment | Low — policy-focused, needs executive summaries | View state-level rankings; identify underserved high-potential regions; export reports for policy briefs |
| **Energy Researcher (Dr. Sharma)** | Professor, IIT Delhi | Publish research; validate methodology against ground truth | High — understands ML, wants to inspect model internals | Access raw features; export model predictions; validate against known plants; use API for custom analysis |
| **Financial Analyst (Anika)** | Clean energy investment analyst | Assess project viability for financing decisions | Medium — understands financial metrics, not ML | View NPV, payback, LCOE for candidate sites; compare risk profiles; export financial models |
| **Landowner / Community Leader (Vikram)** | Village panchayat head | Understand if solar development on community land is viable | Low — needs simple, visual output | Enter location; see suitability score; understand economic benefit |

### Functional Requirements

#### Core Features (MVP — Sprint 1-3)

| ID | Feature | Description |
|----|---------|-------------|
| F1 | **Data pipeline** | Collect, clean, and merge 6 data sources for 60+ districts |
| F2 | **ML model training** | Train single linear model with proper evaluation on 60-district pilot |
| F3 | **Suitability prediction** | Predict CUF score for any location given feature inputs |
| F4 | **FastAPI backend** | Expose `/api/predict`, `/api/sites`, `/api/sites/{id}` endpoints |
| F5 | **Interactive map** | Leaflet map with colored markers for predicted sites |
| F6 | **Site detail page** | Per-site breakdown: GHI, CUF, terrain, economic metrics |
| F7 | **Basic filtering** | Filter sites by state, suitability score, GHI range |

#### Secondary Features (Sprint 4-6)

| ID | Feature | Description |
|----|---------|-------------|
| F8 | **Economic calculator** | LCOE, NPV, payback period, annual generation per site |
| F9 | **Feature importance (SHAP)** | Per-prediction SHAP values showing feature contributions |
| F10 | **State-wise comparison** | Side-by-side comparison of top states |
| F11 | **Site comparison** | Compare up to 5 sites on all metrics |
| F12 | **Export to CSV/PDF** | Download site data, reports, and charts |
| F13 | **Custom coordinate analysis** | Enter lat/lng to analyze any arbitrary location |
| F14 | **Polygon area selection** | Draw polygon on map to analyze enclosed area |

#### Stretch Features (Sprint 7+)

| ID | Feature | Description |
|----|---------|-------------|
| F15 | **National scale** | Expand from 60 to 750+ districts, 30,000+ grid cells |
| F16 | **Real-time data refresh** | Monthly NASA POWER and satellite data updates |
| F17 | **Rooftop analysis** | Building-level solar potential using satellite imagery |
| F18 | **Hybrid renewable optimization** | Wind + solar co-location analysis |
| F19 | **Notification system** | Alert users when new data or model versions are available |
| F20 | **User accounts** | Save preferences, bookmarked sites, custom dashboards |

### Non-Functional Requirements

| Category | Requirement | Target |
|----------|-------------|--------|
| **Scalability** | API handles 100 concurrent users | ≤ 200ms p95 latency for predictions |
| **Scalability** | Map renders 30,000+ markers | ≤ 3s initial load, markers clustered |
| **Reliability** | Backend availability | 99.5% uptime (production) |
| **Security** | All API endpoints authenticated | JWT-based auth (post-MVP) |
| **Security** | No secrets in code | Environment variables, no hardcoded keys |
| **Performance** | Model inference time | ≤ 100ms per prediction |
| **Performance** | Frontend initial load | ≤ 2s (lazy-loaded Three.js excluded) |
| **Accessibility** | WCAG 2.1 AA compliance | 95%+ aXe score |
| **Responsiveness** | Mobile-friendly dashboard | Functional on tablet and phone |
| **Maintainability** | Test coverage | ≥ 80% Python backend, ≥ 60% frontend |
| **Documentation** | Every module documented | README for each directory, docstrings for all public functions |

### Success Metrics

#### User Metrics
- **Monthly Active Users**: ≥ 50 in first 6 months
- **Sessions per user**: ≥ 3 per month
- **Site reports generated**: ≥ 100 per month
- **User satisfaction**: NPS ≥ 40

#### Model Metrics (real data, when available)
- **R² on real CUF data**: ≥ 0.75 (realistic target vs. the current physics-derived scores)
- **MAE**: ≤ 0.02 CUF (2 percentage points)
- **Calibration**: Predictions within ±5% of actual CUF for 80% of test cases
- **Robustness**: Performance degradation ≤ 10% when tested on unseen states

#### System Metrics
- **API latency p95**: ≤ 200ms
- **Error rate**: ≤ 0.1%
- **Data freshness**: ≤ 30 days for climate data

---

## 3.2 Technical Requirements Document (TRD)

### System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                     │
│  │ Browser  │  │ Mobile   │  │ API      │                     │
│  │ (React)  │  │ Web App  │  │ Clients  │                     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                     │
│       │             │             │                             │
├───────┼─────────────┼─────────────┼────────────────────────────┤
│       │             │    CDN/Nginx Reverse Proxy                │
│       │             │    (Static Assets + API Routing)          │
│       │             │             │                             │
├───────┼─────────────┼─────────────┼────────────────────────────┤
│       │             │    APPLICATION LAYER                      │
│  ┌────┴─────────────┴─────────────┴────┐                        │
│  │        FASTAPI SERVER                 │                        │
│  │  ┌─────────┐  ┌─────────┐  ┌───────┐ │                        │
│  │  │ /api/   │  │ /api/   │  │ /api/  │ │                        │
│  │  │ sites   │  │ predict │  │ health │ │                        │
│  │  └────┬────┘  └────┬────┘  └───────┘ │                        │
│  │       │            │                  │                        │
│  │  ┌────┴────────────┴────┐             │                        │
│  │  │  Inference Service    │             │                        │
│  │  │  (Model Loading,      │             │                        │
│  │  │   Preprocessing,       │             │                        │
│  │  │   Prediction, SHAP)    │             │                        │
│  │  └─────────┬─────────────┘             │                        │
│  └────────────┼───────────────────────────┘                        │
│               │                                                    │
├───────────────┼────────────────────────────────────────────────────┤
│               │    DATA LAYER                                      │
│  ┌────────────┴──────────────────┐  ┌──────────────────────┐       │
│  │  Model Registry                │  │  Processed Data       │       │
│  │  (models/*.joblib + metadata)  │  │  (data/processed/)    │       │
│  └───────────────────────────────┘  └──────────────────────┘       │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                    OFFLINE ML PIPELINE (Scheduled)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Data     │→ │ Feature   │→ │ Model     │→ │ Evaluation│          │
│  │ Collection│  │ Engineering│ │ Training │  │ & Registry│          │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────────────┘
```

### Tech Stack Justification

| Layer | Technology | Why Selected |
|-------|-----------|--------------|
| **Frontend Framework** | React 18 + Vite | Fast dev server, HMR, tree-shaking. Established ecosystem with Framer Motion, Three.js, Leaflet integrations |
| **State Management** | Zustand | Lightweight (1KB), no boilerplate, works well with React Query for server state |
| **Styling** | Tailwind CSS 3.4 | Utility-first aligns with component-based architecture. Custom design tokens already defined |
| **3D Rendering** | Three.js + React Three Fiber | Declarative 3D in React. Only used where it adds value (globe viz, particle effects) |
| **Maps** | Leaflet + React Leaflet | No API key required, dark tile theme matches design system, mature library |
| **Charts** | Recharts | React-native charting, composable, themeable. Used for all data visualizations |
| **Animation** | Framer Motion | Physics-based animations, gesture support, layout animations. Already integrated |
| **Backend Framework** | FastAPI + Uvicorn | Async Python, automatic OpenAPI docs, Pydantic validation, high performance |
| **ML Framework** | scikit-learn + XGBoost | Mature, well-documented. Sufficient for structured tabular data with 30-40 features |
| **Experiment Tracking** | MLflow | Open-source, lightweight, integrates with sklearn, tracks params/metrics/artifacts |
| **Model Serialization** | joblib | Standard sklearn serialization. Fast, compressed |
| **Data Processing** | Pandas + NumPy | Industry standard for tabular data. 60-district dataset fits comfortably in memory |
| **Geospatial** | GeoPandas + Shapely | Necessary for spatial operations on district boundaries, proximity calculations |
| **Database** | None (file-based for MVP) | 60 districts × 40 features = 2,400 cells. No database needed until scaling to 30K+ sites |
| **Caching** | In-memory (MVP) | No caching layer needed until we have >100 concurrent users |
| **Cloud Infrastructure** | Docker + AWS/GCP (future) | Containerize for reproducibility. Cloud-agnostic architecture ready for deployment |
| **Orchestration** | docker-compose (dev), K8s (prod) | Simple dev setup, production scaling with K8s |
| **CI/CD** | GitHub Actions | Free for public repos, integrates with Docker Hub, runs tests and builds |
| **Monitoring** | Prometheus + Grafana (future) | Standard observability stack for API metrics, model drift, error rates |
| **Version Control** | Git + GitHub | Standard. Conventional commits, semantic versioning |

### API Design

#### Endpoint Structure

```
GET    /api/health                         → Health check
GET    /api/v1/sites                       → List all predicted sites (with filters)
GET    /api/v1/sites/{district_id}         → Single site detail with all features
POST   /api/v1/predict                     → Predict suitability for custom location
GET    /api/v1/states                      → State-wise aggregate statistics
GET    /api/v1/model/info                  → Current model version, metrics, feature list
```

#### Request/Response Patterns

**GET /api/v1/sites**
```
Query params: ?state=Telangana&min_suitability=0.7&limit=50&offset=0
Response:
{
  "data": [
    {
      "district": "kurnool",
      "state": "Andhra Pradesh",
      "cuf_predicted": 0.1575,
      "ghi": 5.62,
      "suitability_score": 0.87,
      "top_features": {"ghi": 0.38, "temperature": -0.12, "grid_distance": -0.09}
    }
  ],
  "total": 60,
  "model_version": "v1.0.0",
  "generated_at": "2026-05-13T10:00:00Z"
}
```

**POST /api/v1/predict**
```
Body: {
  "latitude": 27.5394,
  "longitude": 71.9101
}
Response: {
  "prediction": {
    "cuf": 0.162,
    "suitability_score": 0.92,
    "suitability_label": "Excellent",
    "features_used": {"ghi": 5.72, "temperature": 28.5, ...},
    "shap_values": {"ghi": 0.042, "temperature": -0.008, ...}
  },
  "model_version": "v1.0.0"
}
```

#### Authentication

- **MVP**: No authentication (public API for a research tool)
- **Post-MVP**: JWT-based authentication via FastAPI middleware. Rate limiting (100 req/min per IP).

#### Error Standards

```json
{
  "error": {
    "code": "INVALID_COORDINATES",
    "message": "Latitude must be between 6 and 38, longitude between 68 and 98.",
    "details": {"provided": {"lat": 50, "lng": 70}}
  }
}
```

Standard error codes: `INVALID_INPUT`, `NOT_FOUND`, `MODEL_ERROR`, `INTERNAL_ERROR`, `RATE_LIMITED`.

### ML System Design

#### Dataset Structure

```
data/
├── raw/
│   ├── nasa_power/       ← GHI, DNI, temperature, humidity, etc.
│   ├── gee_srtm/         ← Elevation, slope, aspect
│   ├── osm/              ← Road, grid, substation distances
│   ├── gee_worldcover/   ← Land use percentages
│   ├── gee_modis/        ← Aerosol optical depth
│   └── census_cea/       ← Population, density, CUF from CEA
├── processed/
│   ├── master_merged.csv          ← After Phase 1 merge
│   ├── master_engineered.csv      ← After Phase 2 features
│   ├── features_train.csv         ← 48 × ~20 (after feature selection)
│   ├── features_test.csv          ← 12 × ~20
│   ├── labels_train.csv           ← CUF + district
│   ├── labels_test.csv
│   ├── scaling_params.csv         ← StandardScaler means/stds
│   └── pipeline_metadata.yaml     ← Reproducibility metadata
└── external/
    └── SolarSite_District_Dataset_v2.xlsx  ← Reference dataset
```

#### Preprocessing Pipeline (Leakage-Free)

```
1. SPLIT first (80/20 stratified by state, seed=42)
2. IMPUTE (train-only medians for numeric, "Unknown" for categorical)
3. WINSORIZE (train-only 5th/95th percentiles)
4. LOG-TRANSFORM skewed features (train-detected, abs(skew) > 3)
5. LABEL-ENCODE categoricals (train-only categories, "Unknown" fallback)
6. STANDARDSCALE (train-only fit)
7. FEATURE SELECTION (RFECV with 5-fold CV on training data only)
```

**Critical change**: Drop physically collinear features BEFORE training:
- Drop `peak_sun_hours` (r ≈ 1.0 with `avg_ghi_kwh_m2_day`)
- Drop two of three distance columns (keep `infrastructure_accessibility_index`)
- Drop `wasteland_builtup_pct` (r ≈ 0.997 with `builtup_pct`)
- Drop `solar_variability` or `solar_efficiency_index` (r ≈ 0.997)

#### Training Architecture

```
Config → DataLoader → FeatureSelector → CrossValidator → Trainer → Evaluator → Registry
```

- **Config**: YAML-based (Pydantic Settings) with model params, data paths, seeds
- **DataLoader**: Reads CSVs, applies train/test split, scaling
- **FeatureSelector**: RFECV (n_features=15) or LassoCV
- **CrossValidator**: 5-fold on training data (NOT test set)
- **Trainer**: Fits model with best hyperparameters on full training set
- **Evaluator**: Computes R², MAE, RMSE, MAPE on held-out test set
- **Registry**: Saves model + scaler + feature names + metadata to `models/`

#### Validation Methodology

| Validation | Purpose | Method |
|------------|---------|--------|
| **Internal CV** | Hyperparameter selection | 5-fold on training data |
| **Hold-out test** | Final performance estimate | 20% stratified holdout (12 districts) |
| **SHAP analysis** | Model interpretability | TreeExplainer / LinearExplainer per prediction |
| **Confidence interval** | Performance uncertainty | Bootstrap 1000 resamples of test set |
| **Ablation study** | Feature importance | Retrain without each feature category, measure impact |
| **Spatial validation** | Generalization to unseen states | Leave-one-state-out cross-validation |

#### Experiment Tracking

Every training run logs:
```yaml
run_id: "20260513_143022_abc123"
model: "ridge"
hyperparams: {alpha: 0.0001}
features_selected: 15
feature_names: ["ghi", "temperature", ...]
metrics: {train_r2: 0.997, test_r2: 0.983, cv_r2_mean: 0.979, cv_r2_std: 0.012}
artifacts: ["model.joblib", "scaler.joblib", "feature_importances.csv"]
timestamp: "2026-05-13T14:30:22Z"
git_commit: "abc123"
```

#### Inference Flow

```
Input (lat, lng)
  → Fetch features from data sources (or use cached district-level features)
  → Apply preprocessing: winsorize, log-transform skewed, encode, scale
    (using saved train-time transformers)
  → Apply feature selection mask (saved from training)
  → Model.predict()
  → Compute SHAP values (using saved explainer)
  → Return prediction + explanation
```

#### Retraining Strategy

- **Frequency**: Monthly (when NASA POWER data updates)
- **Trigger**: Manual (new district data available) or automatic (when new district data is added)
- **Process**: Re-run full pipeline with updated raw data → retrain model → compare metrics → promote if better
- **Rollback**: Keep previous 3 model versions; auto-rollback if new model performs >10% worse on test set
- **Data versioning**: Each raw data snapshot tagged with date. `data/raw_20260501/`

### MLOps Strategy

```yaml
versioning:
  models: "semantic (v1.0.0, v1.1.0)"
  data: "date-based snapshots (raw_20260501)"
  code: "git tags + conventional commits"

monitoring:
  api: "Prometheus /metrics endpoint (request count, latency, error rate)"
  model: "Prediction distribution drift (KS test vs. training baseline)"
  data: "Feature distribution drift (monthly automated check)"

ci_cd:
  training_ci: "GitHub Action: on push to main/ → run tests → run pipeline → evaluate → auto-commit model"
  deployment_cd: "Build Docker image → push to registry → deploy (or manual trigger for production)"

reproducibility:
  seeds: "Fixed (42) for all random operations"
  tracking: "MLflow logs all params, metrics, artifacts per run"
  environment: "Docker image pinned with exact dependency versions"
```

### Security & Compliance

| Area | Strategy |
|------|----------|
| **Secrets** | Environment variables only (`.env`, never committed). GEE credentials in `~/.config/earthengine/` |
| **Input validation** | Pydantic models for all API inputs. Reject lat/lng outside India bounds (6°-38°N, 68°-98°E) |
| **Rate limiting** | FastAPI middleware: 100 req/min per IP |
| **CORS** | Allowlist specific frontend origins in production |
| **HTTPS** | Enforced in production (Nginx/Traefik reverse proxy) |
| **GDPR/Privacy** | No PII collected. Location data is at district level (not individual). IP logs for rate limiting only, rotated daily |
| **Model security** | No adversarial training needed for structured geospatial data. Input ranges validated |

---

## 3.3 UI/UX Design System & Creative Direction

### Design Philosophy

**"Solar Intelligence, Visualized"**

The interface should feel like a command center for solar energy intelligence — not a generic dashboard. Think NASA mission control meets Bloomberg Terminal, with the warmth of sunlight. The design must communicate:

1. **Data density without clutter** — Every pixel serves a purpose
2. **Spatial awareness** — The map is the hero; everything orbits it
3. **Scientific credibility** — Clean typography, consistent units, precise numbers
4. **Emotional engagement** — Solar-themed warm gradients, particle effects that evoke the sun
5. **Trust through transparency** — Explainable AI (SHAP values prominently displayed, not hidden)

### Color Psychology

- **Solar Gold (#F5A623)**: Primary accent. Signals energy, optimism, action. Used for primary CTAs, key metrics, active states.
- **Tech Cyan (#06B6D4)**: Secondary accent. Signals technology, precision, intelligence. Used for tech features, data viz, secondary CTAs.
- **Space Deep (#0A0E1A)**: Background. Near-black with blue undertone. Signals depth, space, professionalism. Darker than Navy.
- **Success Green (#10B981)**: Positive indicators — high suitability scores, online status, completed actions.
- **Warning Purple (#8B5CF6)**: Non-critical alerts, processing states, "moderate" scores.
- **Error Red (#EF4444)**: Critical alerts, poor suitability scores, error states.

### Typography Hierarchy

```
Display (Outfit): Hero headings, section titles, big stat numbers
  weight: 700-900, tracking: -0.02em

Body (Inter): All text, labels, descriptions, paragraphs
  weight: 400-600, line-height: 1.65

Code (JetBrains Mono): Coordinates, scores, metrics, technical data
  weight: 400-600, tabular-nums feature
```

Size scale (consistent across application):
```
5xl+  → Hero headlines (64-72px)
3xl   → Page titles (32px)
2xl   → Section headers (24px)
xl    → Card titles (20px)
lg    → Important body text (18px)
base  → Standard body (16.5px)
sm    → Secondary labels, metadata (14px)
xs    → Fine print, footnotes (12px)
```

### Spacing System (8px base unit)

```
4px   → Tight inline gaps (icon-to-text)
8px   → Standard element gap
12px  → Card internal padding (p-3)
16px  → Card internal padding (p-4)
20px  → Card internal padding (p-5) — DEFAULT
24px  → Section gaps, container padding
32px  → Large section gaps
48px  → Extra large section gaps
80px  → Section vertical padding (section-padding)
```

### Glass Morphism System

The existing system is excellent — fully preserved and extended:

```
.glass         — rgba(13,27,42,0.6) + blur(20px)                   Light transparency
.glass-strong  — rgba(13,27,42,0.85) + blur(30px)                  Strong (navbar, side panels)
.glass-card    — glass + border-radius(14px) + hover lift + shimmer  Interactive cards
.card-shimmer  — Rotating conic gradient border on hover             Premium highlight
```

### Shadow System

```
shadow-glow-gold  — 0 0 20px rgba(245,166,35,0.3)       (Primary glow)
shadow-glow-cyan  — 0 0 20px rgba(6,182,212,0.3)        (Tech glow)
shadow-glass      — 0 8px 32px rgba(0,0,0,0.3)          (Card elevation)
shadow-card-hover — 0 12px 40px rgba(245,166,35,0.1)... (Card interactive)
```

### Motion Philosophy

**Purposeful, not decorative.** Every animation must enhance understanding or guide attention.

**Page-level transitions**:
- Route changes: Fade + 8px vertical slide (Framer Motion AnimatePresence, mode="wait")
- Map interactions: Pan/zoom with inertia, markers animate in with scale bounce

**Micro-interactions**:
- Button hover: 3px lift + glow expansion (0.25s, spring)
- Card hover: 4px lift + 0.5% scale + shimmer sweep (0.4s)
- Stat counter: Animate from 0 to target on scroll into view (2s ease-out)
- Hover on data points: Scale + tooltip fade-in

**Scroll-driven**:
- Section entrance: Elements animate up 30px + fade-in as they scroll into view
- Parallax: Subtle depth on hero section (background moves at 0.5x scroll speed)
- Staggered list items: 0.1s delay per item

**Loading states**:
- Skeleton screens with shimmer animation (matching card layout)
- Pulse animation on data-loading indicators
- Progress bar for data pipeline steps

**AI-state visualizations**:
- Model confidence: Gauge fills with animated gradient
- SHAP contributions: Bars grow with spring physics
- Prediction uncertainty: Fading/brightness indicates confidence

### Accessibility Strategy

```
- Color contrast: All text meets WCAG AA (4.5:1 for body, 3:1 for large text)
- Keyboard navigation: All interactive elements focusable, logical tab order
- Screen readers: ARIA labels on charts, map markers, form controls
- Motion preferences: Respect `prefers-reduced-motion` — disable animations
- Focus indicators: Visible outline (2px solar-gold) on all focusable elements
- Error messages: Visible, persistent, linked to relevant input via aria-describedby
- Skip link: "Skip to main content" link at top of page
```

### UX Architecture

**Information Architecture**:
```
Home (/)
  ├── Hero (vision + stats)
  ├── Problem/Solution (before/after)
  ├── How It Works (pipeline visualization)
  ├── Features Grid
  ├── Interactive Calculator
  └── CTA

Dashboard (/dashboard)
  ├── Stats Bar (top)
  ├── Map (70% width)
  │   ├── Toolbar: Filters | Locate | Area Select
  │   └── Legend (bottom-left)
  └── Site List Panel (30% width)
      └── → Links to Site Detail

Site Analysis (/analyze?id=)
  ├── Breadcrumb: Dashboard > Site Name
  ├── Suitability Gauge + Key Metrics
  ├── Feature Radar + Monthly Generation
  ├── SHAP Waterfall
  └── Economic Analysis

Methodology (/methodology)
  ├── Timeline (4-stage pipeline)
  ├── Ensemble Model Cards
  └── Feature Explorer (42 features)

Results (/results)
  ├── Key Metrics Cards
  ├── Predicted vs Actual Scatter
  ├── State Comparison Chart
  └── Top Sites Table

About (/about)
  ├── Mission
  ├── Research Highlights
  ├── Tech Stack
  └── Team/Contact
```

**User Journey Map (Primary Flow)**:
```
1. Landing page → 2. "Explore Map" CTA → 3. Dashboard (map + site list)
→ 4. Click site marker → 5. Site detail panel → 6. "View Full Analysis"
→ 7. Site Analysis page → 8. "Compare" another site → 9. Side-by-side comparison
```

---

## 3.4 Application Flow & Data Schema

### Application Flow

#### Training Pipeline Flow
```
1. Data Collection (Phase 1)
   ├── GEE: SRTM, WorldCover, MODIS AOD
   ├── NASA POWER: GHI, DNI, temp, humidity, wind, rainfall
   ├── OSM: Road/grid/substation distances
   ├── Census: Population, area, density
   └── CEA: CUF (target), installed capacity
   ↓
2. Merge (Phase 2)
   └── Outer join on district → 60 rows, ~25 raw columns
   ↓
3. Feature Engineering (Phase 2)
   ├── Compute CUF (GHI × PR / 24) — target variable
   ├── Drop leaker: installed_solar_capacity_mw
   └── Derive 15 composite features
   ↓
4. EDA (Phase 2)
   └── Generate distribution plots, correlation heatmap, missing value report
   ↓
5. Preprocessing (Phase 3)
   ├── Drop non-features: district, state, source, AOD
   ├── Drop individual distance cols (keep composite index)
   ├── Train/test split (80/20, stratified by state)
   ├── Impute (train-only medians)
   ├── Winsorize (train-only quantiles)
   ├── Log-transform skewed (train-detected)
   ├── Label-encode categoricals (train-only)
   └── StandardScale (train-only)
   ↓
6. ML Training
   ├── Feature selection (RFECV, 15 features)
   ├── CV (5-fold on training data)
   ├── Hyperparameter optimization (Optuna, on training data via CV)
   ├── Final model fit
   └── Evaluation on held-out test set
   ↓
7. Registry
   ├── Save model (.joblib)
   ├── Save scaler (.joblib)
   ├── Save feature names (.json)
   ├── Save metrics (.json)
   └── Log to MLflow
```

#### Prediction Flow (API)
```
POST /api/v1/predict {lat, lng}
  ↓
1. Geocode lat/lng to nearest district
2. Lookup district features from processed data
3. Apply preprocessing (winsorize → log → encode → scale)
   using saved train-time transformers
4. Select features (using saved feature mask from training)
5. model.predict(features) → CUF score
6. shap_explainer(features) → feature contributions
7. Compute suitability score (0-1 normalized CUF)
8. Return JSON response
```

#### User Interaction Flow (Frontend)
```
User visits "/"
  ↓ (scrolls)
Sees hero → stats → problem/solution → how it works → features → calculator
  ↓ (clicks "Explore Map")
Navigates to "/dashboard"
  ↓
Map renders with all sites as colored markers
  ↓ (uses toolbar)
Filters by state / min score → map updates
OR enters lat/lng → bounding box appears with nearby sites
OR draws polygon → enclosed sites counted and analyzed
  ↓ (clicks marker or list item)
Site detail panel expands → shows GHI, capacity, LCOE, score
  ↓ (clicks "View Detailed Analysis")
Navigates to "/analyze?id=X"
  ↓
Full site breakdown with gauge, radar, SHAP, economics
```

### Backend Schema / ERD

At 60-district scale, the data is tabular (no relational database needed). But for future scale, here's the logical schema:

```
┌──────────────────────┐       ┌──────────────────────┐
│       District        │       │       State           │
├──────────────────────┤       ├──────────────────────┤
│ id (PK)              │───┐   │ id (PK)              │
│ name                 │   │   │ name                 │
│ state_id (FK)        │───┘   │ abbreviation         │
│ latitude             │       │ region               │
│ longitude            │       │ total_districts      │
│ area_sqkm            │       └──────────────────────┘
│ ... (30+ features)   │
│ cuf_actual           │       ┌──────────────────────┐
│ cuf_predicted        │       │   Model Version       │
│ suitability_score    │       ├──────────────────────┤
│ model_version_id (FK)│───┐   │ id (PK)              │
│ generated_at         │   │   │ version              │
└──────────────────────┘   │   │ model_type           │
                            │   │ hyperparameters (JSON)│
                            │   │ features_used (JSON) │
                            │   │ train_r2             │
                            │   │ test_r2              │
                            │   │ created_at           │
                            │   └──────────────────────┘
                            │
                            │   ┌──────────────────────┐
                            │   │   Prediction Log      │
                            │   ├──────────────────────┤
                            │   │ id (PK)              │
                            └───│ model_version_id (FK)│
                                │ input_lat            │
                                │ input_lng            │
                                │ district_id (FK)     │
                                │ predicted_cuf        │
                                │ shap_values (JSON)   │
                                │ latency_ms           │
                                │ error (nullable)     │
                                │ timestamp            │
                                └──────────────────────┘

┌──────────────────────┐       ┌──────────────────────┐
│   Pipeline Run        │       │   Data Snapshot       │
├──────────────────────┤       ├──────────────────────┤
│ id (PK)              │       │ id (PK)              │
│ run_timestamp        │       │ snapshot_date        │
│ steps_completed (JSON)│      │ nasa_version         │
│ success              │       │ srtm_version          │
│ error_log            │       │ osm_version          │
│ output_files (JSON)  │       │ census_version       │
└──────────────────────┘       │ district_count       │
                               └──────────────────────┘
```

**Indexing strategy** (for when database is added):
- Primary keys on all tables
- `idx_district_state` on `District(state_id)`
- `idx_prediction_timestamp` on `PredictionLog(timestamp)`
- `idx_model_version` on `ModelVersion(version)`

**Scalability note**: Current 60 × 40 matrix (2,400 cells) fits entirely in memory. No database needed. When scaling to 30,000+ sites, migrate to PostgreSQL + PostGIS for spatial queries.

**Normalization**: 3NF for districts/states. Model metadata and predictions are append-only and can be partially denormalized for read performance.

---

## 3.5 Sprint-Based Implementation Roadmap

### Sprint 0: Foundation & Environment (1 week)

**Objectives**: Standardize development environment and tooling.

| Task | Deliverable |
|------|-------------|
| Create `pyproject.toml` with all Python dependencies | Single source of truth for Python deps |
| Create `frontend/package.json` cleanup (add TypeScript) | Ready for Sprint 3 frontend refactor |
| Add `.gitignore` entries for `models/`, `reports/`, `ml_logs/`, `audit_outputs/` | Clean git history |
| Set up `pre-commit` hooks: black, isort, ruff | Auto-formatted code |
| Set up GitHub Actions: `test.yml`, `lint.yml` | CI running |
| Delete dead directories: `configs/`, `src/ml/training/` | Clean repo |
| Write `CONTRIBUTING.md` | Onboarding document |
| Fix duplicate README architecture block | Clean README |
| Define conventional commit format | CHANGELOG automation |

**Dependencies**: None
**Risk**: Low
**Tests**: CI passes; pre-commit hooks work

---

### Sprint 1: Data Pipeline Hardening (1.5 weeks)

**Objectives**: Fix data quality issues, multicollinearity, and leakage. Ensure pipeline is reproducible.

| Task | Deliverable |
|------|-------------|
| **Critical**: Drop `peak_sun_hours` (r=1.0 with GHI) | Cleaner feature set |
| **Critical**: Drop individual distance columns (keep composite `infrastructure_accessibility_index`) | No multicollinear distances |
| **Critical**: Drop `wasteland_builtup_pct` (r=0.997 with `builtup_pct`) | Cleaner feature set |
| **Critical**: Drop `solar_variability` or `solar_efficiency_index` (r=0.996) | No duplicated solar ratio |
| Audit: Verify no impossible values in raw data (pre-scaling) | Data quality confirmed |
| Add: Outlier detection with IQR (already in audit) + configurable thresholds | Automated outlier flagging |
| Add: Pipeline metadata export includes dropped features + collinearity report | Full reproducibility |
| Rename: `backend/data_pipeline/main.py` → `phase1_collect.py` | Clear entrypoints |
| Rename: `phase2_3_pipeline.py` → `run_pipeline.py` | Clear entrypoints |
| Add: `data_pipeline/requirements.txt` → merge into root `pyproject.toml` | Single dep file |
| Update: Tests for new feature set | All 29 tests still pass |
| Document: CUF computation clearly — document that CUF is physics-derived, not measured | Transparency for future contributors |

**Dependencies**: Sprint 0
**Risk Area**: Dropping features may change model performance; evaluate carefully
**Tests**: Pipeline integration test on mock 4-row DataFrame; verify output shape

---

### Sprint 2: ML Pipeline Correctness (2 weeks)

**Objectives**: Fix critical ML bugs (test-set leakage, overfitting), implement proper evaluation.

| Task | Deliverable |
|------|-------------|
| **Critical**: Fix HPO to use CV on training data ONLY, never test set | No data leakage in hparam selection |
| **Critical**: Fix `train_ensemble.py` test-set leakage | Clean evaluation |
| **Critical**: Move `objective()` to use training CV split | Correct HPO |
| **Critical**: Add bootstrap confidence intervals for test metrics | Performance uncertainty quantified |
| Add: MLflow experiment tracking | Every run logged |
| Add: Feature selection BEFORE model training (RFECV) | Reduced from ~35 to 15 features |
| Add: Leave-one-state-out cross-validation | Spatial generalization estimate |
| Add: Model comparison using paired t-test (not just bar charts) | Statistical rigor |
| Add: SHAP explainer (LinearExplainer for Ridge, TreeExplainer for RF) | Model interpretability |
| Consolidate: `main.py` + `train_ensemble.py` → `src/cli/train.py` | Single training entrypoint |
| Remove: Dead `src/ml/training/`, `src/ml/utils/` (or populate with actual utils) | No dead code |
| Fix: `src/ml/evaluation/core.py:133` double `cv_cv_` prefix bug | Correct report output |
| Fix: `main.py:77-78` missing `pd` import | No runtime errors |
| Add: `models/.gitkeep` and add `models/` to `.gitignore` (except `.gitkeep`) | Clean repo |

**Dependencies**: Sprint 1 (clean feature set)
**Risk**: Small sample (60) limits what SHAP can meaningfully explain. Accept limitation.
**Tests**: 5 new unit tests for evaluation metrics, HPO correctness, feature selection

---

### Sprint 3: FastAPI Backend (2 weeks)

**Objectives**: Build the API server that the frontend connects to.

| Task | Deliverable |
|------|-------------|
| Create: `src/api/main.py` — FastAPI app with CORS, health endpoint | Server running |
| Create: `src/api/routers/sites.py` — `GET /api/v1/sites` with filtering | Site listing endpoint |
| Create: `src/api/routers/predictions.py` — `POST /api/v1/predict` | Prediction endpoint |
| Create: `src/api/schemas/models.py` — Pydantic request/response models | Type-safe API |
| Create: `src/api/services/inference.py` — Model loading, preprocessing, prediction | Inference pipeline |
| Create: `src/api/services/data.py` — Load processed district data into memory | Data access layer |
| Add: Rate limiting middleware (100 req/min) | API protection |
| Add: Structured error responses | Consistent error handling |
| Add: `/api/v1/model/info` — Current model version, features, metrics | Model transparency |
| Test: All endpoints with pytest + httpx | API test coverage |
| Document: OpenAPI docs (auto-generated by FastAPI) | API documentation |

**Dependencies**: Sprint 2 (trained model, saved transformers)
**Risk**: Inference pipeline must exactly replicate training preprocessing. Test thoroughly.
**Tests**: 10+ API integration tests

---

### Sprint 4: Frontend-Backend Integration (2 weeks)

**Objectives**: Connect the React frontend to the real FastAPI backend. Replace mock data.

| Task | Deliverable |
|------|-------------|
| Wire: `api.js` to use live FastAPI when server is running | Real data flowing |
| Replace: `mockSites.js` → API-fetched site data | Real site data on map |
| Replace: `mockFeatures.js` → API-fetched feature definitions | Real feature listing |
| Replace: `stateData.js` → API-fetched state aggregates | Real state data |
| Update: `useMapData.js` to use `@tanstack/react-query` | Proper server state management |
| Add: Loading skeletons for all data-dependent components | Good UX during data fetch |
| Add: Error boundaries for map, charts, and data panels | Graceful failure handling |
| Update: Landing page metrics to reflect real data (60 districts, not 30,000) | Honest marketing |
| Add: Empty states ("No results found" for filters) | Good UX for edge cases |
| Add: Retry logic for failed API calls (3 retries with exponential backoff) | Resilient frontend |
| Test: Frontend end-to-end with real backend (manual + vitest) | Integration verified |

**Dependencies**: Sprint 3 (FastAPI running)
**Risk**: Frontend currently assumes 30,000+ data points. Maps, filtering, and charts must work with 60.
**Tests**: Vitest component tests for key pages (Dashboard, SiteAnalysis)

---

### Sprint 5: TypeScript Migration & Frontend Hardening (2.5 weeks)

**Objectives**: Add type safety, accessibility, and performance optimizations.

| Task | Deliverable |
|------|-------------|
| Convert: `src/hooks/` → TypeScript | Typed hooks |
| Convert: `src/services/` → TypeScript (typed API responses) | Typed API layer |
| Convert: `src/data/` → TypeScript (typed constants) | Typed constants |
| Add: `src/types/site.ts`, `src/types/api.ts` — Shared type definitions | Single type source |
| Add: State management with Zustand (replace scattered useState) | Centralized state |
| Add: Accessibility pass — ARIA labels, keyboard nav, focus management | WCAG 2.1 AA baseline |
| Add: `@axe-core/react` for accessibility testing | Automated a11y checks |
| Add: Performance: Code-split `SolarGlobe` (already lazy), `ParticleField`, all chart components | Reduced initial bundle |
| Add: `vite.config.js` chunk splitting strategy | Optimized bundle |
| Add: `vitest` setup with React Testing Library | Frontend test infra |
| Add: Responsive testing — tablet layout (768px), mobile layout (375px) | Mobile-friendly |
| Fix: Any console warnings/errors from mock data integration | Clean console |

**Dependencies**: Sprint 4 (stable data flow)
**Risk**: TypeScript migration may introduce build errors. Migrate page-by-page, not all at once.
**Tests**: 15+ component tests; accessibility audit passing

---

### Sprint 6: ML Pipeline Expansion & Evaluation Rigor (2 weeks)

**Objectives**: Properly evaluate the model beyond R². Implement ML best practices.

| Task | Deliverable |
|------|-------------|
| Add: Nested cross-validation (outer: state-based, inner: 3-fold) | Unbiased performance estimate |
| Add: Bootstrap CI for all metrics (1000 resamples) | Performance uncertainty |
| Add: Calibration plot (predicted vs actual with error bands) | Model calibration check |
| Add: Residual analysis (homoscedasticity, normality) | Assumption validation |
| Add: Feature ablation study — retrain without each feature category | True feature importance |
| Add: Model comparison (Ridge vs Lasso vs RF vs XGBoost) with statistical tests | Best model selection |
| Add: Target re-evaluation — is CUF from real plants available as ground truth? | Move beyond physics formula |
| Add: Experiment tracking report (MLflow dashboard or static HTML report) | Comparison visualization |
| Document: Model card (HuggingFace-style) — intended use, limitations, training data, metrics | ML transparency |

**Dependencies**: Sprint 2 (ML pipeline correctness)
**Risk**: With 60 samples, nested CV may be unstable. Accept limitation, document clearly.
**Tests**: Statistical tests for model comparison

---

### Sprint 7: UI Polish & Motion Systems (1.5 weeks)

**Objectives**: Elevate the frontend from "good dashboard" to "premium AI product experience."

| Task | Deliverable |
|------|-------------|
| Add: Map transition animations (markers animate in, zoom transition easing) | Smooth map interactions |
| Add: Chart animations (bars grow, lines draw, gauge fills with spring) | Engaging data viz |
| Add: Hero parallax effect (scroll-driven background movement) | Immersive landing page |
| Add: 3D Earth rotation responds to scroll position | Interactive hero |
| Add: Micro-interactions: Like animation on "Favorite" click, toast notifications | Delightful UX |
| Add: Confetti/celebration animation on completing first site analysis | Novel user onboarding |
| Add: "Pulse" on newly generated predictions | AI-state visualization |
| Add: Tooltip system (hover on any metric shows definition, source, confidence) | Context everywhere |
| Polish: Loading skeletons with shimmer animation matching card layout | Premium loading UX |
| Review: All animations respect `prefers-reduced-motion` | Accessibility compliance |
| Performance: Ensure 60fps on animations (use `will-change`, GPU-accelerated transforms) | Smooth experience |

**Dependencies**: Sprint 5 (TypeScript stable)
**Risk**: Animation complexity may impact mobile performance. Test on low-end devices.
**Tests**: Lighthouse performance audit (target ≥80)

---

### Sprint 8: Testing & QA (1.5 weeks)

**Objectives**: Comprehensive testing across all layers.

| Task | Deliverable |
|------|-------------|
| Backend: Unit tests for all route handlers | 80%+ coverage |
| Backend: Integration tests for full API flow (predict + sites + model info) | E2E verified |
| ML: Unit tests for preprocessing, feature selection, model training | Pipeline correctness |
| ML: Regression tests (same input → same output, seed=42) | Determinism verified |
| Frontend: Component tests for 5 key pages | Coverage ≥ 60% |
| Frontend: E2E test with Playwright (Dashboard → filter → select site → view analysis) | Critical path tested |
| Frontend: Accessibility audit (axe-core) → fix Critical/Serious issues | WCAG AA compliance |
| Frontend: Cross-browser testing (Chrome, Firefox, Safari) | Browser compatibility |
| Manual: QA checklist walkthrough (all user flows, edge cases) | Product quality |
| Performance: Load testing (100 concurrent API requests) | Scalability baseline |

**Dependencies**: Sprint 7 (frontend polish complete)
**Risk**: E2E tests may be flaky with Leaflet map interactions. Mock map for tests.
**Tests**: (This IS the testing sprint — all tests written here)

---

### Sprint 9: Deployment & Observability (1.5 weeks)

**Objectives**: Production deployment infrastructure and monitoring.

| Task | Deliverable |
|------|-------------|
| Create: `infrastructure/docker/Dockerfile.api` — Multi-stage Python image | Containerized API |
| Create: `infrastructure/docker/Dockerfile.frontend` — Nginx serving built React | Containerized frontend |
| Create: `infrastructure/docker/docker-compose.yml` — API + Frontend + (optional) MLflow | One-command dev deploy |
| Add: Prometheus `/metrics` endpoint for API (request count, latency, error rate) | Monitoring |
| Add: Health check endpoint with model status (loaded/loading/error/model_version) | Deployment health |
| Add: Sentry error tracking (optional, post-MVP) | Production error monitoring |
| Create: `infrastructure/scripts/deploy.sh` — Automated deploy script | CI/CD ready |
| Create: GitHub Action `deploy.yml` — Build Docker images, run tests, push to registry | Automated deployment |
| Document: `docs/deployment.md` — Production deployment guide | Ops documentation |
| Security: Scan Docker images for vulnerabilities (Trivy or Docker Scout) | Secure containers |
| Configure: Nginx reverse proxy config for production (SSL, caching, compression) | Production-ready serving |

**Dependencies**: Sprint 8 (all tests passing)
**Risk**: Docker image size. Use multi-stage builds, Alpine base.
**Tests**: docker-compose up → all endpoints return 200; frontend loads and connects

---

### Sprint 10: Production Hardening & Documentation Freeze (1 week)

**Objectives**: Final polish, security review, and documentation finalization.

| Task | Deliverable |
|------|-------------|
| Security: Audit all dependencies (`pip-audit`, `npm audit`) | No known vulnerabilities |
| Security: Environment variable audit (no hardcoded secrets, no creds in git history) | Clean security posture |
| Documentation: Generate `docs/architecture/SYSTEM_OVERVIEW.md` (Mermaid diagrams) | Architecture docs |
| Documentation: Generate `docs/api/API.md` from OpenAPI spec | API reference |
| Documentation: Finalize README with badges, quick start, architecture diagram | Professional README |
| Documentation: Generate `docs/product/PRD.md` and `docs/technical/TRD.md` | Source of truth docs |
| Performance: Lighthouse audit → optimize to ≥85 on all pages | Performance baseline |
| Performance: API load test → document p50/p95/p99 latency | Performance baseline |
| Code Quality: Run `ruff` across entire codebase → zero warnings | Clean codebase |
| Code Quality: Run `eslint` across entire frontend → zero warnings | Clean frontend |
| Freeze: All documentation marked "v1.0" | Source of truth established |
| Release: Tag `v1.0.0` in git, create GitHub Release | First release |

**Dependencies**: Sprint 9 (deployment working)
**Risk**: Low. This is cleanup/documentation.
**Tests**: Full pipeline run (data collection → training → API serving → frontend rendering)

---

## 3.6 ML Integrity & Evaluation Strategy

### The Fundamental Problem

The current target variable CUF is computed via a deterministic physics formula:
```
CUF = GHI × PR(T_cell) / 24
where PR(T_cell) = 0.80 - 0.0045 × max(0, T_cell - 25)
and T_cell = T_ambient + 25
```

This means:
1. **GHI alone explains ~99% of CUF variance** (r = 0.986)
2. **Any model achieving high R² is memorizing this formula**, not learning real-world solar patterns
3. **The current "ML" is essentially function approximation of a known equation**
4. **Training on physics-derived CUF and then predicting CUF is circular** — like training a model to predict `y = 2x + 3` and being impressed by R² = 1.0

### Path Forward

There are three options, ordered by feasibility:

#### Option A: Accept Physics-Based CUF (Short-term)

Keep the physics formula as the target. Reposition the tool as a "solar suitability ranking system" rather than a "predictive ML model." The value is not in ML magic but in:
- **Unified data collection** (combining 6 data sources is genuinely useful)
- **Weighted ranking** (not just GHI, but terrain, infrastructure, land use)
- **Economic modeling** (LCOE, NPV, payback)
- **Geospatial visualization** (putting all this data on an interactive map)

**Action**: 
- Remove aspirational ML claims (R² = 0.88, "127 training plants") from the frontend
- Reposition the "suitability score" as a **weighted composite index**, not an ML prediction
- Use domain-expert weights for feature importance, not learned coefficients
- Make the physics formula transparent and documented

#### Option B: Real CUF from Operational Plants (Medium-term)

Collect actual CUF data from operational solar plants in India (CEA monthly reports, plant-level monitoring data). Use this as ground truth. This is genuine ML — predicting real plant performance from environmental features.

**Action**:
- Contact CEA, MNRE, or individual developers for plant-level CUF data
- Minimum viable: 20+ plants with known CUF, split 15/5 train/test
- This becomes a genuinely challenging prediction problem (real R² of 0.6-0.8 would be impressive)

#### Option C: Classification Approach (Medium-term)

Instead of regression (predicting exact CUF), frame as classification:
- **Class 0**: Unsuitable (CUF < 0.12 or site constraints make deployment impossible)
- **Class 1**: Suitable (CUF ≥ 0.15 and no critical constraints)
- **Class 2**: Highly Suitable (CUF ≥ 0.17 and excellent infrastructure)

This is more robust, aligns with the "selection" use case, and avoids regression with 60 samples.

### My Recommendation

**Adopt Option A immediately** (Sprint 1-2) and **plan for Option B** (Sprint 8+). The weighted composite index approach is honest, useful, and avoids misleading stakeholders with inflated R² values.

### Evaluation Strategy (Regardless of Target)

If using physics-derived CUF:
```
Primary metric: Suitability ranking (Spearman's ρ between predicted and true ranks)
Secondary: Weighted accuracy of tier classification (Excellent/Good/Moderate/Poor)
Tertiary: Feature attribution consistency (do top features align with domain knowledge?)
```

If using real plant CUF:
```
Primary: R² (realistic target: 0.5-0.7)
Secondary: MAE in percentage points (target: < 0.02 CUF)
Tertiary: Calibration error (predicted CUF vs actual, binned)
Explainability: SHAP values for top 5 features per prediction
Robustness: Leave-one-state-out R² (must be positive and stable)
```

### Data Quality Standards

```
1. No feature can have >50% missing values (drop feature if so)
2. All numeric features must have known valid ranges; outliers documented not removed
3. Target variable must not be derived from any feature used for prediction
4. Train/test split must be spatial — no district appears in both sets
5. All preprocessing statistics computed on training data only
6. All random seeds fixed (42) for reproducibility
7. Feature selection performed within cross-validation loop, not before
8. Hyperparameter optimization performed on training data via CV, never test set
9. Final model performance reported with confidence intervals (bootstrap)
10. Every model artifact includes: feature names, scaler, preprocessing params, git commit SHA
```

### Reproducibility Checklist

```
[ ] Fixed random seed (42)
[ ] Exported training data versions (data snapshot date)
[ ] Exported pip freeze / conda environment
[ ] Exported model hyperparameters
[ ] Exported feature selection mask
[ ] Exported scaler parameters
[ ] Exported label encoder mappings
[ ] Exported preprocessing order (impute → winsorize → log → encode → scale)
[ ] MLflow run ID logged
[ ] Git commit SHA logged
```

---

## 3.7 Frontend Experience Strategy

### Current State Assessment

The frontend is visually impressive for a research prototype — excellent use of glassmorphism, custom animations, Three.js globe, and Tailwind design tokens. The aesthetic direction is correct and should be preserved and refined, not replaced.

**Strengths**:
- Design system tokens in `tailwind.config.js` are comprehensive and consistent
- Glass morphism CSS system is well-crafted (`.glass`, `.glass-strong`, `.glass-card`)
- Animation keyframes cover essential motion patterns
- Component architecture is modular (layout/ui/map/charts/calculator)
- Mock data layer is well-structured for rapid development

**Weaknesses** (to be addressed):
- Entirely mock-data driven → Sprint 4/5 will fix this
- No TypeScript → Sprint 5
- No loading/error/empty states → Sprint 4
- No accessibility → Sprint 5
- Inflated metric claims → Sprint 4 (replace with real metrics)
- No responsive testing → Sprint 5
- Zero frontend tests → Sprint 8

### Implementation Priorities

1. **Real data integration** (Sprint 4) — non-negotiable, top priority
2. **Honest metrics** — replace "88% R²" and "30,000 sites" with real numbers (Sprint 4)
3. **TypeScript migration** (Sprint 5) — prevents future bugs at scale
4. **Accessibility baseline** (Sprint 5) — WCAG AA
5. **Loading/error/empty states** (Sprint 4) — essential for real data
6. **Animation polish** (Sprint 7) — nice-to-have but important for premium feel

### Animation Strategy

Every animation must serve one of three purposes:
1. **Guide attention** — Stagger cards, highlight new information
2. **Provide feedback** — Button press, form submission, data loaded
3. **Convey state** — Loading shimmer, error shake, success glow

Remove or disable:
- Decorative-only animations on performance-constrained pages (Dashboard with map)
- GPU-heavy animations when `prefers-reduced-motion` is set
- Animations that block interaction (e.g., page transitions longer than 300ms)

### Component Standards

Every component should handle four states:
```jsx
// Pattern for every component
if (isLoading) { return <LoadingSkeleton layout="card" />; }
if (error)     { return <ErrorCard message={error.message} onRetry={refetch} />; }
if (!data || data.length === 0) { return <EmptyState icon="🗺️" message="No sites found" action="Try adjusting filters" />; }
return <ActualComponent data={data} />;
```

---

## 3.8 Engineering Governance Standards

### Naming Conventions

```
Python:
  - modules: snake_case (data_loader.py, ml_pipeline.py)
  - classes: PascalCase (SolarDataLoader, MLPipeline)
  - functions: snake_case (load_data, fit_transform)
  - variables: snake_case (train_size, feature_names)
  - constants: UPPER_SNAKE_CASE (RANDOM_STATE, PROJECT_ROOT)

Frontend (TypeScript/JSX):
  - components: PascalCase (GlassCard, SuitabilityGauge)
  - hooks: camelCase + "use" prefix (useMapData, useAnimatedCounter)
  - utilities: camelCase (formatScore, calculateSuitability)
  - constants: UPPER_SNAKE_CASE (NAV_LINKS, CHART_COLORS)
  - files: PascalCase for components, camelCase for everything else

Git:
  - branches: feat/short-description, fix/short-description, docs/short-description
  - commits: Conventional Commits (feat:, fix:, docs:, refactor:, test:, chore:)
  - messages: imperative mood ("Add feature X", not "Added feature X")
```

### Code Standards

```
1. SOLID Principles:
   - Single Responsibility: Each module does ONE thing
   - Open/Closed: Extend via plugins (model factory), don't modify base code
   - Liskov: BaseModel → all subclasses must implement fit(), predict(), feature_importances()
   - Interface Segregation: Don't force all models to support SHAP (use optional protocol)
   - Dependency Inversion: High-level training pipeline depends on BaseModel ABC, not concrete models

2. DRY Architecture:
   - No duplicated data loading (Single SolarDataLoader)
   - No duplicated preprocessing logic (Single preprocessing module)
   - No duplicated model creation (Single model factory pattern)
   - No duplicated evaluation metrics (Single compute_regression_metrics)

3. Typed Interfaces:
   - Python: Use type hints on all public functions
   - TypeScript: Define interfaces for all data structures (Site, Prediction, APIResponse)
   - Config: Pydantic BaseSettings for all configuration

4. Testing Standards:
   - Unit tests: Every public function in src/ml/, src/data_pipeline/
   - Integration tests: Full pipeline run with mock 4-row DataFrame
   - API tests: Every endpoint with valid + invalid + edge-case inputs
   - Frontend tests: Every page renders; user flows work with mocked API

5. Error Handling:
   - Python: Custom exceptions (DataPipelineError, ModelTrainingError, InferenceError)
   - API: Consistent error response format with error codes
   - Frontend: ErrorBoundary wrapper for each page; toast for non-critical errors
   - Logging: Structured logging (JSON format) in production; readable format in dev
```

### Documentation Discipline

Every module must contain a module-level docstring:
```python
"""
Module: ml/evaluation/metrics.py
Purpose: Compute and report standard regression metrics for ML model evaluation.
Dependencies: sklearn.metrics (r2_score, mean_absolute_error, mean_squared_error)
Expected Inputs: y_true (np.ndarray), y_pred (np.ndarray)
Expected Outputs: dict with keys "r2", "mae", "mse", "rmse", "mape"
Usage:
    from src.ml.evaluation.metrics import compute_regression_metrics
    metrics = compute_regression_metrics(y_test, y_pred)
"""
```

### Branching Strategy

```
main        — Production-ready, protected branch (no direct pushes)
├── develop  — Integration branch (nightly builds)
│   ├── feat/data-pipeline-fixes    — Sprint 1
│   ├── feat/ml-correctness        — Sprint 2
│   ├── feat/fastapi-backend       — Sprint 3
│   ├── feat/frontend-integration  — Sprint 4
│   └── feat/typescript-migration  — Sprint 5
├── hotfix/  — Emergency fixes
└── docs/    — Documentation-only changes
```

### Linting & Formatting

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.0.0
    hooks:
      - id: black
        args: [--line-length=100]
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort
```

For frontend:
```json
// .eslintrc.cjs
{
  "extends": ["eslint:recommended", "plugin:react/recommended", "plugin:@typescript-eslint/recommended"],
  "rules": {
    "react/prop-types": "off",  // TypeScript handles prop validation
    "no-unused-vars": "warn"
  }
}
```

---

## 3.9 Final Risk Assessment & Recommendations

### Critical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Misleading R² from physics-derived target** | Certain (already happened) | HIGH — undermines credibility of entire ML pipeline | Accept Option A (weighted composite index). Be transparent that this is a ranking system, not a predictive ML model. |
| **Frontend claims inflated metrics (88% R², 30K sites)** | Certain (already present) | HIGH — misleading users/researchers | Sprint 4: Replace all frontend metrics with real data (60 districts, weighted score) |
| **60-sample dataset is too small for ML** | High | MEDIUM — models will overfit or be useless | Accept limitation. Position as POC/pilot. Plan for data expansion (Option B: real CUF data) |
| **No real CUF ground truth** | High | HIGH — the entire premise of "AI site selection" is on shaky ground | Proactively seek real plant data. Until then, use transparent weighted index. |

### Medium Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **TypeScript migration breaks build** | Medium | MEDIUM — frontend blocked | Migrate incrementally (pages one at a time). Keep JS fallback. |
| **API connects but frontend data shape mismatch** | Medium | MEDIUM | Sprint 4: Define shared TypeScript interfaces between frontend and backend before implementing either. |
| **Docker deployment complexity** | Low | LOW — dev-only for now | Keep docker-compose simple. No Kubernetes until we have >100 users. |
| **GEE authentication for collaborators** | Medium | LOW — only during data refresh | Document GEE setup clearly. Cache downloaded data so re-auth not needed often. |

### Low Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Three.js bundle too large** | Low | LOW — already lazy-loaded | Keep lazy loading. Consider removing ParticleField if performance degrades on mobile. |
| **Leaflet dark tiles unavailable** | Low | LOW — use fallback tiles | Have OSM standard tiles as fallback URL. |
| **NASA POWER API rate limit** | Low | LOW — pre-collected data | Already cached in `outputs/raw/`. No live API calls in production. |

### Top 5 Recommendations (Ordered by Impact)

1. **Fix the ML narrative**: Stop claiming R² = 0.88. The physics-derived target makes this meaningless. Rebrand as a "weighted multi-criteria site ranking system." Do this NOW (frontend sprint, 1 day).

2. **Drop collinear features**: 40+ pairs with r > 0.9 make linear model coefficients unreliable. Drop `peak_sun_hours`, individual distance columns, `wasteland_builtup_pct`, and one of `solar_variability`/`solar_efficiency_index`. ~2 hours of work.

3. **Fix test-set leakage in HPO**: Both optimization scripts use the test set to select hyperparameters. This inflates test R². Fix by moving HPO to use only training data with cross-validation. Critical for credibility.

4. **Build the FastAPI backend**: The frontend is entirely mock-data-driven. A real API (even serving 60 districts) makes this a functioning product. This is the single biggest gap between aspiration and reality.

5. **Add comprehensive documentation**: This document serves as the "Source of Truth." Every subsequent implementation decision MUST reference it. No more ad-hoc decisions or aspirational claims without implementation.

---

## APPENDIX A: File Inventory (Post-Refactor)

### Files to DELETE
```
configs/                                    (empty directory)
src/ml/training/__init__.py                 (empty module)
reports/ensemble_summary.csv               (generated artifact)
reports/optimized_summary.csv              (generated artifact)
reports/ml_report.md                        (generated artifact — regenerated each run)
models/*.joblib                             (generated artifacts — exclude from git)
audit_outputs/                              (relocate outputs to reports/audit/)
ml_logs/ml_training.log                    (runtime artifact)
```

### Files to MERGE
```
train_ensemble.py + main.py              →  src/cli/train.py
src/ml/data_loader.py                    →  src/ml/pipelines/data.py
src/ml/optimization.py                   →  src/ml/optimization/hpo.py
```

### Files to RENAME
```
backend/data_pipeline/main.py            →  backend/data_pipeline/phase1_collect.py
backend/data_pipeline/phase2_3_pipeline.py →  backend/data_pipeline/run_pipeline.py
```

### New Files to CREATE
```
src/
├── cli/
│   ├── __init__.py
│   └── train.py
├── api/
│   ├── __init__.py
│   ├── main.py                          (FastAPI app)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── sites.py
│   │   ├── predictions.py
│   │   └── model.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── models.py
│   └── services/
│       ├── __init__.py
│       ├── inference.py
│       └── data.py
├── ml/
│   └── optimization/
│       └── __init__.py
│   └── utils/
│       ├── __init__.py
│       ├── logging.py
│       └── io.py

frontend/src/
├── types/
│   ├── site.ts
│   └── api.ts
├── store/
│   └── useStore.ts                      (Zustand store)

infrastructure/
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
└── scripts/
    └── deploy.sh

docs/
├── architecture/
│   └── system_overview.md
├── product/
│   └── prd.md
├── technical/
│   └── trd.md
├── development/
│   ├── setup.md
│   └── contributing.md
└── governance/
    ├── ml_standards.md
    └── code_review_checklist.md

pyproject.toml
Makefile
.pre-commit-config.yaml
```

---

## APPENDIX B: Quick Reference — Commands

```bash
# Development setup (after refactor)
python -m pip install -e ".[dev]"
pre-commit install

# Run data pipeline
cd src/data_pipeline && python run_pipeline.py --step all

# Run ML training
python -m src.cli.train --models ridge,lasso --feature-selection rfe --n-features 15

# Run tests
pytest tests/ -v --cov=src --cov-report=term

# Start API server
python -m src.api.main  # → http://localhost:8000

# Start frontend
cd frontend && npm run dev  # → http://localhost:5173

# Docker compose (all services)
docker compose -f infrastructure/docker/docker-compose.yml up

# Lint & format
make lint     # → ruff check + black check
make format   # → black + ruff fix + isort
make test     # → pytest + vitest
make build    # → docker build api + frontend
```

---

**End of Document**

*This document is the single "Source of Truth" for the SolarSite-India project. All future implementation, documentation, and decision-making must reference and align with this document. Version 1.0. Any deviations must be documented as amendments with explicit justification.*