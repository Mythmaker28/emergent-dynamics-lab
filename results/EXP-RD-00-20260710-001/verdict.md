# EXP-RD-00 — Verdict: OPEN reaction-diffusion substrate QUALIFIED (12/12)

Protocol `docs/experiments/EXP_RD_00_PROTOCOL.md`. RUN-20260710-2330-EXPRD00. Model: claude-opus-4-8 (lock lifted).

## Checks (all PASS)
| check | result |
|---|---|
| openness (material NOT conserved) | total +99.4% from a non-equilibrium uniform state (homogeneous feed active) |
| EXACT closed limit (F=k=0) | U+V conserved, drift **0.0** |
| **HOMOGENEITY NULL** (no imposed pattern) | uniform state stays **exactly** uniform, ptp = **0.0** |
| tracer partition (sum_c CU=U, CV=V) | 0.0 |
| FEED (external-origin) cohort grows | yes (8912 mass of external origin) |
| tracers passive | zeroing cohorts leaves U,V **bit-identical** |
| determinism / nonnegativity | 0.0 / >= 0 |
| reference-path agreement (2 Laplacians) | 0.0 |
| detector/tracker on real dynamics | max track length **77** (spot regime F=0.025, k=0.055) |
| POSITIVE control (dissipative organization) | P=1.0, M_min=0.065, 83 probe rows, production 0.117, activity 0.085 |
| NEGATIVE control (frozen/imposed pattern) | **identical P/M** (P=1.0, M_min=0.065, 83 probes), production **0.000**, activity **0.000** |

## The imposed-pattern question (explicitly answered)
Two independent guards establish that any future "individuality" cannot be a pattern imposed by external forcing:
1. The forcing is spatially homogeneous, and the **homogeneity null proves it**: a uniform state remains EXACTLY
   uniform forever (ptp = 0.0). The forcing cannot imprint spatial structure; every structure is self-organized.
2. The **negative (imposed-pattern) control** is INDISTINGUISHABLE from a real dissipative organization on P/M
   alone — both sit in the probe quadrant. It is separated ONLY by the open-system rates (production/activity).
   Any future candidate must clear this separation, and re-appearance at the OLD site after displacement in the
   causal intervention would mark an externally maintained spatial slot (occupancy alias).

## Fixes made during qualification (before any claim)
(a) Gaussian seeding killed the pattern -> standard square-patch seeding. (b) The openness check originally started
on the fixed point (U+V==1 everywhere), hiding the source/sink -> replaced by a non-equilibrium probe. (c) Cohort
Laplacian vectorized (identical operator).

## VERDICT
**QUALIFIED.** Proceed to preregister and launch **EXP-RD-01**: a BLIND low-discrepancy map over (F, k, Du, Dv),
matched OPEN vs the EXACT CLOSED limit, under the five evidence levels, frozen P/M and thresholds, the
continued-turnover requirement, CONTROL/SHAM/PERTURBED/PLACEBO causal discipline, and observer-sensitivity checks.
