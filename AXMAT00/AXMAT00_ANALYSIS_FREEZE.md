# AXMAT00 — ANALYSIS FREEZE

`A_X_MATERIALITY_SEMANTICS_AND_SHARPNESS_AUDIT_00`
`PROGRAMME_TYPE = OFFLINE_METHODS_REVIEW_ONLY`

Written and hashed **before** any realized threshold-component table is loaded by review code.
Root of the AXMAT00 record: the recorded FCDDH01R final tip
`7da296e57bd44e223691725b557a12bf9584ae7e`, subtree `de55a961a904a708e07c841a5282f8071499f2ac`.

```
SIMULATOR_IMPORT_LIMIT              = 0
ENGINE_START_LIMIT                  = 0
NEW_SCIENTIFIC_DATA_LIMIT           = 0
ACTIVE_RESPONSE_ARRAY_ACCESS_LIMIT  = 0
FULL_FIELD_NUMERICAL_ACCESS_LIMIT   = 0
REMOTE_OPERATION_SCOPE              = NONE
TOMMY_TECHNICAL_ACTION_REQUIRED     = false
ACTIVE_DATA_DEPENDENCY              = ZERO   (enforced mechanically, see §1)
```

## 0. What this freeze does and does not claim

It does **not** claim cognitive blinding. The historical headline scalars of `FCDDH01R` are already
in the record and in the reviewer's context. The enforceable commitment is narrower and mechanical:
**no active-response object enters review code, formula selection, semantic classification or route
selection.** Published headline scalars may appear in narrative prose only.

Ordering note, declared in advance: this document is written and hashed first; the review code is
written second and hashed into `AXMAT00_EVIDENCE_INDEX`; the realized component table is loaded
third. The freeze therefore carries no code hash of its own, by construction, and the binding runs
freeze → code → data, never the reverse.

## 1. Included and excluded scientific inputs

**Included** (allowlist, enforced by an input validator):

* committed master freezes and method specifications
* the `FCDDH01R` panel lock `b52b1eae…` and threshold lock `fc1b41f8…`, both created before any
  active row
* canonical sham records and sham-derived summaries
* masks, baseline states, scored-time definitions, fixed weights
* reader normalization, coefficient maps, gauge definitions
* numerical-error certificates and independent reference implementations
* manifests, hashes, provenance, schemas, static source inspection
* the final closure report, for historical identities and frozen verdicts only

**Excluded** (denylist; any read is an immediate stop):

* `x`, `d`, `z`, decoded active response matrices, carrier outcomes
* `v_D`, fold axes, active scores, any recomputation of `D3`–`D8`
* full-field active or sham numerical values
* alternate masks, supports, times, weights, gauges, normalizations
* simulator imports, constructors, runners, advances
* empirical calibration against `5.695567518165154e-04` or any active result

Concretely denied file names, by exact basename, inside the review environment:

```
FCDDH01R_DISCOVERY_MATERIALITY_AND_LEVERAGE_REPORT.json
FCDDH01R_DISCOVERY_LOAO_AXIS_ARBITRATION.json
FCDDH01R_DISCOVERY_INTERACTION_AND_ORBIT_TABLE.json
FCDDH01R_DISCOVERY_CONTRASTS.json
FCDDH01R_DISCOVERY_ALL_ROWS_AND_CONTRASTS.json
FCDDH01R_DISCOVERY_GATE_LADDER.json
FCDDH01R_DISCOVERY_COOPTIMAL_GAUGE_REPORT.json
FCDDH01R_DISCOVERY_PRODUCTION_REFERENCE_RECOMPUTATION.json
FCDDH01R_DISCOVERY_ACTIVE_RAW_LOCK.json
FCDDH01R_DISCOVERY_ACTIVE_RAW_MANIFEST.json
_work/DISCOVERY_ACTIVE_RAW_ARCHIVE/**   _work/DISCOVERY_PANEL/**   *.npz
```

A negative fixture must demonstrate that an active-response path is refused by the validator, and
the demonstration must be recorded.

Stop condition: reading any excluded numerical object emits
`ACTIVE_DATA_DEPENDENCY_DETECTED` and the review halts. A partially contaminated methods review is
not continued.

## 2. Exact formulas and units to be checked

Per descendant `d`:

```
ETA_ORACLE_L2[d]  = deterministic bound on reader / scoring / reload arithmetic
TAU_DYNAMIC_L2[d] = 0.01 * G2[d]
TAU_SITE_L2[d]    = 0.01 * RHO_MED[d] / B[d] * sqrt(W_POST)
TAU_MATERIAL_L2[d]= max(ETA_ORACLE_L2[d], TAU_DYNAMIC_L2[d], TAU_SITE_L2[d])
```

Per ancestry `b`, geometry `g`, neutral allocation member `a`:

```
TAU[b,g,a]           = TAU_MATERIAL_L2[descendant(b,g,a)]
A_X[b]               = (1/sqrt(2)) * sum_(g,a) TAU[b,g,a]
A_X_BAR[DISCOVERY]   = (1/12) * sum_b A_X[b]
```

Obligations:

1. Resolve the exact serialized names of every symbol above from the committed record, and prove
   dimensional equivalence to these frozen definitions rather than assuming it.
2. Derive the coefficient `1/sqrt(2)` **independently** from the exact eight-row interaction map.
   The displayed normalization implies an absolute coefficient `1/(2*sqrt(2))` on each of eight
   carrier rows, with the two carriers of one descendant sharing one `TAU`; the derivation must
   show `8 * (1/(2*sqrt(2))) * mean(TAU) = (1/sqrt(2)) * sum_(g,a) TAU`.
3. Reproduce, **from the pre-active threshold lock only**,
   `A_X_BAR[DISCOVERY] = 2.924046708945949e-03`, using certified interval arithmetic over exact
   rationals. Report interval width and the equality policy in force.
4. Reproduce all 48 `TAU` values and all three components through an independent minimal reference
   path that imports no production analysis function. Production/reference agreement is recorded as
   an **oracle**, explicitly not as a semantic proof.

A mismatch at any step is reported as `A_X_FORMULA_OR_PROVENANCE_UNRESOLVED`. It is never repaired
by adopting the reported value.

## 3. Semantic-classification schema

Reported as separate fields; not collapsed into one word, and overlapping properties not forced
into one enum:

```
DECLARED_RULE_INTENT = OPERATIONAL_MINIMUM_EFFECT_SCALE | NUMERICAL_UNCERTAINTY_ENVELOPE
                     | MIXED_OPERATIONAL_RULE | UNRESOLVED
CONSTRUCTION_CLASS   = MIXED_NUMERICAL_AND_PHYSICAL_MAX | PURE_NUMERICAL_BOUND
                     | PURE_PHYSICAL_SCALE | OTHER | UNRESOLVED
ETA_SEMANTICS        = DETERMINISTIC_NUMERICAL_ERROR_BOUND | UNRESOLVED
DYNAMIC_SEMANTICS    = DECLARED_PHYSICAL_MINIMUM_SCALE | OTHER | UNRESOLVED
SITE_SEMANTICS       = DECLARED_PHYSICAL_MINIMUM_SCALE | OTHER | UNRESOLVED
PROBABILISTIC_UNCERTAINTY_INTERPRETATION = LICENSED_BY_EXACT_PARENT_PROOF | NOT_LICENSED | UNRESOLVED
TRIANGLE_BOUND_VALIDITY = VALID | INVALID | UNRESOLVED
SHARPNESS_UNDER_ADMITTED_SET = SHARP_FOR_CARTESIAN_PRODUCT_OF_BALLS | NOT_SHARP
                             | ADMITTED_SET_UNRESOLVED
JOINT_CONSTRAINT_STATUS = NO_PREEXISTING_JOINT_CONSTRAINT
                        | PREEXISTING_JOINT_CONSTRAINT_SUPPORTS_TIGHTER_NUMERICAL_BOUND
                        | JOINT_CONSTRAINT_UNRESOLVED
NECESSARY_VS_SUFFICIENT_STATUS = SUFFICIENT_NOT_NECESSARY | NECESSARY_AND_SUFFICIENT
                               | NECESSITY_UNRESOLVED
```

Plain-language verdict required among: (1) a necessary boundary below which physics is negligible;
(2) a sufficient, deliberately strong gate for a higher-order contrast; (3) a deterministic
uncertainty bound; (4) a convention mixing numerical protection with declared physical scales;
(5) not classifiable from the committed record. More than one may apply; **necessary and sufficient
must not be conflated.**

## 4. Component-dominance summaries to compute

For all 48 descendants: the three components and `TAU_MATERIAL_L2`; the unique dominant component
or every tied component; dominance counts by geometry and by neutral allocation member; exact min,
median, max, and ancestry-balanced summaries; whether geometry or allocation mechanically changes
the scale; every equality, unresolved interval, or provenance defect.

Non-normative anatomy only, computed by the same triangle propagation:

```
A_ETA[b] , A_DYNAMIC[b] , A_SITE[b] , A_PHYSICAL[b] = propagation using max(DYNAMIC, SITE)
```

Declared in advance: because `TAU_MATERIAL` uses `max`, these are **not additive shares**, **not
alternate gates**, and **must never be compared with the active interaction magnitude**.

The `0.01` coefficient must be traced to its exact parent source and classified as physical
constant, fitted coefficient, inherited convention, or unresolved — **without** reference to the
active result.

## 5. Triangle-bound proof obligations

1. Exact units, homogeneity, normalization of every component.
2. Gauge invariance, allocation-label invariance, serializer-order invariance.
3. The triangle inequality derived from the exact coefficient map (not asserted).
4. Sharpness under the explicitly admitted Cartesian product of per-row balls: exhibit an admissible
   error configuration attaining the bound, or prove none exists.
5. A search of the **pre-existing committed method record only** for deterministic joint constraints
   coupling row errors. Independence or cancellation may **not** be inferred from exact twins or
   from realized outcomes.
6. Separation of numerical-error geometry from scientific minimum-effect semantics.
7. How `A_X` scales with contrast arity, and whether `A_X_BAR` shrinks with the number of
   independent ancestries.
8. Whether that scaling is consistent with a minimum-effect gate, a sampling uncertainty, both, or
   neither.

Governing distinction, fixed here: a worst-case `L1` propagation may be a valid **sufficient**
guarantee while being far too strong to serve as a **necessary** definition of physical relevance.
The review establishes what the parent record actually licensed; it does not decide by preference.

## 6. Anti-rescue rules (binding)

No scanning, tuning, reinterpreting or changing of `0.01`. No break-even coefficient for the
observed interaction. No replacing `max` by `ETA`, removing a component, or lowering a threshold.
No root-sum-of-squares, covariance cancellation or independence model absent a deterministic proof
predating active outcomes. No change of norm, support, mask, time window, weights, gauge, centering,
normalization or aggregation. Exact sham twins may **not** be used to set scientific materiality to
zero. No comparison of a diagnostic bound with `X_BAR`, `v_D`, a fold score, or `D4`/`D5`/`D8`. No
tighter prospective method may be described as a historical correction. The fixed-support
differential-axis route is not reopened.

A tighter deterministic proof may refine **only** the numerical-error component, and **only** for a
future protocol. It cannot alter historical `TAU`, `A_X`, `D4`, `D5` or `D8`.

## 7. Route-arbitration rules, fixed before the audit runs

Ranking among `P2_ANCESTRY_POPULATION_PREPLAN`, `ONE_ENDPOINT_FULL_FIELD_PREPLAN`,
`STOP_AND_REDIRECT`. Choose `P2` only if its independent-use and prevalue-freeze conditions all
pass; choose full field only if every full-field condition passes **and** `P2` is not the
higher-value eligible route; otherwise `STOP_AND_REDIRECT`.

The `P2` algebra to verify (exchangeability, continuity, no ties): a tube defined as the maximum of
four exchangeable calibration scores gives marginal coverage `4/5` for one fresh score, expected
exceedances `12/5` among twelve fresh scores, and `P(K >= 3) = 11/28`. These references explain why
three historical exceedances do not by themselves establish population non-transfer; they do not
reclassify any frozen gate.

Full-field inspection is limited to schemas, hashes and byte-availability manifests. No full-field
numerical value is opened. Absent a unique pre-value estimand, return
`FULL_FIELD_NOT_ELIGIBLE__NO_UNIQUE_PREVALUE_ESTIMAND`. PCA, learned masks, radial scans, radius
searches, channel searches, time searches and endpoint tournaments are ineligible.

## 8. Stopping conditions

* any excluded numerical object read → `ACTIVE_DATA_DEPENDENCY_DETECTED`
* formula, symbol resolution or provenance unresolved → `A_X_FORMULA_OR_PROVENANCE_UNRESOLVED`
* zero-engine scope not maintainable → `ZERO_ENGINE_SCOPE_CANNOT_BE_MAINTAINED`
* any request to reclassify `FCDDH01R`, license an axis, or open the hold-out → refuse

## 9. Final disposition schema

```
A_X_ANATOMY_COMPLETE__NEXT=P2_ANCESTRY_POPULATION_PREPLAN
A_X_ANATOMY_COMPLETE__NEXT=ONE_ENDPOINT_FULL_FIELD_PREPLAN
A_X_ANATOMY_COMPLETE__NEXT=STOP_AND_REDIRECT
A_X_FORMULA_OR_PROVENANCE_UNRESOLVED
ACTIVE_DATA_DEPENDENCY_DETECTED
ZERO_ENGINE_SCOPE_CANNOT_BE_MAINTAINED
```

No disposition may contain `FCDDH01R_RECLASSIFIED`, `AXIS_LICENSED` or `HOLDOUT_ELIGIBLE`.
`FCDDH01R` stays frozen at `7da296e5…`; AXMAT00 adds no correction to it.
