# FCDDH00 — FRESH_CROSSED_DIFFERENTIAL_DISCOVERY_HOLDOUT_00 — MASTER FREEZE

**Status of this file: PRE-NUMERICAL.** It is written and committed before any detailed
historical numerical array is loaded, before any new state is generated, before any candidate is
constructed and before any engine is started. It is the binding contract for the whole
programme. Nothing below may be changed after Commit 1; later commits may only *resolve* the
identifiers this file declares must be resolved, and may never redefine an estimand, a gate, a
threshold, a budget or a claim.

---

## 0. Identity of this programme

| field | value |
|---|---|
| NEXT_PROGRAM | FRESH_CROSSED_DIFFERENTIAL_DISCOVERY_HOLDOUT_00 |
| SHORT_NAME | FCDDH00 |
| BRANCH | `dev/fresh-crossed-differential-discovery-holdout-00` |
| WORKDIR | `/home/claude/sweep/FCDDH00` (cloud execution container) |
| REPO | `emergent-dynamics-lab` working copy at `C:\Users\tommy\Documents\ising v3` |
| OWNER | Tommy |
| AUTHORIZATION | the owner-sent handoff prompt, verbatim, in `OWNER_AUTHORIZATION_VERBATIM.txt` |
| AUTHORIZATION_SHA256 | `9dcdd47aaaf4482a349ee95a0f89f061516e8a199cb77911c0345e9eff011169` |
| AUTHORIZATION_BYTES | 68666 |
| PROGRAMME_TYPE | PROSPECTIVE_SEQUENTIAL_DISCOVERY_THEN_HOLDOUT |
| EXECUTION_MODE | ONE_EXECUTOR_SEQUENTIAL |
| PARALLEL_AGENTS_AUTHORIZED | 0 |
| PARALLEL_REVIEWERS_AUTHORIZED | 0 |
| PUSH_AUTHORIZED | false |
| DRAFT_PR_AUTHORIZED | false |
| WORKFLOW_TRIGGER_AUTHORIZED | false |
| TOMMY_ACTION_REQUIRED | false |
| TOMMY_GIT_ACTION_REQUIRED | false |
| FREEZE_WRITTEN_UTC | 2026-08-11T03:57Z |

### 0.1 Resolved Git identifiers (metadata resolution only — no content decoded)

Resolved from the committed object database of the working repository, by
`git rev-parse` / `git log` / `git merge-base` only.

| reported | resolved full object |
|---|---|
| DIRECT_PARENT_REPORTED_TIP `334b7c2b` | commit `334b7c2ba6d97dadb403c7a1ea9700a1c61ad512` |
| — its root tree | `b36f821850a970c6cbb6a29ca539b3a99bbd5d8c` |
| DIRECT_PARENT_REPORTED_SUBTREE `b43e0498` | tree `b43e04983e6a3cbf31b6ccc84b5267fbe17b1ad2` (`334b7c2b:FCRA00`) |
| DIRECT_PARENT_REPORTED_BUNDLE_SHA256 `95ef4511` | `95ef451164d31bea9b16b94e6d86aadad40c696a308e007e9955b1e506ae2e3b` |
| FSQBT00_REPORTED_TIP `b3f45ac7` | commit `b3f45ac7781e0dd48f34886b7c63840af520d502`, tree `6c362f8acb4a80da8769986129a6ea0af58f099d` |
| SQDT00_REPORTED_TIP `16717582` | commit `16717582e7f0dfd371f21c56465e11113d8b6675`, tree `6b3e8650eb62d31380c705944756e4211d20bdae` |
| FWL2CF00_REPORTED_SOURCE | commit `96c7d295e72106cd949d810fa92807c2514e7449`, tree `626dfe3278748b62495f4a90eaa61183770f2d82` |
| TOMMY_MAIN_REPORTED `f3921a4d` | commit `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`, tree `8672babd1bc11d5912cf4820b06fa5947ebcd04b` |

Ancestry verified by `git merge-base --is-ancestor`:
`96c7d295 ≺ 16717582 ≺ b3f45ac7 ≺ 334b7c2b`. `main` (`f3921a4d`) is **not** an ancestor of the
dev chain and must remain at `f3921a4d…` untouched, unchecked-out and unmerged for the whole
programme. HEAD of the working copy is `refs/heads/main`; FCDDH00 is created and advanced by
**lock-free plumbing only** (`GIT_INDEX_FILE` in a scratch index, `write-tree`, `commit-tree`,
direct ref write). `main` is never checked out as a work branch and never written.

### 0.2 Owner-reported FCRA00 facts — what was known BEFORE any FCDDH00 outcome

These are bound here, verbatim, as prior knowledge. They are **owner-reported facts to verify**,
not substitutes for byte-level provenance; Commit 2 verifies them against committed bytes and
records any discrepancy without amending the parent.

```
FSQBT00_PRIMARY_RECOMPUTATION_STATUS          = PASS
FSQBT00_CELL_MATERIALITY                      = 24_OF_24
FSQBT00_DIRECT_CARRIER_CONTRAST_MAGNITUDE     = 12_OF_12
FSQBT00_PARENT_E2_SIGN_CONCORDANCE            = 10_OF_12
FROZEN_P2_TRANSFER_AS_FROZEN                  = NOT_TRANSFERRED
P2_POPULATION_TRANSFER_INTERPRETATION         = INCONCLUSIVE_FROM_THIS_GATE_ALONE
FCRA00_REPORTED_GAUGE_STRUCTURE               = UNIQUE_OR_BLOCK_SEPARABLE__VERIFY_FROM_BYTES
OUTSIDE_P2_INTERCEPT_FRACTION                 = 0.028
OUTSIDE_P2_COMMON_CENTERED_FRACTION           = 0.309
OUTSIDE_P2_CARRIER_DIFFERENTIAL_FRACTION      = 0.663
FCRA00_DIFFERENTIAL_INTERNAL_LOAO_PREDICTION  = 12_OF_12
FCRA00_DIFFERENTIAL_INTERNAL_MIN_ALIGNMENT    = APPROX_0.995
FCRA00_DIFFERENTIAL_DX2_ABSOLUTE_MATERIALITY  = FAIL
FCRA00_DIFFERENTIAL_DX3_ALLOCATION_ROBUSTNESS = FAIL
FCRA00_DISCOVERY_DIRECTION_STATUS             = M0_NO_UNIQUE_DIRECTION_LICENSED
FCRA00_SERIALIZED_DIRECTION                   = NONE
FSQBT00_PROTOCOL_CONFORMITY = NONCONFORMANT__ONE_UNAUTHORIZED_DIAGNOSTIC_START__NO_OUTCOME_OPENED_PROVEN
FSQBT00_ORIGINAL_TIP_DELIVERY_STATUS          = INCOMPLETE_MISSING_FULL_CHECKPOINT_BYTES
CURRENT_CHILD_CHAIN_EVIDENCE_STATUS           = COMPLETE_AFTER_APPEND_ONLY_RECOVERY
FCRA00_ENGINE_STARTS                          = 0
```

Explicitly recorded as known beforehand: the outside-P2 anatomy is **2.8 % intercept /
30.9 % common-centred / 66.3 % carrier-differential**; the historical carrier-differential
NEAR−FAR direction was internally coherent (12/12 LOAO, min squared alignment ≈ 0.995) but
**failed** DX2 (absolute materiality) and DX3 (allocation-orbit robustness); therefore **no
historical direction was serialized and none may be resurrected here**. 12/12 was a *direct
carrier-contrast magnitude* count, never an e2 *direction* count; the e2 sign agreement was
10/12; three of twelve blocks exceeded the frozen P2 tube, so the old strict gate remains
failed; that tube was the maximum of only four calibration folds, so the gate alone does not
establish population non-transfer.

**Role of the twelve historical FSQBT00 blocks in FCDDH00:** they justify, before any new
outcome, exactly one hypothesis class — *carrier-differential NEAR-minus-FAR residual outside
immutable parent P2*. No vector, mean, gauge, midpoint, score, coefficient or fitted object
from those twelve blocks may enter the new axis or its validation. This is enforced
structurally by the dependency firewall (Section 8) and audited by gate D11.

---

## 1. Scientific questions, frozen

**Primary.** On wholly new upstream ancestries where manipulated NEAR/FAR geometry and the
two-member complementary-allocation orbit are **crossed within every ancestry**, can a
carrier-differential direction learned by one fixed algorithm on a fresh 12-ancestry discovery
panel predict a prospective, never-refitted NEAR−FAR × carrier interaction on an untouched
16-ancestry hold-out panel?

**Orthogonal 1.** Is the fixed-direction interaction *absolutely material* in the inherited
weighted-L2 response units, rather than merely directionally coherent?

**Orthogonal 2.** Is it *uniform across the allocation orbit*, or present only after averaging
over the two neutral allocation members?

**Orthogonal 3.** What does the immutable parent-P2 residual distribution look like under a
*population-oriented* estimand, without reclassifying or weakening the old strict max-of-four
containment gate?

---

## 2. Canonical field schema (frozen, exact names)

Every JSON, decision table, manifest and report emitted by FCDDH00 uses **exactly** these field
names, no more, no fewer, no renames, no duplicates. The pre-analysis oracle (Q0W) rejects a
missing, renamed or duplicate field.

```
FCDDH00_PROVENANCE_STATUS
FCDDH00_G1_STATIC_ELIGIBILITY
FCDDH00_PREANALYSIS_ORACLE_STATUS
FCDDH00_RANDOMIZATION_LICENSE
PROTOCOL_CONFORMITY_STATUS
RAW_EVIDENCE_COMPLETENESS_STATUS
ENGINE_START_LEDGER_STATUS
DISCOVERY_CONSTRUCTION_STATUS
DISCOVERY_SHAM_STATUS
DISCOVERY_RAW_ACTIVE_STATUS
DISCOVERY_PANEL_STATUS
DISCOVERY_CELL_MATERIALITY_STATUS
DISCOVERY_DIRECT_CARRIER_CONTRAST_STATUS
DISCOVERY_AXIS_IDENTIFIABILITY_STATUS
DISCOVERY_AXIS_STABILITY_STATUS
DISCOVERY_INTERACTION_ABSOLUTE_MATERIALITY_STATUS
DISCOVERY_ALLOCATION_ORBIT_ROBUSTNESS_STATUS
DISCOVERY_AXIS_SERIALIZATION_STATUS
HOLDOUT_CONSTRUCTION_STATUS
HOLDOUT_SHAM_STATUS
HOLDOUT_RAW_ACTIVE_STATUS
HOLDOUT_PANEL_STATUS
HOLDOUT_CELL_MATERIALITY_STATUS
HOLDOUT_DIRECT_CARRIER_CONTRAST_STATUS
HOLDOUT_FIXED_AXIS_DIRECTIONAL_REPLICATION_STATUS
HOLDOUT_FIXED_AXIS_RANDOMIZATION_STATUS
HOLDOUT_ALLOCATION_AVERAGED_DIRECTION_SECONDARY_STATUS
HOLDOUT_INTERACTION_ABSOLUTE_MATERIALITY_STATUS
HOLDOUT_ALLOCATION_ORBIT_ROBUSTNESS_STATUS
FSQBT00_LEGACY_STRICT_MAX4_ALL_BLOCK_CONTAINMENT_STATUS
P2_HOLDOUT_DESCENDANT_SCORE_STATUS
P2_HOLDOUT_DESCENDANT_EXCEED_COUNT_OF_64
P2_HOLDOUT_ALL4_ANCESTRY_COUNT_OF_16
P2_HOLDOUT_GENERATOR_INTERVAL_LICENSE
P2_POPULATION_TRANSFER_INTERPRETATION
DISCOVERY_CONSTRUCTION_STARTS
DISCOVERY_SHAM_STARTS
DISCOVERY_ACTIVE_STARTS
HOLDOUT_CONSTRUCTION_STARTS
HOLDOUT_SHAM_STARTS
HOLDOUT_ACTIVE_STARTS
OTHER_STARTS
TOTAL_CHARGED_STARTS
TOTAL_RAW_ADVANCE_SEQUENCES
```

Orthogonality rule, frozen: **no positive field may overwrite a negative field, and no negative
gate may erase a positive material response.** The following combinations are legal and must be
reported as such rather than compressed: directionally replicated but below absolute
materiality; replicated on the allocation-averaged estimand but not uniform over the orbit;
absolutely material but not prospectively replicated; old strict P2 containment failed while
its population exceedance rate remains uncertain; all cells materially responsive while the
targeted interaction is absent.

---

## 3. Units, panels and hard start budget

The **only** independent unit is one upstream ancestry block. Within a block the four
descendants, two carriers, two channels, sites and scored times are *repeated conditions*.

```
DISCOVERY_INDEPENDENT_UNITS        = 12    DISCOVERY_DESCENDANTS_PER_BLOCK = 4   ACTIVE_ROWS/BLOCK = 8
HOLDOUT_INDEPENDENT_UNITS          = 16    HOLDOUT_DESCENDANTS_PER_BLOCK   = 4   ACTIVE_ROWS/BLOCK = 8
TOTAL_NEW_INDEPENDENT_UNITS_IF_ELIGIBLE = 28
TOTAL_NEW_DESCENDANTS_IF_ELIGIBLE       = 112
TOTAL_NEW_ACTIVE_ROWS_IF_ELIGIBLE       = 224
```

Sample sizes are **frozen for design reasons, not fitted to the FCRA00 effect**. Twelve
discovery ancestries support the inherited 10/12 leave-one-ancestry qualification. Sixteen
hold-out ancestries make 12/16 the first robust success count, with one-sided fair-sign tail
2517/65536 = 0.0384063720703125 and ≈ 0.798 power at the *explicit design reference*
P(block success) = 0.80 — a design reference, not an estimate from FCRA00. These are planning
references, inferential only under the separately stated sampling / null licenses. **The
hold-out is never extended after observing outcomes.**

Every complete block contains exactly:

```
g ∈ {NEAR, FAR}                 manipulated geometry
a ∈ {0, 1}                      neutral H3 complementary-allocation orbit (unordered; 0/1 has no physical sign)
o ∈ {CARRIER_1, CARRIER_2}      the two historical 1× carriers
d = the unique descendant for each (block, g, a)
```

### 3.1 Hard maxima (never exceeded, never extended)

| phase | construction / qualification | shams | active | hard maximum |
|---|---|---|---|---|
| discovery (12 blocks / 48 descendants) | 96 | 96 | 96 | 288 |
| hold-out (16 blocks / 64 descendants) | 128 | 128 | 128 | 384 |
| complete eligible programme | 224 | 224 | 224 | **672** |

```
OTHER_OR_DIAGNOSTIC_STARTS_AUTHORIZED = 0
POST_PANEL_SHAM_RETRIES_AUTHORIZED    = 0
ACTIVE_RETRIES_AUTHORIZED             = 0
REPLACEMENT_AFTER_FIRST_SHAM          = false
REPLACEMENT_AFTER_FIRST_ACTIVE_BYTE   = false
```

### 3.2 Charging convention (frozen)

```
C_BLOCK_ACTUAL = C_PRECURSOR_ADVANCE
               + C_NEAR_A0_DESCENDANT_ADVANCE + C_NEAR_A1_DESCENDANT_ADVANCE
               + C_FAR_A0_DESCENDANT_ADVANCE  + C_FAR_A1_DESCENDANT_ADVANCE
               + every separately state-advancing qualification operation
PHASE_CONSTRUCTION_CHARGE = C_SETUP_ACTUAL + Σ_attempted C_BLOCK_ACTUAL
```

* Any term implemented inside one process still contributes **one raw advance sequence** when it
  independently advances state.
* **Charge the larger of fresh process starts and raw advance sequences.**
* A candidate that advances a precursor and three descendants before the fourth fails is
  rejected and charged for the precursor plus those three advances; the missing fourth branch is
  not charged and the candidate is **never resumed**.
* A pure hash / read / static check costs **zero**.
* Every setup that instantiates *and advances* physics, every failed candidate, every rejected
  complete block, every crash after launch, every timing probe, smoke test and diagnostic
  continuation is charged. **There are no uncharged engine probes.** No timing probe or smoke
  test will be run in this programme; the runner cost is derived statically from the exact
  committed code.
* A transport failure may be retried **only** when an idempotency record proves that no engine
  was instantiated and no state advanced. Otherwise the start is charged, not replayed, and the
  affected panel closes as incomplete.

Three worked examples are persisted in `ENGINE_START_BUDGET_AND_WRITEAHEAD_SPEC.md`
(pre-launch transport failure; uncertain launch; complete block).

### 3.3 Frozen, unchangeable objects

No change is authorized to: `LAWSPEC`, `ENGINE_EQUATIONS`, `STATE_VARIABLES_OR_TRACERS`,
`FOUNDER_GENERATOR`, `SETTLE_RULE_OR_CHECKPOINT_TIME`, `FIXED_SUPPORT_MASKS`,
`READER_OR_NORMALIZER`, `HORIZON_SCORED_TIMES_OR_WEIGHTS`, `BOUNDARY_OR_SCHEDULER`,
`CARRIER_1_OR_CARRIER_2_EXECUTABLE`, `CARRIER_PARAMETERS_APPLICATION_TIME_DOMAIN_OR_TOUCHSET`,
`CARRIER_DOSE_1X`, `PARENT_MU_P1_P2_E1_E2_OR_TUBE`, `MATERIALITY_SEMANTICS`.

Specifically forbidden: a third carrier; any dose search; repeated involution as a fake dose;
new PCA/P3; fresh quotient selection; nonlinear classifier; new mask; new window; selected
subset; threshold lowering; response/TAU normalization; off-support/full-field endpoint
analysis; and any further fit on the twelve FSQBT00 blocks. The recovered historical full-field
bytes may be used **only** to verify provenance and evidence completeness — never as a readout.

---

## 4. The G1 within-ancestry crossed route (frozen)

Only the existing **semantics-preserving G1 complete-factorial route** is used. If it cannot be
reproduced without new engine semantics, the programme stops before construction with
`WITHIN_ANCESTRY_G1_NOT_FREEZABLE__ZERO_STARTS`. **No G2 observational substitute is permitted.**

### 4.1 Frozen construction contract

For an upstream ancestry seed `S`, the **upstream precursor** is

```
PRECURSOR(S) = edlab.experiments.sc_mcm.config.seed_state(SPEC, TRACER, S, "random")
```

a pure function of `S` alone: it draws from `numpy.random.default_rng(S)` and performs **zero
engine advances**. It is therefore byte-identical for all four descendants of the block, and it
is independent of geometry and of allocation. Its bytes and hash are persisted per block.

Each of the four descendants `(S, g, a)` is then produced by the **already-committed explicit
form**, unchanged:

```
domc_core.set_geometry(g)                       # explicit geometry argument; g ∈ {NEAR, FAR}
e   = wsfscrp_core.engine()                     # PPAIEngine(SPEC, PPAIParams(gain=1/3, z_index=0), TRACER)
f0  = domc_core.found(S)                        # PRECURSOR(S) × _blob(g); ZERO advances
f   = domc_core.advance(e, f0, domc_core.T_FOUND)                    # 150 steps
hA, hB = (ppai_core.HIST_H, ppai_core.HIST_L) if a == 0 else (ppai_core.HIST_L, ppai_core.HIST_H)
st  = domc_core.advance(e, domc_core.apply_dual_history(e, f, hA, hB), domc_core.SETTLE)   # 120 + 120 steps
```

`HIST_H = "cc"`, `HIST_L = "00"`; the two allocation members are the two assignments of that
unordered pair to the two half-planes. Total 390 engine steps per descendant, in exactly one
raw advance sequence, in exactly one fresh process.

**What changes relative to FSQBT00 is only that `S` is now common to the four cells and
`(g, a)` are crossed within `S`.** FSQBT00 tied `(g, a)` to `S mod 4` over the namespace
N = 65100; WSFSCRP00's `make_founder` tied `a` to `S mod 2`. FCDDH00 unties them. The call
sequence, LawSpec, engine, founder generator, settle rule and checkpoint time are byte-identical
to the committed parent code. Byte-for-byte reproduction of every historical parity-selected
branch by the explicit form is proved **statically**, by source-level equivalence of the two
call sequences under the substitution `a := 0 if S % 2 == 0 else 1`, in
`G1_WITHIN_ANCESTRY_ELIGIBILITY_AUDIT.md`. **No physics is instantiated for the equivalence
test.**

### 4.2 Requirements that must hold or the programme stops

1. Same upstream precursor bytes for all four descendants of a block.
2. One and only one descendant per (NEAR/FAR × H3-member) cell.
3. Geometry independent of allocation construction order.
4. Reader-compatible masks and support in every cell.
5. No geometry/allocation **label** enters admission, reader, gauge or threshold *formula*.
   Descendant-specific sham values may differ and remain bound to bytes. (The frozen reader is
   *parameterised by the physical site positions*, which are the geometry itself; that is the
   inherited physical readout, not a label leak. Admission, gauge selection and threshold
   formulae contain no `g`/`a` term whatsoever.)
6. No fallback to seed parity as a physical factor.
7. No G2 observational substitute.

### 4.3 Admissibility (unchanged, pre-outcome, response-blind)

Per descendant, on the settled checkpoint:
`wsfscrp_core.t0_masks` must return exactly two eligible components (`rho > 0.30`, ≥ 12 sites,
periodic 4-connected); the independent `wsfscrp_core.reference_masks` must agree on the
unordered pair; `B_of > 0`; `rho` finite. **A defect in one descendant rejects the entire
four-descendant candidate block.** No scored future, sham threshold or response proxy may enter
admission.

---

## 5. Role queues, namespace and randomization (frozen rules)

### 5.1 Static runner audit, then queues

Derived from the exact committed runner **without advancing physics**:

```
C_SETUP_D, C_SETUP_H   = maximum charged setup starts per phase
C_BLOCK_MAX            = worst-case charged starts / advance sequences for one attempted
                         precursor plus its four required descendants and qualification
N_D_ATTEMPT = floor((96  - C_SETUP_D) / C_BLOCK_MAX)
N_H_ATTEMPT = floor((128 - C_SETUP_H) / C_BLOCK_MAX)
```

If `N_D_ATTEMPT < 12` or `N_H_ATTEMPT < 16`, stop before construction as
`CONSTRUCTION_BUDGET_CANNOT_ATTEMPT_REQUIRED_COMPLETE_PANELS`.

`N` = the smallest integer ≥ 71000 divisible by 1000 such that the entire interval of
`N_D_ATTEMPT + N_H_ATTEMPT` upstream candidate seeds is absent from **every** used, reserved,
generated, opened and exposed namespace in the repository. If not clean, `N += 1000` and repeat
the same metadata-only test.

```
DISCOVERY_CANDIDATE_QUEUE = N … N + N_D_ATTEMPT − 1                                   (ascending)
HOLDOUT_CANDIDATE_QUEUE   = N + N_D_ATTEMPT … N + N_D_ATTEMPT + N_H_ATTEMPT − 1       (ascending)
```

Candidate **role is assigned before construction and never changes**. Accept the first twelve
complete discovery blocks and, only if later eligible, the first sixteen complete hold-out
blocks. A discovery failure cannot promote a hold-out candidate; a hold-out candidate cannot
replace a discovery block. Failed candidates remain consumed and logged. Queue exhaustion stops
the phase. The complete two-role interval is reserved and manifested in Commit 2, but **no
hold-out state is generated unless the discovery axis later qualifies.**

One common upstream seed per four-descendant block. Geometry and allocation are explicit
arguments — never inferred from seed bits, filenames or serializer order. Child identifiers are
metadata-only `(upstream_seed, g, a)` tuples and cannot affect physics.

### 5.2 Counterfactual admission invariance (precondition of the randomization license)

Because the constructor is a pure function of `(S, g, a)` and admission is evaluated on the
**complete unordered quartet**, both values of the joint geometry-slot coin produce the same
unordered set of four explicit-factor descendants, the same checkpoint and mask hashes, and the
same accept/reject decision. This is proved in Commit 2 and re-tested by oracle Q0U. If the
proof fails, panel construction may continue prospectively but `FCDDH00_RANDOMIZATION_LICENSE =
false`.

### 5.3 Randomization scheduler (frozen, byte-exact)

One 256-bit OS randomization seed is generated **exactly once**, written and fsynced before any
derivation, and committed before construction. A crash between generation and commit must
recover those exact bytes; **no redraw is permitted**.

```
SHAKE256("FCDDH00|geometry|"   + role + "|" + candidate_index + "|" || seed) → first bit
SHAKE256("FCDDH00|allocation|" + role + "|" + candidate_index + "|" + g + "|" || seed) → first bit
SHAKE256("FCDDH00|run_order|"  + role + "|" + candidate_index + "|" || seed) → stream used by
      Fisher–Yates with rejection sampling, never modulo-biased reduction
```

Each geometry bit is used **directly, once**. The implementation hash, known-answer fixtures and
the complete schedule are persisted. No schedule byte may be regenerated from a different
library or PRNG.

Per ancestry block: (i) one fair **block-level** geometry coin maps NEAR/FAR jointly across both
allocation members onto otherwise neutral branch slots; (ii) the neutral H3 0/1 serializer
labels are independently exchanged within each geometry **only for execution blinding** — the
analysis must remain invariant to every such exchange; (iii) carrier execution order and
descendant run order are randomized without changing carrier identity or the physical estimand.

The joint geometry coin (rather than two allocation-specific coins) gives **one exact sign-flip
unit per ancestry** for the 16-block hold-out randomization distribution.

`FCDDH00_RANDOMIZATION_LICENSE = true` additionally requires all of: counterfactual admission
invariance (5.2); neutral branch slots identical before the explicit geometry intervention; one
consistent implementation of each named treatment; no interference or shared mutable state
between descendants or ancestries; process, RNG, cache and file isolation; outcome invariance to
carrier/descendant execution order; assignment cannot alter reader, masks, gauge or analysis
definitions; complete assignment and launch chronology proven from committed ledgers.

**Thresholds are geometry-specific pre-active measurements** and are treated separately in the
materiality gate; they are *not* assumed invariant for the primary response-only randomization
test. If any randomization condition fails, the prospective finite-panel result is retained and
all inferential randomization p-values are set to `NOT_LICENSED`.

---

## 6. Exact frozen estimands

Array shapes, coefficient maps and units are resolved from the committed parent objects in
Commit 2. The formulas below bind scientific meaning. If a parent serialization uses an
algebraically equivalent scale, **one complete isometry is certified and the vectors and every
bound are transformed together before outcomes**. A dimensional mismatch is never repaired
after reading responses.

### 6.1 Per-row weighted-L2 response

Inherited, unchanged: scored times `H_GRID = 40·i, i = 1…10` native steps (`dt = 1/10`, physical
times 4…40), trapezoid weights `W` normalised to sum 1, reader
`X_A(t) = Σ_{support A} ρ_t / B`, `X_B(t) = Σ_{support B} ρ_t / B`, `B` the fixed pre-treatment
normalizer from raw baseline bytes. For a row (descendant × carrier):

```
δ_A[h] = X_A^active[h] − X_A^sham[h]          δ_B[h] = X_B^active[h] − X_B^sham[h]      (exact rationals)
M2² = Σ_h W[h] (δ_A[h]² + δ_B[h]²)
u[h] = sqrt(W[h]/2) (δ_A[h] + δ_B[h])         v[h] = sqrt(W[h]/2) (δ_A[h] − δ_B[h])
z(s) = ( u[0..9] , s · v[0..9] ) ∈ R^20 ,     s ∈ {+1, −1}
```

`‖z(s)‖² = M2²` for either `s`; the map is an exact isometry onto the parent's 20-dimensional
weighted-L2 coordinate space. `s` is the **linked A/B exchange**: one optional exchange per
**complete descendant**, shared across both carriers and every scored time.

```
TAU[b,g,a] = descendant-specific response-radius materiality threshold
```
computed from that descendant's own SHAM_0 by the unchanged inherited rule
`TAU² = max(η_oracle², τ_dynamic², τ_site²)` with `η_oracle = 0` on the exact scoring path,
`τ_dynamic² = (1/100)² Σ_h W[h]((X_A[h]−X_A[0])² + (X_B[h]−X_B[0])²)`,
`τ_site² = ((1/100)·median(ρ_0|support)/B)² · Σ_h W[h]`. Both carriers of one descendant use the
**same canonical sham and the same TAU**.

**Gauge rule (immutable parent-P2 residual rule).** With `Q = I − P2_parent`,
`a_o = u_o − mu_parent`, `b_o = v_o`, the descendant residual at gauge `s` is
`Σ_o (a_oᵀQa_o + b_oᵀQb_o) + 2s Σ_o a_oᵀQb_o`. Therefore

```
D_desc = Σ_{o ∈ {C1,C2}} (u_o − mu)ᵀ Q v_o
s      = −1 if D_desc > 0 ; +1 if D_desc < 0 ; both co-optimal if D_desc = 0
```

This is **descendant-separable**, hence block-separable; it is blind to geometry, allocation,
discovery/hold-out role and any candidate-axis score. Co-optimal orbits are **enumerated**, never
averaged away.

For every legal linked gauge representative:

```
r[b,g,a,o] = (I − P2_parent) @ (z[b,g,a,o] − mu_parent)
d[b,g,a]   = ( r[b,g,a,CARRIER_2] − r[b,g,a,CARRIER_1] ) / sqrt(2)
x[b]       = (1/2) Σ_{a ∈ {0,1}} ( d[b,NEAR,a] − d[b,FAR,a] )
```

`mu_parent` cancels exactly in `d`. Carrier and geometry signs are physically named and frozen.
Allocation labels have no sign and disappear through the exact average. **`x` is never centred by
a fresh midpoint; zero is the predeclared no-interaction origin.**

Proved before outcomes (Q0D–Q0I): `P2_parent @ x[b] = 0` within certified arithmetic; `x[b]`
unchanged by either allocation-member exchange within NEAR or FAR; the joint block-level
NEAR/FAR slot swap maps `x[b] → −x[b]`; all four descendants and all eight carrier rows carry
their exact coefficients.

### 6.2 Exact response-unit materiality propagation

Each of the eight row responses enters `x[b]` with absolute coefficient `1/(2√2)`; each of the
four rows of a cross-orbit pair contrast enters with absolute coefficient `1/√2`. Both are
re-derived from the exact committed coefficient map in `EXACT_INTERACTION_COEFFICIENT_MAP.json`
and certified in `EXACT_TAU_PROPAGATION_CERTIFICATE.json` before any outcome. Because `Q` is an
orthogonal projector, `‖Q w‖ ≤ ‖w‖`, so the triangle-inequality floors are conservative:

```
A_X[b]                = (1/√2) Σ_{g,a} TAU[b,g,a]                  E_X[b] = A_X[b]²
A_PAIR[b,aN,aF]       = √2 ( TAU[b,NEAR,aN] + TAU[b,FAR,aF] )
X_BAR[B]              = (1/|B|) Σ_b x[b]
A_X_BAR[B]            = (1/|B|) Σ_b A_X[b]                          E_X_BAR[B] = A_X_BAR[B]²
s[b;v]                = ⟨v, x[b]⟩       S_BAR[B;v] = (1/|B|) Σ_b s[b;v]      E_FIXED = S_BAR²
```

**Root-sum-of-squares is never used** (no parent certificate proves the required error
independence). **`x`, `d`, `z` and axis scores are never divided by TAU.**

The fixed directional interaction is **absolutely material** only if
`lower(S_BAR[B;v]) > upper(A_X_BAR[B])` after the axis is oriented by discovery and frozen.
**Equality fails.** The rotation-invariant comparison `lower(‖X_BAR[B]‖) > upper(A_X_BAR[B])` is
also reported but **cannot rescue a failed fixed-axis validation and may not define a new
hold-out direction.**

Sampling significance, sign coherence and absolute materiality are three different fields. A
small but reproducible interaction may pass the first two and fail the third without any
threshold change.

### 6.3 Direct cell and carrier-contrast materiality (unchanged inherited tests)

```
CELL_MATERIAL[b,g,a,o]        ⟺  M2[b,g,a,o]² > TAU[b,g,a]²
DIRECT_CARRIER_CONTRAST[b,g,a] = z[b,g,a,CARRIER_2] − z[b,g,a,CARRIER_1]
DIRECT_CARRIER_CONTRAST_MATERIAL ⟺ ‖DIRECT_CARRIER_CONTRAST[b,g,a]‖ > 2 · TAU[b,g,a]
```

(The inherited committed bound is exactly this triangle bound: FSQBT00 used
`contrast_norm_sq > 4·TAU²`.) Complete panels are required; **no selection of only responding
descendants and no selection of the more responsive carrier.**

### 6.4 Allocation-orbit uniformity

```
p[b,aN,aF;v]  = ⟨v, d[b,NEAR,aN] − d[b,FAR,aF]⟩        (all four cross-orbit pairings)
u[b;v]        = min_{aN,aF} p[b,aN,aF;v]
J[b;v] = 1  ⟺  for all four (aN,aF):  lower(p[b,aN,aF;v]) > upper(A_PAIR[b,aN,aF])
m[b;v] = min_{aN,aF} ( lower(p[b,aN,aF;v]) − upper(A_PAIR[b,aN,aF]) )
```

`u > 0` means every NEAR allocation member lies above every FAR allocation member along the
fixed carrier-differential axis; it is invariant to independent allocation-member relabellings
and is deliberately **stronger** than the allocation-averaged interaction. An unresolved
interval, an equality, or one failing allocation pairing gives `J = 0`. `J = 1` exactly when the
certified `m > 0`.

Three separate statuses are kept: `ALLOCATION_AVERAGED_INTERACTION`,
`UNIFORM_ACROSS_ALLOCATION_ORBIT`, `ALLOCATION_MODULATION_DESCRIPTIVE_ONLY`. The last may use
the predeclared H3 orbit outer-product object but **cannot select another axis or alter the
primary verdict**.

### 6.5 Immutable P2 summaries (historical unit preserved)

```
FSQBT00_LEGACY_STRICT_MAX4_ALL_BLOCK_CONTAINMENT_STATUS = FAILED_AS_PREDECLARED
P2_POPULATION_TRANSFER_INTERPRETATION                    = INCONCLUSIVE_FROM_THIS_GATE_ALONE
```

That gate is **never rerun or reclassified** on a differently aggregated unit. For each of the
64 hold-out descendants, the directly comparable immutable-object score is

```
R_P2_DESC[b,g,a] = (1/2) Σ_o ‖(I − P2_parent)(z[b,g,a,o] − mu_parent)‖²
Q_P2_DESC[b,g,a] = R_P2_DESC[b,g,a] / TUBE_P2_LOBO_parent
```

All 64 certified scores/ratios and `P2_HOLDOUT_DESCENDANT_EXCEED_COUNT_OF_64` are reported. The
64 descendants are **clustered within sixteen ancestries and are never treated as 64 independent
Bernoulli trials.** Three *new* ancestry summaries are reported, none of them the legacy gate:

```
R_P2_ANCESTRY_MEAN[b] = (1/4) Σ_{g,a} R_P2_DESC[b,g,a]
R_P2_ANCESTRY_MAX[b]  = max_{g,a} R_P2_DESC[b,g,a]
J_P2_ALL4[b] = 1 ⟺ every R_P2_DESC[b,g,a] ≤ TUBE_P2_LOBO_parent
P2_HOLDOUT_ALL4_ANCESTRY_COUNT_OF_16 = Σ_b J_P2_ALL4[b]
```

All three are reported; **none is selected after outcomes.** An exact two-sided Clopper–Pearson
interval may accompany `P2_HOLDOUT_ALL4_ANCESTRY_COUNT_OF_16` **only if** the upstream ancestry
generator, seed sampling and outcome-blind admissibility mechanism justify iid Bernoulli
sampling with one common probability; **exchangeability alone is insufficient**; otherwise these
are finite-panel distributions only (`P2_HOLDOUT_GENERATOR_INTERVAL_LICENSE = NOT_LICENSED`).
No pass/fail population threshold is invented after seeing any count; one exceedance is not
called non-transfer; a good ancestry mean does not erase the historical failed gate.

### 6.6 Certified arithmetic convention (frozen)

`δ_A`, `δ_B`, `B`, `W`, `TAU²` are **exact rationals** (`fractions.Fraction`); every float64 is
itself an exact dyadic rational, so `mu`, `P1`, `P2`, `e1`, `e2` and the serialized axis enter
exactly. The only irrational entering the response map is `sqrt(W[h]/2)`; the production path
therefore carries every derived quantity as a **rational interval enclosure**, using a
`√2` enclosure of width < 2⁻¹⁰⁰, and every comparison is a certified interval comparison in
which an unresolved comparison is reported as `UNRESOLVED`, never silently resolved. The
independent reference path recomputes the same quantities by a deliberately different route in
float64 and must agree with the production enclosure. **Equality anywhere is failure**, in every
gate.

---

## 7. Discovery panel procedure (frozen)

1. **Construct** exactly twelve complete G1 blocks from the frozen discovery candidate queue,
   accepting the first twelve complete blocks passing 4.3. Persist per accepted block: upstream
   precursor bytes and hash; four descendant checkpoint bytes and hashes; complete ancestry
   graph; explicit geometry and H3 orbit arguments; randomized neutral slot mapping and
   execution order; fixed-support masks and hashes; normalizer/domain/boundary/scheduler
   metadata; every charged start and raw advance sequence. If twelve cannot be obtained within
   96 construction/qualification starts, close as
   `DISCOVERY_COMPLETE_FACTORIAL_PANEL_INCOMPLETE` with **zero** shams and **zero** active
   starts. At the twelfth acceptance, commit `FCDDH00_DISCOVERY_PANEL_LOCK` **before any sham**;
   the 48 descendants are then permanently assigned to discovery.
2. **Twin shams**: 48 × {SHAM_0, SHAM_1} = **96** starts, two identity continuations per sealed
   descendant from byte-identical checkpoints in separate fresh processes. Persist full engine
   terminal hashes **and the complete canonical A/B reader series at every scored time for both
   twins** (the historical omission is not repeated). Require exact full-horizon identity,
   production/reference reader agreement, immutable masks, no carrier touch set. Compute every
   descendant TAU and all exact interaction coefficient propagations, then commit
   `FCDDH00_DISCOVERY_THRESHOLD_LOCK`. A mismatch, crash or missing twin stops the programme with
   **zero** discovery active starts; no descendant is replaced or rerun.
3. **Raw-only active acquisition**: 48 × 2 = **96** starts, the two unchanged historical 1×
   carriers from each sealed descendant, separate fresh processes, frozen randomized execution
   order, write-ahead ledger. Persist full scored trajectories, terminal hashes and raw metadata;
   the archive stays **opaque to all analysis code** until all 96 rows are present and
   `FCDDH00_DISCOVERY_ACTIVE_RAW_LOCK` is committed as a direct append-only descendant. No
   partial panel, spare descendant, retry, best arm or best cell is eligible; any launched but
   incomplete row gives
   `DISCOVERY_ACTIVE_PANEL_INCOMPLETE__NO_AXIS__ZERO_HOLDOUT_STARTS`.

---

## 8. Discovery-only axis training, and the D-gates (frozen)

After the raw lock, all 96 rows are decoded independently through the production and reference
implementations. The **only** trainable vector is

```
X_BAR_D = (1/12) Σ_{b ∈ DISCOVERY} x[b]        v_D = canonical_unit(X_BAR_D),  ⟨v_D, X_BAR_D⟩ > 0
```

If the certified norm interval contains zero, **no axis exists**. No intercept, midpoint,
covariance, whitener, P3, classifier, nonlinear map, selected time/channel or alternative
normalization is fitted.

**Leave-one-ancestry-out (twelve folds).** Omit one complete upstream ancestry and *all* of its
four descendants / eight carrier rows and associated shams; recompute every training gauge using
only the eleven remaining ancestries and the immutable label-blind parent-P2 rule; fit
`v_D[−b] = canonical_unit(mean_{j≠b} x[j])`, oriented toward its own eleven-block mean only;
score the omitted block as `⟨v_D[−b], x[b]⟩` **without reorientation**; persist the complete
co-optimal gauge orbit, axis, rank-1 projector, score and squared alignment with the full
discovery axis. For the omitted ancestry every descendant gauge is rebuilt from that
descendant's own response by the same label-blind, axis-blind parent-P2 criterion; a full-panel
gauge is never reused. Block separability is proved from the immutable parent rule
(descendant-separability ⇒ block-separability). If separability is not proved the axis is
`UNRESOLVED`; **no globally coupled discovery optimization is substituted.**

```
L_D[b] = ⟨v_D, x[b]⟩² / Σ_j ⟨v_D, x[j]⟩²      (concentration diagnostic, not a decomposition)
```

**Gates — all must pass for hold-out eligibility:**

```
D0  provenance, design lock, raw identity and both implementations pass
D1  discovery cell materiality 96/96
D2  direct carrier contrast material in all 48 descendants
D3  ‖X_BAR_D‖ certifiably nonzero above numerical error        (ALONE determines identifiability)
D4  lower(‖X_BAR_D‖) > upper(A_X_BAR[DISCOVERY])
D5  ≥ 10/12 omitted ancestries have J[b; v_D[−b]] = 1          (unresolved folds do not count)
D6  min full-versus-fold squared alignment ≥ 0.80
D7  max L_D[b] < 0.50
D8  ∀ b, with the full-discovery sign v_D and no reorientation:
        lower(⟨v_D, mean_{j≠b} x[j]⟩) > 0   and   mean_{j≠b} m[j; v_D] > 0
D9  allocation exchanges and co-optimal gauges preserve the axis projector, fold scores and
    categorical verdict
D10 production and independent reference outputs agree within the frozen bounds
D11 dependency audit proves zero FSQBT00/FCRA00 vector and zero hold-out row entered the trainer
```

10/12 is a **predeclared internal stability guard** (79/4096 under a fair-sign reference), not a
confirmatory p-value and not an independent replication. Equality passes the 0.80 alignment
guard but **fails** the < 0.50 leverage guard; zero scores fail. Discovery materiality (D4) and
worst-pair allocation-orbit robustness (D5) are **eligibility gates, not decorations**: FCRA00
already produced an internally coherent but sub-material, allocation-fragile direction, and
repeating that pattern would not justify consuming sixteen hold-out ancestries. A numerically
stable but sub-material discovery result is reported honestly and the programme then stops with
**zero hold-out starts**.

If all D-gates pass, exactly one object is serialized —
`FCDDH00_DIFFERENTIAL_INTERACTION_AXIS_D1.{npz,json}` plus `…_LOADER.py` — carrying
`SOURCE = TWELVE_NEW_CROSSED_DISCOVERY_ANCESTRIES`,
`AXIS_SPACE = OUTSIDE_PARENT_P2__CARRIER_DIFFERENTIAL`,
`ESTIMAND = ALLOCATION_AVERAGED_NEAR_MINUS_FAR_X_CARRIER`,
`VALIDATION_STATUS = NOT_YET_TESTED`, `TRANSFER_STATUS = NOT_CLAIMED`,
`ABSOLUTE_MATERIALITY_STATUS = DISCOVERY_RESULT_REPORTED_SEPARATELY`, together with the exact
array, interval coefficients, canonical sign, all twelve fold axes/projectors, gauge transport,
training ancestry manifest, response-unit formula, scorer hash and mutation tests; unit norm, P2
orthogonality and byte-for-byte disk round-trip verified. The axis and
`FCDDH00_HOLDOUT_ANALYSIS_LOCK` are committed **before any hold-out state is generated**.

If any D-gate fails or is unresolved: each canonical discovery field takes its own gate-specific
`PASS | FAIL | UNRESOLVED`;
`DISCOVERY_AXIS_SERIALIZATION_STATUS = NOT_LICENSED__FAILED_GATES=<exact list>`; every canonical
hold-out field = `NOT_REACHED_BY_PREDECLARED_STOP`; `HOLDOUT_*_STARTS = 0`. The programme closes.
**No common axis, total-response axis, fresh PCA, subset, regularizer or second training rule is
tried.** A leverage, firewall, materiality or allocation failure may forbid serialization but may
**never** rewrite an otherwise identifiable axis as non-identifiable.

**Firewall.** `DISCOVERY_AXIS_TRAINER_V1` may output values only from the twelve discovery
blocks. `HOLDOUT_FIXED_AXIS_SCORER_V1` must reject any request to fit, center, rotate, rescale,
orient or choose an axis from hold-out rows. Source hashes and a resolved-symbol dependency
graph are frozen. **Dynamic imports, `eval`, unresolved `getattr`, filename/seed label inference
and string-to-call dispatch are forbidden** anywhere in the FCDDH00 analysis path.

---

## 9. Hold-out procedure and H-gates (frozen)

Eligible **only** after the axis, loader, scorer and hold-out analysis lock are committed,
independently read back and pass all mutation tests, and only if no hold-out checkpoint, mask,
sham or trajectory already exists or has been opened.

16 complete G1 blocks from the preassigned hold-out queue under the already frozen outcome-blind
gates (≤ 128 construction starts, else `HOLDOUT_PANEL_STATUS = INCOMPLETE`,
`HOLDOUT_SHAM_STARTS = 0`, `HOLDOUT_ACTIVE_STARTS = 0`,
`HOLDOUT_FIXED_AXIS_DIRECTIONAL_REPLICATION_STATUS = NOT_EVALUABLE__PANEL_INCOMPLETE`; no extra
discovery blocks, no loosened admission, no recycled ancestries) → `FCDDH00_HOLDOUT_PANEL_LOCK`
→ 64 × 2 = **128** twin shams → `FCDDH00_HOLDOUT_THRESHOLD_LOCK` → 64 × 2 = **128** raw-only
active starts → `FCDDH00_HOLDOUT_ACTIVE_RAW_LOCK`. Only then may the fixed scorer decode.

### 9.1 Exact block-level randomization calibration

```
s_H[b] = ⟨v_D, x[b]⟩            K_H = Σ_b J[b; v_D]            T_H = Σ_b s_H[b]
```

`K_H` is the predeclared **material / orbit-robust support gate**. The primary randomization
statistic is the **threshold-free fixed-axis response sum `T_H`**.

If §5.3 proved one independent fair geometry coin per ancestry and neutral pre-intervention
branch slots, **all 2¹⁶ assignments are enumerated**; for each assignment NEAR/FAR is jointly
swapped across both allocation members inside the affected ancestry and `x`, every `p`, `J`, `K`
and `T` are **recomputed through the complete frozen scorer and gauge rule** — not by negating a
cached scalar (the exact equivariance identity is proved separately and cross-checked against the
recomputation).

**The exact sharp null**: within every neutral branch slot and allocation orbit, the outside-P2
carrier-differential response would be unchanged if the explicit geometry assignment were
switched between NEAR and FAR. It is *not* the broader null that geometry has no common effect on
either carrier, and it says nothing about ungenerated laws or lattices.

```
P_RANDOMIZATION_T = #{assignments with T_perm ≥ T_observed} / 2^16      (observed included; no +1 patch)
```

Because `J` contains geometry-specific sham-derived `TAU`, the corresponding enumerated count
tail is **not** an exact test of the response-only sharp null and is reported only as

```
K_ASSIGNMENT_TAIL_SENSITIVITY        = #{assignments with K_perm ≥ K_observed} / 2^16
K_ASSIGNMENT_TAIL_INFERENTIAL_STATUS = NONINFERENTIAL_UNDER_RESPONSE_ONLY_SHARP_NULL
```

`P_RANDOMIZATION_T` cannot rescue too few materially robust ancestry successes, and `K_H` cannot
rescue a failed response-only randomization test. `BLOCK_SUCCESS_FRACTION = K_H/16` is reported;
a Clopper–Pearson interval is attached **only** under the iid sampling proof of §6.5, kept
distinct from the assignment-randomization p-value. The predeclared design reference
`P(K ≥ 12 | p_success ≤ 1/2) = 2517/65536 = 0.0384063720703125` is reproduced exactly; it is
inferential for `K` only under that iid common-probability model or a separately proved stronger
joint sharp null, and is **never** evidence of universal geometry or an iid biological
population. If the license fails, `P_RANDOMIZATION_T = NOT_LICENSED`, all sixteen immutable
scores and `K_H` are still reported, and **no sign-flip test is invented**.

```
HOLDOUT_FIXED_AXIS_RANDOMIZATION_STATUS =
    LICENSED__RESPONSE_ONLY_T_P=<EXACT_RATIONAL>
  | NOT_LICENSED__REASON=<EXACT_FAILED_LICENSE_CONDITIONS>
  | NUMERICALLY_UNRESOLVED
  | NOT_EVALUABLE__INCOMPLETE_PANEL
  | NOT_REACHED_BY_PREDECLARED_STOP
```

### 9.2 Fixed validation gates

```
H0 hold-out provenance, panel/raw identity and axis-loader integrity pass
H1 hold-out cell materiality 128/128
H2 direct carrier contrast material in all 64 descendants
H3 every gauge / co-optimal orbit gives the same fixed scores, J values and categorical verdict
H4 production and independent reference computations agree
H5 K_H ≥ 12 of 16, unresolved/equality counted as failures
H6 P_RANDOMIZATION_T ≤ 0.05 when randomization is licensed
H7 lower(T_H) > 0 and at least 12/16 allocation-averaged s_H[b] positive
H8 max s_H[b]² / Σ_j s_H[j]² < 0.50
H9 no hold-out fit, recentering, rescaling, reorientation, row exclusion or discovery/FCRA
   data dependency is reachable
```

When randomization is not licensed, H6 is `NOT_EVALUABLE` and **no confirmatory
causal/randomized label is available**; a separate `FINITE_PANEL_COHERENCE_12_OF_16` status is
reported if H0–H5 and H7–H9 pass, and it is **not** called randomized validation.
`K_H ≥ 12` is frozen now: never continue from 16 to 20 or 24 after observing `K_H = 10` or `11`;
never reinterpret one allocation pairing as the primary; never count four margins or 128 carrier
rows as independent n.

### 9.3 Separate verdicts and exact labels

```
HOLDOUT_ALLOCATION_AVERAGED_DIRECTION_SECONDARY_STATUS
  = PASS if ≥12/16 s_H[b] > 0 and the licensed T randomization passes
  | FAIL | RANDOMIZATION_NOT_LICENSED | UNRESOLVED
HOLDOUT_INTERACTION_ABSOLUTE_MATERIALITY_STATUS
  = PASS iff lower(S_BAR[HOLDOUT; v_D]) > upper(A_X_BAR[HOLDOUT]) | FAIL | UNRESOLVED
HOLDOUT_ALLOCATION_ORBIT_ROBUSTNESS_STATUS = K_H_OF_16 with the model-licensed reference or the
  explicitly noninferential assignment-tail sensitivity kept separate
```

The block-success primary already imposes the strongest allocation-orbit and materiality
requirement; the averaged fields explain failures and **never rescue H5**.

```
HOLDOUT_FIXED_AXIS_DIRECTIONAL_REPLICATION_STATUS =
    RANDOMIZED_HOLDOUT_VALIDATED | FINITE_PANEL_COHERENT__RANDOMIZATION_NOT_LICENSED
  | NOT_VALIDATED | NOT_EVALUABLE_INCOMPLETE_PANEL | NUMERICALLY_OR_GAUGE_UNRESOLVED
HOLDOUT_INTERACTION_ABSOLUTE_MATERIALITY_STATUS =
    FIXED_DIRECTION_ABSOLUTELY_MATERIAL | FIXED_DIRECTION_BELOW_ABSOLUTE_MATERIALITY | UNRESOLVED
HOLDOUT_ALLOCATION_ORBIT_ROBUSTNESS_STATUS =
    ROBUST_ACROSS_FULL_COMPLEMENTARY_ORBIT | ALLOCATION_AVERAGED_ONLY__WORST_PAIR_FAILS
  | NO_DIRECTIONAL_SUPPORT | UNRESOLVED
```

Also reported: the hold-out mean vector and its fixed alignment with `v_D`; all block and pairing
margins in original response units; exact discovery-versus-hold-out axis score distributions
without fitting a hold-out axis; fixed P2 projected/outside energy and the tube-exceedance
summary of §6.5; H3 allocation-modulation objects as descriptive secondary quantities only. **No
fresh quotient, hold-out PCA, common axis, alternate residual space or FCRA axis comparison.**

**There is exactly one confirmatory randomization family**: the fixed differential interaction
statistic `T_H`, with the material/orbit `K_H` gate conjunctive. No confirmatory p-value is
attached to P2 summaries, H3 modulation or any other secondary; any unavoidable additional
inferential family would have been frozen before outcomes and Holm-corrected — none is declared,
so **all other values are labelled exploratory**.

---

## 10. Decision matrix, precedence and claim ceiling (frozen)

Top-level disposition is one of, with only an evidence qualifier added when required:

```
PARENT_PROVENANCE_OR_G1_ELIGIBILITY_UNRESOLVED__ZERO_STARTS
PREANALYSIS_ORACLE_OR_LOCK_FAIL__ZERO_STARTS
DISCOVERY_COMPLETE_FACTORIAL_PANEL_INCOMPLETE__ZERO_HOLDOUT_STARTS
DISCOVERY_SHAM_OR_ACTIVE_PANEL_INCOMPLETE__NO_AXIS__ZERO_HOLDOUT_STARTS
DISCOVERY_AXIS_NOT_LICENSED__ZERO_HOLDOUT_STARTS__FAILED_GATES=<EXACT_D0_D11_LIST>
DISCOVERY_DIFFERENTIAL_AXIS_SERIALIZED__HOLDOUT_PANEL_INCOMPLETE__VALIDATION_NOT_EVALUABLE
HOLDOUT_COMPLETE__FIXED_DIFFERENTIAL_INTERACTION_NOT_VALIDATED
HOLDOUT_COMPLETE__FINITE_PANEL_COHERENT__RANDOMIZATION_NOT_LICENSED
HOLDOUT_COMPLETE__RANDOMIZED_DIFFERENTIAL_INTERACTION_VALIDATED__BELOW_ABSOLUTE_MATERIALITY
HOLDOUT_COMPLETE__ALLOCATION_AVERAGED_DIRECTION_ONLY__PRIMARY_NOT_VALIDATED
HOLDOUT_COMPLETE__RANDOMIZED_DIFFERENTIAL_INTERACTION_VALIDATED__ABSOLUTELY_MATERIAL__FULL_ALLOCATION_ORBIT_ROBUST
NUMERICALLY_OR_GAUGE_UNRESOLVED
```

Mapping, total and prospective: `FULL_ALLOCATION_ORBIT_ROBUST` means `K_H ≥ 12/16` with all four
orbit pairings passing inside each successful ancestry — it does **not** mean 16/16. If H5 fails
but the allocation-averaged secondary passes →
`ALLOCATION_AVERAGED_DIRECTION_ONLY__PRIMARY_NOT_VALIDATED` (explicitly a *failed primary* with a
positive weaker secondary; because H5 uses `J` it can never carry the strongest label). If H0–H5
and H7–H9 pass but the license/H6 is unavailable → `FINITE_PANEL_COHERENT__RANDOMIZATION_NOT_
LICENSED`. If H0–H9 pass and aggregate fixed-axis materiality fails → the
validated-below-absolute-materiality label. If H0–H9 and aggregate materiality pass → the
full-orbit robust positive label. Every other complete-panel outcome is `NOT_VALIDATED` with the
exact failed H-gates listed. **No label choice is postponed to post-outcome discretion.**

**Strict stop precedence** (no later positive field crosses an earlier fatal stop): provenance
and static G1 eligibility → preanalysis freeze, firewall and oracle → discovery complete panel
and twin shams → discovery complete raw acquisition → discovery material, orbit-robust axis
qualification → immutable axis serialization and hold-out lock → hold-out complete panel and twin
shams → hold-out complete raw acquisition → fixed-axis validation → secondary P2 distribution and
descriptive diagnostics → closure.

**Claim ceiling.** The maximum licensed positive statement is: *on a prospectively generated,
complete, within-ancestry crossed development panel, a carrier-differential outside-parent-P2
direction learned by one frozen algorithm on twelve independent discovery ancestries predicted a
material NEAR-minus-FAR × carrier interaction in at least twelve of sixteen untouched hold-out
ancestries, uniformly across the neutral complementary-allocation orbit, under the exact
randomized finite-panel calibration.* Only the clauses whose gates actually pass are used. If
absolute materiality fails: “directionally coherent but below the inherited operational
materiality floor.” If allocation uniformity fails: “allocation-averaged only.” If the
randomization license fails: “finite-panel coherence; randomized/causal validation not
licensed.”

**Never claimed:** life, organism, individuality, autonomy, memory, inheritance, agency or
open-ended evolution; a universal, intrinsic or biological second dimension; broad universality
from one engine, LawSpec, lattice or generator; that parent P2 transferred because vectors
numerically project onto it; population non-transfer because one or more blocks exceed an old
tube; causal allocation effects from the neutral H3 member labels; a new carrier, dose,
mechanism, reader, mask, window or off-support process; statistical independence of descendants,
carriers, channels, sites or time; confirmation from the twelve FCRA00 blocks or their
post-outcome direction; a "first discovery" or priority claim. No persistence, turnover,
morphology, boundedness, energy throughput or carrier flow metric may substitute for the exact
response estimand.

---

## 11. Fatal stops and permitted engineering corrections (frozen)

**Fatal to the affected science branch:** unresolved parent tip/tree/raw identity or a changed
`main`; a master freeze or code lock written after prohibited numerical access; G1 unable to
cross both factors from identical precursor bytes; any FCRA00 vector or hold-out row reaching
the discovery trainer; carrier/reader/normalizer/mask/horizon/threshold/P2 mutation; an
unauthorized engine probe, retry, replacement or budget exceedance; a partial panel analyzed as
complete; a raw archive decoded before its raw-only commit; a missing row imputed, rerun or
replaced; co-optimal gauges changing an axis/projector/score/verdict without an `UNRESOLVED`
classification; an allocation matching selected because it looks favorable; a sample size
extended after outcome access; hold-out code that fits, recenters, rescales, rotates or flips the
axis; production and reference implementations disagreeing beyond the frozen certified arithmetic
bounds; existing evidence deleted, overwritten, hidden or rewritten.

**Permitted without asking Tommy:** fixing packaging, path, serializer or report-rendering
defects that cannot alter numerical science (documented exactly); repairing a *pre-outcome*
analysis implementation bug before any affected raw outcome is decoded, then rerunning all
synthetic oracles, recommitting hashes and reading back the lock; resuming idempotent metadata
and opaque-copy work after a transient bridge failure; adding append-only crash-recovery commits
containing opaque completed blocks.

**If a scientific analysis bug is discovered after discovery decoding but before hold-out
generation**, the trainer is *not* silently amended: the current axis is closed as invalid and the
programme stops with zero hold-out starts. A corrected algorithm would need a new authorization
and a new discovery panel.

---

## 12. Git and delivery discipline (frozen)

Branch `dev/fresh-crossed-differential-discovery-holdout-00` created from the exact FCRA00 tip
`334b7c2ba6d97dadb403c7a1ea9700a1c61ad512`. `main` is never modified or checked out as a work
branch. **No amend, rebase, reset, force update, history replacement, merge into main, push, PR
or workflow trigger.** Required logical commit order (extra raw-only recovery commits permitted
inside the marked phases):

1. master freeze and owner/provenance intent — **pre-numerical**
2. resolved provenance, G1 eligibility, role queues, randomization schedule, symbolic design lock — **zero starts**
3. dependency firewall, code hashes, non-vacuous oracle, lock read-back — **zero starts**
4. discovery construction and sealed panel
5. discovery twin shams and numerical threshold lock
6. discovery opaque active acquisition (+ optional per-block raw-only checkpoints), then complete raw lock
7. discovery decode, gates, optional axis serialization and hold-out analysis lock
8. hold-out construction and sealed panel — only if eligible
9. hold-out twin shams and numerical threshold lock
10. hold-out opaque active acquisition (+ optional per-block raw-only checkpoints), then complete raw lock
11. fixed-axis hold-out analysis and secondary immutable-P2 summaries
12. report, manifest and delivery-only closure

Every commit after an engine phase includes the cumulative write-ahead ledger. Unused authorized
starts are recorded separately — **authority is not an obligation to spend**. A
non-self-referential `SHA256SUMS_SCOPE.json` covers every delivered FCDDH00 file except
`SHA256SUMS`, the out-of-tree final bundle and Git metadata; `SHA256SUMS` is built and verified
from the committed tree **and** from an independent object extraction; the final subtree id is
reproduced with the two available Git implementations (device 2.34.1, cloud 2.43.0) where
possible; the final bundle is built only after the final tip exists and its digest is reported
**out of band**. **No command, click, upload, token, branch manipulation or Git action is
delegated to Tommy.**

---

## 13. Commit-1 scope declaration

Commit 1 contains exactly: `FCDDH00_MASTER_FREEZE.md`, `OWNER_AUTHORIZATION_BINDING.json`,
`PRE_NUMERICAL_ACCESS_LEDGER.jsonl`, `GIT_AND_PARENT_PROVENANCE_INTENT.md`, plus the verbatim
authorization text `OWNER_AUTHORIZATION_VERBATIM.txt` that `OWNER_AUTHORIZATION_BINDING.json`
hashes (the authorization is the subject of the binding, not an extra artefact). It resolves Git
metadata and hashes opaque files only. Every pre-freeze read of any parent object is enumerated
in `PRE_NUMERICAL_ACCESS_LEDGER.jsonl`, including one read that is declared as a protocol
deviation there and in `PROTOCOL_DEVIATIONS.md`. The committed freeze is read back through an
independent path and its hash verified before any later phase.
