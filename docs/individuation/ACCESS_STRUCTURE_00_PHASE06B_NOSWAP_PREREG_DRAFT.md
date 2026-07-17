# ACCESS-STRUCTURE-00 — Phase 0.6B no-transplant prospective decision tree (DRAFT)

**DRAFT v0.6B — REVISE-READY — NOT SEALED — NOT AUTHORISED — DO NOT EXECUTE PROSPECTIVELY**

A design-review artifact only. It records the prospective logic implied by the no-transplant interface-clamp design
(`ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_DESIGN.md`) after DEV feasibility. Fields marked `BLOCKED` must be frozen and
human-reviewed before any seal. **No seed family is chosen here and none may be chosen from any confirmation
outcome.** 03G and V5 are fixed prior evidence.

## Question and fixed prior

Given certified 03G Outcome B, determine whether the turnover-surviving causal feeding state is accessible from the
tracked target’s local/core memory, whether the sufficient unit is the body core or an extended comoving object,
whether a global channel is essential, and whether the effect is a residual direct readout — **without transplanting
any spatial state**. Environmental sufficiency is addressed only to the partial extent a no-transplant design allows
(see the design, §8).

## Nomenclature

`C` = local/core microstate on the frozen periodic disk `d ≤ r_unit`; body held fixed, only `Mf` varied.
Barrier = the two-cell clamp ring `r_unit < d ≤ r_unit+2` (bit-exact isolator). `E` = complement. `G` = global
`up_ref`. `D` = Markov phase (arrays + `step`; no hidden buffers/RNG). The historical decoder letters are `L/E/G`
scopes and are secondary only.

## Unit, eligibility, validity

- **Statistical unit: the original world.** Technical target and (if used) crossed branches are averaged within
  world before inference.
- **Outcome-independent eligibility.** Targets are the frozen geometry-selected `K=3` (`pick`: size ≥ 45, pairwise ≥
  24). Enclosed radii `{r_tight, r_unit}` are fixed from the perturbation-halo measurement (DEV: decay radius ≈ 4,
  core radius 10), never from feeding. Every opened world, including ineligible/invalid ones, appears in raw output;
  reserve activation may use eligibility variables only.
- **World validity (G0).** A world is invalid if any primary or control branch has fewer than three distinct tracks,
  any `MERGE/SPLIT/LOST/AMBIGUOUS`, coverage ≥ 0.15, non-finite state, an absent uptake endpoint, a failed clamp/
  standardization gate, or a failed manipulation-validity check. World-level censorship (never keep only survivors).
- **Minimum valid worlds: ≥ 18** (a hard floor, not a power justification). `BLOCKED`: design-based power calculation
  and prospective family size after margins are frozen.

## Fixed probe and horizon

Candidate common probe = the CONFIRM-02 frozen probe: standardize `N := N0`, settle 40 steps, uniform additive
stimulus `0.25 × 5` (cumulative `1.25·N0`), horizon 40, integrated uptake on the bijectively tracked target
(`θ = 0.10`); fixed-initial-mask integrated uptake is the tracker-independent convergent control. The probe adds the
same forcing to every branch and does **not** reset or homogenise the collar/environment under test. `BLOCKED`: freeze
the probe, the surgery-to-probe interval, and the horizon jointly with the margins; the probe is a candidate until the
clamp is re-qualified under the sealed configuration.

## Primary arms and contrasts

Four in-place arms (no transplant), each isolated by the two-cell reference clamp where marked:

| Arm | Core memory | Barrier | 
|---|---|---|
| `OWN·COUPLED` | own | coupled (no clamp) |
| `OWN·CLAMPED` | own | clamped to no-history reference |
| `STD·COUPLED` | standardized in place | coupled |
| `STD·CLAMPED` | standardized in place | clamped |

- **Primary causal contrast** `τ_C = Y(OWN·CLAMPED) − Y(STD·CLAMPED)` (core memory sufficiency under a shared
  standardized boundary).
- Secondary contrasts `τ_E = Y(STD·COUPLED) − Y(STD·CLAMPED)`, `τ_joint`, interaction `τ_S`.
- **Halo cut**: `τ_C` at `r_tight` vs `r_unit` (H_HALO).

`BLOCKED`: freeze the practical sufficiency margin, the equivalence margin, the simultaneous-interval/multiplicity
method, and power — all from design/manipulation noise, never from confirmation outcomes.

## Sham and manipulation-validity gate (all run before any active feeding is exposed)

1. **Clamp-disabled identity**: `NoSwapClampEngine(driver=None)` equals the frozen engine bit-for-bit.
2. **Own-replay sham**: clamping the barrier to the world’s own recorded trajectory reproduces the free continuation
   at `|error| ≤ 1e-12 + 1e-10·|reference|` (DEV: exactly 0). Its future-feeding bias must lie inside a frozen
   equivalence margin.
3. **Exact isolation**: an environment perturbation outside the barrier leaves the core bit-identical under the
   two-cell clamp with `up_ref=0` (DEV: 0.0 on 12/12 targets).
4. **Standardization locality**: `standardize_core_memory` changes only `Mf` on the core; non-target change 0.0.
5. **Reference outcome-independence**: the no-history reference trajectory depends only on the reference world and
   geometry, not on the recipient’s history (so the clamp cannot inject the recipient’s own history).
6. **Temporal-discontinuity bound**: the barrier jump under the standardized clamp must lie under a separately frozen
   absolute bound, and the matched-sham jump must be equivalent to zero (DEV own-replay jump = 0).
7. **Partition fidelity**: only the declared core (memory) and the declared barrier change; scheduler `step`, engine
   parameters, tracker-independent geometry, and diagnostic invariants pass.
8. **Viability/tracker**: every primary and control branch keeps three distinct bijective tracks, no censor event,
   coverage < 0.15, valid tracked and fixed-mask readouts, finite arrays, and the full horizon.
9. **Global/readout controls**: identifying results repeat under dynamic `up_ref = 0`; `λ₊ = 0` removes only
   memory’s positive feeding modulation and never disables the uptake endpoint; the algebraic direct-coupling
   prediction is reported alongside.
10. **`D`/RNG**: identical scheduler step and engine context; no hidden buffer or RNG; no phase scramble.

Any failure yields `FEASIBILITY_FAIL / UNRESOLVED`, never a storage or absence claim.

## Controls for body, geometry, nutrient, global channel

- **Body/geometry**: the core factor varies only `Mf`; rho/U/V/geometry are identical within a counterfactual block.
- **Nutrient**: the standardized clamp supplies an on-manifold nutrient/flux boundary and local `F·(N0−N)`
  replenishment; the double-null shares the identical clamp so any residual nutrient effect cancels in `τ_C`.
- **Global channel**: repeat under `up_ref = 0`.
- **Direct readout**: `λ₊ = 0` and the algebraic prediction.
- **Environment-coupling confound** (for `τ_E` only): compare restored real-environment coupling against the
  standardized clamp; a positive `τ_E` is labelled “environmental access not excluded,” never “environmental storage.”

## Decision tree (each leaf states the hypothesis update)

Enter only if all manipulation-validity gates pass; otherwise `UNRESOLVED (feasibility)`.

1. **`τ_C` vs margin.**
   - `τ_C` not above margin (equivalence-supported null) → local/core memory sufficiency **not established**. Go to 5
     (environment/global). Update: H_C ↓; H_E/H_G/H_S remain open.
   - `τ_C` above margin → 2.
2. **`λ₊ = 0` and algebraic prediction.**
   - `τ_C` collapses under `λ₊ = 0` **and** is fully predicted by `⟨λ₊·m_plus/(1+λ₊·m_plus)⟩` → **H_0 (local direct
     readout)** supported: local access is a short-lived directly-coupled remnant, not individual memory. H_C ↑ (as
     *access*), H_0 ↑; no ownership/identity claim.
   - `τ_C` survives beyond the algebraic prediction → 3. Update: H_0 ↓ (not sufficient alone).
3. **`up_ref = 0`.**
   - `τ_C` collapses → **H_G** supported (global channel essential). H_G ↑, H_C ↓.
   - `τ_C` survives → 4. Update: H_G ↓ (DEV prior: `up_ref` barely moves `m_plus`).
4. **Halo cut (`r_tight` vs `r_unit`).**
   - Survives at `r_tight` → **H_C** supported, sufficient unit = body core. H_C ↑, H_HALO ↓.
   - Lost at `r_tight`, restored at `r_unit` → **H_HALO** supported, sufficient unit = extended comoving object.
     H_HALO ↑.
   - Both lost → `UNRESOLVED (radius)`; no scan permitted.
5. **`τ_E` with the environment-coupling control (partial).**
   - `τ_E` above margin and above the coupling control → **environmental access not excluded** (partial H_E). If both
     `τ_C` and `τ_E` hold → **H_R (redundant, partial)**. If separate arms are equivalence-null but `τ_S`/joint hold →
     **H_S (synergistic, partial)**, matched must exceed crossed without a clamp-artefact failure.
   - `τ_E` equivalence-null → environmental access **not established** (never “absent”).
6. **Phase probe (exploratory).**
   - Phase-mismatched replay abolishes `τ_C` while matched preserves it, beyond the boundary-disturbance envelope →
     **H_PHASE** flagged (interpret cautiously; Markov substrate). Otherwise H_PHASE ↓.
7. **`UNRESOLVED`** covers wide intervals, failed equivalence, failed controls, radius ambiguity, and any pattern not
   uniquely classified. “Not established” is never “absent.” No outcome establishes identity, individual memory,
   metaphysical ownership, life, or active reconstruction.

## Secondary analyses

Predeclared conditional decoding from frozen `L / C / E / G` scopes and a single named continuous PID estimator
(unique-local, unique-environment, redundancy, synergy), all fit inside held-out original-world folds; secondary and
model-dependent; cannot rescue a failed causal or feasibility gate.

## Outcome independence

No feature, decoder, PID estimator, hyperparameter, eligibility rule, enclosed radius, reference construction, probe,
margin, or clamp parameter may be selected using any confirmation outcome. The individual is fixed before any
confirmation data exist.

## Blocked freezes before any seal

`BLOCKED`: practical/equivalence margins; simultaneous-interval/multiplicity method; probe + interval + horizon
freeze under the sealed clamp; design-based power and prospective family size; semantic seed-family audit and
disposal of the broken `refs/heads/probe/tmp01` without deleting evidence. **No seed family is named in this draft.**

Current recommendation: **REVISE → GO-ready mechanics, pending the blocked freezes and human review.** No prospective
family, seal, push to a protected ref, merge, V5 change, or active reconstruction is authorised by this draft.
