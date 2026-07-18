# COUNTERFACTUAL-HISTORY-CORE-00 — DEV-only exact-clone protocol

**Status:** frozen before seed 57001; DEV only; no prospective authorization.

**Accepted parent:** `4ef4bed0ee43a8d6edaec2b597e205eeb2393327`.

**Manifest:** `COUNTERFACTUAL_HISTORY_CORE_00_MANIFEST.json`.

## Scientific question and scope

For one pre-history focal target in each independent source world, do fixed differences in cumulative dose and in
temporal order at matched dose remain in the evolved core and alter future feeding after deep material turnover
under a common probe? The exact-clone factorial repairs the four-natural-target infeasibility of
BALANCED-HISTORY-ISOLATION-00 without reusing its observed targets or changing the world generator.

This identifies counterfactual causal behaviour inside the deterministic simulator because all four potential
outcomes can be generated from one pre-treatment state. It does not reproduce the physical-experiment limitation
that only one potential outcome can be observed per individual. External generalization rests on the 24 independent
original source worlds, never on branch or droplet counts.

The experiment cannot establish identity, unique ownership, active reconstruction, reproduction or heredity.

## Frozen source worlds and focal selection

The immutable DEV family is 57001–57024, with no extension. Each world is warmed for the frozen 800 steps. Detected
components are placed into the existing deterministic descending-size greedy set subject to size at least 45,
coverage below 15%, radius-10 core containment and pairwise centroid separation at least 24. The two-cell barrier
must not intersect another selected target. The selected set is then assigned canonical tracker IDs by centroid
coordinates and size; the lowest eligible ID is the focal target. Selection uses no future survival, memory,
turnover or feeding outcome. A world with no focal target is pre-treatment ineligible.

Coordinates, body metrics, masks, all eligibility terms and the selected tracker ID are recorded.

## Exact checkpoint and branching

At the pre-history checkpoint, one serialization contains `rho`, `U`, `V`, `c`, `N`, `C`, `uptake`, `Mf` and
absolute `IOMState.step`. The tracker mapping is the canonical ordered set of selected masks plus the frozen focal
ID. The tracer scheduler is a pure function of `step`. Initialization consumes the seeded RNG; engine continuation
contains no stochastic draw and retains no RNG object. Thus the common-random-number policy is exact deterministic
continuation.

Four states and tracker mappings are deserialized from the same payload. Deterministic canonical bytes, fieldwise
zero errors, mapping hashes and focal identity must be identical before treatment. Histories run in a seed-derived
SHA-256 permutation. Canonical and reversed execution order must produce identical label-specific results on the
already-open DEV test seed before 57001 is initialized.

## Histories and non-focal rule

Each history consists of two consecutive 60-step local Gaussian nutrient episodes followed by the frozen 120-step
settle:

| History | Episode 1 (`a1`) | Episode 2 (`a2`) | Dose | EARLY-LATE coordinate |
|---|---:|---:|---:|---:|
| H_L_EARLY | 0.0175 | 0.0075 | 0.025 | +0.01 |
| H_L_LATE | 0.0075 | 0.0175 | 0.025 | -0.01 |
| H_H_EARLY | 0.0325 | 0.0225 | 0.055 | +0.01 |
| H_H_LATE | 0.0225 | 0.0325 | 0.055 | -0.01 |

Only the focal target is assigned a history. Every non-focal selected target has direct amplitudes `(0,0)` in every
branch. Natural diffusion or other physical spillover from the single focal Gaussian is a causal consequence of
that focal intervention, not a different assigned neighbour history.

## Fixed deep-turnover assessment

After the settle, one passive focal-origin cohort is appended. Every branch advances exactly 1000 additional steps,
with geometry-only bijective tracking at every step. Step 1000 was frozen as a round pre-data margin above the
already-open DEV deep range 793–890; no result from this family selected it. The common elapsed time prevents
history-specific assessment ages and enables one common history-independent boundary source.

A branch is deep-valid only if the focal target remains bijectively tracked, coverage stays below 15%, an entity is
matched, and old focal material fraction `M <= 0.25` at step 1000. No failed potential outcome is set to zero.

## First stages

Before any probe, the frozen features are read without modifying the core: core `m_plus`, `m_minus`, the frozen
11-dimensional `Mf` summaries, component standard deviations/correlation/roughness, the fixed centered full-field
core vector, body size/mass/radius, neighbour distance, core rho/N/c/u/v/sigma, world `up_ref`, world N/c/rho,
material M and elapsed time. Dose is expected positive on mean core `m_plus`. The protocol-fixed EARLY-minus-LATE
order contrast is expected negative on mean core `m_minus`; signs are never flipped per world.

## Common boundary and probes

The boundary source is one same-seed no-drive continuation from the exact checkpoint. It receives no history,
advances for the same 240 history-plus-settle steps and fixed 1000 turnover steps, and is selected by the frozen
on-manifold median-size/centroid component rule. A single source state is translated onto each recipient's radius-10
core/two-cell collar. No result-dependent alternative reference is created.

Each deep branch enters six continuations without any erase, standardization, graft or replacement of core `Mf`:

- `coupled`: ordinary frozen engine; primary;
- `isolated`: two-cell no-swap reference clamp plus `up_ref=0`; primary;
- `coupled_g0` and `sham_own_replay_g0`: global-matched manipulation controls;
- `coupled_lamplus0` and `isolated_lamplus0`: secondary readout-mediation controls.

All arms reset only `N := N0`, settle for 40 steps, receive the same uniform `+0.25 N` for five steps, and advance
through the frozen 40-step horizon. Primary `Y` is integrated uptake on the bijectively tracked focal component
through step 40. Integrated fixed-mask uptake is the tracker-independent convergence control; instantaneous step-40
uptake and earlier times are diagnostics. The own-replay clamp must match `coupled_g0` exactly.

## Estimands and original-world inference

For each arm and complete source world:

`delta_D = 0.5 * [(Y_HE + Y_HL) - (Y_LE + Y_LL)]`

`delta_O = 0.5 * [(Y_LE + Y_HE) - (Y_LL + Y_HL)]`

`delta_DO = (Y_HE - Y_HL) - (Y_LE - Y_LL)`

`T_D`, `T_O` and `T_DO` are isolated minus coupled contrasts. Scaling and fitting are unnecessary. Means, medians,
standard deviations, 95% Student-t intervals and sign counts summarize the original-world contrast vector. A
directional gate requires at least 75% protocol-aligned signs and a 95% interval excluding zero. An unoriented gate
uses the majority direction without changing individual signs.

A complete feeding block requires all four histories to pass post-history tracking, fixed-step deep turnover, both
primary probes and manipulation controls. At least four complete source worlds are required. All assigned-history
survival indicators are also analysed as paired factorial contrasts across pre-treatment eligible worlds; a common
sign in at least 75% of worlds plus a two-sided 95% interval excluding zero is a frozen `SURVIVAL_EFFECT` gate.

## Frozen decision logic

1. Fewer than four complete worlds: `DEV-FEASIBILITY-FAIL`; downstream absence is not inferred.
2. Invalid cloning, tracker, clamp, global standardization, endpoint or sham: `MANIPULATION_INVALID` when estimable.
3. Differential pre-probe persistence: `SURVIVAL_EFFECT`; complete-block feeding is selection-sensitive.
4. Neither protocol-aligned first stage: `NO_MEMORY_FIRST_STAGE`.
5. Order first stage without isolated feeding: `ORDER_STATE_WITHOUT_FEEDING`.
6. Positive dose first stage and feeding in isolation, with compatible coupled direction, but no complete order
   result: `DOSE_ONLY`.
7. Protocol-aligned dose and order first stages plus isolated feeding contrasts and compatible coupled directions:
   `DOSE_AND_ORDER`.
8. Valid state first stages but no isolated feeding transport: `NO_TRANSPORT`.
9. Otherwise: `UNRESOLVED`.

`PREREG-CANDIDATE-GO` requires `DOSE_AND_ORDER`, all gates, at least four source worlds and positively aligned
leave-one-world-out full-field order vectors. No outcome authorizes prospective execution.

`lam_plus=0` is secondary contrast mediation: collapse supports the designed uptake channel; persistence indicates
another path. Endpoint availability alone is not mediation and collapse cannot erase an intact pre-probe first stage.

## Before-data abort gates

Before seed 57001: four byte-identical clones; focal identity; exact history values/order; zero direct non-focal
drive; execution-order invariance; deterministic replay; clamp-disabled identity; exact two-cell spatial isolation;
`up_ref=0`; original-world aggregation; no branch/target pseudoreplication; and fresh namespace verification. Any
failure aborts before DEV execution.
