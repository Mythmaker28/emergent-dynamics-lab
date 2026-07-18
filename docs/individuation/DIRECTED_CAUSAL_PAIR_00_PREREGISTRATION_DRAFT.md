# DIRECTED-CAUSAL-PAIR-00 — draft preregistration

Status: **PHASE-0 DRAFT — NOT SEALED — NOT AUTHORIZED — NO PROSPECTIVE FAMILY OPENED**
Parent: `7deeb8e0bd4ac972e1dd133fc8992fcfc4f2fb2b`
Recommendation: **REVISE before any prospective preseal**

This draft asks whether two naturally formed, spatially separated, non-fusing droplets can be treated as two causal
individuals. It does not define individuality by a successful result. It fixes the unit, interventions, outcomes,
censoring logic, and directed estimands needed for a later preregistration. No seed family, hard cap, effect margin,
or prospective authorization is created here.

## 1. Scientific unit and scope

The statistical unit is the **original world**. Targets A and B, the sentinel target, the four history clones,
access-regime clones, time points, and reciprocal directions are repeated measurements nested within that world.
They are never counted as independent samples.

The primary outcome is the already-qualified, per-target integrated uptake under the corrected common probe:

- set `N := N0` exactly;
- settle 40 steps;
- apply a uniform `N += 0.25` for steps 1–5;
- integrate uptake on the component followed by the frozen bijective tracker through step 40;
- retain fixed-mask uptake only as a convergent control.

Body size, `rho` mass, centroid motion, pair separation, halo overlap, and geometry are possible mediators of the
history intervention. They are recorded and reported but are **not regression covariates in the primary total-effect
analysis**.

## 2. Eligibility and pair assignment

Eligibility is evaluated before any writer is applied:

1. the ordinary warm world contains at least three targets accepted by the unchanged 03G detector/selection rules:
   size at least 45 and greedy pairwise toroidal centroid separation at least 24;
2. choose one unordered pair by maximum initial toroidal centroid separation, with ties resolved by ascending frozen
   target index;
3. use the remaining target as a sentinel, not as another statistical unit;
4. orient the selected pair without an outcome: even `original_world_id` gives ascending target indices A/B, odd
   gives descending A/B;
5. diagnostic target indices may label records but may not enter physics, detection, tracker association, or an
   association gate.

The selected pair may never be replaced by another pair after histories, turnover, geometry changes, clamp failure,
or probe results. A failure censors the entire original world across all arms.

## 3. Exact-clone history factorial

At the common prewriter state, serialize the complete persistent state (`rho,U,V,c,N,C,Mf,uptake,step`) and create
four byte-audited clones:

| Arm | writer at A | writer at B |
|---|---:|---:|
| `H00` | 0 | 0 |
| `H10` | 1 | 0 |
| `H01` | 0 | 1 |
| `H11` | 1 | 1 |

All four prewriter hashes must be identical. The writer is the existing 03G local Gaussian nutrient writer only:
two 60-step phases, Gaussian centred on the prewriter target, `sigma=max(3,0.8*rg)`, with each phase amplitude drawn
from the unchanged uniform range `[0.005,0.035]`.

Exactly one amplitude pair `(a1,a2)` is drawn per original world from a separately sealed, pair-outcome-blind writer
stream. The same pair is used for A and B. Every arm executes the same loops and array expressions
`N += h_A*a_phase*patch_A + h_B*a_phase*patch_B`; the history bits alone differ. Thus treated-target dose and
floating-point work are matched between A and B. `H11` necessarily contains two treated targets and is not relabelled
as a dose-matched single-target arm.

No pair feeding response, future geometry, or target survival may select the amplitude pair. The future preseal must
bind the writer stream without inspecting its values.

## 4. Deep turnover and common time

All arms run under ordinary coupling after the writer. A separate `H00` reference continuation determines the
original world's common deep-turnover step by the unchanged 03G turnover rule. The same step is then used in every
history arm. The step is not selected separately in response to each arm.

At that step every target must remain distinct and must satisfy the frozen deep-turnover rule. `P(tau)` and `M(tau)`
are stored jointly for each target. They are never replaced by `P*(1-M)`, `theseus_score`, `memory_score`, or another
composite. Failure by A, B, the sentinel, or any essential clone censors the whole world.

## 5. Access-regime clone set

From every valid deep history arm, branch exact clones into:

- `ORDINARY`: unchanged coupling;
- `OWN_REPLAY_SHAM_A` and `OWN_REPLAY_SHAM_B`: target-specific own-replay wrapper, required to be bit-exact with
  ordinary continuation;
- `REFERENCE_NOSWAP_A` and `REFERENCE_NOSWAP_B`: one recipient at a time, radius-10 core, ring `10 < d <= 12`,
  outcome-independent `H00` reference replay; no simultaneous dual clamp is required;
- `UP_REF_ZERO`: existing `up_ref=0` ablation only;
- `REFERENCE_NOSWAP_A_UP_REF_ZERO` and `REFERENCE_NOSWAP_B_UP_REF_ZERO`: recipient cut plus global-channel ablation.

The no-swap wrapper must preserve scheduler step, engine parity, persistent fields, and external tracker rules. The
reference replay is built without A/B pair outcomes. The common corrected probe is identical in every access regime.

## 6. Directed estimands

Let `Y_i^r(ab)` be the integrated tracked uptake of recipient `i in {A,B}` in access regime `r`, with history bits
`a` at A and `b` at B. Define `C_ij` with **row = recipient/outcome** and **column = written source**:

```text
C_AA^r = 1/2 [(Y_A^r(10)-Y_A^r(00)) + (Y_A^r(11)-Y_A^r(01))]
C_AB^r = 1/2 [(Y_A^r(01)-Y_A^r(00)) + (Y_A^r(11)-Y_A^r(10))]
C_BA^r = 1/2 [(Y_B^r(10)-Y_B^r(00)) + (Y_B^r(11)-Y_B^r(01))]
C_BB^r = 1/2 [(Y_B^r(01)-Y_B^r(00)) + (Y_B^r(11)-Y_B^r(10))]
```

`C_AB` is therefore B→A; `C_BA` is A→B. They are never pooled or assumed equal. The per-recipient interaction is:

```text
I_A^r = Y_A^r(11) - Y_A^r(10) - Y_A^r(01) + Y_A^r(00)
I_B^r = Y_B^r(11) - Y_B^r(10) - Y_B^r(01) + Y_B^r(00)
```

Primary total effects are `C^ORDINARY` and `I^ORDINARY`. Channel diagnostics are:

- spatial/environment attenuation into recipient A: `C_Aj^ORDINARY - C_Aj^REFERENCE_NOSWAP_A`;
- spatial/environment attenuation into recipient B: `C_Bj^ORDINARY - C_Bj^REFERENCE_NOSWAP_B`;
- global attenuation: `C_ij^ORDINARY - C_ij^UP_REF_ZERO`;
- residual with both routes cut: recipient-matched `REFERENCE_NOSWAP_*_UP_REF_ZERO` matrix;
- clamp artefact: `C^OWN_REPLAY_SHAM_i - C^ORDINARY`, required to be numerically null before inference.

The sentinel outcome is a diagnostic for world-global or diffuse contamination; it is not a third row/column in the
primary pair matrix and not another sample.

## 7. Hypotheses and discriminating patterns

The hypotheses are not forced to be mutually exclusive. Exact nonzero/equivalence margins and multiplicity control
must be frozen by a power/preseal step before prospective authorization.

| Hypothesis | Predeclared diagnostic pattern |
|---|---|
| `H_I` — two individuated local carriers | positive diagonal total effects with off-diagonal effects inside frozen equivalence margins; diagonals survive recipient no-swap and `up_ref=0` |
| `H_ENV` — local environment mediates influence | an ordinary cross effect is attenuated by the corresponding recipient no-swap cut beyond its sham envelope; combined no-swap+`up_ref=0` leaves no unexplained cross effect |
| `H_PAIR` — directed pair coupling | at least one off-diagonal effect survives `up_ref=0`, is localized to the selected pair rather than the sentinel, and changes under the recipient no-swap cut |
| `H_ASYM` — directional asymmetry | the world-level contrast `C_AB-C_BA` differs from the frozen zero/equivalence region; no direction is chosen post hoc |
| `H_REL` — non-additive relational state | `I_A` and/or `I_B` exceeds its frozen interaction margin and is not explained by sham, global, or clamp-contamination diagnostics |
| `H_GLOBAL` — world-global channel | pair and sentinel effects co-move and materially collapse under `up_ref=0`; recipient-specific no-swap alone does not explain the collapse |
| `H_0` — no detectable directed causal pair effect | all four ordinary matrix entries and both interactions are inside frozen null/equivalence regions, with valid manipulation and probe controls |

A clean diagonal is evidence for target-local causal persistence, not metaphysical ownership. A nonzero off-diagonal is
evidence for directed influence, not automatically a relational individual. `H_REL` requires the factorial
interaction plus channel controls.

## 8. Analysis and no pseudoreplication

For each original world, compute the complete vector
`(C_AA,C_AB,C_BA,C_BB,I_A,I_B)` in each access regime. World-level vectors are the only inputs to confidence
intervals, randomization tests, or bootstrap intervals. No target-level, arm-level, or time-point-level row is fed to
an analysis as an independent observation.

Primary reports include:

1. the four non-symmetrized ordinary-coupling matrix entries;
2. `C_AB-C_BA` without averaging reciprocal directions;
3. both interaction effects;
4. no-swap, `up_ref=0`, combined-cut, own-replay, fixed-mask, and sentinel diagnostics;
5. unadjusted total effects together with, but never conditioned on, mass/geometry/halo mediator summaries;
6. contamination trajectories for residual `N`, `up_ref`, clamp barrier jumps, and outside-target field changes.

The confirmatory rule remains **unsealed** because Phase 0 has no independently justified effect/equivalence margin
for the directed matrix. A future preseal must derive operating characteristics without viewing prospective pair
outcomes and must specify simultaneous-error handling across the four matrix entries, two interactions, and the
single asymmetry contrast.

## 9. Whole-world gates and kill switches

The following are fail-closed:

1. **Outcome-independent eligibility:** any evidence that pair choice, orientation, writer draw, deep time, or clamp
   reference used pair feeding results invalidates the family.
2. **Exact clone:** any prewriter clone hash mismatch invalidates that original world; systematic mismatch stops the
   family.
3. **Target/tracker identity:** any diagnostic ID entering physics/detection/association, or any unlogged alternative
   association edge/gate term, stops the family.
4. **No fusion/switching:** `MERGED`, `SPLIT`, `LOST`, `AMBIGUOUS`, component switch, non-bijective assignment, fewer
   than three distinct live targets, or coverage at least 0.15 in any essential arm censors the whole world.
5. **Separation/halo:** A–B toroidal centroid distance below 24 or any overlap of the two radius-12 halo masks at any
   recorded step censors the whole world. No alternative pair is substituted.
6. **Reciprocity:** missing H10/H01, missing recipient-A/B access arm, or accidental `C_AB=C_BA` symmetrization stops
   analysis.
7. **Sham equivalence:** own-replay must be byte-identical to ordinary continuation. Any nonzero state difference is
   a mechanical failure, not an effect to subtract.
8. **Dose/numerics:** A and B must receive the identical per-target schedule and every history arm must execute the
   same loop/array-operation count. A mismatch invalidates the world.
9. **Deep turnover:** all three targets in all four history arms must pass the frozen joint P/M turnover gate at the
   common H00-derived step.
10. **Common probe:** any change from `N:=N0`, settle 40, uniform 0.25 for 5, horizon 40, or bijective tracker rules
    invalidates the family.
11. **No pseudoreplication:** counting targets, arms, directions, or steps as independent worlds invalidates the
    analysis.
12. **No post-outcome selection:** no world/target/arm may be dropped because of the magnitude or sign of Y, C, or I.
13. **Minimum valid worlds:** fewer than 18 whole valid original worlds at a separately frozen hard cap yields
    `FEASIBILITY_FAIL / SCIENTIFIC QUESTION UNANSWERED`, not a negative result. Eighteen is inherited as a structural
    minimum from 03G; it is not claimed as a completed power justification for this new matrix.
14. **Mechanical feasibility fail:** no prospective authorization until a fresh DEV-only qualification demonstrates
    the entire pair-context H00/H10/H01/H11 clone construction, history-bearing recipient no-swap/sham arms,
    per-step separation/halo logging, and valid probe continuations without reading pair feeding contrasts.

## 10. Raw evidence requirement

The draft minimum schema is
`docs/individuation/DIRECTED_CAUSAL_PAIR_00_RAW_SCHEMA_DRAFT.json`. It requires exact clone/state hashes, writer
execution, joint P/M trajectories, raw descriptors, all association alternatives and gate terms, pair geometry,
halo overlap, global/local contamination channels, clamp diagnostics, probe outcomes, and mediators. It deliberately
does not add a generic feature battery, decoder, reader, or composite identity score.

## 11. Authorization boundary and exact next action

This draft authorizes no new seed, seed-family inspection, seed reservation, prospective run, or V5/03G modification.
The exact next authorized action is one DEV-only, outcome-blind mechanical qualification on the already-open 500xx
worlds that writes no Y/C/I contrasts and closes kill switch 14. Only after review may a separate preseal freeze
effect margins, multiplicity, platform, seed family, hard cap, manifests, and human authorization.
