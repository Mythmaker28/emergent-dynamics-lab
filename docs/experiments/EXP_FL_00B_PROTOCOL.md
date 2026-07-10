# EXP_FL_00B — Frozen Protocol: passive-tracer (cohort) resolution sensitivity check

Status: **FROZEN before measuring.** Preregistered by `RUN-20260710-2115-EXPFL00B`. Methodological correction
required before EXP_FL_01 map #2: verify the cohort resolution is adequate by a principled criterion rather than
lowering M reactively after a negative map.

## QUESTION
Is the 8-cohort field M under-resolving constituent turnover (biasing the map #1 negative), and what cohort
resolution should EXP_FL_01 map #2 use -- selected by a measurement-resolution criterion only?

## PROCEDURE
For granularities G in {8,16,32} (plus a G=64 convergence probe): (1) measure M_min on the VALIDATED turnover
reference (the EXP-REF-01 rotating-blob-with-turnover field, with G cohorts); (2) measure mean/min field M on
representative static Flow-Lenia regimes (blind map-#1 laws {0,6,12,18}, deterministic, NOT chosen by result);
(3) verify DYNAMICS IDENTICAL across G: the mass field A must be bit-identical for G=8 vs G=32 (cohorts passive).

## PRE-DECLARED SELECTION CRITERION (measurement-resolution only; NOT yield)
Select G* = the COARSEST granularity in {8,16,32} that (a) resolves the reference's known turnover:
M_min_ref(G) <= 0.15, and (b) is convergent: |M_min_ref(G) - M_min_ref(next finer)| <= 0.10. The reference has
genuine near-complete turnover, so an adequate tracer registers M_min <= 0.15; the coarsest adequate, convergent
resolution minimizes discretization risk. Static-regime M is reported ONLY as a specificity diagnostic (a large
drop under finer tracers would indicate spurious discretization turnover, reinforcing the coarser choice); it is
NEVER used for selection, and neither is target-quadrant occupancy or candidate yield.

## FALSIFIERS / GUARDS
- If dynamics differ across G (A not identical) -> cohorts are not passive -> STOP (would invalidate the substrate).
- If no G in {8,16,32} resolves the reference turnover (all M_min_ref > 0.15) -> the tracer is under-resolving ->
  select the finest (32) and note the limitation; this is the only case where a finer resolution is adopted, and
  it is driven by reference sensitivity, not by candidate yield.

## OUTPUT / DECISION
Report M_min_ref(G), static M(G), the passive-invariance check, and the selected G*. EXP_FL_01 map #2 uses G*.
