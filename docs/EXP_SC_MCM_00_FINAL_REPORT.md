# EXP-SC-MULTI-CHANNEL-ORGANIZATIONAL-MEMORY-00 — FINAL REPORT
## Orthogonal Functional Readout of Distributed Experience Memory

**Branch:** `exp/sc-multi-channel-organizational-memory-00`  **Starting commit:** `0ea1250` (IOM-00 final)
**Physics:** frozen scaffold engine `7c91b91` + the IOM-00 memory WRITING (unchanged) + one new READOUT
channel. With `lam_minus=0` the mechanism is **bit-identical to IOM-00** (verified max deviation 0.0).

## Erratum to IOM-00 (issued here)
IOM-00's `PASS — HISTORY-CLASS MEMORY ONLY` is imprecise; the response decoded net exposure at
R2 ~ 0.95-0.97, so the accurate reading is `PASS — LOW-DIMENSIONAL CAUSAL EXPERIENCE MEMORY` with
`INDIVIDUATION: FAIL`, and "high-dimensional storage" is downgraded to "high-dimensional internal variation;
reproducible high-dimensional history information not established" (held-out memory->history R2 < 0).

## Storage-information audit (Phase 1, no new physics)
From frozen IOM-00 states: temporal ORDER is reproducibly stored in the contrast m- = m1 - m2
(m-(H1)=-0.23 vs m-(H2)=-0.34; paired diff std 0.004-0.007 -> **100% held-out classification, dev AND
prospective**). Continuous SPATIAL sector history is NOT stored (held-out memory->amps R2 ~ 0.01 global,
-1.6 field). Decision **S1** (order is stored): freeze writing, modify read-out only.

## Mechanism (Level R1 read-out ladder, minimal)
Two orthogonal scalar channels on the EXISTING two-component memory:
    m_plus  = m1 + m2  -> nutrient UPTAKE:        uptake_eff       = uptake * (1 + lam_plus  * tanh(m_plus))
    m_minus = m1 - m2  -> attractant PRODUCTION:  c_production_eff = s*rho  * (1 + lam_minus * tanh(m_minus))
Writing frozen (lam_plus=0.25 as IOM; lam_minus=0.15 new). Independently ablatable; no tags.

## Results (dev AND held-out prospective)
- **Order read-out (G6) + channel specificity (G9): PASS — the load-bearing test IOM-00 failed.** Temporal
  order now drives a DISTINCT accessible output (attractant / mean_c). Ablating only the m- channel
  (lam_minus=0) collapses the order effect on that axis by **70x (dev) / 73x (prospective)**, while the
  uptake axis carries no order (~0.0001). Ablating both channels -> exactly 0.
- **Dose read-out retained (G5), erasure (G7), transplant (G8), clone ceiling (G13), viability (G3, size
  ~103), turnover (G4, M~0.12): PASS.** Backward compatibility (G2) exact.
- **Response dimensionality (G10), two continuous history dims (G11), individuation (G12): FAIL.** On the
  held-out family the response has effective dimensionality **1.08**; of the two independent phase-drives
  only the recent one is decodable (p2 R2 = 0.57; p1 R2 = -0.09) -> **one** continuous dimension.
  Root cause: the write signal Psi = tanh(...) SATURATES, so the two components stay strongly correlated
  and the STORAGE is ~1-D in viable regimes; a second read-out channel makes order a distinct causal axis
  but cannot manufacture a second independent continuous dimension the storage does not hold.

## Gates
PASS: G1 storage, G2 backward-compat, G3 viability, G4 turnover, G5 dose, G6 order, G7 erasure, G8
transplant, G9 channel-specificity, G13 clone, G14 no-tag-leakage, G15 minimality.
FAIL: **G10 response-dimensionality, G11 two-history-dims, G12 individuation.** Prospective reproduced
the order-readout PASS (73x) and the one-dimensional response.

---

## VERDICT

`EXP-SC-MULTI-CHANNEL-ORGANIZATIONAL-MEMORY-00: PASS — ORDER-SENSITIVE MEMORY ONLY`

- `STORAGE INFORMATION:` order reproducibly stored (m-, 100% held-out); net exposure stored (m+); continuous magnitude / spatial history NOT reproducibly stored (Psi saturates).
- `DOSE READOUT:` retained via m+ -> uptake (dose_readout > clone).
- `ORDER READOUT:` YES, and channel-specific -> attractant axis; 70x (dev) / 73x (prospective) contrast vs the m- ablation; absent on the uptake axis. This is the advance over IOM-00.
- `RESPONSE DIMENSIONALITY:` ~1 (effective dim 1.08 held-out); one continuous history dimension recoverable.
- `ERASURE:` YES — ablating both channels removes the response entirely (~0).
- `TRANSPLANT:` YES — the read-out is transplant-based (memory into a common body reproduces the signature).
- `CHANNEL ABLATION:` correct — lam_minus=0 removes ONLY the attractant-axis order effect; lam_plus retains the uptake/dose effect.
- `MATERIAL TURNOVER:` order signature survives (M~0.12) but attenuated (~17% retained).
- `INDIVIDUATION:` FAIL — response ~1-D; within/between-history AUC 0.75 is carried by the single decodable dimension, not high-cardinality individuation.
- `NEXT-PROJECT DECISION:` order-sensitive only -> do NOT add persistence. Because the STORAGE (not just read-out) is ~1-D from Psi saturation, the next step is to revise the WRITING to store independent continuous magnitudes without saturation (or add recurrent internal plasticity), then re-expand functional channels. No further mechanism added here.
- `QUANTUM HARDWARE: NOT USED` — a classical channel-capacity / storage-saturation bottleneck; a QPU cannot add a stored dimension the substrate does not hold (see EXP_SC_MCM_00_QUANTUM_RELEVANCE.md).

`HMC PROSPECTIVE SPLIT remains SEALED.`
`SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED.`
`EXP-SC-01 remains BLOCKED.`

No subsequent experiment launched automatically. No writing parameter was retuned; only readout couplings added.
