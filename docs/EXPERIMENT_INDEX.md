# Experiment Index

| Experiment ID | Status | Substrate/mechanism | Runs | Artefacts | Interpretation |
|---|---|---|---:|---|---|
| HIST-EXP01-9992e6c | AUDITED_NOT_RERUN | Historical Particle Life CORE | 8 archived | local Git object `9992e6c`; historical CSV/results | Code/tests/artefacts independently audited; historical simulation not independently rerun |
| BASELINE-COREV0-20260710-001 | SUPERSEDED_FOR_INTERPRETATION | Pre-repair Particle Dynamics CORE V0 | 36 | `results/BASELINE-COREV0-20260710-001/` | Technical exploratory artefact; original all-green/candidate disposition invalidated by independent numerical/tracker audits |
| HOLDOUT-COREV0-20260710-001 | SUPERSEDED_NOT_RUN | Frozen pre-repair laws 1,3,6,10 | 0 | `docs/experiments/HOLDOUT_COREV0_01_PROTOCOL.md` | Stopped before execution; retained only as historical preregistration |
| BASELINE-COREV0-20260710-002 | COMPLETED_DIAGNOSTIC | Repaired Particle Dynamics CORE V0 | 36 | `results/BASELINE-COREV0-20260710-002/` | Exact-SHA numerical PASS and tracker diagnostic GO; 384 raw probe rows, all retain sparse-alias risk |
| HOLDOUT-COREV0-20260710-002 | INVALIDATED_SELECTION_BUG | Repaired CORE V0 laws 1,3,6,10 | 20 | `results/HOLDOUT-COREV0-20260710-002/` | Preserved; clean-cadence join was applied incorrectly, so no disposition accepted |
| HOLDOUT-COREV0-20260710-003 | COMPLETED_NEGATIVE | Repaired CORE V0 law 3 | 5 | `results/HOLDOUT-COREV0-20260710-003/` | 1/5 fresh seeds qualifies; below frozen 2/5 gate; no probability claim, no perturbation promotion |
| EXP02-COREV0-20260710-001 | COMPLETED_ANALYZED_9_ELIGIBLE | CORE V0 regime map | 900 | `results/EXP02-COREV0-20260710-001/` (raw local/ignored; committed index, analysis, figures) | Integrity PASS; nine laws pass 2/3 screening; direct P/M/edge diagnostics exact but reject zero aliases; hold-out 004 frozen for all nine |
| HOLDOUT-COREV0-20260710-004 | PREREGISTERED | Repaired CORE V0 laws `{0,12,35,52,73,94,209,225,298}` | 0 | `docs/experiments/HOLDOUT_COREV0_04_PROTOCOL.md` | Five unseen seeds `{3001..3005}`; unchanged clean-long/cross-cadence gate; retain only at `>=2/5`, diagnostic alias-unresolved |
| EXP03-A | NOT_STARTED | CORE V0 + density preference | 0 | protocol pending | Only after eligible negative/insufficient EXP02 |
| EXP03-B | NOT_STARTED | CORE V0 + orbital interaction | 0 | protocol pending | Same observables/nulls/sampling philosophy |
| EXP03-C | NOT_STARTED | CORE V0 + density + orbital | 0 | protocol pending | Final Particle Dynamics causal family before substrate decision |
