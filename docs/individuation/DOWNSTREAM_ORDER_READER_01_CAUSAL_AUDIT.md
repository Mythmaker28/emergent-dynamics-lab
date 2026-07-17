# DOWNSTREAM-ORDER-READER-01 — exact causal-path audit

Status: **DESIGN ONLY — WRITTEN WITHOUT A NEW SCIENTIFIC OUTCOME**

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

The selected observable is **mass-specific +x material transport produced by the frozen face-flux operator under a
matched local attractant ramp**, evaluated on the first response step.

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
v_h^lambda(a) = dt/M * sum_{x-faces f inside K} F_h,f^lambda(a).
D_h^lambda    = [v_h^lambda(+1)-v_h^lambda(-1)]/2.
```

`D` is an amplitude-specific directional transport response in lattice cells per update. The diffusive term is
identical across the `+/-` arms and cancels; the remaining contrast is the executed chemotactic response. Dividing
flux by mass is part of the physical velocity definition, not a fitted correction. No mass, radius, geometry or
body variable enters a regression, match, exclusion or residualization.

No y-axis repeat, radius-of-gyration endpoint, centroid endpoint, decoder, morphology score or feeding endpoint is
authorized. Direct source susceptibility is retained only as the named positive calibration control.

## 4. Mechanistic ablation and signed theory

Repeat the complete standardized settle and source-expression step with `lam_minus=0`, then apply the identical
three-arm `c` ramp. Unlike the old multiplicative source-gain assay, the directional probe still creates a real
chemotactic response when `lam_minus=0`; the ablation is therefore not forced to zero by probe construction.

Define the `lam_minus`-dependent attenuation of directional response for history `h`:

```text
A_h = D_h^(lam_minus=0) - D_h^(lam_minus=0.15).
```

The source calibration gives higher EARLY-minus-LATE `m_minus`-linked production. For nonnegative `c`, increasing
mean face attractant decreases `chi_f` because

```text
d chi_f / d cbar_f
  = -2 chi0 cbar_f/c_sat^2 / [1+(cbar_f/c_sat)^2]^2 <= 0.
```

The preregistered direction is consequently **positive EARLY-minus-LATE attenuation**: EARLY should be more
saturated and less responsive to the common directional ramp. Existing gradients, spatial source heterogeneity,
upwind changes and density can reverse this prediction; that is the non-algebraic downstream test, not a reason to
change the sign later.

## 5. Audit disposition

The frozen engine contains a measurable first downstream functional operator, and the proposed probe can be
constructed without negative `c`, clipping, unequal added attractant, tracker-dependent scoring or a feeding
endpoint. The observable is technically definable.

It is not yet execution-qualified. A passive flux logger and the ramp construction must first pass code-only
identity, symmetry, synthetic positive/negative and clamp tests. No scientific seed or already-open history outcome
is needed for that qualification.
