# BALANCED-HISTORY-ISOLATION-00 — DEV report

**Verdict:** `DEV-FEASIBILITY-FAIL — REVISE-MECHANICS`

**Prospective recommendation:** **NO GO**; human review required; no prospective namespace was inspected or opened.

**Canonical parent:** `6d1a5f718b965d2896f2a3e4d6cbcf5c8c83542f`

**Before-data freeze commit:** `87f2629`

**Manifest SHA-256:** `83eaffd530cfb82d07010f0e5171fc631dc98251de9b4c3be2dd2af98a33f08b`

**Raw DEV result SHA-256:** `a507a27e92089e417d0dafb27aa66a6bca1674a56a3c457bcae2ac80022a470d`

## Independent scientific judgment

The semantic and allocation design is valid, but the natural-world mechanics do not supply the four eligible
pre-history targets required to instantiate it. Across the immutable 24-world DEV family, no world reached the
assignment gate. Therefore this experiment produced no treated target, no post-treatment selection, no deep
intervention, and no dose/order/interaction endpoint.

This is a clean feasibility failure. It is not evidence that cumulative-dose memory, temporal-order memory, local
transport, `lam_plus` mediation, or an isolated causal effect is absent. None of those questions was evaluated.
The protocol must not be promoted to prospective use in its current four-target form.

## Semantic verdict — PASS

Engine inspection confirmed that `a1` and `a2` are amplitudes of a local Gaussian nutrient patch delivered in two
genuinely ordered consecutive 60-step episodes. Swapping them reverses temporal order at exactly matched total
dose. All four frozen amplitudes are strictly inside the previously exercised `[0.005,0.035)` support.

The histories can affect `N` diffusion, other targets, body/geometry, uptake, physical fields and ordinary global
`up_ref`; these were predeclared causal paths/diagnostics. Assignment was implemented only after four-target
eligibility. No legacy random history was split, reanalysed or reinterpreted.

## Allocation and namespace verdict — PASS, never instantiated

The fresh DEV namespace was exactly `55001–55024`. A pre-run semantic-integer audit found no reuse in the current
tree, reachable history, valid local/remote-tracking refs, the recovered malformed-ref commit, or the remote-only
`origin/main` head. No prospective namespace was inspected or reserved.

The manifest's cyclic Latin square was exactly balanced: each of four histories occupies each spatial slot six
times across the 24 planned worlds, keyed only by seed. All 13 before-data gates passed at the freeze commit.
However, because zero worlds had four eligible targets, the schedule remained planned only: `assignment_applied`
is false for every world, and the intention-to-treat assigned count is zero in every history condition.

## Pre-treatment eligibility and complete-block validity

| Frozen gate | Result |
|---|---:|
| Planned original worlds | 24 |
| Worlds with 4 eligible pre-history targets | 0 |
| Worlds with 3 selected targets | 17 |
| Worlds with 2 selected targets | 7 |
| Worlds assigned all four histories | 0 |
| Deep-valid worlds | 0 |
| Complete valid worlds | 0 |

Every world exited for the same pre-treatment reason:
`fewer_than_four_pre_history_eligible_targets`. The minimum requirement was four complete original worlds; the
observed count was zero. No failed target was discarded into a survivor-only analysis and no feeding value was
imputed.

## Primary factorial endpoints

Dose, order and dose-by-order interaction contrasts are **not estimable** in coupled or isolated arms (`n=0`
original worlds). They are not numerically zero. Consequently `T_D`, `T_O` and `T_DO` are also not estimable.

The critical temporal-order test was never entered. The experiment therefore neither supports `DOSE_ONLY` nor
`DOSE_AND_ORDER`, and it cannot support `NO_LOCAL_TRANSPORT`.

## First stage, manipulation and transport

- Core `mplus`, core `mminus`, predefined `Mf` summaries and full-field metrics: not evaluated.
- Body, geometry, nutrient and physical-state factorial contrasts: not evaluated.
- Qualified clamp and own-replay sham on treated deep states: not evaluated.
- Ordinary coupled versus isolated transport: not evaluated.
- Global-matched coupled versus isolated transport: not evaluated.
- Boundary-reference reversal: not applicable; only one independent defensible reference existed pre-outcome.

The machine result represents these downstream gates as `null` (not evaluable) once the minimum-world gate fails.
The validated two-cell isolation and `up_ref=0` mechanisms remain engineering qualifications from the pre-execution
tests, not evidence about this untreated family.

## `lam_plus=0` mediation

No valid treated deep world existed, so intact-versus-`lam_plus=0` dose or order contrasts have `n=0`. Mediation is
not evaluated. Endpoint non-availability is not a mediation result.

## Exact allowed interpretation

The fixed four-target, within-world factorial is mechanically infeasible under this natural-world eligibility rule
for DEV seeds 55001–55024. This says only that the design could not create an analyzable block. It does not establish
absence of local dose state, order-sensitive state, feeding expression, environmental access, or causal transport.

Any repair must be reviewed before execution. Scientifically defensible options include redesigning the assignment
unit so exact dose/order balance is achieved across original worlds rather than requiring four simultaneous natural
targets, or establishing a new pre-treatment world-generation/eligibility mechanism. Simply dropping to survivor
targets, weakening separation/size after seeing this result, extending the seed list, or retrospectively pairing the
observed 2–3 targets would violate the frozen design.

## Execution and validation

The before-data package was committed and pushed before seed 55001. The single bounded run used:

```powershell
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' `
  -m experiments.individuation.balanced_history_isolation_dev `
  --manifest docs\individuation\BALANCED_HISTORY_ISOLATION_00_ASSIGNMENT_MANIFEST.json `
  --output docs\individuation\BALANCED_HISTORY_ISOLATION_00_DEV_RESULTS.json
```

The run wrote an atomic checkpoint after each world and finished all 24 seeds without extension. A serialization-only
post-run repair changed the announced digest to hash the raw bytes actually persisted on Windows and changed
downstream failed booleans to explicit not-evaluable `null` values when `n<4`; it did not initialize or rerun a
world, change eligibility, or alter the verdict. Resume verification skipped all 24 completed seeds and produced the
raw hash above.

Final focused and regression validation is recorded in the run journal. No prospective/confirmation seed, seal,
main merge, publication claim, or reconstruction/division/heredity experiment was opened.

## Recommendation

**NO prospective preregistration is scientifically justified.** Return `DEV-FEASIBILITY-FAIL — REVISE-MECHANICS`
for human review. The next authorized action is review of a new pre-data design that preserves original-world
inference and orthogonal dose/order assignment without requiring four simultaneous eligible natural targets.
