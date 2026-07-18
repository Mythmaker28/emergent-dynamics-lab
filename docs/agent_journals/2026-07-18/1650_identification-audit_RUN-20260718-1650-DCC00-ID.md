# DEEP-CHECKPOINT-CAUSAL-CUT-00 Phase 0 independent identification audit

- **Role:** independent scientific identification and candidate-operator auditor
- **Run ID:** `RUN-20260718-1650-DCC00-ID`
- **Start time:** 2026-07-18 16:50:04 +02:00
- **End time:** 2026-07-18 17:52:16 +02:00
- **Starting branch:** `codex/deep-checkpoint-causal-cut-00-phase0`
- **Starting Git state:** `cce7a27955f5cfb1fc3d95388bba9378bc8d85eb`; primary integration journal untracked; no tracked changes
- **Ending Git state:** HEAD unchanged at `cce7a27955f5cfb1fc3d95388bba9378bc8d85eb`; this journal untracked
  alongside the primary/other-agent work; no tracked changes made by this auditor

## Assigned scope

Independently audit and design Phase 0 for a no-history-writer experiment that begins at exact serialized deep DEV
checkpoints, tests an exact-clone `C00/C10/C01/C11` pair-local-cut factorial, preserves the common state, defines
separate `Y_A` and `Y_B`, and discriminates diagonal, crossed, common-mode, relational, and manipulation-artifact
explanations. Audit only: do not inspect or compute feeding outcomes, initialize any seed, use `58xxx`, change
V5/03G, execute prospective work, or edit shared reports, indexes, or schemas.

## Actions

- Read `AGENTS.md`, the research charter, project state, decision log, experiment index, run index, latest partial
  journal, and the current/last experiment manifest and report in the required order.
- Verified branch/HEAD/status and accepted `STOP_PAIR_MECHANICS` without reinterpretation.
- Performed a read-only inventory of the four deep-feasible already-open DEV worlds, their selected pairs, deep
  state hashes, checkpoint persistence, and the existing global-ablation, memory-surgery, and no-swap operators.
- Inspected only mechanical keys/values from the Phase-0.6B record. No feeding response or pair contrast was read.
- Specified a conditional, non-executable `C00/C10/C01/C11` factorial, full non-symmetrized matrix, competing
  hypotheses, raw numerical contract, and fail-closed gates.

## Important files read or changed

- Read: required durable state listed above; `DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json`;
  `ACCESS_STRUCTURE_00_PHASE0_REPORT.md`; `ACCESS_STRUCTURE_00_PHASE05_REPORT.md`;
  `ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_DESIGN.md`; mechanical-only selected fields from
  `ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_RESULTS.json`; `access_structure_operators.py`;
  `access_structure_noswap_operators.py`; `access_structure_noswap_dev_feasibility.py`;
  `turnover_diag_engine.py`; `turnover_dev_runner.py`; and the frozen `sc_mcm/engine.py`.
- Changed: this journal only.

## Reproducible commands and experiments

Read-only commands included `git branch --show-current`, `git rev-parse HEAD`, `git status --short --branch`,
`rg` source inventories, and standard-library JSON key/whitelist extraction. No simulation, intervention,
prospective seed, feeding readout, or outcome analysis was performed.

Validation: `git diff --check` passed; no code was changed, so no engine or scientific test was run.

## Candidate deep-checkpoint inventory

The existing static mechanical record identifies four already-open worlds with three continuous uncensored tracks
at the first frozen deep-turnover instant. The pair was selected by maximum initial toroidal separation and oriented
without outcomes. Values below are mechanical metadata only.

| DEV world | Deep step | Exact state-content SHA-256 | A | B | Deep A-B distance | Radius-12 halo gap |
|---:|---:|---|---:|---:|---:|---:|
| 50002 | 847 | `bfe23b0c2bae892a60938eb65f629afca3155889fee7f77f90b30ab74a21ba4f` | 0 | 2 | 34.3725707066 | 10.3725707066 |
| 50004 | 793 | `4f6422672e2948c828a12670fda6b3946b5ddf077ea226c88bf7863bcdffaf9f` | 0 | 1 | 29.2420582235 | 5.2420582235 |
| 50005 | 831 | `c63ce1017a9b0f0a1b3e1aa4666d6e0acc1328916aea189ce140ac220b0ce2ce` | 1 | 0 | 32.9711376533 | 8.9711376533 |
| 50007 | 890 | `a8a044c655151365f1ce06021c99a193876cab7e5933f53cbaf7a03f52011693` | 1 | 0 | 32.2227639388 | 8.2227639388 |

The state hash covers `step` plus exact bytes, shape, and dtype for `rho,U,V,c,N,C,uptake,Mf`. However, the
repository contains only reconstructed state hashes and summary JSON; `turnover_dev_raw.json` explicitly stores
deep summaries, not the arrays, and no checkpoint `.npz` artefact was found. Thus these are valid checkpoint
**candidates**, not yet exact serialized checkpoint inputs satisfying this mission.

## Candidate-operator audit

### 1. Global term ablations

- Frozen `lam_plus=0` is an interpretable deletion of the `m_plus -> uptake` edge, but `MCParams.lam_plus` is a
  scalar used at every grid cell. It is global, not local to A or B.
- `up_ref_zero` and `copy_disabled` are also world-global flags in `DiagEngine`.
- `MEM_NOWRITE` (`eta_w=0`) is an existing common no-new-history continuation and could be shared by all clones;
  it is not a local A/B cut.

Verdict: scientifically legible controls, but none implements `C10/C01`.

### 2. Local memory erase/standardization

`erase_core_memory` and `standardize_core_memory` change `Mf` on a disk. They destroy or replace the candidate
carrier rather than delete its readout/access edge. The existing record reports an immediate `m_plus` seam around
0.51. They cannot distinguish unavailable access from absent source state.

Verdict: local state surgery, not a local access-channel cut.

### 3. No-swap boundary replay

`NoSwapClampEngine` overwrites a radius-10-to-12 collar after every step. It writes every persistent/derived state
field on that collar: `rho,U,V,c,N,C,uptake,Mf`. The intervention is explicitly a non-conservative Dirichlet driver,
not an edge deletion. Exact far-environment isolation was shown only with the separate **global** `up_ref=0`
ablation. Existing qualification is single-target, never simultaneous dual-pair `C11`.

The mechanical record is especially important for sham interpretation:

- own-replay sham core disturbance and collar jump: exactly `0.0`;
- active reference-replay maximum collar jump: `1.8145423147669801`;
- active reference-replay maximum core disturbance: `1.8655212794863028`.

Thus the sham matches code path but not active disturbance. A crossed response could reflect broad boundary
replacement, non-conservation, temporal forcing, or the global ablation rather than loss of a local readout edge.
It also writes a new exogenous boundary trajectory, contrary to the strict no-new-history spirit of this mission.

Verdict: spatially bounded actuator, but not a mechanically interpretable local access-channel cut.

## Conditional minimal factorial (non-executable)

This design states what would be required if a pre-existing or separately authorized local edge-cut operator later
qualified. It does **not** create, implement, or authorize such an operator.

For original world `w`, deserialize one immutable deep checkpoint `S_w` four times. Freeze two disjoint target
supports `D_A,D_B` from checkpoint geometry only; diagnostic IDs/tracker outputs never enter physics. Define
`z_A,z_B in {0,1}`, where `1` means the same predeclared candidate edge is disabled only on that fixed support:

- `C00`: `(z_A,z_B)=(0,0)`; neither cut;
- `C10`: `(1,0)`; A cut only;
- `C01`: `(0,1)`; B cut only;
- `C11`: `(1,1)`; both cut.

All four must share byte-identical checkpoint arrays, scheduler step, environment, boundary, additive probe, body
state, passive tracer state, horizon, and common `eta_w=0` no-new-history continuation. Passive inheritance of the
already-present state may remain, but no exposure-dependent history term or external boundary replay may write
`Mf`. The cut must be a term-level edge deletion with zero state surgery at intervention. Each arm also requires a
computational sham twin that evaluates the same fixed masks and code path while retaining the coefficient; active
and sham therefore both have zero instantaneous state disturbance.

The fixed support is acceptable only while the corresponding tracked body stays inside it, the partner and sentinel
stay outside it, and `D_A` and `D_B` remain disjoint. Any dynamic physics mask derived from diagnostic identity or
arm-specific tracking is forbidden. A target leaving its fixed support censors the entire original world.

## Responses and full non-symmetrized causal matrix

For arm `ab`, retain separate raw future responses `Y_A^{ab}` and `Y_B^{ab}`. The primary candidate is the
predeclared time-integral of **total** uptake on the bijectively tracked entity; per-step total and specific uptake,
plus a fixed-checkpoint-mask convergence readout, remain raw diagnostics. Body/mass/geometry divergence after the
cut is a mediator and is not adjusted away.

Use loss-under-cut signs. The factor-averaged non-symmetrized matrix is

```
                         cut at A                                  cut at B
response A   D_A<-A = 1/2[(Y_A00-Y_A10)+(Y_A01-Y_A11)]   D_A<-B = 1/2[(Y_A00-Y_A01)+(Y_A10-Y_A11)]
response B   D_B<-A = 1/2[(Y_B00-Y_B10)+(Y_B01-Y_B11)]   D_B<-B = 1/2[(Y_B00-Y_B01)+(Y_B10-Y_B11)]
```

Never average A with B. Also retain all conditional effects:

- `D_r<-A|B intact = Y_r00-Y_r10` and `D_r<-A|B cut = Y_r01-Y_r11`;
- `D_r<-B|A intact = Y_r00-Y_r01` and `D_r<-B|A cut = Y_r10-Y_r11`;
- response-specific interaction `I_r = Y_r00-Y_r10-Y_r01+Y_r11`;
- directional asymmetry `D_A<-B - D_B<-A`, reported with its own interval rather than inferred from one significant
  and one non-significant cell.

The original world is the inference unit. The four current DEV worlds are mechanical development cases only and
cannot determine a probability, margin, alpha, hard cap, or prospective family.

## Competing hypotheses and identification boundaries

- **H_DIAGONAL / local direct access:** both diagonal cells exceed a frozen practical margin; crossed cells and
  interactions meet frozen equivalence bounds. For a local `lam_plus` deletion, the diagonal is partly algebraic
  and is a positive control, not evidence of individuality.
- **H_A_TO_B / H_B_TO_A:** respectively `D_B<-A` or `D_A<-B` exceeds margin after the diagonal direct effect,
  causal-latency, sham, sentinel, confinement, fusion, and tracker gates pass. The two directions remain separate.
- **H_RECIPROCAL:** both crossed cells exceed margin; symmetry is not assumed and must be tested directly.
- **H_COMMON:** both response rows move similarly after either cut, with sentinel/far-field/global diagnostics and
  timing consistent with a shared environment or common-mode path. The 2x2 matrix alone cannot distinguish this
  from two parallel crossed paths.
- **H_RELATIONAL:** one or both `I_r` exceed a frozen interaction margin while separate conditional effects meet
  the corresponding equivalence rules. Interaction alone does not distinguish synergy from floor/ceiling
  nonlinearity; raw trajectories and predeclared scale checks are required.
- **H_MANIPULATION:** active-sham imbalance, off-support immediate change, non-conservation beyond the declared
  edge, body/support escape, fusion, tracker ambiguity, or premature far-field/global response. No causal-state
  interpretation survives this hypothesis.
- **H_NULL:** every matrix/interaction cell meets a prospective equivalence bound. Non-significance alone never
  establishes this.

Even a clean crossed cell establishes a directed total effect through the intact shared world, not a direct
member-to-member wire. It can be mediated by the environment. A single candidate edge tests access through that
edge only; it cannot establish storage location, ownership, identity, life, or active reconstruction.

## Minimum closed raw schema

The raw contract must contain no derived effect, interaction, classifier, or hypothesis verdict. At minimum:

1. **Provenance:** schema/version, mission/mode, code commit and file hashes, checkpoint-manifest hash, operator and
   test hashes, exact allowed DEV IDs, no prospective namespace, platform, and complete command.
2. **Checkpoint:** immutable path, file SHA-256, state-content SHA-256, `step`, dtype/shape and per-field hashes for
   `rho,U,V,c,N,C,uptake,Mf`, serialization round-trip equality, and no persistent RNG/hidden-buffer declaration.
3. **Pair:** frozen outcome-blind A/B/sentinel indices, orientation and selection rule, deep-turnover evidence,
   initial masks/weighted centroids, pair distance/halo gap, and support-mask hashes.
4. **Clone equality:** exact per-field and clock errors for all four clones before intervention; common
   environment/body/boundary/probe hashes.
5. **Arm:** `C00/C10/C01/C11`, explicit cut booleans, sham identity, coefficient/support hashes, intended and actual
   changed-term support, no state-surgery hash, and no-write configuration.
6. **Every step:** state/field hashes; A/B/sentinel component masks, weighted centroids, size/mass/coverage;
   pair distance and halo overlap; every tracker candidate edge and individual gate; split/merge/loss/ambiguity;
   support containment and wrong-body intersection; finite values; global scalar and field totals; inside,
   one-cell, near, far, partner, and sentinel disturbance norms; causal-cone timing; active-sham numerical deltas.
7. **Responses:** raw per-step `Y_A` and `Y_B` numerators/denominators and fixed-mask convergence values in a
   separately sealed outcome payload. The mechanical validator may hash that payload but may not open it.
8. **Gate disposition:** per-arm and whole-original-world mechanical booleans, earliest failure, and exact reasons.
   Only a complete engine-free validator success may release the outcome payload to a separate analyzer.

## Kill switches

Fail closed before outcomes if any of the following occurs:

1. an exact serialized checkpoint is absent, hash-mismatched, not round-trip exact, or not the declared deep step;
2. any clone differs in any state byte or clock before intervention;
3. the continuation writes new exposure-dependent history (`eta_w != 0`) or an external driver overwrites `Mf`;
4. the alleged local cut is a global scalar change, carrier erasure/replacement, tracker/ID-controlled physics,
   boundary replay, or multi-field state surgery rather than the frozen edge deletion;
5. A/B supports overlap, touch the wrong body/sentinel, or differ across arms; the cut target exits its fixed
   support; or `C11` does not equal the exact disjoint composition of the two local toggles at the first update;
6. active and sham differ at intervention in any state array, or an immediate update change appears outside the
   declared support/one-step causal closure;
7. any unaccounted global/common-mode response precedes the physical causal latency;
8. either entity or sentinel becomes non-viable, fuses, splits, merges, is lost/ambiguous, crosses the separation
   threshold, overlaps halos/supports, or fails tracker-independent convergence in any arm;
9. any arm is absent: invalidity is at the original-world level, never repaired by selecting a surviving subset;
10. any `Y`, contrast, interaction, margin, or outcome-bearing diagnostic is opened before the mechanical validator
    passes the complete four-arm record;
11. any prospective namespace, seed, V5/03G, or `58xxx` artefact is touched.

## GO / REVISE / STOP rule

- **GO (human mechanical review only):** exact serialized checkpoints exist; an already-existing local edge cut and
  exact sham satisfy all confinement/composition/pair gates on the fixed DEV set; the four-arm raw chain reproduces
  engine-free; outcomes remain sealed. GO still authorizes no prospective family.
- **REVISE:** only a non-scientific packaging/serialization/schema defect remains and the operator identity and
  already-demonstrated localization do not change. A new or materially altered intervention is not a revision.
- **STOP-LOCAL-CUT:** no existing operator is both local and mechanically interpretable; achieving localization
  requires a new spatial engine term, an external replay/writer, a global ablation, carrier destruction, or
  tracker-controlled physics.

## OBSERVED

- `DIRECTED-CAUSAL-PAIR-00` Phase 0.5 failed its frozen history-writer viability gate in all four worlds before a
  common history-bearing deep step; pair `Y/C/I` were not exposed.
- This distinct mission requires an already-serialized, already-open deep state and no history writer.
- Four already-open deep pair candidates exist and have content hashes, but no exact serialized checkpoint file.
- No current operator implements a target-local readout edge deletion. The broad no-swap actuator fails the strict
  local-channel and disturbance-matched-sham interpretation required here.

## INFERRED

The factorial is scientifically identifiable only if at least one existing cut changes a declared candidate
access edge inside one entity while leaving the partner, common environment, body, probe, boundary, and clock
matched. That precondition is not met. Rebranding the collar writer as a local cut would confound the result with
boundary forcing and violate the user's explicit fail-closed rule.

## HYPOTHESIS

If a genuinely target-local term deletion existed, crossed cells of the non-symmetrized matrix could reveal
directional access after direct diagonal and shared-environment explanations were separated. The repository does
not currently contain that operator.

## WHAT WOULD FALSIFY THIS?

No exact serialized checkpoint contains a continuously tracked, separated, viable deep-turnover pair; or every
candidate cut changes global/common state, alters body viability, creates an unmatched seam, crosses the pair
boundary, or lacks a matched sham. Either condition requires `STOP-LOCAL-CUT` for Phase 0.

## Failures and dead ends

- PowerShell `ConvertFrom-Json` rejected the mechanical JSON because state dictionaries contain both `C` and `c`;
  standard-library Python was used for key/whitelist extraction. This did not expose outcome values.
- State hashes are not substitutes for exact serialized checkpoint inputs.

## Decisions

- Treat the history-writer stop as final and orthogonal to the no-writer checkpoint question.
- Fail closed before outcome access; operator qualification must precede any readout computation or inspection.
- Independent Phase-0 disposition: **STOP-LOCAL-CUT**. Do not invent a local lambda field, dual boundary driver, or
  dynamic tracker-controlled support in this mission.

## Unresolved risks

- The precise semantics of "no new history" should be frozen before any later design: this audit uses the strict
  existing `eta_w=0` continuation while allowing passive copying of already-present `Mf` onto new mass.
- A future local `lam_plus` cut would make its diagonal uptake effect partly algebraic; only crossed effects after
  causal latency address directed pair access.
- Fixed supports preserve diagnostic-ID independence but censor motion; dynamic supports risk treatment
  endogeneity and diagnostic information entering physics.
- Four DEV worlds cannot set inference margins, a hard cap, or a prospective family.

## Handoff

Return **STOP-LOCAL-CUT** for Phase 0. Preserve the four checkpoint candidates and the conditional factorial as a
non-executable design record. Exact next authorized action, if the user later opens a distinct mission, is human
choice about whether to authorize development of a term-level local readout cut and exact checkpoint serialization;
that would be a new operator project, not continuation or rescue of this audit.
