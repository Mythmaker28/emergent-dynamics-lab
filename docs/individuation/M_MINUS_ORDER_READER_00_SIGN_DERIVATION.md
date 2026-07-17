# M_MINUS-ORDER-READER-00 — exact sign and causal-path derivation

Status: **CODE-ONLY; WRITTEN BEFORE ANY 570XX READER OUTPUT**

## Exact downstream path

The frozen multi-channel engine writes both memory components and then evaluates

```text
m_minus(x) = tanh(newm1(x)-newm2(x))
q_c(x)     = s rho0(x) [1 + lam_minus m_minus(x)]
c(t+dt,x)  = c(t,x) + dt[D_c lap(c) + q_c - delta c].
```

This is the only occurrence of `lam_minus` in the engine. The same-step direct effect is attractant production.
On the next update, `c` enters the face gradient `dc` and the saturation
`chi=chi0/[1+(mean_face_c/c_sat)^2]`, thereby changing material flux. Flux transports `rho`, internal fields,
tracers and memory; later consequences include centroid, morphology, uptake and writing through
`Psi=tanh[k_exp(N-c)+k_up(uptake-up_ref)]`. Those later signs depend on gradients, saturation and geometry. The
source term is the only direct reader with an algebraically fixed sign.

## Why the frozen negative state prediction was wrong

For a homogeneous component with shared write input `x_t`, no transport, templating, diffusion or clipping,

```text
m_k(t+1) = q_k m_k(t) + w x_t,
q_k = 1-dt eta_dk,
w   = dt eta_w.
```

The frozen values are `dt=0.1`, `eta_w=0.015`, `eta_d1=0.35`, `eta_d2=0.006`; hence
`q1=0.965`, `q2=0.9994`, and `w=0.0015`. Let each episode last `T=60`, the post-history settle be `S=120`, and
let `Delta=0.01` be the EARLY-minus-LATE amplitude difference in episode 1 (with `-Delta` in episode 2).

After the two episodes and settle,

```text
Delta m_k = -w Delta q_k^S (1-q_k^T)^2 / (1-q_k).
```

Numerically,

```text
Delta m1          = -4.6377041581e-06
Delta m2          = -2.9102795171e-05
Delta(m1-m2)      = +2.4465091013e-05
Delta tanh(m1-m2) = +2.4464801452e-05  (near the origin).
```

Both components are lower in EARLY than LATE, but the slow component retains the early episode more strongly and
has the larger negative difference. Subtracting it makes `m1-m2` positive. The frozen EARLY-minus-LATE convention
was explicit and remains unchanged; the error was algebraic orientation, not a contrast convention change. The
exact spatial engine contains endogenous `Psi`, transport, templating, diffusion, clipping and evolving masks, so
the scalar formula does not predict its magnitude. It does establish that the intended reduced two-timescale logic
did not justify a negative sign. The accepted positive 17/17 observation is therefore compatible with the corrected
orientation; it does not convert the failed preregistration into a pass.

## Reader perturbation and sign

The frozen reader probe changes only the fractional local gain `a` of the existing term:

```text
q_c(x;a) = s rho0(x)[1 + lam_minus(1+a)m_minus(x)],  x in core.
```

The existing grid `lam_minus={0.05,0.15,0.25}` fixes `epsilon=2/3`, so `a=-epsilon,0,+epsilon` reproduces those
three coefficients around the frozen value `0.15`. For the one-step integrated source,

```text
chi_h = [Y_h(+epsilon)-Y_h(-epsilon)]/(2 epsilon)
      = dt s lam_minus sum_core rho0_h(x)m_minus_h(x).
```

All prefactors are positive. Therefore a positive density-weighted EARLY-minus-LATE `m_minus` contrast predicts
positive order susceptibility. This sign is frozen before reader outcomes. Raw density weighting is allowed to
falsify it; the per-core-mass robustness endpoint tests whether body mass alone sets the result. With
`lam_minus=0`, `chi_h` and all factorial susceptibility contrasts are exactly zero by construction.

## Phase-A disposition

**A valid reader exists:** local attractant production is directly and uniquely multiplied by the `m_minus` reader
term. The mission therefore proceeds with this one observable. Directional displacement, flux and morphology are
not selected because their signs require additional state-dependent terms and would invite outcome-based choice.

Theory classification: **`SIGN_THEORY_CORRECTED`**. This is a transparent correction of the reduced-theory sign,
not a reinterpretation of `NO_MEMORY_FIRST_STAGE`, and not an empirical reader classification.
