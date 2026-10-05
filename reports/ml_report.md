# ML Training Report
## Model Comparison
| Model | Train R² | Test R² | CV R² ± std | Test RMSE | Features |
|-------|----------|---------|-------------|-----------|----------|
| ridge           | 0.6181 | -0.1961 | -0.3623±0.8524 | 0.011063 | 10 |
| lasso           | 0.6181 | -0.1960 | -0.3617±0.8526 | 0.011062 | 10 |

## Top Features by Model
### ridge
- avg_ghi_kwh_m2_day: 0.0088
- population_pressure: 0.0061
- aspect_deg: 0.0050
- elevation_m: 0.0041
- longitude: 0.0032
- population_density_per_sqkm: 0.0023
- builtup_pct: 0.0012
- shrubland_pct: 0.0010
- annual_rainfall_mm: 0.0006
- wasteland_pct: 0.0004

### lasso
- avg_ghi_kwh_m2_day: 0.0088
- population_pressure: 0.0060
- aspect_deg: 0.0050
- elevation_m: 0.0041
- longitude: 0.0032
- population_density_per_sqkm: 0.0022
- builtup_pct: 0.0012
- shrubland_pct: 0.0010
- annual_rainfall_mm: 0.0006
- wasteland_pct: 0.0004
