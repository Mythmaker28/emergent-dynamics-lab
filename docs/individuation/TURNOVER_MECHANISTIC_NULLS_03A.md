# LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A — Mechanistic-null specification (TASK 3)

*Controls that distinguish passive persistence from reconstruction, and direct coupling from emergent causality.
Implemented in `turnover_diag_engine.py` (validated byte-identical to the frozen engine with all flags off) +
`turnover_dev_diagnostics.py`. DEV results in `TURNOVER_DIAGNOSTICS_CERTIFICATE.json`.*

| null | definition | DEV result (4 feasible worlds) | frozen status |
|---|---|---|---|
| **A. C1c normal** | passive-copy engine, unchanged | reference: deep own +0.131, m₊ ≈ 0.15–0.33 | main line |
| **B. eta_w=0 (post-history)** | no new writing after the history; passive inheritance still allowed | m₊ ratio **0.44×** intact — a decayed remnant survives | **passive carry-over/decay, NOT reconstruction** (stated honestly) |
| **C. up_ref := 0** | global write reference zeroed, local history unchanged | memory ratio **1.00**, deep own **identical** ([0.182,0.113,0.149]) | diagnostic, **non-gating** (frozen); global channel causally irrelevant |
| **D. algebraic readout prediction** | predicted own-fraction = ⟨λ₊·m₊/(1+λ₊·m₊)⟩ at probe start | observed = **0.87×** predicted (obs ≤ pred, all worlds) | **gating interpretation**: effect ≤ direct coupling ⇒ no emergent causality |
| **E. copy-disabled** | drop `Mf += g·m` so new growth does not inherit memory (old material unchanged) | m₊ ratio **0.26×** intact — memory **collapses** | clean ablation of an existing term; **passive copy is necessary** |

## Why each is a clean ablation, not new physics

B, C, E each **zero exactly one pre-existing term** of the frozen engine (the writing gain `eta_w`; the global
reference `up_ref`; the inheritance term `Mf += g·m`), exactly as the existing ablation engine zeros `lam_plus/
lam_minus`. `DiagEngine(up_ref_zero=False, copy_disabled=False)` is **byte-identical** to
`MultiChannelMemoryEngine` over 300 steps (max|Δ| = 0.0), proving the ablations are surgical. D is a pure
post-hoc calculation on the intact trajectory (no engine change).

## Frozen interpretations (pre-prospective)

- **D is the null for the interventional effect.** If prospective `own_observed ≤ own_predicted`, the interventional
  gate is **not independent evidence** — it is the algebraic multiplier. Only `own_observed ≫ predicted` (with the
  ownership gate also passing) would indicate something beyond direct coupling.
- **E frozen meaning:** memory survival that disappears under copy-disable is **passive copy**, by definition not
  material-independent persistence and not reconstruction. C1c cannot exhibit reconstruction (no error-correcting
  term); a copy-disabled-robust survival would be a surprise that this architecture cannot produce.
- **C is diagnostic/non-gating** (frozen): `up_ref := 0` bounds the known global channel. It is not the only possible
  distributed channel — see the L/P/E/G access-structure test.
- **Never** describe B (eta_w=0) alone as a test of active reconstruction. It tests passive carry-over.
