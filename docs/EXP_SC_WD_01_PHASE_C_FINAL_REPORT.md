# WD-01 Phase C — Final Scientific Report

## FINAL VERDICT
**WD-01 PHASE C: FAIL — CAUSAL READOUT DID NOT GENERALIZE.**
A minimal dynamic-range writing correction raised **storage** to two prospectively-decodable coordinates in
a viable droplet — a real advance over Phase B — but the second (order) coordinate is stored spatially and is
**not causally expressed**: it collapses under mean-transplant and is sub-threshold in-place. Causal-response
dimensionality stays ≈1.

- PHASE B CORRECTION: the "two EMAs ⇒ 1-D" and "substrate cannot store 2 magnitudes" claims were narrowed
  (see erratum, commit be08738). Phase C shows the frozen rule's 1-D was indeed **parameterization-bound**:
  a de-saturated, timescale-separated variant stores 2-D. WD-01 constrained the *writing rule*, not the substrate.
- SELECTED MECHANISM: **C1c** (H1 class). Same single write signal Ψ; two existing components; readouts
  unchanged. eta_w 0.05→0.015, eta_d1 0.03→0.35 (faster forgetting on the fast component), eta_d2 0.003→0.006,
  k_exp 2.0→1.0 (de-saturate Ψ). C2 (distinct signals) was **not authorized** — C1 sufficed for storage (minimality).
- WRITE SIGNALS: one (Ψ), read on two timescales. (H1 supported; H2 not needed.)
- STORED MEMORY DIMENSIONALITY: **2** (prospective h1=0.94, h2=0.94 within-family; strict train-on-dev 0.76/0.96;
  σ₂/σ₁ 0.02→0.23 vs C0; shuffle null ≈ −0.4).
- CAUSAL RESPONSE DIMENSIONALITY: **≈1** (transplant effdim 1.02, in-place 1.12). h1 causal 0.61/0.50; **h2
  causal −0.04 (transplant) / 0.30 (in-place, <0.50 gate)**.
- GROUPED DECODING: grouped leave-history-out throughout; row-LOO never used (Phase B error not repeated).
- PROSPECTIVE VALIDATION: sealed family (SHA-256 c6d0cd3c…) executed once. Storage PASSES; causal gate FAILS.
- MATERIAL TURNOVER: not re-measured in Phase C (inherited MCM M≈0.12).
- VIABILITY: preserved (localized size ≈31–36; no delocalization). This is **not** a viability tradeoff.
- CAPACITY–VIABILITY OUTCOME: **CV-A for storage** (de-saturation yields 2-D storage while viable); the causal
  shortfall is READOUT OBSERVABILITY, not viability.
- LEAKAGE AUDIT: clean (only physical nutrient drive enters dynamics; grouped, shuffle-controlled).
- REPRODUCTION READINESS: **NOT READY**. GENOME RELEVANCE: **NOT REQUIRED**. QUANTUM HARDWARE: **NOT USED**.

## OBSERVED
- C0 (frozen) reproduces rank-1 (dev min-score 0.19; prospective σ₂/σ₁ 0.036). Three C1 variants de-saturate
  and store 2-D on dev (C1a 0.84, C1c 0.84, C1b 0.61); C2a 0.79. C1c selected (highest σ₂/σ₁ 0.229, best F_low).
- Sealed prospective, C1c: both coordinates decode (0.94/0.94; strict train-on-dev 0.76/0.96), viable (size 31).
- Causal (common-body mean-transplant): h1 0.61, **h2 −0.04**; memory-inert control collapses both (−0.19/−0.19,
  validating the test). In-place, memory-isolated (dR=full−inert, spatial memory intact): h1 0.50, **h2 0.30**.
- The order coordinate h2 lives in the **spatial** memory pattern (10-D spatial decode 0.90 ≫ entity-mean 2-D 0.62).

## INFERRED
- The dynamic-range writing correction genuinely creates a second **stored** dimension: with de-saturated Ψ and
  a faster fast component, m_fast tracks the recent drive and m_slow the cumulative drive. H1 is supported at
  the storage/writing-map level.
- The bottleneck has **moved from writing to readout**. The two existing scalar readouts (m₊→uptake mean-field,
  m₋→attractant mean-field) plus mean-transplant collapse the spatially-stored order coordinate; the global
  response moves along a single axis (effdim ≈1), so h2 is not causally expressed and does not transplant.

## FALSIFIED
- Phase B's implicit "storage is intrinsically 1-D for this architecture" — falsified: storage is 2-D after a
  minimal parameter change, viability intact.
- The hope that de-saturated storage would automatically yield a 2-D **causal** readout — falsified: storage
  2-D does not imply causal 2-D; the mean-field/transplant readout is the limiter.

## SPECULATIVE
- A spatial/structured causal readout (full-field memory transplant preserving the pattern, or a
  polarization-sensitive probe) might causally express and transplant the order coordinate. This is a READOUT
  experiment, not a writing one.

## Independent opinion — is the central direction still justified?
Partly, and more narrowly than the handoff frames it. Phase C is a real result: a *minimal, interpretable*
writing change turns a genuinely rank-1 memory into a viable rank-2 **store**, and the earlier "1-D" was
parameterization-bound (Phase B over-generalized; corrected). But "multi-dimensional causal experience memory"
still fails at the point that matters for the project's ambitions — **causal expression and transplantable
organizational continuity** of the second coordinate. Storing a number the droplet cannot act on, and cannot
carry through a body swap, is not yet organizational memory in the sense the roadmap needs. I recommend
**one focused readout experiment** (spatial transplant / structured probe) before any further writing changes,
and I continue to advise deflationary language: this is two-dimensional *storage*, one-dimensional *causal
expression* — not individuation, not lineage. If the readout experiment also fails, the honest conclusion is
that local write+mean-field readout on this substrate caps causal experience memory at one dimension, and the
escalation toward reproduction/genome should stop.

## Next experiment (precise)
Preregister a **spatial causal readout**: (i) full-field memory transplant that preserves the (m1,m2) spatial
pattern into a standardized body (with an alignment/erase control), and (ii) a polarization-sensitive probe
response; test whether h2 reaches held-out causal R²≥0.5 and survives transplant. Keep writing = C1c frozen.
Do NOT add a third component or readout until this readout test is decided.

## Sealed/blocked (unchanged)
HMC PROSPECTIVE SPLIT remains SEALED. SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED. EXP-SC-01 remains BLOCKED.
REPRODUCTION EXPERIMENT: NOT EXECUTED.
