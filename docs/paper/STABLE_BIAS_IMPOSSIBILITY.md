# THE STABLE-BIAS IMPOSSIBILITY (deliverable 1)
Theorem appendix, EXP-GT-PC-00 consolidation. Formalizes why point certification failed on
`contaminated_highSNR`.

## Model
Observed data on m reference channels over a response window:
  y_i = c_i p + e_i,  i=1..m,   c_i = q(1 - beta_i),   e_i ~ noise (declared family).
`p` is the known response profile; `q` is the target; `beta_i` the (unknown) contamination action on
reference i. Write theta = (q, beta_1..beta_m). The observable-generating map is
  H(theta) = ( c_1, .., c_m ) = ( q(1-beta_1), .., q(1-beta_m) ).

## Proposition 1 (observational collinearity / non-identifiability)
For any q' != 0 define beta'_i = 1 - (q/q')(1 - beta_i). Then theta' = (q', beta'_1..beta'_m) satisfies
  c'_i = q'(1 - beta'_i) = q(1 - beta_i) = c_i   for every i.
Hence theta and theta' induce the **identical** distribution of observed data y (identical means c_i p,
identical noise). Therefore q is NOT identifiable from {y_i} alone: the family {theta' : q' != 0} is an
observationally equivalent orbit. Only a constraint on some beta_i (e.g. a certified clean reference
beta_k = 0, or a known gain, or a bound) intersects the orbit in a point. (This is the T6-E direction made
explicit as a one-parameter unidentified scale.)

## Proposition 2 (internal precision cannot resolve it)
Let T_n be ANY estimator of q computed from n independent replications (or from SNR -> infinity) using
only internal information: repeated measurement, high SNR, leave-one-reference-out stability,
leave-one-probe-out stability, confidence-interval width, independent software implementations, bootstrap
consistency. Because theta and theta' produce identical data distributions, T_n has the identical sampling
distribution under theta and under theta'. Thus for any valid coverage guarantee simultaneously at theta
and theta', the confidence set must contain BOTH q and q'. Since q' is arbitrary, any internally-valid set
that covers is the whole unidentified orbit (an interval/line) — NOT a point. Equivalently: no internal
procedure can output a point with guaranteed validity across the orbit. **Internal precision (small
variance, stability, replication agreement) is orthogonal to identifiability.**

## Corollary (stable bias — the operational failure mode)
Suppose a procedure assumes reference k is clean (beta_k = 0) and reports q_hat = c_hat_k. As SNR -> inf,
c_hat_k -> c_k = q(1 - beta_k) almost surely, with Var(q_hat) -> 0. If the assumption is wrong
(beta_k != 0) the estimate CONVERGES to the biased limit q(1 - beta_k), is STABLE under leave-one-out of
the other references (c_hat_k does not depend on them), and passes bootstrap consistency (c_hat_k is
consistent for c_k). Every internal diagnostic passes; the limit is wrong.

## Numerical demonstration (`point_cert/stable_bias_demo.py`, raw in stable_bias_demo.json)
q = 1.0; assumed-clean channel k=0 is actually 30% contaminated (beta_0 = 0.30); biased limit q(1-beta_0)=0.700.
| SNR | q_hat mean | Var(q_hat) | bias | leave-one-out shift |
|----:|-----------:|-----------:|-----:|--------------------:|
| 5   | 0.7004 | 4.1e-2 | -0.300 | 0 |
| 50  | 0.7007 | 4.3e-4 | -0.299 | 0 |
| 1000| 0.7000 | 1.1e-6 | -0.300 | 0 |
Variance -> 0, estimate converges, leave-one-out shift is exactly 0 — yet bias = -0.300 persists.

## Connection to the prospective result
`contaminated_highSNR` covered only 7/23 certified points. There the operative "clean-anchor / sign"
contract selects a reference that is in fact contaminated; the high SNR makes the wrong estimate precise
and stable, so certificates C4 (leave-one-ref), C5 (fold), C6 (selection-aware), C8 (SNR floor) all pass.
This is Corollary above, realized. The only fix is an EXTERNAL anchor that constrains some beta_i (see
`EXTERNAL_ANCHORS.md`). Hence: **point certification is impossible on the stable-contamination direction
without external calibration**, and is withdrawn.
