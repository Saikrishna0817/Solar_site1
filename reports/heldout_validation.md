# Held-out plant validation
Model `ridge` · hold-out = 20% of 13 in-scope CEA plants (split seed 42, same as training) · labels are CEA actual MU/MW/8760.
| plant_name | district | state | cuf | model_cuf | model_err | c0_cuf | c0_err |
|---|---|---|---|---|---|---|---|
| Nizamabad Solar | nizamabad | Telangana | 0.1788 | 0.1894 | 0.0105 | 0.1801 | 0.0013 |
| Warangal Solar | warangal | Telangana | 0.1815 | 0.1831 | 0.0016 | 0.1794 | -0.0021 |
| Kurnool Ultra Mega Solar | kurnool | Andhra Pradesh | 0.208 | 0.1899 | -0.0181 | 0.1878 | -0.0202 |
| Metric | Model | C0 physics baseline |
|---|---|---|
| MAE (CUF) | 0.0101 | 0.0079 |
| Bias (pred − actual) | -0.0020 | -0.0070 |

**Verdict:** C0 beats model on this hold-out (3 plants, narrow target range 0.179-0.208).
