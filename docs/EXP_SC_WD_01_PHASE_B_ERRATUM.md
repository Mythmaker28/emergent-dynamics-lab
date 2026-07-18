# WD-01 Phase B — Interpretive Erratum (required before Phase C)

The Phase B final report and gate certificate contain two overclaims. They are corrected here. The
OBSERVED numbers (rank≈1, corr(m1,m2)≈0.99, σ₂/σ₁≤0.015, leakage 0.57→0.19) stand; only the *scope of
inference* is narrowed.

## Overclaim 1 — "Two EMAs of one scalar are intrinsically one-dimensional"
**Incorrect as stated.** Two filters with different time constants can in principle encode multiple
*temporal* properties (e.g. recent vs. cumulative) of a single input signal.
**Corrected statement:** *Under the tested gains, clipping, histories and viable operating range, the two
filtered memory components became nearly collinear at the interrogation time.* The collapse is a property
of the parameterization+regime, not a theorem about two-timescale filters.

## Overclaim 2 — "The substrate cannot store two independent magnitudes"
**Too broad.** WD-01 constrains the **writing rule**, not the Particle-Dynamics substrate.
**Corrected statement:** *The present writing architecture did not store two independently recoverable
coordinates in the viable regimes tested.*

## Required distinctions (used throughout Phase C)
- **Substrate capacity** — what the particle dynamics could in principle hold. Not measured by WD-01.
- **Writing-map capacity** — rank of (history)→(stored memory) for a given write rule. WD-01: ≈1 for the frozen rule.
- **Memory-state dimensionality** — rank of the stored (m1,m2) field at interrogation. WD-01: ≈1.
- **Observability** — whether a decoder can read a stored coordinate at the chosen window.
- **Causal-response dimensionality** — independent axes the memory drives in the physical response. WD-01: ≈1.

Phase C tests whether a **minimal** change to the writing rule (C1 dynamic-range, else C2 distinct signals)
raises the writing-map/memory-state dimensionality to 2 **while preserving viability**, evaluated on a
freshly sealed prospective family with grouped (leak-free) decoding.
