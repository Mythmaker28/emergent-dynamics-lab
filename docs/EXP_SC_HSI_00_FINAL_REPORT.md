# EXP-SC-HIDDEN-STATE-CAUSAL-INDIVIDUATION-00 — FINAL REPORT
## Hidden-State Individuation and Causal Accessibility in the Frozen Droplet Substrate

**Branch:** `exp/sc-hidden-state-causal-individuation-00`  **Starting commit:** `25c419a` (HMC final)
**Substrate:** frozen scaffold engine (blob `7c91b91`, unchanged), β = 0.10, D_int = 0.008.
**Erratum issued** to the prior experiment (see `EXP_SC_HMC_00_ERRATUM.md`): its `SNAPSHOT SUFFICIENT`
label was unsupported (all regressions lost to baseline); corrected to `NO HISTORY-SPECIFIC CAUSAL
PERSISTENCE` + `PREDICTIVE COMPARISON: INDETERMINATE`.

## Mission
Determine — before any new physics — whether the frozen substrate contains a hidden state that is
(1) persistent, (2) individual-specific, (3) causally consequential, (4) accessible via bounded N/c
handles. Primary evidence: matched counterfactual pairs + direct causal divergence, NOT regressions.

## Method (frozen, preregistered)
A library of **100 development + 32 prospective** independent trajectories, 4 checkpoint ages each,
storing accessible snapshot X (geometry + external fields + uptake), privileged hidden h (U/V phenotype
+ mean σ), attractor coordinates, and compact canonical full states. Attractor classes were fit by
k-means (k=4) on development. Matched aliasing pairs (snapshot-close, hidden-far) were frozen on
development, with controls: exact clone (independent noise), σ-scramble (spatial U/V permuted, mean σ
preserved), σ-flip (U↔V swap → opposite attractor, rho/c/N held), same/different-attractor. A bounded
N/c probe grid was searched on development and the most informative probe (**N+0.5×15**) frozen.

## Findings (each question answered separately)

**Q1 — Hidden-state existence: YES.** 63–71 % of the hidden-state variance is not linearly explained by
the accessible snapshot (spatial components het/interface/radial/janus have R² 0.13–0.26 on X; mean σ
0.59). A hidden internal organization exists beyond the snapshot.

**Q2/Q3 — Individual specificity & temporal persistence: NO.** Within-trajectory hidden drift (2.82)
**exceeds** same-attractor between-trajectory spread (2.14); individuation AUC = **0.40 (dev) / 0.30
(prospective)** — below chance. The hidden state is organized into ~4 generic **attractor classes**
(sizes 32/12/46/10), not individual identities. Attractor persistence is short: only 23 % of
trajectories remain in a single class over 900 steps (consecutive-checkpoint stability 0.58).

**Q4 — Causal consequence: YES, but only as attractor class.** Flipping the attractor class (σ-flip,
snapshot held) drives accessible-future divergence to **1.8× (dev) / 2.6× (prosp) the clone ceiling with
no probe, and 4.46× / 4.49× under the nutrient probe** (exceeds the ceiling in 97 %/100 % of states).
Scrambling the finer spatial organization while preserving mean σ is **inert** (0.06× / 0.04× the
ceiling; exceeds it in ~4 % of states). The genuinely-hidden fine organization is epiphenomenal; the
causal power lives entirely in the coarse attractor class.

**Q5 — Accessibility: YES for the attractor class.** The bounded nutrient probe N+0.5×15 exposes the
attractor difference at 5.67× the clone ceiling (100 % non-destructive); nutrient deprivation is least
informative (0.68×), consistent with uptake ∝ N·(1+βσ). The finer hidden organization remains
inaccessible (scramble inert under every probe).

**Markov / snapshot sufficiency.** Among snapshot-matched pairs, hidden distance does not predict future
divergence beyond snapshot distance (partial correlation −0.09). Because the one causally-relevant latent
(attractor class / mean σ) is itself accessible via uptake, and the residual hidden organization is
causally inert, the **accessible snapshot is approximately Markov-sufficient for future accessible
behaviour** — established positively (via the controlled scramble), not from underpowered models.

**Temporal-order value: weak/continuity-only.** Consecutive-in-time hidden states are only modestly
closer than non-consecutive (ratio 0.78); with individuation absent, temporal order carries continuity,
not individuating memory. (Gate G9 is not required — no history claim is made.)

## Gates
Development gates (assay validity + result discrimination): G1 matching ✔ · G2 hidden diversity ✔ ·
G3 clone ceiling ✔ · G4 non-destructive probes ✔ · G5 attractor diagnosis ✔ · **G6 individuation ✘
(the substantive negative)** · G7 causal consequence ✔ · G8 intervention accessibility ✔ · G9 temporal
order — n/a · G10 no tracker leakage ✔ · G11 non-vacuity ✔ · G12 truth independence ✔.
Prospective family independently reproduced both the causal-consequence PASS (flip 4.49× ceiling) and the
individuation failure (AUC 0.30).

---

## VERDICT

`EXP-SC-HIDDEN-STATE-CAUSAL-INDIVIDUATION-00: PASS — GENERIC CAUSAL ATTRACTOR MEMORY`

- `HIDDEN-STATE EXISTENCE:` YES — 63–71 % of hidden variance lies beyond the accessible snapshot (spatial U/V organization).
- `INDIVIDUATION:` NO — within-trajectory drift exceeds same-attractor spread; AUC 0.40 dev / 0.30 prospective; ~4 generic attractor classes; short persistence (23 % single-class over 900 steps).
- `CAUSAL CONSEQUENCE:` YES as attractor class only — σ-flip 1.8–2.6× (no probe) / 4.5× (probe) the clone ceiling; σ-scramble inert (0.04–0.06×). The fine hidden organization is epiphenomenal.
- `INTERVENTION ACCESSIBILITY:` YES for the attractor class — bounded nutrient probe N+0.5×15 exposes it at 5.67× the clone ceiling, 100 % non-destructive; the fine organization stays inaccessible.
- `SNAPSHOT SUFFICIENCY:` approximately Markov-sufficient for accessible futures — the causal latent (attractor class) is accessible via uptake; the hidden residual is causally inert (partial corr h;future|x = −0.09).
- `TEMPORAL-ORDER VALUE:` weak, continuity-level only (ratio 0.78); no individuating temporal memory.
- `NEXT-PHYSICS DECISION:` **B** — the existing physics contains only GENERIC ATTRACTOR memory; a new mechanism for individual-specific memory must be designed (no mechanism added in this mission).
- `QUANTUM HARDWARE: NOT USED` — bounded relevance audit only; the classical model fully captures the generic-attractor discrimination, so no quantum-distinguishable task arises (see EXP_SC_HSI_00_QUANTUM_RELEVANCE.md).

`HMC PROSPECTIVE SPLIT remains SEALED.`
`SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED.`
`EXP-SC-01 remains BLOCKED.`

No further experiment launched automatically. No physics modified.
