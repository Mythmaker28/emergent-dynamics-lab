# LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A — Fission / censoring policy (TASK 1)

*Frozen policy for genuine droplet division and other integrity events during turnover. Data:
`TURNOVER_EVENTS_03A.json`.*

## Event classification (kept separate — no lumping)

The bijective tracker's statuses map to distinct physical events, each counted separately:

| tracker status | physical event | policy |
|---|---|---|
| SPLIT | **genuine fission** (one component → ≥2 comparable daughters) | **censor the trajectory**; world invalid |
| MERGED | fusion / percolation | censor; world invalid (0 observed in DEV) |
| LOST | loss / death / shrink below threshold | censor; world invalid |
| AMBIGUOUS | unresolvable near-tie | censor; world invalid |

DEV counts: **FISSION 3, LOSS/DEATH 1, FEASIBLE 4, INELIGIBLE 2** (of 10). Fission is genuine, not detector flicker:
50001 track-1 61→38+22 cells (overlaps 0.62/0.36); 50009 track-0 105→68+36. Feasibility is therefore a real ~50 %
constraint, and the family is powered accordingly (`TURNOVER_POWER_REPAIR_03A.md`).

## Single-droplet continuity rule (frozen)

- A genuine fission **censors that trajectory** at the fission step. The world is invalid for the individuation
  question (all-three-valid gate).
- **Never silently select one daughter as "the same individual."** No daughter inherits the parent's identity for
  any continuity or reproduction claim.
- Fission events are **preserved as a separate SECONDARY dataset** (`fission_secondary_dataset` in
  `TURNOVER_EVENTS_03A.json`: seed, track, step) for a possible future reproduction/division study — which is
  **out of scope here** (parking lot). **No reproduction, heredity, or division claim** is made from them in this
  mission.
- Censoring is applied identically in DEV and prospectively; no post-hoc adjustment.

## Why this matters

The merge-incident lineage (39/39 → 17 survivors, ×4.8 inflation) shows that silently following a survivor or a
daughter corrupts the readout. The bijective tracker + world-level censorship + this policy prevent survivor-
selection bias (risk R4/R7). Fission attrition is a **fact about the architecture**, reported, not engineered away.
