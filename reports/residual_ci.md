# Phase 3 — residual models over C0 (pre-registered, ALL reported)

n=13 plants / 11 districts · features: avg_ghi_kwh_m2_day, max_temp_c · CV: LOGO · CI: 2000 district bootstraps (seed 42)

| model | LOGO MAE | C0 MAE | Δ (95% CI) | beats C0 point | beats C0 CI95 | conformal90 ± |
|---|---|---|---|---|---|---|
| ridge | 0.00446 | 0.00805 | -0.00359 ([-0.00565, -0.00115]) | True | True | 0.00945 |
| elastic_net | 0.00541 | 0.00805 | -0.00264 ([-0.00556, 0.00141]) | True | False | 0.00987 |

Held-out check (same spec, 20%, seed 42):
| model | heldout MAE | C0 MAE | winner |
|---|---|---|---|
| ridge | 0.0064 | 0.00785 | model |
| elastic_net | 0.00915 | 0.00785 | c0 |

**Gate 3: PASS** -> serving: residual ridge
(prior md parse of the old artifact kept for reference: {'model_mae': 0.0101, 'c0_mae': 0.0079, 'winner': 'c0', 'source': 'reports/heldout_validation.md'})
