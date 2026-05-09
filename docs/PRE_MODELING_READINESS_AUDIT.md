# SolarSite-India Pre-Modeling Readiness Audit

**Date**: 2026-05-08  
**Auditor**: Senior Data Science Engineer, ML Validation Specialist  
**Dataset**: SolarSite-India (Post-Processing, Post-Refactor)  
**Model Family**: Solar PV Site Suitability (Regression)  
**Status**: Pre-Modeling  

---

## 1. EXECUTIVE SUMMARY

This Pre-Modeling Readiness Audit evaluates the SolarSite-India pipeline after successful completion of Stages 1–3 (Logic Correction, Architectural Refinement, and Preliminary Validation). The goal is to determine whether the processed dataset is statistically sound, free of leakage, and modeling-ready.

### Key Findings at a Glance

| Domain | Finding | Severity |
|--------|---------|----------|
| **Data Leakage** | Imputation + encoding applied on full dataset **before** train/test split | **CRITICAL** |
| **Multicollinearity** | 4 pairs with perfect/near-perfect correlation (VIF = inf); 40 pairs with \|r\|>0.8 | **CRITICAL** |
| **Outliers** | 22 outliers (36.7%) in `population_density_per_sqkm` on 60-row dataset | **HIGH** |
| **Missingness** | 0 missing values in final dataset; imputed earlier with known leakage | **MEDIUM** |
| **Pipeline Leakage** | No district overlap; scaling is train-only; target leaker removed | **PASS** |
| **Reproducibility** | Deterministic (seed=42); modular; requires input-path injection for testing | **PASS** |
| **Reproducibility** | Deterministic (seed=42); modular; testable minus path-injection | **PASS** |

---

## 2. PIPELINE AUDIT FINDINGS

### 2.1 Data Leakage Analysis

#### A. Imputation **BEFORE** Train/Test Split (CRITICAL)

**Code Location**: `solarpipeline/preprocess.py`, lines 99–100

```python
Imputation order:  
99: _impute_numeric(features, numeric_cols)  # leaks test statistics into training 
100: _encode_categorical(features, cat_cols) # leaks test categories into encoding  
103: train_test_split(...)
```

**Issue**: Median values for imputation, and category encodings, are computed on the **full** dataset (60 rows), not the training set (48 rows). This means test data contributes to the fill/encoding statistics, leaking distribution information from test → model training.

**Impact**: In production, this would fail because new test data would not have the combined distribution statistics. The model is trained with information it wouldn't have in production.

**Quantification**: In this particular dataset, there are only NaN in `census_pop_2011` (61.7% missing), which makes the leakage substantial and visible in the median.

#### B. Perfect Multicollinearity (CRITICAL)

**Engineered features perfectly correlated by construction:**

| Feature Pair | r | Why | VIF |
|-------------|---|---|-----|
| `avg_ghi_kwh_m2_day` ↔ `peak_sun_hours` | 1.0000 | `peak_sun_hours` = `avg_ghi` × 0.4 | inf |
| `dist_nearest_road_km` ↔ `dist_nearest_transmission_line_km` | 0.9999 | Heuristic-generated, same formula | inf |
| `dist_nearest_road_km` ↔ `dist_nearest_substation_km` | 0.9999 | Heuristic-generated, same formula | inf |
| `dist_nearest_transmission_line_km` ↔ `dist_nearest_substation_km` | 0.9999 | Heuristic-generated, same formula | inf |
| `builtup_pct` ↔ `wasteland_builtup_pct` | 0.9975 | `wasteland_builtup_pct` = `wasteland_pct` + `builtup_pct` + buffer | inf |

**Impact**: Any linear model (Ridge, Lasso, OLS, elastic net) will crash or produce unstable coefficients due to singular matrices. The full regression model becomes non-identifiable and nonsensical.

**Recommendation**: 
- Drop `peak_sun_hours` (it is a redundant multiplier of avg_ghi)
- Drop all three individual distance features; keep only `infrastructure_accessibility_index` (their composite)
- Drop `wasteland_builtup_pct` (keep `wasteland_pct` and `builtup_pct` separately, or keep the composite and drop individual)

#### C. Leakage Verification (PASS)

| Check | Method | Result |
|-------|--------|--------|
| District overlap | `set(f_train.district) & set(f_test.district)` | 0 (PASS) |
| Target leakage (`installed_solar_capacity_mw`) | Column presence | Not present (PASS) |
| Target-derived features | Search for "cuf" in features | None (PASS) |
| Scaling computation | `scaling_params.csv` generated from train? | 39 rows = train-only (PASS) |
| Randomness | Seed set? | `random_state=42` (PASS) |

### 2.2 Missing Value Handling (MEDIUM with leakage)

| Column | Missing Before | % Missing | Imputation Strategy | Leakage? |
|--------|---------------|-----------|-------------------|----------|
| `census_pop_2011` | 37 / 60 | 61.7% | Full median | YES |
| `census_pop_2024_projected` | 0 / 60 | 0.0% | N/A | No |

- **Stage 2 action**: Median imputation applied before split (leakage)
- **Root cause of NaN**: Census data gap for several newly reorganized districts; handled by `safe_read_csv` and imputed downstream

### 2.3 Outlier Handling (HIGH)

**Current state**: No outlier treatment. StandardScaler is applied, which is sensitive to outliers.

**Features with extreme outlier counts (IQR method, pre-scaled):**
- `population_density_per_sqkm`: **22 outliers** (36.7% of rows) ← critical
- `terrain_flatness_score`: 11 outliers (18.3%)
- `wetland_pct`: 9 outliers (15.0%)

**Impact on models**: Linear and distance-based models (SVM, kNN) are highly sensitive. Tree-based models are robust, but decision thresholds become very sensitive with extreme values.

### 2.4 Feature Engineering Review

| Feature | Source Construction | Validity | Risk |
|---------|---------------------|----------|------|
| `solar_variability` | `avg_dni / (avg_dhi + 0.01)` | Valid | Medium (collinear with others) |
| `peak_sun_hours` | `avg_ghi * 0.4` | REDUNDANT | **CRITICAL** — perfectly collinear with avg_ghi |
| `solar_efficiency_index` | `avg_dni / (avg_ghi + 0.01)` | Valid | Medium (ratio of related variables) |
| `terrain_flatness_score` | `1 / (1 + slope)` | Valid | Low |
| `infrastructure_accessibility_index` | Weighted harmonic mean of distances | Valid | Low |
| `wasteland_builtup_pct` | `wasteland + builtup` | REDUNDANT | **CRITICAL** — near-perfect collinear with builtup |
| `forest_proximity_km` | `100 / (tree_cover + 1)` | Valid | Low |
| `dominant_land_use` | `idxmax` on `_pct` columns | **BROKEN** | CODE BUG — no land cols pass the filter |
| `climate_stress_index` | `temp * humidity / 1000` | Valid | Low |
| `humidity_temp_interaction` | `humidity * max_temp / 1000` | Valid | Low |

**Feature design issue**: `dominant_land_use` is intended to be categorical but fails completely because every `_pct` column is in the exclusion list. The try/except swallows the error silently, so no buggy column is added. But the intended behavior never executes.

### 2.5 Pipeline Reproducibility & Code Quality

| Criterion | Assessment |
|-----------|------------|
| Deterministic | ✅ `random_state=42` on split; reproducible run |
| Modular | ✅ 7-module `solarpipeline` package with SRP |
| Serialization | ⚠️ `label_encoders.csv` saved but no formal load/save API for deployment |
| sklearn compatibility | ⚠️ Not yet a `Pipeline` object; manual ordering allows leakage (see imputation order) |
| Test coverage | 29/29 pytest passing |
| Docstrings | ✅ PEP-257 compliant |

---

## 3. STATISTICAL HEALTH CHECK

### 3.1 Feature Correlation & Multicollinearity

- **Pairs above |r| = 0.8**: 40 pairs
- **Pairs above |r| = 0.9**: 21 pairs
- **Pairs above |r| = 0.95**: 17 pairs
- **Perfect collinearity (r = 1.000)**: 3 pairs

**Top 10 most correlated pairs:**

| Rank | Feature 1 | Feature 2 | r |
|------|-----------|-----------|---|
| 106 | avg_ghi_kwh_m2_day | peak_sun_hours | 1.0000 |
| 457 | dist_nearest_road_km | dist_nearest_substation_km | 0.9999 |
| 456 | dist_nearest_road_km | dist_nearest_submission_line_km | 0.9999 |
| 481 | dist_nearest_transmission_line_km | dist_nearest_substation_km | 0.9999 |
| 640 | builtup_pct | wasteland_builtup_pct | 0.9975 |

**VIF (Variance Inflation Factor):**

| Feature | VIF | Status |
|---------|-----|--------|
| avg_ghi_kwh_m2_day | inf | Perfect collinearity |
| peak_sun_hours | inf | Perfect collinearity |
| builtup_pct | inf | Perfect collinearity |
| cropland_pct | 11,389,078 | Astronomical |
| wasteland_pct | 4,194,304 | Astronomical |

### 3.2 Target Variable Analysis

- **Mean**: 0.1490
- **Std**: 0.0053
- **Skewness**: 0.068 (nearly symmetric)
- **Kurtosis**: -0.321 (platykurtic — flatter than normal)
- **Distribution**: Well-behaved, narrow range for a regression target
- **Stratification**: Applied by `state`, but for regression, stratification is typically not needed. However, with n=60, ensuring balanced representation of each state is reasonable.

### 3.3 Feature Scaling Validation

| Aspect | Assessment |
|--------|-----------|
| Scaler choice | StandardScaler (z-score) — appropriate for linear models, neural nets, SVM |
| Train-only fit | ✅ Verified (check `scaling_params.csv`) |
| Robustness to outliers | ⚠️ Skewed features (skew>3) with outliers will dominate distances |
| Orthogonality | N/A — StandardScaler does not address multicollinearity |

**Recommendation for current model family**:
- If the target model is **tree-based** (Random Forest, XGBoost, LightGBM): StandardScaler is unnecessary; features should be used in their original scale.
- If the target model is **distance-based** (SVM, KNN): StandardScaler is correct but should be combined with RobustScaler for outlier-heavy features.

### 3.4 Distribution Diagnostics

**Skewness & Kurtosis:**

| Feature | Skewness | Kurtosis | Recommendations |
|---------|----------|----------|-----------------|
| `population_density_per_sqkm` | 7.724 | 59.773 | Log-transform or RobustScaler |
| `wetland_pct` | 6.422 | 43.872 | Log-transform or cap at 95th percentile |
| `slope_deg` | 6.166 | 43.248 | Log-transform |
| `builtup_pct` | 4.243 | 20.245 | Cap at 95th percentile |
| `wasteland_builtup_pct` | 4.133 | 19.445 | Cap at 95th percentile |

**Key observations**:
- `solar_variability` (coefficient of variation): moderate skew in some regions
- Rest are relatively well-behaved.

---

## 4. DATA QUALITY & CONSISTENCY AUDIT

### 4.1 Inconsistent Labels

- **CUF label drift between train and test**: 0 discrepancies
- **State label consistency**: All train/test labels consistent

### 4.2 Duplicate Rows & Near Duplicates

| Check | Count | Status |
|-------|-------|--------|
| Exact duplicate rows (train) | 0 | ✅ PASS |
| Exact duplicate rows (test) | 0 | ✅ PASS |
| Near-duplicate numeric vectors | 0 | ✅ PASS |

### 4.3 Invalid / Impossible Values (Pre-Scaling)

| Feature | Check | Pass/Fail | Note |
|---------|-------|-----------|------|
| `avg_ghi_kwh_m2_day` | 4.9–5.7 kWh/m²/day within known Indian range | ✅ | Valid |
| `avg_dni_kwh_m2_day` | 3.5–4.2 kWh/m²/day within range | ✅ | Valid |
| `avg_temp_c` | 23.8–28.3°C within expected range | ✅ | Valid |
| `annual_rainfall_mm` | 100–160 mm within Telangana/AP range | ✅ | Valid |
| `population_density_per_sqkm` | 0–26,759 is extremely high range | ⚠️ WARN | Verify for outliers |
| `dist_nearest_road_km` | 1–4 km, heuristic values | ⚠️ WARN | Synthetic data, not real |
| `slope_deg` | 0.2–52°, range is 52° is possible but extreme | ⚠️ WARN | Verify for outliers |

### 4.4 Data Drift (Train vs Test)

**Kolmogorov-Smirnov test (α=0.05):**

- **✅ No feature shows statistically significant drift.** All p-values > 0.05.
- Highest drift: `avg_wind_speed_m_s` (KS=0.354, p=0.156) and `grassland_pct` (KS=0.354, p=0.156)
- Both are non-significant, confirming the stratified split preserved distributions.

### 4.5 Missing Value Heatmap

- **Total missing values in final dataset**: 0
- **Imputation occurred during pipeline**: Yes (census_pop_2011, 37/60 rows)
- **All NaN present before imputation**: Yes, in generated master data
- **Imputation effect**: Filled with full median (leakage risk, see Section 2.1)

---

## 5. VISUALIZATION INSIGHTS

Generated visualizations are available in `audit_outputs/`:

| Visualization | File | Insight |
|--------------|------|---------|
| Correlation Heatmap | `correlation_heatmap.png` | Identifies clusters of redundancy among land-use and distance features |
| CUF Distribution | `cuf_distribution.png` | Nearly symmetric, narrow range — serviceable for regression |
| Skewness Bar Chart | `skewness_bar.png` | Population density dominates with skew=7.7 |
| Outlier Boxplots | `outlier_boxplots.png` | Confirms 22 outliers in population density |
| VIF Plot | `vif_bar.png` | Log-scale confirms infinite VIF for 3 features |
| Perfect Collinearity Scatter | `scatter_perfect_collinear.png` | Visual confirmation of 1:1 linear dependencies |

---

## 6. MODELING READINESS VERDICT

### 6.1 Passing Items (✅)

| Item | Verdict |
|------|---------|
| No district overlap between train/test | ✅ This is correct (no leakage by geography) |
| No target-derived features | ✅ No `cuf` information in features |
| Scaling is train-only | ✅ Verified from `scaling_params.csv` |
| Deterministic | ✅ `random_state=42` |
| 0 missing values | ✅ Ensure downstream models receive a full matrix |

### 6.2 Failing / Critical Items (⛔)

| Item | Severity |
|------|----------|
| Imputation + encoding on full dataset before split | **CRITICAL** |
| Perfect multicollinearity (VIF=inf, r=1.0) | **CRITICAL** |
| No outlier treatment for 22 outlier population density | **HIGH** |
| 40 correlated pairs >0.8 | **HIGH** |
| Feature count (39) vs n=60 | **HIGH** |

### 6.3 Issues Requiring Action

| Item | Severity | Explanation |
|------|----------|-------------|
| Fix imputation order (split first → impute train → test) | **CRITICAL** | Prevents leakage of test distribution |
| Drop `peak_sun_hours` or `avg_ghi_kwh_m2_day` | **CRITICAL** | Perfect multicollinearity |
| Drop `dist_road`, `dist_power_line`, `dist_substation` (keep `infrastructure_accessibility_index` only) | **CRITICAL** | Perfect multicollinearity |
| Drop `wasteland_builtup_pct` or `builtup_pct` | **CRITICAL** | Near-perfect multicollinearity |
| Apply `log1p` or robust scaling to `population_density_per_sqkm`, `wetland_pct`, `slope_deg` | **HIGH** | Heavy skewness |
| Cap outliers (e.g., 95th percentile) for population_density | **HIGH** | 22 outliers is 36.7% of 60 rows |
| Fix `dominant_land_use` logic (can't be derived if all categorical excluded) | **MEDIUM** | Code bug, silently fails (Penang doesn't have a land column) |
| Reduce feature space from 39 to ~15–20 via RFE | **RECOMMEND** | Sample size vs dimensionality challenge |

---

## 7. PRIORITIZED REMEDIATION PLAN

### 7.1 Critical Problems (Fix Before Modeling)

| # | Issue | Root Cause | Recommended Fix | Impact |
|---|-------|-----------|-----------------|--------|
| 1 | Full-dataset imputation | Median computed on 60 rows pre-split | Move imputation to per-split: train fit → train_test_split → transform | Removes distribution leakage |
| 2 | Perfect collinearity (peak_sun_hours) | `peak_sun_hours = avg_ghi * 0.4` | Drop `peak_sun_hours` (or drop `avg_ghi` and keep `peak_sun_hours`) | Enables linear model convergence |
| 3 | Perfect collinearity (distances) | Heuristic OSM data is identical source | Drop all 3 individual distances; keep `infrastructure_accessibility_index` | Prevents singular matrices |
| 4 | Near collinearity (builtup) | `wasteland_builtup_pct = wasteland + builtup` | Drop `wasteland_builtup_pct`; keep components | Reduces VIF |

### 7.2 High Priority Problems

| # | Issue | Recommended Fix | Impact |
|---|-------|-----------------|--------|
| 5 | 22 outliers in `population_density` | Cap at 95th percentile, or winsorize, or log-transform | Improves robustness for linear models |
| 6 | 40 correlated pairs >0.8 | Reduce feature space using RFE (e.g., `sklearn.feature_selection.RFECV`) | Smaller model, better generalization |
| 7 | Skewness >3 for 3 features | Apply `log1p` or Yeo-Johnson transformation before scaling | Less outlier influence |

### 7.3 Medium Priority Improvements

| # | Issue | Recommended Fix |
|---|-------|-----------------|
| 8 | `dominant_land_use` silent failure | Either fix the exclusion logic or remove feature entirely from code |
| 9 | No outlier detection pipeline | Add RobustScaler for non-tree models; keep StandardScaler for 
| 10 | Hardcoded paths in tests | Refactor `merge_sources` to accept `raw_dir` parameter for test injection |

### 7.4 Nice-to-Have Enhancements

| # | Improvement | Value |
|---|-------------|-------|
| 11 | Feature Importance (F-Select) | Pre-emptively select top-15 features before ML training |
| 12 | PCA / UMAP | Visualize clusters for additional insights, but not needed for modeling |
| 13 | ColumnTransformer Pipeline | Replace manual imputation/encoding with sklearn `Pipeline` and `ColumnTransformer` for full serialization |

---

## 8. RISK ANALYSIS

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Linear model fails to converge due to perfect multicollinearity | **HIGH** | **CRITICAL** | Remove linear-dependent features |
| Data leakage from imputation inflates apparent model performance | **MEDIUM** | **CRITICAL** | Reorder split before imputation; re-run evaluation |
| Model overfits due to 39 features × 48 samples | **HIGH** | **HIGH** | Aggressive feature selection (RFE, Lasso) |
| Infrastructure features are synthetic (not real-world) | **HIGH** | **MEDIUM** | Document for deployment; prioritize real OSM data |
| Production model fails on unseen data with missing values | **MEDIUM** | **HIGH** | Fix imputation order; serialize median dict; validate inputs |
| Outliers in population_density dominate scaled distance | **MEDIUM** | **MEDIUM** | Apply RobustScaler or winsorize |

---

## 9. FINAL RECOMMENDATION

### Verdict: ⚠️ **CONDITIONAL GO — Critical fixes required before model training**

### Justification

The pipeline is **architecturally sound** after Stage 2 refactoring (modular, testable, secure). However, the dataset **contains two critical blockers that must be resolved** before any supervised learning can proceed safely:

1. ⛔ **Imputation is applied before the train-test split**, causing data leakage.
2. ⛔ **Perfect multicollinearity** renders linear models non-identifiable and may break distance-based models if they rely on covariances.

### Required workflow

1. **Fix leakage** (reorder split → impute → scale)
2. **Remove perfectly collinear features** (`peak_sun_hours` and `dist_*` individual distances)
3. **Handle outliers** for `population_density_per_sqkm`
4. **Re-run the pipeline** to generate cleansed `features_train.csv` and `features_test.csv`
5. Run `pytest` to verify no regressions
6. Re-run this audit to verify clean results
7. **After remediation, proceed to ML modeling**

### Expected Timeline for Remediation

| Task | Effort |
|------|--------|
| Fix imputation order | ~30 min |
| Drop collinear features | ~15 min |
| Re-run pipeline + tests | ~30 min |
| Re-audit | ~15 min |
| **Total** | **~1.5 hours** |

---

**Report End. Contact: Senior DS Engineer, ML Validation Team**
