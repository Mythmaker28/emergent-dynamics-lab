# KOVACS-HIDDEN-STATE-00 — Phase-1 scientific-value gate (T5, frozen)

This decision logic was frozen before the coincidence analysis was applied; the applied outcome follows.

## Frozen decision logic

Let `q` = fraction of eligible DEV worlds that reach the core-mass target **and** pass the **full** overt
physical coincidence panel (every panel variable within its mechanical tolerance:
`tol_v = max(1e-9, 3·median natural repeatability_v)`; equivalently, indistinguishable from an
identical-history sham at numerical resolution). Tolerances derive only from sham/numerical resolution and
natural DEV repeatability — never from any excursion size.

- **`STRONG_KOVACS_FEASIBLE`** — `q ≥ 0.60` under a common or algorithmically-frozen protocol (a
  sufficient fraction of worlds reach a full overt-panel coincidence). Only this outcome permits
  specifying a future primary excursion estimand.
- **`SCALAR_ONLY_FEASIBLE`** — core mass matches but the overt area/shape/energy panel does not coincide
  to tolerance in enough worlds (major *or* systematic minor residuals remain). Supports at most "mass is
  not a sufficient macrostate"; **normally `STOP_PROSPECTIVE`** unless an independent scientific argument
  makes even that weak claim worth a prospective family.
- **`MATCHING_INVALID`** — matching depends on future-excursion information, matching-variable selection
  by predictive performance, surgery, field transplantation, regression residualization, or uncontrolled
  clock-time differences.
- **`FEASIBILITY_FAIL`** — the frozen protocol cannot produce enough coincidence-qualified worlds (cannot
  even approach coincidence).
- **`UNRESOLVED`** — validity holds but the evidence cannot select one defensible protocol.

**Guardrail (frozen):** `SCALAR_ONLY_FEASIBLE` is **not** upgraded merely because non-mass variables (or
memory) differ. Their difference is the *limitation*, not positive evidence. Equivalence is never claimed
without a pre-outcome scientific margin.

## Applied outcome

- `q = 0/17 = 0.00` full-overt-panel-qualified worlds, under both the sham (0) tolerance and the
  3σ-repeatability tolerance (`KOVACS_HIDDEN_STATE_00_PHASE1_COINCIDENCE_ANALYSIS.json`).
- Matching used no future information, no surgery, no regression; clock time is common by construction;
  determinism proven → **not** `MATCHING_INVALID`.
- The protocol reaches a *close* (~1–2 % relative) coincidence, so it is not a "cannot approach"
  `FEASIBILITY_FAIL`; but the residuals are **systematic** (spike consistently lighter/smaller/less
  energetic than sustained at matched dose) and above mechanical tolerance.
- The consistent slow-memory residual does **not** upgrade the class (guardrail), and the overt residual
  is itself standardized-consistent (core_N |mean|/SD 3.85, collar_N 3.71) — a coherent overt difference.

**→ `SCALAR_ONLY_FEASIBLE` → `STOP_PROSPECTIVE`.**

No independent scientific argument was found that would make "core-region mass is not a sufficient
macrostate" — already strongly indicated by the accepted physical-carryover result — worth a prospective
family: the only overt-coincident natural axis (the parent's order axis) has an even weaker hidden margin
and is the stopped line. Phase 1 therefore recommends **not** opening a prospective Kovacs family.
