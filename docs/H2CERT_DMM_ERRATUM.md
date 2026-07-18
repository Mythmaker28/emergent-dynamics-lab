# H2-CERT-01 — DMM-01 Interpretive Erratum + Implementation-Ablation Audit

## Wording corrections (required)
- Replace "h2 survives every test only at the noise margin" with: **h2 initial storage is robust; its
  persistence and causal expression under turnover remain marginal and family-dependent.**
- Replace "new material acquisition demonstrates organizational reconstruction" with: **the existing growth
  rule (`Mf += g·m`) passively copies local intensive memory into newly added mass; this establishes local
  propagation BY CONSTRUCTION, not active reconstruction.**

## Implementation-ablation audit (G4/G5/G6) — VERIFIED VALID
Deterministic unit test on a deliberately nonuniform synthetic memory field:
- Engine configs match runner: A0 (eta_t0.010,D_m0.010), A3 (D_m0), A4 (eta_t0), A34 (both 0) — confirmed in `eng.mem`.
- One-step memory-field change vs A0: A3 max|ΔMf|=3.4e-3, A4=8.4e-4, A34=4.2e-3 → **ablations are physically ACTIVE**.
- Isolated terms per step: diffusion max 4.2e-2, templating max 1.0e-2 (non-negligible on the field).
- Verdict: **ABLATIONS VALID — EFFECT NEGLIGIBLE IN THE REAL REGIME (on the h2 decode).** DMM-01's finding
  "A0=A3=A4=A34 (decode)" is real: the smoothing changes the field but its effect on the DIST h2-decode is
  swamped by growth-injected dispersion. DMM's "not smoothing" conclusion stands, correctly re-worded: the
  smoothing ablation has a small (not zero) field effect and a negligible decode effect. Not Outcome E.
