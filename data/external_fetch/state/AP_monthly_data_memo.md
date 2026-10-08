# Andhra Pradesh plant-wise monthly generation — search log & RTI path

**Status:** [PENDING RTI] — no free public source found for plant-wise AP monthly
generation as of 2026-10-08. This memo records every source tried so nobody
repeats it, and drafts the RTI ask (Phase 1.6 of the implementation plan).

## What we need (label requirement)

Plant-wise **monthly energy (MWh)** and **installed capacity (MW)** for
Andhra Pradesh solar plants, to form measured CUF = MWh / (MW × hours).
Same bar as TGTRANSCO (Gate 1 of `reports/label_qa.md`).

## Sources tried (free)

| Source | URL | Result | Date |
|---|---|---|---|
| APSLDCL (discom) | `https://apsldc.in` | HTTP 000 / unreachable from this network | 2026-10-08 |
| APTRANSCO | `https://aptransco.com` | HTTP 000 / unreachable | 2026-10-08 |
| NR-EDCAP | `https://nredcap.ap.gov.in` | HTTP 000 / unreachable | 2026-10-08 |
| APSPDCL (discom) | `https://apspdcl.in` | HTTP 200, consumer portal only — no plant-wise generation | 2026-10-08 |
| CEA monthly RE reports | `cea.nic.in` | ✅ state-wise AP solar totals (MU) and ISGS plant rows; **no** non-ISGS AP plant rows | 2026-10-08 |
| CEA IC July 2026 | `data/official/IC_July2026.xlsx` | state-level only: AP grand total 31,114.86 MW / RES(MNRE) 13,385.43 MW (derived: read from sheet, as on 31.07.2026) | 2026-10-08 |
| Wikipedia plant tables | `en.wikipedia.org` | regex parse yielded 0 usable AP plant capacity rows | 2026-10-08 |
| NREL PVWatts / REopt | `developer.nrel.gov` | DNS dead from this network | 2026-10-08 |
| Global Solar Atlas | `globalsolaratlas.info` | HTTP 403 (SPA, no raster) | 2026-10-08 |

Reachability failures are network-side (000), not proof the data is absent —
re-check before filing.

## What we can use meanwhile

- **State-level** AP solar generation: CEA monthly RE `Solar ` sheet
  (state totals, MU/month) → Phase 4 energy-balance check, not plant labels.
- **ISGS plants only**: CEA `ISGS` sheet has 4 AP solar rows
  (Greenko/SAEL×2/Simhadri/Amgreen) for the report month →
  `data/plant_labels/cea_isgs_month_energy.csv`.
- CEA capacity totals: state-level only (see table above).

## RTI ask (draft) [PENDING]

Filed under RTI Act 2005, s.6(1), to **APTRANSCO** (and copy: APSPDCL/APEPDCL
discoms), fee as prescribed:

> Kindly provide, for the period 01-04-2023 to 31-03-2026, month-wise details
> for each solar generating station (MW > 10) in Andhra Pradesh:
> (i) installed capacity (MW), (ii) energy injected / generation (MWh or kWh),
> (iii) station name as in the SLDC/registry. Electronic copy preferred.

Same ask against **TGERC** remains open for plant capacities (Gate 1 open item
in `reports/label_qa.md`).

*Flagged derived figures: none here — this is a source log.*
