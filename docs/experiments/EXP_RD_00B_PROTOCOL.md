# EXP-RD-00B — Frozen Protocol: temporal feed cohorts (pulse-chase) tracer qualification

Status: **FROZEN.** Preregistered by `RUN-20260710-2345-EXPRD00B`. Corrects a real flaw in EXP-RD-00's tracer.
No law search until this passes.

## THE FLAW BEING FIXED
A single permanent FEED cohort can detect the INITIAL replacement of material by external matter, but once
feed-origin mass DOMINATES a structure its cohort composition stops changing, so **continued turnover becomes
invisible** (M -> 1 while material is still being replaced). The tracer saturates exactly where continued turnover
matters.

## THE FIX — ROTATING TEMPORAL FEED COHORTS (pulse-chase)
Cohorts = `n_spatial` initial-origin spatial cohorts + `n_temporal` ROTATING TEMPORAL FEED cohorts.
- New feed mass enters the **currently active temporal cohort**: index `n_spatial + ((step // tau_feed) % n_temporal)`.
- The **reaction transfer U -> V carries the source species' LOCAL cohort proportions** (unchanged).
- **Homogeneous removal scales every cohort equally**, i.e. removes the LOCAL cohort proportions (unchanged).
- Cohorts remain **strictly passive**: they never enter U, V, or any rate (verified: zeroing them leaves U and V
  bit-identical). Partitions hold exactly: sum_c CU = U, sum_c CV = V.

## VALIDATION CONTROLS (pre-declared)
- **C1 CONTINUOUS THROUGHPUT:** open Gray-Scott throughout. The structure keeps replacing its material, so the
  tracer MUST keep reporting turnover in the LATE window: `median_late_M(C1) < 0.5` (the frozen probe threshold).
- **C2 ONE-TIME REPLACEMENT, THEN NO FURTHER TURNOVER:** open for a phase (external matter replaces the original),
  then switch to the EXACT CLOSED limit (F=k=0: no feed, no removal). The tracer MUST report (near-)no continued
  turnover: `median_late_M(C2) ~ 1`.
- **DISCRIMINATION:** `median_late_M(C2) - median_late_M(C1) > 0.30`.
- **LEGACY CHECK:** the single permanent FEED cohort must FAIL these (demonstrating the flaw was real).

## TEMPORAL RESOLUTION SELECTION (measurement-discrimination ONLY)
Candidates (tau_feed, n_temporal) with cycle ~= the observation window. **Select the COARSEST tau_feed that is
adequate**, where adequate := `median_late_M(C1) < 0.5` AND `discrimination > 0.30`. The selection uses ONLY the
two controls; it NEVER uses candidate yield, target-quadrant occupancy, or any screening outcome.

## RESULT (this run)
| tracer | C1 late-M | C2 late-M | discrimination | adequate |
|---|---|---|---|---|
| legacy single permanent FEED cohort | **0.936** (saturated/blind) | 1.000 | **0.064** | **FAILS** |
| tau=500, T=4 | 0.851 | 1.000 | 0.149 | no |
| **tau=250, T=8** | **0.109** | 1.000 | **0.891** | **YES -> SELECTED (coarsest adequate)** |
| tau=125, T=16 | 0.032 | 1.000 | 0.968 | yes |
| tau=62, T=32 | 0.011 | 1.000 | 0.989 | yes |
In every case the structure ends 100% feed-origin -- the saturation regime in which the legacy tracer is blind.

## DECISION
PASS -> the qualified tracer is `TracerSpec(n_spatial=8, n_temporal=8, tau_feed=250)`. Freeze it and launch
EXP-RD-01 exactly as planned (blind matched OPEN vs exact CLOSED Gray-Scott map, frozen P/M thresholds, no
composite score; then fresh-seed hold-out -> alias audit -> causal intervention with the continued-turnover
requirement -> observer sensitivity, for any survivor).
