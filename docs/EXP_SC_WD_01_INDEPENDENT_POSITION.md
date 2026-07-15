# EXP-SC-WRITING-DIMENSIONALITY-01 — Independent Scientific Position (Handoff §5)

Written after reading the code and BEFORE accepting the certificate's interpretation. The previous
agent's conclusions are evidence to audit, not doctrine.

## 1. What is genuinely established (I agree)
- A distributed, bounded memory field m=(m1,m2) exists, is causal, erasable, transplantable, survives
  material turnover, and is written by local experience — this reproduces across IOM-00 → MCM.
- **Temporal order is really stored and now really readable.** m−=m1−m2 encodes H1(N→c) vs H2(c→N);
  the 2nd readout (m−→attractant) makes it causal, collapsing ~63–73× under lam_minus ablation and
  absent on the uptake axis. Independently reproduced (seed 32000: 62.8×). This is a solid positive.
- Backward compatibility is exact. Viability and no-leakage hold.

## 2. What was only inferred (I challenge)
The certificate's load-bearing negative — "STORAGE is ~1-D because the write signal Ψ saturates" —
is **inferred, and its stated evidence is confounded**. Reading `continuous.py`/`harness.apply_cont_history`:
the two "independent" continuous coordinates are applied as **sequential nutrient drives** with
**mismatched amplitudes**: p1 = early phase, amp ∈ [0.005, 0.025]; p2 = late phase, order_w ∈ [0, 1].
That is a **20–47× amplitude mismatch**. The coordinate that fails to decode (p1) is the SMALL, EARLY one.

## 3. Is saturation really the most likely bottleneck?
The certificate says p1 fails *because Ψ saturates*. But Ψ = tanh(2(N−c)+…) saturates for the **large**
drive, not the small one — so p1 lived in Ψ's **linear** regime. Saturation, if anything, should blur the
**large** coordinate (p2), yet p2 is the one that decodes. **The stated mechanism points the wrong way for
the coordinate that actually failed.** The p1 failure is far better explained by (a) 20–47× smaller
amplitude (low SNR) and (b) being the early phase, buried under a much larger late phase, aliased into
the slow component's (p1+p2) sum. These are **history-design / dynamic-range** causes, not write saturation.

## 4. Competing explanations for the apparent one-dimensionality
Distinguishable, and I test them (Phase B): history-basis mismatch; stimulus dynamic-range; **single write
channel** (m1,m2 are two EMAs of ONE scalar Ψ, so storage is at most a 2-D projection of one signal, and
collapses to 1-D whenever Ψ is near-binary); the **m∈[−1,1] hard clip** (a saturation distinct from Ψ);
readout via a 5-D global settled signature (throws away spatial/temporal structure); replicate-leaking
row-LOO decoder (4 seeds/history → the certificate's row-LOO R²=0.57 is optimistic); n=12 power.

## 5. Smallest experiment that discriminates them
A frozen-writing sweep that (i) samples p1,p2 **independently over matched ranges**, (ii) decodes each
**directly from the memory field** (bypassing the tanh readout), and (iii) measures the **sensitivity
singular spectrum** of (p1,p2)→(m1,m2) plus a **constant-drive saturation curve**. If matched ranges +
direct-memory decode recover two coordinates → the "1-D" verdict was a design/readout artifact
("frozen memory was multi-dimensional; readout inadequate"). If they still collapse to rank-1 → the write
is intrinsically ~1-D, and I must further attribute it (Ψ vs clip vs single-channel).

## 6. What would make me reject the whole direction
If even a minimal, viability-preserving write change cannot produce a **second, independently decodable,
held-out** coordinate, then "multi-dimensional causal experience memory" is not reachable by *plumbing*
on this substrate, and the honest move is to stop escalating the framing (memory ≠ individuation ≠
lineage) rather than add channels/components until something looks high-dimensional.

## Position summary
I expect **the storage to be genuinely ~1-D in the viable regime (saturation real), but the certificate's
specific evidence and mechanism to be partly wrong** (history-amplitude mismatch confound; the true limiter
is a single saturating+clipped scalar write, not a p1-specific Ψ-saturation). Phase B decides.
