# Journal — EXP-SC-HISTORY-MATERIAL-CONTINUITY-00

- **Role:** primary scientific execution agent. **Run:** interactive (isolated branch; not under the
  scheduled-run lock protocol). **Start/End Git:** base `e17f431` → branch `exp/sc-history-material-continuity-00`.
- **Scope:** return to the grand question (history vs material continuity) on the FROZEN scaffold substrate.

## OBSERVED
- Frozen droplet physics = scaffold engine; state (rho,U,V,c,N,C); β=0.10; D_int=0.008; cohort C passive
  (bit-identical verified). Material half-life ≈ 268 steps → real turnover (M_tc mean 0.265, all < 0.35).
- Entity self-organizes, stable, perturbable by N/c, coexists at low occupancy. Phase 0 = SUBSTRATE_OK.
- Per-axis (n=12): only P2 internal state persists vs reset/scramble (1.00) but at chance vs unrelated
  (0.50); P1 shared by construction; P3/causal near chance. Individuation AUC: P2 0.65 (weak), causal 0.52.
- Predictive models A/B/C/D all worse than the mean baseline; history no advantage over snapshot.
- 11/12 dev gates pass; G10 (history signal) fails.

## INFERRED
- The one "persistence" is *evolved interior ≠ random reset*, NOT history individuation — the entity
  resembles its own past no more than an unrelated entity's past. Reproduces EXP-SC-00B/R8-B with sharper
  tools. Whatever persists is snapshot-readable ⇒ history is redundant for prediction.

## HYPOTHESIS / WHAT WOULD FALSIFY THIS
- H: in this substrate, organizational continuity is not causally load-bearing beyond the snapshot.
- Falsifier: a substrate with PINNED internal organization (declared in PROJECT_STATE) could show
  within << between individuation and a history predictive advantage. Requires NEW physics — out of scope.

## FAILURES / DEAD ENDS (environment)
- Create-only FUSE mount (unlink EPERM); stale git index.lock/HEAD.lock unclearable; background jobs do
  not survive isolated shells. Resolved via: lock-free git plumbing (alt index + commit-tree + ref write),
  resumable budget-bounded runner, and rewriting an Edit-mangled file via bash heredoc.

## DECISION
- VERDICT FAIL — SNAPSHOT SUFFICIENT. Prospective hold-out PRESERVED (G10 failed). No metrology
  experiment launched. SC-PILOT-CAUSAL-FINGERPRINT and EXP-SC-01 remain BLOCKED.

## HANDOFF / EXACT NEXT AUTHORIZED ACTION
- If pursued: preregister a PINNED-internal-organization substrate protocol (new physics) BEFORE any run;
  do NOT lower D_int after failure (forbidden). Prospective seeds 9501–9516 remain unburned.
