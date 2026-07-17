# DOWNSTREAM-ORDER-READER-01 — revised preregistration draft

Status: **INSTRUMENT QUALIFIED — SCIENTIFIC DRAFT UNSEALED — NO SEED FAMILY ASSIGNED OR OPENED**

## 1. Question and claim boundary

Question: does same-dose EARLY-versus-LATE history alter the first executed chemotactic face-flux response
downstream of the calibrated `m_minus -> q_c` source channel?

This draft accepts `M_MINUS-ORDER-READER-00` only as a validated constitutive source calibration. It does not
reinterpret `COUNTERFACTUAL-HISTORY-CORE-00`, use feeding as primary, establish ownership or memory, start
`BODY-EQUALIZATION`, or authorize a scientific run.

## 2. Histories and statistical unit

The four exact-clone histories remain

- `H_L_EARLY`, `H_L_LATE`;
- `H_H_EARLY`, `H_H_LATE`.

The original source world is the sole statistical unit. Histories, source-expression conditions and ramp arms are
paired potential outcomes and never increase `n`. No droplet-, face-, time-step- or arm-level pseudoreplication is
permitted.

If separately approved later, the design placeholder remains 24 primary original worlds and at most 12
feasibility-only reserve worlds, with at least 18 complete original worlds required. This is not a family assignment
or execution authorization. No seed numbers or namespace are selected by this draft. Reserve activation could use
only predeclared eligibility, reconstruction, tracker and survival fields, never source or flux outcomes.

## 3. One common standardized settle

For each eligible history:

1. create the four histories from exact clones;
2. run the unchanged fixed deep-turnover interval;
3. require the stored/reconstructed deep-state hash and fixed history label;
4. set only `N:=N0`;
5. settle exactly 40 steps once with `lam_minus=0.15` inside the existing radius-10 core and two-cell no-swap
   clamp, using the translated same-seed no-history/no-drive boundary, `up_ref=0`, and no feeding stimulus;
6. hash and retain that single settled state before any source condition or ramp arm exists.

There is no separate `lam_minus=0` settle. The focal memory and physical core remain untouched. Boundary input is
history-independent and recorded before response arms exist.

## 4. Source-only intervention and common response update

Clone the exact settled state into two source-expression inputs with identical hashes. Run exactly one
source-expression update in each:

```text
lambda_S = 0.15  (intact source expression)
lambda_S = 0     (source-expression ablation)
```

`lam_minus` varies only during this update. All other engine parameters, the source-step collar frame and every
input field are identical. Since `lam_minus` enters only the terminal attractant source, the two outputs must be
exactly identical in `rho/U/V/N/C/uptake/Mf` and may differ only in `c`. The direct source susceptibility is logged
here as a calibration control.

After the source update, clone each source output into three ramp arms and alter only `c`:

```text
c_a = c_1 + 0.01 * 1_K * (1 + a G),
a = -1, 0, +1,
G = d_x/10 on K, 0 outside K.
```

Execute exactly one response update for every arm with one common response engine configuration,
`lam_minus=0.15`, and the same next collar frame. The primary flux is logged at the beginning of that response
update, before uptake, memory writing or the response update's terminal source can affect it. Total post-settle
horizon is two engine updates: one source-expression update and one response update.

No second amplitude, y-axis repeat, longer-horizon endpoint or favorable post hoc window is allowed.

## 5. Exactly one downstream observable

For history `h`, source-expression condition `lambda_S` and ramp arm `a`, define

```text
J_h^lambda_S(a)
  = dt/M_h^lambda_S * sum F_x
```

over positive-x engine faces whose two endpoints both lie inside the fixed core. `M_h^lambda_S` is the core `rho`
mass immediately before the ramp arms diverge. `F_x` is the exact full material face flux returned to the engine's
transport calculation. `J` is named the **mass-specific internal +x face-flux sum**. It is not asserted to be
whole-body displacement because boundary flux is excluded.

The paired directional response is

```text
D_h^lambda_S = [J_h^lambda_S(+1)-J_h^lambda_S(-1)]/2.
```

The selected source-channel interaction is

```text
A_h = D_h^(lambda_S=0) - D_h^(lambda_S=0.15).
```

The primary within-world estimand is

```text
delta_A_O = 0.5 * [
  A(H_L_EARLY) - A(H_L_LATE)
  + A(H_H_EARLY) - A(H_H_LATE)
].
```

This is the original-world EARLY-minus-LATE difference in the downstream source-channel interaction. Because the
two source conditions begin from the same settled state, `delta_A_O` remains interpretable as the incremental
effect of source-expression `lam_minus` even if `D^(lambda_S=0)` itself retains an order contrast through another
pathway.

Low- and high-dose EARLY-minus-LATE contrasts of the same `A` observable are consistency summaries. Dose and
dose-by-order contrasts of `A` are descriptive only and cannot replace the primary estimand.

## 6. Positive source calibration control

During the intact source-expression update, recompute the already-validated direct source susceptibility

```text
chi_source,h = dt*s*0.15*sum_K rho0,h*m_minus,h.
```

Its world-level order contrast is a positive calibration control only. It cannot rescue a null, reversed or
uncertain downstream interaction. Its positivity is not evidence that the downstream flux sign is mechanically
fixed.

## 7. Directional hypothesis and unsealed margins

The preregistered directional hypothesis remains

```text
delta_A_O > 0.
```

It follows from the proposed saturation mechanism: higher EARLY `m_minus`-linked source production may raise mean
face `c` and reduce `chi(cbar)`. It is not a manipulation-validity theorem. The qualified synthetic ramp returns a
positive response in an ordinary-`c` fixture and a negative response in a strongly saturated fixture. A negative
scientific result would therefore falsify the directional hypothesis rather than invalidate the instrument.

The practical margins are explicitly unsealed:

```text
m_A = UNSEALED
m_0 = UNSEALED
```

The earlier tentative values `0.0001` and `0.00005` are not thresholds and must not enter classification. Synthetic
fixtures can establish numerical identity, resolution and sign reversibility; they cannot determine the smallest
scientifically meaningful internal flux interaction. A later `m_A` must be justified before outcomes from physical
scale or scientific relevance. A later `m_0`, if retained, must also be selected without outcomes and is secondary.
Neither margin may be estimated, tuned or lowered from scientific outcome values.

## 8. Eligibility, survival and complete-world rules

Eligibility is assessed before history assignment from unchanged parent geometry/tracker rules. It cannot use
source calibration, ramp response, future survival or any confirmation outcome.

A history/source-condition/arm is valid only if:

- exact-clone, deep-state and common-settle hashes pass;
- the two source-expression inputs are exact settled-state clones;
- only `c` differs between source-expression outputs;
- the target remains alive and bijectively tracked with no split, merge, ambiguity, loss or death event;
- coverage remains below the existing 15% cap;
- the complete tracked body remains inside the fixed radius-10 core through settle, source and response;
- core and two-cell collar are disjoint and common source/response collar frames are used;
- pre-ramp states are identical across `-1/0/+1` arms except for the declared `c` addition;
- no numerical clipping or negative `c` is introduced;
- deterministic rerun is exact.

An original world is complete only if all four histories, both source-expression conditions and all three ramp arms
are valid through the response update. If any required branch fails, the entire world is excluded from scientific
contrasts with its feasibility disposition retained. Failed branches are never zero and incomplete blocks are
never analyzed.

No post-history matching, trimming, regression, covariance adjustment or residualization by mass, size, radius,
geometry, nutrient, energy or body state is allowed. Those fields may be logged as diagnostics but never modify the
primary estimand or eligibility.

## 9. Code-only manipulation qualification

The following synthetic gates now pass:

1. the passive logger leaves the base engine output hash unchanged;
2. the logger leaves the qualified no-swap clamp output hash unchanged;
3. recorded arrays exactly equal `_face_flux` arrays for axes `(-2,-1)` and are read-only copies;
4. the 40-step settle is common at `lam_minus=0.15`, source inputs are exact clones, only source-step `c` differs,
   and all response updates use common `lam_minus=0.15`;
5. the radius-10 disk has 317 cells and 296 internal +x faces;
6. `G` lies in `[-1,1]`, sums to zero, arms are nonnegative, and each adds total `c=3.17`;
7. the `+/-` directional components reverse symmetrically within the frozen float64 criterion;
8. a closed fixture satisfies the first-moment identity with residual `-5.55e-17`;
9. a boundary-flux fixture shows that internal flux and boundary mass exchange are distinct;
10. the same matched ramp produces both positive and negative synthetic response signs under different saturation;
11. no test imports a scientific outcome runner or opens a source world.

Failure of logger identity, exact flux capture, schedule isolation, ramp construction or boundary accounting is
`MANIPULATION_INVALID`. A negative response sign is not manipulation invalidity.

## 10. Statistical summaries and secondary ablation diagnostic

If a scientific family is ever separately authorized, report original-world `delta_A_O` values, `n`, mean,
median, standard deviation, 95% Student-t interval and sign counts. No decoder, feature selection, outlier removal
or multiplicity-driven endpoint replacement is allowed.

Also report the EARLY-minus-LATE order contrast in `D^(lambda_S=0)` as a secondary pathway diagnostic. Equivalence
to zero may support specificity, but failure of equivalence cannot erase or reclassify the primary interaction;
it means another order pathway remains and narrows the mechanistic claim.

No scientific candidate/null classification is sealed while `m_A` and `m_0` are unsealed. In particular, the old
`ABLATION_NONSELECTIVE` precedence and numeric candidate/null thresholds are withdrawn from this draft.

## 11. Stopping and authorization boundary

Code-only instrument status is `QUALIFIED`. Scientific-preregistration status remains `REVISE` because the margins
and final prospective bindings are unsealed. This document assigns no seed and authorizes no reconstruction of a
570xx downstream outcome, prospective family, feeding endpoint, `BODY-EQUALIZATION`, additional direction, longer
horizon or reader battery.

Even a future positive interaction would establish only a history-dependent first-step internal chemotactic
face-flux interaction under standardized isolation. It would not establish ownership, individual memory, identity,
feeding order, heredity or active reconstruction.
