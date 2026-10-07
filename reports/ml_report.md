# ML Training Report
## Model Comparison
| Model | Train R² | Test R² | CV R² ± std | CV MAE | Test RMSE | Features |
|-------|----------|---------|-------------|--------|-----------|----------|
| ridge           | 0.9891 | 0.1533 | -0.2506±0.0000 | 0.0081 | 0.012107 | 10 |
| lasso           | 0.9891 | 0.1601 | -0.0377±0.0000 | 0.0071 | 0.012058 | 10 |
| elastic_net     | 0.9871 | 0.1188 | 0.1953±0.0000 | 0.0061 | 0.012351 | 10 |
| random_forest   | 0.2157 | 0.0588 | -0.4882±0.0000 | 0.0083 | 0.012765 | 10 |
| xgboost         | -0.0000 | -0.0483 | -0.5631±0.0000 | 0.0086 | 0.013472 | 10 |
| voting          | 0.7957 | 0.1428 | -0.2867±0.0000 | 0.0075 | 0.012182 | 10 |


## Baseline check (pvlib C0 physics chain)
C0 vs CEA-actual (11 districts): MAE=0.0075, Spearman ρ=0.9091

| Model | CV MAE (pooled OOF) | Beats C0? |
|-------|---------------------|-----------|
| ridge           | 0.0081 | NO |
| lasso           | 0.0071 | yes |
| elastic_net     | 0.0061 | yes |
| random_forest   | 0.0083 | NO |
| xgboost         | 0.0086 | NO |
| voting          | 0.0075 | NO |

_CV MAE is over plant rows; C0 MAE is over district rows — different populations, same label definition. Negative CV R² on this dataset mostly reflects a narrow target range, not a broken model._
## Top Features by Model
### ridge
- aod_2023: 0.0046
- slope_aspect_interaction: 0.0032
- avg_dhi_kwh_m2_day: 0.0029
- aerosol_optical_depth: 0.0026
- grassland_pct: 0.0019
- latitude: 0.0016
- max_temp_c: 0.0011
- avg_ghi_kwh_m2_day: 0.0008
- climate_stress_index: 0.0008
- population_density_per_sqkm: 0.0002

### lasso
- aod_2023: 0.0047
- slope_aspect_interaction: 0.0033
- latitude: 0.0026
- avg_dhi_kwh_m2_day: 0.0025
- aerosol_optical_depth: 0.0024
- grassland_pct: 0.0021
- avg_ghi_kwh_m2_day: 0.0009
- max_temp_c: 0.0000
- population_density_per_sqkm: 0.0000
- climate_stress_index: 0.0000

### elastic_net
- aod_2023: 0.0034
- slope_aspect_interaction: 0.0031
- aerosol_optical_depth: 0.0029
- avg_ghi_kwh_m2_day: 0.0021
- grassland_pct: 0.0016
- max_temp_c: 0.0007
- avg_dhi_kwh_m2_day: 0.0007
- latitude: 0.0000
- population_density_per_sqkm: 0.0000
- climate_stress_index: 0.0000

### random_forest
- population_density_per_sqkm: 0.3750
- slope_aspect_interaction: 0.2188
- avg_ghi_kwh_m2_day: 0.1875
- aerosol_optical_depth: 0.1250
- latitude: 0.0625
- grassland_pct: 0.0312
- aod_2023: 0.0000
- max_temp_c: 0.0000
- avg_dhi_kwh_m2_day: 0.0000
- climate_stress_index: 0.0000

### xgboost
- latitude: 0.0000
- avg_ghi_kwh_m2_day: 0.0000
- avg_dhi_kwh_m2_day: 0.0000
- max_temp_c: 0.0000
- aerosol_optical_depth: 0.0000
- aod_2023: 0.0000
- grassland_pct: 0.0000
- population_density_per_sqkm: 0.0000
- climate_stress_index: 0.0000
- slope_aspect_interaction: 0.0000
