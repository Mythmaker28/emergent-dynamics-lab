# FCDDH00 — DEPENDENCY FIREWALL REPORT

Zero engine starts. Frozen before the first construction start.

## 1. Static constructs

Every FCDDH00 module was parsed. Across all 17
modules:

* banned constructs (`eval`, `exec`, `compile`, `__import__`, `importlib`, `runpy`, `globals`,
  `locals`, `vars`, `delattr`): **none**, except the single declared allowlist entry
  `{"fh_oracle.py": ["setattr"]}` — fh_oracle.py contains exactly one setattr, inside a negative control that REQUIRES a PermissionError; it is unreachable from any construction, acquisition or scoring path;
* dynamic imports (`importlib`, `runpy`, `pkgutil`): **none**;
* unresolved `getattr` (a second argument that is not a literal): **none**;
* string-to-call dispatch, filename inference and seed-label inference: **none**;
* `clean = True`.

The resolved-symbol dependency graph — every import and every resolved attribute call, per
module, with its SHA-256 and git blob id — is in `DEPENDENCY_FIREWALL_GRAPH.json`.

## 2. Direction of allowed dependence

```
fh_core  (certified interval arithmetic, frozen estimand chain)   <- no FCDDH00 imports
fh_ref   (independent reference)                                  <- imports NOTHING from fh_core
fh_decode                                                         <- fh_core, fh_ref
DISCOVERY_AXIS_TRAINER_V1                                         <- fh_core ONLY
HOLDOUT_FIXED_AXIS_SCORER_V1                                      <- fh_core ONLY
EXACT_RANDOMIZATION_ENUMERATOR_V1                                 <- fractions ONLY
fh_disc  (discovery driver)                                       <- fh_core, fh_decode, fh_ref, trainer, scorer
fh_hold  (hold-out driver)                                        <- fh_core, fh_decode, scorer, enumerator
```

* `HOLDOUT_FIXED_AXIS_SCORER_V1` imports the trainer: **False**.
* `DISCOVERY_AXIS_TRAINER_V1` references any of FSQBT00 / FCRA00 / WL2SMF00 / FWL2CF00:
  **True**.
* `fh_ref` imports `fh_core`: **False** — the reference is a genuinely independent second path
  (trapezoid contraction matrix, reverse-order summation, explicit rotation matrix, mu-form
  residual, explicit eight-row signed assembly, argmin gauge, float64 throughout).

## 3. Trainer scope enforcement

`DISCOVERY_AXIS_TRAINER_V1.assert_discovery_only` rejects any source path that does not begin with
`/home/claude/sweep/FCDDH00/DISCOVERY_` and any path containing `HOLDOUT`, `holdout`, `FSQBT00`, `FCRA00`, `WL2SMF00`
or `FWL2CF00`. `fit` refuses any ancestry count other than twelve, any non-ascending manifest and
any duplicate id. Oracle groups Q0B, Q0K and Q0L exercise all of these with required-to-fail
mutations.

## 4. Scorer immutability

`HOLDOUT_FIXED_AXIS_SCORER_V1.load_axis` refuses an axis whose `SOURCE`, `AXIS_SPACE` or
`ESTIMAND` differs from the frozen strings, whose npz hash does not match, or whose npz and json
vectors disagree. `FrozenAxis` raises `PermissionError` on any in-place mutation. `score_block`
raises on any request to center, rescale or reorient. The module contains no `eig`, `eigh`, `svd`,
`pca`, `lstsq` or `pinv`. Oracle groups Q0M and Q0N exercise all of these.

## 5. The only permitted search on the hold-out path

Finite exhaustive enumeration of the inherited linked A/B gauge under the immutable parent-P2
residual criterion (`enumerate_linked_gauge`), which is label-blind and axis-blind and returns the
complete co-optimal orbit. No continuous optimizer, no threshold selection, no model comparison.

## 6. Raw-lock guard

`fh_decode.require_raw_lock` is the first statement of both `fh_disc.main` and `fh_hold.main`; it
raises `PermissionError` unless the corresponding `FCDDH00_<ROLE>_ACTIVE_RAW_LOCK.json` exists.
Oracle group Q0R exercises it in both directions.

## 7. Oracle

`FCDDH00_PREANALYSIS_ORACLE_STATUS = PASS` —
23 groups, all non-vacuous (True), all passing (True),
58 required-to-fail mutations, engine starts
0. The ten separate perturbations demanded by the authorization — a weight, a
scored time, a reader coefficient, a mask byte, a P2 coefficient, a carrier label, a geometry
label, an ancestry role, a TAU and a raw hash — are individually recorded in
`negative_controls`, together with the unpaired-allocation-membership control. A vacuous
self-comparison is itself rejected as a control.
