# EXP03-A Internal Critique — PASS A (mechanism challenge)

- Run: RUN-20260710-1850-EXP03A. Model: claude-opus-4-8 (lock lifted). Target: density-preference mechanism @3406ef0.
- Question: is density preference only a trivial reformulation of the CORE V0 interaction matrix / range? What
  result would truly distinguish EXP03-A from a mere interaction-matrix or range change?

## Argument that it is NOT trivial

- CORE V0 force on i is a sum of 2-body terms: `sum_j f(type_i, type_j, d_ij)`. The density term is
  `k*(comfortable - sum_j K(d_ij)) * ghat_i`: the scalar `(comfortable - sum_j K)` couples ALL neighbours
  multiplicatively with the direction to the local neighbour mass. The force i feels toward a given neighbour
  therefore depends on HOW MANY OTHER neighbours i has. This is irreducibly many-body; no pairwise
  type-interaction (any matrix, any range/short_range/repulsion) can produce a term whose SIGN flips with the
  total local neighbour count.

## Distinguishing observables / ablations (pre-declared)

1. **Homeostatic sign-flip:** a probe particle's radial density force reverses direction as its local density
   crosses `comfortable_density`. Demonstrated at the force level by
   `test_homeostatic_sign_below_and_above_comfortable`. No interaction-matrix change yields a neighbour-count
   sign reversal.
2. **Self-limiting density:** varying `comfortable_density` at a fixed interaction matrix should shift the
   equilibrium local density / cluster compactness toward the target — a homeostatic set-point an
   attraction/repulsion balance does not have.

## Verdict

The mechanism is genuinely distinct from an interaction-matrix/range change (many-body, sign-flipping). **No STOP.**
IMPORTANT consequence carried into analysis: a P/M *distributional shift* alone does NOT prove a distinct causal
family (an interaction change could also shift the distribution). Distributional shift is therefore reported as
Level 1 (descriptive) only; the mechanism's distinctness rests on the sign-flip/self-limiting ablation, not on the
screen distribution.
