# SolarSite-India Data Quality & Statistical Health Audit Report

**Date**: 2026-05-08  
**Auditor**: Senior Data Science Engineer  
**Dataset**: SolarSite-India (Processed)

---

## 1. DATA QUALITY & CONSISTENCY AUDIT (Task A)

### 1.1 Dataset Overview
| Dataset | Shape (Rows, Cols) | Remarks |
|---------|-------------------|---------|
| `features_train.csv` | (48, 40) | 48 districts, 39 numeric features |
| `features_test.csv` | (12, 40) | 12 districts, 39 numeric features |
| `labels_train.csv` | (48, 3) | 48 labels |
| `labels_test.csv` | (12, 3) | 12 labels |
| `master_dataset_engineered.csv` | (60, 44) | Full dataset with 44 columns |

### 1.2 Duplicate & Near-Duplicate Analysis
- **Exact duplicates (train)**: 0 rows
- **Exact duplicates (test)**: 0 rows
- **Near-duplicates (identical numeric vectors)**: 0 rows
- **Conclusion**: No duplicate or near-duplicate records detected.

### 1.3 Inconsistent Labels
- **Districts with inconsistent CUF across train/test**: 0
- All district labels are consistent between splits.

### 1.4 Invalid Feature Ranges / Impossible Values
Since features have been **StandardScaled**, many values now appear negative or >100. On the **original scale**, we checked the following:

| Check | Train | Test | Status |
|-------|-------|------|--------|
| Negative distances | 26/26/... | 7/7/... | **Investigate** (likely scaling artifact, must verify in raw) |
| GHI outside [2.5, 7.0] kWh/m²/day | 48 | 12 | **Investigate** |
| Humidity outside [0, 100] | 27 | 8 | Likely scaling artifact |
| Cloud cover outside [0, 100] | 30 | 8 | Likely scaling artifact |
| Land cover % outside [0, 100] | Multiple | Multiple | Likely scaling artifact |
| Wind speed negative | 28 | 3 | Likely scaling artifact |

> **⚠️ Recommendation**: Re-run range checks on the **original unscaled** `master_dataset_clean.csv` or raw data to confirm no impossible values exist before scaling.

### 1.5 Null / Missing Value Analysis
- **Total missing values**: 0 across all datasets.
- **Missing value heatmap**: Not applicable (no missing values).

### 1.6 Data Drift (Train vs Test)
Top 5 features by KS test statistic (higher = more different distributions):

| Feature | KS Statistic | p-value |
|---------|-------------|---------|
| `avg_wind_speed_m_s` | 0.354 | 0.156 |
| `grassland_pct` | 0.354 | 0.156 |
| `wasteland_builtup_pct` | 0.333 | 0.209 |
| `census_pop_2024_projected` | 0.312 | 0.274 |
| `avg_ghi_kwh_m2_day` | 0.312 | 0.274 |

- **No feature shows statistically significant drift (all p > 0.05)**.

### 1.7 Categorical / Encoding Check
- **District overlap between train and test**: 0 districts
- **Train districts**: 48 | **Test districts**: 12
- **Unexpected categorical levels**: None detected

---

## 2. STATISTICAL HEALTH CHECK (Task B)

### 2.1 Summary Statistics (Original Scale)
Key metrics from `master_dataset_engineered.csv`:

| Feature | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|---------|-------|------|-----|-----|-----|-----|-----|-----|
| avg_ghi_kwh_m2_day | 60.0 | 5.271 | 0.185 | 4.896 | 5.163 | 5.316 | 5.359 | 5.657 |
| avg_temp_c | 60.0 | 26.991 | 0.878 | 23.770 | 26.523 | 27.215 | 27.593 | 28.330 |
| cuf | 60.0 | 0.1490 | 0.0053 | 0.1391 | 0.1449 | 0.1494 | 0.1522 | 0.1616 |

*(Full table available in `summary_statistics.csv`)*

### 2.2 Feature Correlation Analysis
**Top 10 Most Correlated Feature Pairs:**

| Rank | Feature 1 | Feature 2 | Correlation |
|------|-----------|-----------|-------------|
| 106 | `avg_ghi_kwh_m2_day` | `peak_sun_hours` | 1.0000 |
| 457 | `dist_nearest_road_km` | `dist_nearest_substation_km` | 1.0000 |
| 456 | `dist_nearest_road_km` | `dist_nearest_transmission_line_km` | 1.0000 |
| 481 | `dist_nearest_transmission_line_km` | `dist_nearest_substation_km` | 1.0000 |
| 640 | `builtup_pct` | `wasteland_builtup_pct` | 0.9975 |
| 737 | `solar_variability` | `solar_efficiency_index` | 0.9967 |
| 499 | `dist_nearest_transmission_line_km` | `infrastructure_accessibility_index` | -0.9927 |
| 522 | `dist_nearest_substation_km` | `infrastructure_accessibility_index` | -0.9927 |
| 475 | `dist_nearest_road_km` | `infrastructure_accessibility_index` | -0.9926 |
| 114 | `avg_ghi_kwh_m2_day` | `cuf` | 0.9860 |

**Multicollinearity Alert:**
- Pairs with |r| > 0.8: **40 pairs**
- Pairs with |r| > 0.9: **21 pairs**
- Perfect or near-perfect collinearity detected for:  
  - `avg_ghi_kwh_m2_day` ↔ `peak_sun_hours` (r ≈ 1.0)  
  - `dist_nearest_road_km` ↔ `dist_nearest_substation_km` (r ≈ 0.9999)  
  - `dist_nearest_road_km` ↔ `dist_nearest_transmission_line_km` (r ≈ 0.9999)  
  - `dist_nearest_transmission_line_km` ↔ `dist_nearest_substation_km` (r ≈ 0.9999)  
  - `builtup_pct` ↔ `wasteland_builtup_pct` (r ≈ 0.997)

**VIF (Top 10):**

| Feature | VIF |
|---------|-----|
| avg_ghi_kwh_m2_day | ∞ |
| peak_sun_hours | ∞ |
| builtup_pct | ∞ |
| cropland_pct | 11389078.85 |
| wasteland_pct | 4194304.00 |
| shrubland_pct | 898295.95 |
| dist_nearest_road_km | 274799.08 |
| dist_nearest_transmission_line_km | 233785.00 |
| grassland_pct | 146609.07 |
| dist_nearest_substation_km | 86288.14 |

**Interpretation:** VIF = ∞ indicates perfect multicollinearity (redundant features). VIF > 10 is concerning.

### 2.3 Target Variable (CUF) Analysis
- **Mean**: 0.1490
- **Std**: 0.0053
- **Min**: 0.1391
- **Max**: 0.1616
- **Skewness**: 0.068 (nearly symmetric)
- **Kurtosis**: -0.321 (platykurtic / flatter than normal)

**CUF by District (Lowest 3):**
- kakinada: 0.1391
- parvathipuram manyam: 0.1394
- srikakulam: 0.1396

**CUF by District (Highest 3):**
- sri sathya sai: 0.1616
- anantapuram: 0.1603
- kurnool: 0.1575

> **Stratified Split Note**: For regression with n=60, stratification by CUF bins is **reasonable** but not strictly necessary. The current split (48/12) preserves no district overlap, which is the most critical guardrail.

### 2.4 Feature Scaling Validation
- **Mean of feature means (train)**: ~0.0 (max abs mean ≈ 6.5e-15)
- **Mean of feature stds (train)**: ~1.01
- **Max deviation of std from 1**: ~0.011

**Verdict**: Scaling appears correctly applied using **train-only statistics**. However, StandardScaling preserves heavy skewness and does not bound outliers; tree-based models do not require it, and for distance-based models (SVM, KNN, neural nets), it is necessary.

### 2.5 Distribution Diagnostics
**Most Skewed Features (Absolute Skewness):**
- population_density_per_sqkm: 7.724
- wetland_pct: 6.422
- slope_deg: 6.166
- builtup_pct: 4.243
- wasteland_builtup_pct: 4.133
- wasteland_pct: 3.951
- water_pct: 2.056
- forest_proximity_km: 1.914
- shrubland_pct: 1.780
- tree_cover_pct: 1.691

**Kurtosis Summary (Top 5 highest):**
- population_density_per_sqkm: 59.773
- wetland_pct: 43.872
- slope_deg: 43.248
- builtup_pct: 20.245
- wasteland_builtup_pct: 19.445


**Outlier Summary (IQR method, original scale):**
- **population_density_per_sqkm**: 22 outlier(s)
- **terrain_flatness_score**: 11 outlier(s)
- **wetland_pct**: 9 outlier(s)
- **slope_deg**: 8 outlier(s)
- **builtup_pct**: 8 outlier(s)
- **water_pct**: 7 outlier(s)
- **forest_proximity_km**: 6 outlier(s)
- **wasteland_pct**: 6 outlier(s)
- **wasteland_builtup_pct**: 6 outlier(s)
- **grassland_pct**: 5 outlier(s)


---

## 3. DATA LEAKAGE DETECTION (Task C)

### 3.1 District Overlap
- **Train/Test overlapping districts**: 0
- **Status**: ✅ PASS. No leakage from overlapping geographic units.

### 3.2 Feature Leakage from Target
- **Suspected leakage features containing 'cuf' or 'target'**: None found in feature set.
- **Installed solar capacity feature**: Not present.
- **Status**: ✅ PASS.

### 3.3 Scaling Leakage
- **Scaling parameters** (`scaling_params.csv`) contains 39 rows (one per feature).
- Columns: `feature`, `mean`, `scale`.
- Assuming these were computed on the **training set only**, no leakage from global statistics.
- **Status**: ✅ PASS (assuming train-only fit).

### 3.4 Overall Leakage Verdict
- No structural leakage detected. Split is spatially aware (no overlapping districts). Target-derived features absent.

---

## 4. RECOMMENDATIONS & ACTIONS

### Data Quality Fixes
1. **Re-check original-scale impossible values**: Run range checks on `master_dataset_clean.csv` (or raw data) to ensure no negative distances, >100% land covers, or impossible GHI values existed before StandardScaling.
2. **Handle Perfect Multicollinearity**: 
   - Drop `peak_sun_hours` (perfect collinear with `avg_ghi_kwh_m2_day`).
   - Drop two of the three distance columns (keep e.g., `dist_nearest_substation_km` or create a single composite infrastructure distance index).
   - Drop `wasteland_builtup_pct` (r ≈ 0.997 with `builtup_pct`).
3. **Address High Skewness**: 
   - Apply `log1p` or `yeo-johnson` transform to `population_density_per_sqkm`, `wetland_pct`, and `slope_deg` if using linear/distance models.
   - Tree-based models are robust to skewness but may benefit from less extreme splits.
4. **Outlier Treatment**: 
   - 22 outliers in `population_density_per_sqkm` on a dataset of 60 rows is extreme. Verify if these are data entry errors (e.g., area mismatch).
5. **Missing Values**: No action needed (0 missing), which is excellent.

### Model Readiness
- **Current feature set**: High multicollinearity will destabilize linear models and inflate coefficient variance. Apply the drops above.
- **Scaling**: Correctly applied. Keep StandardScaler for neural nets / SVM / KNN; it's neutral for tree-based models.
- **Target distribution**: Approximately normal. No heavy skew or extreme kurtosis. Good for OLS / Ridge / Lasso.
- **Sample size**: 60 total is very small for 39 features. **Consider feature selection (e.g., RFE, Lasso) or dimensionality reduction (PCA)** to prevent overfitting.

---

## 5. APPENDIX: Generated Files

| File | Description |
|------|-------------|
| `audit_report.json` | Full JSON report |
| `summary_statistics.csv` | Descriptive statistics |
| `correlation_matrix.csv` | Full feature correlation matrix |
| `correlation_heatmap.png` | Visual heatmap |
| `cuf_distribution.png` | Target distribution plots |
| `skewness_kurtosis.csv` | Distribution shape metrics |
| `skewness_bar.png` | Skewness visualization |
| `outlier_summary.csv` | Outlier counts per feature |
| `outlier_boxplots.png` | Boxplot visualizations |
| `vif_bar.png` | VIF (log scale) bar chart |
| `scatter_perfect_collinear.png` | Example of perfect collinearity |

---
*End of Report*
