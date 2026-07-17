# DOWNSTREAM-ORDER-READER-01 — numerical tolerance and margin rationale

## Numerical floor

For every logged internal +x face `f`, the frozen repository float64 comparison rule is

```text
e_f = 1e-12 + 1e-10 * abs(F_f).
```

For `n=296` internal faces, let `S_abs=sum(abs(F_f))`, `u=eps_float64/2`, and
`gamma_k=k*u/(1-k*u)`. The conservative arm bound for
`J=(dt/M)*sum(F_f)` is

```text
e_input = n*1e-12 + 1e-10*S_abs
e_sum   = gamma_(n-1) * (S_abs + e_input)
e_J     = abs(dt/M)*(e_input+e_sum)
          + gamma_2*(abs(J) + abs(dt/M)*(e_input+e_sum)).
```

All subtractions and halvings are then propagated through the fixed linear definitions of `D`, `A` and
`delta_A_O` by the sum of absolute coefficient-weighted input bounds plus a `gamma_(2k)` arithmetic term. For each
complete world:

```text
delta_num_world = max(
  propagated delta_A_O bound,
  5.551115123125783e-17 closed-domain identity residual,
  0 logger-identity residual,
  0 deterministic-replay residual
).

delta_num_family = max(delta_num_world over complete worlds).
```

The raw record stores `J`, `sum(abs(F_f))`, face count, `dt` and core mass, so the independent reproducer derives
the bound without importing the runner, engine or contract module. The numerical floor grows with observed flux
magnitude only through the predeclared relative-error rule; it is not selected to favor a claim.

## Scientific margins

No outcome-independent physical argument currently maps a particular internal one-step face-flux interaction to a
behavioural, morphological or macroscopic consequence. Synthetic identities establish metrology, not relevance.
Therefore:

- no `m_A` practical-access margin is proposed;
- no `m_0` equivalence margin is proposed;
- no dimensionless relevance normalization is proposed;
- zero or unstable denominators are avoided rather than patched;
- only a bounded causal-detection claim is available;
- no behavioural or macroscopic importance claim is available.

Core mass is the only denominator in the endpoint. It is fixed by the equation, must be finite and strictly
positive before arms diverge, and is identical across the three ramp arms. A nonpositive or nonfinite mass is a
kill-switch, not an imputation.

Any future scientific margin would require a new human-reviewed, outcome-independent derivation and reseal before
scientific files are opened. It cannot be estimated from this family or from a favorable synthetic response.
