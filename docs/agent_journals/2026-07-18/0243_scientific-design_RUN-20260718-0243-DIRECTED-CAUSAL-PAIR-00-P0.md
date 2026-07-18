# Agent journal — DIRECTED-CAUSAL-PAIR-00 Phase 0

- Role: independent scientific auditor and directed-factorial designer
- Run ID: `RUN-20260718-0243-DIRECTED-CAUSAL-PAIR-00-P0`
- Start time: 2026-07-18 02:43 CEST
- End time: 2026-07-18 03:05 CEST
- Starting Git state: isolated worktree created from clean exact commit
  `7deeb8e0bd4ac972e1dd133fc8992fcfc4f2fb2b`
- Ending Git state: coherent Phase-0 branch tip; expected clean after the commit containing this journal
- Branch: `codex/directed-causal-pair-00-phase0`
- Worktree: `C:\Users\tommy\Documents\ising-v3-directed-causal-pair-00-phase0`
- Runtime lock: not applicable; direct human-requested design/audit run, not a scheduled heartbeat

## Assigned scope

Perform **Phase 0 only** for `DIRECTED-CAUSAL-PAIR-00`: independently select the smallest accepted parent; preserve
V5/03G and 58xxx artefacts; audit already-open DEV worlds for a separated natural pair; determine exact-clone
factorial feasibility without pair-outcome selection; specify a directed non-symmetrized causal matrix, DAG,
hypotheses, access/channel controls, raw schema, draft preregistration, kill switches, and GO/REVISE/STOP judgement;
commit and push the isolated branch; stop before any prospective seed-family inspection or execution.

## Repository and provenance audit

Read in the mandated order:

1. `AGENTS.md`;
2. `docs/RESEARCH_CHARTER.md`;
3. `docs/PROJECT_STATE.md`;
4. `docs/DECISION_LOG.md`;
5. `docs/EXPERIMENT_INDEX.md`;
6. `docs/RUN_INDEX.md`;
7. latest prior journal
   `docs/agent_journals/2026-07-17/0252_operator-qualification_RUN-20260717-0252-ACCESS-STRUCTURE-00-P05.md`;
8. current/last experiment design, manifest-equivalent results, and summary under
   `docs/individuation/ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_*`.

Also inspected the exact writer, corrected probe, tracker, turnover DEV raw, Phase-0.5 qualification, no-swap
operators/results, and their Git history/hashes. The first accepted linear parent containing the 03G lineage plus
implemented and reported no-swap mechanics is
`7deeb8e0bd4ac972e1dd133fc8992fcfc4f2fb2b`. It avoids later access phases and downstream reader work.

The original shared checkout was highly dirty and had a broken unrelated ref `refs/heads/probe/tmp01`; it was not
modified. A first normal worktree checkout encountered Windows-invalid historical cache paths under
`results/_tomo_cache`. After verifying the failed target had no worktree registration and the exact branch pointed
to the intended parent, created a `--no-checkout` worktree and used sparse non-cone checkout excluding only that
invalid cache directory. The branch/worktree then checked out cleanly.

## Actions and important files

Created:

- `experiments/individuation/directed_causal_pair_phase0_audit.py` — stdlib-only, static, outcome-blind audit with a
  hard `50001-50010` namespace guard and no engine import;
- `experiments/individuation/test_directed_causal_pair_phase0.py` — geometry, selection, audit, and committed-result
  contract tests;
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json` — hash-bound machine audit;
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_REPORT.md` — independent judgement, provenance, DAG, design,
  hypotheses, raw requirement, and kill switches;
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PREREGISTRATION_DRAFT.md` — unsealed factorial and analysis contract;
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_RAW_SCHEMA_DRAFT.json` — smallest sufficient world-nested schema.

Updated:

- `docs/PROJECT_STATE.md`;
- `docs/EXPERIMENT_INDEX.md`;
- `docs/RUN_INDEX.md`;
- `docs/DECISION_LOG.md` with genuine Phase-0 decision D-091.

No V5/03G source or raw artefact was modified. No 58xxx record was opened, enumerated, reserved, or executed. No
prospective engine or seed family was instantiated.

## Reproducible commands

The isolated worktree reuses the original checkout's untracked virtual environment only as an interpreter:

```powershell
$python = 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe'
& $python experiments/individuation/directed_causal_pair_phase0_audit.py `
  --repo . `
  --output docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json
& $python -m json.tool docs/individuation/DIRECTED_CAUSAL_PAIR_00_RAW_SCHEMA_DRAFT.json > $null
& $python -m json.tool docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json > $null
& $python -m unittest experiments.individuation.test_directed_causal_pair_phase0 -v
```

Observed validation before handoff: 21/21 focused audit/no-swap/access-operator pytest checks PASS; the standalone
tracker contract reports 10/10 PASS; both JSON files parse; the new Python files compile. An optional Draft-2020-12
meta-schema check was unavailable because `jsonschema` is not installed in the frozen local environment; no package
was added for this documentation-only check.

## OBSERVED

- Four of ten open DEV worlds are pair-eligible: 50002, 50004, 50005, 50007.
- Each contains three targets with no turnover `first_censor`; all three pass the existing deep G0 continuation.
- Outcome-blind maximum-initial-separation selection yields pairs whose initial/deep distances are respectively:
  50002 35.2546/34.3726; 50004 29.3007/29.2421; 50005 33.6020/32.9711; 50007 32.9757/32.2228.
- The smallest endpoint gap beyond two radius-12 halos is 5.2421 cells.
- Phase-0.5 reports pairwise-disjoint radius-10 core blocks and exact serialization/no-op controls.
- Phase-0.6B reports 12/12 single-target bit-exact isolation under `up_ref=0`, exact own-replay sham, and viable
  single-target continuations.
- Existing turnover raw has initial/deep centroids but no per-step pair distance or halo-overlap count.
- Existing no-swap qualification used no-history continuations and did not run a recipient beside a history-bearing
  partner. No H00/H10/H01/H11 pair set exists.

## INFERRED

- The pair factorial is compositionally plausible using accepted components.
- Available evidence is insufficient for prospective mechanical GO because two load-bearing pair-context contracts
  have not been exercised: continuous separation/halo logging and history-bearing recipient clamp/sham validity.
- Four worlds are feasibility cases, not independent support for a four-entry directed causal matrix.
- `C_AB` and `C_BA` must remain distinct; symmetrizing them would erase the question of direction.
- Body/mass/geometry lie on intervention-to-feeding paths and therefore belong in unadjusted total effects plus
  mediation diagnostics, not primary regression adjustment.

## HYPOTHESIS

Two genuinely distinct causal carriers should primarily produce stable diagonal effects, while environmental,
pair-local, asymmetric, relational, or global organization predicts distinct off-diagonal, cut-sensitivity,
interaction, asymmetry, or sentinel patterns. These are diagnostic signatures, not conclusions; margins remain
unsealed.

## WHAT WOULD FALSIFY THIS?

- A pair-context DEV qualification that cannot keep H00/H10/H01/H11 exact clones distinct and valid under unchanged
  tracker/fusion/separation rules would falsify mechanical feasibility.
- Any selected pair crossing below 24 cells, overlapping radius-12 halos, fusing, switching components, or losing
  the sentinel in an essential arm would falsify that world's eligibility.
- Any nonzero own-replay difference would falsify sham equivalence.
- A writer schedule or pair choice that depends on pair feeding outcomes would invalidate the design.
- A prospective family yielding fewer than 18 whole valid worlds at its future frozen hard cap would leave the
  scientific question unanswered.

## Failures and dead ends

- Initial worktree checkout failed on Windows-invalid tracked `_tomo_cache` names. Recovered without deleting or
  modifying repository data by sparse-excluding only that historical cache path.
- First synthetic pair-selection test accidentally made pair 1-2 farther than the intended pair. Corrected the
  test fixture; the production selection code and generated DEV result were unchanged.
- A prospective `GO` was rejected because the existing single-target no-swap record is not the pair-context test.
- A `STOP` was rejected because all missing contracts are mechanically testable without changing physics or
  thresholds.

## Decisions and unresolved risks

Decision: **REVISE**. D-091 records the exact directed-matrix convention, world-level unit, mediator handling,
available DEV evidence, missing mechanics, and authorization boundary.

Unresolved before any preseal:

- pair-context mechanical qualification;
- continuous geometry/halo raw evidence;
- final effect and equivalence margins;
- multiplicity and operating-characteristic justification for the four matrix entries plus interactions/asymmetry;
- authoritative runtime, future seed family, hard cap, manifests, and fresh human authorization.

## Handoff

Exact next authorized action after review: run one outcome-blind mechanical qualification on already-open 500xx DEV
worlds only. It may record clone equality, writer operations, per-step geometry, tracker/fusion state, clamp/sham
disturbance, and probe viability. It must not compute or inspect pair Y/C/I contrasts. Do not open a prospective
namespace, alter V5/03G/58xxx, relax thresholds, symmetrize the matrix, or add a reader/decoder/composite.
