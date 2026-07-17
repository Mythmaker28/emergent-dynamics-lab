# Agent journal — ACCESS-STRUCTURE-00 Phase 0.5

- **Role:** causal-state inventory and DEV intervention-operator qualification engineer
- **Run ID:** `RUN-20260717-0252-ACCESS-STRUCTURE-00-P05`
- **Start:** 2026-07-17 02:52:12 +02:00
- **End:** 2026-07-17 03:34:31 +02:00
- **Starting Git state:** clean isolated branch `codex/access-structure-00-phase0` at `ef7fe06a920dac56dc9f4ea84836f63e73001e0e`
- **Ending Git state:** coherent Phase 0.5 deliverable prepared for one local commit on the same isolated branch;
  no push or merge (exact commit hash is reported in the final handoff because a commit cannot contain its own hash)
- **Scheduled-run lock:** not applicable; direct human-approved Phase 0.5 DEV-only work
- **Authorization boundary:** operator qualification only on already-open seeds `50001-50010`; no prospective family, seal, push, merge, 03G/V5 modification, ownership claim, or active reconstruction

## Assigned scope

Inventory the complete causal and dynamical state; replace ambiguous `L0/E0` notation with explicit donor-labelled
`C_A E_A` arms; implement and qualify no-op, round-trip, sham, coordinate transform, matched/crossed graft,
standardization/reset, global-channel ablation, and readout-ablation operators on the existing DEV namespace only;
protect halo and dynamical-phase alternatives; revise the unsealed preregistration; return GO/REVISE/STOP and commit
locally.

## Starting observations

- Phase 0 commit `ef7fe06` is preserved and is the exact starting HEAD.
- Worktree is clean on the isolated ACCESS-STRUCTURE branch.
- Repository declarations and executable guards agree that `50001-50010` is the existing DEV namespace.
- The prior Phase 0 report found only four deep-feasible worlds: 50002, 50004, 50005, 50007.
- `L` remains reserved for the frozen 03G 11-statistic readout. Phase 0.5 uses `C/B/H/E/N-P/G/D` and records overlaps.

## Important files read

- `AGENTS.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md`
- `docs/EXPERIMENT_INDEX.md`
- `docs/RUN_INDEX.md`
- Phase 0 journal, report, DEV feasibility JSON, and unsealed preregistration draft
- attached Phase 0.5 human authorization and mission

## Actions and reproducible commands

- Read the repository contract and durable state in the mandated order, then inspected the Phase 0 artefacts,
  complete engine update, detector, material tracer, bijective tracker, DEV guards, and existing ablation engines.
- Confirmed the only authorized namespace from both declarations and executable guards: `50001-50010`.
- Reconstructed the four existing deep-feasible states and measured body support radii/target separation using only
  geometry; selected radius-10 `C` and one-cell `H` without future feeding.
- Implemented `experiments/individuation/access_structure_operators.py`: complete state serialization, partition,
  exact shams, reciprocal core exchange, on-manifold standardization/reset wrapper, band and state audits.
- Implemented `experiments/individuation/access_structure_dev_qualification.py` with a hard DEV seed guard. It never
  evaluates active crossed feeding.
- Implemented eight focused operator tests.
- Executed the complete qualification:

  `C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe -m experiments.individuation.access_structure_dev_qualification --output docs\individuation\ACCESS_STRUCTURE_00_PHASE05_DEV_QUALIFICATION.json --seeds 50001 50002 50003 50004 50005 50006 50007 50008 50009 50010`

- Regenerated the result after adding explicit branch-balance, seam, halo, cohort, and geometry summaries. Final
  machine-result SHA-256: `90713D86396C2A551B693C140D3F8B1FC338029E65ACAF69E977757686296ECA`.
- Validation:
  - `python -m pytest experiments\individuation\test_access_structure_operators.py experiments\individuation\test_turnover_end_to_end_03g.py tests\test_engine.py -q` -> 29 passed;
  - `python experiments\individuation\test_bijective_tracker.py` -> 10/10 passed;
  - `python -X utf8 experiments\individuation\test_turnover_tracer.py` -> all six checks passed;
  - machine JSON assertions and `git diff --check` passed.
- Wrote the complete variable-level state map, donor-labelled arm table, DEV qualification report, revised unsealed
  preregistration, kill-switches, D-090, project/index updates, and this journal.

## OBSERVED

- `rho,U,V,c,N,C,Mf,uptake,step` are the complete persistent state under compatible frozen engine context.
  Incoming `uptake` is a previous-step readout and is not read by the next update. `up_ref`, fluxes, gradients,
  concentrations, memory readouts, and write signals are recomputed. No persistent RNG, velocity/momentum,
  previous-state buffer, flux/gradient buffer, or solver cache exists.
- All 12 history-source bodies and four no-history reference bodies fit in radius-10 `C`; selected source blocks are
  disjoint. `B` is a subset of `C`; physical fields overlap every spatial compartment.
- Exact controls are all zero-error immediately; serialized and no-op states remain identical after 10 steps.
  Coordinate-sham future-feeding bias is exactly zero.
- Every one of six active arms is 4/4 valid for the 40-step qualification. Expected post-surgery body overlap and
  IoU are both 1. Dynamic `up_ref=0` and `lam_plus=0,lam_minus=0.15` branches remain viable and retain uptake.
- Active surgery changes no undeclared `H/E` cell at time zero. Base-cohort accounting error is at most `2.56e-15`.
  Reciprocal-pair conservation error is at most `9.10e-13`.
- Boundary seam ratios fail: maximum `22.872x`; only 4/168 field-arm-world values pass the unsealed `1.25x`
  candidate. Maximum one-cell-halo RMS difference rises from `0.809` at step 1 to `0.985` at step 40; far-E maximum
  RMS is `0.0287` at step 40.
- Individual branch totals are not matched even though pairs conserve: maximum absolute deltas include `c=84.58`,
  `U=58.14`, and `rho=40.72`.
- No active crossed future-feeding outcome and no hypothesis outcome were evaluated.

## INFERRED

- Exact reciprocal exchange solves source-state preservation and paired conservation, but not causal
  interpretability. The hard interface creates a numerical/physical transient that can imitate relational synergy.
- Forty-step viability is a necessary engineering pass, not evidence that surgery is on-manifold or unbiased.
- The fixed radius-10 `C` is broader than droplet material. Even a future valid positive would establish local/core
  access under this support, not material ownership.
- Pairwise conservation cannot substitute for the requested per-arm mass/body/physical-field balance because `G`
  and future feeding can respond to branch-level totals.

## HYPOTHESIS

Selective full-state manipulation may be technically possible only if core/body/halo/environment boundaries and
the simulation's dynamical phase are preserved explicitly; otherwise graft disturbance may be inseparable from the
intended compartment change.

## WHAT WOULD FALSIFY THIS?

Exact or bounded no-op/sham equivalence plus viable matched and crossed DEV grafts that preserve all non-target
state and complete dynamical phase would falsify the claim that surgery artifacts are inseparable. Conversely,
systematic off-manifold failure under every selective operator would falsify technical separability.

## Failures and dead ends

- Three preliminary geometry-only commands stopped before producing evidence because they used a wrong report path,
  outdated helper signature, and a nonexistent centroid helper. They were corrected without opening a new seed or
  evaluating feeding.
- A first one-world smoke summary counted the reciprocal donor site as changed far environment because both swaps
  were combined in one state. The operator was corrected to produce two branch clones (`C_B E_A` and `C_A E_B`),
  with conservation audited across the pair. The corrected smoke had zero unintended `H/E` change.
- Collecting the script-style tracker checker with pytest caused a pytest internal `SystemExit: 0` after its 10/10
  passes. Running it through its intended standalone entry point passed. The first standalone tracer command hit a
  Windows CP1252 print error on `Δ`; `python -X utf8` ran the unchanged tests successfully.

## Decisions

- Do not treat `L` as the complete droplet microstate.
- Do not inspect or select any prospective seed namespace.
- Qualification effects are engineering evidence only and cannot answer where memory resides.
- Reject one-way scaled grafts because scaling changes donor `C`; use reciprocal exact exchange for qualification.
- Reject the current hard-boundary operator for causal inference despite viability passes.
- Record D-090 and recommend REVISE. Do not inflate the seam threshold to the failed DEV maximum.

## Unresolved risks

- A boundary-aware correction may erase or manufacture the very halo/interface relation under test.
- Arm-level balance may be impossible without altering `H/E` or donor `C`; if so, the correct next decision is STOP.
- The common probe remains unqualified because 03G's nutrient reset would overwrite an environmental compartment.
- Practical/equivalence margins, power, and the prospective family remain deliberately unset.

## Handoff

**REVISE — stop for human review.** The current operator is mechanically exact and viable but fails seam and
individual-arm balance gates. No prospective family, preregistration seal, push, merge, V5/03G change, ownership
claim, or active reconstruction is authorized. A further boundary-aware/balance repair on already-open DEV requires
new explicit approval. If approved, it must expose `H` with the two named halo controls and pass unchanged gates;
otherwise STOP.
