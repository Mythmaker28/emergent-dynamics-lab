# FSQBT00_MASTER_FREEZE

`FRESH_SERIALIZED_QUOTIENT_BASIS_TRANSFER_00`.
Written, hashed and committed **before any parent npz, reader series, response vector, basis
array, score array or candidate state is opened**. Source code, git metadata, schemas and prose
were inspected before this commit; numerical science arrays were not.

Workdir `/home/claude/sweep/FSQBT00`, branch `dev/fresh-serialized-quotient-basis-transfer-00`,
created from the exact SQDT00 tip `16717582e7f0dfd371f21c56465e11113d8b6675`.

---

## 0. Scope, restated as binding

    OWNER = Tommy
    PARENT_PROGRAM        = SQDT00
    PARENT_TIP            = 16717582e7f0dfd371f21c56465e11113d8b6675   (resolved from the branch)
    PARENT_SCIENCE_PARENT = 96c7d295e72106cd949d810fa92807c2514e7449   (FWL2CF00 commit 6)
    TOMMY_MAIN            = f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77   (verified, never touched)

    EXECUTION_MODE = ONE_EXECUTOR_SEQUENTIAL
    PARALLEL_AGENTS_AUTHORIZED = 0    PARALLEL_REVIEWERS_AUTHORIZED = 0

    DISCOVERY_OBJECT = FWL2_RELATIVE_QUOTIENT_BASIS_V1   (immutable; never re-fitted/re-versioned)
    DISCOVERY_SOURCE = EXACT_COMMITTED_FWL2CF00_ACTIVE_PANEL_ONLY
    TRANSFER_TARGET  = EXACT_COMMITTED_PARENT_ARRAYS mu,P1,P2,e1,e2  (subject to corrected LOBO license)

    FRESH_INDEPENDENT_ANCESTRY_BLOCKS = 12   FRESH_DESCENDANTS_PER_BLOCK = 1
    FRESH_CARRIER_ARMS = EXACT_TWO_HISTORICAL_FWL2CF00_CARRIERS
    FRESH_DOSE = EXACT_HISTORICAL_1X_ONLY     FRESH_ACTIVE_ROWS = 12*2 = 24

    MAX_PANEL_CONSTRUCTION_STARTS = 24  EXPECTED 12
    MAX_TWIN_SHAM_STARTS = 24           EXPECTED 24
    MAX_ACTIVE_STARTS = 24              EXPECTED 24
    MAX_OTHER_OR_DIAGNOSTIC_STARTS = 0  MAX_RETRIES_AFTER_PANEL_LOCK = 0
    MAX_TOTAL_ENGINE_STARTS = 72        EXPECTED_IF_FIRST_QUALIFY = 60
    UNUSED_STARTS_MAY_BE_REPURPOSED = false

    NEW_OPERATOR_EXECUTABLE = NEW_DOSE = SECOND_DOSE = false
    NEW_LAWSPEC = ENGINE_EQUATION_CHANGE = NEW_STATE_VARIABLE_OR_TRACER = false
    READER_CHANGE = MASK_REDETECTION = CHECKPOINT_TIME_CHANGE = false
    HORIZON_OR_TIME_WEIGHT_CHANGE = NORMALIZER_CHANGE = false
    GEOMETRY_OR_ALLOCATION_CAUSAL_CLAIM = ENVIRONMENTAL_ARM = QPU_ACCESS = false
    PUSH_AUTHORIZED = DRAFT_PR_AUTHORIZED = WORKFLOW_TRIGGER_AUTHORIZED = false
    TOMMY_ACTION_REQUIRED = TOMMY_GIT_ACTION_REQUIRED = false

**The twelve ancestry blocks are the ONLY independent units.** Carriers, channels, sites and
scored times are repeated conditions. n is never reported as 24, 48, #sites or #times.

---

## 1. The scientific question

Does the exact response-informed `FWL2_RELATIVE_QUOTIENT_BASIS_V1` transfer — with **no** refit,
rescale, recenter or rotation — to twelve truly fresh ancestry blocks under the exact same two
historical carriers at their exact historical 1x dose? The only representation freedom is the
predeclared legal A/B linked-swap gauge. This programme **does not** construct a new dose axis;
SQDT00 proved the 2x is statically inadmissible, and designing a new operator after seeing the
~1.754 deficit would answer a different, response-informed question.

---

## 2. The mandatory correct-unit LOBO audit (decisive, before any fresh state)

**Owned finding, from the SQDT00 artefacts not its prose.** SQDT00's stability loop reads
`for dleft in range(16): keep = [i for rows if D_OF[i] != dleft]`. `D_OF` maps a row to its
**descendant** (0..15), so each fold removed **one descendant (2 rows)** — this is
leave-one-**descendant**-out (LODO), over 16 folds, and produced the reported 3.14 degrees. The
independent unit is the **ancestry block**, so the correct stability refit removes **one block
(4 descendants = 8 rows)** per fold, giving **4 folds**. SQDT00's audit is therefore
`INCORRECT_LODO`, and **no transfer license is inherited** until the true LOBO is computed here.

FWL2CF00 panel structure (bound from the committed panel):

    4 ancestry blocks : seeds 65000, 65001, 65002, 65003
    16 descendants    : block x {FAR,NEAR} x {alloc a0,a1}
    32 rows           : descendant x {CARRIER_1, CARRIER_2}

The true LOBO computation (a **correction of the frozen gate**, not a new analysis):

* remove one complete ancestry block at a time (4 folds), each dropping its 4 descendants / 8 rows;
* equal block weights, then the exact inherited within-block row weights;
* the exact legal linked A/B gauge (one optional exchange per descendant, shared across carriers
  and all scored times);
* fit `mu_minus_b`, `P2_minus_b`, `e2_minus_b` on the remaining three blocks only;
* reconstruct the omitted block **out of sample** against the fold-specific object, minimising its
  legal linked-swap quotient distance in the same per-line units the future transfer will use;
* the full-object reconstruction of the omitted block is an explicitly **in-sample** diagnostic
  that cannot calibrate a tube;
* `mu, P1, P2, e1, e2` in the serialized V1 object are **never** changed; no new rotation,
  threshold, solver, subset or gauge is chosen after seeing a fold.

Stored as `FWL2_RELATIVE_QUOTIENT_BASIS_V1_LOBO_AUDIT`; V1 is never overwritten or silently
versioned.

### 2.1 Corrected nested licenses (SQDT00 gates, now on the 4 true folds)

    BASIS_S0 = exact parent rederivation and an independent implementation agree
    BASIS_S1 = same certified linked-swap argmin for k=0,1,2 (full object)
    BASIS_S2 = full I2/I1 > 0.01 and full I2/R0 > 0.05
    BASIS_S3 = every true-LOBO fit has a certified common linked-swap argmin for k=0,1,2,
               positive I2 and both preserved relative gates
    BASIS_S4 = min squared alignment full_P2 vs LOBO_P2 > 0.80
    BASIS_S5 = min squared projective alignment full_e2 vs LOBO_e2 > 0.64
    BASIS_S6 = max complete-ancestry-block contribution to I2 < 0.50
    BASIS_S7 = serialized reload and mutation oracles pass

    P2_TRANSFER_LICENSE_CORRECTED = S0 and S1 and S2 and S4 and S6 and S7
    E2_AXIS_TRANSFER_LICENSE_CORRECTED = P2_TRANSFER_LICENSE_CORRECTED and S3 and S5 and S6

Strict inequalities; equality FAILS. The 0.01/0.05/0.80/0.64/0.50 boundaries are tested before
any fold result is read. E2 requires certified `lambda1 > lambda2 > lambda3` for the full object
and each fold (a lambda2/lambda3 gap alone does not prevent rotation with e1). Certify eigen
residuals, orthonormality, both eigengaps and propagated projector/axis error; a bitwise disk
round-trip alone does not certify the axis.

### 2.2 The transfer tube

    TUBE_P2_LOBO = max over the 4 folds of
      [ certified upper bound on the omitted block's mean-per-line quotient residual to
        mu_minus_b / P2_minus_b ]  +  certified numerical propagation bound

Serialized as one exact conservative rational threshold with its exact mean-per-line units, block
and line weights and held-out gauge rule. A descendant-level or in-sample tube may not be reused
because its number is smaller.

### 2.3 License consequences

    P2_CORRECTED == false        -> FRESH_PANEL_LICENSE = NO ; ENGINE_STARTS = 0
    P2 pass, E2 fail             -> FRESH_PANEL_LICENSE = YES ; TRANSFER_TARGET = FROZEN_P2_ONLY ;
                                    SIGNED_E2_CLAIMS = FORBIDDEN (route to the projective-P2 branch)
    P2 pass, E2 pass             -> FRESH_PANEL_LICENSE = YES ; TRANSFER_TARGET = FROZEN_P2_AND_e2

---

## 3. Inherited frozen objects (bound, never re-derived)

Engine/LawSpec, founder generator, history family and settle rule, checkpoint time, fixed-support
`t0` masks, reader `q_channels`, normaliser `B = dsum(rho[MA|MB])`, horizon `H_GRID=[40..400]`,
`dt=1/10`, trapezoid weights `[1/18, 1/9 x8, 1/18]` (sum 1), `W_POST=1`, materiality coefficient
`0.01` — all exactly as qualified in WSFSCRP00/WL2SMF00/FWL2CF00. Carrier 1
`etcmnfc_core.transpose(st,I,J)`, carrier 2 `ppai_core.state_cross(st)`, sham identity copy, at the
exact descendant `t0`, touch-set `{Mf}`, dose = exact historical 1x. Bound by source-file sha256 in
`FSQBT00_MASTER_FREEZE_HASHES.json`; parent artifacts bound by git blob id in
`PARENT_PROVENANCE_BINDING.json`.

## 4. Weighted-L2 response, gauge, weights

    dA(h)=X_A[INT]-X_A[SHAM_0]   dB(h)=X_B[INT]-X_B[SHAM_0]
    z = concat_h( sqrt(w_h) dA , sqrt(w_h) dB )   in R^20
    M2^2 = ||z||^2 = ||u||^2 + ||v||^2   (u=(dA+dB)/sqrt2 weighted, v=(dA-dB)/sqrt2 weighted)

Legal gauge: exactly one optional A/B exchange per ancestry block (per descendant, one per block
here since one descendant per fresh block), shared across both carriers, all scored times, and all
transfer/quotient calculations that jointly use those rows. Per-carrier / per-time / per-channel /
per-row orientation is forbidden. Fresh row weights `alpha[b,o] = 1/(12*2) = 1/24`;
`E_TAU_FRESH = sum_b TAU_b^2 / 12`; `A_TAU_FRESH = sqrt(E_TAU_FRESH)`. Exact rationals or certified
intervals throughout; equality fails unless a gate rule says otherwise.

## 5. Materiality threshold (exact WL2 rule, unchanged)

    TAU_b = max( ETA_ORACLE_L2_b, 0.01*||weighted sham drift||_b, 0.01*RHO_MED_b/B_b*sqrt(W_POST) )

`ETA_ORACLE_L2` is an exact/certified arithmetic bound, not a fitted noise distribution. Cell rule
on exact squares: `M2^2 > TAU^2`; equality is FAILURE. TAU decides materiality; z is never divided
by TAU.

## 6. Fresh candidate queue (deterministic, metadata-only)

Smallest integer `N >= 65000`, divisible by 100, with `N..N+23` disjoint from every historical,
held-out, reserved, generated, opened or exposed seed/namespace, and none in `62000-62009`
(reserved and unread) or `64000-64011`. If a hundred-block is unclean, increment N by 100 and
retry (provenance/seed-ledger inspection only, never outcome arrays). Map to four locked
subqueues, round-robin, three acceptances each:

    c=0 (NEAR,a0) seeds N+0+4j ; c=1 (NEAR,a1) N+1+4j ; c=2 (FAR,a0) N+2+4j ; c=3 (FAR,a1) N+3+4j ; j=0..5

Nuisance labels are balanced only — no geometry/allocation/interaction effect is identified. A
failed candidate stays charged and logged; never repaired. Panel membership sealed before any
sham; at the first active byte all twelve are consumed for every future held-out role.

## 7. Stop precedence (first applicable)

    1 parent provenance/content defect
    2 master freeze not proven prior to numerical loading
    3 ancestry-block mapping unavailable
    4 CORRECT_LOBO P2 license fails            -> NO fresh panel, 0 starts
    5 pre-execution oracle / dependency firewall fails
    6 twelve-block panel incomplete in 24 construction starts
    7 sham twin / prospective threshold foundation fails
    8 preactive lock / readback fails
    9 active schedule incomplete
    10 runtime oracle / raw manifest / raw-only readback fails
    11 delivery integrity fails

## 8. Certification standards

EXACT (Fraction) for reader, deltas, M2^2, U, V, R0 and its gauge minimisation. ENCLOSING
(certified rational intervals via exact Sylvester inertia by Bareiss leading-minor sign sequences +
Weyl slack) for eigenvalues, hence R1,R2,I1,I2, the tube residuals, and every alignment/energy
gate. FLOAT-WITH-BOUND only to seed brackets and select the gauge argmin, always with an exact
enclosure at the selection. Float-only reporting is insufficient anywhere.

## 9. Claim ceiling (maximum positive claim)

On twelve fresh, independently generated ancestry blocks under the exact two historical carriers at
their exact historical 1x dose, the response-informed FWL2 P2/e2 object — first requalified by
**true leave-one-ancestry-block-out** analysis — transferred without refit to this exact
developmental panel. If only P2 passes, say P2 (never e2). If the second coordinate is below
absolute materiality, say so in the same sentence. Always forbidden: retroactive reclassification
of GIMB00/FWL2CF00/SQDT00; any claim a 2x dose exists or works; e2 as a causal mechanism; intrinsic
rank exactly two; geometry/allocation/founder-stratum/environmental attribution; operator
specificity without a separately material direct contrast; population/individuality/reproduction/
life/AGI claims; counting descendants, carriers, channels, sites or times as replications.

## 10. Deviations carried in (append-only, never repaired)
D0 (SQDT00 handoff text lost to compaction), D1 (SQDT00 full-clone substituted by object-db
extraction + cross-version tree id), D2 (inherited stale FWL2CF00 bundle-digest record). These are
historical facts; parent artefacts are not rewritten. This programme additionally records, as an
append-only corrigendum, that **SQDT00 BASIS_S5 used leave-one-descendant-out, not
leave-one-ancestry-block-out** — corrected here without mutating the V1 object.
