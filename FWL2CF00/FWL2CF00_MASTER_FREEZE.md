# FWL2CF00_MASTER_FREEZE

Written and hashed before any engine instantiation and before any fresh numeric row exists.

## Ordered questions

    Q_PRIMARY_1 = do all 32 locked carrier cells exceed their own prospective weighted-L2 threshold
    Q_PRIMARY_2 = if so, what is the fresh gauge-invariant carrier quotient structure
    Q_PRIMARY_3 = does the exact frozen parent founder-stratum object transfer without refit
    Q_PRIMARY_4 = if transfer passes, what is its origin

`FROZEN_FACTOR_PIPELINE_STATUS = PARENT_OBJECT_NOT_EVALUABLE`, declared here, before any fresh
data. GIMB00 serialised only scalar summaries of its founder-stratum object; the axis vectors
`psi_plus` and `Psi_minus` are in no committed parent tree. Rebuilding them would mean reopening
and refitting the historical exposed active rows, which this handoff forbids. Therefore
**Q_PRIMARY_3 = NOT_EVALUABLE_FROM_COMMITTED_PARENT_OBJECT and Q_PRIMARY_4 = NOT_REACHED**, while
Q_PRIMARY_1 and Q_PRIMARY_2 remain fully eligible. Predeclared fresh factor objects may still be
evaluated and may only be labelled `FRESH_FACTOR_EFFECT_NOT_PARENT_STRATUM_EXPLANATION`.

## Panel, arms, gauge

16 sealed descendants, 4 upstream ancestry blocks, `g in {NEAR,FAR}` manipulated (G1),
`a in {0,1}` neutral complementary-allocation members (H3). Two frozen carrier arms per
descendant, taken only from `FUTURE_ACTIVE_CARRIER_ARM_LOCK.json`:

* `CARRIER_1` = `etcmnfc_core.transpose(st, I, J)`, code sha256 `b9c878acd70ab6d9`,
  declared touch set `['Mf']`, applied at the descendant t0.
* `CARRIER_2` = `ppai_core.state_cross(st)`, code sha256 `88945808a458afab`,
  declared touch set `['Mf']`, applied at the descendant t0.

`EXPECT_STRUCTURAL_ZERO_AT_H0 = true` for both arms: each writes `Mf` only, never `rho`, and the
reader integrates `rho` over the immutable masks, so `r(h0) = (0,0)` exactly.

Gauge: one optional A/B swap per descendant, shared across all scored times AND both carrier arms.
`u -> u`, `v -> -v`. A per-time, per-arm, per-row, per-geometry-cell or per-contrast swap is not
the gauge. `M2` alone is known to be blind to some illegal per-time swaps and may not validate
scope; the whole-descendant block reconstruction oracle does.

## Estimand

    X_A[r,d,h] = sum_i M_A0[d,i] rho[r,d,h,i] / B[d]        (raw, undifferenced)
    delta_A[d,o,h] = X_A[INT,d,o,h] - X_A[SHAM_0_REPLAY,d,h]
    z[d,o] = concat_h( sqrt(w_h) delta_A , sqrt(w_h) delta_B )
    M2[d,o]^2 = sum_h w_h (delta_A^2 + delta_B^2) = ||u||^2 + ||v||^2

## Immutable thresholds, bound not recomputed

Per descendant, the exact rational `B`, `RHO_MED`, `G2^2`, `ETA_ORACLE_L2 = 0`,
`TAU_DYNAMIC_L2^2`, `TAU_SITE_L2^2`, `TAU_MATERIAL_L2^2` and the dominance label are taken from
`WL2SMF00_NUMERICAL_THRESHOLD_LOCK.json`. Replay values are checked against the lock as an oracle;
the **locked** threshold remains operative in every decision.

    alpha[d,o] = 1/32 per response row; n stays 4 ancestry blocks
    E_TAU (exact) = 94971782624215449372940448202388861614592487373856502632877747223704158377180586190926260126920895296469857633869450374828841869300240540628201693035479592728752747858939873397275255928213618043841767033751206157047236404723546862193311329272532071381826145224985476468349733442404626780609007765230237258264815819042770917252979754653520523376729950209975802734303184822432198546952386897963791448505726345309017687531317798164970074783764920958994677852283471320591456038400817089923729659633668889479664962119678575008028572844582229/85254207097581195196360685833334841806458635450440357368014475639111582765778802658560874787206328810458811290992179102132567347005519760082752203313084408777338700378673559596172489761376313075533369294386288559633683179348594965290695706796180845292814524401856583503665457983860680600492790098557880570116992035832363742338581466982939837988482949960321780236099328263623978233416861909086833626737297934373808162416235357881368522932217337536557322566024934357390164560325357549438411603284859983413273477075339927475941907607461888000000
    E_TAU (float) = 1.113984e-06
    A_TAU (float) = 1.055454e-03

## Cell rule (exact squares; no floating square root in the decision path)

    PASS iff lower(M2^2) >  upper(TAU_MATERIAL_L2^2)
    FAIL iff upper(M2^2) <= lower(TAU_MATERIAL_L2^2)
    otherwise NUMERICALLY_UNRESOLVED.  Equality is FAILURE.

Global: any certified FAIL -> ALL_CELL_MATERIALITY = FAIL; else any unresolved -> UNRESOLVED;
else PASS_32_OF_32. The complete-panel gate passes only on 32 of 32.

## Quotient (only after PASS_32_OF_32)

    R_k = global min over linked descendant swaps, affine mean and orthonormal k-dim model
    I1 = R0 - R1 (parent alias L1)      I2 = R1 - R2 (parent alias L2)
    I1_interval = [lower(R0)-upper(R1), upper(R0)-lower(R1)]
    I2_interval = [lower(R1)-upper(R2), upper(R1)-lower(R2)]
    Q_RATIO_SQ = I2/I1 in the decision path; Q_RATIO = sqrt only for display

    QDIM0 lower(R0) > upper(E_TAU)
    QDIM1 lower(sqrt(I2)) > upper(A_TAU)
    QDIM2 lower(Q_RATIO_SQ) > 0.01
    QDIM3 lower(I2/R0) >= 0.05
    FRESH_QUOTIENT_AT_LEAST_TWO_PASS = all four

Boundaries: `I2/I1` exactly 0.01 FAILS; share exactly 0.05 PASSES; a certified interval crossing a
boundary is `NUMERICALLY_UNRESOLVED`; `upper(R0)<=0` DEGENERATE_TOTAL_SCATTER; `upper(I1)<=0`
DEGENERATE_FIRST_INCREMENT; `upper(I2)<=0` NO_SECOND_INCREMENT; an interval touching zero forbids
the corresponding division or square root. `0 <= I2 <= R0` makes QDIM1 imply QDIM0; both fields are
kept as a consistency oracle. `R0 > 20*E_TAU` is the boundary condition at share exactly 0.05, not
a necessary condition when the observed share is larger.

Direct one-family reconstruction, evaluated over EVERY co-optimal M1:
`upper(R1/R0) < 0.05` and every row's `upper(ONE_FAMILY_CELL_RESIDUAL) < 0.10`; equality at 0.10
fails; the parent certified-zero denominator rule applies.

## Optimiser certification

All `2^(16-1) = 32768` linked swap assignments are enumerated after removing the single global
duplicate. `R0` is certified **exactly** for every assignment, because
`R0(eps) = C - ||ubar||^2 - ||sum_d eps_d V_d||^2` reduces to an exact binary quadratic form.
`R1` and `R2` are enumerated exhaustively in float64 over all 32768 with a Weyl / backward-stability
error bound, and the argmin plus every near-tie is then certified in exact rational arithmetic by
Sylvester inertia. If the certified margin between the winner and the runner-up does not exceed the
error bound by at least a factor of 100, the result is `FRESH_CARRIER_QUOTIENT_NUMERICALLY_UNRESOLVED`.

## Budget

    SHAM_0_RECONSTRUCTION = 16      ACTIVE_CARRIER = 32      SETUP_OR_DIAGNOSTIC = 0
    TOTAL_MAXIMUM = 48;  zero retries; tranches independent; unused starts are not repurposable
    START_ENTER is durably appended and fsynced before each subprocess launch; the launch consumes
    the continuation even if the child dies before its first scored output.

Frozen sham schedule: ['65000_FAR_a0', '65000_FAR_a1', '65000_NEAR_a0', '65000_NEAR_a1', '65001_FAR_a0', '65001_FAR_a1', '65001_NEAR_a0', '65001_NEAR_a1', '65002_FAR_a0', '65002_FAR_a1', '65002_NEAR_a0', '65002_NEAR_a1', '65003_FAR_a0', '65003_FAR_a1', '65003_NEAR_a0', '65003_NEAR_a1']

Frozen active schedule (opaque ids assigned before execution; labels are not decoded until the raw
panel lock is committed and independently read back):
{
 "65000_FAR_a0|CARRIER_1": "5c4707ace8f852fa",
 "65000_FAR_a0|CARRIER_2": "0a8d3459ba8ad519",
 "65000_FAR_a1|CARRIER_1": "c39e94f24febc701",
 "65000_FAR_a1|CARRIER_2": "c928d27c1dce9687",
 "65000_NEAR_a0|CARRIER_1": "13ee2319c8a5a39a",
 "65000_NEAR_a0|CARRIER_2": "c03fa623b4f9d8fc",
 "65000_NEAR_a1|CARRIER_1": "a5a8c7eb71ed6f32",
 "65000_NEAR_a1|CARRIER_2": "57b88ff102fd7524",
 "65001_FAR_a0|CARRIER_1": "083a37e73654a779",
 "65001_FAR_a0|CARRIER_2": "f220aaf448820733",
 "65001_FAR_a1|CARRIER_1": "7969ff9397e2e450",
 "65001_FAR_a1|CARRIER_2": "ee1ef4f26e7e9503",
 "65001_NEAR_a0|CARRIER_1": "7d9a44a7bbb92ad7",
 "65001_NEAR_a0|CARRIER_2": "f4022020c0243ddf",
 "65001_NEAR_a1|CARRIER_1": "31c07e2a6e9b2ba8",
 "65001_NEAR_a1|CARRIER_2": "0b47777b2bc2502a",
 "65002_FAR_a0|CARRIER_1": "fefd00d71ff40bc2",
 "65002_FAR_a0|CARRIER_2": "d3f483a8c80ffe74",
 "65002_FAR_a1|CARRIER_1": "6876a03b2141f347",
 "65002_FAR_a1|CARRIER_2": "f6ed76755751184b",
 "65002_NEAR_a0|CARRIER_1": "2111c405acafea54",
 "65002_NEAR_a0|CARRIER_2": "36a12f4fa8410a3c",
 "65002_NEAR_a1|CARRIER_1": "70eee30623389b24",
 "65002_NEAR_a1|CARRIER_2": "1ad12ee40f9c35db",
 "65003_FAR_a0|CARRIER_1": "bd5103d47ba32082",
 "65003_FAR_a0|CARRIER_2": "1f653f815c017b2e",
 "65003_FAR_a1|CARRIER_1": "8d17fb32b19ea76c",
 "65003_FAR_a1|CARRIER_2": "1288d174a7c08f39",
 "65003_NEAR_a0|CARRIER_1": "2110e6dd6b32298a",
 "65003_NEAR_a0|CARRIER_2": "d6a1e206be75362e",
 "65003_NEAR_a1|CARRIER_1": "749ce69dad740465",
 "65003_NEAR_a1|CARRIER_2": "908f01f25b64b453"
}

## Append-only

    WSFSCRP00 / FSCMA00 / GIMB00 / WL2SMF00 _DISPOSITION_REWRITTEN = false
    PARENT_THRESHOLDS_RECOMPUTED_OR_CHANGED = false
    PARENT_PANEL_MEMBERSHIP_CHANGED = false
    HISTORICAL_ACTIVE_ROWS_OPENED_OR_REFIT = false

WL2SMF00 prospectively qualified descendant-specific weighted-L2 materiality thresholds and sealed
a G1 x H3 target panel before any active outcome. It did not measure a carrier response. FWL2CF00
reconstructs the missing canonical sham reference series without recalibration, executes only the
two already locked carrier arms, and evaluates the predeclared quotient and factorial objects. No
historical active result or parent threshold is reclassified.

## Claim ceiling

RESPONSE_INFORMED_EXPLORATORY_DEV, PROSPECTIVELY_LOCKED_PANEL_AND_THRESHOLDS, one LawSpec, one
checkpoint and horizon, fixed-support reader, FOUR independent ancestry blocks, finite designed
panel, single-executor internal oracle, not independent review, not confirmatory, not population
inference. 16 descendants and 32 arms are never independent replications. No signed history claim
under H3. No physical A/B identity. No intrinsic or universal rank. No environmental claim from a
carrier-only programme.
