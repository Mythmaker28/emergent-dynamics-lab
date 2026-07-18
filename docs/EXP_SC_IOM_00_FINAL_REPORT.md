# EXP-SC-INDIVIDUAL-ORGANIZATIONAL-MEMORY-00 — FINAL REPORT
## Experience-Written Distributed Organizational Memory

**Branch:** `exp/sc-individual-organizational-memory-00`  **Starting commit:** `709f963` (HSI final)
**First mission authorized to modify substrate physics.** Only a bounded memory extension was added; the
base scaffold physics is otherwise the frozen engine `7c91b91` and is recovered bit-identically when the
memory is uncoupled.

## Mechanism (minimal extension)
A distributed organizational-memory field m = (m1, m2) rides rho like U,V (extensive Mf = rho*m):

    d_t(rho m_k) = D_m lap(rho m_k) + eta_w rho Psi - eta_d[k] rho m_k + eta_t rho (T(m_k) - m_k)
    Psi = tanh(k_exp (N - c) + k_up (uptake - <uptake>))         (local experience signal)
    T(m) = 4-neighbour mean (local organizational templating / self-maintenance)
    growth: new material inherits local m (Mf += g*m)            (impression onto new material)
    coupling: uptake_eff = uptake * (1 + lam_m tanh(m1 + m2))    (function; ==uptake when lam_m=0)

m1 forgets fast (eta_d1=0.03), m2 slow (eta_d2=0.003), giving a two-timescale store. Every entity starts
m=0; memories arise only from experienced history. No IDs / seeds / cohort labels enter the physics.

## What passed (memory is real, causal, robust — dev AND held-out prospective)
- **Backward compatibility (G3):** with lam_m=0 the base fields evolve bit-identically to the frozen
  engine (max deviation 0.0); with eta_w=lam_m=0 memory stays exactly 0.
- **Viability + turnover (G1,G2):** the entity remains localized; pulse-chase material overlap falls to
  M~0.15 (< 0.35) with memory active.
- **History writing (G4):** different histories write different memory states.
- **Causal readout (G6):** erasing memory on an identical body changes the frozen-probe response by
  **49.9x (dev) / 50.6x (prospective) the exact-clone stochastic ceiling.**
- **Erasure / minimality (G7,G14):** with the memory channel uncoupled (lam_m=0) the effect is **exactly
  0** — the response difference is entirely the memory, nothing else.
- **Transplant (G8):** transplanting one entity's memory into another's body shifts its response by
  **5.6x / 5.5x the clone ceiling.**
- **Turnover continuity (G9):** after ~85% material replacement (M~0.15) the memory's causal effect
  persists; the memory rode the organization (new material inherited it), not the old material.
- **Non-categorical storage (G10):** the memory field occupies an effective ~11 dimensions — far beyond
  the 4 generic attractor classes of the frozen substrate.

## What failed — and why it is the key scientific finding
- **Temporal-order read-out (G5): FAIL.** Order IS written into memory (m1-vs-m2 separation ~0.46, ~4.7x
  clone) but is NOT causally expressed (order->response 0.022, below the clone ceiling), because the single
  scalar coupling tanh(m1+m2) is blind to the m1-m2 contrast that encodes order.
- **Individual specificity (G11): FAIL.** The causal read-out is essentially **one-dimensional**: the
  future response decodes the NET experienced dose almost perfectly (LOO R2 = 0.95 dev / 0.97 prospective)
  but recovers the full 4-dimensional history only weakly (R2 = 0.24 / 0.55), and same-history memory is
  barely more similar than different-history memory across bodies (memory-field individuation AUC 0.57).

The bottleneck is structural: the field **writes** high-cardinality history (eff. dim ~11) but the single
scalar functional coupling **reads out** only ~1 dimension (net experience level). The memory is therefore
a graded, continuous, causally-active *experience-level* memory — richer than discrete classes, but it
does not individuate trajectories.

## Gates
Pass: G1,G2,G3,G4,G6,G7,G8,G9,G10,G12,G13,G14. Fail: **G5 (order read-out), G11 (individuation).**
No tag leakage (G12): memory starts at 0 and is written only by experience. Truth/construction and
scoring are in separate modules. Prospective family (31000-31031) reproduced every passing gate.

---

## VERDICT

`EXP-SC-INDIVIDUAL-ORGANIZATIONAL-MEMORY-00: PASS — HISTORY-CLASS MEMORY ONLY`

- `HISTORY WRITING:` YES — different experiences write different, bounded, distributed memory that is
  inherited by newly grown material and survives material turnover.
- `TEMPORAL ORDER:` WRITTEN but NOT READ — order lives in the m1-m2 contrast (~4.7x clone) yet is
  causally silent under the scalar coupling (order->response ~ clone ceiling).
- `CAUSAL READOUT:` YES and strong — erase changes the probe response 50x the clone ceiling, exactly 0
  when the channel is uncoupled (dev + prospective).
- `ERASURE:` YES — removing/uncoupling memory removes the history-specific response entirely.
- `TRANSPLANT:` YES — transplanting memory transfers the response tendency (~5.5x clone).
- `MATERIAL TURNOVER:` PASS — effect persists after ~85% replacement (M~0.15); carried by organization,
  not old material.
- `INDIVIDUATION:` NO — the causal read-out is ~1-D (net dose R2~0.95; full history R2 0.24-0.55; memory
  individuation AUC 0.57). Not high-cardinality; does not individuate trajectories.
- `MEMORY DIMENSIONALITY:` storage ~11 effective dimensions; causal read-out ~1 dimension (scalar-coupling
  bottleneck).
- `NEXT-PROJECT DECISION:` history-class memory only — DO NOT call it identity. A higher-dimensional /
  multi-coupled memory is scientifically justified: couple several memory components to several distinct
  functions (or make the coupling read the m1-m2 contrast) so the demonstrably high-cardinality WRITING is
  matched by high-cardinality READ-OUT. Do not merely add persistence. No mechanism was added here.
- `QUANTUM HARDWARE: NOT USED` — bounded relevance audit only (see EXP_SC_IOM_00_QUANTUM_RELEVANCE.md);
  the mechanism and its ~1-D read-out are fully classical, so no quantum-distinguishable task arises.

`HMC PROSPECTIVE SPLIT remains SEALED.`
`SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED.`
`EXP-SC-01 remains BLOCKED.`

No subsequent experiment launched automatically.
