# MRFA01 — MINIMAL-REPRODUCTION-FAILURE-AUTOPSY-01
## FINAL REPORT

A zero-run autopsy of FMRT01. It asks one question: did FMRT01 fail because the daughter remained
dependent on its parent, or because criterion D did not measure local daughter autonomy?

**`NEW_SCIENTIFIC_RUNS_USED = 0`.** No seed, no world and no trajectory was created.

---

## 0. The answer, and the part of it that is uncomfortable

Criterion D did **not** measure local daughter autonomy. It compares a quantity defined over 6.25 %
of the lattice against a reference computed over 100 % of it, and its verdict changes when X is added
in a distant corner with no change to the daughter at all. In 20 of 22 blocks D's bound exceeds the
daughter's **entire** mass at the moment of intervention, so a daughter that maintained its field
perfectly would still be scored a failure.

But correcting the scope does not rescue the experiment, and this is the finding that matters most.
At the B1 point a *centre* is **one Y molecule**. Every triggered block has exactly two Y-occupied
cells at maturation; the selective intervention removes one Y and the global intervention removes two.
No daughter produced a new Y in any of the 22 blocks, in either arm that kept a daughter. So the
object whose autonomy was being tested is a single molecule, its persistence is that molecule's
survival, and its 'function' is Y-gated catalysis that the frozen law entails at any cell holding a
Y and an X. **No local criterion measurable inside a 250-step hold can separate daughter autonomy
from the law restating itself.**

Terminal disposition: `DAUGHTER_AUTONOMY_CRITERION_NOT_IDENTIFIABLE__EXACT_MISSING_OBJECT_NAMED`.

---

## 1. Binding, after the sixth container rollback

> this mission began after the SIXTH container rollback. HEAD had reverted to 06c592313df96601de8d2a89676d5a5cf79fc414 (FLCR01 C4) and the entire FMRT01 tree was gone, together with FLRS02, FDFLT01, RCD01 and SPOIQ01. The repository was rebuilt from the bundles on Tommy's Windows disk and every restored byte was verified against the hashes FMRT01 itself committed.

Every restored byte was checked against the hashes FMRT01 itself committed: 129 + 86 + 33 files, 0 bad. Engine byte-unchanged: True.

| Accounting, recomputed from bytes | |
|---|---|
| blocks seeded | 85 |
| blocks triggered | 22 |
| blocks not triggered | 63 |
| technical replacements | 0 |
| reserve use | 0 |
| raw archives | 85 |

### The §1 gate

the archives store ONE state hash per triad, because the three arms are produced by deep copy from one state. The three hashes were therefore RECOMPUTED, one per arm, in the bit-exact reconstruction.

```
PRE_INTERVENTION_PHYSICAL_STATE_IDENTICAL = 22 / 22
PRE_INTERVENTION_RNG_STATE_IDENTICAL      = 22 / 22
```

**PASS — the autopsy is interpretable**

The reconstruction that produced those three hashes is a **bit-exact deterministic replay** of the 22
already executed frozen seeds — `TECHNICAL_PROVENANCE_RECONSTRUCTION` — accepted only because it reproduced every archived hash,
fingerprint, scalar and series in 22 of 22 triads. Its outputs never enter a denominator.

It exists because the archives do not contain what §5 requires: they store world-level totals every 25
steps and record the GLOBAL arm's daughter mass as `null`, because that code path needed a surviving Y
component to place the disc.

---

## 2. What FMRT01 actually established, preserved

R1 recomputed molecule by molecule: **22 of 22** by calculator A, **22 of 22** by calculator B, against FMRT01's reported 22.

Fraction of the daughter's local X that was produced *after* the daughter lineage originated:
min 0.7079, q1 0.7951, median 0.8781, q3 0.9233, max 0.9714.

```
DAUGHTER_FIELD_MATERIAL_RENEWAL = ESTABLISHED_WITHIN_FMRT01_TRIGGERED_WORLDS
```

This is **not** minimal reproduction and is not labelled as such.

Criterion E recomputed: positive in 20/22 SELECTIVE, 22/22 SHAM, 0/22 GLOBAL. Median accepted births
inside the fixed daughter disc: SELECTIVE 110.0, SHAM 114.0, GLOBAL 0.0.

> X birth is Y-gated in the frozen engine, so a surviving Y with X present produces X with probability near one. E establishes that production continued; it does not establish that the daughter is autonomous, and it is not treated as if it did.

---

## 3. Criterion D

```
criterion_D  <=>  daughter_mass_post  >  Q_0.95[ Binomial( N_X_world_at_intervention , (1-muX)^250 ) ]
```

| | |
|---|---|
| Left-hand side | a LOCAL count over 6.25 % of the lattice at one instant |
| Right-hand side | a quantile of a GLOBAL count over 100 % of the lattice |
| Reference derived from | `WHOLE_WORLD_X_MASS` |
| Median bound | 94.0 |
| Median daughter mass at intervention | 71.0 |
| Blocks where the bound exceeds the daughter's entire mass | 20/22 |
| Bound / the daughter's own decayed stock | 3.549 |
| Measured old material in the fixed disc (GLOBAL arm) | 19.0 |
| Analytic bound / measured old material | 4.86 |

**World-size test.** Scaling the world's X while leaving the daughter untouched:

| World X scaled | Median bound | SELECTIVE passes |
|---|---|---|
| x0.5 | 49.5 | 20/22 |
| x1 | 94.0 | 3/22 |
| x2 | 181.0 | 0/22 |
| x4 | 352.0 | 0/22 |

D's right-hand side scales with the number of X molecules anywhere in the world; its left-hand side does not. Adding X in a distant corner of the lattice, with no change whatsoever to the daughter, flips D against the daughter. A criterion whose verdict depends on matter that is nowhere near the object it is about is not measuring that object. This is decisive and it does not depend on FMRT01's outcome.

D **is** alpha-valid, and that is worth preserving. D's false-positive rate really is bounded by 0.05 under its stated null, and that is worth preserving. But alpha-validity is necessary, not sufficient: a test that can never fire is alpha-valid and useless. D is close to that regime here.

```
CLASSIFICATION = WORLD_SCALE_CRITERION_MISAPPLIED_TO_LOCAL_DAUGHTER
```

derived from the definition and from the scientific object 'local daughter autonomy', not from the fact that D failed. The two load-bearing facts are (i) the LHS and RHS are different spatial objects differing by a factor of 16 in area, and (ii) D is not invariant to world size or to unrelated X elsewhere, which the scientific object must be.

---

## 4. The SHAM falsification

SHAM keeps both centres and removes 0 molecules. Its daughter survives **22/22** and produces X in the
fixed disc **22/22**. It still fails D in **14/22**. FMRT01 reported 8/22; recomputed 8/22, agrees: True.

- **A** → `REJECTED`
- **B** → `SUPPORTED`
- **C** → `MECHANICALLY_REFUTED`

Conclusion: **B — D is mis-scaled relative to local function.** X birth is Y-gated: engine_obtc.py _react_core draws births ~ Binomial(min(n[res],free), min(1, k*nX*nY)), so a cell with nY = 0 can never produce X. The GLOBAL arm, which removes every Y, produced EXACTLY ZERO X inside the fixed daughter disc across all 22 blocks. Production is therefore a direct, unambiguous signature of a local Y source, and it is present in both SHAM and SELECTIVE. What D measures instead is whether the local mass beats a global stock figure, which is a different question.

---

## 5. The three-arm causal decomposition

Windows predeclared from physics before any trajectory was inspected. One X e-folding is
249.4997 steps; FMRT01's hold is 250 steps = **1.002005 e-foldings**, so only the first of the three
requested windows exists. `NOT_AVAILABLE__FMRT01_HOLD_IS_EXACTLY_ONE_E_FOLDING` — extending the arms would be a new trajectory, not a reconstruction.

Geometry: disc radius 5.0 centred on the t_m daughter centroid, FIXED, identical in all arms.

| Sub-window | daughter-only effect (mass) | parent increment (mass) | daughter-only (births) |
|---|---|---|---|
| W1_0_to_1_3_efold | +18.12 | -2.04 | +43.00 |
| W2_1_3_to_2_3_efold | +39.14 | -0.60 | +40.00 |
| W3_2_3_to_1_efold | +45.58 | +11.99 | +32.00 |

| Arm | Endpoint fixed-disc mass (median) | Total fixed-disc births (median) |
|---|---|---|
| SELECTIVE | 66.0 | 110.0 |
| SHAM | 72.5 | 114.0 |
| GLOBAL | 19.0 | 0.0 |

**GLOBAL produced exactly zero births inside the daughter disc, in every block, total.** X birth is
Y-gated in the frozen engine, so production is an unambiguous signature of a local Y source — and
under SELECTIVE the only Y left in the world is the daughter's.

The parent adds almost nothing to the daughter's local field for the first two-thirds of the
e-folding (parent increment -2.04 then -0.60) and only +11.99 in the last third.

---

## 6. The autonomy indices, after their audit

The audit was done first. GLOBAL produces EXACTLY ZERO births in the fixed daughter disc in all 22 blocks, so the birth denominator reduces to SHAM's own production, which is strictly positive in 22 of 22. The mass denominator can collapse when the daughter's centre drifts out of the fixed disc in the SHAM arm, which happens in block 84.

- Mass denominator non-positive in 1 block(s); birth denominator non-positive in 0.
- Is mass the right response variable? no. Mass can be sustained by inherited stock and by diffusion from the parent region. Accepted births cannot: a birth at time t > t_m is new material produced at a Y-occupied cell. The production index is the one that answers the question asked.
- Parent/daughter discs are disjoint in 13 blocks and overlap in 9. overlap inflates the denominator and biases A DOWNWARD, i.e. towards the null. A_birth median is 1.2895 on the
  disjoint subset and 0.9153 on the overlapping one, so the concern is real and does not drive the result.

| Index | n | median | q1 | q3 | ≥0.5 | ≥0.8 | >1 | <0 |
|---|---|---|---|---|---|---|---|---|
| A_mass | 21 | 0.7619 | 0.5417 | 1.2950 | 18 | 9 | 6 | 0 |
| A_birth | 22 | 0.9781 | 0.7132 | 1.5133 | 21 | 16 | 11 | 0 |

A_birth ≈ 1 means the daughter alone produces about as much new X in its own disc as it does with the
parent present. `NO_THRESHOLD_IS_CHOSEN_FROM_FMRT01_OUTCOMES = True`.

---

## 7. What the object under test actually is

| | |
|---|---|
| Y-occupied cells at maturation | 2, in every block |
| N_Y at maturation | 2 |
| Y removed by SELECTIVE / GLOBAL | [1] / [2] |
| Daughters that produced a new Y during the hold | SELECTIVE 0, SHAM 1, of 22 |
| Single-Y survival over the hold | 0.977112 |
| Observed daughter persistence | 0.9091 |
| X e-folding | 249.5 steps |
| Y decay e-folding | 10797.3 steps |
| Hold, in X e-foldings | 1.0020 |
| Hold, in Y e-foldings | 0.0232 |
| Empirical single-centre → two-centre waiting time | 3323.0 steps |
| Hold as a fraction of that | 0.0752 |
| Analytic Y-birth waiting time | 4423–13270 steps |

> at B1 a 'centre' is a single Y molecule. Its persistence over the hold is molecule survival, (1-muY)^250 = 0.977112, and its 'function' is Y-gated X catalysis, which the frozen law entails at any cell holding a Y and an X. The hold is matched to the X relaxation timescale and is 7.5 % of the timescale on which the organiser population changes at all. Any LOCAL criterion measurable inside this hold therefore tests the law, not the daughter.

---

## 8. Where the 19 R2 failures are, and the 17 that matter

| Class | Count |
|---|---|
| `daughter_Y_centre_lost` | 2 |
| `FROZEN_R2_PASS` | 3 |
| `local_mass_STABLE_but_frozen_D_fails` | 9 |
| `local_mass_DECLINES_while_production_continues` | 8 |

Sum 22 of 22, `IS_A_PARTITION = True`.

### The 17 worlds where E passed and frozen R2 failed

in every one of these the daughter Y centre survived, produced new X inside its own disc, held X integrity and saw no third centre. The ONLY frozen criterion they failed is D, the mass comparison against a bound computed on the whole world's X.

| | |
|---|---|
| Median bound | 95 |
| Median daughter mass at intervention | 69.0 |
| Median excess of the bound over that mass | +27.0 |
| Blocks where the bound exceeded the daughter's entire mass | 16 of 17 |
| Median new X produced in the fixed daughter disc | 110 |
| Median GLOBAL control births in the same disc | 0 |

---

## 9. Population incidence and conditional autonomy, kept apart

a conditional success rate must never stand in for the population rate. Both must be visible in any future minimal-reproduction claim, together with their joint.

| | k/n | rate | exact 95 %% |
|---|---|---|---|
| `P_TRIGGER` | 22/85 | 0.258824 | [0.169850, 0.365236] |
| `P_AUTONOMY_GIVEN_TRIGGER_FROZEN_R2` | 3/22 | 0.136364 | [0.029056, 0.349122] |
| `P_JOINT_FROZEN_R2` | 3/85 | 0.035294 | [0.007338, 0.099696] |

---

## 10. Candidate criteria applied to the existing worlds — diagnostics only

`STATUS = POST_OUTCOME_AUTOPSY_DIAGNOSTIC`. none of these criteria was preregistered. Reporting a p-value for any of them would present a post-outcome choice as a prospective test. The counts exist for one purpose only: to judge whether a fresh test would be worthwhile.

| Candidate | SELECTIVE | SHAM | GLOBAL | population rate over 85 |
|---|---|---|---|---|
| `FROZEN_D_world_scoped` | 3 | 8 | 0 | 0.035294 |
| `DAUGHTER_SCOPED_ANALYTIC_BOUND` | 20 | 22 | 0 | 0.235294 |
| `DEFINITION_II_production_only` | 22 | 22 | 0 | 0.258824 |
| `DEFINITION_IV_paired_vs_measured_GLOBAL` | 20 | 21 | 0 | 0.235294 |

---

## 11. The single-centre operator as a reference

| Aspect | Comparable? |
|---|---|
| source law | True |
| substrate law | True |
| X decay | True |
| mobility / p_hop | True |
| capacity regime | True |
| substrate history | False |
| measurement radius | False |
| certified error | False |

```
SINGLE_CENTRE_OPERATOR_NOT_TRANSPORTABLE_TO_DAUGHTER_CONTEXT
```

- only the unblocked kernel is exact and the daughter context is capacity-constrained
- the operator's r80 = 8.544 exceeds FMRT01's measurement radius of 5.0
- the daughter's substrate history is a two-centre history, outside the qualification scope
- no certified bound exists, so no frozen exact null can be derived from it

Therefore: use the paired causal fork, which is empirical, exactly scoped and world-size invariant by construction. This choice is load-bearing.

---

## 12. FMRT01's provenance defects, classified and not repaired

`NO_FMRT01_JSON_WAS_ALTERED = True`.

- **P1** trigger leakage through raw naming → `OUTCOME_METADATA_LEAK__NO_ADAPTIVE_CONSEQUENCE`
- **P2** durability-gate self-reference → `NONSCIENTIFIC_PROVENANCE_GATE_DEFECT`
- **P3**, found by this autopsy: FMRT01 reports PRIMARY_SCIENTIFIC_WORLDS = 255 = 85 x 3. Only the 22 triggered blocks forked into three arms; the other 63 ran a single trajectory. Arm-instances actually instantiated: 22 x 3 + 63 x 1 = 129. → `DESCRIPTIVE_OVERSTATEMENT__NO_DENOMINATOR_AFFECTED`

`ORIGINAL_MACHINE_DISPOSITION = MINIMAL_REPRODUCTION_TEST_TECHNICALLY_INVALID`
`FMRT01_ADJUDICATED_DISPOSITION = MINIMAL_REPRODUCTION_NOT_QUALIFIED__DAUGHTER_INDEPENDENCE_NOT_ESTABLISHED`

the frozen primary test did not reject H0: q <= 0.05. K = 3 against a required critical count of 4, exact one-sided p = 0.09482304591843077. That stands, and nothing in this autopsy changes it.

`A_BROKEN_DURABILITY_BOOLEAN_DOES_NOT_QUALIFY_A_FAILED_TEST = True`.

---

## 13. Two independent calculators

They share the raw archives and nothing else: scalar_source — A: the meta blob inside each .npz, B: FMRT01_SEALED_RECORDS.jsonl; geometry — A: numpy broadcast disc mask, B: explicit integer cell loop with math.hypot; binomial_quantile — A: scipy.stats.binom.ppf, B: 50-significant-digit Decimal PMF recurrence; R1 — A: numpy boolean masking, B: pure-python per-molecule loop; contrasts — A: numpy over the reconstruction JSON, B: python lists re-read from the CSV.

15 quantities checked, **0 disagreements**. `INDEPENDENT_REANALYSES_AGREE`.

One numeric difference is recorded rather than hidden: the float rendering of (1-muX)^250, A = 0.3671424535662421, B = 0.3671424535662424, relative difference 9.072e-16.
Cause: IEEE double repeated multiplication in A versus a 50-digit decimal power in B. Load-bearing: False — the derived integer quantile survivor_upper is identical in 22 of 22 blocks, so no classification moves.

---

## 14. Eligibility for a fresh test

| # | Condition | Met |
|---|---|---|
| 1 | criterion D did not validly operationalise local daughter autonomy | **True** |
| 2 | one replacement criterion follows from physics/causal design, not outcome optimisation | **False** |
| 3 | the criterion is measurable losslessly | **True** |
| 4 | SHAM and GLOBAL_OFF provide valid positive/negative causal references | **True** |
| 5 | post-outcome diagnostics show the criterion is not vanishingly rare | **True** |
| 6 | a fresh experiment is decision-capable within <= 256 primary worlds | **False** |
| 7 | the criterion has a frozen null and an exact testable prediction | **False** |

4 of 7. `FRESH_TEST_ELIGIBLE = False`.

**Condition 2 fails.** Definition IV is derived from the design and has an exact exchangeability null, but at a 250-step hold its content reduces to Y-gated catalysis by a surviving single molecule, which the frozen law entails. A criterion entailed by the law is not a replacement criterion; it is a restatement of the law.

**Condition 6 fails.** at 85 blocks the exact unconditional power against the exchangeability null, planned on the conservative lower bounds q = 0.7405 and P(trigger) = 0.1822, is 0.5216 — below 0.80. Reaching 0.80 needs q >= about 0.87, which is above the conservative planning input.

**Condition 7 fails.** the null is exact — matched-pair exchangeability, H0: q <= 0.5 — but the prediction is not testable in the scientific sense at this scale: the law entails the outcome whenever the daughter's single Y molecule survives, which it does with probability 0.977112 per hold.

Had it been eligible, the null would have been exact — `q <= 0.5`, matched-pair exchangeability — and the exact unconditional power
at 85 blocks on the conservative planning inputs (q = 0.7405, P(trigger) = 0.1822) is **0.5216**, below 0.80.

| Blocks | q=0.95 | q=0.90 | q=0.85 | q=0.80 | q=0.75 |
|---|---|---|---|---|---|
| 50 | 0.8613 | 0.7265 | 0.5790 | 0.4360 | 0.3100 |
| 60 | 0.9291 | 0.8227 | 0.6844 | 0.5327 | 0.3869 |
| 70 | 0.9649 | 0.8886 | 0.7685 | 0.6181 | 0.4595 |
| 85 | 0.9885 | 0.9468 | 0.8579 | 0.7209 | 0.5542 |
| 128 | 0.9996 | 0.9942 | 0.9662 | 0.8879 | 0.7434 |

---

## 15. Terminal disposition

```
DAUGHTER_AUTONOMY_CRITERION_NOT_IDENTIFIABLE__EXACT_MISSING_OBJECT_NAMED
```

### The exact missing object

1. **a daughter centre whose identity is not a single molecule** — at B1 every triggered block has exactly two Y-occupied cells and NY = 2; SELECTIVE removes one Y and GLOBAL removes two. Centre persistence is therefore molecule survival and centre function is single-molecule catalysis. Neither is a property of a daughter as opposed to a molecule.

1. **a hold window matched to the organiser timescale** — T_HOLD = 250 steps = 1.0020 X e-foldings but only 0.0232 Y decay e-foldings, and 7.52 % of the empirical single-centre-to-two-centre waiting time of 3323 steps. No Y was produced by any daughter in any of the 22 blocks, in either arm that retained a daughter.

### No handoff is created

NONE — §14 authorises HANDOFF_FRESH_LOCAL_DAUGHTER_AUTONOMY_TEST_01 only if a fresh test is justified. It is not.

A successor becomes eligible only with:

- a daughter centre with internal state, so that centre persistence is not one molecule's survival
- a hold window matched to the organiser timescale rather than to the X relaxation timescale
- and only then a paired SELECTIVE vs GLOBAL_OFF endpoint under matched-pair exchangeability

B1, unchanged. No parameter search, no substrate change, no architecture change proposed.

---

## 16. Status

```
MINIMAL_REPRODUCTION_STATUS = NOT_ESTABLISHED
STRONG_SELF_REPRODUCTION_STATUS = NOT_TESTED
HEREDITY_STATUS = NOT_TESTED
R3_STATUS = NOT_TESTED
H3_STATUS = NOT_TESTED
REPRODUCTION_STATUS = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED
X_LAWSPEC_BASELINE = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
NEW_SCIENTIFIC_RUNS_USED = 0
```

FMRT01's frozen result is unchanged and no retroactive success is claimed: NOT_CLAIMED_AND_NOT_POSSIBLE.
