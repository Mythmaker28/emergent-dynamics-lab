# EXP-SC-HISTORY-MATERIAL-CONTINUITY-00 — FINAL REPORT
## History versus Material Continuity in the Frozen Droplet Substrate

**Stage:** DEVELOPMENT complete. Prospective hold-out **PRESERVED (not burned)** — development gate G10 was not met.
**Branch:** `exp/sc-history-material-continuity-00`  **Starting commit:** `e17f431`
**Substrate:** frozen scaffold engine (`edlab/substrates/scaffold/engine.py`, blob `7c91b91`), β = 0.10 (EXP-SC-00B selection, not retuned), D_int = 0.008. Physics untouched.

---

## 1. The question

Can a mesoscopic organization retain a **causally meaningful continuity through material turnover**, and does its continuous **history** predict its future better than present **material composition** or instantaneous **phenotype**?

This is a *privileged existence assay*: it reads simulation-internal state (U, V, cohorts) for diagnosis. It is **not** a transferable observer. It asks only whether the phenomenon exists in this substrate.

## 2. What the substrate can do (Phase 0 — PASS: `SUBSTRATE_OK`)

A localized mesoscopic entity self-organizes and is stable across the whole window. Material genuinely turns over: a **passive pulse-chase** (cohort bin 0 = material present at t0; the cohort field never touches the physics — verified **bit-identical** rho/U/V, max deviation **0.0**) shows the labelled fraction fall
`M(t0,t): 0.73 → 0.49 → 0.34 → 0.28` (old material leaving 9.9→3.0, new entering 3.7→7.6), partition-robust across detector thresholds. External handles N and c perturb the entity without destroying it. Entities coexist at ~7% occupancy. The interior is structured (U/V) and functionally coupled (β·σ modulates uptake). Every capability question passed.

## 3. Material continuity (the axis M)

Across 12 development trajectories, at the checkpoint t_c: **M_early mean 0.56 → M_tc mean 0.265** (range 0.228–0.326), **12/12 below the preregistered low-material band M_low = 0.35**. Material replacement is substantial and real. **G2 PASS.**

## 4. Organizational axes — reported SEPARATELY (no composite scalar)

Continuity is the distance between an arm's t_c axis vector and the entity's OWN earlier axis vector. "H closer than a control" is a per-seed paired test (n=12).

| Axis | H vs P (phenotype reset) | H vs M (material scramble) | H vs U (unrelated) | reading |
|------|--------------------------|----------------------------|--------------------|---------|
| P1 geometry | 0.00 (tie) | 0.00 (tie) | 0.08 | shared by construction; cannot test history |
| **P2 internal U/V** | **1.00** | **1.00** | **0.50** | persists vs *destruction*, but **at chance vs an unrelated entity** |
| P3 function (uptake) | 0.58 | 0.67 | 0.50 | near chance |
| P4/R causal response | 0.50 | 0.58 | 0.58 | near chance |
| P5 recovery / P6 path | H-only diagnostics (reported in DEV_RESULTS) | | | |

**Individuation (within-history vs between-entity):** P2 AUC = 0.65 (weak; within 2.71 vs between 3.36), causal response AUC = 0.52 (**none**). The one axis that "persists" (P2) does so only because an *evolved* interior differs from a *random reset* — it is **not history-individuating**: the entity resembles its own past no more than it resembles an unrelated entity's past. This reproduces the earlier EXP-SC-00B / R8-B finding ("identity exists; it does not persist") with sharper instruments.

**Axes remaining history-specifically within regime: 0 of 6 (required ≥ 3).**

## 5. History versus material versus snapshot — predictive comparison

Simple, auditable leave-one-out k-NN models predict the future causal-response profile from information available earlier (NRMSE, baseline = predict-the-mean = 1.000):

| Model | Inputs | LOO NRMSE |
|-------|--------|-----------|
| A material | cohort overlap M, mass | 1.074 |
| B snapshot phenotype | geometry + function + visible fields | 1.148 |
| C history | snapshot + past response profile + path | 1.069 |
| D full state | C + internal U/V | 1.169 |

**No model beats the mean baseline.** History (C) does not exceed snapshot (B) or material (A) in any better-than-baseline sense. The future causal response is not predictable from the entity's history beyond what the instantaneous phenotype already carries.

## 6. Counterfactual controls (K1–K10) and the exact-clone ceiling

Tracer passivity **K1 PASS** (bit-identical). Tracker-free segmentation **K2 PASS**. Full-state clones reproduce future dynamics within a stochastic ceiling **below H's own drift in 12/12** (**K4/G5 PASS**). The material-only trap **K5** fires as expected: arm M (material intact, organization scrambled) reproduces H's response (d_M ≈ d_H) — material overlap is therefore **not** counted as continuity. The shape-only trap **K6** likewise. Unrelated entities **K8** are kept separate and are indistinguishable from H relative to its past. Temporal shuffling **K7** is vacuous (no history signal to destroy). Partition alternatives **K9 PASS**. Intervention-null **K10 PASS**.

## 7. Development gates

**11 / 12 pass.** The single failure is decisive:

- G1 entity ✔ · G2 turnover ✔ · G3 tracer passivity ✔ · G4 responsiveness ✔ · G5 clone validity ✔ · G6 phenotype-reset validity ✔ · G7 material-reset validity ✔ · G8 axis independence ✔ · G9 partition robustness ✔ · **G10 history signal ✘** · G11 non-vacuity ✔ · G12 truth independence ✔.

Per protocol, **all development gates must pass before the prospective split may be executed.** G10 failed, so the prospective hold-out was **not run and is preserved**.

## 8. Interpretation and claim scope

In this frozen substrate, a continuously evolving organization **does not** retain a *history-specific* causal signature through substantial material replacement, and its history **does not** predict its future causal behaviour better than its instantaneous phenotype. Whatever persists (a low-diversity evolved interior) is readable from the snapshot; the full history is redundant for prediction. This does not establish identity, consciousness, life, individuality, or anything about physical droplets. The indicated (out-of-scope) next step, already declared in `PROJECT_STATE.md`, is a substrate whose internal organization is **PINNED** rather than merely multistable — which requires new physics and a new protocol, and is explicitly **not** attempted here.

---

## VERDICT

`EXP-SC-HISTORY-MATERIAL-CONTINUITY-00: FAIL — SNAPSHOT SUFFICIENT`

- `MATERIAL CONTINUITY AXIS:` real, passive, partition-robust; M_tc mean 0.265 (12/12 below M_low = 0.35). Substantial replacement confirmed.
- `ORGANIZATIONAL AXES:` P1 geometry — shared by construction (untestable for history); P2 internal U/V — persists vs reset (1.00/1.00) but NOT history-individuating (vs unrelated 0.50; AUC 0.65); P3 function — chance; P4 causal response — chance (AUC 0.52); P5 recovery / P6 path — H-only, no discrimination. **0 of 6 axes remain history-specifically within regime (≥3 required).**
- `HISTORY PREDICTIVE VALUE:` none beyond snapshot (LOO NRMSE C = 1.069; no model beats the 1.000 mean baseline).
- `SNAPSHOT PREDICTIVE VALUE:` no advantage of history over snapshot; instantaneous phenotype is as informative as the full history — hence *snapshot sufficient*.
- `FULL-STATE CLONE CONTROL:` valid; stochastic ceiling below H drift in 12/12 (reproducibility established).
- `PHENOTYPE-RESET CONTROL:` valid (geometry preserved, internal history erased).
- `MATERIAL-RESET CONTROL:` valid (material preserved exactly, organization scrambled) — reproduces H's response, confirming the material-only trap.
- `QUANTUM HARDWARE: NOT USED` (bounded relevance audit only — see EXP_SC_HMC_00_QUANTUM_RELEVANCE.md; no precise quantum-distinguishable task was produced by the classical study).

`SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED.`
`EXP-SC-01 remains BLOCKED.`

Prospective hold-out PRESERVED. No metrology experiment launched. No split/merge follow-up (primary did not pass).

**Alternative reading (documented for honesty):** the predictive-model comparison is underpowered (n=12; all models ≈ baseline), which on its own would support `INDETERMINATE` for the *predictive* dimension. The verdict `SNAPSHOT SUFFICIENT` is driven by the well-powered per-axis and individuation analyses, which show no history-specific organizational persistence on any axis.
