# MCM01_APPEND_ONLY_CORRECTIONS

Append-only. Nothing in `MCM01_PREFREEZE_ANALYSIS_PLAN.md`, in `_freeze1.json`, or in any
artefact of MINCORE, MTW01 or this mission is edited. Each entry is dated, linked to the hash and
the commit it concerns, and carries its reason.

---

## C-1 — 2026-08-12T22:10Z — the pointwise form of the criticality gate is a specification defect

**Concerns** `MCM01_PREFREEZE_ANALYSIS_PLAN.md` section 6, `code/mcm.py::persistence_gate`,
frozen under `METHODS_CORE_HASH = 0ad009794f7297df289f8e28e65f8518135539a0013c6403eae0d49f7cfd2813`.

**What was frozen.** The persistence gate required *"fraction of steps with `c_X·G(0) > 1` ≥
0.90"*, i.e. the criticality condition applied **pointwise, step by step**.

**What the calibration data show.** `c_X = min(n[SX], free)` is a small non-negative **integer**
and it is strongly intermittent: across the eight calibration arms its median over the
measurement window is exactly **0**, its mean is 0.23 to 0.56, and it is at or above 1 in only
19 % to 40 % of steps. A pointwise criterion at threshold 1 is therefore not satisfiable by
construction for this observable, whatever the parameters.

**Why this is a defect and not a result.** Section 3 of the frozen plan derives the condition as
a statement about a **mean offspring number**: a lone body molecule triggers `c_X` births per step
for `G(0)` steps *in expectation*, so the quantity that must exceed 1 is `E[c_X]·G(0)`.
Transcribing it into a per-step test was an error of form, not a scientific choice. The frozen
selection rule (section 5), which uses a pooled `c_X` and not a per-step test, was **not**
affected.

**Effect on this mission's conclusion: none.** The decision was taken by the frozen selection
rule, and it was checked under both poolings: with the declared median pooling **0 of 4** points
survive, and with the mean as an alternative pooling **0 of 4** survive as well
(`out/_selection.json`). The conclusion is therefore invariant to the defect. Moreover the
persistence gate was **never executed on real data**, because the mission stopped at sequential
rule 3, before any confirmation arm.

**Correction carried forward, not applied retroactively.** Any future use of this gate must test
`mean(c_X over the window) · G(0) > 1` and report the pointwise fraction as a descriptive
intermittency statistic only. The frozen bytes of this mission are left exactly as they are.

```
STATUS = DEFECT_RECORDED__CONCLUSION_UNAFFECTED__FIX_DEFERRED_TO_THE_NEXT_MISSION
```

---

## C-2 — 2026-08-12T22:10Z — three claims inherited from MTW01 are corrected, not withdrawn

**Concerns** `MTW01/out/MINCORE_TIMESCALE_WINDOW_FINAL_REPORT.md`, commit `85ba2d8`, and
`MTW01/out/_window.json` (sha256 `3a1b7ae5…216342`). Those artefacts are **not** modified.

| MTW01 statement | correction, with the reason |
|---|---|
| `N_X ≤ S0/muX` presented as an exact bound | not exact. `_diffuse` accepts `min(movers, dest_free)`, capped by free capacity and not by `S0`, so a cell can hold more than `S0` resource units. The exact per-organiser bound is `N_X ≤ 7/muX` at `CAP = 16`. |
| `Q_max = 27` | 27 is reproduced only under the restriction `n[SY] ≤ S0`, which is unsound for the same reason. The exact maximum is **28**, at `nX = 7, nSY = 4, free = 4`. |
| `D = p_hop/4` | `_diffuse` applies four direction attempts per step, so a particle can move and move back within one step: `D_eff = q(1−q)`, `q = p_hop/4`. The error is −5 % at `p_hop = 0.2` and −25 % at `p_hop = 1`. |
| `G(0)` computed for the X walk alone | the organiser also moves and the source requires co-location with it, so the relative walk is the correct one. The X-only value overstates `G(0)` by 24 % at the MTW01 design point. |
| "the MTW01 cloud was subcritical or critical" | **the point was supercritical**: `c_X·G(0) = 2.53`. The maintenance condition was not what failed. What failed is that the quasi-stationary population was `N_X* = c_X/muX = 33.5` — predicted with no free parameter against the 35 recorded — beside an absorbing state. |
| `1519` versus `190` | the same quantity under two conventions for the separation time. `τ = Δ²/D_Y` gives 1518.6; the exact 2D first passage `τ = Δ²/(8·D_Y)` gives 189.8. The ratio is exactly **8.0000**. With the corrected `D_eff` the traceable final value is **180.4**. The conclusion (window empty at the frozen MINCORE point) is unaffected in every convention. |

None of these changes any MTW01 **disposition**. `WINDOW_NOT_CONFIRMED__FAILURE_NOT_ATTRIBUTABLE_TO_THE_HAZARD`
stands, and so does `H3 = 0` on all four MTW01 arms.

```
STATUS = INHERITED_CLAIMS_CORRECTED__DISPOSITIONS_UNCHANGED
```

---

## C-3 — 2026-08-12T22:10Z — what the MINCORE stop probably was, stated as a conjecture

`MINCORE/out/_pilot.json` records the stop `FIRST_SOURCE_CLUSTER_TOUCHES_WALL_OR_FILLS_DOMAIN`
with `support_cells = 439`, `N_X = 1186`, `N_Y = 1081`. The present mission establishes that the
same engine's feed rule drives total occupancy monotonically to `CAP·L²`. It is therefore
plausible that what MINCORE recorded as the cluster "filling the domain" was the lattice filling
with **resource**, not the cluster growing. The saved MINCORE outputs contain a single descriptor
and no time series, so this cannot be checked from them.

```
MINCORE_STOP_WAS_THE_SAME_RATCHET = CONJECTURE__NOT_CHECKABLE_FROM_THE_SAVED_OUTPUTS
```

This is the one point on which a bounded human observation would be worth more than a chain of
automated audits; it is raised in the final report under `TOMMY_ACTION_REQUIRED`.
