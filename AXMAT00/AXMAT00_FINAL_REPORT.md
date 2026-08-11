# AXMAT00 — FINAL REPORT

`A_X_MATERIALITY_SEMANTICS_AND_SHARPNESS_AUDIT_00` · offline methods review only.
Root: FCDDH01R final tip `7da296e57bd44e223691725b557a12bf9584ae7e`, subtree `de55a961a…`.

```
DISPOSITION = A_X_ANATOMY_COMPLETE__NEXT=P2_ANCESTRY_POPULATION_PREPLAN
```

## 1. The answer

`A_X` is a **deliberately strong sufficient gate**, built as a **mixed operational convention**, and
propagated worst-case. It is **not** a necessary physical boundary, and **not** a probabilistic
uncertainty envelope.

```
DECLARED_RULE_INTENT                     = MIXED_OPERATIONAL_RULE
CONSTRUCTION_CLASS                       = MIXED_NUMERICAL_AND_PHYSICAL_MAX
ETA_SEMANTICS                            = DETERMINISTIC_NUMERICAL_ERROR_BOUND
DYNAMIC_SEMANTICS                        = DECLARED_PHYSICAL_MINIMUM_SCALE
SITE_SEMANTICS                           = DECLARED_PHYSICAL_MINIMUM_SCALE
PROBABILISTIC_UNCERTAINTY_INTERPRETATION = NOT_LICENSED
TRIANGLE_BOUND_VALIDITY                  = VALID
SHARPNESS_UNDER_ADMITTED_SET             = SHARP_FOR_CARTESIAN_PRODUCT_OF_BALLS
JOINT_CONSTRAINT_STATUS                  = NO_PREEXISTING_JOINT_CONSTRAINT
NECESSARY_VS_SUFFICIENT_STATUS           = SUFFICIENT_NOT_NECESSARY
```

## 2. Zero-engine, zero-active status

Simulator imports 0 · engine starts 0 · new scientific data 0 · active-response arrays opened 0 ·
full-field values opened 0 · remote operations 0 · seeds consumed 0.
`ACTIVE_DATA_DEPENDENCY = ZERO`, enforced by an allowlist validator; six negative fixtures — four
active-analysis reports and two `.npz` array paths — were all refused. Six inputs were accepted,
each hashed: the pre-active threshold lock, the exact interaction coefficient map, the TAU
propagation certificate, the phase-payload identity report, the twin-sham oracle, and the factor
graph spec. The published headline scalars appear in prose only and entered no computation.

## 3. Formulas reproduced

The coefficient `1/sqrt(2)` was derived independently from the committed eight-row map, not read
off: `x[b] = (1/2) sum_a (d[NEAR,a] - d[FAR,a])` with `d = (r_C2 - r_C1)/sqrt(2)` gives every one of
the eight carrier rows an absolute coefficient `1/(2 sqrt 2)`; the two carriers of a descendant
share one `TAU`, so `sum_rows |coeff| TAU = (1/(2 sqrt 2)) * 2 * sum_{g,a} TAU = (1/sqrt 2) sum_{g,a} TAU`.
The pair coefficient checks out the same way: four rows at `1/sqrt(2)` give `sqrt(2)(TAU_N + TAU_F)`.

Weights are exact: `1/18 + 8*(1/9) + 1/18 = 1`, so `W_POST = 1` and `sqrt(W_POST) = 1`.

`TAU_DYNAMIC` was rebuilt from the raw sham series and the committed weights over exact rationals —
a reference path importing no production analysis function — and matches the lock **48/48 exactly**.
`TAU_MATERIAL = max(...)` matches **48/48**. All 48 enclosures are consistent with the committed
ones, all positive and finite. Per-ancestry `A_X` agrees with the lock **12/12**.

```
A_X_BAR[DISCOVERY] reproduced = 2.924046708945949e-03   (bit-identical IEEE-754 double)
certified enclosure width     = 2.11e-154   (relative 7.2e-152; a double ulp here is 6.5e-19)
```

Recorded rather than glossed: the published decimal does not lie *inside* that 1e-154-wide
enclosure, because the decimal is a correctly-rounded rendering of the exact value. The criterion
met is the right one — the correctly-rounded double of the certified enclosure is bit-identical to
the published value. Equality policy: verdicts only on strictly separated enclosures; equal
enclosures are never read as equal values.

## 4. Component anatomy

```
ETA_ORACLE_L2  = 0 exactly, all 48 descendants, never dominant
TAU_DYNAMIC_L2 dominant 48/48, zero ties
TAU_SITE_L2    never dominant;  DYN/SITE ratio 2.70 – 4.80 (median 4.14)
TAU  min 7.055948e-04   median 1.078938e-03   max 1.264019e-03   max/min 1.79
```

The numerical branch of the `max` is **identically zero throughout**, exactly as the committed
ledger declares (`eta_oracle = 0 exactly on the exact rational scoring path`). So in this record
`A_X` carries **no numerical-uncertainty content at all**: it is entirely a declared physical scale.

Non-normative anatomy (not additive shares, not alternate gates, never comparable with any active
magnitude): `A_ETA_BAR = 0`, `A_SITE_BAR = 7.477e-04`, `A_DYNAMIC_BAR = A_PHYSICAL_BAR = A_X_BAR
= 2.924047e-03`.

**Geometry mechanically changes the scale.** `FAR > NEAR` in **24/24** descendant pairs, ratio
1.146–1.688 (median 1.406); means 1.2013e-03 vs 8.663e-04. The FAR arm drifts more on its own sham
and therefore buys a larger `TAU`, so the per-ancestry gate is set predominantly by the noisier arm.
Allocation shows a consistent ordering inside NEAR (12/12) but no consistent direction inside FAR
(5/12); since `A_X[b]` is a symmetric sum over both members, `A_X` and `A_X_BAR` are exactly
invariant under allocation exchange regardless.

Ancestry-balanced means are stable: 1.0125e-03 to 1.0428e-03 across the twelve ancestries (3%).

## 5. Origin of the `0.01`

Traced to `FCDDH01R/_work/FROZEN_ESTIMAND_AND_UNIT_LEDGER.md` §3, which states the rule verbatim and
marks it **“(inherited, unchanged)”**; the same `1/100` appears in the threshold lock's own
`symbolic_to_numeric_map`. It multiplies (a) the descendant's own weighted-L2 sham drift away from
its `t0` checkpoint and (b) the median support density over `B`.

```
CLASSIFICATION = INHERITED_CONVENTION expressing a DECLARED PHYSICAL MINIMUM-EFFECT SCALE
```

Not a physical constant: no committed derivation ties `1/100` to the lattice, the LawSpec, the
carriers or the reader. Not a fitted coefficient: nothing in the record shows it estimated, tuned or
scanned; it predates every active row. The parent record states the intent directly —
*“the conservative triangle-inequality floor … is an exploratory materiality guard, **not a
sampling-error calibration**.”* This classification uses no active result.

## 6. Triangle, sharpness, joint constraints

Validity: `||sum_i c_i e_i|| <= sum_i |c_i| ||e_i|| <= sum_i |c_i| tau_i`, then `||Q w|| <= ||w||`
for the orthogonal projector `Q = I - P2`, so the pre-projection bound survives projection. **VALID.**

Sharpness: pick a unit vector `u` in `range(Q)` and set `e_i = sign(c_i) tau_i u`. Every `||e_i|| =
tau_i`, so the configuration is admissible under the declared Cartesian product of per-row balls,
and `Q(sum_i c_i e_i) = (sum_i |c_i| tau_i) u` attains the bound exactly. **SHARP.**

This matters more than it looks. **The conservatism of `A_X` does not live in the inequality — the
inequality is tight.** It lives entirely in the *choice of admitted set*: independent per-row balls
whose radii are fixed at a declared 1% physical scale, then aggregated worst-case a second time
across the twelve ancestries.

Joint-constraint search over the committed method record found the decisive statement already
there: *“RSS is FORBIDDEN because no parent certificate proves the required error independence.”*
The structural facts that do exist — the `h=0` structural zero (at the reference index, outside the
ten-node weighted sum), the exact cancellation of `mu` in `d`, the gauge sign shared across both
carriers — none of them couples the error budget. Two carriers of a descendant share one `TAU`,
which fixes two ball *radii* to a common value; nothing in the record proves the two row
*deviations* are common-mode, and this review does not infer it.

```
JOINT_CONSTRAINT_STATUS = NO_PREEXISTING_JOINT_CONSTRAINT
```

Invariance, machine-checked over exact rationals: gauge channel swap — identical; allocation
exchange — identical; 200 random serializer permutations — identical.

## 7. Scaling, and why it settles the semantics

`A_X[b]` is a **sum** over the four cells scaled by `1/sqrt(2)`: it **grows linearly with contrast
arity**. Adding cells raises the gate. Identity check: `(4/sqrt 2) * mean TAU = 2.924046709e-03 = A_X_BAR`.

`A_X_BAR` is a **mean over ancestries of per-ancestry gates**: it is **invariant in `n`**. A sampling
envelope would shrink as `1/sqrt(12)` to `8.441e-04`; the realized value does not shrink at all.

```
SCALING_CONSISTENCY = CONSISTENT WITH A MINIMUM-EFFECT GATE, NOT WITH A SAMPLING UNCERTAINTY
```

## 8. What exact twins do and do not prove

The 48/48 bit-identical sham twins prove **determinism**: the engine, given the same checkpoint and
schedule, reproduces the same trajectory bit for bit. They therefore prove there is no stochastic
run-to-run jitter to average away.

They do **not** estimate stochastic noise — there is none to estimate — and they do **not** set
materiality to zero. `TAU` is not a noise estimate; it is a declared minimum-effect scale defined
against the system's own sham drift. Determinism makes `eta_oracle = 0` credible; it says nothing
about whether a 1% floor is the right scientific bar.

## 9. What the historical ratio can and cannot mean

Narrative only, computed nowhere in this review: the record's ratio `0.194784` says the realized
interaction amplitude sat at about one fifth of `A_X_BAR`.

It **can** mean: the interaction did not clear a deliberately strong sufficient gate; and, since the
gate is sharp under its admitted set, no tighter propagation of the *same* admitted set would have
changed that verdict.

It **cannot** mean: that the interaction is zero; that it is physically negligible; that a
population effect is absent; or that some other threshold would have been the correct one. Turning
that ratio into a break-even coefficient is explicitly forbidden and was not done.

## 10. Why FCDDH01R stays frozen and the fixed-support axis route closes

`FCDDH01R` remains `DESCRIPTIVE_DETERMINISTIC` and
`NONCONFORMANT_POSTSTART_EXECUTOR_REPAIR`, gates `{D4,D5,D8}` failed, axis `NOT_LICENSED`, hold-out
`ZERO_STARTS__NOT_REACHED`, `RECLASSIFICATION_ALLOWED = false`. AXMAT00 adds **no** correction to
that record and creates nothing inside it.

The fixed-support differential-axis route closes for a reason this audit sharpens rather than
softens: the gate it failed is tight under its own admitted set, its numerical component is already
exactly zero so there is no numerical slack to recover, and the only remaining way to lower it would
be to redefine the declared 1% physical scale — a scientific redefinition, not a correction, and one
that could never be applied retroactively.

## 11. Ranked next route

1. **`P2_ANCESTRY_POPULATION_PREPLAN` — ELIGIBLE.** All five conditions pass. It is a distinct
   scientific question about the inherited parent basis, not an axis rescue.
2. `STOP_AND_REDIRECT` — the fallback if the owner declines to fix a loss function prospectively.
3. **`ONE_ENDPOINT_FULL_FIELD_PREPLAN` — INELIGIBLE**, `FULL_FIELD_NOT_ELIGIBLE__NO_UNIQUE_PREVALUE_ESTIMAND`,
   with the additional and prior blocker `FULL_FIELD_BYTES_ABSENT_FROM_THE_FCDDH01R_SUBTREE`.

The `P2` algebra verified exactly: marginal coverage `4/5`, expected exceedances `12/5`,
`P(K >= 3) = 11/28 ~ 0.393`, under exchangeability of all sixteen scores and continuity with
zero tie probability. Three historical exceedances among twelve are therefore entirely ordinary and
establish nothing on their own about population non-transfer.

Kept rigorously distinct: **testing** the inherited tube estimates the coverage of the fixed tube
built from the existing four calibration scores — that is the transfer question. **Recalibrating** a
new tube around the same `P2` basis can always be made to cover by construction and therefore cannot
prove transfer of the first. Any preplan must fix the ancestry-level score by the claim (maximum of
the four cell scores for a robustness claim; the mean answers a different question), never by
outcomes.

Execution of that preplan is outside this task: it would require fresh owner authorization and a
fresh seed namespace.
