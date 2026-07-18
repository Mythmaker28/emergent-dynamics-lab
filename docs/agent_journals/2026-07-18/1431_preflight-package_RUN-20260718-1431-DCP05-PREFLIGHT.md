# Agent journal - DIRECTED-CAUSAL-PAIR-00 Phase 0.5 preflight/package audit

- Role: independent fail-before-engine binding and seedless-package auditor
- Run ID: `RUN-20260718-1431-DCP05-PREFLIGHT`
- Start time: 2026-07-18 14:31 CEST
- End time: 2026-07-18 14:40 CEST
- Starting Git state: clean branch `codex/directed-causal-pair-00-phase05` at recovery checkpoint
  `898b4595dec15e7d5277058d41697a618405bb99`
- Ending Git state: HEAD unchanged at `898b4595dec15e7d5277058d41697a618405bb99`; shared worktree contains this
  role's runner/test changes plus concurrent executor, mechanics, schema, reproducer, and integrator work
- Worktree: `C:\Users\tommy\Documents\ising-v3-directed-causal-pair-00-phase0`
- Runtime lock: not applicable; this was a direct recovery audit using synthetic/static checks only and initialized
  no world

## Assigned scope

Independently audit `directed_causal_pair_phase05_runner.py`, its focused mechanics tests, and the requirements for an
unsealed seedless prospective package if DEV mechanics qualifies. Patch only concrete runner/preflight defects and
existing focused mechanics tests. Do not execute a world, create the final DEV manifest, inspect a prospective
namespace, compute pair feeding `Y/C/I`, commit, push, or edit indexes/package documents.

## Operating-contract review

Read in the required order: `AGENTS.md`, `docs/RESEARCH_CHARTER.md`, `docs/PROJECT_STATE.md`,
`docs/DECISION_LOG.md` through D-091, `docs/EXPERIMENT_INDEX.md`, `docs/RUN_INDEX.md`, the latest journal
`0345_mechanics-tests_RUN-20260718-0345-DCP05-TEST.md`, and the current Phase-0 report/manifest-equivalent summary.
Also read the Phase-0 preregistration draft and inherited scientific-package journal
`0315_scientific-package_RUN-20260718-0315-DCP05-SCI.md`. No prospective or `58xxx` artefact was enumerated or
opened.

## Files changed by this role

- `experiments/individuation/directed_causal_pair_phase05_runner.py`
- `experiments/individuation/test_directed_causal_pair_phase05_mechanics.py`
- this unique journal

## Concrete preflight defects found and repaired

1. The manifest could live at any in-repository path. It is now accepted only at
   `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_DEV_MANIFEST.json`, before its bytes are read.
2. `code_commit` could be merely an ancestor of `HEAD`, while dirty tracked code could execute. It must now equal
   exact checked-out `HEAD`, and the tracked index/worktree must be clean.
3. Untracked namespace initializers could execute before the bound executor while evading tracked-file checks.
   Exact import-shadow paths for the namespace packages are now required absent without any directory-wide scan.
4. The exact code-binding set omitted 31 tracked local modules actually loaded by executor import, including package
   initializers and transitive engine/detector dependencies. They are now in `EXPECTED_CODE_PATHS`, and a runtime
   static-import test proves every loaded local source is hash-bound.
5. Normalized aliases such as backslashes or `./` were accepted for the output directory. The manifest must now
   contain the one exact POSIX path string.
6. The concurrent executor audit established that diagnostic switch detection must cover the sentinel and tracker
   lifecycle time must use monotonic simulator time, not a resetting stage counter. Added focused regressions for an
   A-to-sentinel switch and a `60 -> 1 -> 1` stage-step sequence with engine steps `101 -> 102 -> 103`.

The exact-24 fixture was made uniform-rho so it remains a literal boundary test under the now-consistent
rho-weighted centroid convention.

## Exact DEV manifest construction after the code is final

Do not construct the manifest before these steps are true:

1. Finish the schema/executor/reproducer/test integration, including
   `test_directed_causal_pair_phase05_reproduce.py`, and commit one code checkpoint.
2. Require that checkpoint to be exact `HEAD`, descended from accepted Phase-0 commit
   `4bcb551092291b7383c4168f653818d4bade14f6`, with no tracked index/worktree changes.
3. For every exact key in runner `EXPECTED_INPUT_PATHS`, record the current-file SHA-256 and the Git blob from
   `4bcb551092291b7383c4168f653818d4bade14f6:<path>`. Current bytes must equal that binding.
4. For every exact key in runner `EXPECTED_CODE_PATHS`, record the current-file SHA-256 and the Git blob from
   `<code_commit>:<path>`. Runner and reproducer binding sets must be identical.
5. Build exactly these top-level fields and no others: `schema`, `mission`, `mode`, `phase0_commit`, `code_commit`,
   `allowed_seed_namespace`, `worlds`, `pair_assignments`, `prospective_namespace`, `output_directory`,
   `input_files`, and `code_files`.
6. Freeze the values exactly: schema `DIRECTED-CAUSAL-PAIR-00-PHASE05-DEV-MANIFEST-v1`; mode
   `DEV_ONLY_MECHANICAL`; allowed namespace `50001..50010`; worlds `[50002,50004,50005,50007]`; the four accepted
   A/B/sentinel assignments; `prospective_namespace: null`; and output
   `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW`.
7. Serialize sorted compact UTF-8 JSON with `allow_nan=false` and exactly one final LF at the fixed manifest path.
   Keep it untracked through execution so `code_commit == HEAD` remains possible; commit manifest and raw only after
   the bounded run completes.
8. Call `validate_preflight` first. Only after it passes may the runner dynamically import the executor. Use
   `--resume` only for the same bound manifest and its exact ordered raw prefix.

No prospective namespace, seed, reserve, or seed stream is part of this DEV manifest.

## Minimal unsealed seedless prospective package

Create this package only if the engine-free reproduction reports a complete four-world prefix, all four worlds
mechanically complete, and outcome firewall pass. The package remains documentation-only and non-executable. Its
minimal fields are:

- identity/status: schema, mission, `UNSEALED_SEEDLESS_HUMAN_REVIEW_ONLY`, `executable:false`;
- provenance: Phase-0 commit, Phase-0.5 code commit, DEV manifest/raw-schema/COMPLETE/reproduction hashes, mechanical
  disposition;
- fixed scientific structure: original world as the sole unit; eligibility/pair/orientation rules; exact
  `H00/H10/H01/H11` and access regimes; unchanged writer, turnover, tracker, and common-probe schedules;
- primary estimand: world-level
  `Delta_IND = 0.5*((C_AA-C_BA)+(C_BB-C_AB))`, guarded by positive reciprocal `D_A` and `D_B` intersection-union
  rules;
- separately named secondary families: four directed entries, `C_AB-C_BA`, `I_A`, `I_B`, pair-total response,
  recipient-matched no-swap sensitivities, global sensitivities, shams, fixed-mask, sentinel, and mediator
  diagnostics;
- exclusive classifier order: `MANIPULATION_INVALID`, `UNRESOLVED`, `INDIVIDUATED_CAUSAL_ACCESS`, one of the three
  single-secondary labels, mixed-secondary `UNRESOLVED`, then `NO_INDIVIDUATION_ESTABLISHED`;
- multiplicity architecture: primary/secondary FWER partition, reciprocal intersection-union guard, one enumerated
  Holm-controlled secondary family, with all numeric alpha allocations still null;
- synthetic-only operating-characteristic plan and required scenario/stress grid, status `PENDING` until qualified;
- future scientific raw extension contract: recipient-labelled primitive A/B/sentinel probe observations plus
  mechanical/mediator/contamination series, but no stored derived `Y`, `C`, `I`, matrix, reader, or composite;
- explicit null/unsealed fields: prospective namespace, seed family, primary/reserve lists, hard cap, final powered
  minimum valid worlds, writer-stream binding, platform, environment lock, interval/test engine, positive/equivalence
  margins, numeric error allocation, final seal, authorization, and execution command;
- exact next action: human seal review only.

The historical value 18 may be recorded only as an inherited structural-floor reference, not frozen as completed
power for this matrix. No TOST/equivalence or absent-cross-access claim is permitted without a separately justified
pre-outcome margin.

## Reproducible commands and results

Baseline before editing:

```powershell
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m pytest -q `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py
# 36 passed in 1.32s
```

Final validation:

```powershell
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m py_compile `
  experiments/individuation/directed_causal_pair_phase05_runner.py `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py
# PASS

& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m pytest -q `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py
# 44 passed in 1.25s

git diff --check -- `
  experiments/individuation/directed_causal_pair_phase05_runner.py `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py
# PASS

# Standard-library comparison of the two exact binding sets:
# input_bindings_equal=True; code_bindings_equal=True
```

No world, engine constructor, DEV response, scientific analyzer, or prospective runner was invoked.

## OBSERVED

- Executor import loaded 31 local tracked sources absent from the checkpoint's exact binding map. The eager package
  import includes generic `edlab.experiments.analyze_streaming`; it is now bound, but is not called and computes no
  pair outcome.
- Exact `HEAD` plus tracked-clean state is necessary because a commit ancestor and selected file hashes do not bind
  all transitive import behavior.
- Namespace packages require an explicit absent-shadow guard because no tracked `__init__.py` exists at those two
  paths.
- At audit time the focused reproducer test file named in the exact binding set had not yet been created, so an
  executable manifest could not yet be validly constructed.
- Concurrent mechanics work reconciled rho-weighted centroids across executor raw masks/collars. The reproducer
  still required parity for those physical centroid primitives and sentinel-switch validation when handed off.

## INFERRED

- A valid manifest can be constructed mechanically only after the final code checkpoint; attempting it earlier
  either binds stale code or creates a self-inconsistent ancestry/cleanliness state.
- A seedless package can freeze algebra, classifier structure, and the list of future seal decisions without
  selecting or even naming a prospective seed family.
- Mechanical qualification cannot justify scientific effect sizes, variance, equivalence margins, sample size, or
  power. Those remain human-seal decisions supported only by synthetic operating characteristics and external
  pre-outcome justification.

## HYPOTHESIS

If the final reproducer accepts the exact raw prefix and the manifest is built only after a clean exact code
checkpoint using the steps above, then the four-world DEV disposition is mechanically bound and can support a
seedless human-review package without leaking pair feeding outcomes.

## WHAT WOULD FALSIFY THIS?

- Any malformed manifest path, binding, checkout, output alias, or import shadow reaching executor import.
- Any local source loaded by executor import absent from `EXPECTED_CODE_PATHS`.
- Any tracker role switch, including a sentinel switch, escaping `PAIR_IDENTITY_SWITCH`.
- Any tracker assignment/death timestamp following a reset stage counter instead of monotonic engine time.
- Any engine-free reproducer disagreement with rho-weighted geometry/raw primitives, hash chain, failure union, or
  complete-world classification.
- Any unsealed package containing a prospective namespace/seed, executable authorization, derived pair outcome,
  numeric scientific margin, or pseudoreplicated target/arm-level inference.

## Failures and dead ends

- The first post-hardening focused run had two failures because old exact-binding-set tests reached the new
  checkout-clean guard in a temporary non-Git directory. Mocking that unrelated guard restored the intended test
  isolation; the exact binding regression itself was unchanged.
- A concurrent rho-centroid improvement shifted the gradient-weighted exact-24 fixture to `23.9999109970751`.
  Uniform rho restored a literal 24-cell boundary fixture; mechanics was separately reconciled by the executor
  auditor.
- No executable manifest was made because the code commit and reproducer-test inventory were not final.

## Decisions

1. Bind the exact canonical manifest location, exact HEAD, clean tracked state, absent namespace shadows, strict
   output string, and complete current local import closure before executor import.
2. Keep future package choices explicitly null instead of inventing seeds, margins, platform, hard cap, or power.
3. Treat preferential target-specific access as the possible primary claim; do not require or claim off-diagonal
   equivalence.

## Unresolved risks

- Deep raw-prefix verification still occurs inside the executor after engine modules import but before the first
  world is built. If the final threat model requires a tampered resume prefix to cause zero engine-module imports,
  move the standard-library reproducer prefix check ahead of executor import.
- The generic eager analyzer import is bound and unused. A stricter no-analyzer-import policy would require making
  `edlab.experiments` initialization lazy before the code checkpoint.
- Final runner/reproducer binding equality must be rerun after the missing reproducer test and any last dependency
  changes are committed.
- The unsealed scientific package must not be created if the final mechanics or engine-free reproduction is
  incomplete/failed.

## Handoff

Runner and focused-test changes are ready: canonical manifest path, exact clean code checkout, import-shadow guard,
full local import-closure bindings, strict output string, sentinel-switch regression, and monotonic tracker-time
regression. Focused validation is 44/44 green.

Exact next action: finish reproducer centroid/sentinel parity and its missing focused test, rerun the integrated
static/synthetic suites, commit the final code checkpoint, then construct the DEV manifest exactly as above. Only a
mechanically complete engine-free reproduction may advance to the unsealed seedless human-review package.
