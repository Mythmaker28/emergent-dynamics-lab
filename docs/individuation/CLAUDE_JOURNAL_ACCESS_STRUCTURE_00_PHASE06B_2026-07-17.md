# Claude journal — ACCESS-STRUCTURE-00 Phase 0.6B (no-transplant) — 2026-07-17

Branch `claude/access-structure-noswap-design-06` off parent
`fa261734300631f16ca5e0bacceba11d5f7ddc1e`. Independent of the Phase-0.6A transplant repair (Codex). DEV-only; no
prospective seed; no history-A-vs-B feeding contrast computed.

## What I set out to do
Determine whether the ACCESS-STRUCTURE hypotheses (H_C, H_E, H_R, H_S, H_HALO, H_PHASE, H_G, H_0) can be
distinguished **without** grafting a foreign spatial state into a foreign environment, keeping the endpoint at future
feeding under a standardized probe. Explore three non-surgical trajectories, reject invalid designs, choose one
minimal design, and DEV-qualify a prototype without editing the transplant operator.

## Key facts established by independent inspection
- Real engine = `edlab/experiments/sc_mcm/engine.py` (`MultiChannelMemoryEngine`), not the `sc_iom` variant.
  `m_plus=tanh(m1+m2)→uptake` (`λ₊=0.25`), `m_minus=tanh(m1−m2)→attractant` (`λ₋=0.15`).
- **All spatial coupling is nearest-neighbour**; the only non-local term is the world-global scalar `up_ref`.
  Nutrient `N` replenishes locally (`F·(N0−N)`) and diffuses (`D_N=0.5`). State is Markov at arrays+`step`; no hidden
  buffers/RNG.
- DEV worlds 50001–50010 are seed-generated; deep-feasible = 50002@847, 50004@793, 50005@831, 50007@890.
  World/probe/tracker builders: `turnover_dev_diagnostics.to_S0`/`run_to`, `nonmerging_confirm.measure`,
  `bijective_tracker`.

## Decisions and why
- **Chose an in-place directional interface clamp** (Trajectory A/C intersection): hold a predeclared collar ring at
  an outcome-independent reference each step, severing the core from the environment’s history with a standardized,
  nutrient-matched boundary. This gives the Phase-0 2×2 (core-memory × environment-coupling) with **no transplant and
  no immediate core seam**. Implemented as `NoSwapClampEngine(DiagEngine)` — byte-identical when disabled — plus an
  in-place `standardize_core_memory` (varies only `Mf` on the core; body held fixed).
- **Two-cell barrier.** A one-cell overwrite is a topological separator for the one-cell stencil but leaks at ~1e-13
  once a front arrives; a two-cell barrier gives **bit-exact** isolation. Locked by a test.
- **Halo defined feeding-blind** by a perturbation influence-decay length (~4 cells, inside the radius-10 core) plus
  a static footprint; enclosed radii {6,10} fixed from this, not from feeding.
- **Honest scope.** H_E/H_R/H_S are only partially separable without transplant, because standardizing the core body
  inside the real environment is itself a transplant. Declared clean on H_C, H_HALO, H_G, H_0 (≥4).

## Rejected alternatives
Hard no-flux (Neumann) cut (reflection artefact); decoder-only; endpoint blocking; starvation-as-erasure;
correlation-as-storage; learned outcome-selected directions; inert-clamp tautology; hidden external controller;
temporal seam of equal severity; post-hoc individual redefinition. Details in the design §4.

## DEV feasibility (mechanics only) — `..._NOSWAP_RESULTS.json` sha256 `100ecb99…`
12 targets (4 worlds × 3). Bit-exact isolation `0.0` on 12/12; clamp-disabled == frozen engine bit-for-bit;
own-replay sham disturbance and temporal jump exactly 0; reference-clamp core disturbance ~1.87 (intended isolation,
common-mode in `τ_C`), barrier temporal jump max 1.81 / mean 0.09, **zero immediate core change**; disturbance
localizes at the barrier and penetrates the core only gradually (C 0.00→0.11 over 40 steps); memory standardization
changes only core `Mf` (non-target 0.0); all arms 40-step viable with uptake endpoint present; reference source
recipient-history-independent; existing `up_ref=0` and `λ₊=0` ablations valid; comoving halo decay radius 4. Full
rebuild and cached rerun are byte-identical.

## Validation
`test_access_structure_noswap_operators.py`: 9 passed. Existing regressions
(`test_access_structure_operators.py`, `test_turnover_tracer.py`): 13 passed. Determinism: RESULTS.json byte-identical
across rebuild and cache (`100ecb994718153d3e898b610a9b80b2c5ea74005d41493cd9cc0988fa6edee6`).

## Status / next
GO for the design mechanics on DEV, with a declared partial scientific scope. NOT sealed; no margins/probe/power/seed
frozen. Next authorized action: human review of the design + unsealed decision tree; the strategic reviewer
reconciles this no-swap line against the Phase-0.6A transplant repair. Stop after Phase 0.6B.

## File ownership
Created only new no-swap files: `experiments/individuation/access_structure_noswap_operators.py`,
`access_structure_noswap_dev_feasibility.py`, `test_access_structure_noswap_operators.py`, and
`docs/individuation/ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_{DESIGN.md,PREREG_DRAFT.md,RESULTS.json,RESULTS.sha256}` plus
this journal. Did not edit the transplant operator, the Phase-0.5 qualification, the prereg draft, any 0.6A/Codex
file, shared indexes, or certified results.
