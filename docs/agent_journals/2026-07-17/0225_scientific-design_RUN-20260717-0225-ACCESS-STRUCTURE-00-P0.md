# Agent journal — ACCESS-STRUCTURE-00 Phase 0

- **Role:** independent scientific auditor and intervention-design engineer
- **Run ID:** `RUN-20260717-0225-ACCESS-STRUCTURE-00-P0`
- **Start:** 2026-07-17 02:25:06 +02:00
- **End:** 2026-07-17 02:45:58 +02:00
- **Starting Git state:** clean isolated branch `codex/access-structure-00-phase0` at `d4a146a241588c0debd3a0cc6133bc6f6bb8824c`
- **Ending Git state:** coherent Phase-0 changes on `codex/access-structure-00-phase0`, ready for validation and commit; no push
- **Scheduled-run lock:** not applicable; direct user-requested Phase 0 design work, no prospective experiment authorized or launched

## Assigned scope

Audit the exact 03G L/B/E/N/P/G definitions and their limits, determine what the frozen environmental summaries could not detect, design the smallest intervention experiment distinguishing local, environmental, redundant, synergistic/relational, and residual/body-state explanations, and test technical feasibility using already-open DEV data only. Draft a preregistration and frozen kill-switches, give an explicit GO/REVISE/STOP recommendation, and stop for human review before any prospective seed is opened.

## Starting observations

- The canonical lineage is linear: certified 03G result `9cb996b` -> independent raw reproduction `a8d6446` -> V5 `d4a146a`.
- The original checkout at `C:\Users\tommy\Documents\ising v3` is heavily dirty and was not modified or cleaned.
- A Windows-incompatible tracked cache filename initially prevented a conventional worktree checkout. The branch was preserved and a sparse worktree was constructed without altering the original checkout.
- Canonical 03G status is Outcome B with 21 valid original worlds: `G_OWN_PERM=true`, `G_CAUSAL=true`, `G_LOCAL_EXCLUSION=false`, `DISTRIBUTED_ENV=false`.

## Important files read

- `AGENTS.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md`
- `docs/EXPERIMENT_INDEX.md`
- `docs/RUN_INDEX.md`
- latest journal `docs/agent_journals/2026-07-17/0126_paper-synthesis_PAPER-20260717-0126-05.md`
- `docs/individuation/TURNOVER_EXECUTION_MANIFEST_03G.json`
- `results/LCI-TURNOVER-PROSPECTIVE-03G/analysis/analysis_report_03g.md` and machine certificate, read from the canonical Git object
- `docs/individuation/TURNOVER_PROTOCOL_03G.md`
- `docs/individuation/TURNOVER_RAW_SCHEMA_03G.json`
- `docs/individuation/TURNOVER_DECISION_TREE_03G.json`
- `experiments/individuation/turnover_scope_features.py`
- `experiments/individuation/turnover_scope_features_03e.py`
- `experiments/individuation/turnover_scope_features_03g.py`
- `experiments/individuation/turnover_statistics_03g.py`
- `experiments/individuation/turnover_analyzer_03g.py`
- `experiments/individuation/turnover_engine_03g.py`
- `experiments/individuation/turnover_runner_03g.py`
- `experiments/individuation/turnover_dev_runner.py`
- `experiments/individuation/turnover_dev_diagnostics.py`
- `experiments/individuation/turnover_dev_raw.json`
- `experiments/individuation/turnover_dev_diagnostics_raw.json`
- `edlab/experiments/sc_mcm/engine.py`
- `edlab/substrates/scaffold/engine.py`

## Actions and reproducible commands

- Fetched origin read-only to obtain the three canonical commits.
- Verified ancestry with `git merge-base --is-ancestor`.
- Created `codex/access-structure-00-phase0` at exact V5 commit `d4a146a`.
- Created sparse worktree `C:\Users\tommy\Documents\ising-v3-access-structure-00` containing the scientific sources and documents required for Phase 0.
- Audited exact scope feature code and gate implementation against the certified 03G analysis object.
- Audited seed namespaces across valid refs. Apparent `55xxx` hits were byte-count values, not semantic seed
  declarations; the pre-existing broken ref `refs/heads/probe/tmp01` prevents a clean all-ref family claim, so no
  family was selected.
- Parsed the already-open DEV raw and diagnostics. Deep feasible seeds are 50002/50004/50005/50007.
- Deterministically reconstructed all four deep states using their already-open seeds and exact recorded depths.
  Maximum absolute error against committed diagnostics was `1.67e-16` for `m_plus` and `1.11e-16` for material
  retention; all three tracks were alive in every reconstructed world.
- Wrote the Phase-0 report, proposed preregistration skeleton, and machine-readable DEV feasibility record.
- Updated project, experiment, run, and decision indexes. No source physics, prospective raw, or manuscript file was
  modified.
- Validated the JSON artifact and `git diff --check`.
- Ran `python experiments/individuation/test_turnover_end_to_end_03g.py`: 7/7 PASS.
- Ran `PYTHONUTF8=1 python experiments/individuation/test_turnover_tracer.py`: all six tracer/tracker checks PASS,
  including zero feedback, deterministic bytes, monotone material retention, bijection, and fission censorship.

## OBSERVED

- 03G `L` is 11 target-memory distribution summaries, not the complete tracked droplet.
- `B` contains local `N,c`, and `E` retains target-local `rho,U/rho,V/rho,c,N,uptake` while masking only target
  `m1,m2`. Neither is a clean causal compartment.
- `E` loses angular/fine/relational/temporal information and anything beyond radius 24. `Gm` retains only occupied-
  cell means/SDs plus mean uptake and occupied fraction; it loses all spatial and cross-field structure.
- `Gf` is exactly `L||Gm` and `P` contains `L`; both are diagnostic and cannot localize ownership.
- Certified `L>E` and `L>B` Student-t lower bounds are negative; `E` and `Gm` skill lower bounds are also negative.
  This produces `G_LOCAL_EXCLUSION=false` and `DISTRIBUTED_ENV=false` without establishing absence.
- Existing code supports target `Mf` erase, N standardization, common probe, trackers/fixed masks, and global
  `up_ref` ablation. It does not support a qualified full environment reset, standardized body in original
  environment, crossed state graft, or matched graft sham.
- DEV direct algebraic readout predictions closely track observed erase fractions, making residual direct readout a
  serious alternative; the comparison remains exploratory.

## INFERRED

- Outcome B establishes causal persistence in the original matched world, not the compartment that is sufficient.
- A causal 2x2 `L/E` factorial plus matched-cross contrast is the smallest design that can distinguish local,
  environmental, redundant, and synergistic/relational access.
- The new design is implementable on explicit state arrays but is not yet manipulation-qualified. A prospective run
  now would confound storage with graft shock and body/environment mismatch.

## HYPOTHESIS

The 03G Outcome B may arise from causal state stored locally, environmentally, redundantly, relationally, or from a residual body/readout variable that the frozen access comparison did not isolate causally.

## WHAT WOULD FALSIFY THIS?

A validated factorial state-exchange intervention under a common future probe that assigns sufficiency to one compartment, or shows the effect disappears after body-state matching, would eliminate corresponding alternatives.

## Failures and dead ends

- Conventional worktree checkout failed on tracked filenames containing `|`, illegal on Windows. Resolved with a sparse worktree; no historical file was renamed or removed.
- The first tracer-test invocation reached its first assertion but failed while printing Unicode delta under the
  Windows cp1252 console. Re-run with Python UTF-8 output; the unchanged suite then passed completely. This was a
  console-encoding failure, not a scientific or test assertion failure.

## Decisions

- Preserve 03G and V5 unchanged.
- Treat frozen decoding gates as evidence about access through finite summaries, not as causal localization.
- No new prospective family or active reconstruction experiment will be run in Phase 0.
- Recommend **REVISE**, not GO or STOP.
- Require a DEV-only manipulation qualification and a later complete human-approved preregistration before any new
  prospective family.

## Unresolved risks

- No exact, validated `E0`, `B0`, donor map, boundary/seam rule, or energy-matching correction exists.
- No active-operation-equivalent sham or frozen practical/equivalence margin exists.
- Four feasible DEV worlds establish reconstructibility, not a reliable feasibility rate or statistical power.
- Continuous PID is estimator-dependent and must remain secondary with its assumptions frozen.
- The broken Git ref prevents declaring a new semantic seed namespace clean; no candidate family was selected.

## Handoff

Recommendation: **REVISE — HUMAN REVIEW REQUIRED — NO PROSPECTIVE AUTHORIZATION**.

Exact next action is review of `docs/individuation/ACCESS_STRUCTURE_00_PHASE0_REPORT.md`. If the human approves a
repair, implement and validate only the manipulation kernel on already-open DEV seeds `50001-50010`; freeze every
remaining field in a later preregistration and return for a second explicit authorization before opening any
prospective seed. Preserve 03G commits/raw and V5 unchanged. Do not push or merge this branch under the current
mission.
