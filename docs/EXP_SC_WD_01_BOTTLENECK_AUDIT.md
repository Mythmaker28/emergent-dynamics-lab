# EXP-SC-WRITING-DIMENSIONALITY-01 — Phase B: Causal Bottleneck Audit (writing FROZEN)

Primary question: *is the ~1-D causal memory intrinsic to the writing dynamics in the viable regime, or an
artefact of history design and readout?* Physics unchanged; only inputs varied and the memory field read.
Design preregistered in `results/wd01/run_diag.py` (fixed RNG seeds 4101/4102/4103; DEV-family seeds
32100–32103 only; prospective 33xxx untouched). Raw: `results/wd01/wd01_diag_raw.pkl`; summary:
`results/wd01/diag_summary.json`; figure: `results/wd01/wd01_diagnostic.png`.

## D2 — Constant-drive saturation curve (OBSERVED)
Single-phase drive p (T=60)+settle, seed 32100. Entity-mean memory and reconstructed-Ψ occupancy:

| p | Ψ occ(|Ψ|>0.9) | m1(fast) | m2(slow) | clip1 | clip2 | size |
|---|---|---|---|---|---|---|
|0.001|0.09|0.45|0.73|0.00|0.33|36|
|0.005|0.43|0.63|0.86|0.05|0.55|38|
|0.012|0.71|0.82|0.95|0.24|0.80|41|
|0.020|0.83|1.00|1.00|0.91|1.00|47|
|0.050|0.94|0.98|1.00|0.85|0.97|151|

- The **slow component m2 is already ≥0.73 at the smallest drive** and pins to the ±1 clip by p≈0.02.
- The localized entity is viable for p≲0.02–0.03; by p=0.05 it grows/disperses (size 151). So the **viable
  drive range and the graded-memory range barely overlap**: within viability, the mean memory is largely
  saturated (Ψ nonlinearity + hard clip), with only the fast component m1 retaining graded range.

## D1 — Storage rank & direct-from-memory decode (OBSERVED)
Independent (p1,p2), 12 histories × 4 seeds/condition, decode by grouped **leave-history-out** ridge from the
entity-mean memory; sensitivity σ₂/σ₁ from the standardized (p1,p2)→(m1,m2) linear map (decoder-independent).

| condition (p1,p2 range) | valid | corr(m1,m2) | σ₂/σ₁ | decode p1 | decode p2 |
|---|---|---|---|---|---|
| A mismatch  p1∈[.005,.025], p2∈[0,1] | 48/48 | +0.988 | 0.015 | −0.54 | **+0.38** |
| B matched   p1,p2∈[.005,.025]        | 48/48 | ~0 (clip noise) | 0.000 | +0.05 | −0.34 |
| C matched-low p1,p2∈[.001,.006]      | 48/48 | +0.999 | 0.004 | +0.18 | +0.03 |

- **The input→memory map is rank-1 in every regime** (σ₂/σ₁ ≤ 0.015 for the entity mean; ≤0.13 for a 10-D
  spatial summary). corr(m1,m2)≈0.99 wherever the memory is not simply clip-pinned.
- **No condition yields two coordinates decodable at R²≥0.5** (the G_TWO_DIMS threshold). The best single
  coordinate is p2=0.38 in the mismatched design — and **it does not survive range-matching** (B: p2=−0.34).
- The certificate's row-LOO p2=0.57 was inflated by replicate leakage; grouped-LOO gives 0.38.

## Interpretation — which explanation wins
- **Saturation is REAL but the certificate's mechanism was wrong.** p1 did not fail "because Ψ saturates"
  (p1 sat in Ψ's linear regime). p1 failed from 20–47× smaller amplitude + early-phase burial. Correcting
  the mismatch does **not** rescue a 2nd dimension → the limiter is deeper than the p1/p2 story.
- **Root cause = a single saturating+clipped scalar write.** m1,m2 are two different-timescale EMAs of the
  SAME experience scalar Ψ. Because Ψ is near-binary for any non-tiny drive and m is hard-clipped at ±1
  (slow component saturated across the whole viable range), the two EMAs are near-identical → **storage is
  effectively rank-1**. Adding *readout* channels (what MCM did) cannot add a *storage* dimension.
- **Direct-from-memory decode excludes a "readout inadequate" escape.** Bypassing the tanh readout and
  decoding straight from the stored field still fails → the deficiency is in **storage**, not readout.

## Phase-B verdict (Handoff §8.5 labels)
- **PRIMARY: SATURATION BOTTLENECK CONFIRMED** — specifically a single-scalar, saturating (Ψ) and
  hard-clipped (m∈[−1,1]) write; the slow component is saturated throughout the viable regime.
- **SECONDARY: HISTORY-DESIGN BOTTLENECK** — the *prior evidence* for 1-D was confounded by a 20–47×
  history-amplitude mismatch and a replicate-leaking decoder; corrected here.
- REJECTED: "frozen memory was multi-dimensional; readout inadequate" (storage itself is rank-1).

→ This **justifies the Phase-C writing-redesign gate** (see preregistration). It does not, by itself,
demonstrate a second dimension.

## Verification addendum (differential — independent second/third paths)
- **Third independent rank estimator agrees.** Participation ratio (effective rank) of (m1,m2):
  A=1.012, B=1.000, C=1.001. Together with corr(m1,m2)≈0.99 and σ₂/σ₁≤0.015, three independent
  estimators converge on **rank 1**. Grouped-LOO ridge and plain OLS-LOO both keep every coordinate <0.5.
- **Correction to viability wording.** "Valid" in the runner meant "an entity was detected", not
  "localized". Largest-entity size by condition: A=**3321**/4096 (delocalized — the mismatched original-style
  late drive up to 1.0 disperses the droplet), B=54, C=32 (localized). So the **only** regime showing any
  second-coordinate hint (A) is **outside viability**; in the viable localized regimes (B, C) storage is
  unambiguously rank-1. This adds a **VIABILITY–CAPACITY TRADEOFF** label: capacity for a 2nd dimension and
  droplet viability do not co-occur here. Memory is near-maximally written in all conditions (mean m+ =
  1.86–2.00 of 2.0), so the negative is not under-writing.
- **Leakage proven on the PUBLISHED number.** Re-running the certificate's own row-LOO on
  `cont_prospective.pkl` reproduces its published **p2 R²=0.570** exactly; grouped leave-history-out on the
  same data gives **0.190** (+0.38 inflation from 4 seeds/history sharing the target). Even the certificate's
  best continuous coordinate is ≈0.19 held-out — below the 0.5 gate. Raw log: `results/wd01/verification.txt`.
