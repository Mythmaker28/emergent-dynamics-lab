# EXP-RD-02 — Decision: NEGATIVE. No audited individuality survives the frozen chain.

Protocol frozen in `docs/experiments/EXP_RD_01_PROTOCOL.md` @b3badb8. RUN-20260711-0000-EXPRD02.
Laws {1,5,7,10,11,13,14,16,19} FROZEN; never ranked, replaced or visually selected. Thresholds, tracer, P/M and
mechanism unchanged throughout.

## EXPLICIT DENOMINATORS
Causal post-intervention window = 750 steps at the frozen cadence 50 -> **N_POST = 15 post snapshots**; every
"frac_organized" is out of 15. Sensitivity denominators stated per setting: cadence 25 -> 30; cadence 100 -> 8.
Hold-out denominator = 5 unseen seeds per law. Causal denominator = 10 unseen seeds per law.

## LEVEL 3 — FRESH-SEED HOLD-OUT (frozen >=2/5, unseen seeds 11001-11005)
**9/9 laws SURVIVE** (laws 5,7,10,11,14,16,19 at 5/5; law 1 at 3/5; law 13 at 2/5). 0 rejected. Recurrence is real.

## LEVEL 4 — DIRECT ALIAS AUDIT
Dissolution/reformation: **0/8**. Stationary (occupancy-suspect, net displacement < 3 cells): **laws 5, 11, 14**.
Law 11 shows heavy fragmentation/tracker churn (27 splits, 20 ambiguous, 16.5 entities/snapshot). Law 13 has NO
eligible clean-long probe-positive track on the audit seeds. These are resolvable only causally.

## LEVEL 5 — SAME-STATE CAUSAL INTERVENTION (9 laws x 10 UNSEEN causal seeds = 90 units)
CONTROL / SHAM / PERTURBED / PLACEBO from an identical pre-intervention state. **SHAM == CONTROL bit-for-bit in
every enrolled unit.** Audited requires: re-establishment at the new site, exceeding PLACEBO by 0.25, no old-site
regeneration, AND **continued temporal-cohort turnover after recovery** (no frozen lumps).

| law | seeds | enrolled | censored | AUDITED | frozen_lump | placebo_fail | occupancy | destroyed | audited/enrolled [Wilson 95% CI] |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 10 | 10 | 0 | 1 | 0 | 0 | 0 | 9 | 0.100 [0.018, 0.404] |
| 5 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0.000 [0.000, 0.278] |
| 7 | 10 | 10 | 0 | 1 | 0 | 0 | 0 | 9 | 0.100 [0.018, 0.404] |
| 10 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0.000 [0.000, 0.278] |
| 11 | 10 | 10 | 0 | 1 | 0 | 6 | 3 | 0 | 0.100 [0.018, 0.404] |
| 13 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0.000 [0.000, 0.278] |
| 14 | 10 | 10 | 0 | 3 | 0 | 0 | 0 | 7 | 0.300 [0.108, 0.603] |
| 16 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0.000 [0.000, 0.278] |
| 19 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0.000 [0.000, 0.278] |
**POOLED: enrolled 90, censored 0, AUDITED 6/90 = 0.067 [0.031, 0.138].**
Failure modes: **destroyed 75/90 (83%)**, placebo_failure 6, occupancy_alias 3, frozen_lump 0.

## OBSERVER SENSITIVITY (preregistered, applied to EVERY apparent success)
**0/6 survive.** All six fail cadence perturbation (25 and/or 100); all six survive both tracker perturbations
(x0.8, x1.2). Per the frozen rule, an audited success that fails the sensitivity check is an observer artefact and
is WITHDRAWN.

## NET RESULT: **0 audited successes survive the full frozen chain.**

## Why it failed
Displacing an open reaction-diffusion dissipative structure off its site **destroys it in 83% of units**: the
organization is maintained by its LOCATION in the chemical field, not carried by its material. Where it does
survive, the signal is placebo-explained, occupancy-aliased, or observer-fragile. Notably **frozen_lump = 0** --
the Flow-Lenia failure mode did not recur, because in this open substrate the structures simply do not survive
displacement at all.

## HONEST CAVEAT ON MY OWN METHOD (flagged, not exploited)
My cadence perturbation also shifts the ENROLLMENT time (t* = WARMUP_SNAP * cadence), so it conflates an observer
change with an enrollment change. All 6 units survive the PURE tracker perturbations. This is a weakness in my
sensitivity design and the correct remedy is a future pre-declared sensitivity that perturbs the observer WITHOUT
moving the enrollment point. **It does not rescue this result:** the 6/90 base rate [3.1%, 13.8%], the 83%
destruction rate, and the placebo/occupancy failures already fail to support any claim.

## DECISION
**EXP-RD-02 NEGATIVE.** Nothing is promoted. The open Gray-Scott substrate reaches the continued-turnover regime
and shows robust screening recurrence (9/9 hold-out), but no constituent-carried, continued-turnover individuality
survives the causal intervention and observer sensitivity. Levels 3 and 5 are demonstrably different levels.
No thresholds, composites, mechanisms or laws were changed.
