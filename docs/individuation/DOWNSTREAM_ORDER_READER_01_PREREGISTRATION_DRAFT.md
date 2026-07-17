# DOWNSTREAM-ORDER-READER-01 — preregistration draft

Status: **DESIGN-ONLY DRAFT — NOT SEALED — NO SEED FAMILY ASSIGNED OR OPENED**

## 1. Question and claim boundary

Question: does same-dose EARLY-versus-LATE history alter the first executed chemotactic transport response
downstream of the calibrated `m_minus -> q_c` source channel?

This draft accepts `M_MINUS-ORDER-READER-00` only as a validated constitutive source calibration. It does not
reinterpret `COUNTERFACTUAL-HISTORY-CORE-00`, use feeding as primary, establish ownership or memory, start
`BODY-EQUALIZATION`, or authorize a prospective run.

## 2. Frozen histories and statistical unit

The four exact-clone histories remain

- `H_L_EARLY`, `H_L_LATE`;
- `H_H_EARLY`, `H_H_LATE`.

The original source world is the sole statistical unit. Histories, `lam_minus` conditions and ramp arms are paired
potential outcomes and never increase `n`. No droplet-, face-, time-step- or arm-level pseudoreplication is
permitted.

The eventual family, if separately approved, will contain 24 primary original worlds and at most 12
feasibility-only reserve worlds. No seed numbers are assigned by this draft. Reserve activation may inspect only
predeclared eligibility, reconstruction, tracker and survival fields, never source or flux outcomes. At least 18
complete original worlds are required for a scientific classification.

## 3. Common standardized state

For each eligible world:

1. create the four histories from exact clones;
2. run the unchanged fixed deep-turnover interval;
3. require the stored/reconstructed deep-state hash and fixed history label;
4. set only `N:=N0`;
5. settle 40 steps inside the existing radius-10 core and two-cell no-swap clamp, using the translated same-seed
   no-history/no-drive boundary, `up_ref=0`, and no feeding stimulus;
6. do this separately with `lam_minus=0.15` and `lam_minus=0`, leaving `lam_plus` and all other parameters fixed.

The focal memory and physical core are untouched. Boundary input is history-independent and is recorded before
the response arms exist.

## 4. Frozen source-expression and response horizon

After the 40-step settle, run one unperturbed source-expression update. Log the actual direct source term from the
new memory state; no directional ramp is present in this update. Because the source is written at the end of an
engine step, this update creates the first `c` field that can carry the current `m_minus` contribution into future
flux.

Immediately after that update, create three byte-identical state copies and alter only `c`:

```text
c_a = c_1 + 0.01 * 1_K * (1 + a G),
a = -1, 0, +1,
G = d_x/10 on K, 0 outside K.
```

Execute exactly one response update under the corresponding next common collar frame. The primary flux is logged
at the beginning of that response update, before uptake, memory writing or the next source update. Total horizon:
two engine updates after the settle — one source-expression update and one response update. The directional
perturbation exists for the response update only.

No second amplitude, y-axis repeat, longer-horizon endpoint or favorable post hoc window is allowed.

## 5. Exactly one downstream observable

For each history `h`, `lam_minus` condition `lambda`, and ramp arm `a`, define

```text
v_h^lambda(a)
  = dt/M_h^lambda * sum F_x
```

over the positive-x engine faces with both endpoints inside the fixed core. `M_h^lambda` is the core `rho` mass
immediately before the ramp arms diverge. `F_x` is the exact full material face flux used by the engine. The paired
directional response is

```text
D_h^lambda = [v_h^lambda(+1)-v_h^lambda(-1)]/2.
```

The selected downstream `lam_minus`-dependent response is

```text
A_h = D_h^0 - D_h^0.15.
```

Positive `A_h` means the intact order-source channel attenuates response to the common directional attractant
probe relative to `lam_minus=0`.

The primary within-world estimand is

```text
delta_A_O = 0.5 * [
  A(H_L_EARLY) - A(H_L_LATE)
  + A(H_H_EARLY) - A(H_H_LATE)
].
```

This is the original-world EARLY-minus-LATE difference in the downstream `lam_minus`-dependent response.

Low- and high-dose EARLY-minus-LATE contrasts of the same `A` observable are consistency gates. The dose and
dose-by-order contrasts of `A` are descriptive only and cannot replace the primary estimand.

## 6. Positive source calibration control

During the source-expression update, recompute the already-validated direct source susceptibility

```text
chi_source,h = dt*s*lam_minus*sum_K rho0,h*m_minus,h.
```

Its world-level order contrast must retain the corrected positive orientation, a 95% Student-t interval above
zero, and at least 75% positive original-world signs. This is a calibration control only. It cannot rescue a null,
reversed, sub-margin or ablation-nonselective downstream result.

## 7. Frozen sign and practical margin

The predicted sign is

```text
delta_A_O > 0.
```

The practical margin is

```text
m_A = 0.0001 lattice cells per response update
```

at the fixed `epsilon_c=0.01` ramp amplitude. This is an amplitude-specific mass-transport displacement proxy, not
a standardized effect size. It corresponds to one ten-thousandth of a lattice cell of differential
transported-mass motion in the first response update, or 0.01% of the fixed one-cell spatial unit. The ramp creates
a nominal per-face concentration increment of `epsilon_c/R = 0.001`; the practical margin is fixed at one tenth of
that small-gradient scale. It is deliberately separate from the float64 tolerance. The margin is fixed without
downstream outcome data and must not be lowered after a negative result.

The `lam_minus=0` order-response equivalence margin is

```text
m_0 = 0.00005 lattice cells per response update.
```

This equivalence margin is exactly one half of the practical-effect margin and is likewise fixed before outcome.

## 8. Eligibility, survival and complete-world rules

Eligibility is assessed before history assignment from the unchanged parent geometry/tracker rules. It cannot use
source calibration, ramp response, future survival or any confirmation outcome.

A history/condition/arm is valid only if:

- exact clone and deep-state bindings pass;
- the target remains alive and bijectively tracked with no split, merge, ambiguity, loss or death event;
- coverage remains below the existing 15% cap;
- the complete tracked body remains inside the fixed radius-10 core after the settle, source-expression update and
  response update;
- core and two-cell collar are disjoint and the same history-independent collar frame is used across ramp arms;
- pre-ramp states are identical across `-1/0/+1` arms except for the declared `c` addition;
- no numerical clipping or negative `c` is introduced;
- deterministic rerun is exact.

An original world is complete only if all four histories, both `lam_minus` conditions and all three ramp arms are
valid through the response update. If any required branch fails, the entire world is excluded from scientific
contrasts with its feasibility disposition retained. Failed branches are never zero, and the remaining histories
are never analyzed as an incomplete block.

No post-history matching, trimming, regression, covariance adjustment or residualization by mass, size, radius,
geometry, nutrient, energy or body state is allowed. Those fields may be logged as diagnostics but never modify the
primary estimand or eligibility.

## 9. Manipulation qualification required before any family

Before a scientific outcome can be produced, code-only fixtures must establish:

1. the flux logger does not change any engine state or hash;
2. the logger records the exact `_face_flux` arrays used in transport;
3. radius-10 integer-core construction gives 317 cells and the scored +x interior-face set is fixed;
4. `G` lies in `[-1,1]`, has zero discrete sum within float64 tolerance, and all arms add equal total `c`;
5. `c_plus-c_sham = -(c_minus-c_sham)` within `1e-12+1e-10*abs(reference)`;
6. only `c` differs before the response step and no arm clips;
7. reversing the ramp reverses the directional flux response on a synthetic gradient fixture;
8. a uniform-ramp or `chi0=0` fixture returns zero directional response;
9. diffusion cancels from the paired `D` contrast when `rho` is shared;
10. `lam_minus=0` retains ordinary directional probe responsiveness rather than becoming a vacuous zero arm;
11. clamp-off identity, common-collar identity, deterministic rerun and external-seed refusal pass.

Failure of any item is `MANIPULATION_INVALID`, not a scientific null.

## 10. Frozen summaries and decision rule

For world-level `delta_A_O`, report `n`, mean, median, standard deviation, 95% Student-t interval, sign counts and
the complete list of world values. No decoder, feature selection, outlier removal or multiplicity-driven endpoint
replacement is allowed.

`DOWNSTREAM_ORDER_READER_CANDIDATE` requires all of:

- at least 18 complete original worlds;
- every manipulation gate passes;
- the direct source calibration control passes in its corrected positive direction;
- the 95% interval for `delta_A_O` lies entirely above `+0.0001`;
- at least 75% of original-world `delta_A_O` values are positive;
- both low- and high-dose EARLY-minus-LATE `A` contrasts have at least 75% positive world signs;
- the 95% interval for the order contrast in `D^(lam_minus=0)` lies wholly inside
  `[-0.00005,+0.00005]`.

Classification precedence:

1. `MANIPULATION_INVALID` if a construction, logger, clamp or deterministic gate fails;
2. `FEASIBILITY_FAIL` if fewer than 18 complete original worlds exist at the frozen cap;
3. `SOURCE_CALIBRATION_FAIL` if the direct source control does not reproduce its corrected positive orientation;
4. `ABLATION_NONSELECTIVE` if the `lam_minus=0` order response is not equivalent to zero;
5. `DOWNSTREAM_ORDER_READER_CANDIDATE` if every positive gate passes;
6. `SOURCE_CALIBRATED_DOWNSTREAM_NULL` if source calibration passes and the downstream 95% interval is wholly
   within `[-0.0001,+0.0001]`;
7. `SIGN_REVERSED` if the downstream interval lies wholly below `-0.0001`;
8. `UNRESOLVED` otherwise.

No classification may be upgraded by feeding, morphology, centroid displacement, a different direction, a longer
horizon, a smaller margin or a high-dimensional decoder.

## 11. Stopping and authorization boundary

This document is not a seal and assigns no seed. The current recommendation is `REVISE` pending code-only
instrument qualification and human acceptance of the sign and practical margins.

Even a future `DOWNSTREAM_ORDER_READER_CANDIDATE` would establish only a prospective history-dependent
chemotactic transport response under standardized isolation. It would not establish ownership, individual memory,
identity, feeding order, heredity or active reconstruction, and it would not automatically authorize
`LOCAL_OWNERSHIP_PAIR_00` or `BODY-EQUALIZATION`.
