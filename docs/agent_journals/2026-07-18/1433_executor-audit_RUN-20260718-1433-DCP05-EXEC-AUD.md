# Agent journal — DIRECTED-CAUSAL-PAIR-00 Phase 0.5 executor audit

- Role: independent outcome-blind executor/mechanics integration auditor
- Run ID: `RUN-20260718-1433-DCP05-EXEC-AUD`
- Start time: 2026-07-18 14:33 CEST
- End time: 2026-07-18 14:42 CEST
- Starting Git state: clean branch `codex/directed-causal-pair-00-phase05` at
  `898b4595dec15e7d5277058d41697a618405bb99` when the audit began
- Ending Git state: HEAD unchanged at `898b4595dec15e7d5277058d41697a618405bb99`; shared worktree contains this
  agent's executor/mechanics edits and journal plus concurrent integrator changes to the runner, reproducer, schema,
  tests, and a separate recovery journal. This agent did not commit, stage, push, or touch those concurrent files.
- Worktree: `C:\Users\tommy\Documents\ising-v3-directed-causal-pair-00-phase0`
- Runtime lock: not applicable; this is a direct human-requested synthetic/read-only audit and no DEV world is
  initialized or executed

## Assigned scope

Independently audit only the inherited Phase-0.5 executor/mechanics integration against D-091, the Phase-0 report,
and the draft preregistration. Focus on passive per-step geometry, `H00/H10/H01/H11`, H00-derived common deep time,
tracker/halo/fusion/switch gates, role-specific own/reference no-swap, `up_ref=0`, combined isolation, viability-only
probe execution, and zero feeding-outcome inspection. Patch only the executor/mechanics for concrete defects; do
not initialize a DEV world, inspect a prospective/58xxx artefact, commit, push, or edit project indexes.

## Operating-contract and provenance review

Read in the required order:

1. `AGENTS.md`;
2. `docs/RESEARCH_CHARTER.md`;
3. `docs/PROJECT_STATE.md`;
4. all of `docs/DECISION_LOG.md`, including D-091;
5. `docs/EXPERIMENT_INDEX.md`;
6. `docs/RUN_INDEX.md`;
7. latest journal at audit start,
   `docs/agent_journals/2026-07-18/0345_mechanics-tests_RUN-20260718-0345-DCP05-TEST.md`;
8. `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json` and the Phase-0 report.

Also read the complete Phase-0 report and preregistration draft, the inherited executor/mechanics, the accepted
tracker, no-swap/state operators, scaffold detector, material tracer, and the earlier API/mechanics journal. No
result directory, DEV state, prospective namespace, or `58xxx` artefact was enumerated or opened.

## Files changed by this agent

- `experiments/individuation/directed_causal_pair_phase05_executor.py`
- `experiments/individuation/directed_causal_pair_phase05_mechanics.py`
- this unique journal

## Concrete defects found and repaired

1. **Outcome firewall violation by incidental computation.** `_detect_masks`, prewriter target selection, and H00
   reference selection called `scaffold.observables.detect`, which computes per-entity `specific_uptake` on every
   call even when discarded. Replaced it with a geometry-only adapter using the exact accepted rho threshold,
   periodic four-neighbour labelling, minimum cell count, rho-weighted circular centroid, and Rg. The executor now
   never reads the uptake array through detection.
2. **Executor could not start.** All three `seed_snapshot` calls omitted the required `component_masks` argument,
   causing an immediate `TypeError` at writer/access entry. Every seed snapshot now receives the outcome-free
   detected component masks.
3. **Wrong per-step geometry convention.** Pair, track, collar, and persisted core/halo centers were derived from
   binary masks while the frozen detector and Phase-0 assignment use rho-weighted circular centroids. Added an
   optional validated weight field to `periodic_centroid` and applied the rho-weighted convention consistently to
   current components/tracks, pair distance, core/halo masks, collar diagnostics, arm collars, and H00 reference
   centers. The 24-cell distance threshold was not changed.
4. **H00 reference was not role-specific.** One arbitrary median-sized H00 component supplied both A and B
   reference clamps. `_run_access_set` now receives the tracked H00 masks and uses H00-A for recipient A and H00-B
   for recipient B, preserving the frozen orientation and pair context.
5. **Sentinel switch escaped the gate.** `component_switch` compared only A against B. It now compares each of the
   three assigned tracks against every other prior essential track, so an A/B-to-sentinel switch is fail-closed.
6. **Initial clamp geometry was unchecked.** Clamped `PROBE_STANDARDIZE` seed records now include the fixed collar
   and recipient, so recipient/partner/sentinel collar/core intrusions fail before the first scheduled step.
7. **Tracker time reset across stages.** Stage-local counters were passed to `BijectiveTracker.update`, so event
   times could move backward at writer/settle/turnover/probe boundaries. Tracker lifecycle now uses monotonic
   `state.step`; `stage_step` remains separately persisted.
8. **Vacuous isolation pass.** Bit-exact isolation could pass after the far-environment perturbation vanished. The
   mechanical pass now additionally requires a nonzero terminal far-field difference.

No physics equation, writer bit, threshold, arm, schedule, outcome, state field, detector threshold, tracker
association rule, probe constant, or prospective identifier was changed.

## Reproducible synthetic/read-only validation

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m pytest -q -p no:cacheprovider `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py `
  experiments/individuation/test_access_structure_operators.py
# 52 passed in 1.29s (44 focused Phase-0.5 tests + 8 synthetic state/operator tests)

& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' `
  experiments/individuation/test_bijective_tracker.py
# 10/10 checks PASS

& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -c `
  "import ast,pathlib; files=('experiments/individuation/directed_causal_pair_phase05_executor.py','experiments/individuation/directed_causal_pair_phase05_mechanics.py'); [ast.parse(pathlib.Path(p).read_text(encoding='utf-8'), filename=p) for p in files]; print('AST_PARSE_PASS')"
# AST_PARSE_PASS

git diff --check -- `
  experiments/individuation/directed_causal_pair_phase05_executor.py `
  experiments/individuation/directed_causal_pair_phase05_mechanics.py `
  docs/agent_journals/2026-07-18/1433_executor-audit_RUN-20260718-1433-DCP05-EXEC-AUD.md
# PASS
```

An additional synthetic state exposed an `uptake` property that raises on access; `_geometry_entities` and
`_detect_masks` completed, and their weighted centroid agreed with the accepted `circular_centroid` to `1e-12`:
`OUTCOME_FREE_WEIGHTED_DETECTOR_PASS`.

The first focused baseline during concurrent integration was 37 pass / 2 fail because newly added clean-checkout
preflight ran before the exact-binding-set assertion in two tests. The integrator corrected that runner/test-order
issue outside this scope; the final focused run above is 44/44. A combined pytest invocation including the legacy
script-style tracker test produced a pytest collection `SystemExit` after its own 10/10 PASS; rerunning the tracker
as its intended standalone script produced the clean result above.

## OBSERVED

- D-091's four fixed worlds, arm bits, common H00 deep-time rule, 80-step corrected probe schedule, and frozen
  tracker thresholds remain unchanged in the executor.
- The logger hashes the complete persistent state (including the engine-produced uptake field) only for mechanical
  state identity/finiteness; it no longer calculates or extracts any target feeding response.
- H00 alone discovers the deep turnover step; H10/H01/H11 stop at that same step and must satisfy the material gate
  there. No arm chooses its own convenient endpoint.
- Own replay compares every full-state hash with ordinary; `up_ref=0` is a distinct free regime; ordinary and
  `up_ref=0` H00 sources are recorded separately for role-matched reference clamps.
- The engine-free reproducer still needs its concurrent rho-centroid reconciliation: before handoff it recomputed
  centroids from binary masks and derived switches only across A/B, which would reject the corrected raw or miss a
  sentinel switch. This was reported to the integrator and preflight auditor as a pre-execution package dependency.

## INFERRED

- The repaired executor/mechanics now implement the intended outcome-blind physical contract: cadence-1 geometry,
  exact factorial scheduling, H00-fixed deep time, three-track fail-closed identity, history-bearing pair context,
  role-specific reference replay, schedule-only viability, and live nonvacuous isolation.
- A full DEV run remains scientifically unauthorized until the standard-library reproducer/schema accept exactly
  the same rho-weighted primitives and the final manifest is regenerated against all changed blobs.

## HYPOTHESIS

If the final raw validator consumes the persisted rho-weighted centroids as bound physical primitives (or persists
sufficient rho moments), and the exact preflight/code hashes are regenerated, then the four-world mechanical run
can decide only pair mechanics without exposing Y/C/I.

## WHAT WOULD FALSIFY THIS?

- Any access-regime seed snapshot raising an argument error or omitting the collar context.
- Any geometry record whose distance/core/halo/collar masks use different centers.
- Any call path reading or computing `specific_uptake`, integrated uptake, Y, C, or I.
- Any A/B/sentinel reassignment not producing a tracker event or `PAIR_IDENTITY_SWITCH`.
- Any H00/B role substituted for H00/A (or vice versa) in reference replay.
- Any isolation pass with a zero far-field difference.
- Any engine-free reconstruction that cannot reproduce the final executor's raw gates exactly.

## Failures and dead ends

- No real executor smoke was run because even an already-open DEV world was explicitly out of this auditor's scope.
  This correctly leaves runtime qualification to the final bound runner after package reconciliation.
- The engine-free raw validator cannot independently reconstruct a rho-weighted centroid from a binary mask alone.
  The integrator must either bind the persisted centroid as a primitive and verify its downstream consequences or
  add sufficient rho moments. Reverting to a binary centroid would violate the accepted detector geometry and is not
  an acceptable shortcut.

## Decisions

1. Preserve exact frozen physics and thresholds; repair orchestration/measurement only.
2. Use a mask-only geometry adapter rather than calling an outcome-producing convenience detector.
3. Treat A, B, and sentinel as one essential three-track identity set for switch detection.
4. Use tracked role-specific H00 reference masks, never an arbitrary component.
5. Keep the frozen 24-cell and discrete radius-12 gates separate and unchanged.

## Unresolved risks and handoff

- Reconcile the concurrently edited standard-library reproducer and final schema with rho-weighted centroid
  primitives, all-three-track switch derivation, and initial collar records before any DEV execution.
- Rerun the complete focused raw/reproducer suite after that reconciliation and regenerate the exact code/input
  bindings because these executor/mechanics changes alter the bound blobs.
- Only then may the primary integrator execute the already-authorized four-world DEV mechanical plan. This journal
  authorizes no run and makes no `GO_FOR_HUMAN_SEAL_REVIEW` decision by itself.

Exact next action: finish the engine-free raw-contract reconciliation, rerun its synthetic corpus plus the 44 focused
mechanics/preflight tests, then rebuild the clean hash-bound DEV manifest before any engine import.
