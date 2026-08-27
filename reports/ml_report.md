# ML Training Report
## Model Comparison
| Model | Train R² | Test R² | CV R² ± std | Test RMSE | Features |
|-------|----------|---------|-------------|-----------|----------|
| ridge           | 0.9965 | 0.9961 | 0.9733±0.0141 | 0.000310 | 14 |

## Top Features by Model
### ridge
- solar_potential_score: 0.0079
- avg_ghi_kwh_m2_day: 0.0076
- avg_dni_kwh_m2_day: 0.0043
- effective_ghi: 0.0035
- avg_humidity_pct: 0.0034
- annual_rainfall_mm: 0.0024
- aridity_index: 0.0023
- solar_variability: 0.0011
- aod_2023: 0.0003
- avg_cloud_cover_pct: 0.0002
