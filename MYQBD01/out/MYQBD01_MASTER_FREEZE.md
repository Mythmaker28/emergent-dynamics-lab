# MYQBD01 — MASTER FREEZE
## MINORITY-Y-Q-BOUND-DERIVATION-01 — raw-only, zero new scientific runs

> Committed **before** any detailed framewise Q trajectory or spatial-array access.
> This mission is response-informed and developmental: the approximate branch means
> (static ≈ 2.369048, mobile ≈ 3.169730) and the observed maximum (28) are already known from
> the repaired PMCR01 parent. The freeze fixes the RULES; it does not claim blinding.

## 1. Exact scientific question

Can the already-recorded `Q` trajectories of the 28 OBFOR01 arms, treated **explicitly as a
development dataset**, provide a **branch-specific** environmental operator, or a conservative
bound, sufficient to map the non-empty `(β, muY)` region into an executable candidate
`(kY, muY)` region for a later **independent** test?

## 2. Eligible arms

All 28 delivered OBFOR01 fresh arms. 14 static (condition S, tag prefix `S__`… here `S`), 14
mobile (condition M). No arm may be removed because its `Q` distribution is unusual. Eligibility
is by delivery, not by outcome.

## 3. Independent unit and event-time convention

- **Independent unit = one world (one arm).** 9 000 in-window frames per arm are NOT 9 000
  independent replicates. Branch-level uncertainty is computed from the **14 arm-level means**.
- **Event time**: the recorded `Q` (series index 20) is written in `Recorder.pre_react`, on the
  post-diffusion pre-reaction state, and finalized every step (`series` has 11 000 rows). It is
  therefore **event-aligned per step** with the Y-birth Binomial. Burn-in = 2000; analysis
  window = steps 2001…11000 (9 000 frames).

## 4. Q-like quantities (never conflated)

`Q_ORGANISER`, `Q_REACTION`, `Q_POSITION(x)`, `Q_LINEAGE`, `Q_AGGREGATE`, `Q_RECORDED`. The
recorded field equals `Q_REACTION = Q_ORGANISER = Q_AGGREGATE` in the one-Y baseline. It does not
equal `Q_POSITION`/`Q_LINEAGE` for a separated descendant.

## 5. Missing / censored frames

`Q` has zero missing values in the delivered arms (to be re-verified in the inventory). `Q = 0`
is a valid observation (no exposure), not a censored frame, and its episodes are analysed
explicitly.

## 6. Frozen PMCR01 persistence and timing thresholds (bound, not re-chosen)

```
T_HORIZON        = 11000
T_WINDOW         =  9000
BURN_IN          =  2000
CAP              = 16
Q_MAX            = 28              (exhaustive admissible-state enumeration; observed max = 28)
D_REL            = 0.05
CORE_R           = 5.0
TAU_SEP_MOBILE   = 125.0           (= CORE_R^2 / (4 D_REL); MOBILE branch only)
TAU_SEP_STATIC   = infinity        (p_hop_Y = 0 -> descendants never separate)
ALPHA_SURVIVAL   = 0.5             (survival to T >= 1/2)
N_STAR           = 10.0            (E[nY(T)] <= 10, the bounded-minority / nY<<CAP proxy)
GAMMA_SEP        = 0.5             (expected separated second centres <= 1/2)
MIN_EVENTS       = 1.0             (a control must fire at least once over the horizon)
```

These are the exact values in `PMCR01_REACHABILITY_REGIONS.json`. Any that was developmental
rather than preregistered is labelled developmental but **kept fixed** for this mission. None is
changed after detailed trajectory access.

## 7. Exact one-Y and two-Y operators

- **One-Y**: `f(z) = (m + (1−m)z)·(1 − p(1−m)(1−z))^c`, `c = min(nSY, free)`,
  `p = min(1, kY·nX·nY)`, `m = muY`, newborns exposed to decay in their birth step. Re-derived
  independently from source, not assumed from PMCR01.
- **Two-Y**: the smallest exact state up to the frozen premature-third-centre boundary,
  distinguishing `ONE_Y`, `TWO_Y_COLOCATED`, `TWO_Y_SEPARATED`, `THREE_OR_MORE_STOP`, `EXTINCT`.
  Whether the process remains Galton–Watson is tested, not assumed (the trial count is `c`, not
  `c·nY`; `p` contains `nY`; co-located Y share a nonlinear channel).

## 8. Candidate-region decision rule (frozen now)

For each **mobile** arm `i`, derive its exact eligible region `R_i ⊂ (kY, muY)` using the
**strongest operator justified** by the phase, spatial-recoverability, reduction-validity and
feedback analyses. Primary developmental region:

```
R_ALL_MOBILE = intersection of R_i over ALL 14 mobile arms
```

- No arm may be removed to make the intersection non-empty.
- A point estimate from the pooled frame mean is **insufficient**; the region must be built from
  arm-level operators with arm-level uncertainty.
- Robustness diagnostics (reported, not used to relax the rule): leave-one-arm-out
  intersections, arm-level median region, per-arm boundary contributions, sensitivity to
  event-phase uncertainty, to certified rare-Y error, and to the frozen thresholds without
  retuning them.

## 9. Terminal dispositions (exactly one)

```
EXISTING_Q_DATA_SUPPORTS_DISCOVERY_DERIVED_EXECUTABLE_Y_REGION
EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED
EXISTING_ENVIRONMENT_OPERATOR_STRUCTURALLY_PRECLUDES_WINDOW
```

The positive disposition requires ALL of: all 28 arms accounted for; all 14 mobile arms
included; no frame pseudo-replication; Q event-phase resolved; mobile spatial environment
resolved; one-Y operator verified; two-Y state operator verified; frozen-environment error
controlled; no target-derived Y outcome; mobile region positive width; all-arm intersection
positive width; no single arm creates the region; no favourable subset selection;
`SCIENTIFIC_RUNS_USED = 0`.

Structural preclusion requires the **exact operator** to prove no admissible `(kY, muY)` can meet
the frozen mobile conditions even under the most favourable admissible environment. Failure on
the 14 observed arms is not structural proof; wide uncertainty is not; a missing ledger is not.

## 10. Claim ceiling

A positive result means only that the developmental `Q` data support a candidate region eligible
for **one** independent prospectively frozen test. It is not a confirmation of the region, not a
confirmed `kY` window, not confirmed persistence or separation, and never reproduction or
heredity. No later wording may erase the `POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC` status of the 28
arms.
