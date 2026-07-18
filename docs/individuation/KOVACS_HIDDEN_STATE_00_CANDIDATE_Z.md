# KOVACS-HIDDEN-STATE-00 — candidate `Z` comparison and selection/refusal (Phase 0)

**Rule of selection.** `Z` is chosen on **mechanical** criteria from already-open DEV data
(`KOVACS_HIDDEN_STATE_00_CANDIDATE_Z_AUDIT.json`, produced by
`experiments/individuation/kovacs_hidden_state_candidate_z_audit.py`, reading the frozen
COUNTERFACTUAL-HISTORY-CORE-00 DEV results, 17 complete worlds 57001–57024). No candidate is chosen
because it predicts, or is expected to predict, a later Kovacs excursion. Exactly **one** primary `Z`
is selected; every other candidate is explicitly refused with a reason.

## 1. Mechanical criteria (frozen before inspection)

A primary `Z` must be:

1. **scientifically interpretable** — a named physical property of the organism, not a fitted score;
2. **measurable without a tracker-dependent endpoint if possible** — the endpoint (the post-release
   `Z` trajectory) should not require per-step re-segmentation that a tracker collision could corrupt;
3. **capable of monotone or well-defined threshold crossing** — so a frozen crossing rule can bring two
   histories to a common value;
4. **history-controllable** — the histories must be able to move it (else no match is meaningful);
5. **not the tested coordinate** — it must not itself be the hidden memory state under test;
6. **individual-level** — a property of the organism, not of the whole world/environment (which is held
   common by design and so cannot be the object matched).

An auxiliary requirement, used to break ties in favour of a clean estimand: a **support common to both
clones**, so the between-branch difference cancels common drift exactly (§4 of the derivation).

## 2. Candidate table (already-open DEV audit)

| candidate | interpretable | tracker-free endpoint | frozen dose \|contrast\| | per-world span (median) | verdict |
|---|:--:|:--:|---:|---:|---|
| **core mass** (`core_rho_mass`, frozen r=10 mask) | yes | **yes** | 4.556 | 4.361 | **PRIMARY** |
| body mass (`body_mass`, tracked) | yes | no | 3.626 | 3.064 | secondary/robustness |
| body area (`body_size`) | yes | no | 4.176 | 3 (integer) | refuse |
| shape (`body_rg`) | yes | no | 0.149 | 0.139 | refuse |
| uptake memory (`mplus_mean`) | no | no | 0.013 | 0.012 | refuse (is hidden state) |
| order memory (`mminus_mean`) | no | no | 0.014 | 0.017 | refuse (is hidden state) |
| world mass (`world_rho_mass`) | yes | yes | 5.637 | 5.195 | refuse (environment) |
| world uptake (`world_up_ref`) | yes | yes | ~2e-6 | ~0 | refuse (environment; held common) |
| feeding-ready / probe uptake | partial | no | — | — | refuse (probe- and outcome-adjacent) |

## 3. Selection: primary `Z` = core mass (frozen checkpoint-centred radius-10 mask)

`Z = sum(rho over the radius-10 core mask centred at the pre-history checkpoint focal centroid)`.

It uniquely satisfies all mechanical criteria at once:

- **Interpretable**: the mass of the organism's core region — the same "core rho mass" already treated
  as a first-class macro-observable in the parent lineage (dose contrast +4.556, 17/17 positive).
- **Tracker-free endpoint**: the mask is a fixed set of coordinates frozen at the checkpoint; the
  post-release `Z(t)` is `rho` summed over that fixed support with **no per-step tracking**, so a late
  tracker collision (a documented failure mode in this project's merge-incident record) cannot corrupt
  the endpoint.
- **Common support**: the two clones descend from the *same* checkpoint, so the mask is **identical**
  for both branches. The primary between-branch estimand `D_w = ∫(Z_A − Z_B)` therefore differences two
  sums over the *same* cells, cancelling common non-equilibrium drift and any shared forcing exactly.
- **Crossable & controllable**: DEV masses move smoothly and are strongly history-driven; the crossing
  probe (`KOVACS_HIDDEN_STATE_00_DEV_FEASIBILITY.md`) shows core/body mass rising and falling under
  designed schedules, i.e. threshold-crossable from either side.
- **Contains body mass (not identical to it)**: the parent protocol requires `body ⊆ radius-10 core`
  (`_geometry` / `ns.core_and_collar`) for a valid probe, so `core mass ≥ body mass`. In DEV the
  core-region mass is **1.10–2.03× the tracked body mass (median 1.38×)** and also includes any
  peri-focal `rho` inside the fixed disk — it is a *core-region* amount, deliberately **not** relabelled
  as body mass. This is an accepted interpretability cost of the tracker-free common support; the tracked
  body-mass robustness reading (below) indicates whether a divergence is intra-focal or peri-focal.

**Robustness co-observable (not primary):** tracked focal body mass. It is the most intuitive "whole
organism" amount but its endpoint is tracker-dependent and its per-branch support differs, contaminating
the between-branch difference. It is reported alongside `Z` as a consistency check only; a disagreement
between the frozen-mask primary and the tracked robustness reading is a diagnostic, never a promotion.

## 4. Refusals (explicit)

- **body area (`body_size`)** — refused as primary: integer-valued with a median per-world span of only
  3 cells, so the crossing tolerance would be a large fraction of the achievable range (coarse match);
  and its endpoint is tracker-dependent. Retained as a *diagnostic* co-observable because at fixed mass
  25 % of its history variation survives (a natural hidden DOF to report, not to match on).
- **shape (`body_rg`)** — refused: it is a distribution/shape statistic, not a conserved amount; weak
  history loading (0.149); 57 % of its variation survives a mass match, i.e. it is largely *independent*
  of the matched amount and so is a hidden-DOF *report*, not a matching target.
- **uptake memory (`mplus_mean`), order memory (`mminus_mean`)** — refused on principle: these are the
  internal memory readouts, i.e. candidate hidden coordinates themselves (they retain 96–99 % of their
  variation at fixed mass). Matching on them would conflate the matched macrostate with the hidden state
  the experiment is meant to detect.
- **world mass (`world_rho_mass`), world uptake (`world_up_ref`)** — refused: these are environment-
  level quantities. The environment is held **common** by design (common boundary source, `up_ref`
  clamp); matching a world-level quantity would not be a statement about the organism's hidden state,
  and `up_ref` is in any case near-constant across histories (span ~0).
- **feeding-ready state / probe uptake** — refused: it requires the standardised feeding probe, so it is
  both tracker- and probe-dependent and sits adjacent to the *outcome* (feeding) of the stopped prior
  line, risking outcome-selection. Kovacs is deliberately **probe-free**.

## 5. Integrity notes

- The selection uses only the sign/scale and tracker-dependence of observables, never their (unmeasured)
  association with any Kovacs excursion. No excursion is computed in Phase 0.
- The DEV numbers cited here are reproducible from the committed audit script over the committed frozen
  DEV JSON; provenance is recorded in `KOVACS_HIDDEN_STATE_00_CANDIDATE_Z_AUDIT.json`.
- `n` is the original source world throughout; per-history, per-branch and per-cell values here are
  descriptive inputs to selection, not statistical units.
