# SQDT00_MASTER_FREEZE

`SERIALIZED_QUOTIENT_DOSE_TRANSFER_00`.
Written, hashed and committed **before any parent `npz`, response row, reader series, score
vector or numeric certificate is loaded**, other than the summary figures the owner had already
exposed in the handoff prose (R0, R1, R2, I1, I2, E_TAU, A_TAU, the 0.570 ratio and the 32/32
materiality count). Nothing below is derived from a fresh array.

Workdir `/home/claude/sweep/SQDT00`, branch `dev/serialized-quotient-dose-transfer-00`, parent
the exact full commit `96c7d295e72106cd949d810fa92807c2514e7449`.

---

## 0. Standing constraints, restated so that they bind this programme

    TOMMY_ACTION_REQUIRED               = false
    TOMMY_GIT_ACTION_REQUIRED           = false
    PUSH_AUTHORIZED                     = false
    DRAFT_PR_AUTHORIZED                 = false
    WORKFLOW_TRIGGER_AUTHORIZED         = false
    EXECUTION_MODE                      = ONE_EXECUTOR_SEQUENTIAL
    PARALLEL_AGENTS_AUTHORIZED          = 0
    PARALLEL_REVIEWERS_AUTHORIZED       = 0
    SEEDS_62000_THROUGH_62009           = RESERVED_AND_UNREAD__DO_NOT_GENERATE_OR_OPEN
    NEW_LAWSPEC                         = false
    ENGINE_EQUATION_CHANGE              = false
    NEW_STATE_VARIABLE_OR_TRACER        = false
    FIXED_SUPPORT_READER_CHANGE         = false
    CHECKPOINT_TIME_CHANGE              = false
    HORIZON_CHANGE                      = false
    TIME_WEIGHT_CHANGE                  = false
    NORMALIZER_CHANGE                   = false
    MASK_CHANGE_AFTER_T0                = false
    NEW_OPERATOR_EXECUTABLE             = false
    OPERATOR_SHOPPING                   = false
    DOSE_SHOPPING                       = false
    THIRD_DOSE_OR_ARM                   = false
    ENVIRONMENTAL_INTERVENTION_STARTS   = 0
    MISSING_PARENT_AXIS_RECONSTRUCTED   = false
    MAX_OTHER_OR_DIAGNOSTIC_ENGINE_STARTS = 0
    MAX_RETRIES_OR_REPLACEMENTS_AFTER_PANEL_LOCK = 0

Tommy's `main` (`f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`) is never moved, checked out, merged
or modified. Every git operation uses a separate `GIT_INDEX_FILE`. No parent output is ever
rewritten; corrigenda and claim ledgers are append-only.

### 0.1 Declared limitation of this freeze (recorded before any result)

The verbatim SQDT00 handoff text was lost when this session's context was compacted; only the
structured constraint block, the six ordered questions, the section skeleton and the named stop
tokens survived into the working summary. Consequently **the exact wording of the 38 deliverable
names, of the Q0–Q19 gate texts and of the 16 numbered report explanations is reconstructed here
from the surviving binding constraints, not quoted.** This is recorded as deviation D0 and is
reported in the final disposition. Every constraint that did survive is treated as binding and
is honoured literally.

---

## 1. Inherited frozen objects — bound, not re-derived

| object | source | binding |
|---|---|---|
| LawSpec / engine | `PPAI/ppai_engine.py` via `wsfscrp_core.engine()` | `PPAIEngine(C.SPEC, PPAIParams(gain=1/3, z_index=0), C.TRACER)` |
| fixed-support reader | `WSFSCRP00/wsfscrp_core.py::q_channels` | unchanged |
| scored native steps | `H_GRID = [40,80,...,400]`, `dt = 1/10` | unchanged |
| time weights | trapezoid, exact `Fraction`, `[1/18, 1/9 x 8, 1/18]`, sum `1` | unchanged |
| `W_POST` | `1` exactly (`h0` is not a scored time) | unchanged |
| normaliser | `B = dsum(rho[MA|MB])` at `t0`, exact rational | unchanged |
| masks | `t0_masks`, unordered pair, canonical by sorted site ids | unchanged, never re-derived after `t0` |
| carrier arm 1 | `etcmnfc_core.transpose(st, I, J)` | unchanged |
| carrier arm 2 | `ppai_core.state_cross(st)` | unchanged |
| sham | identity copy | unchanged |
| materiality coefficient | `0.01` | inherited unchanged, never re-tuned |

The engine, the reader and both carrier callables are bound by the sha256 of their source files
in `SQDT00_MASTER_FREEZE_HASHES.json`. The parent artifacts are bound by git blob id in
`SQDT00_PARENT_ARTIFACT_BLOB_BINDING.json`.

---

## 2. The response object

For an arm `X` on descendant `d` with masks `(MA, MB)` and normaliser `B`:

    X_A(h) = dsum(rho_h[MA]) / B
    X_B(h) = dsum(rho_h[MB]) / B          h in H_GRID

    dA(h) = X_A^{arm}(h) - X_A^{SHAM_0}(h)
    dB(h) = X_B^{arm}(h) - X_B^{SHAM_0}(h)

`dsum` accumulates in `Fraction`, which is exact because every IEEE-754 float64 is a dyadic
rational and `Fraction` addition is exact and order-independent. `npz` round-trips the raw
IEEE-754 bytes. Hence the scoring path carries **zero** arithmetic error and
`ETA_ORACLE_L2 = 0` exactly.

At `h0` (the native step 0 of the continuation) the arm and its sham are byte-identical by
construction, so `dA(h0) = dB(h0) = 0` exactly. `h0` is not a scored time; its structural zero is
checked, never scored.

### 2.1 Orthonormal channel coordinates

    u(h) = sqrt(W_h / 2) * (dA(h) + dB(h))
    v(h) = sqrt(W_h / 2) * (dA(h) - dB(h))

    phi(row) = ( u(h_1..h_T) , v(h_1..h_T) )  in  R^{2T},  T = 10, 2T = 20

    M2^2 = sum_h W_h ( dA^2 + dB^2 ) = ||u||^2 + ||v||^2 = ||phi||^2

`M2` is the weighted-L2 response amplitude. The identity `M2^2 = ||u||^2 + ||v||^2` is checked
exactly on every row.

### 2.2 The gauge

The A/B labelling of the two support components is physically meaningless. The admissible gauge
group is **exactly one A/B exchange per descendant**, `eps_d in {+1,-1}`, shared across all
scored times, all arms **and all doses** of that descendant. Under `eps_d = -1`,

    u -> u        v -> -v

Consequences that this freeze fixes in advance:

* `M2` alone is **blind** to an illegal per-time or per-arm swap, because `M2^2 = ||u||^2+||v||^2`
  is invariant under any sign pattern whatsoever. Only the whole-descendant block invariant
  `(u, V (x) V)` detects such an illegality. Every gauge oracle in this programme therefore
  tests the block object, never `M2`.
* With `D` descendants the enumeration is `2^{D-1}` after pinning `eps_1 = +1` (the global sign
  is unobservable).

---

## 3. The quotient estimand

Let the rows be indexed `i = 1..n` with `alpha_i = 1/n`, and let `d(i)` be the descendant of row
`i`. Write `U_ij = <u_i, u_j>` and `V_ij = <v_i, v_j>` (both exactly rational). For a gauge
assignment `eps`, the Gram of the gauged rows is

    Z(eps)_ij = U_ij + eps_{d(i)} eps_{d(j)} V_ij

    G(eps)    = ( double-centred Z(eps) ) / n         (affine mean removed)

    R_0(eps)  = trace G(eps)
    R_k(eps)  = trace G(eps) - lambda_1 - ... - lambda_k      (k = 1, 2)

    R_k = min over eps of R_k(eps)
    I_1 = R_0 - R_1        I_2 = R_1 - R_2

`R_k` is the mean squared residual of the rows about an affine `k`-dimensional model in the
orthonormal coordinates of section 2.1; `I_1` and `I_2` are the first and second explained
increments. `I_1` and `I_2` are the objects the parent programme called `L1` and `L2`.

`R_0` reduces to an exact binary quadratic form,

    R_0(eps) = C - A_const - eps^T M eps,
    C = sum_i alpha_i (U_ii + V_ii),  A_const = sum_ij alpha_i alpha_j U_ij,
    M_pq = sum_{i in p} sum_{j in q} alpha_i alpha_j V_ij,

so `R_0` is **exactly** minimisable over all `2^{D-1}` assignments. This freeze requires that the
minimisation be exact, not sampled: the enumeration is performed by an exact integer Gray-code
sweep after clearing denominators.

---

## 4. The discovery object `FWL2_RELATIVE_QUOTIENT_BASIS_V1`

At the certified argmin `eps*`, with `psi_i = phi_i(eps*) - mu` and
`mu = (1/n) sum_i phi_i(eps*)`:

    Sigma  = (1/n) sum_i psi_i psi_i^T          (a 20 x 20 operator)
    e_1    = the top eigenvector of Sigma       ||e_1|| = 1
    e_2    = the second eigenvector of Sigma    ||e_2|| = 1,  <e_1,e_2> = 0
    P_1    = e_1 e_1^T
    P_2    = e_1 e_1^T + e_2 e_2^T
    c_ik   = <psi_i, e_k>                        (per-row scores)

**Sign canonicalisation, frozen now**: for each `k`, the entry of `e_k` of largest absolute
value is made positive; ties in absolute value are broken by the smallest coordinate index. The
global gauge sign is fixed by pinning `eps*_1 = +1`. Both rules are deterministic functions of
the fitted object and of nothing else.

The object is serialised as **real machine-readable arrays** (`.npz` with float64 arrays and a
companion `.json` carrying the exact rational forms where they exist), never as scalar summaries
only. This is the precise defect that made the parent's frozen-stratum transfer
`NOT_EVALUABLE_FROM_COMMITTED_PARENT_OBJECT`: `GIMB00` serialised
`R_STRATUM_0`, `E_STRATUM`, `P_STRATUM_PLUS/MINUS`, `sector` and support counts, but **never**
the vectors `psi_plus` / `Psi_minus`. A scalar cannot be projected onto.

### 4.1 Forbidden aliases

This object is **not** and must never be called, in any artifact of this programme:

    GIMB00_STRATUM_AXIS
    PARENT_FOUNDER_STRATUM
    RECOVERED_PARENT_MODE
    HISTORICAL_SECOND_MODE

It is a basis fitted to the **FWL2CF00 fresh active panel**, in the FWL2CF00 gauge, in the
FWL2CF00 coordinates. It has no established relation to any GIMB00 object, and this programme
establishes none.

### 4.2 Basis stability gates, frozen before fitting

    BASIS_S0  the fit uses only committed FWL2CF00 bytes, no fresh array
    BASIS_S1  eps* is the exact argmin of R_0 over all 2^{D-1} assignments
    BASIS_S2  the same eps* attains the reported R_1 and R_2
    BASIS_S3  lambda_1 and lambda_2 admit disjoint exact rational enclosures
              (lambda_1 strictly above lambda_2, lambda_2 strictly above lambda_3)
    BASIS_S4  e_1 and e_2 are orthonormal to within a certified residual
    BASIS_S5  leave-one-descendant-out refits keep the principal angle between P_2 and the
              full-fit P_2 below 30 degrees for every left-out descendant
    BASIS_S6  the reconstruction identity holds: R_0 - sum_k c_.k^2 / n = R_2
    BASIS_S7  the object round-trips: reload from disk reproduces every score bit-for-bit

    P2_TRANSFER_LICENSE      granted only if S0..S7 all pass
    E2_AXIS_TRANSFER_LICENSE nested inside P2_TRANSFER_LICENSE, granted only if in addition
                             lambda_2 is separated from lambda_3 by more than the certified
                             enclosure width (otherwise the 2-plane transfers but the axis e_2
                             individually does not)

### 4.3 Duplication invariance

Replacing the row set by two exact copies of itself must leave `R_0/E_TAU`, `I_2/E_TAU` and
`sqrt(I_2)/A_TAU` unchanged. This is required as a proof plus a numerical check, and it is what
licenses comparing a 32-row parent panel with an 8-descendant fresh panel at all.

### 4.4 The required multipliers

The parent failed `QDIM1` with `sqrt(I_2)/A_TAU = 0.570`. This programme reports, **from certified
intervals and never from the rounded 0.570**:

    ENERGY_MULTIPLIER_REQUIRED    = E_TAU / lower(I_2)
    AMPLITUDE_MULTIPLIER_REQUIRED = upper(A_TAU) / lower(sqrt(I_2))

---

## 5. Materiality thresholds and aggregation

Per descendant `d`, from its own twin shams only:

    TAU_MATERIAL_L2[d] = max( ETA_ORACLE_L2,
                              0.01 * || weighted sham drift ||,
                              0.01 * RHO_MED / B * sqrt(W_POST) )

The coefficient `0.01` is inherited unchanged. The cell rule is decided on **exact squares**:

    CELL_MATERIAL_PASS  iff  M2^2 > TAU^2        equality is FAILURE

Aggregation:

    E_TAU = sum_i alpha_i TAU_i^2        A_TAU = sqrt(E_TAU)

**The `alpha[d,o] = 1/16` identity.** With 8 descendants and two doses the row index is `(d, o)`
with `o in {1x, 2x}` and `alpha[d,o] = 1/16`; the threshold is a property of the null and carries
no dose, so `TAU[d,o] = TAU[d]`. Then

    E_TAU = sum_{d,o} (1/16) TAU[d]^2 = (1/8) sum_d TAU[d]^2

which is **identical** to the per-dose aggregate over 8 rows with `alpha_d = 1/8`. The pooled and
the per-dose bounds therefore coincide exactly, and no choice between them can be made after
seeing data.

Aggregation lemmas, inherited and re-proved here: A/B swaps are isometries; weighted centering is
a contraction; orthogonal projection is a contraction. Hence under the all-immaterial null
`R_0 <= E_TAU` and `sqrt(I_2) <= A_TAU`. Because `I_2 <= R_0`, **the modal gate strictly implies
the total gate**; passing `QDIM0` while failing `QDIM1` is therefore not a contradiction but the
designed conservatism.

---

## 6. Dose semantics

    DOSE_1X = EXACT_PARENT_LOCKED_DOSE
    DOSE_2X = EXACTLY_TWO_TIMES_PARENT_LOCKED_DOSE
    gamma_low = 1     gamma_high = 2      THIRD_DOSE_OR_ARM = false

Because `NEW_OPERATOR_EXECUTABLE = false`, `OPERATOR_SHOPPING = false`,
`DOSE_SHOPPING = false` and `MISSING_PARENT_AXIS_RECONSTRUCTED = false`, a `2x` arm is admissible
**only if a dose axis already exists inside the parent's locked arm objects and locked
executables**. This freeze fixes, before looking, the complete list of places where such an axis
could live and the test applied to each:

    A. the committed arm lock object          does it declare a dose, and what value?
    B. the locked callables' signatures       is there a scalar amplitude / strength argument?
    C. the cardinality axis (carrier 1)       can the locked pair list be doubled?
    D. the amplitude axis (both carriers)     is a scaled displacement realisable
                                              (i) without a new executable and
                                              (ii) inside the frozen domain predicate?

If no axis survives A–D, the disposition is `DOSE_2X_STATICALLY_INADMISSIBLE_OR_UNRESOLVED` and
**no fresh panel is built and zero engine starts are spent**. Inventing an axis at this point
would be dose shopping performed with full knowledge that `1x` fell short by a factor near 1.75,
which is exactly the failure mode the constraint block forbids.

The audit is **static**: it evaluates stored states and frozen predicates and performs no engine
step. A zero-step static evaluation is not an engine start and is logged separately as such.

### 6.1 Scaling predictions, frozen before any 2x datum

If a `2x` arm were executed and the response were linear in dose:

    R_k(2x)      = 4 * R_k(1x)          for every k
    I_2(2x)      = 4 * I_2(1x)
    sqrt(I_2)    ratio  =  exactly 2
    TAU, E_TAU, A_TAU   unchanged (they are null quantities and carry no dose)

---

## 7. Stop rules, in strict precedence

    S1  parent provenance not resolvable from a committed branch or a verified bundle
            -> PARENT_PROVENANCE_UNRESOLVED, stop, zero starts
    S2  offline rederivation does not reproduce the parent's committed scores
            -> OFFLINE_REDERIVATION_MISMATCH, stop, zero starts
    S3  basis stability gates fail
            -> NO_P2_TRANSFER_LICENSE, stop, zero starts
    S4  AMPLITUDE_MULTIPLIER_REQUIRED not strictly below 2 (from certified intervals)
            -> PARENT_DOSE_MULTIPLIER_NOT_BELOW_2__NO_FRESH_PANEL_LICENSE, stop, zero starts
    S5  no dose axis survives the static audit of section 6
            -> DOSE_2X_STATICALLY_INADMISSIBLE_OR_UNRESOLVED, stop, zero starts
    S6  the pre-execution oracle is vacuous in any group
            -> VACUOUS_ORACLE, stop before any start
    S7  the fresh panel cannot be filled inside 16 construction starts
            -> INSUFFICIENT_JOINTLY_ELIGIBLE_TARGET_BLOCKS, stop

`S4` and `S5` are independent: `S4` asks whether a doubled dose would be *enough*, `S5` asks
whether a doubled dose *exists*. Both are decided offline, before any fresh panel.

---

## 8. Panel design, frozen now (executed only if S1–S6 all pass)

Seed namespace `66000–66015`, disjoint from every prior use (`61000-61009`, the reserved and
unread `62000-62009`, `63xxx`, `64000-64011`, `65000-65007`). Four cell-specific subqueues of
four, in this frozen order:

    (NEAR, alloc 0) : 66000, 66001, 66008, 66009
    (NEAR, alloc 1) : 66002, 66003, 66010, 66011
    (FAR,  alloc 0) : 66004, 66005, 66012, 66013
    (FAR,  alloc 1) : 66006, 66007, 66014, 66015

Round-robin across the four cells, two acceptances per cell, eight accepted ancestries.
Qualification is the predicate inherited verbatim from the WL2SMF00 constructor: exactly two
eligible components of at least `MIN_SITES = 12` sites under `rho > 0.30`, agreement between the
production and the independent reference mask implementation, `B > 0`, and finite `rho`.

**Parity de-confounding rule, frozen now.** FSCMA00 established that `make_founder` assigns
`(HIST_H, HIST_L)` on even seeds and `(HIST_L, HIST_H)` on odd, and that the WL2SMF00 queue
happened to align even seeds with `FAR`, collapsing geometry, history order and seed parity into
a single axis. Each subqueue above therefore contains two even and two odd seeds, and the
acceptance rule is: accept the first qualifying seed; then accept the next qualifying seed of the
**opposite** parity; only if no opposite-parity candidate qualifies, accept the next qualifying
seed of any parity and record `PARITY_BALANCE_NOT_ACHIEVED` for that cell.

Geometry and allocation remain `NOT_TESTED_IN_THIS_DESIGN`; the panel spans them to widen the
null and the ancestry variance, not to estimate their effects.

---

## 9. Start accounting

    MAX_PANEL_CONSTRUCTION_STARTS = 16
    MAX_TWIN_SHAM_STARTS          = 16
    MAX_ACTIVE_STARTS             = 32
    MAX_TOTAL_ENGINE_STARTS       = 64
    EXPECTED_TOTAL_IF_FIRST_EIGHT_CANDIDATES_QUALIFY = 56
    MAX_RETRIES_OR_REPLACEMENTS_AFTER_PANEL_LOCK     = 0
    MAX_OTHER_OR_DIAGNOSTIC_ENGINE_STARTS            = 0

One constructed descendant state is one start, inherited unchanged from WSFSCRP00. A precursor
shared by an allocation pair is an internal sub-step of that pair. Raw advance-sequence counts
are logged separately for transparency. Every start is entered in an fsync'd `START_ENTER` log
**before** the subprocess launches, so a crashed start can never be silently unspent.

---

## 10. Certification standards

* **EXACT** — a rational identity in `Fraction`, or an exact integer computation. Used for the
  reader, the deltas, `M2^2`, `U`, `V`, `R_0` and the `R_0` gauge minimisation.
* **ENCLOSING** — a certified rational interval `[lo, hi]` containing the true value, obtained by
  exact Sylvester inertia counting on `G - t I` via exact `LDL^T` in `Fraction`, bisected. Used
  for eigenvalues, hence for `R_1`, `R_2`, `I_1`, `I_2` and every ratio built from them.
* **FLOAT-WITH-BOUND** — a float computation accompanied by an explicit backward-stability and
  Weyl bound, used **only** for selecting the gauge argmin of `R_1` and `R_2` among the
  `2^{D-1}` assignments, and only when the runner-up gap exceeds the bound by a stated factor.
  Every reported *value* additionally carries an exact enclosure at the selected argmin.

Float-only reporting is insufficient anywhere in this programme and is never used.

---

## 11. What this programme may never claim

* That the serialised basis is, or recovers, any GIMB00 or founder-stratum object.
* That geometry or allocation has any effect. They are `NOT_TESTED_IN_THIS_DESIGN`.
* That a dose response exists, unless a dose axis was found to exist and both doses were run.
* That `n = 8` ancestries supports a distributional inference. The independent unit is the
  ancestry block; repeated arms, doses and shams within a block are repeated conditions, never
  replications.
* That the parent's `0.570` was "nearly" significant. The reported requirement is a certified
  interval, and a requirement below 2 is a statement about arithmetic, not about physics.
