# FSCMA00 -- protocol freeze

Every item below was written to disk before the first environmental engine start of this
programme. Nothing was refitted afterwards.

## Carrier sentinels (inherited, uniqueness proved)

* **CARRIER_1** = `matched_transposition`
  (`etcmnfc_core.transpose(st, I, J)`),
  superfamily CONSERVATIVE_CARRIER_REDISTRIBUTION.
* **CARRIER_2** = `intensive_reflection`
  (`ppai_core.state_cross(st)`),
  superfamily NONCONSERVATIVE_CARRIER_TRANSFORMATION.

Uniqueness: The parent manifest names exactly one canonical_sentinel_instance per TRAIN superfamily, and no other instance appears anywhere in the parent's scored path. The parent's executable make_ops() constructs exactly two operators and no more. The parent's 12 scored cells are exactly 6 founders x these 2 sentinels.
**VERDICT: PARENT_CARRIER_SENTINEL_IDENTITY_RESOLVED**

## Environmental operators

* **ENV_PRIMARY** `domc_core._perturb_N(st, 0.5)`
  -- N <- clip(N + 0.5*N0, 0, None); additive, global, exact
* **ENV_SECONDARY** `domc_core._perturb_N(st, 0.25)`
  -- statically admissible and, unlike the plan sketched at the start, **executed**, because the
  frozen start-accounting matrix showed it fits.

## The A/B quotient

The endpoint pair is *unordered*, canonicalised per founder by sorted site-id lists, so channel A
of one founder has no a-priori relation to channel A of another. Fitting one family across founders
requires fixing that gauge first.

* Gauge: founder **64001** fixed
  `no_swap`; the remaining five enumerated exhaustively (2^5 = 32).
* Objective: minimum exact weighted residual of the one-mode model, `trace(G) - lambda_1(G)`.
* Winner: swap **[64002, 64006, 64010]**.
* Exactly certified against the runner-up: winner residual upper bound
  5.318515e-06 <
  runner-up lower bound
  9.653798e-06,
  relative gap 0.815.
* **VERDICT: AB_QUOTIENT_IDENTIFIED**

An independent, hypothesis-free rule -- align each founder's CARRIER_1 response in sign with the
gauge founder's -- selects the **same** three founders. The two rules were checked against each
other precisely because the enumeration objective could otherwise be accused of rewarding a
collapsed spread rather than a one-dimensional one.

## No-change declarations

* `NEW_LAWSPEC` = False
* `ENGINE_EQUATION_CHANGE` = False
* `NEW_STATE_VARIABLE_OR_TRACER` = False
* `CHECKPOINT_TIME_CHANGE` = False
* `HORIZON_CHANGE` = False
* `FIXED_SUPPORT_READER_CHANGE` = False
* `DIRECT_RHO_INTERVENTION` = False
* `DYNAMIC_COMPONENT_REDETECTION` = False

## Frozen worst-case start accounting

Written before the first outcome. Caps: PROBE 24, LOCKED 60, TOTAL 84.

| line | planned | actually consumed |
|---|---|---|
| PROBE sham + replicate | 7 | 7 |
| PROBE ENV_PRIMARY | 6 | 6 |
| PROBE ENV_SECONDARY | 6 | 6 |
| PROBE discarded pre-outcome | 0 | 1 |
| LOCKED sham | 6 | 12 |
| LOCKED CARRIER_1 + CARRIER_2 | 12 | 12 |
| LOCKED ENV_PRIMARY | 6 | 6 |
| **total** | **43** | **50** |

**Deviation, disclosed:** the LOCKED sham line cost 12 instead of 6. Stage A of the sealed LOCKED
evaluation did not persist its sham forks, so stage B had to re-derive them. That is an oversight
in my staging design, not a cap breach: LOCKED consumed 30 of 60 and the programme 50 of 84.
