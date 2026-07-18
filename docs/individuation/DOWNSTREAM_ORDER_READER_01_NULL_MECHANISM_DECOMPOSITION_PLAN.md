# DOWNSTREAM-ORDER-READER-01 — frozen null-mechanism decomposition plan

Status: **FROZEN BEFORE ANY MECHANISM DECOMPOSITION OUTPUT**

Scope: one bounded post-result, raw-only algebraic autopsy. This plan cannot change, rescue or reinterpret the
prospective `NO_ACCESS_ESTABLISHED` classification. The original source world is the only inferential unit. Faces
are algebraic summands only.

## 1. Immutable inputs and fail-closed sufficiency gate

The only permitted scientific inputs are the committed prospective manifest, `results.json`, `run_state.json`,
W001-W048 raw JSON shards, and the committed raw-only reproduction at accepted commit
`d71c7ebb14cb74d47bbaac7858f4ec0286240bdb`.

Before any decomposition value is evaluated, require all of the following:

1. raw collection SHA-256 is `8d4baaac198cf5e5526359ad723d4cebd0c0614ffa2441fead41144ef573adf1`;
2. reproduction SHA-256 is `35616172409424d28d765acecb2c29ac1f2527fb7acd48196a9113e85081b679`;
3. W001-W048 and seeds 58001-58048 are exact and ordered;
4. all 35 complete-world stored contrasts and the frozen classification reproduce exactly;
5. every parent binding in the immutable manifest matches;
6. the persisted raw contains numerical face-level `c_i`, `c_p`, `rho_i`, `rho_p`, executed internal +x face
   flux, core membership, and—only for the partition question—numerical boundary face flux.

A hash of a face array is identity evidence, not a numerical face array. An aggregate signed sum and aggregate
absolute sum cannot recover the individual face contributions or their covariation with `cbar`, `dc`, upwind
density and free capacity. If item 6 fails, return exactly `RAW_INSUFFICIENT`, produce no decomposition estimates,
set the roadmap to `UNRESOLVED_RAW_INSUFFICIENT`, and never initialize or reconstruct a world.

## 2. Exact notation and face equations

For complete original world `w`, histories
`h ∈ {H_L_EARLY,H_L_LATE,H_H_EARLY,H_H_LATE}`, source condition
`lambda ∈ {zero,intact}`, ramp `a ∈ {-1,0,+1}`, and an internal positive-x face `f=(i,p)`:

```text
dc[h,lambda,a,f]     = c[p] - c[i]
cbar[h,lambda,a,f]   = (c[i] + c[p])/2
chi(cbar)             = chi0 / (1 + (cbar/c_sat)^2)
rho_up                = rho[i] if dc > 0 else rho[p]
rho_dn                = rho[p] if dc > 0 else rho[i]
capacity              = max(0, 1 - rho_dn/rho_max)
Adv                    = chi(cbar) * dc * rho_up * capacity
F                      = Adv - D_rho * (rho[p] - rho[i])
j                      = dt/M * F
```

The `dc=0` rule is the literal engine branch: use `rho[p]` as `rho_up` and `rho[i]` as `rho_dn` because the
condition is strictly `dc > 0`.

The source-conditioned core mean and internal gradient changes, evaluated after the source-expression update and
before the matched ramp, are:

```text
Delta_core_c[h] = mean over x in K of (c[intact,x] - c[zero,x])
Delta_dc[h,f]   = dc[h,intact,f] - dc[h,zero,f]
Delta_cbar[h,f] = cbar[h,intact,f] - cbar[h,zero,f]
Delta_chi[h,f]  = chi(cbar[h,intact,f]) - chi(cbar[h,zero,f])
```

For each ramp arm, the exact source-conditioned nonlinear chemotactic response is:

```text
Delta_Adv[h,a,f] = Adv[h,intact,a,f] - Adv[h,zero,a,f].
```

Because source clones have identical `rho` before the response and the matched ramps change only `c`, the
diffusive term is identical across source conditions at fixed `(h,a,f)`. It must nevertheless be checked from raw
face inputs rather than assumed from a hash.

## 3. Exact face contribution to the frozen primary

Let the frozen history-order coefficients be:

```text
s[H_L_EARLY] = +1/2
s[H_L_LATE]  = -1/2
s[H_H_EARLY] = +1/2
s[H_H_LATE]  = -1/2.
```

The exact per-face contribution to the original-world primary interaction is:

```text
q[w,h,f] = s[h] * dt/(2*M[h]) * (
    F[h,zero,+1,f] - F[h,zero,-1,f]
  - F[h,intact,+1,f] + F[h,intact,-1,f]
).
```

Then:

```text
signed_sum[w] = sum over h,f q[w,h,f] = stored delta_A_O[w]
absolute_sum[w] = sum over h,f abs(q[w,h,f])
cancellation_index[w] = abs(signed_sum[w]) / absolute_sum[w].
```

Frozen zero-denominator rule: if `absolute_sum == 0`, set `cancellation_index=0.0`, set
`cancellation_zero_denominator=true`, and do not label that world cancellation. A nonzero signed sum with zero
absolute sum is an arithmetic failure.

No face is an observation, no face-level confidence interval is permitted, and no complete world may be removed.

## 4. Linearized saturation prediction and exact nonlinear response

At the zero-source face state:

```text
chi_prime(cbar0)
  = -2*chi0*cbar0/c_sat^2 / (1 + (cbar0/c_sat)^2)^2

L[h,a,f]
  = chi_prime(cbar0) * Delta_cbar[h,a,f]
    * dc[h,zero,a,f] * rho_up[h,zero,a,f] * capacity[h,zero,a,f]

N[h,a,f] = Delta_Adv[h,a,f].
```

`L` is the first-order saturation-only prediction, holding the zero-source gradient, upwind selection, density
and free capacity fixed. `N` is the exact nonlinear source-conditioned chemotactic response and includes exact
changes in gradient sign, upwind selection and all multiplicative terms. The exact change in saturation factor is
`Delta_chi`; it is reported separately from `L`.

Apply the same `+1/-1` ramp contrast, `dt/M` scaling and frozen history coefficients to `L` and `N`. Compare them
only at the original-world level. No fitted slope, regression, decoder, clustering or feature search is permitted.

## 5. Candidate failure-mode signatures

These are descriptive compatibility checks, never confirmation or support:

1. **LOCAL BUFFERING:** `Delta_core_c` is nonzero, but the recomputed absolute face-response sum is at or below the
   already-frozen world numerical bound. This is a numerical-resolution statement, not scientific equivalence.
2. **SIGNED CANCELLATION:** the absolute face-response sum exceeds the world numerical bound, contains both signs,
   but the signed sum remains within the bound. Report the cancellation index; do not threshold faces as samples.
3. **SATURATION-REGIME HETEROGENEITY:** the exact `cbar/c_sat`, `Delta_chi`, linearized prediction and nonlinear
   response show different signs or materially different algebraic orientation across original worlds. No new
   relevance margin may be learned from the results.
4. **GRADIENT/UPWIND GATING:** the exact nonlinear response differs in sign from the saturation-only prediction in
   conjunction with a recorded `dc` sign/upwind selection change, or the residual exact response after the
   saturation-only term algebraically dominates it. Density and capacity remain equation terms, not covariates.
5. **INTERNAL/BOUNDARY PARTITION:** only if prospectively persisted numerical boundary face flux exists, apply the
   identical source-by-ramp-by-order contrast to boundary faces and report internal and boundary signed/absolute
   sums separately. Hashes or core-mass changes cannot substitute for boundary face values.

If data were sufficient, a unique mechanism could drive a new-probe recommendation only if exactly one signature
held in at least `ceil(0.75*n_complete)` original worlds and no competing signature reached that count. Otherwise
the descriptive diagnosis would be `MIXED_NO_DOMINANT_MECHANISM` and the line would close. This dominance rule is
frozen before outputs and is not an inferential test.

## 6. Permitted outcomes and roadmap

The audit diagnosis is exactly one of the six mission labels. `RAW_INSUFFICIENT` has precedence over every
mechanistic label. The roadmap is exactly one of the three mission labels. Under `RAW_INSUFFICIENT`, it is
necessarily `UNRESOLVED_RAW_INSUFFICIENT`.

The prospective result remains `NO_ACCESS_ESTABLISHED` in every case. No absence, equivalence, one-sided rescue,
new endpoint, longer horizon, axis search, body equalization or prospective extension is licensed.
