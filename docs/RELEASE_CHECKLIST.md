# Release checklist

Gate before any Zenodo/GitHub release or manuscript submission. Tick only what is verified.

- [x] **CI present** — `.github/workflows/tests.yml` (pytest on push/PR, Python 3.11, `requirements.txt`).
- [x] **Lockfile done** — `requirements.lock.txt` at repo root (`pip freeze` from `.venv`, 86 pins).
- [x] **Data cards done** — `docs/DATA_CARDS.md` (TGTRANSCO Tr_losses, CEA RE generation ISGS,
      CEA installed capacity; licence = "not stated, treat as public, attribution: TGTRANSCO/CEA").
- [x] **Label provenance** — `data/external_fetch/SOURCES.md` §H (URL pattern + month-naming gotcha),
      raw PDFs + `data/raw/tgtransco/SHA256SUMS`, QA `reports/label_qa.md`.
- [ ] **Zenodo archive** `[PENDING — needs account/DOI]` — deposit code + `data/plant_labels/*.csv`
      + data cards after Gate review; add DOI to README and citation block.
- [x] **Model card pointer** — `reports/ml_report.md` (per-model CV, "Beats C0?" column);
      `models/gate.json` = Gate 3 verdict for the served model (residual ridge: held-out
      0.0064 vs C0 0.00785, LOGO ΔMAE CI [−0.00565, −0.00115], conformal 90 % ±0.00945);
      `reports/heldout_validation.md` keeps the older 43-feature artifact's honest loss.
- [x] **Serving gate wired to Phase 3 results** — `src/api/services/gate.py` reads
      `models/gate.json` (held-out + interval, not just CV MAE); Gate 3 fail ⇒ C0 only;
      `/api/health` exposes `gate3_pass`, `heldout`, `conformal90_halfwidth`, `delta_ci95`.
- [x] **Energy balance done** — `reports/energy_balance.md` (TGTRANSCO vs CEA same-month,
      ratios 0.70–0.79 flagged as scope mismatch; LOGO per-plant errors; PVWatts/SRRA status).
- [x] **Citation block for the eight flaws** — `docs/PAPER.md` §1 table (L1–L8, severity + status)
      and §1.1 additional disclosures; all eight must appear in the manuscript limitations section
      (fix plan hard rule: "All eight documented flaws appear in the limitations section").
- [ ] **AEF run + licence verify** — `docs/aef_setup.md` `[PENDING]` (no GEE creds here); AEF licence
      note `[VERIFY BEFORE PUBLICATION]` before any embedding-derived claim ships.
- [ ] **Scope check** — TG+AP only, every derived figure flagged (`[DERIVED]`/`[ASSUMPTION]`),
      no fabricated numbers, free tools only.
