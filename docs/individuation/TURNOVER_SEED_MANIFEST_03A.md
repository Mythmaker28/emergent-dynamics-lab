# HISTORICAL CLAUDE 03A SEED PLAN — NON-AUTHORITATIVE

Superseded by `TURNOVER_SEED_MANIFEST.md`. The authoritative family is 50 primary seeds (`54001-54050`) plus 46
feasibility-reserve seeds (`54051-54096`) under one total hard cap of 96.

# LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A — Corrected seed manifest (NOT opened)

## DEV seeds (this + parent mission)

`50001–50010`. Feasible: 50002, 50004, 50005, 50007. Fission: 50001, 50006, 50009. Loss/death: 50003. Ineligible:
50008, 50010. Raw: `turnover_dev_raw.json`; diagnostics raw: `turnover_dev_diagnostics_raw.json`. Diagnostic re-reads
of 51xxx/52xxx/53xxx permitted for context, never for parameter selection; not re-run.

## PROPOSED confirmatory family — `54001–54096` (NOT OPENED)

- **96 seeds, cap 96, frozen** (raised from the parent's 50 after the Beta-Binomial power repair). Gives
  **P(N_valid ≥ 18) = 0.93**, P(≥24) = 0.82 (`TURNOVER_POWER_REPAIR_03A.md`).
- **Optional sealed reserve `54097–54120`** — activated only on a pre-outcome geometric-eligibility trigger, hard cap
  120, declared before execution, no outcome reference.
- **Registry check — ABSENT.** `git grep '\b54[0-9]{3}\b'` across all 18 branches returns only byte-counts and
  decimal fractions; no seed-family definition. Used families: 30/31/32/33/50/51/52/53xxx. `54xxx` is fresh.
- **NOT opened by this mission.** No 54xxx seed is run; no outcome is inspected. Opening requires Tommy's explicit
  authorization after review of this corrected PRESEAL candidate.
