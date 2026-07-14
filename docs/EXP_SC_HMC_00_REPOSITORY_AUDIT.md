# EXP-SC-HISTORY-MATERIAL-CONTINUITY-00 — REPOSITORY & PHYSICS AUDIT

## Git grounding (independent verification)
- `git status`/`git log`/`git fsck` run. Starting HEAD at handoff: `9326522`; during grounding two
  metrology commits appeared on `main` (`721690b` set-valued paper, `e17f431` CI/Docker repair) from an
  autonomous heartbeat run. Point-certification final `f4e776e` is present (origin/main lineage). fsck:
  only dangling objects (normal), no corruption.
- **Stale git index artefact found and neutralized:** a staged 345-file deletion (23,491 deletions) of
  the entire metrology programme was sitting in the index while the files still existed on disk. It was
  **not** committed (that would have destroyed historical certificates). Stale 0-byte `index.lock` and
  `HEAD.lock` (13–21 h old, crashed process) blocked normal index ops.
- **Environment constraints handled:** the working tree is a create-only FUSE mount (unlink/rm return
  EPERM; the stale locks cannot be removed from the sandbox). All work was therefore isolated on a new
  branch `exp/sc-history-material-continuity-00` (base `e17f431`), committed via lock-free git plumbing
  (alternate index in /tmp + `commit-tree` + direct ref write) so `main` and all history are untouched.
- The project runtime lock `RUN-20260712-EXPMO00` (EXP_MO_00, starting_head `17eba0f8`) is ~2 days
  orphaned; per its own conservative policy it was NOT cleared, and this experiment does not use the
  scheduled-run lock protocol (interactive execution on an isolated branch).

## Frozen droplet physics (verified, untouched)
`edlab/substrates/scaffold/engine.py` (blob `7c91b91`). State `(rho, U, V, c, N, C)`:
- rho — scaffold density (**material**); U, V — extensive internal species (U = rho·u), the internal
  bistable "identity" network; c — shared attractant (cohesion); N — nutrient; C — passive cohorts with
  `sum_c C == rho`; uptake — behavioural observable.
- Governing terms: chemotactic advection χ(c) with volume exclusion + rho diffusion D_rho; attractant
  c: D_c ∇² + s·rho − δ·c; nutrient N: D_N ∇² + F(N0 − N); growth/uptake g = dt·g0·rho·N·(1−rho/rho_max)
  ·(1 + **β**·σ), σ = (u−v)/(u+v); homogeneous death (1 − dt·k); internal bistable toggle
  du = a/(1+(v/K)²) − u, dv = a/(1+(u/K)²) − v with small internal diffusion **D_int = 0.008**.
- **β = 0.10** confirmed as the EXP-SC-00B prospectively-selected value (`BETA_SELECTED = 0.10`); the
  spec default is 0.6 and is overridden, not retuned.
- Material half-life ln2/(k·dt) = ln2/(0.02588·0.1) ≈ 268 steps ⇒ genuine turnover within the window.
- Cohort tracer is **dynamically passive** (never enters rho/U/V/c/N); verified empirically bit-identical.
- Entity masks/trackers: `detect()` is ID-free (rho threshold + periodic components); no tracker
  optimization on P or M (AGENTS.md invariant honoured).

## Frozen physics blob hashes (unchanged by this experiment)
- scaffold/engine.py `7c91b91` · scaffold/observables.py `196539e` · reaction_diffusion/engine.py `4e1c588`
- exp_sc_00.py `b1cd64d` · exp_sc_00b.py `d66da3c`

Sources compiled from disk under a fresh `PYTHONPYCACHEPREFIX`. Python 3.10.12, numpy 2.2.6, scipy 1.15.3.
