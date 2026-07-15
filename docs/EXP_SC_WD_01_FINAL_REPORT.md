# EXP-SC-WRITING-DIMENSIONALITY-01 — Final Scientific Report

## FINAL VERDICT
**EXP-SC-WRITING-DIMENSIONALITY-01: FAIL — WRITING REMAINS EFFECTIVELY ONE-DIMENSIONAL (viable regime).**
Scope executed: Phase A (replicate) + Phase B (frozen-writing bottleneck audit). Phase C (writing redesign)
was reached, justified, and **preregistered but not executed** (requires a fresh sealed prospective family).

- PREVIOUS MCM REPLICATION: A-PASS — core replicated (backward-compat exact; order-readout 62.8×; storage rank-1).
- PRIMARY BOTTLENECK: single saturating (Ψ=tanh) + hard-clipped (m∈[−1,1]) **scalar** write; only ONE
  experience signal is written, on two timescales.
- SATURATION HYPOTHESIS: **CONFIRMED but corrected** — real, yet the certificate's "p1 fails because Ψ
  saturates" is wrong (p1 was in Ψ's linear regime); the prior 1-D evidence was also confounded by a
  20–47× history-amplitude mismatch (HISTORY-DESIGN, secondary).
- STORED MEMORY DIMENSIONALITY: effectively **1** (σ₂/σ₁ ≤ 0.015 entity-mean; corr(m1,m2)≈0.99).
- CAUSAL RESPONSE DIMENSIONALITY: **1** (effdim≈1.08, unchanged; consistent with rank-1 storage).
- MATERIAL TURNOVER: preserved (inherited M≈0.12; not re-run this session).
- VIABILITY: preserved in the viable/localized regime (matched drives: largest-entity size 32–54). The
  mismatched original-style regime (late drive→1.0) DELOCALIZES the droplet (size ≈3321/4096) — a
  **VIABILITY–CAPACITY TRADEOFF**: the only regime with any 2nd-coordinate hint is outside viability.
- LEAKAGE AUDIT: clean — no tag/label/cohort/seed/probe id in the dynamics.
- WRITING MODIFICATION: **none** (diagnostic only; redesign preregistered).
- PROSPECTIVE VALIDATION: not run (no new mechanism to validate; HMC/SC prospective remain sealed/blocked).
- SERIAL BOTTLENECK: NOT AUTHORIZED (multi-dim memory did not pass).
- REPRODUCTION READINESS: **REPRODUCTION NOT READY**.
- GENOME RELEVANCE: **GENOME NOT REQUIRED** at this stage.
- QUANTUM HARDWARE: **NOT USED** (classical identifiability/saturation bottleneck; no benchmarkable quantum advantage).

## 1. What was observed
Backward compatibility is exact (max|dev|=0 over 200 steps). Temporal order is genuinely stored (m−=m1−m2)
and now causal (attractant channel, 62.8× collapse under ablation, uptake-axis clean) — a solid positive that
replicates. In a frozen-writing sweep, the memory saturates across essentially the whole viable drive range
(slow m2 ≥0.73 even at p=0.001; both components clip by p≈0.02), and the input→memory map is **rank-1 in every
regime** (mismatched, matched, matched-low). No regime decodes two coordinates from the stored field at R²≥0.5.

## 2. What I infer
The storage limit is intrinsic to the write, but not for the reason stated: m1,m2 are two EMAs of one
saturating, clipped scalar Ψ, so they are near-collinear and carry ~one number. More readout channels cannot
fix this; a second **independent write signal** (or a de-saturated analog write) is required. Decoding
directly from memory rules out a "readout-only" explanation.

## 3. What was falsified
(a) The certificate's mechanism ("p1 fails because Ψ saturates") — p1 sat in Ψ's linear regime; it failed
from amplitude+phase burial. (b) The hypothesis that the frozen memory is secretly multi-dimensional and only
the readout was inadequate — direct-from-memory decode is still rank-1. (c) The certificate's p2 R²=0.57 as a
clean storage signal — re-running that row-LOO reproduces 0.570 exactly, but leakage-free grouped leave-history-out on the SAME
published data gives 0.190 (+0.38 inflation), and it vanishes when ranges are matched.

## 4. Independent opinion
The droplet program has produced a real, defensible result (causal, transplantable, turnover-surviving,
order-sensitive memory). But "multi-dimensional causal experience memory" is **not** reachable by adding
readout/plumbing on this substrate: one scalar write ⇒ one stored magnitude. The vocabulary should stay
deflationary — this is *acquired order-sensitive memory*, not individuation, not lineage. The next step is a
**single, minimal, honestly-sealed** write change (component-specific drive + de-saturation), and if that
fails to yield a second independently-decodable held-out coordinate, the escalation toward reproduction/genome
should stop rather than accumulate mechanisms until something looks high-dimensional.

## 5. Precise next experiment
Execute the preregistered Phase C (`EXP_SC_WD_01_PHASE_C_PREREGISTRATION.md`): compare C0/C1/C2 (prefer C2 —
m1←uptake-surprise, m2←(N−c) balance — the smallest change giving two independent write axes) over a matched,
de-saturated history band; select on new dev seeds; validate ONCE on a newly sealed prospective family; pass
only if two coordinates each reach held-out R²≥0.5 with incremental independence, viability, and no leakage.

## Sealed/blocked (unchanged)
HMC PROSPECTIVE SPLIT remains SEALED. SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED. EXP-SC-01 remains BLOCKED.
REPRODUCTION EXPERIMENT: NOT EXECUTED.
