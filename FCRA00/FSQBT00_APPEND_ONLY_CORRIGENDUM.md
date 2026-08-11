# FSQBT00_APPEND_ONLY_CORRIGENDUM

Append-only. This is a correction of **record and interpretation**. It does **not** amend or rewrite
any FSQBT00 commit, does **not** reclassify the frozen gate, and does **not** repair protocol
conformity. Every number below was independently reproduced in FCRA00 through both a production and
an independent reference path (`PRIMARY_RECOMPUTATION_STATUS = PASS`).

## 1. Magnitude vs direction (the load-bearing prose fix)

The FSQBT00 disposition string `…CARRIER_DIRECTION_REPLICATED_12_OF_12…` conflated two distinct
quantities. Corrected:

* `DIRECT_CARRIER_CONTRAST_MATERIAL = 12/12` — the **magnitude** of the native carrier contrast
  (‖z₂−z₁‖² > (2·TAU)²) holds in all twelve ancestry blocks. Reproduced exactly (12/12).
* `PARENT_E2_SIGN_CONCORDANCE = 10/12` — the **direction** (sign of the fresh e2 carrier contrast vs
  the parent e2 orientation) agrees in ten of twelve blocks. Reproduced exactly (10/12).

**"Direction replicated 12/12" was wrong** and is withdrawn. The direction concordance is 10/12; the
magnitude materiality is 12/12. The combinatorial references for 10/12 are
`79/4096 = 0.0193` (one-sided) and `79/2048 = 0.0386` (two-sided); a licensed p-value is
`NOT_LICENSED` (the sign-flip/exchangeability null for twelve ancestry blocks is not justified, and
the gauge selection is response-informed).

## 2. Frozen e2 transfer

`FROZEN_E2_TRANSFER_AS_FROZEN = NOT_TRANSFERRED`. The frozen e2 incremental energy (4.585·10⁻⁷) is
below the absolute floor E_TAU_FRESH (1.113·10⁻⁶), and it is gated by the P2 per-block failure.
10/12 sign concordance does not rescue it.

## 3. Strict gate vs population non-transfer (the load-bearing interpretation fix)

`FROZEN_P2_TRANSFER_AS_FROZEN = NOT_TRANSFERRED` stands — 3/12 blocks exceeded the frozen tube, so
the preregistered all-block gate failed exactly as written. Reproduced with a **certified**
trichotomy: `65101_NEAR_a1` (×1.222), `65104_NEAR_a0` (×1.137), `65108_NEAR_a0` (×1.058) are
`CERTIFIED_EXCEED`; the other nine `PASS`; none `NUMERICALLY_UNRESOLVED`. Aggregate use and
containment also reproduce: projected energy 3.62× E_TAU, aggregate outside residual 0.701× tube.

**But** `POPULATION_NONTRANSFER = NOT_ESTABLISHED`. The tube was the **maximum of only four**
true-LOBO calibration folds, and the fresh gate required **all twelve** future scores below it —
a strict fixed-panel uniformity gate, not a calibrated population-transfer test. Under exchangeability
of four calibration and twelve future scores, `P(K≥3 above the max of four) = 11/28 ≈ 0.393`, so
3/12 exceedances are unremarkable. FSQBT00 prose that read the failure as
"parent-panel-specific geometry" / "the precise fitted geometry doesn't transfer" **over-claimed**
and is narrowed to: `STRICT_NO_REFIT_ALL_BLOCK_CONTAINMENT = FAIL_3_OF_12`,
`UNIFORM_FIXED_PANEL_CONTAINMENT = NOT_QUALIFIED`,
`POPULATION_P2_NONTRANSFER = INCONCLUSIVE_FROM_THIS_GATE_ALONE`.

## 4. Fresh quotient claim ceiling

The fresh quotient is a **new fit on the same 24 FSQBT00 rows**. "Independent" means independent of
the parent panel, **not** statistically independent of the carrier contrast or the P2 analysis.
Reproduced exactly: `R0 = 4.0924·10⁻⁶`, `I1 = 3.5746·10⁻⁶`, `I2 = 4.411·10⁻⁷`, `R1 = 5.178·10⁻⁷`,
`R2 = 7.669·10⁻⁸`; `I2/R0 = 0.108`, `R1/R0 = 0.127`, `I2/I1 = 0.123`; common argmin for k=0,1,2;
class `RELATIVE_AT_LEAST_TWO__SECOND_BELOW_ABSOLUTE_MATERIALITY`.

## 5. Protocol and evidence record

* `FSQBT00_PROTOCOL_CONFORMITY_STATUS =
  NONCONFORMANT__ONE_UNAUTHORIZED_DIAGNOSTIC_START__NO_OUTCOME_OPENED_PROVEN` (seed 70000).
  Charged starts corrected to **61** (12+24+24+1); the figure 60 was the sealed-programme
  raw-advance count and excluded the probe.
* `FSQBT00_ORIGINAL_TIP_DELIVERY_STATUS = INCOMPLETE_MISSING_FULL_CHECKPOINT_BYTES`; the child chain
  now carries the exact 12 checkpoint bytes (`CURRENT_CHAIN_EVIDENCE_STATUS =
  COMPLETE_AFTER_APPEND_ONLY_CHILD_RECOVERY`). Support-restricted sufficiency re-proved bit-for-bit
  against the recovered full-field trajectories.

An append-only record correction never turns `NONCONFORMANT` into `PASS`, and never makes the
historical FSQBT00 tip self-contained retroactively.
