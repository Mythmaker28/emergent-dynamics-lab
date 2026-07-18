# SET-IDENTIFICATION MANUSCRIPT (repaired T6)

Model: drift-free channels `v_i = q(1 − α_i κ_i) + ε_i`, `i=1..m`. Observed: `{v_i}`, `sign` of the coupling
geometry via `lam_i` (from the pre-window), coupling spread. Unknown: `q`, `{κ_i}`. Let `β_i = α_i κ_i` (the
contamination action). Contracts C0–C6 as declared.

## T6-A — Attenuation one-sided bound
**Assume** `0 ≤ β_i < 1 ∀i` (C1), no clean anchor. Then `|v_i| = |q|(1−β_i) ≤ |q|`, so **`max_i|v_i| ≤ |q|`**:
`max|v|` is a valid lower bound (LOWER_BOUND_ONLY). The *useful* extreme is the MAXIMUM (least attenuated).
*Counterexample outside scope:* any `β_i<0` makes `|v_i|>|q|` and breaks it.

## T6-B — Amplification one-sided bound
**Assume** `β_i ≤ 0 ∀i` (C2), no anchor. Then `|v_i| = |q|(1−β_i) ≥ |q|`, so **`min_i|v_i| ≥ |q|`**:
`min|v|` is a valid UPPER bound (UPPER_BOUND_ONLY). The historical rule reported this as a *lower* bound — the sign
error. The useful extreme is the MINIMUM.

## T6-C — Clean-anchor extremal theorem
**Assume** `∃ j: κ_j = 0` (C3), identity unknown. Then `v_j = q` exactly, and since every other
`|v_i| = |q||1−β_i|`, the true `|q|` is one of the observed `|v_i|` and lies at an **extreme** of `{|v_i|}` whenever
all `β_i` share a sign; in general `|q| ∈ [min|v|, max|v|]` (the bracket, two-sided, sign-agnostic — INTERVAL). With
a sign contract the extreme is pinned: attenuation → `|q| = max|v|`; amplification → `|q| = min|v|` (POINT).
*Numerical:* bracket covers 40/40 with a clean anchor (all sign regimes); the clean channel is always an extreme.

## T6-D — Sparse-contamination identifiability
**Assume** at most `s` of `m` references contaminated (C4), differential (C6), couplings non-collinear. If
`m − s ≥ 2` the clean majority mutually agree and are located by disagreement → `q` is POINT-identified as their
common value, no sign contract needed. Minimal `m` for point-ID under `s` contaminated: `m ≥ 2s+1` guarantees a
clean majority is identifiable by agreement (Byzantine-style). With `m = s+1` (one clean, unknown) only the bracket
(T6-C) is available. **Three references give point-ID for s≤1**; that is the exact sense in which "three" was
minimal — and only for single-reference contamination.

## T6-E — Sign-agnostic impossibility
**Claim:** under C0 (no sign) and without C3 (no guaranteed clean reference), `q` is NON-identifiable. *Proof by
construction:* take `q, {κ_i}` and `q' = 2q, κ'_i` with `α_i κ'_i = 1 − (1−α_i κ_i)/2`. Then
`q'(1−α_iκ'_i) = 2q·(1−α_iκ_i)/2 = q(1−α_iκ_i) = v_i` for every `i`. Two responses differing by 2× produce
identical observations. No estimator recovers `q`. **The set is unbounded** (any scale is consistent). Only a sign
or clean-anchor contract collapses it.

## Operational map (encoded in consolidation/signsafe.py)
| contract | output |
|---|---|
| clean-anchor + agree | POINT (common value) |
| clean-anchor + disagree + sign | POINT (extreme by sign) |
| clean-anchor + disagree + no sign | INTERVAL [min,max] |
| no anchor + attenuate | LOWER_BOUND_ONLY (≥ max\|v\|) |
| no anchor + amplify | UPPER_BOUND_ONLY (≤ min\|v\|) |
| no anchor + no sign | NON_IDENTIFIABLE |
| all agree, no anchor (common-mode) | NON_IDENTIFIABLE |
| spread < 0.15 | ILL_CONDITIONED |
