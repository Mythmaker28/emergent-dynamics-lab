# HISTORICAL CLAUDE 03A POWER NOTE — NON-AUTHORITATIVE

The Beta-Binomial cap repair is retained, but the external `54097-54120` reserve is withdrawn. See the canonical
`TURNOVER_POWER.md` for the reconciled 50+46 family under the hard cap of 96.

# LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A — Power & feasibility repair (TASK 4)

*Corrects the parent's 50-seed / ≥18-valid proposal, which was internally inconsistent under small-sample
uncertainty. Computation in the mission log; DEV inputs from `turnover_dev_raw.json`.*

## The parent proposal was underpowered

DEV: eligibility 8/10, feasibility-of-eligible 4/8 → net valid 4/10. Propagating the small-sample uncertainty with a
**Beta-Binomial** (Jeffreys priors: eligibility Beta(8.5,2.5), feasibility Beta(4.5,4.5)) gives net p/seed mean
**0.387** (5th–95th pct **0.17–0.63** — very wide at this sample size).

`P(N_valid ≥ floor)` under the Beta-Binomial predictive:

| N seeds | E[valid] | P(≥12) | P(≥18) | P(≥24) |
|---|---|---|---|---|
| 50 (parent) | 19.3 | 0.84 | **0.57** | 0.29 |
| 64 | 24.7 | 0.92 | 0.76 | 0.53 |
| 80 | 30.9 | 0.96 | 0.87 | 0.71 |
| **96** | 37.1 | 0.98 | **0.93** | 0.82 |
| 120 | 46.4 | 0.99 | 0.96 | 0.91 |

**The parent's 50 seeds give only P(N_valid≥18) = 0.57 — a coin flip, not the implied ≥90 %.**

## Repair

- **Family cap raised to 96 seeds (`54001–54096`), frozen.** P(N_valid ≥ 18) = **0.93**; P(≥24) = 0.82.
- **Valid-world floor: ≥18** (primary), justified from the graded-decode power (confirmation-01: n=9→0.10, n=18→0.75
  for a *real* effect). **≥24 = "strong" tier** for the ownership + access-structure decode (L/P/E/G), reached with
  P=0.82 at N=96.
- **No outcome-dependent extension.** If < 18 valid at cap 96 → Outcome **E** (feasibility failure), no verdict.
- **Sealed reserve (optional, pre-declared):** an eligibility-only reserve `54097–54120` may be activated **only** if
  the *geometric eligibility* (a pre-outcome quantity) falls below a frozen threshold during the run, with a hard cap
  of 120 total and no reference to any outcome. If used, it is declared before execution.

## Power of the primary gates at ≥18–24 valid

- **G3-OWNERSHIP / ACCESS** (the real question): needs ≥18 valid for a *real* graded effect, ≥24 for the 4-way
  L/P/E/G comparison. This is the binding constraint and is **at genuine risk of a null** (DEV: homogenization,
  ownership unresolved). A well-powered null is a valid Outcome B/D.
- **G4 interventional** (secondary): over-powered at n≥6 — but gated by its algebraic-prediction null D, so a pass
  there is not independent evidence.

## Cost

Per seed ≈ 35 s (early-censor) to 70 s (feasible + assay). **N=96 ≈ 83 min** single-core on the pinned venv,
checkpointed/batchable. (Optional reserve to 120 ≈ 104 min.)

## Every proposed seed unused

`54001–54096` verified **absent** from all 18 branches (only byte-counts / decimals match `\b54[0-9]{3}\b`; no seed
family). Outcomes are **not** inspected (none run).
