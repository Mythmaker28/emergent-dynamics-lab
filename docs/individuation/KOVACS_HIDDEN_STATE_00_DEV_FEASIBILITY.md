# KOVACS-HIDDEN-STATE-00 — DEV-only crossing & timing feasibility (Phase 0)

**Scope & firewall.** Everything here is derived from **already-open DEV worlds (57001–57024)**. Two
committed, reproducible artifacts back every number:

- `KOVACS_HIDDEN_STATE_00_CANDIDATE_Z_AUDIT.json` — read-only audit of the frozen
  COUNTERFACTUAL-HISTORY-CORE-00 DEV results (17 complete worlds);
- `KOVACS_HIDDEN_STATE_00_DEV_CROSSING.json` — a bounded engine probe on 6 open worlds
  (`experiments/individuation/kovacs_hidden_state_dev_crossing_probe.py`).

The probe measures **only the candidate matching variable** (focal mass) during drive and no-drive
relaxation. It does **not** compute any post-release between-branch excursion, and no design parameter
(`m*`, tolerance, horizon, gate) is chosen from any response. The probe **does run the engine**
(`make_checkpoint`, `engine.step`) on already-open DEV worlds to record matching-variable trajectories;
it opens **no new seed namespace** and computes **no excursion outcome** (so this is DEV feasibility, not
a prospective run). The 6 probed worlds are the first six complete-block DEV worlds by seed (57001,
57003, 57006, 57008, 57009, 57010); the incomplete worlds 57002/04/05/07 were skipped by that rule, not
by any outcome.

## 1. Question this must answer

For a genuine Kovacs test three feasibility facts must hold:

1. **Existence of a crossing** — two frozen histories can bring the two clones to a *common* value of
   `Z` (`m*`), preferably by approaching it from **different directions** (one descending, one
   ascending), which maximises the hidden-state difference at the match.
2. **Timing** — whether a single fixed **same-clock-time** schedule can place both at `m*` at a common
   step across heterogeneous worlds (option a), or whether a **frozen, per-world, outcome-independent
   crossing rule** with age controls is required (option b).
3. **Non-triviality** — matching `Z` must leave the clones in *different* hidden states (else the null
   is trivial and the test uninformative).

## 2. Non-triviality — hidden DOF survive a mass match (already-open DEV audit)

Within-world-centred across the four existing histories (17 worlds), the fraction of each observable's
history variation that **survives** a match on the **primary `Z` (core-region mass)**:

| co-observable | corr with core mass | fraction surviving at fixed core mass |
|---|---:|---:|
| body area | 0.886 | **0.46** |
| shape (rg) | 0.802 | 0.60 |
| tracked body mass | 0.945 | 0.33 |
| uptake memory `m_plus` | −0.093 | 0.996 |
| order memory `m_minus` | −0.284 | 0.96 |

Even with the *weak* existing histories (all monotone-growth, dose-dominated, median per-world mass
span ≈3.06), a core-mass match leaves ~46 % of the area variation, ~60 % of the shape variation, ~33 %
of the tracked body-mass variation, and essentially all of the internal memory variation unmatched.
**Non-triviality holds**: distinct hidden states at a matched core mass are not just possible but present
in DEV. (The body-mass-referenced version — area 0.25, shape 0.57 — is the secondary reference in the
audit JSON; the core-region mass is 1.10–2.03× the body mass, median 1.38×, so it is not identical to
body mass.) A purpose-built overshoot/approach pair (below) is expected to separate them substantially
more.

## 3. Existence of a crossing — overshoot is realisable (engine probe)

Three schedules were run per world on the frozen focal clone (amplitude · steps):
`OVERSHOOT = (0.060·60, starve·60, no-drive·360)`, `APPROACH = (0.010·120, no-drive·360)`,
`NODRIVE = (no-drive·480)`. Focal mass was recorded every step (tracked focal mass; frozen core mass
co-recorded).

| seed | overshoot peak (elapsed) | overshoot decline after peak | overshoot post-peak min | approach max | crossing band overlap? |
|---|---:|---:|---:|---:|:--:|
| 57001 | 64.84 (298) | 5.32 | 59.52 | 41.07 | no (needs longer starve) |
| 57003 | 63.18 (171) | 11.22 | 51.96 | 51.97 | **yes (≈52)** |
| 57006 | 39.59 (133) | 7.44 | 32.16 | 36.85 | **yes (≈34)** |
| 57008 | 80.61 (242) | 13.23 | 67.38 | 61.30 | no (needs longer starve) |
| 57009 | 34.82 (151) | 6.48 | 28.34 | 30.95 | **yes (≈30)** |
| 57010 | 47.26 (212) | 8.42 | 38.84 | 38.40 | borderline (≈38.5) |

**Findings (stated conservatively).**

- **Non-monotone overshoot exists in every world (6/6):** a hard early feed followed by starvation
  drives focal mass up to a peak and then *down*. So a history can cross a target `m*` **from above**.
  This is the robust, fully-demonstrated result.
- **Band overlap in 3/6 worlds** (57003, 57006, 57009; 57010 borderline): the overshoot's declining
  branch descends into the value range the gentle approach also reaches, so a common per-world `m*` is
  crossable by both histories there with untuned amplitudes.
- **Genuine opposite-direction crossing (approach still ascending at the shared value) is demonstrated in
  only 1/6** (57003, and marginally — the approach reaches ≈52 at its own turning point while the
  overshoot descends through ≈52). In 57006 and 57009 the gentle approach (amplitude 0.010) itself
  overshoots and peaks at elapsed 1–2, then declines, so *both* branches arrive at the shared value
  **descending**. The stated mechanism "`H_APPR` approaches from below" is therefore **under-demonstrated**
  in DEV: a still-ascending approach at the crossing needs a gentler/slower sustained feed (or an earlier
  match time). Establishing opposite-direction crossings across the DEV set is a **Phase-1 calibration
  target**, not a current result.
- In the non-overlap worlds the overshoot mass is still monotonically declining at the end of the
  360-step no-drive tail; a stronger/longer starvation stage brings its declining branch into the
  approach band. The dynamics that make this work (net mass loss under starvation) are directly observed.

## 4. Timing — a fixed same-clock-time schedule is infeasible; a per-world crossing rule is required

- **World heterogeneity is large.** Achievable masses are world-specific: post-turnover DEV focal body
  masses (first-stage `body_mass`) range 12.4–32.7 across worlds, and under strong feed the tracked-mass
  peaks range 34.8–80.6. A single **absolute** `m*` cannot be common across worlds; `m*` must be defined
  **per world** by a frozen rule.
- **Crossing times differ ≈2×** (overshoot peaks at elapsed 133–298). A single fixed schedule pair
  cannot place both branches at `m*` at a **common step** across worlds.

Therefore option (a) — a fixed same-clock-time two-stage schedule with one absolute target — is **not**
feasible here. Option (b) is adopted: a **frozen, outcome-independent per-world crossing rule** with
explicit age/time controls (specified in `KOVACS_HIDDEN_STATE_00_PROTOCOL.md`):

- `m*` set per world by a frozen, outcome-independent reference (the direct-relaxation / no-drive
  reference mass at a fixed elapsed step) — never from a Kovacs excursion;
- each branch **released at the first step ≥ a minimum age at which its `Z` first crosses `m*`** (a
  stopping rule on the *matching* variable, not the outcome);
- release ages recorded per branch; the **branch-age difference** is a covariate/gate, and an equal-age
  variant is retained so age cannot masquerade as hidden state.

## 5. Tolerance and horizon (mechanical, frozen; not tuned from any response)

- **Match tolerance** `tol`: a fixed fraction of the per-world pre-history mass scale (proposed
  `tol = 0.02 · m0`, with `m0` the checkpoint focal mass), i.e. a ~2 % match. This is a mechanical
  scale-relative choice, set before any excursion is seen. A world where neither history can reach `m*`
  within `tol` after the min-age gate is `MATCH_INVALID` for that world (never imputed).
- **Horizon** `T_hor`: a round number on the established DEV timescales (proposed 120 steps, the parent
  probe horizon scale), fixed independently of any excursion. Earlier/later times are diagnostic only.

These are Phase-0 *proposals* to be locked verbatim at seal; they are recorded now so they are
demonstrably not back-selected from an outcome.

## 6. Feasibility verdict

- Non-triviality: **established** (hidden DOF survive a core-mass match in DEV: 46 % area, 60 % shape,
  96–99.6 % memory).
- Overshoot crossing (from above): **fully demonstrated** — non-monotone in 6/6 worlds.
- Common-`m*` reachability: **band overlap demonstrated in 3/6** untuned; genuine opposite-direction
  crossing demonstrated in only **1/6** (marginal). The matching *mechanism* exists; a robust
  opposite-direction crossing is **not yet demonstrated**.
- Tolerance-level match (both branches within `tol = 0.02·m0` at `N_min ≥ 12` complete worlds):
  **not tested** here — the probe used a disclaimed placeholder `m*` and never applied the acceptance
  tolerance. This is unproven and is a Phase-1 item.
- Timing: a fixed same-clock-time schedule is **infeasible** (mass scales and crossing times differ ≈2×);
  a frozen per-world crossing rule with age controls is required and is feasible.

**Net:** the matching *mechanism* is demonstrated (overshoot + band overlap); the *quantitative* match
(opposite-direction crossing across the DEV set, both branches within `tol`, at `N_min`) is **not yet
demonstrated** and is the first Phase-1 task.

**Open item carried to Phase 1 (design finalisation, under human review):** DEV-calibrate a per-world
schedule family + crossing rule that lands both branches within `tol` of the per-world `m*` — with a
still-ascending approach where achievable — in a pre-declared minimum fraction of worlds, and demonstrate
opposite-direction crossings across the full DEV set, *before* any seal. This is matching-variable
calibration only and opens no prospective namespace.
