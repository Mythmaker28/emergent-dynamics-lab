# EXP-SC-H2-FINAL-CERTIFICATION-01 (H2-CERT-01) — Final Scientific Report

## FINAL VERDICT
**H2-CERT-01: FAIL — h2 IS TRANSIENT UNDER DEEP TURNOVER.**
**ARCHITECTURE DECISION: CLOSE h2 ESCALATION ON THE CURRENT ARCHITECTURE.**

- IMPLEMENTATION AUDIT: **ABLATIONS VALID — effect negligible on the decode** (not Outcome E). Unit tests on a
  nonuniform synthetic field: disabling D_m/eta_t changes the one-step memory field (3.4e-3 / 8.4e-4); engine
  params match the runner. DMM-01's "A0=A3=A4=A34 decode" is real and correctly re-worded (small field effect,
  swamped by growth-injected dispersion), not a bug.
- POWER TARGET: deep-turnover held-out h2 is ≤0.50 with CIs spanning zero, so a lower CI bound >0.50 is
  **mathematically unreachable for any N**; adequate power ⇒ CLOSE. M≤0.25 is feasible with full viability.
- PROSPECTIVE SAMPLE: sealed 4 seeds × 12 histories, executed once (SHA-256 4265b98c…).
- INITIAL h1: 0.94. INITIAL h2: 0.80 (95% CI [0.48, 0.93] — lower bound marginally under 0.50 at n=12).
- DEEP-TURNOVER M: 0.21 (step 650), 48/48 viable, localized size 49.
- DEEP-TURNOVER h1: 0.93 (robust). DEEP-TURNOVER h2: **−0.02, 95% CI [−2.17, 0.93] → NOT CERTIFIED**.
- NEW-MATERIAL h2: 0.28 → NOT CERTIFIED. CROSS-FAMILY STABILITY: **FAIL** (per-seed [−0.37,−0.47,+0.09,−0.04]).
- CAUSAL h2 RESPONSE / DISPERSION ABLATION: not run (retention failed → moot; Phase C already showed ~1-D causal).
- VIABILITY: PASS. LEAKAGE AUDIT: clean. REPRODUCTION READINESS: NOT READY. GENOME RELEVANCE: NOT REQUIRED.
  QUANTUM HARDWARE: NOT USED.

## OBSERVED
- M≤0.25 reached in a viable localized droplet (48/48). Held-out h2 collapses to ≈0 by deep turnover (−0.02 at
  M=0.21) with a CI spanning [−2.17, 0.93]; every seed-family fails; h1 stays ~0.93 throughout.
- Initial h2 storage is real (0.80) but its CI lower bound (0.48) is already at the margin at n=12.

## INFERRED
- h2 is an **initial-storage-only** statistic: robustly decodable at rest, frame-free, passively copied into
  new material by construction — but it does not persist as a distinguishable code once the droplet has
  substantially renewed itself, and its deep-turnover value is dominated by irreducible between-body noise.

## FALSIFIED
- "h2 is a turnover-surviving second organizational memory dimension" — falsified on adequately-powered,
  sealed, held-out data at M≤0.25.
- The Outcome-E worry (invalid prior ablations) — falsified (ablations verified active).

## SPECULATIVE
- A different architecture (distinct write signals, protected/bistable maintenance, or a compact heritable
  code) might support a persistent second dimension — but that is a NEW architecture, explicitly out of scope,
  and this certification does not motivate building it on the strength of h2.

## Independent judgment — synthesis of the whole arc (WD-01 → Phase C → SMC-01 → DMM-01 → H2-CERT-01)
The five experiments converge cleanly. **h1** — cumulative experience — is a genuine, robust, reproducible,
**one-dimensional** causal, transplantable, turnover-surviving organizational memory. **h2** — the putative
second coordinate — has now been tested at every stage: it exists at rest (decodable, frame-free), but it is
**not causal** (Phase C: ~1-D response, mean-transplant −0.04), and **not turnover-surviving** (this
certification: ≈0 at M≤0.25, held-out). It survived each earlier stage only at the noise margin, and the
adequately-powered kill-switch resolves that ambiguity: h2 is an epiphenomenal statistic, not a second
organizational-memory dimension. **The h2 escalation is closed on this architecture.** The project's real,
publishable result is the 1-D organizational memory (h1) with its full control suite; the individuation /
lineage / reproduction / genome program is **not** supported by the evidence and should not proceed on this
substrate. No further h2 certification should be requested (per the kill-switch rule).

## Sealed/blocked (unchanged)
HMC PROSPECTIVE SPLIT remains SEALED. SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED. EXP-SC-01 remains BLOCKED.
REPRODUCTION EXPERIMENT: NOT EXECUTED.
