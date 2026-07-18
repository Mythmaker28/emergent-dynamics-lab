# KOVACS-HIDDEN-STATE-00 — Phase-1 natural-coincidence report

**Verdict: `SCALAR_ONLY_FEASIBLE` — `STOP_PROSPECTIVE`.**

Phase 1 asked whether a scientifically *stronger* natural macrostate-coincidence than scalar core-mass
matching is reachable — two exact-clone histories brought to coincidence on a **compact overt physical
panel** (not one scalar), without surgery, regression, transplantation or outcome tuning — so that a
future divergence could be attributed to genuinely hidden state rather than to already-known physical
carryover. The answer, on the already-open DEV worlds, is **no at a mechanically-defensible tolerance**:
the closest natural coincidence still leaves a *systematic* overt residual, so matching remains scalar in
force. **No scientific excursion outcome was computed** anywhere in this phase.

Branch `claude/kovacs-hidden-state-00-phase1` off Phase-0 `e76a94f`. Frozen schedule
`schedule_sha256` recorded in `KOVACS_HIDDEN_STATE_00_PHASE1_DEV_RESULTS.json`.

## 1. Design (and why it changed from the Phase-0 crossing picture)

The Phase-1 pilot established a decisive mechanical fact: **after the frozen 1000-step deep turnover the
feed–starve overshoot transient is gone** (turnover ≫ the fast-memory timescale ~28 steps), leaving only
a near-constant dose-carryover mass offset. A post-turnover *opposite-direction* mass crossing — the
Phase-0 mechanism — is therefore **not naturally achievable** (pilot 57001: the strong-feed branch stayed
~5.4 mass units above the gentle branch throughout relaxation; no crossing).

The design therefore matches **total dose** between two histories that differ only in **delivery
pattern**, so the clones reach a **common-clock coincidence** (equal core mass at the same absolute time)
by construction, and the scientific question becomes whether the *overt panel* also coincides while the
*hidden memory* differs:

- `H_SPIKE = [(0.060, 40), (0.0, 120)]` — brief strong spike then rest (dose 2.40);
- `H_SUSTAINED = [(0.015, 160)]` — gentle sustained feed (dose 2.40);
- then the frozen 1000-step deep turnover (`M ≤ 0.25`), then a 180-step no-drive relaxation;
- coincidence read at the frozen common-clock relaxation step `k = 90` (robustness `k ∈ {60,90,120}`).

The gentle stage stays within the parent drive support `[0.005, 0.035]`; the brief spike (0.060) exceeds
it and is declared explicitly. Calibration/analysis clone separation and determinism are in
`KOVACS_HIDDEN_STATE_00_PHASE1_CALIBRATION_SPEC.md`; the schedule is a single global-frozen family (no
per-world outcome-dependent tuning) and is hashed before any coincidence analysis.

## 2. Overt physical panel (tracker-free, frozen common core mask)

All variables are computed on the frozen radius-10 core mask centred at the pre-history checkpoint focal
centroid — **identical for both clones** and requiring no per-step tracking: `core_mass`, `core_support`
(occupied cells), `core_rg2` (2nd spatial moment), `core_centroid_off`, `core_N`, `core_c`,
`core_uptake`, `collar_mass`, `collar_N`. Memory (`m1,m2,m_plus,m_minus`) is recorded **only** as the
hidden residual diagnostic and is never part of the matching panel.

## 3. Mechanical tolerances (not from any excursion)

Per the Phase-1 rule, tolerances come only from (i) the **identical-history sham** — two clones with the
*same* history give bit-identical panels, so the sham residual is numerically **0**; and (ii) **natural
DEV temporal repeatability** — the panel's step-window standard deviation during relaxation. The frozen
gate uses `tolerance_v = max(1e-9, 3 · median_repeatability_v)`. No excursion size enters.

## 4. Results (17 complete DEV worlds; `KOVACS_HIDDEN_STATE_00_PHASE1_COINCIDENCE_ANALYSIS.json`)

Determinism: **bit-identical replay proven** (independent re-clones reproduce the post-relaxation state
hash exactly). Coincidence topology: **no opposite-direction crossing** in any world — both branches
relax in the same direction; the coincidence is dose-matched common-clock (this directly answers Task 4:
opposite-direction crossing is *not* achievable post-turnover).

**Full overt-panel coincidence qualification: `0/17` worlds** — under BOTH the sham tolerance (0) and the
3σ-repeatability tolerance. Per-variable pass fractions (3σ-repeatability):

| panel variable | median residual | median repeatability | 3σ tol | frac worlds passing |
|---|---:|---:|---:|---:|
| core_mass | 0.304 | 0.047 | 0.140 | 0.235 |
| core_support | 1.0 | 0.452 | 1.355 | 0.706 |
| core_rg2 | 0.217 | 0.010 | 0.030 | 0.118 |
| core_centroid_off | 0.025 | 0.001 | 0.002 | 0.000 |
| core_N | 0.433 | 0.021 | 0.063 | 0.000 |
| core_c | 0.492 | 0.157 | 0.470 | 0.471 |
| core_uptake | 0.0004 | 0.0001 | 0.0002 | 0.118 |
| collar_mass | 0.080 | 0.010 | 0.030 | 0.118 |
| collar_N | 0.147 | 0.008 | 0.023 | 0.000 |

Every world fails the *full* panel; the residuals are **systematic** (not noise): the spike branch is
consistently lighter/smaller/less-energetic than the sustained branch at matched dose (delivery
efficiency differs), so the overt macrostate genuinely differs by ~1–2 % relative — small, but ~10× the
natural repeatability and above the identical-history sham (0).

**Hidden memory residual (diagnostic, not matched):** the *slow* memory carries a consistent residual
while the *fast* memory is matched:

| memory readout | mean Δ (spike−sustained) | sign consistency | \|mean\|/cross-world-SD |
|---|---:|---:|---:|
| m1_mean (fast) | +0.00006 | 13/4 | 0.34 (noise) |
| m2_mean (slow) | −0.0160 | **0/17 (all −)** | 4.96 |
| m_plus_mean | −0.0147 | **0/17 (all −)** | 4.62 |
| m_minus_mean | +0.0149 | **17/0 (all +)** | 4.71 |

This is the timescale-separation signature: at the common-clock coincidence the fast field has washed out
(matched) while the slow field retains the delivery-pattern history (~4× the order-axis effect of the
parent line). It is a **real residual hidden DOF** — but see §6.

## 5. Frozen value gate → verdict

The frozen decision logic (`KOVACS_HIDDEN_STATE_00_PHASE1_VALUE_GATE.md`) requires, for
`STRONG_KOVACS_FEASIBLE`, that a sufficient fraction of worlds pass the **full** overt physical
coincidence panel under a common/frozen protocol. Here `0/17` pass at a mechanically-defensible
tolerance. Core mass approximately matches (~1–2 %) but the overt area/shape/energy/nutrient panel does
not coincide to tolerance. Therefore:

- not `STRONG_KOVACS_FEASIBLE` (full panel fails);
- not `MATCHING_INVALID` (matching used no future info, no surgery, no regression; clock time is common
  by construction; determinism proven);
- not `FEASIBILITY_FAIL` in the "cannot approach coincidence" sense — the protocol reaches a *close*
  (~1–2 %) coincidence, just not to tolerance;
- the honest class is **`SCALAR_ONLY_FEASIBLE`**: scalar mass matches, but overt panel residuals remain
  above mechanical tolerance and are the limitation → **`STOP_PROSPECTIVE`**.

## 6. Why the memory residual does not upgrade the verdict

Per the mission's explicit guardrail — *do not upgrade `SCALAR_ONLY_FEASIBLE` merely because non-mass
variables differ; their difference is the limitation, not positive evidence* — the consistent slow-memory
residual cannot rescue the claim. More decisively, the overt residual is itself **systematic and
standardized-consistent** (core_N |mean|/SD = 3.85, collar_N = 3.71, comparable to the memory channels'
~4.6–5.0): the delivery pattern leaves a coherent overt physical difference, not just a hidden one.
Because the overt macrostate is not matched to mechanical tolerance, a future divergence could not be
attributed to hidden state rather than to the ~1–2 % overt residual **without a pre-outcome margin we
cannot establish** (establishing it would require excursion sizes, which are forbidden). Claiming
equivalence here would violate "never claim equivalence without a pre-outcome scientific margin."

## 7. Claim-classification table (frozen, Phase-1)

| class | condition | reached? |
|---|---|:--:|
| STRONG_KOVACS_FEASIBLE | ≥ frozen fraction of worlds pass the FULL overt panel at mechanical tolerance under a frozen protocol | no (0/17) |
| SCALAR_ONLY_FEASIBLE | scalar mass ~matches but overt panel residuals remain above tolerance (the limitation) | **YES** |
| MATCHING_INVALID | matching depends on future info / selection / surgery / regression / uncontrolled clock time | no |
| FEASIBILITY_FAIL | frozen protocol cannot even approach coincidence in enough worlds | no |
| UNRESOLVED | evidence insufficient to select a protocol | no |

## 8. What a future STRONG design would require (not authorised here)

A defensible STRONG configuration would need the overt panel matched to sham/numerical tolerance while a
hidden field differs — which the natural dynamics do not provide, because the same history difference
that writes the hidden residual also writes a coherent overt residual (no free lunch without surgery,
which is forbidden). The only overt-coincident natural axis is the parent's **order** axis (same dose,
early-vs-late), whose overt residual is smaller but whose hidden residual is ~4× smaller still and was
already found non-functional for the one downstream readout tested — i.e. an even weaker margin, and it is
the stopped line. No natural, surgery-free route to a strong margin was found.

## 9. Firewall & integrity

No post-release excursion / Kovacs hump was computed, plotted, or inspected (enforced structurally and by
test). No new seed namespace; only already-open DEV worlds 57001–57024 were run. No body surgery, field
transplantation, regression residualization, decoder battery, or outcome-selected matching variable. `n`
= original source world. V5 / 03G / DIRECTED-CAUSAL-PAIR / 58xxx untouched; shared indexes not edited.
