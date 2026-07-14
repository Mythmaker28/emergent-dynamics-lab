# NOISE-AWARE SET IDENTIFICATION — SPECIFICATION
EXP-GT-NOISE-AWARE-SET-IDENTIFICATION-00. Deliverables 2,3,4,5,6,7,9.

## 0. Observable model
Channel i is observed over a response window of length L, aligned to the exogenous probe onset:
  y_i(t) = c_i · p(t) + n_i(t),   c_i = q · (1 − α_i κ_i)   (== v_i in the T6 manuscript)
`p` is the KNOWN response profile; `q` is the response (target |q|); `κ_i` the per-reference
contamination; `n_i` the noise. The instrument estimates the c_i WITH uncertainty and propagates.

## 1. Exact-zero prohibition (deliverable 2)
The instrument MUST NOT return Q = {0} on the basis of: a threshold crossing; low SNR; a non-significant
test; a noisy pre/post comparison; or agreement of noisy channels near zero. Exact zero is permitted ONLY
via an independent STRUCTURAL contract (`null_structural`): a construction known to be null, an
intervention physically unable to reach the response channel, or an exact conservation/symmetry result.
Even then, exact mathematical zero (`EXACT_ZERO_STRUCTURAL`) is distinguished from practical equivalence
(`PRACTICALLY_ZERO_WITHIN_MARGIN`, requires a declared margin δ_q and Q ⊆ [−δ_q, δ_q]).

## 2. Noise contract (deliverable 3) — preregistered bounded family
The instrument is validated against, and only against, this bounded family:
  1. white Gaussian; 2. correlated Gaussian AR(1), |φ|≤0.7; 3. OU drift residual (slow mean-reverting
  drift + white); 4. heavy-tailed (Student-t, df≥3, finite variance); 5. heteroscedastic (variance a
  bounded monotone function of within-window time); 6. reference-dependent scale (per-channel σ).
Outside this family the instrument may return `OUT_OF_SCOPE`. Detected residual lag-1 autocorrelation ρ is
handled by a HAC effective-sample-size inflation √((1+ρ)/(1−ρ)); polynomial drift order-1 removes net
within-window drift.

## 3. Calibration / development partition (deliverable 4)
All method selection and constant calibration use ONLY the development generator
(`noise_aware/devgen.py`, namespace seed 0x0DE7) and the historical regressions. The burned N=2000
hold-out is used only as named regressions, never for calibration and never prospectively. The fresh
prospective generator (`noise_aware/prospgen.py`) is committed and hash-gated BEFORE execution.

## 4. Channel uncertainty method (deliverable 5) and why it was chosen
Candidate methods considered: exact Gaussian t-intervals (fail under correlation/heavy tails);
Studentized intervals (fail under autocorrelation); split-conformal residual intervals (valid marginally,
but exchangeability broken by OU drift); plain block bootstrap (under-covers OU as measured, 0.79);
**studentized moving-block bootstrap with HC3 studentization, a max-|t| simultaneity correction, order-1
drift regressor, and a HAC ρ-inflation** (SELECTED). Measured development coverage of the SELECTED method
(Arm O, N=800): white 1.00, ar1 1.00, ou 0.99, heavy 0.98, hetero 0.99, refdep 0.96 — all ≥ 0.95 target.
The plain block bootstrap without ρ-inflation gave OU 0.79 and was rejected. Polynomial drift order ≥ 2
was rejected: the smooth exponential profile is near-collinear with quadratic/cubic drift, exploding the
coefficient variance (median relative width 1.6 → 5.5) and destroying informativeness.

## 5. Simultaneous coverage (deliverable 6)
Because several channels are combined, the channel intervals are FAMILY-WISE (simultaneous): the bootstrap
multiplier is the (1−α) quantile of the max-|t| statistic over channels. Consequence: selecting the
noisiest or largest channel cannot break coverage (mission section 13). Bonferroni/Holm were considered
but are conservative relative to the max-|t| bootstrap under cross-channel correlation.

## 6. Theorem-aware set propagation (deliverable 7) — derivation
Let I_i = [c_i^lo, c_i^hi] be the simultaneous CIs and M_i = |I_i| the induced magnitude intervals
(if 0 ∈ I_i then M_i = [0, max(|lo|,|hi|)] — a "zero-compatible" channel). Under contract:

* **attenuate, no anchor** (0 ≤ β_i < 1 ⇒ |c_i| ≤ |q|): a valid simultaneous LOWER bound is
  L = max_i c_i^lo,magnitude ; Q = [max(L,0), ∞). Proof: |q| ≥ max_i|c_i| ≥ max_i M_i^lo w.p. ≥1−α.
* **amplify, no anchor** (β_i ≤ 0 ⇒ |c_i| ≥ |q|): |q| ≤ min over DETECTED channels of M_i^hi.
  Zero-compatible channels are EXCLUDED from the min because a dead/dropout channel (|c|≈0) violates the
  amplification model; excluding it only widens Q, so coverage is preserved. Q = [0, U].
* **clean anchor** (∃ clean j, |c_j| = |q|): Q = [min_i M_i^lo, max_i M_i^hi]; pinned to the max
  (attenuate) or the min over detected (amplify) extreme under a sign contract.
* **sparse s, m−s ≥ 2, differential**: the largest set of mutually-overlapping M_i (interval max-clique)
  of size ≥ m−s is the clean majority; Q = their intersection.
* **no sign, no anchor**: `NON_IDENTIFIABLE` (T6-E: the scale is unrecoverable; Q unbounded).
Interval endpoints are NEVER plugged into deterministic point formulas: the whole interval is propagated.
Because each T6 relation is an exact monotone set-inclusion in the |c_i|, substituting simultaneous CI
endpoints yields a set that covers |q| with probability ≥ 1−α. Safety is thus INHERITED from channel
coverage; no step special-cases zero.

## 7. Statuses (deliverable 7) and the two arms (deliverable 9)
Statuses: POINT_IDENTIFIED, INTERVAL_IDENTIFIED, LOWER_BOUND_ONLY, UPPER_BOUND_ONLY, ZERO_COMPATIBLE,
BELOW_DETECTION_LIMIT, PRACTICALLY_ZERO_WITHIN_MARGIN, EXACT_ZERO_STRUCTURAL, NON_IDENTIFIABLE,
SIGN_CONTRACT_REQUIRED, ANCHOR_CONTRACT_REQUIRED, REFERENCE_MIXTURE_ILL_CONDITIONED, INSUFFICIENT_SNR,
OUT_OF_SCOPE. `ZERO_COMPATIBLE` means 0 ∈ Q, NOT that 0 is the only value.

* **ARM O (conditional)** may receive externally declared sign/anchor/sparsity contracts; each is recorded
  in `Result.external_contract` with its provenance. It validates conditional theorems; it does not claim
  the contracts are observable.
* **ARM B (blind)** receives NO truth-derived metadata. It may use only contracts establishable from
  independent sensor-physics calibration or declared intervention geometry (modelled as `op_sign`,
  `op_anchor`). With no establishable contract it returns a wider set or `NON_IDENTIFIABLE`. The two arms
  are computed by independent calls and MUST NOT be compared as if answering the same question.

## 8. Statistical target
Primary: 1−α = 0.95 simultaneous coverage. Primary safety endpoint: proportion of emitted sets excluding
the true response. HARD failure: any false `{0}` on a nonzero case; or a single invalid confident POINT on
the prospective hold-out. Diagnostics also at 80/90/99%.
