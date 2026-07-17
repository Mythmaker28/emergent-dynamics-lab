# ACCESS-STRUCTURE-00 — Phase 0.7 CORE-SUFFICIENCY-00 power note

**UNSEALED — NO PROSPECTIVE PLAN AUTHORISED — DEV descriptive inputs only.** A defensible power plan **cannot** be set
from the current DEV pilot, for the reasons below. This note records the historical inputs and a conditional sketch so
a future human decision is informed; it authorises nothing and selects no seed.

## Historical valid-world inputs (already-open DEV 50001–50010)

- Deep-feasibility rate: **4/10** worlds (50002, 50004, 50005, 50007) reached a deep-feasible turnover snapshot with
  three alive, distinct targets. The other six were split/lost/ineligible under the frozen no-operator disposition.
- Given deep-feasibility, arm viability was **144/144** (three distinct bijective tracks, coverage < 0.15, uptake
  endpoint present) across all 2×2 arms and all three probe conditions — so within deep-feasible worlds, world-level
  validity was 4/4.
- Net: an outcome-independent eligible-and-valid **world rate ≈ 0.40**, dominated by the deep-feasibility gate, not
  the operator.

## Why a power plan is not defensible now

The primary (twin-referenced) estimand is not a stable, interpretable target:

- world-level `tau_clamped` (normal) = `[−0.00012, −0.02053, −0.00931, −0.04697]`, mean `−0.0192` — small (~1% of the
  ~1.5–2.2 feeding scale), and although consistently negative at world level, it is **sign-variable at the target
  level** and **reverses against the erase reference in 4/4 worlds** (report §9);
- it collapses ~69% under `lam_plus=0` (direct-readout-mediated);
- between-world heterogeneity is large relative to the mean (min/median/max `−0.047 / −0.015 / −0.0001`).

A power calculation on an effect whose **sign depends on the null** and whose magnitude is ~1% would be
non-defensible; optimizing a margin against these DEV values is explicitly disallowed.

## Minimum valid-world requirement (carried, not sealed)

The prior programme’s hard floor of **≥ 18 valid original worlds** is retained as a floor, not a power justification.
At an eligible-and-valid world rate ≈ 0.40, reaching 18 valid worlds implies opening on the order of ~45 candidate
worlds (before any reserve rule) — but this figure is moot until the estimand/null is corrected.

## Conditional sketch (contingent on a corrected null — NOT authorised)

*Only if* a future phase adopts a reference-robust null that isolates the history-bearing component and re-passes DEV,
a world-level plan would: model the original world as the unit; use a one-sided practical margin and a two-sided
equivalence margin frozen from manipulation/sham noise (never from feeding outcomes); apply a simultaneous-interval or
predeclared multiplicity correction across `tau_clamped`, `tau_coupled`, and `interaction`; and size N from the
corrected effect’s world-level dispersion at the ≥ 18 floor. No numbers are set here because the corrected effect does
not yet exist.

Recommendation: **STOP-CORE-SUFFICIENCY.** Revisit power only after a corrected, reference-robust estimand passes a
fresh DEV audit under explicit human authorisation.
