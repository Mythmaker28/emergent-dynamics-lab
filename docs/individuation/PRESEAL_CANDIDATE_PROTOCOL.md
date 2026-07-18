# PRESEAL_CANDIDATE — LCI-CAUSAL-TURNOVER-PREREG-03

## ⚠ NOT AUTHORIZED FOR PROSPECTIVE RUN

*This is a CANDIDATE pre-registration. It is NOT a sealed PRESEAL. No confirmatory seed may be run and no
prospective family opened until Tommy authorizes it. The design branch commit carrying this file is a design
artifact, not a prospective seal. Branch `design/lci-causal-turnover-prereg-03` off `9c8a62c`.*

## 1. Question & hypotheses

**Question.** A droplet that received its own local history retains (1) that local information, (2) its own causal
capacity over its feeding, and (3) its distinction from neighbours, after deep renewal of its matter, while remaining
a distinct physical component?

**Ladder hypotheses (règle finale — each only interpreted if the prior holds):**
- **H0 feasibility** — three droplets can reach per-droplet `M_i ≤ 0.25` while staying alive, distinct, and
  non-fusing. *(DEV: ~50 % of eligible worlds; fission/loss attrition is real.)*
- **H1 rest replication** — storage + own-specific causal readout replicate at rest (as confirm-02).
- **H3 deep storage** — graded own-history is still decodable from renewed material, own beating neighbour AND global.
- **H4 deep causal** — do-erase of own memory still lowers own feeding, own-specific, at depth.
- **H6 individuation-through-turnover** — H0∧H1∧H3∧H4 with own separable from neighbour/sham AND global.

**Pre-declared expectation (honest).** DEV predicts H0 marginal (needs a large family), H4 likely PASS (coupled
readout — low bar), **H3 likely FAIL** (graded memory homogenizes locally). H6 is therefore *unlikely to be cleanly
established*; the probable result is "spatial-locality individuation survives, graded-content individuation does not."

## 2. Frozen engine (no physics change)

`MultiChannelMemoryEngine` / C1c (`eta_w=0.015, eta_d1=0.35, eta_d2=0.006, k_exp=1.0`, `lam_plus=0.25,
lam_minus=0.15`) on `IOMState`. Detection `SCDetectionSpec(threshold=0.30, min_cells=12)`. Ablation engine
`lam_plus=lam_minus=0`. Passive-decay-null engine `eta_w=0` (diagnostic only). up_ref-neutralized engine (diagnostic)
= `up_ref:=0` variant. The main-line engine is unmodified.

## 3. Protocol (per DEV/prospective world)

**A. Write local histories.** `WARM=800`; pick K=3 targets size ≥45, pairwise ≥24 (frozen, outcome-independent);
two-phase simultaneous local Gaussian nutrient histories (`AMP∈[0.005,0.035]`, `PHASE=60`); `SETTLE=120` →
rest snapshot `S0`. (Verbatim confirm-02 storage block; storage matrix `Cm`, features `feat`.)

**B. Rest snapshot + causal assay.** From `S0`, the frozen confirm-02 battery `nm.measure` (probe **uniform
0.25×5**, N-standardise, `HORIZON=40`, bijective primary + fixed-mask convergent readout) on branches
{intact, erase-target_j, erase-neighbour (= erase_j, i≠j), sham, ablation, erase-ablate_j}. World-level G0
censorship (any MERGE/SPLIT/LOST/AMBIGUOUS, or coverage ≥0.15, or <3 distinct, in any contrast branch → world
invalid). The assay runs on **branches**; the main world continues unperturbed.

**C. Turnover.** From the unperturbed `S0` with per-target passive material tracers (`MATERIAL_TRACER_SPEC.md`):
no new local history, no behavioural probe, **C1c unchanged, memory writing LEFT ACTIVE under a strictly neutral
(no-drive) environment** — justified below. Bijective tracker every step; record `M_i, P_i, G` every 10 steps with
explicit MERGE/SPLIT/LOST/AMBIGUOUS censorship.

> **Writing-during-turnover decision (frozen, Phase 4C).** Chosen: **left active, C1c unchanged, neutral
> environment.** Justification: (i) freezing `eta_w` would *change* C1c and make the test unrepresentative of the
> actual architecture; (ii) "neutral" = no external drive/probe, so no new *spatially-structured* common information
> is injected; (iii) the only common term is the pre-existing `up_ref`, shown negligible in-regime (ratio 6e-4,
> `GLOBAL_CHANNEL_AUDIT.md`); (iv) any homogenization by ongoing neutral writing is a *real property* of the
> architecture and must be measured, not engineered away. A separate `eta_w=0` passive-decay null decomposes
> copy-survival vs re-writing. This choice does **not** introduce new common information able to overwrite the local
> histories (the injected environment is unstructured; the structured writing is each droplet's own local `N−c`).

**D. Deep snapshot.** First pre-declared step where **all three** are ALIVE + distinct + non-fusing (coverage <0.15)
+ each `M_i ≤ 0.25` + no invalidating tracker event. If not reached before `TURN_CAP=1500` → world =
FEASIBILITY INVALID (reason recorded). No "best instant" selection — the *first* qualifying step is taken.

**E. Deep causal assay.** From the deep snapshot (unperturbed), the SAME `nm.measure` battery, same probe/horizon/
gates/tracker, no parameter re-tuning. Compare REST and DEEP without selecting the better.

## 4. Gates (frozen; separate, no composite)

- **G0 feasibility** — ≥ **12** valid worlds AND ≥ pre-declared fraction of eligible; `TURN_CAP=1500`; seed cap **50**
  (frozen, no post-outcome extension); all seeds reported; no silent survivor-keeping.
- **G1 rest storage** — `DD_mem ≥ 10`, `|off| < 0.05`.
- **G2 rest readout** — paired worldboot lower-CI of own-dose decode > null95 AND own-dose R² > neighbour.
- **G3 deep storage (PRIMARY-at-risk)** — own-dose deep decode > within-world null AND > neighbour-dose AND >
  global-mean-history; world-CI; per-seed reported; **order reported separately, non-gating**. Do not reopen V4 h2.
- **G4 deep causal** — worldboot lower-CI(own) > 0, lower-CI(own−sham) > 0, lower-CI(own−neigh) > 0, ablation ≈ 0,
  tracked and fixed same sign, no fusion during assay.
- **G5 retention (two tiers, no invented 0.50)** — report REST, DEEP, ratio DEEP/REST, DEEP−REST, paired world-CI.
  *Causal survival* = deep own lower-CI > 0. *Strong retention* = ratio lower-CI above a **justified** threshold; if
  no mechanistic justification exists it stays secondary/descriptive (NOT auto-0.50).
- **G6 individuation-through-turnover** — PASS only if G0 ∧ G1 ∧ G3 ∧ G4, own distinct from neighbour/sham, AND the
  global channel cannot explain the effect. (Note: G4 alone — the coupled interventional readout — does **not**
  suffice; G3 is required.)

## 5. Nulls & controls (prospective)

Passive-decay null (`eta_w=0`); up_ref-neutralized diagnostic (`up_ref:=0`; and `k_up=0` upper bound); permuted
between-droplet histories; global-common history; own vs neighbour vs global-mean-history decoders; ablation collapse;
fixed-mask convergent; baseline size/mass/position decoders (must FAIL where memory succeeds); inter-droplet memory
homogenization trajectory.

## 6. Power, seeds, exclusions, environment

- **Power** (`TURNOVER_POWER.md`): interventional gates over-powered at ≥6 valid; G0 needs ~44–49 seeds for ≥12
  valid; **G3 needs ≥18 valid AND a real effect (at risk).**
- **Proposed family: `54001–54050`** (50 seeds, cap 50, frozen). **Verified absent from the whole registry** (18
  branches; `TURNOVER_SEED_MANIFEST.md`). **NOT opened by this mission.**
- **Exclusions**: <3 well-separated targets (geometric, outcome-independent, pre-prospective); FEASIBILITY INVALID
  worlds counted against the floor, never silently dropped.
- **Environment**: py3.11.15 (DEV) / py3.10.12 (sealed lock), numpy 2.2.6, scipy 1.15.3, matplotlib 3.10.9.
  Determinism byte-identical on the fixed platform.

## 7. Candidate hashes, commands, cost

- Candidate content hashes (runner/analyze/tracer/tests) recorded in `PRESEAL_CANDIDATE.json` at commit time.
- Reproduction commands: `TURNOVER_REPRODUCTION.md`.
- **Cost estimate**: ~35 s (infeasible/early-censor) to ~70 s (feasible, with deep assay + null) per seed; a 50-seed
  family ≈ **35–50 min** single-core on the pinned venv. DEV pilots (this mission) already spent ~15 min.

## 8. What this candidate does NOT do

Opens no prospective family; runs no confirmatory seed; touches no sealed artifact (`main f3921a4`, V4 `23b53ae`,
release, C1c, probe 0.25×5, bijective tracker, historical PRESEAL/RESULTS all intact); makes no identity/life/agency
claim; does not pursue ACTIVE-RECONSTRUCTION.
