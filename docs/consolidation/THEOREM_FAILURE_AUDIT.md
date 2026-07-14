# THEOREM-FAILURE AUDIT — validity vs informativeness

The previously reported "rates" (T6-A 0.995, T6-B 0.970) were **not** theorem pass rates. Separating the metrics:

## Validity (mandatory: 0 violations among trials satisfying the hypotheses)
ε-separated statements, ε = 3σ_noise. Over **2000 trials each**:

| theorem | conclusion tested | **violations** |
|---|---|---|
| T6-A (attenuation, no anchor) | `max_i \|v_i\| ≤ \|q\|` | **0 / 2000** |
| T6-B (amplification, no anchor) | `min_i \|v_i\| ≥ \|q\|` | **0 / 2000** |
| T6-C (clean anchor) | `\|q\| ∈ [min\|v\|, max\|v\|]` | 0 |
| T6-E (no anchor, no sign) | non-identifiable ⇒ refuse | 0 |

**Zero unexplained violations.** The theorems hold.

## Informativeness (how often a non-vacuous conclusion is emitted)
T6-A 99.4% (1988/2000); T6-B 96.2% (1925/2000). The residual cases are **safe refusals**: when the contaminations
`β_i` are nearly equal the channels agree, and without a clean anchor the instrument cannot exclude common-mode,
so it returns NON_IDENTIFIABLE. Refusal ≠ violation.

## Classification of every earlier "failure"
All 14 were `NON_IDENTIFIABLE` with small β-spread (0.015–0.059). In every one the theorem conclusion still held
(T6-A ratios ≤ 1.0; T6-B ratios ≥ 1.0). None was a counterexample, an implementation error, or a tolerance failure.
