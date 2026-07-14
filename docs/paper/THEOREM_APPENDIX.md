# THEOREM APPENDIX (deliverable 13)
Self-contained statements. Model: channels `v_i = q(1 − α_iκ_i) + ε_i`, `β_i = α_iκ_i`, contracts declared.

## T6-A — Attenuation one-sided bound
If `0 ≤ β_i < 1 ∀i` (no anchor), then `|v_i| = |q|(1−β_i) ≤ |q|`, so `max_i|v_i| ≤ |q|`: a valid LOWER bound.
## T6-B — Amplification one-sided bound
If `β_i ≤ 0 ∀i` (no anchor), then `|v_i| ≥ |q|`, so `min_i|v_i| ≥ |q|`: a valid UPPER bound.
## T6-C — Clean-anchor bracket
If `∃ j: κ_j = 0`, then `v_j = q`; `|q|` lies in `[min_i|v_i|, max_i|v_i|]`, pinned to the max (attenuate) or
min (amplify) under a sign contract.
## T6-D — Sparse-contamination identifiability
At most `s` contaminated, differential, non-collinear: `m − s ≥ 2` ⇒ clean majority located by agreement;
`m ≥ 2s+1` ⇒ point-identified by agreement (Byzantine-style). Under noise/dropout the budget must count each
potential dropout as a possible contaminant (see SPARSE_UNDER_DROPOUT).
## T6-E — Sign-agnostic impossibility
Under no sign and no clean anchor, `q` is non-identifiable: for `q' = 2q`, `κ'` with `α_iκ'_i = 1−(1−α_iκ_i)/2`
gives identical `v_i`. The set is unbounded.

## Proposition 1 — Observational collinearity (general)
For channels `c_i = q(1−β_i)` and any `q' ≠ 0`, `β'_i = 1 − (q/q')(1−β_i)` gives `c'_i = c_i ∀i`. Hence
`(q,β)` and `(q',β')` induce identical observed distributions; `q` is unidentifiable without a constraint on
some `β_i`.

## Proposition 2 — Internal precision cannot resolve non-identifiability
Any estimator using only internal information (repeated measurement, high SNR, leave-one-reference-out,
leave-one-probe-out, CI width, independent implementations, bootstrap) has identical sampling distribution
under `(q,β)` and `(q',β')` of Prop 1. A set with valid coverage at both must contain both `q` and `q'`;
since `q'` is arbitrary, any internally-valid covering set is the whole unidentified orbit, not a point.

## Corollary — Stable bias
Assuming reference `k` clean when `β_k ≠ 0` gives `q_hat = c_hat_k → q(1−β_k)` with `Var → 0`, stable under
leave-one-out, bootstrap-consistent — a precise, stable, biased limit. Demonstrated numerically
(`stable_bias_demo.py`): `Var(q_hat) → 1.1e-6`, `bias → −0.30` at `β_0 = 0.30`. This is the
`contaminated_highSNR` prospective failure (7/23 covered).

## Validity vs informativeness (proved vs empirical)
T6-A..E and Propositions 1–2 are EXACT. The 0/10,000 false-zero property is EXACT (structural). Set coverage
(0.959/0.969) and point coverage (0.795) are EMPIRICAL on frozen hold-outs and are not promoted to theorems.
