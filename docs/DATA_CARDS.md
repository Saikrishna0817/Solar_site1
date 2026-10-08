# Data cards

Three primary-source cards, one block each. Fields: name · provider · URL · access date · licence ·
grain · known caveat · used-for. Licence text below is boilerplate where no licence is stated —
**do not invent finer print**.

## a. TGTRANSCO monthly Tr_losses PDFs

- **Name:** TGTRANSCO monthly transmission-loss reports (`Tr_losses_<Mon>-<YYYY>.pdf`)
- **Provider:** Telangana State Power Transmission Corporation Ltd (TGTRANSCO)
- **URL:** `https://www.tgtransco.com/user_uploads/trans_losses/Tr_losses_<Mon>-<YYYY>.pdf`
  (per-month variants; month token is not normalised — see SOURCES.md §H)
- **Accessed:** 2026-10-08 — 29 PDFs local in `data/raw/tgtransco/`, hashes in `SHA256SUMS`
- **Licence:** Indian govt publication; licence not stated (treat as public, attribution: TGTRANSCO)
- **Grain:** monthly PDF; generator/feeders × 132/220 kV injection point, net energy in MU (Mar-2021 … Nov-2025, gapped)
- **Known caveat:** net energy at injection point (not gross) → CUF biased low; capacity unpublished
  (only 3 plants reach a 12-month window); solar split = name keyword
- **Used-for:** label factory → `data/plant_labels/plant_month_energy.csv` (2321 rows, 65 solar names),
  `plant_registry.csv`, `plant_capacity.csv`, `plant_cuf.csv`; QA `reports/label_qa.md`

## b. CEA monthly RE generation report — ISGS sheet

- **Name:** CEA Monthly Renewable Energy Generation Report, July 2026 — sheet `ISGS`
- **Provider:** Central Electricity Authority (India), Renewable Energy Project Monitoring Division
- **URL:** `https://cea.nic.in/renewable-generation-report/?lang=en` →
  `https://cea.nic.in/wp-content/uploads/resd/<path>/RE_Monthly_Generation_report_July_2026.xlsx`
- **Accessed:** 2026-10-08 (repo copy `data/official/RE_Monthly_Generation_report_July_2026.xlsx`;
  download logged 2026-07 in `docs/PAPER.md` §2.1)
- **Licence:** Indian govt publication; licence not stated (treat as public, attribution: CEA)
- **Grain:** month, station × state/region × sector (Central/State/Private) × type, Actual Generation (MU)
- **Known caveat:** single-month snapshot; ISGS stations only (state-wise and source-wise are other
  sheets); no installed MW in the sheet → any CUF needs a separate capacity join
- **Used-for:** state-wise RE generation cross-checks; `CUF = MU × 1000 / (MW × 8760)` (PAPER §2.1)

## c. CEA installed capacity (IC_July2026.xlsx)

- **Name:** CEA Installed Capacity (MW) of Power Stations, as on 31.07.2026 (utilities, incl. allocated shares)
- **Provider:** Central Electricity Authority (India)
- **URL:** `https://cea.nic.in/installed-capacity-report?lang=en` →
  `https://cea.nic.in/wp-content/uploads/installed/2026/07/<file>.xlsx` (link discovered by
  `scripts/fetch_official_data.py`)
- **Accessed:** 2026-10-08 (repo copy `data/official/IC_July2026.xlsx`; download logged 2026-07 in PAPER §2.1)
- **Licence:** Indian govt publication; licence not stated (treat as public, attribution: CEA)
- **Grain:** all-India table — region × ownership/sector × fuel, MW, as on 31.07.2026 (sheet `IC_July 2026`)
- **Known caveat:** utility installed capacity only; as-on date (Jul-2026) does not match the
  2023-24 label window — disclose the offset whenever capacity and labels are combined
- **Used-for:** coal-to-solar scenario inputs (PAPER §4: AP row 169, TG row 173)

## d. CEA CO2 Baseline Database v20.0

- **File:** `data/official/CO2_Database_Version_20.0_2023_24.xlsx`
  (sha256 `3bebd8e5…` in `data/official/SHA256SUMS`)
- **Source:** Central Electricity Authority — CO2 Baseline Database for the Power Sector,
  Version 20.0, data year 2023-24, dated 2024-12-01; methodology = UNFCCC CCM "Tool to
  Calculate the Emission Factor for an Electricity System" v7.0.
  Access: https://cea.nic.in/cdm-co2-baseline-database/ (open; licence not stated —
  treat as Indian govt publication with attribution: CEA).
- **Grain / vintage:** all-India grid emission factors incl. imports, annual 2019-20…2023-24.
- **Fields used:** `Results` sheet — Simple Operating Margin **0.9615**, Combined Margin
  **0.7568**, Weighted Average **0.7275** tCO2/MWh (2023-24). `[OFFICIAL]`
- **Used-for:** coal-to-solar scenario CO₂ avoided (PAPER §4 EF band 0.7568–0.9615).

## e. CEA daily RE generation report (State-Wise)

- **Files:** `data/official/Report-2024-06-30.xlsx`, `Report-2024-07-31.xlsx`,
  `Report-2025-11-30.xlsx` (+ `SHA256SUMS`).
- **Source:** CEA Renewable Energy Monitoring Division, daily report; the last-day file's
  `State-Wise` sheet carries "Cumulative Generation during <month>" per state (MU).
  Access: https://gen-re.cea.gov.in/reports (open; archive starts 2024-06-30).
- **Used-for:** Phase 4 same-month energy balance vs TGTRANSCO plant sums
  (`reports/energy_balance.md`) — measured ratios 0.70–0.79 flagged as scope mismatch
  (EBC tables list a subset of state solar).
