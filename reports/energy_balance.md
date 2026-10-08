# Phase 4 — energy balance, per-plant error, blocked cross-checks

## 4.1 Energy balance: TGTRANSCO plant sum vs CEA state total (same month)

| month | TGTRANSCO solar (MU) | CEA Telangana solar (MU) | ratio | within ±10% | CEA AP solar (MU) |
|---|---|---|---|---|---|
| 2024-06 | 366.56 | 513.64 | 0.714 | False | 329.36 |
| 2024-07 | 310.77 | 391.42 | 0.794 | False | 300.79 |
| 2025-11 | 374.27 | 534.92 | 0.7 | False | 403.69 |

Sources: CEA daily RE report (State-Wise sheet, cumulative column) — same-official-source check.

**Finding (flagged): all three ratios are outside ±10% (0.70-0.79).** The consistent shortfall means the TGTRANSCO EBC tables do NOT cover all Telangana solar — only the plants listed in the transmission-loss tables (~70-80% of the CEA state-control total). Scope mismatch, not an energy error: CEA state-control area includes open-access/private plants absent from the EBC listing. Interpretation [REVIEW]: treat TGTRANSCO labels as representative of the listed subset, not the state.

## 4.2 Per-plant error (measured label CUF, n=13, LOGO out-of-fold)

| model | MAE (CUF) |
|---|---|
| residual ridge (+C0) | 0.00446 |
| C0 physics alone | 0.00805 |

Full table: `data/plant_labels/plant_error_table.csv` (every figure measured or model-derived; no clamping).

## 4.3 Cross-check status

- **NREL PVWatts V8**: `developer.nrel.gov` DNS-dead from this environment — offline pvlib chain NOT cross-checked. [BLOCKED — rerun `pvwatts/v8.json` compare when reachable]
- **Global Solar Atlas**: HTTP 403 (SPA, no raster) [BLOCKED]
- **SRRA station holdouts**: no free station-level data found; holdout labels remain TGTRANSCO/CEA only [PENDING — RTI/next data drop]
- Flagged derived figures: all MAEs/ratios above are computed from the cited official files.
