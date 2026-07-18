# CRD IDENTIFIABILITY — THEOREM MANUSCRIPT (independent treatment)

Notation: measurement `m = q + g0 w`; references `h_i = g_i w + e_i q`; `q` causal response, `w` drift,
`e_i` contamination of reference i; pre-window (q=0) gives `lam_i = g0/g_i`; drift-free `v_i = m - lam_i h_i =
q(1 - lam_i e_i)`.

## T1 — RMS dilution (holds)
`D_W = sqrt((1/W) ∫_0^W |Δr|² dt)`. For a finite-energy transient (`∫|Δr|² < ∞`), `D_W = O(W^{-1/2}) → 0`.
Assumption: transient (square-integrable) discrepancy. Counterexample (out of scope): a persistent step
`Δr → c ≠ 0` gives `D_W → |c|`, no dilution. Numerically verified (CFP→CRD-00). **Status: holds as stated.**

## T2 — Independent-sham insufficiency (holds)
A sham sharing only the *distribution* of `w` has an independent realization `w'`; `E[w-w']=0` but
`Var(w-w') = 2Var(w)` per episode. Distribution-matching is unbiased in expectation and useless per instance.
**Status: holds.**

## T3 — Single-reference multiplicative ambiguity (holds)
With one reference, `v_1 = q(1 - lam_1 e_1)`. Any `(q', e_1')` with `q'(1-lam_1 e_1') = q(1-lam_1 e_1)` is
observationally identical. Without an absolute scale, the response magnitude is unidentifiable. **Status: holds.**

## T4 — Differential contamination identifiability (holds, independently reproduced)
With M references of *distinct* `lam_i` and *distinct* `e_i`, the disagreements `v_i - v_j = q(lam_j e_j -
lam_i e_i)` are nonzero and locate the contaminated channels; if ≥1 reference is clean it recovers `q` exactly.
Sufficient conditions: coupling spread `std(1/lam)/|mean(1/lam)| ≥ 0.15`; ≥1 uncontaminated reference.
Independently reproduced: differential κ∈[0.02,0.35] corrected to within 1%. **Status: holds.**

## T5 — Common-mode non-identifiability (holds, independently reproduced)
If `e_i = c·g_i` for all i (⇒ `lam_i e_i = c·g0` constant), every `v_i = q(1 - c g0)` is attenuated identically:
observationally collinear with a rescaling of `q`. No passive-reference redundancy recovers the absolute scale.
Independently reproduced (common-mode → single attenuated value). **Status: holds.**

## T6 — Lower-bound result — **FALSIFIED AS HISTORICALLY STATED; RESTRICTED HERE**
**Historical claim:** the largest-amplitude channel `argmax_i |v_i|` yields a rigorous *lower bound* on `|q|`,
because "contamination attenuates (`e_i ≥ 0`, `lam_i > 0` ⇒ `|v_i| ≤ |q|`)."

**Falsifier:** the attenuation factor is `(1 - lam_i e_i)`. Amplification occurs whenever `lam_i e_i < 0` — i.e.
`e_i < 0` (negative contamination) OR `g_i < 0` (negative drift coupling, so `lam_i < 0`) even with `e_i > 0`.
Then `|v_i| > |q|` and `argmax` selects the *most amplified* channel. Measured against the FROZEN instrument:
`e = (-0.1,-0.1,-0.1)` → CORRECTED, `q_hat/q = 1.106` (10.5% **overstatement**, labelled confident). With
`g = (-0.8,-1.5,-1.15), e = (0.1,0.1,0.1)` (κ>0, "contract satisfied") → `q_hat/q = 1.105`. Empirical coverage of
the historical point estimate under amplifying contamination: **0/40**; mixed-sign: 3/40. Every historical dev and
prospective case used `e ≥ 0` AND `g_i > 0`, so this direction was never tested.

**Restricted theorem T6′ (holds, 40/40 coverage in all regimes):** if ≥1 reference is uncontaminated, `|q|` is an
*extreme* of `{|v_i|}`, so `|q| ∈ [min_i |v_i|, max_i |v_i|]` under **either** sign of `lam_i e_i`. A *point*
estimate (which extreme) requires an independently established sign contract `sign(lam_i e_i) ≥ 0`; absent it, the
method must return the bracket and abstain on the point. Under no clean reference and common-sign contamination the
bracket lies entirely on one side of `|q|` and is a one-sided bound whose direction is set by `sign(lam_i e_i)` —
a lower bound only under attenuation.

**Operational consequence:** the frozen CRD-03 instrument's `LOWER_BOUND_ONLY`/`CORRECTED` outputs are valid only
under an undeclared sign contract. The corrected operational rule is: emit a bracket; emit a point only with an
established sign contract; abstain otherwise.
