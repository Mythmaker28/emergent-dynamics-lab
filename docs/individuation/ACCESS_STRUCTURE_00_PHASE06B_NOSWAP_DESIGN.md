# ACCESS-STRUCTURE-00 — Phase 0.6B no-transplant causal-access design

Status: **PHASE 0.6B COMPLETE — GO (mechanics) with a declared PARTIAL scientific scope — NOT SEALED — NO
PROSPECTIVE SEED — HUMAN REVIEW REQUIRED**

Branch `claude/access-structure-noswap-design-06`, based exactly on the Phase 0.5 parent
`fa261734300631f16ca5e0bacceba11d5f7ddc1e` (“Qualify ACCESS-STRUCTURE Phase 0.5 operators”). This document is the
independent no-transplant counterpart to the Phase 0.6A transplant repair (Codex). It does not reopen 03G, modify
V5, edit the transplant operator, or authorise active reconstruction. It evaluates whether the ACCESS-STRUCTURE
hypotheses can be distinguished **without grafting a foreign spatial state into a foreign environment**, keeping the
endpoint at future feeding under a standardized probe.

All quantitative claims below are DEV-only, on the already-open worlds 50001–50010 (deep-feasible: 50002, 50004,
50005, 50007). No seed outside that namespace was executed, no prospective family was chosen, and no
history-A-versus-history-B feeding contrast was computed.

## 1. Independent scientific judgment

Phase 0.5 showed that exact state exchange is mechanically executable but causally uninterpretable in its current
form: crossed-core surgery produces boundary seams up to 22.872× the recipient’s natural boundary jump, the one-cell
halo reacts after a single update, and the disturbance reaches the far environment by step 40. The Phase-0 factorial
(`C_A H_0 E_0`, `C_0 H_A E_A`, matched, crossed) requires an environment reset, a standardized-body operator, and a
matched/cross graft — all transplants, all seam-producing.

The key enabling fact for a no-transplant route is structural, not incidental. In the frozen
`MultiChannelMemoryEngine` **every spatial coupling is nearest-neighbour** (`np.roll ±1`, the four-neighbour
Laplacian `lap`, the donor-cell `_face_flux`, and the four-neighbour template `_tmean`); the **only** non-local term
is the world-global scalar `up_ref = mean(uptake over alive cells)`. Nutrient `N` is replenished locally everywhere
by `F·(N0−N)` (`F=0.024`, `N0=1`) and diffuses with `D_N=0.5`. Consequently a region can be severed from its
environment **exactly and in place** by overwriting a thin collar with an outcome-independent boundary signal after
each step: information from the environment reaches the collar during a step but is discarded before it can cross
into the core, while the core continues under the true engine and does not starve. There is no foreign core, no
translated body, and therefore no spatial seam of the Phase-0.5 kind — the core is never touched at the instant of
intervention.

This does not make every hypothesis cleanly separable without transplant (Section 8), but it makes the central
sufficiency question — does the local/core state, cut from its specific environment, still express its history in
future feeding? — answerable with a bit-exact, low-disturbance, sham-controlled operator.

## 2. State map and compartments (inherited from Phase 0.5, verified independently)

Persistent state is `rho, U, V, c, N, C, uptake, Mf` plus the scheduler `step`; the physics is Markov at this
snapshot under the frozen engine, with **no** hidden velocity/momentum, previous-state, flux/gradient, or RNG buffer
(re-verified against `sc_mcm/engine.py`). Readout couplings: `m_plus = tanh(m1+m2)` multiplies uptake
(`g ∝ (1+λ₊·m_plus)`, `λ₊=0.25`); `m_minus = tanh(m1−m2)` modulates attractant production (`λ₋=0.15`).

Operational partition around a tracked target centre (Phase 0.5 DEV geometry, unchanged):

| Symbol | Meaning | This design |
|---|---|---|
| `C` (core) | complete local microstate on a periodic disk `d ≤ 10` (contains every DEV body; worst radius 8.93) | enclosed **scientific unit** whose sufficiency is tested |
| barrier | ring `10 < d ≤ 12` | **engineering clamp barrier** (2 cells; see §6) |
| `E` (environment) | complement | severed / standardized by the clamp |
| `G` | world-global `up_ref` | tested by the existing `up_ref=0` ablation |
| `D` | Markov phase = arrays + `step` (no hidden buffers) | preserved; parity untouched |

## 3. Task 1 — three non-surgical trajectories, evaluated

**A. Causal coupling cut (isolation).** Preserve the physical state; modify the future coupling across a `C/H` or
`H/E` boundary. Because coupling is nearest-neighbour, a cut is exact. A *hard no-flux (Neumann) cut* is
implementable but reflects material at the boundary (attractant/ nutrient accumulation), which is a genuine
reflection artefact. A *standardized-boundary cut* — hold the collar at an outcome-independent reference each step —
avoids reflection, supplies a plausible nutrient/flux boundary, and severs the environment’s history. Local nutrient
replenishment (`F·(N0−N)`) means the isolated core does **not** starve. Identifiability: tests core sufficiency; any
reflection/starvation effect is common to the arms that share the clamp and cancels in the sufficiency contrast.
This trajectory is the basis of the chosen design.

**B. Phase-preserving boundary replay.** Continue the core in place while replacing only its incoming boundary
forcing with a recorded/counterfactual boundary signal, with a common probe and common random numbers (there is no
persistent RNG, so “CRN” reduces to identical scheduler alignment). Matched (own), standardized (no-history), and
crossed (foreign) sources are all definable by recording the source collar trajectory before the probe. This is a
strict generalisation of A (A = replay of a standardized source). It is explicitly distinct from state
transplantation: **no static spatial field is moved into the core**; only the time-series crossing the interface is
substituted, and the core’s own field is never overwritten. Risk: a foreign replay can inject the source’s history
(intended, and measured) and can create a temporal discontinuity at the collar (measured; §7).

**C. In-situ causal-horizon intervention.** Reset/standardize a predeclared region in place (core, collar, inner
halo, outer halo, far E, global) rather than transplanting foreign material. In-place standardization of the *memory
field* on a support is clean (it is the 03G/`causal_confirm` erase, generalised to an on-manifold reference; it
touches only `Mf` on that support). In-place standardization of the *full physical body* (rho,U,V,c,N) is **not**
available without effectively re-creating a reference body inside the core — a transplant with a seam — so this
design standardizes only the memory field and holds the body fixed. A small predeclared set of enclosed radii
(core-only vs core+halo) locates the minimal sufficient comoving region without a retrospective radius scan.

The three trajectories are not independent: the chosen design is the **intersection** of A and C — an in-place
standardized-boundary clamp (A/B) combined with in-place core-memory standardization (C) — which is exactly the
Phase-0 factorial re-expressed with no transplant.

## 4. Task 2 — attractive but invalid designs, explicitly rejected

- **Decoder-only comparison** (read `L/E/G` and compare skill): rejected as primary. Phase 0 already showed
  low-dimensional decoders confound direct readout with storage; decoding is secondary and model-dependent here too.
- **Endpoint blocking** (disable the uptake equation and call the loss “erasure”): rejected. The uptake endpoint is
  never disabled; `λ₊=0` removes only memory’s *modulation* of feeding, never the feeding itself.
- **Starvation-as-erasure** (cut nutrient delivery, attribute the feeding loss to memory): rejected. The clamp
  supplies an on-manifold nutrient/flux boundary and local replenishment keeps the core fed; the sufficiency
  contrast differences out any residual starvation because both of its arms share the identical clamp.
- **Storage inferred from correlation**: rejected. Claims rest on an interventional feeding contrast under a shared
  boundary, not on correlation between `m_plus` and feeding.
- **Learned outcome-selected intervention directions**: rejected. Every mask, radius, reference, and pair rule is
  frozen from geometry and manipulation validity, never from feeding or own-dose decoding.
- **Over-clamping the memory into tautological persistence**: rejected. The core memory is either retained or
  standardized to an on-manifold reference; it is never *held fixed during the probe* in the primary arms (an inert
  clamp would make persistence tautological — it exists only as a labelled secondary control, as in `causal_confirm`).
- **Hidden external controller that supplies the answer**: rejected. The boundary source is a recorded free
  trajectory of an outcome-independent world (own, or the no-history reference); it carries no future-feeding
  information and, for the standardized source, no recipient history (verified: §9).
- **Trading a spatial seam for an equally severe temporal seam**: guarded, not assumed. The temporal discontinuity
  the clamp imposes is measured against a matched sham (own-replay), which is **exactly zero** (§7); only the
  deliberate standardized substitution moves the collar, and that movement is common-mode across the sufficiency
  arms.
- **Redefining the individual after seeing confirmation results**: excluded by construction — this is a DEV design;
  no confirmation outcome exists.

## 5. Task 3 — the chosen minimal design

**In-place directional interface clamp — a no-transplant 2×2 factorial with a comoving-halo cut and the existing
global/readout ablations.**

Two in-place factors, both varying only what they must:

- **Core history** `M ∈ {OWN, STD}` — retain the core `Mf`, or standardize it in place to the translated
  on-manifold no-history reference (`standardize_core_memory`; changes only `Mf` on `d ≤ 10`, verified spatially
  clean, non-target change 0.0).
- **Environment coupling** `B ∈ {COUPLED, CLAMPED}` — leave the real environment coupled, or clamp the barrier ring
  to the outcome-independent no-history reference trajectory each step (`NoSwapClampEngine`), severing the
  environment’s specific history with a standardized, nutrient-matched boundary.

Primary arms and prospective contrasts (world-level means; **not** computed in DEV):

| Arm | `M` | `B` | Role |
|---|---|---|---|
| `OWN·COUPLED` | own | coupled | intact (no-op) |
| `OWN·CLAMPED` | own | clamped | isolated core carrying its history |
| `STD·COUPLED` | std | coupled | standardized core in the real environment |
| `STD·CLAMPED` | std | clamped | double-null reference |

- `τ_C = Y(OWN·CLAMPED) − Y(STD·CLAMPED)` — **core sufficiency**. Both arms share the identical reference clamp, so
  the clamp’s isolation disturbance, any reflection, and any starvation are common-mode and cancel; the residual is
  the causal effect of the retained core memory under a standardized boundary.
- `τ_E = Y(STD·COUPLED) − Y(STD·CLAMPED)` — **environmental access**, with the caveat in §8 (confounded by the
  physical coupling that the real environment restores; only partially separable without transplant).
- `τ_joint = Y(OWN·COUPLED) − Y(STD·CLAMPED)`; interaction `τ_S = OWN·COUPLED − OWN·CLAMPED − STD·COUPLED +
  STD·CLAMPED` — **synergy/relational**.

**Comoving-halo cut (H_HALO).** Repeat the clamp at two predeclared enclosed radii: the core radius (`d ≤ 10`) and a
tighter radius (`d ≤ 6`, still containing the body core). If core-sufficiency survives the tighter isolation, the
sufficient unit is the body core; if it requires the wider enclosure, the sufficient unit is the extended comoving
object. The enclosed radii are fixed from the outcome-independent halo measurement (§9), never from feeding.

**Global and readout ablations (existing, in place).** `up_ref = 0` (`DiagEngine`) tests the global channel (H_G);
`λ₊ = 0` with the algebraic prediction `⟨λ₊·m_plus/(1+λ₊·m_plus)⟩` tests direct readout (H_0). Both remain valid on
all four DEV worlds (uptake endpoint present every step).

**Phase probe (H_PHASE).** A phase-mismatched replay clamps the barrier to the reference trajectory shifted by Δ
steps; the matched replay uses Δ=0. Because the state is Markov with no hidden oscillator, this is a bounded
secondary probe (§10).

## 6. Why a two-cell barrier

The engine’s one-cell stencil means a one-cell overwrite ring is, in principle, a four-adjacency separator (verified
exactly equal to the core’s dilation boundary). In practice a one-cell clamp leaks at ~1e-13 (machine epsilon) once a
front reaches it, whereas a **two-cell overwrite barrier gives bit-exact isolation** (core difference exactly 0.0
under an environment perturbation over 40 steps, all 12 DEV targets). The enclosed radius, not the barrier thickness,
defines the scientific unit. This is a small, reportable engineering result and is locked by
`test_width1_barrier_leaks_but_width2_exact`.

## 7. Hypothesis-by-outcome table

`Y` is integrated future feeding on the bijectively tracked target under the frozen probe. A positive contrast
requires a preregistered practical margin; a “failure” requires a preregistered equivalence bound, never a
non-significant result. “Not established” never means “absent.”

| Hypothesis | Signature under the no-swap design | Distinguishable here? |
|---|---|---|
| `H_C` core/local sufficient | `τ_C > 0`; survives tighter-radius isolation; not collapsed to pure `λ₊` algebra | **Yes (clean)** |
| `H_E` environment sufficient | `τ_E > 0` with the core memory standardized, *and* survives an environment-history control | **Partial** — confounded by physical coupling (§8) |
| `H_R` redundant | both `τ_C` and `τ_E` independently exceed margins | **Partial** (inherits H_E limit) |
| `H_S` synergistic/relational | `τ_S` and joint exceed margins while both separate upper bounds are below sufficiency | **Partial** (inherits H_E limit) |
| `H_HALO` extended comoving unit | core-radius isolation preserves `τ_C` but tighter-radius isolation loses it | **Yes (clean)**, within the predeclared radii |
| `H_PHASE` dynamical-phase access | phase-mismatched replay abolishes `τ_C` while phase-matched preserves it, beyond the boundary-disturbance envelope | **Weak a priori** (Markov; §10) |
| `H_G` global channel essential | `τ_C`/effects collapse under `up_ref=0` | **Yes (clean)** — DEV context: `up_ref` barely moves `m_plus` (0.1994→0.1997) |
| `H_0` residual readout/body | `τ_C` collapses under `λ₊=0` and is fully predicted by the algebraic direct-coupling term | **Yes (clean)** |

The design distinguishes **H_C, H_HALO, H_G, H_0 cleanly** (four major hypotheses, meeting the Task-3 bar) and
places bounded, honestly-labelled constraints on H_E/H_R/H_S/H_PHASE.

## 8. What the design cannot distinguish (declared limits)

- **Environmental sufficiency (H_E) cannot be isolated from environmental physical coupling without transplant.**
  Showing “environment alone suffices” requires a standardized core held inside the real environment (`C_0` in `E`),
  which is a body transplant with a seam. In place, we can only standardize the *memory field* and restore *coupling*
  (`τ_E`), which conflates history access with the nutrient/flux the real environment brings back. `τ_E` is therefore
  reported with an environment-coupling control, and a positive `τ_E` is labelled “environmental access not excluded,”
  never “environmental storage established.”
- **The core factor varies only the memory field.** The body (rho,U,V,c,N) is held fixed on the core, matching the
  03G/`causal_confirm` counterfactual. Claims are “local/core memory access,” not “material ownership” or
  “droplet-only storage.”
- **H_PHASE has little room** in a Markov substrate; a positive phase-mismatch effect would more likely reflect
  boundary-disturbance asymmetry than genuine dynamical-phase storage, and is treated as exploratory.
- A clean `τ_C` that is fully predicted by the `λ₊` algebra supports **local direct readout**, which is *a* form of
  local access but not individual memory, identity, life, or active reconstruction.

A clean partial answer (H_C/H_HALO/H_G/H_0) is preferred to an experiment that claims to separate everything.

## 9. Task 5 — operational definition of the comoving causal halo

The halo is defined **without reference to feeding**, two ways that agree:

1. **Perturbation influence-decay length.** Perturb the persistent memory carrier `Mf` at the body centre by a small
   relative amount and continue; the response amplitude, binned by radius at the relaxed step, falls below 1% of its
   near-core peak at radius **≈ 4** on every DEV target — well inside the radius-10 core. The propagation *front*
   advances at the nearest-neighbour rate (~1 cell/step) but is not the halo; the decay length is.
2. **Static comoving footprint.** The body/attractant profile (contiguous from centre, local peak) confirms the
   physical object is contained within the core radius.

Because the comoving causal halo (~4 cells) sits strictly inside the radius-10 core, the Phase-0.5 core already
over-covers the halo, and H_HALO can be tested by the tighter-radius cut (§5) rather than a radial scan. The two
enclosed radii (6 and 10) are fixed from this measurement, not from any feeding outcome.

## 10. Task 6 — phase inventory

Persistent phase for exact continuation is exactly `{rho, U, V, c, N, C, Mf, uptake, step}`; there is no hidden
buffer or RNG (re-verified). The clamp preserves the scheduler `step`, the update parity (it acts only *after* each
frozen step), and every equation. “Common random numbers” reduces to identical scheduler alignment, since no RNG is
consumed in continuation. A **phase-matched replay** clamps the barrier to the reference value recorded at the same
relative step (Δ=0); a **phase-mismatched replay** uses the reference value from relative step `t+Δ`. Only the
temporal alignment of the standardized boundary is varied — no spatial field is moved and no buffer is scrambled.
Because the substrate is Markov, feasibility of a phase-shifted replay does not by itself imply phase memory; the
probe is exploratory and its interpretation is preregistered as such.

## 11. Task 4 — DEV feasibility results (mechanics only)

Full machine-readable results: `ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_RESULTS.json`
(sha256 `100ecb994718153d3e898b610a9b80b2c5ea74005d41493cd9cc0988fa6edee6`; byte-identical on full rebuild and cached
rerun). Worlds 50002/50004/50005/50007, all three targets alive (12 targets).

| Check | Result |
|---|---|
| clamp disabled == frozen engine (bit-for-bit, 30 steps) | max abs `0.0` |
| **bit-exact isolation** (E-perturbation → core change, width-2, `up_ref=0`, 40 steps) | `0.0` on **12/12** targets |
| own-replay sham disturbance to core / barrier temporal jump | `0.0` / `0.0` (exact, like the Phase-0.5 same-source sham) |
| reference clamp core disturbance (max over targets) | `1.87` — the intended isolation effect, common-mode in `τ_C` |
| reference clamp barrier temporal discontinuity (max / mean) | `1.81` / `0.092` — no immediate core seam |
| immediate disturbance in the core at intervention | `0.0` (core never touched at `t=0`) |
| disturbance localization (`m_plus` RMS vs free, 50002 T0) | step 1: C `0.000`, H `0.317`, E₂₋₃ `0.194`, E_far `0`; step 40: C `0.110`, H `0.333`, E_far `0.009` |
| in-place memory standardization | only `Mf` on the core changes; non-target change `0.0`; core `m_plus` seam ≈ `0.51` |
| all arms 40-step viable (3 distinct alive tracks, coverage < 0.15) | **pass** (own/reference/std/double-null/tight) |
| uptake endpoint present every step, all arms | **pass** |
| reference source outcome-independent (recipient-history-blind) | **pass** |
| existing ablations valid (`up_ref=0`, `λ₊=0`) | **pass**, uptake endpoint retained |
| comoving causal-halo decay radius (max over targets) | `4` (< core radius 10) |

Contrast with Phase 0.5: the crossed transplant produced an immediate one-cell-halo reaction (H RMS 0.809 at step 1)
and seams up to 22.872×; the no-swap clamp produces **zero immediate core change**, a matched sham with **zero**
temporal seam, and an isolation disturbance that is common-mode across the sufficiency arms and therefore cancels in
`τ_C` — precisely the property the transplant lacked.

## 12. Recommendation

**GO for the design mechanics on DEV, with a declared partial scientific scope.** The in-place interface-clamp
operator is bit-exact, viable, localized, sham-controlled, outcome-independent, and reuses the frozen engine and
probe unchanged. It distinguishes H_C, H_HALO, H_G, and H_0 cleanly and bounds H_E/H_R/H_S/H_PHASE honestly.

Exact next authorized action: human review of this design and the accompanying unsealed decision tree
(`ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_PREREG_DRAFT.md`). No practical/equivalence margins, no probe freeze, no power
calculation, and **no seed family** are set here; none may be chosen from any confirmation outcome. Do not
preregister or open any prospective seed until margins, probe, power, and a semantic seed-family audit are frozen and
receive explicit human approval. The strategic reviewer should reconcile this no-swap line against the Phase-0.6A
transplant repair; they are deliberately competing designs, and this branch establishes that a defensible causal
question is answerable without spatial grafting.
