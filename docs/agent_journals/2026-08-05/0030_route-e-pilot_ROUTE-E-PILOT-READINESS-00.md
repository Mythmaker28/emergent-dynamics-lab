# ROUTE_E_PILOT_READINESS_AND_FEASIBILITY_00 — journal

role: Route E pilot runner · start/end 2026-08-04 → 2026-08-05
starting git state: `eccd46bc2a64e9348f6a41cf6d488d28c3736e81` (A1-R5), tree `886572a1…`
branch: `pilot/route-e-pilot-readiness-00`
scope: owner-authorised minimal closure, then ONE exploratory pilot. No `k`, no 42/9, no A2,
no confirmatory run, no preregistration.

## OBSERVED

- Phase 0 exact. The A1-R5 commit is NOT in the owner's working repository (`git cat-file`
  fails on all three A1 commits there); it lives only in the exported bundles. The full chain
  was therefore reconstructed in a clean clone: clone from `origin`, fetch `199f29eb`, then
  unbundle A1-R3, A1-R4, A1-R5 in order. Commit, parent, tree, both SHA-256 values and
  `git patch-id --stable` all match the announced values exactly.
- Baseline suite in this environment at `eccd46bc`: 1 435 passed / 12 failed / 22 skipped.
  The twelve are 5 declared historical failures plus 7 caused by the absent pinned drand
  verifier (`verify_round` returns `configuration_error` where the tests expect `invalid`).
  Recorded before any change so that regressions could be separated from inheritance.
- The qualified measurement bridge persists ONLY the sampled frames. Between two of them
  sixteen engine steps occur whose gross flows are discarded. Gate G2 is therefore
  unsatisfiable from the bridge's output as designed — a fact about the persistence, not a
  defect of the bridge. A pilot-only transport ledger was added rather than a weaker proof.
- The pilot acquisition's sampled frames are byte-identical to `run_measurement_bridge`'s at
  L = 16, 24 and 32 for the same law, initial state and schedule.
- 48/48 worlds completed, 0 technical incidents, 48/48 engine re-executions byte-identical,
  1 024 transitions recomputed per world with tracer deviation 0 and conservation drift 0.
- 48/48 worlds mechanically ineligible, cause `WRAPPING_COMPONENT_PRESENT` in every case.
  Only 6/48 wrap at the enrolment frame; median first wrapping frame is 16, the first sampled
  frame after t = 0.
- Labelled fraction at enrolment: mean 0.745, range 0.671–0.811. Matter and cohort are both
  exactly conserved, so this ratio is fixed for the whole run.
- `q_min_inventory = 0` for every eligible track at every setting: the thresholds are not made
  unreachable by conservation.
- At threshold 0.60, where 9 worlds are eligible, union residuals are 0.744–0.904 while the
  FOCAL residuals of the same 9 tracks are 0.0, 0.0, 2e-6, 8.4e-5, 0.0018, 0.155, 0.221,
  0.691, 0.733.

## INFERRED

The percolating component is produced by the engine's dynamics, not by the initial-condition
law: 42 of 48 worlds do not wrap at enrolment and all of them wrap later. Changing the IC law
would therefore not repair the eligibility rule.

The union enrolment convention makes the residual track the lattice-wide labelled fraction
rather than the replacement of the focal component. This is consistent with conservation:
under mixing, every local ratio tends to the global one, and the global one is fixed at ~0.74.

## HYPOTHESIS

A component-focal cohort measures the intended quantity and the union cohort does not. The
focal figures above are consistent with that, on the same bytes and the same flows, but they
were computed as a prespecified DIAGNOSTIC at a non-frozen detection threshold and are not a
result about Route E.

## WHAT WOULD FALSIFY THIS?

An engine world in which the union residual falls well below the world's global labelled
fraction would falsify the mixing explanation. None was observed in 48 worlds. A world in
which the focal and union residuals agree would falsify the union/focal claim; the nine
compared tracks all disagree, seven of them by more than 0.5.

## Failures and dead ends

- A search of the engine's law space for a genuine `Y = 1` fixture was deliberately NOT run.
  Whether the engine can produce persistence with replacement is the pilot's scientific
  question; building a gate fixture by selecting such a world would have answered it with a
  chosen example. The `Y = 1` fixture is transport-constructed and declared synthetic instead.
- The first draft of the admission failed an independent review with four executable
  counter-examples, all real: a resealed `mask` channel fabricated `Y = 1` in a world with
  identically zero flows; a single distant `1e11` matter cell inflated a ledger-wide absolute
  tolerance until an erased cohort passed; a blanked mask frame became a NEGATIVE result
  instead of an incident; and `--horizon` was a free knob that moved the outcome. One
  corrective pass closed all four; each is now an armed regression test.
- Three of my own tests were weak and the reviewer was right about all three: one was
  tautological, one was a string search, one exercised a path the admission never takes.

## Decisions

Disposition `PILOT_DESIGN_RISK_OBSERVED`. Two design risks are recorded, both measured. No
`k`, no thresholds, no POSITIVE, no NEGATIVE. `confirmatory_run_authorized = false`.

## Unresolved risks

The three external STOPs remain open and were deferred by explicit owner decision, not closed.
The focal-cohort finding is a diagnostic at a non-frozen threshold; making it primary is a
design decision for the owner, not for this mission.

## Handoff

ONE owner decision, on the two observed design risks, before any preregistration mission.
Nothing else is authorised.
