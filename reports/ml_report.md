# ML Training Report
## Model Comparison
| Model | Train R² | Test R² | CV R² ± std | Test RMSE | Features |
|-------|----------|---------|-------------|-----------|----------|
| ridge           | 0.9891 | 0.1533 | 0.0133±1.0467 | 0.012107 | 10 |
| lasso           | 0.9891 | 0.1601 | -0.9517±2.7399 | 0.012058 | 10 |
| random_forest   | 0.2157 | 0.0588 | -9.1727±16.6789 | 0.012765 | 10 |
| xgboost         | -0.0000 | -0.0483 | -8.7707±15.7356 | 0.013472 | 10 |

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
