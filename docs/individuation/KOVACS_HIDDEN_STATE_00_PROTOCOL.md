# KOVACS-HIDDEN-STATE-00 — minimal Kovacs protocol (Phase-0 design)

**Status.** Phase-0 design draft. DEV only. No prospective family inspected, reserved, or initialised.
No seal. Machinery reused verbatim from the accepted parent
`03a909a` (`codex/counterfactual-history-mechanism-reconciliation-00`): `make_checkpoint`,
`clone_checkpoint`, the focal-Gaussian drive of `apply_history`, `turnover_fixed`, `no_drive_reference`,
the two-cell no-swap isolation clamp with `up_ref=0`, and `access_structure_noswap_operators.core_and_collar`
for the frozen core mask. The primary observable and match rule are new; everything they touch is
inherited unchanged.

**Statistical unit.** The original source world. Histories, threshold crossings, clones, branches, time
points and reference/sham arms **never** increase `n`.

## 0. Objects and notation

- `Z` = **core-region mass** = `sum(rho over the radius-10 core mask centred at the checkpoint focal
  centroid)` (frozen coordinate mask, identical for both clones; tracker-free endpoint). **Contains** the
  focal body mass (`body ⊆ core` ⇒ `core mass ≥ body mass`; DEV core is 1.10–2.03× body, median 1.38×);
  it is not identical to body mass and includes any peri-focal `rho` inside the disk.
- `m0` = checkpoint focal mass (per world). `m*` = per-world match target (§4). `tol` = match tolerance.
- `t_R` = release step (per branch, per world). `T_hor` = probe-free relaxation horizon.

## 1. One exact pre-history snapshot per world

For each source world, build the world (`seed_world` + `WARM=800`), select the single pre-history focal
target by the **existing** frozen rule (descending-size greedy set; size ≥ 45; coverage < 15 %;
radius-10 core containment; pairwise separation ≥ 24; two-cell barrier clear; lowest canonical tracker
ID among eligible). Selection uses no future survival, turnover, match, or excursion outcome. Serialize
the complete Markov state (`rho, U, V, c, N, C, uptake, Mf`, absolute `step`) once. A world with no
eligible focal target is pre-treatment ineligible and contributes nothing.

## 2. Exact clone branches

Deserialize the payload into the required branches (byte-identical: canonical state bytes, tracker
mapping hash, focal identity, and field-wise zero error must match before treatment, exactly as
`validate_four_clones`). Branches are potential outcomes, not replicates.

## 3. Two frozen histories (two-stage protocols)

Assign to the focal target two **frozen, pre-declared** two-stage histories, applied as focal-Gaussian
nutrient drive (`state.N += a·patch` per step; non-focal targets receive `(0,0)`; physical spillover
from the single focal Gaussian is a treatment consequence, not a second history):

- **`H_OVER` (overshoot):** a strong early feeding stage followed by a starvation stage — drives `Z`
  **above** `m*`, then lets it **descend** toward `m*` (DEV-demonstrated non-monotone, 6/6 worlds).
- **`H_APPR` (approach):** a gentle sustained feeding stage — drives `Z` **up toward** `m*` from below.

The intended configuration reaches a common `m*` from **opposite directions** (one descending, one
ascending), maximising the hidden-state difference at the match. The DEV probe shows this is only
partially achieved with untuned amplitudes — the gentle approach still overshoots-and-declines in
low-carrying-capacity worlds — so establishing a genuine opposite-direction crossing across the DEV set
is a Phase-1 calibration target (`KOVACS_HIDDEN_STATE_00_DEV_FEASIBILITY.md`), not a settled result.
Exact amplitudes/durations per world are set by the frozen crossing-rule calibration (§4); the *family*
and *rule* are pre-declared, never per-world hand-set from any excursion. The gentle stage stays within
the parent drive support `[0.005, 0.035]`; the strong overshoot stage used in the DEV probe (~0.06)
**exceeds** that ceiling, so its in-distribution status for the parent qualification must be checked and
declared explicitly at seal.

## 4. Bring both branches to the common `Z` target — frozen crossing rule (option b)

A fixed same-clock-time schedule is **infeasible** here (worlds differ ≈2–3× in mass scale and crossing
time; `KOVACS_HIDDEN_STATE_00_DEV_FEASIBILITY.md`). The match therefore uses a **frozen,
outcome-independent, per-world crossing rule with explicit age/time controls**:

1. **Per-world target `m*`** = `Z` of the **direct-relaxation reference** (the common same-seed no-drive
   continuation, `no_drive_reference`) evaluated on the frozen core mask at a **fixed elapsed step**
   `t_ref` (pre-declared). `m*` is a function of the history-independent reference only — never of any
   Kovacs excursion, and never of the branch being matched.
2. **Minimum age gate** `A_min` (pre-declared, common to both branches).
3. **Release step `t_R`** for each branch = the **first step `≥ A_min` at which that branch's `Z` first
   crosses `m*`**. This is a stopping rule on the *matching variable*, not the outcome.
4. **Match acceptance:** `|Z_b(t_R) − m*| ≤ tol`, with `tol = 0.02·m0` (frozen, scale-relative). A
   branch that never crosses `m*` within `tol` after `A_min` (before a turnover/tracker failure) makes
   the world `MATCH_INVALID`; it is **never** imputed.
5. **Direction record:** the crossing direction (`H_OVER` from above, `H_APPR` from below) is recorded;
   an equal-target opposite-direction crossing is the primary configuration.

Because the two branches generally cross at **different steps/ages**, branch age at release is recorded
and enters analysis as (i) a covariate/gate and (ii) an **equal-age control variant** in which both
branches are released at a common pre-declared step and matched only within `tol` — so that a divergence
cannot be an artifact of differing release age. No body-equalisation surgery is used at any point: the
match is achieved by the histories and the crossing time alone.

Of the frozen scalars, only `tol = 0.02·m0` and `T_hor` (proposed 120) carry proposed numeric values in
Phase 0; `A_min` and `t_ref` are declared **symbolically** and receive their frozen numeric values from
the Phase-1 power/calibration step (fixed by mechanical rule on the DEV timescales, never from an
excursion). They are not yet frozen numbers and must not be read as such.

## 5. Deep turnover (retained, frozen)

Between history and the match/release window, each branch advances the frozen **1000-step deep-turnover
interval** (`turnover_fixed`): geometry-only bijective tracking every step, coverage < 15 %, and
`deep_valid` requiring old focal-material fraction `M ≤ 0.25` (≥75 % replacement). A branch failing deep
validity censors its world (no imputation). Placing the crossing/release **after** turnover makes the
test about history that **persists or regenerates across material replacement** — with no ownership
claim.

## 6. Common release — identical everything, probe-free

At `t_R`, both branches are released under a **common** continuation and simply advanced `T_hor` steps
with **no probe**:

- **same dynamics** — the ordinary frozen engine (`MEM_INTACT`), identical parameters;
- **same environment / qualified boundary** — one **common, history-independent** boundary source
  (`no_drive_reference` continuation) translated onto each recipient's radius-10 core / two-cell collar,
  exactly as the parent's qualified common-boundary continuation. Because the tracer/feed scheduler is a
  pure function of absolute `step` and the branches generally release at **different** absolute steps
  `t_R`, the release must **align the boundary/scheduler phase** (feed-cohort phase) across the two
  branches and the reference — the readout indexes elapsed `s` from each branch's own `t_R` while the
  injected boundary trajectory is presented at a common phase — so that a divergence cannot arise from a
  differing scheduler phase. This absolute-clock alignment is a required before-data check;
- **same `up_ref` condition** — `up_ref` **clamped to a common value** (`up_ref = 0`, the parent's
  isolated arm) so the endogenous environment cannot differ between branches (primary). A coupled arm
  with endogenous `up_ref` is a **secondary** readout only.
- **probe-free** — no `N` reset, no stimulus, no feeding readout. Relaxation only.
- **no manipulation at release** — no erase, standardisation, graft, or replacement of core `Mf`;
  release is pure continuation of `F`.

`Z_b(t)` is recorded every step on the frozen core mask for `t ∈ [t_R, t_R + T_hor]`; tracked body mass
and body area are co-recorded as diagnostics.

## 7. Required controls (each per world, all frozen)

- **Direct-relaxation reference** — the common no-drive continuation; supplies `m*` and a
  history-neutral relaxation baseline `Z_ref(t)`.
- **Exact own-replay sham** — re-running a branch from its own release state under the common release
  must reproduce `Z_b(t)` **bit-for-bit** (determinism gate).
- **Identical-history clone control** — two clones given the **same** history and matched to `m*` must
  give between-branch difference `D ≡ 0` (any nonzero exposes a match/tracker/clamp defect →
  `MATCH_INVALID`, not hidden state).
- **One-step discontinuity diagnostic** — `|Z_b(t_R+1) − Z_b(t_R)|` must lie within the free-running
  per-step increment; a jump signals a release/bookkeeping artifact.
- **Survival / tracker controls** — focal bijectively tracked through `t_R + T_hor`, coverage < cap;
  failed branches censor the world, never imputed as zero.
- **Clock-time / branch-age control** — release ages recorded; equal-age variant (§4) run so age cannot
  masquerade as hidden state.
- **Tracker-independent robustness** — primary `Z` is already frozen-mask (tracker-free); tracked body
  mass is the convergence cross-check.

## 8. Before-data abort gates (all must pass before any DEV-calibrated match is executed)

Byte-identical clones; focal identity; exact history values/order; zero direct non-focal drive;
deterministic replay; two-cell isolation exactness; `up_ref=0` common; frozen core mask identical across
clones; `m*` computed from the reference only; `tol`, `A_min`, `t_ref`, `T_hor` frozen and
outcome-independent; original-world aggregation with no branch/target/crossing pseudoreplication; and
(for any future prospective phase) a fresh disjoint seed namespace. Any failure aborts before execution.

## 9. What is measured (estimand pointer)

The primary quantity is the **between-history excursion of `Z` from the matched value** aggregated once
per source world, defined and classified in `KOVACS_HIDDEN_STATE_00_ESTIMAND_AND_CLASSIFICATION.md`; the
raw per-world fields that make a genuine null distinguishable from an invalid match are in
`KOVACS_HIDDEN_STATE_00_NULL_DIAGNOSTIC_SCHEMA.json`. No excursion is computed in Phase 0.
