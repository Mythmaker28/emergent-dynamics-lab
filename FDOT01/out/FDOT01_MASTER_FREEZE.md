# FDOT01 — FRESH DAUGHTER ORGANISER TURNOVER TEST 01
## MASTER FREEZE — committed BEFORE the first fresh world

| | |
|---|---|
| Parent | DAUGHTER-ORGANISER-TURNOVER-CRITERION-01 |
| Parent tip | `d9f29d33864985068570ad3ddb9f69436b021234` |
| Point | B1, `kY = 2.5118864315095822e-05`, `muY = 9.261187281287937e-05` |
| Primary worlds | 160 |
| Technical reserves | 6 |
| Horizon | 11000, every world, no scientific early stop |
| Methods hash | `318b4313e086eea32e78507dd41509f3ad25799f4edabe0916afa1eb80314d1f` |
| Engine byte-unchanged | True |

---

## 1. The event is inherited, not redesigned

**Centre.** a time-indexed connected component of Y-occupied cells under the frozen centre rule — toroidal single-linkage over Y-occupied cells with adjacency distance <= CORE_R, `CORE_R = 5.0`.

**Identity.** a component at step t+1 continues a component at step t when it is the unique nearest component by toroidal centroid distance in both directions and that distance does not exceed CORE_R. A step at which the match is not mutually unique ENDS the identity interval; it is never resolved by preference.

**COMPLETE_TURNOVER** requires: the component remains nonempty throughout the identity interval; at least one Y removal recorded inside C; at least one accepted Y birth recorded inside C; both events lie inside ONE continuous centre-identity interval.

**Functional continuity.** `ACTIVE_LOCAL_X_PRODUCTION` — across the identity interval containing the turnover event pair, the centre records at least one accepted X birth inside its local domain on both sides of the removal event. Zero is the only threshold used, and zero is not a choice: it is the value the matched no-source control takes.

**No genealogy.** no parent-child assignment between Y molecules is invented, asserted or required. The engine keeps no Y tracker and DOTC01 does not create one.

---

## 2. A declared difference between the parent's definition and the parent's code

DOTC01's audit CODE linked components by mutual-nearest with a tie guard, which does not terminate an identity interval when one component splits into two that both remain within CORE_R. Its written DEFINITION says a match that is not mutually unique ends the interval, and FDOT01 §5 lists ties, splits and merges as all terminating identity.

§1 orders the parent DEFINITION preserved. FDOT01 implements the definition, which is strictly stricter than the parent code.

| Developmental B1, 44 worlds | complete | functional |
|---|---|---|
| under the strict rule FDOT01 uses | 2 | 1 |
| as DOTC01 reported | 4 | 3 |

Measured **before any fresh world existed**, and reported rather than resolved in favour of the
more convenient number.

---

## 3. The primary endpoint

does the prospectively frozen B1 law repeatedly produce daughter organising centres whose local organising function survives replacement of constituent Y material?

```
K   = the number of fresh independent worlds, of 160, that satisfy FUNCTIONAL_COMPLETE_TURNOVER
Qualify iff K >= 2
```

a p = 0 null is degenerate: a single event would reject it automatically. The criterion here is prospective REPLICATION — the frozen event seen independently in at least two fresh worlds under one fixed law.

It is not a biological constant, a probability threshold of nature, a hypothesis test.

Rate estimation is co-primary descriptive evidence, the developmental worlds are never pooled
with the fresh ones, and no threshold may be invented after the fact.

---

## 4. Detection assurance at N = 160, computed before any world

| Design input | p | E[K] | K>=1 | K>=2 | K>=3 |
|---|---|---|---|---|---|
| STRICT_RULE_one_sided_95_lower | 0.001165 | 0.186 | 0.1702 | 0.0153 | 0.0009 |
| STRICT_RULE_point_estimate | 0.022727 | 3.636 | 0.9747 | 0.8807 | 0.7069 |
| DOTC01_REPORTED_one_sided_95_lower | 0.018840 | 3.014 | 0.9523 | 0.8058 | 0.5822 |
| DOTC01_REPORTED_point_estimate | 0.068182 | 10.909 | 1.0000 | 0.9998 | 0.9990 |

> the launcher expected P(K >= 2 | N = 160, p_design) to come out near 0.80 using DOTC01's reported functional rate of 3/44 and its lower bound 0.01884. Recomputing the developmental input from the parent bytes under the rule FDOT01 §5 MANDATES — ties, splits and merges all terminate centre identity — gives 1/44, not 3/44, and a lower bound of 0.001165. At that input the assurance for K >= 2 is far below 0.80. This is reported BEFORE the runs, not discovered afterwards. N is not changed, because §3 fixes it and adaptive sample size is forbidden.

> a K < 2 outcome must therefore NOT be read as evidence that the phenomenon is absent. At the conservative input the experiment is underpowered for the K >= 2 threshold by construction. The rate estimate and its exact interval carry the information in that case, and §4 already makes rate estimation co-primary descriptive evidence.

---

## 5. Seeds

```
seed = 940000000 + int(SHA256(parent_tip|FDOT01|B1|KIND|index + 10000*bump)[:12],16) mod 50000000
```

160 primary and 6 reserve seeds, disjoint from a 411-seed registry (True), all unique (True), 0 bumps.

---

## 6. Horizon and third centres

Every world runs the full 11000 steps. These are **not** stops: `EXTINCT`, `PREMATURE_THIRD_CENTRE`, `MAX_PERMITTED_Y`, `event became impossible`, `one turnover already succeeded`.

The only break is a genuine engine invariant failure, which is a technical fault and not a scientific outcome.

> a daughter identity interval that splits into multiple centres TERMINATES, so that candidate centre cannot complete a turnover after the split. The world is still recorded to the horizon, and third-centre timing is reported as a scientific outcome, never as a technical failure.

---

## 7. Fixtures

13 fixtures, all pass, and the two independent implementations agree on every one.

| Fixture | Pass | A == B |
|---|---|---|
| 1_translation | True | True |
| 2_crossing | True | True |
| 3_equal_distance_tie | True | True |
| 4_split | True | True |
| 5_merge | True | True |
| 6_birth_inside_centre | True | True |
| 7_death_inside_centre | True | True |
| 8_birth_then_death_functional | True | True |
| 8b_birth_then_death_no_post_X | True | True |
| 9_death_then_birth_NY_ge_2 | True | True |
| 10_single_Y_death_extinction | True | True |
| 11_no_bridging_across_an_empty_gap | True | True |
| 12_observer_inertness | True | True |

---

## 8. Firewall and claim ceiling

Exposed during execution: `opaque arm token`, `completed`, `technical failure`, `checksum written`.

Withheld: `seed`, `turnover`, `birth/death counts`, `centre count`, `runtime`, `file size`, `stop reason`, `X production`, `success status`.

> organiser-level constituent turnover with retained local function at the frozen B1 law. Not reproduction, not heredity, not self-replication.

```
MINIMAL_REPRODUCTION_STATUS = NOT_ESTABLISHED
STRONG_SELF_REPRODUCTION_STATUS = NOT_TESTED
HEREDITY_STATUS = NOT_TESTED
H3_STATUS = NOT_TESTED
REPRODUCTION_STATUS = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED
X_LAWSPEC_BASELINE = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
```
