# FCDDH00 — FROZEN ESTIMAND AND UNIT LEDGER

Resolved from the committed parent objects. Nothing here may change after Commit 2.

## 1. Coordinate space and units

The parent weighted-L2 space is `R^20`. Coordinates `0..9` are the **common** channel `u`,
coordinates `10..19` are the **differential** channel `v`. The parent basis file
`SQDT00/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz` declares this layout explicitly
(`coord_layout`, `coord_htime`), and `PARENT_BASIS_NUMERICAL_CERTIFICATE.json` records the check.

Scored native steps `H_GRID = 40, 80, …, 400`; `dt = 1/10`; physical scored times `4 … 40`.
Trapezoid weights normalised to sum 1:

```
W = [1/18, 1/9, 1/9, 1/9, 1/9, 1/9, 1/9, 1/9, 1/9, 1/18]        sum W = 1 exactly
sqrt(W[h]/2) = 1/6            for h in {0, 9}          (exactly rational)
sqrt(W[h]/2) = sqrt(2)/6      for h in 1..8            (enclosed, width < 2^-100)
```

Reader (frozen, unchanged): `X_A(t) = sum_{support A} rho_t / B`, `X_B(t) = sum_{support B} rho_t / B`,
with `B` the fixed pre-treatment normalizer taken from raw baseline bytes. All reader sums are
exact rationals: every float64 is a dyadic rational.

## 2. Per-row response

```
delta_A[h] = X_A^active[h] - X_A^sham0[h]        delta_B[h] = X_B^active[h] - X_B^sham0[h]
M2^2       = sum_h W[h] ( delta_A[h]^2 + delta_B[h]^2 )                     (exact rational)
u[h]       = sqrt(W[h]/2) ( delta_A[h] + delta_B[h] )
v[h]       = sqrt(W[h]/2) ( delta_A[h] - delta_B[h] )
z(s)       = ( u[0..9] , s * v[0..9] ) in R^20 ,   s in {+1,-1}
||z(s)||^2 = M2^2   for either s                                            (exact isometry)
```

`h = 0` (the checkpoint time) is a **structural zero**: the carriers touch `Mf` only, so `rho`
at `t0` is untouched and `X^active[0] - X^sham[0] = 0` exactly. This is asserted per row.

## 3. Thresholds

```
TAU[b,g,a]^2 = max( eta_oracle^2 , tau_dynamic^2 , tau_site^2 )      (inherited, unchanged)
eta_oracle   = 0 exactly on the exact rational scoring path
tau_dynamic^2 = (1/100)^2 sum_h W[h] ( (XA_s[h]-XA_s[0])^2 + (XB_s[h]-XB_s[0])^2 )
tau_site^2    = ( (1/100) * median(rho_0 restricted to the support) / B )^2 * sum_h W[h]
```

Both carriers of one descendant share the same canonical sham (`SHAM_0`) and the same `TAU`.

## 4. Interaction chain

```
r[b,g,a,o] = (I - P2_parent) ( z[b,g,a,o] - mu_parent )
d[b,g,a]   = ( r[.,CARRIER_2] - r[.,CARRIER_1] ) / sqrt(2)        (mu cancels exactly)
x[b]       = (1/2) sum_{a in {0,1}} ( d[b,NEAR,a] - d[b,FAR,a] )
```

`x[b]` is the allocation-orbit-averaged NEAR-minus-FAR × carrier interaction vector of one
independent ancestry. It is **not** centred by any fresh midpoint: zero is the predeclared
no-interaction origin.

Identities proved before outcomes (oracle Q0D–Q0I) and re-checked on every panel:

* `P2_parent @ x[b] = 0` within certified arithmetic;
* `x[b]` is exactly invariant under either allocation-member exchange within NEAR or FAR;
* the joint block-level NEAR/FAR slot swap maps `x[b] -> -x[b]` exactly;
* all four descendants and all eight carrier rows carry their exact coefficients.

## 5. Materiality units

Each of the eight rows enters `x[b]` with absolute coefficient `1/(2*sqrt(2))`; each of the four
rows of a cross-orbit pair contrast enters with `1/sqrt(2)`. Because `Q = I - P2` is an
orthogonal projector, `||Q w|| <= ||w||`, so the triangle floors stay conservative:

```
A_X[b]          = (1/sqrt 2) sum_{g,a} TAU[b,g,a]                  E_X[b] = A_X[b]^2
A_PAIR[b,aN,aF] = sqrt(2) ( TAU[b,NEAR,aN] + TAU[b,FAR,aF] )
X_BAR[B]        = (1/|B|) sum_b x[b]      A_X_BAR[B] = (1/|B|) sum_b A_X[b]
s[b;v] = <v, x[b]>        S_BAR[B;v] = (1/|B|) sum_b s[b;v]        E_FIXED = S_BAR^2
p[b,aN,aF;v] = <v, d[b,NEAR,aN] - d[b,FAR,aF]>      u[b;v] = min over the four pairings
```

Root-sum-of-squares is **never** used. `x`, `d`, `z` and axis scores are **never** divided by
`TAU`. Absolute materiality requires `lower(S_BAR) > upper(A_X_BAR)`; **equality fails**.

## 6. Certified arithmetic

`delta_A`, `delta_B`, `B`, `W`, `TAU^2` are exact `fractions.Fraction`. `mu`, `P1`, `P2`, `e1`,
`e2` and the serialized axis are float64, hence exact dyadic rationals. The only irrational in
the response map is `sqrt(W[h]/2)`, enclosed with a `sqrt(2)` enclosure of width `< 2^-100`.
Every derived quantity is carried as a rational interval with **outward** rounding at 200 bits.
Every comparison is a certified interval comparison whose third outcome is `UNRESOLVED`. The
Cauchy–Schwarz step `|<v,w>| <= ||v|| ||w||` uses the certified **upper** bound on `||v_D||`, so
float64 unit-norm rounding cannot break rigour.

An independent reference path (`fh_ref.py`) recomputes the same quantities in float64 by a
deliberately different route (trapezoid contraction matrix, reverse-order summation, explicit
rotation matrix, mu-form residual, explicit eight-row signed assembly, argmin gauge) and must
agree within the frozen bound `relative 1e-9 / absolute 1e-30`.
