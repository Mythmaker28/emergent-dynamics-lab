# Agent journal — DOWNSTREAM-ORDER-READER-01 instrumentation

- Role: passive instrumentation and synthetic qualification engineer
- Run ID: `RUN-20260717-2317-DOWNSTREAM-ORDER-READER-01-INSTRUMENT`
- Start: 2026-07-17 23:17:06 +02:00
- End: 2026-07-17 23:27:53 +02:00
- Starting Git state: clean isolated worktree at design commit `0abab247662d10c041dd52003b8b018d4ebfd521`
- Branch: `codex/downstream-order-reader-01-instrumentation`
- Ending Git state: clean dedicated branch after the instrumentation commit and push; primary checkout unchanged
- Scheduled-run lock: not applicable; direct human authorization for instrumentation and synthetic fixtures only
- Assigned scope: implement only the passive exact-face-flux logger and synthetic qualification; revise the causal
  schedule, endpoint wording, sign status, secondary ablation role and margin rationale; open no scientific seed or
  outcome.

## Files and evidence read

- `AGENTS.md`, research charter, project state, decision-log tail, experiment/run indexes and preceding design
  journal.
- Current downstream causal audit, preregistration draft and GO/REVISE/STOP recommendation.
- `M_MINUS_ORDER_READER_00_PROTOCOL.md`, DEV report and accepted source-calibration result boundary.
- Frozen `ScaffoldEngine._face_flux`, `MultiChannelMemoryEngine.step`, `DiagEngine`, `NoSwapClampEngine`, `IOMState`
  and existing source-reader tests.
- Testing-strategy skill instructions; used to keep the qualification focused on fast unit/engine-integration
  identities, edge cases and data integrity rather than an outcome runner.

## Actions

1. Created the instrumentation branch from the clean design commit; no scientific state was reconstructed.
2. Implemented a passive logger mixin for both `DiagEngine` and `NoSwapClampEngine`. It returns the inherited live
   flux array unchanged and records a separate read-only copy.
3. Implemented pure matched-ramp geometry, explicit internal/boundary face masks, the mass-specific internal +x
   face-flux sum, boundary diagnostics and a closed-fixture first-moment check.
4. Added seven synthetic fixtures covering base/clamp state identity, exact logged flux, one common 40-step settle,
   source-only `lam_minus` branching, common response configuration, matched ramp, first moment, boundary flux and
   saturation sign reversal.
5. Revised the audit and preregistration: the endpoint is not displacement; positive sign is a directional
   hypothesis; source-zero order equivalence is secondary; `m_A/m_0` are unsealed.
6. Added the code-only qualification report and updated durable project, experiment, run and decision records.
7. Did not import a scientific outcome runner, select a seed namespace, reconstruct 570xx, run feeding,
   `BODY-EQUALIZATION`, another reader or a reader battery.

## Reproducible commands

```powershell
$env:PYTHONUTF8='1'
$py='C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe'
& $py -m pytest experiments/individuation/test_downstream_order_reader_instrumentation.py -q
# initial: 7 passed in 1.32s
& $py -m py_compile experiments/individuation/downstream_order_reader_instrumentation.py `
  experiments/individuation/test_downstream_order_reader_instrumentation.py
& $py -m pytest experiments/individuation/test_downstream_order_reader_instrumentation.py `
  experiments/individuation/test_mminus_order_reader_dev.py `
  experiments/individuation/test_access_structure_noswap_operators.py -q
# final: 27 passed in 5.95s
```

The final strengthened focused run, including the common no-swap schedule, was `7 passed in 0.82s`.

## OBSERVED

- Base logged/unlogged terminal hashes are identical:
  `39537c88c00a339c2d9e47f33b4578807e58f211abe90907cd1a0dda77c0128f`.
- The logger records exact read-only arrays in axis order `(-2,-1)` and remains identical under the no-swap clamp.
- One common intact settle can be cloned; changing `lam_minus` for only the next source update changes only output
  `c`; all response arms can then use common `lam_minus=0.15`.
- Radius-10 geometry has 317 cells and 296 internal +x faces; all arms add total `c=3.17`.
- Closed-fixture first-moment residual is `-5.55e-17`.
- Boundary flux changes core mass without entering the internal endpoint.
- The matched ramp response is `+2.6175406501143461e-4` in an ordinary synthetic field and
  `-2.024053728781291e-6` under strong saturation.
- No scientific outcome was generated.

## INFERRED

- The passive logger measures the exact executed first-step operator without changing physics.
- The open radius-10 endpoint must be named an internal face-flux sum; the closed first-moment identity does not
  turn it into whole-body movement when boundary flux exists.
- Response sign depends on saturation and state. Positive EARLY-minus-LATE attenuation is falsifiable science, not
  a mechanical qualification rule.
- Exact common-settle cloning isolates the one-step source contribution more cleanly than separate settles.
- A nonzero order response under source ablation indicates another order pathway but does not erase the primary
  source-condition-by-order interaction.

## HYPOTHESIS

If a separately approved scientific family is ever run, EARLY history will show a larger source-channel-dependent
attenuation of the mass-specific internal +x face-flux response than LATE history. No practical magnitude is
currently sealed.

## WHAT WOULD FALSIFY THIS?

- A valid scientific primary interaction at or below zero would falsify the directional hypothesis.
- A logger/state hash mismatch, wrong flux array, schedule contamination, unequal ramp, unaccounted boundary term
  or nondeterministic fixture would invalidate the instrument.
- A source-zero order pathway would narrow mechanism specificity but would not by itself falsify the primary
  interaction estimand.

## Failures and dead ends

- The previous endpoint wording implied displacement without a closed-domain proof. It was replaced by the exact
  internal face-flux name; a closed fixture and an explicit open-boundary counterfixture were both added.
- The previous separate `lam_minus` settles allowed trajectories to differ for 40 steps. Human review replaced
  them with one common settle and a one-update source-only branch.
- The former numeric margins were not supported by a scientific relevance argument. They were withdrawn as
  thresholds rather than tuned from any outcome.
- `ruff` was not installed in the repository environment (`No module named ruff`); `py_compile`, focused tests,
  regression tests and `git diff --check` provide the recorded validation instead.

## Decisions, unresolved risks and handoff

- Instrument status: `QUALIFIED` after final regression confirmation.
- Scientific preregistration: `REVISE` because `m_A`, `m_0` and final prospective bindings remain unsealed.
- The passive logger adds observational memory to the engine object; future scientific code must clear or consume
  records per step and must never feed them back into physics.
- Exact next action: human review of the updated causal audit and margin rationale. No seed or outcome is the next
  authorized action.
