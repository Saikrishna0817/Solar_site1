# Label QA — TGTRANSCO label factory (Phase 1)

Raw PDFs: 29 months, SHA-256 in `data/raw/tgtransco/SHA256SUMS`.
Long table: 2321 rows (65 distinct names, 65 solar-keyword rows).
12-month windows present: 2023-01..2023-12, 2023-08..2024-07.

## Gate 1 decision (recorded, user unavailable)
- Acceptance was "40 plants with valid 12-month CUF, or explicit decision to proceed with fewer".
- Plants with capacity + full window: **3** — decision: **proceed with fewer**.
- Gap cause: TGTRANSCO publishes name+MU only; capacity needs TGERC/PPA/RTI (plan §2.1 rules).
- Next capacity sources: TGERC PPA orders, MNRE plant list, RTI to TSPCL/NREDCAP.

## Coverage vs archive
| Gap | Months |
|---|---|
| 2021 | Mar only |
| 2022 | Jan, Mar, Sep missing |
| 2024 | Aug-Dec missing |
| 2025-26 | Nov 2025 only |

## Cross-checks & flags
- Net energy at injection point (not gross) — per TGTRANSCO header, CUF biased low (disclosed).
- CUF outliers beyond [0.10, 0.30]: listed below.
- Solar classification = name keyword (solar/sun/pv/acme/azure) across sections; wind/MSW/sugar rows excluded.


## CUF windows produced
| plant_name | district | state | window | months | installed_capacity_mw | total_mu | cuf | cuf_source | capacity_source | source |
|---|---|---|---|---|---|---|---|---|---|---|
| 132kv SCCL 30MW Solar Plant (Manuguru) | Bhadradri Kothagudem | Telangana | 2023-01..2023-12 | 12 | 30.0 | 42.45 | 0.16152968036529677 | official_monthly | name-embedded MW in TGTRANSCO table | TGTRANSCO Tr_losses monthly PDFs |
| 132kv SCCL 30MW Solar Plant (Manuguru) | Bhadradri Kothagudem | Telangana | 2023-08..2024-07 | 12 | 30.0 | 41.68 | 0.15816636308439586 | official_monthly | name-embedded MW in TGTRANSCO table | TGTRANSCO Tr_losses monthly PDFs |
| 132kv SCCL 37 MW Solar Plant (Sitharampatnam) | unknown | Telangana | 2023-01..2023-12 | 12 | 37.0 | 60.37 | 0.18625817598420338 | official_monthly | name-embedded MW in TGTRANSCO table | TGTRANSCO Tr_losses monthly PDFs |
| 132kv SCCL 37 MW Solar Plant (Sitharampatnam) | unknown | Telangana | 2023-08..2024-07 | 12 | 37.0 | 60.86 | 0.18725692906020772 | official_monthly | name-embedded MW in TGTRANSCO table | TGTRANSCO Tr_losses monthly PDFs |
| NTPC Solar power plant (10MW) | unknown | Telangana | 2023-01..2023-12 | 12 | 10.0 | 10.68 | 0.12191780821917808 | official_monthly | name-embedded MW in TGTRANSCO table | TGTRANSCO Tr_losses monthly PDFs |
| NTPC Solar power plant (10MW) | unknown | Telangana | 2023-08..2024-07 | 12 | 10.0 | 9.41 | 0.10712659380692167 | official_monthly | name-embedded MW in TGTRANSCO table | TGTRANSCO Tr_losses monthly PDFs |

## CEA ISGS monthly energy (Phase 1.7)

- Source: `RE_Monthly_Generation_report_July_2026.xlsx` sheet `ISGS`, month `2026-07`.
- Rows: 7 TG/AP solar ISGS plants -> `data/plant_labels/cea_isgs_month_energy.csv`.
- CAVEAT: ISGS subset only (central/state/private ISGS), not all TG/AP plants; one month on hand — a 12-mo CUF window needs 12 monthly CEA reports.
- CAVEAT: station names differ from the TGERC register (`Ntpc_Ramagundam_Fsp` ~ `Ramangundam Solar`); matches flagged in `alias_of`, never silently merged.
