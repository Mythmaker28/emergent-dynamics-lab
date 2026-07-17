# Agent journal — COUNTERFACTUAL-HISTORY-CORE-00 DEV exact-clone factorial

- **Role:** independent scientific auditor and exact-clone counterfactual intervention engineer
- **Run ID:** `RUN-20260717-1451-COUNTERFACTUAL-HISTORY-CORE-00`
- **Start:** 2026-07-17 14:51:46 +02:00
- **End:** 2026-07-17 20:36:43 +02:00
- **Starting Git state:** clean isolated branch `claude/counterfactual-history-core-00-dev` at exact accepted parent
  `4ef4bed0ee43a8d6edaec2b597e205eeb2393327`
- **Ending Git state:** coherent final result committed and pushed on
  `claude/counterfactual-history-core-00-dev`; working tree clean at handoff
- **Scheduled-run lock:** not applicable; direct human-authorized bounded DEV mission
- **Authorization boundary:** one fresh DEV-only family of at most 24 original worlds; no prospective or confirmation
  seed, no V5/03G reinterpretation, no main merge, and no reconstruction/division/heredity work

## Assigned scope

Design, freeze, validate, and execute a single-target exact-clone four-history factorial that estimates dose, temporal
order, and their interaction after deep turnover, with ordinary coupled and qualified isolated continuations. Treat
the original source world as the only statistical unit and stop after DEV for human review.

## Important files read

- Repository operating contract and durable state chain through the accepted BALANCED-HISTORY-ISOLATION-00 result.
- Attached COUNTERFACTUAL-HISTORY-CORE-00 mission.
- Statistical-analysis skill instructions.

## Actions and reproducible commands

- Created the isolated branch/worktree at the exact accepted parent and left the prior worktree and dirty main
  checkout untouched.
- Read the full operating-contract chain, latest BALANCED-HISTORY-ISOLATION-00 journal, manifest, report and machine
  summary before implementation.
- Audited simulator continuation state: the persistent Markov state is the eight physics arrays plus absolute
  `IOMState.step`; the feed scheduler is a pure function of `step`; engine steps retain no RNG and draw no randomness.
- Audited namespace candidate 57001–57024 with negative alphanumeric/dot decimal-literal boundaries in the working
  tree, histories reachable from all valid local/origin heads, all live remote heads, commit messages and recovered
  malformed-ref commit `c8a8b35`; no decimal seed literal occurred. Hash substrings were not treated as decimal
  namespace use. The malformed ref was preserved.
- Froze the manifest, protocol, unsealed preregistration draft, runner and 15 focused gates. Manifest SHA-256:
  `298dcc02d391eb8952d3d293fdaf1bcd9ceef2c032d8e521771ee50cce569457`.
- Selected a fixed 1000-step post-history turnover assessment as a round pre-data margin above the already-open
  DEV deep range 793–890. This fixes elapsed time across histories and permits one common no-drive boundary source.
- Before-data validation on already-open DEV seed 50002 only:

  ```powershell
  $py='C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe'
  & $py -m py_compile experiments\individuation\counterfactual_history_core_dev.py `
    experiments\individuation\test_counterfactual_history_core_dev.py
  & $py -m pytest experiments\individuation\test_counterfactual_history_core_dev.py -q
  # 15 passed in 63.90s
  ```

- A full already-open-seed integration smoke then produced one eligible, exact-clone-valid, four-history-complete
  source world with all four fixed-step deep checks and probes valid. It was a technical smoke only; its scientific
  contrasts were not inspected or used to change the frozen design.
- Committed and pushed the exact before-data freeze as
  `e504288da2b0f2c58d9f3e1fe9914ebb574ab2eb` before seed 57001.
- Executed the one bounded DEV family:

  ```powershell
  $py='C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe'
  & $py -m experiments.individuation.counterfactual_history_core_dev `
    --manifest docs\individuation\COUNTERFACTUAL_HISTORY_CORE_00_MANIFEST.json `
    --output docs\individuation\COUNTERFACTUAL_HISTORY_CORE_00_DEV_RESULTS.json
  ```

- The first process was interrupted after 15 atomically persisted worlds. The same command resumed from raw,
  explicitly skipped 57001-57015, initialized only 57016-57024, and completed exactly 24 unique source worlds.
- Implemented and ran an independent raw-only reproduction that imports neither runner nor engine:

  ```powershell
  & $py -m experiments.individuation.counterfactual_history_core_reproduce `
    --raw docs\individuation\COUNTERFACTUAL_HISTORY_CORE_00_DEV_RESULTS.json `
    --output docs\individuation\COUNTERFACTUAL_HISTORY_CORE_00_RAW_REPRODUCTION.json
  ```

- Raw DEV SHA-256: `d4e6f2d9cedcc8b459973e10641b1b28d91b3b52315cbba36120640ef9386da6`.
- Raw reproduction SHA-256: `d993ca08cafa9d567d4b78a1dc505ab25c18dff2598aeec8fbbe45e9ed479e73`.
- Wrote the DEV report, updated durable state/indexes, and recorded decision D-092.
- Final validation:

  ```powershell
  & $py -m py_compile experiments\individuation\counterfactual_history_core_dev.py `
    experiments\individuation\counterfactual_history_core_reproduce.py `
    experiments\individuation\test_counterfactual_history_core_dev.py `
    experiments\individuation\test_counterfactual_history_core_reproduce.py
  & $py -m pytest experiments\individuation\test_counterfactual_history_core_dev.py `
    experiments\individuation\test_counterfactual_history_core_reproduce.py `
    experiments\individuation\test_access_structure_noswap_operators.py `
    experiments\individuation\test_turnover_tracer.py -q
  # 30 passed in 93.88s
  & $py experiments\individuation\test_bijective_tracker.py
  # 10/10 checks PASS
  ```

  `git diff --check` reported no whitespace error; the raw audit confirmed `COMPLETE`, exact ordered unique seeds
  57001-57024, `NO_MEMORY_FIRST_STAGE`, and raw reproduction pass.

## OBSERVED

- Engine continuation is deterministic after seeded initialization; no hidden RNG or mutable scheduler exists
  outside `IOMState.step`. Clamp drivers alone have a cursor and every probe arm receives a fresh/reset driver.
- The existing descending-size/separation target rule yields three eligible tracker targets on open seed 50002;
  canonical spatial ordering makes target 0 focal without future information.
- Four clones from one serialization have identical deterministic bytes, tracker mappings and focal identity with
  zero fieldwise numerical error.
- Canonical and reversed history execution orders give identical label-specific states.
- The two-cell clamp with `up_ref=0` remains bit-exactly isolated, and the disabled clamp remains bit-identical to
  the ordinary frozen engine.
- All 24 source worlds were pre-history eligible; 17/24 supplied complete four-history deep/probe blocks. Seven
  were incomplete due to post-history or turnover tracker events. Failed potential outcomes were not imputed.
- All eligible worlds passed exact cloning. All complete worlds passed common-boundary, `up_ref=0`, sham and
  core-Mf-preservation gates. The paired survival-effect gate did not pass its frozen sign requirement.
- Coupled feeding dose was +0.18776 [0.05195, 0.32357]; isolated feeding dose was +0.17904
  [0.03878, 0.31930]. Order and interaction feeding intervals crossed zero.
- The targeted core `m_plus` dose first stage was +0.00040 [-0.00821, 0.00900] and failed. The targeted core
  `m_minus` EARLY-minus-LATE first stage was +0.00367 [0.00306, 0.00427], uniformly opposite the frozen negative
  direction; its sign was not flipped.
- Body mass, body radius, body size and multiple core/world physical baselines retained large dose/order effects.
  The positive feeding-dose contrast therefore cannot be attributed to the targeted memory coordinate.
- `lam_plus=0` did not produce a supported selective collapse. The raw-only reproduction passed every comparison,
  reproduced `NO_MEMORY_FIRST_STAGE`, and recorded `engine_initialized=false`.

## INFERRED

- Exact counterfactual branching removes the mechanical need for four simultaneous natural targets while retaining
  a paired 2x2 factorial inside each independent source world.
- A fixed elapsed turnover time is preferable to comparing history branches at different first-crossing ages; body,
  geometry, material M and global/physical baselines remain reported as possible causal pathways.
- Gaussian diffusion/spillover from the one focal intervention is a treatment consequence. No neighbour receives
  a separately assigned history in any branch.
- Exact-clone branching repaired mechanical feasibility, but it did not identify the targeted memory mechanism.
  Rich history-dependent state and a dose-linked causal feeding pathway may still exist through body or other
  physical state; `NO_MEMORY_FIRST_STAGE` must not be stated as absence of history dependence.

## HYPOTHESIS

The exact same pre-history Markov state may encode a dose-dependent and/or temporal-order-dependent local state
whose causal expression can be compared without between-target imbalance by assigning all four histories to exact
counterfactual clones of one focal target.

## WHAT WOULD FALSIFY THIS?

Failure of byte-identical cloning, focal identity, no-drive non-focal equivalence, execution-order invariance,
history semantics, deep survival/complete blocks, isolation, or endpoint validity would block a preregistration
candidate.

## Failures and dead ends

- Candidate 56001–56024 was rejected during namespace audit because decimal literal 56023 already occurs as a
  historical raw-index value. Candidate 57001–57024 passed the semantic decimal audit.
- An initially over-strict rule requiring separation from every size-eligible component and collar clearance from
  every small fragment yielded no focal target on open seed 50002. Before any fresh world and before the manifest
  freeze, this was corrected to the existing frozen descending-size greedy separated target set, followed by
  canonical tracker IDs and collar clearance among selected targets. No outcome or memory/feeding value was used.
- `test_bijective_tracker.py` executes ten checks and calls `sys.exit` at module import, so including it in a combined
  pytest collection produced an internal `SystemExit` after all ten checks passed. It was rerun through its intended
  standalone interface (10/10 pass); the remaining four pytest modules then passed 30/30.

## Decisions

- Exact accepted parent and prior DEV family 55001–55024 are preserved unchanged.
- A single pre-history focal target is selected before treatment; clones are counterfactual branches, not replicates.
- Accept the frozen `NO_MEMORY_FIRST_STAGE` decision. Do not relabel it `DOSE_ONLY` or `DOSE_AND_ORDER`, flip the
  order sign, select a secondary feature, or reinterpret the positive feeding-dose contrast as targeted memory.
- STOP this preregistration candidate. No prospective seed, seal or active-reconstruction work is authorized.

## Unresolved risks

- Complete-block feeding is based on 17/24 worlds and cannot answer what the failed potential outcomes would have
  produced. The frozen survival-effect gate passed neither its required common-sign count nor its full decision.
- The dose-feeding pathway remains scientifically unresolved because body and physical state differ by history.
- This DEV result does not authorize a prospective family or a new post-hoc mechanism search.

## Handoff

Human review `COUNTERFACTUAL_HISTORY_CORE_00_DEV_REPORT.md` and the raw-only reproduction. Exact next authorized
action: decide whether to stop the question or commission a fresh pre-data design that separates the targeted memory
coordinate from body/physical dose pathways. Do not open prospective seeds, seal the draft, merge main, modify
03G/V5, or start reconstruction/division/heredity.
