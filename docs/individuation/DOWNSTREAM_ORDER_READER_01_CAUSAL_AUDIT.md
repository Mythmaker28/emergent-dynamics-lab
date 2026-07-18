# DOWNSTREAM-ORDER-READER-01 — exact causal-path audit

> **Prospective-package addendum:** the causal path and instrument audit below remain accepted. The final
> no-margin claim logic, fixed family and updated disposition are recorded in
> `DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_PACKAGE_REPORT.md` and
> `DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_PREREGISTRATION_CANDIDATE.md`.

Status: **CODE-ONLY INSTRUMENT QUALIFIED — NO SCIENTIFIC OUTCOME OR SEED OPENED**

Parent: `M_MINUS-ORDER-READER-00` result commit
`6ae4a0e31d541f7bda1f424cb8682b960c979612`. The parent result is accepted only as a constitutive source
calibration. Its parent `NO_MEMORY_FIRST_STAGE — STOP THIS PREREGISTRATION CANDIDATE` verdict remains unchanged.

## 1. Exact update ordering

At the beginning of an engine step, material transport is computed from the *incoming* `rho` and `c` fields. For
each positive-coordinate face `f=(i,p)` on axis `k`, the frozen engine evaluates

```text
dc_f       = c_p - c_i
cbar_f     = (c_i + c_p)/2
chi_f      = chi0 / [1 + (cbar_f/c_sat)^2]
rho_up,f   = rho_i if dc_f>0 else rho_p
rho_dn,f   = rho_p if dc_f>0 else rho_i
A_f        = chi_f dc_f rho_up,f max(0,1-rho_dn,f/rho_max)
F_f        = A_f - D_rho(rho_p-rho_i).
```

`F_f` is then used in the conservative divergences that transport `rho`, `U`, `V`, `C`, and `Mf`. Uptake, death,
internal dynamics and memory writing follow. Only at the *end* of the step does the order channel update the
attractant field:

```text
m_minus(x) = tanh(newm1(x)-newm2(x))
q_c(x)     = s rho0(x)[1+lam_minus m_minus(x)]
c_next(x)  = c(x) + dt[D_c lap(c)(x)+q_c(x)-delta c(x)].
```

Therefore the current `m_minus -> q_c` contribution cannot affect flux in the same step. Its first possible flux
effect is the next step, when `c_next` enters `_face_flux`.

The full directed path is:

```text
history order
  -> different newm1-newm2
  -> m_minus
  -> q_c at the end of a source-expression step
  -> changed local c level and gradient
  -> next-step chi(cbar)*dc chemotactic face flux
  -> conservative transport of rho, U, V, C and Mf
  -> movement/morphology readouts from transported rho
  -> uptake from transported rho, U, V and Mf later in that same response update
  -> subsequent memory writing.
```

Movement/morphology and feeding are downstream of the executed flux, but neither is selected. Morphology is a
readout of transported material, not an intermediate asserted to cause feeding.

## 2. Why the source result is insufficient

The accepted calibration used

```text
chi_source = dt*s*lam_minus*sum_K rho0*m_minus.
```

That quantity is algebraically fixed once the state is known. The next-step face response is not. Substituting
`c(a)=c0+a b` into the advective term gives

```text
A_f(a) = chi0 [dc_f(0)+a db_f]
         / {1+[(cbar_f(0)+a bbar_f)/c_sat]^2}
         * rho_up,f(a) * max(0,1-rho_dn,f(a)/rho_max).
```

It depends on the spatial source distribution, existing `c`, saturation, the sign of each face gradient, density
and free capacity. The integrated source susceptibility does not determine its sign or magnitude. A downstream
flux result can therefore fail despite a positive source calibration.

## 3. Exactly one selected downstream observable

The selected observable is **the mass-specific internal +x face-flux sum produced by the frozen face-flux operator
under a matched local attractant ramp**, evaluated on the first response step. It is not named whole-body
displacement or net transport because the radius-10 core is not a closed material boundary.

Use the existing integer-centered radius-10 qualified core `K`. Let `d_x` be signed periodic displacement along
array axis `-1` from the integer core centre and define

```text
G(x) = d_x/R,  R=10, for x in K;  G(x)=0 outside K.
```

Thus `G` lies in `[-1,1]`, is antisymmetric, and sums to zero on the 317-cell integer-centred disk. The three
nonnegative matched probe arms are

```text
c_a(x) = c_1(x) + epsilon_c 1_K(x)[1 + a G(x)],
a in {-1,0,+1},
epsilon_c = 0.01.
```

All arms add the same total attractant. `a=0` is the common-offset sham; `a=+1` and `a=-1` have equal mass and
opposite directional components. `epsilon_c=0.01` is fixed before outcomes, is below the committed `0.03`
attractant-history scale, and is not estimated from downstream data.

For the positive-x faces whose two endpoints lie in `K`, log the exact `F_f` used by the engine in the response
step. With pre-response core mass `M`, define

```text
J_h^lambda(a) = dt/M * sum_{x-faces f with both endpoints in K} F_h,f^lambda(a).
D_h^lambda    = [J_h^lambda(+1)-J_h^lambda(-1)]/2.
```

`J` is an amplitude-specific internal face-flux aggregate in lattice cells per update. The diffusive term is
identical across the `+/-` arms and cancels from `D`; the remaining contrast is the executed chemotactic response.
Dividing by pre-ramp core mass is part of the declared observable, not a fitted correction. No mass, radius,
geometry or body variable enters a regression, match, exclusion or residualization.

On a synthetic closed lattice fixture with the positive-x wrap flux set to zero, the discrete conservative update
obeys exactly

```text
sum_x x * delta_rho(x) = dt * sum_{non-wrap +x faces} F_x,
```

with observed residual `-5.55e-17`. A separate nonzero-boundary fixture proves that boundary flux changes core mass
while leaving the internal endpoint unchanged. Therefore the closed-fixture first-moment identity is a mechanical
qualification, not permission to call the open-core endpoint displacement.

No y-axis repeat, radius-of-gyration endpoint, centroid endpoint, decoder, morphology score or feeding endpoint is
authorized. Direct source susceptibility is retained only as the named positive calibration control.

## 4. Revised source-only intervention and directional hypothesis

Every history undergoes exactly one common 40-step settle with `lam_minus=0.15`. Clone that exact settled state.
Only the next, single source-expression update differs: one clone uses `lam_minus=0.15`, the other
`lam_minus=0`. Because `lam_minus` enters at the final `c` update, the two source-expression outputs are identical
in every persistent field except `c`. Apply the matched three-arm ramp only after this source update. Every arm then
uses one common response engine with `lam_minus=0.15`; the logged primary flux occurs before that response step can
write its own terminal source.

Define the `lam_minus`-dependent attenuation of directional response for history `h`:

```text
A_h = D_h^(source lam_minus=0) - D_h^(source lam_minus=0.15).
```

The source calibration gives higher EARLY-minus-LATE `m_minus`-linked production. For nonnegative `c`, increasing
mean face attractant decreases `chi_f` because

```text
d chi_f / d cbar_f
  = -2 chi0 cbar_f/c_sat^2 / [1+(cbar_f/c_sat)^2]^2 <= 0.
```

The preregistered directional hypothesis is **positive EARLY-minus-LATE attenuation**: EARLY should be more
saturated and less responsive to the common directional ramp. This is not a manipulation-validity theorem. A
matched synthetic fixture gives positive paired response `+2.6175e-4` at ordinary `c` but negative response
`-2.0241e-6` under strong saturation. Existing gradients, spatial source heterogeneity, upwind changes and density
can therefore reverse the response without invalidating the logger or ramp. The scientific sign remains fixed as a
falsifiable hypothesis and cannot be changed after outcomes.

The `lam_minus=0` order contrast is a secondary pathway diagnostic. Failure to show its equivalence to zero would
show that another order-dependent pathway remains, but would not algebraically invalidate the primary
EARLY-minus-LATE interaction in `A`, because both source branches start from the same settled state and differ only
during the declared source-expression update.

## 5. Code-only qualification

The passive logger is a mixin over both `DiagEngine` and the qualified no-swap clamp engine. It calls the inherited
`_face_flux`, returns that live array unchanged to transport, and stores a separate read-only copy. On the synthetic
state, logged and unlogged terminal hashes are both
`39537c88c00a339c2d9e47f33b4578807e58f211abe90907cd1a0dda77c0128f`; recorded axis order is exactly
`(-2,-1)`. The no-swap-clamped identity also passes.

Seven synthetic fixtures pass: passive base identity, passive clamp identity, common-settle/source-only branching,
matched ramp geometry, closed first-moment identity, explicit boundary-flux separation, and saturation-induced sign
reversal. They instantiate no source world and import no downstream outcome runner.

## 6. Margin rationale and disposition

The frozen engine contains a measurable first downstream functional operator, and the proposed probe can be
constructed without negative `c`, clipping, unequal added attractant, tracker-dependent scoring or a feeding
endpoint. The observable is technically definable.

The earlier numerical proposals `m_A=0.0001` and `m_0=0.00005` are withdrawn as seals. Both margins are
**UNSEALED**. Synthetic fixtures establish numerical fidelity and possible effect orientation; they do not establish
a scientifically meaningful minimum effect. A later `m_A` must be justified independently from scientific outcome
values, using a declared scientific resolution or relevance argument. Any `m_0` must likewise be selected without
outcomes and remains secondary rather than a primary-validity gate.

The instrument is code-only qualified. The scientific preregistration remains `REVISE` until humans accept a
margin rationale and the remaining prospective design bindings. No 570xx reconstruction, new seed, family,
`BODY-EQUALIZATION`, feeding endpoint or reader battery is authorized.
