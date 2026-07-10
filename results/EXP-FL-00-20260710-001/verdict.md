# EXP-FL-00 — Verdict: Flow-Lenia field stack QUALIFIED

Protocol @817d417. RUN-20260710-2030-EXPFL00. Model: claude-opus-4-8 (Fable 5 lock lifted by the user).

## Checks (all PASS)
- mass_conservation (rel drift < 1e-9; measured ~1.6e-16), nonnegativity, cohort_partition_preserved (~4.5e-15),
  determinism (exact), passive_tracer_invariance (A identical with/without cohorts, exact),
  reference_path_agreement (FFT vs direct potential ~1.6e-15), detector_tracker_on_real_dynamics (track len >= 3),
  expref01_recognized, expref01_separated.

## EXP-REF-01 on the field stack
Reference (rotating blob + cohort turnover): single continuous track, P=1.0, M_min=0.067 (turnover),
probe-positive; |circulation|=0.99, velocity dispersion=1.22. Static-flux field null: identical P/M but
|circulation|=0, velocity dispersion=0. RECOGNIZED and SEPARATED (P not recalibrated).

## VERDICT
**QUALIFIED** -> preregister and launch EXP_FL_01 as a blind low-discrepancy Flow-Lenia regime map under the same
five evidence levels (distributional shift / screening signal / fresh-seed recurrence / alias rejection / causal
re-establishment) and causal discipline. No composite score; thresholds frozen; P/M separate; same-state causal
intervention carried over. Scope caveat: separation is vs the zero-velocity static-flux null; the flowing-occupancy
alias is resolved only by the same-state causal intervention.
