# Agent journal — DIRECTED-CAUSAL-PAIR-00 Phase 0.5 mechanics tests

- Role: independent synthetic-mechanics and fail-before-engine preflight test engineer
- Run ID: `RUN-20260718-0345-DCP05-TEST`
- Start time: 2026-07-18 03:45 CEST
- End time: 2026-07-18 04:02 CEST
- Starting Git state: branch `codex/directed-causal-pair-00-phase05` at
  `4bcb551092291b7383c4168f653818d4bade14f6`; shared worktree already contained concurrent untracked Phase-0.5
  implementation and three other agents' journals
- Ending Git state: HEAD unchanged at `4bcb551092291b7383c4168f653818d4bade14f6`; shared worktree remains uncommitted
  with concurrent Phase-0.5 files; this agent changed only the focused test file and this unique journal
- Worktree: `C:\Users\tommy\Documents\ising-v3-directed-causal-pair-00-phase0`
- Runtime lock: not applicable; this was a direct human-requested synthetic test task and launched no world

## Assigned scope

Create only `experiments/individuation/test_directed_causal_pair_phase05_mechanics.py` plus this journal. Test
periodic geometry, the independent separation/halo/contact gates, synthetic crossing/switch/fusion, passive logging,
tracker-label independence, deterministic encodings, recursive outcome firewall, exact DEV manifest types and
assignments, forbidden-namespace path refusal, ordered-prefix integrity, and standard-library preflight behavior.
Do not initialize a real world, inspect a forbidden namespace, import scientific analyzers, compute pair outcomes,
touch the primary checkout, or commit.

## Operating-contract and provenance review

Read in the required order:

1. `AGENTS.md`;
2. `docs/RESEARCH_CHARTER.md`;
3. `docs/PROJECT_STATE.md`;
4. `docs/DECISION_LOG.md` including D-091;
5. `docs/EXPERIMENT_INDEX.md`;
6. `docs/RUN_INDEX.md`;
7. latest journal at the time of work,
   `docs/agent_journals/2026-07-18/0315_firewall-schema_RUN-20260718-0315-DCP05-FW.md`;
8. `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_REPORT.md` and
   `DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json`.

Inspected the concurrent Phase-0.5 mechanics, runner, executor, reproducer, accepted tracker, no-swap operators,
state serialization, material tracer, and relevant earlier synthetic tests. No result directory was enumerated or
opened and no engine/world constructor was called.

## Files changed

- `experiments/individuation/test_directed_causal_pair_phase05_mechanics.py`
- `docs/agent_journals/2026-07-18/0345_mechanics-tests_RUN-20260718-0345-DCP05-TEST.md`

## Test coverage added

- periodic wraparound centroid/distance;
- exact 24 versus below 24, with the exact-24 lattice halo touch kept as an independent fail-closed gate;
- radius-12 halo overlap, four-neighbour contact, and periodic contact;
- separated-component crossing with reordered component enumeration;
- forced tracker-identity switch and synthetic physical fusion;
- logged versus unlogged synthetic `IOMState` identity over three deterministic updates;
- geometry invariance to external tracker-ID relabeling;
- canonical little-bit packed masks and deterministic gzip;
- nested, case-insensitive outcome-key rejection and non-overbroad physical-key acceptance;
- exact frozen worlds, A/B/sentinel assignments, order, duplicates, Boolean/string rejection;
- standard-library-only runner import closure;
- malformed preflight proving zero executor import and zero output-directory creation;
- exact input/code binding path sets and symlink/junction refusal before file opening;
- a synthetic forbidden-namespace decoy proving refusal before read;
- valid ordered prefix, hole, same-size shard tamper, declared-plan tamper, and path escape.

## Reproducible commands and results

Final commands:

```powershell
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m pytest -q `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py
# 36 passed in 1.14s

& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m py_compile `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py `
  experiments/individuation/directed_causal_pair_phase05_mechanics.py `
  experiments/individuation/directed_causal_pair_phase05_runner.py
# PASS

git diff --check -- experiments/individuation/test_directed_causal_pair_phase05_mechanics.py
# PASS
```

The isolated worktree has no `.venv`. The interpreter from the primary checkout was used read-only while the current
working directory and all imported source/cache paths remained in the isolated worktree.

## OBSERVED

- The passive observer left every persistent `IOMState` field and step bit-identical to an unlogged clone.
- Reordering detected components did not change track identity in a clean crossing. The continuous separation gate
  fired while tracker events remained empty.
- A forced identity switch emitted `PAIR_IDENTITY_SWITCH`; a fused component censored both pair tracks as `MERGED`.
- Exact distance 24 is not “below 24”, but inclusive radius-12 lattice masks touch there. The halo gate therefore
  independently rejects the fixture as intended.
- Packed masks and gzip were byte-identical across repeated generation.
- Recursive outcome-key checks reject nested and case-varied scientific names while allowing physical field `c` and
  ordinary mechanical identity labels.
- Initial tests found that `validate_ordered_prefix` ignored a tampered declared plan and accepted a root escape.
  The integrating agent hardened the helper; both regressions now pass.
- Initial API review found transient mechanics/reproducer key-shape mismatches and a self-rejected reproducer status
  key. These were reported immediately; a dedicated reproducer agent was reconciling them concurrently.
- Runner preflight initially resolved paths before checking links and permitted arbitrary nonempty binding maps.
  The integrating agent added unresolved-path symlink/junction checks and exact frozen input/code path sets; focused
  regressions now pass. Real symlink creation lacked Windows privilege, so the fallback exercises the same branch
  with `_is_link_or_junction` mocked true and proves no read occurs.
- The accepted no-swap geometry rounds floating centroids to integer grid centers before making disks. The concurrent
  reproducer initially used unrounded continuous centers; this convention mismatch was reported for reconciliation.
- The executor can legitimately emit incomplete arm payloads after a mechanical failure, while the concurrent
  reproducer initially required all pass-only sections. This failure-path contract gap was reported; an explicit
  failure union was being implemented.
- For the combined no-swap plus `up_ref=0` sham gap, the integrating agent chose to keep the frozen eight regimes
  and strengthen exact-isolation evidence: compare the unperturbed own-replay/`up_ref=0` full-state hash at all 80
  steps against the persisted free `UP_REF_ZERO` trajectory. That implementation still requires final verification.

## INFERRED

- Continuous centroid separation and discrete halo overlap must remain separate gates; one cannot stand in for the
  other at the exact boundary.
- Synthetic masks and state fixtures are sufficient to test observer passivity, correspondence failure semantics,
  path guards, and persistence integrity without using any development outcome.
- Fail-before-engine protection is materially stronger when exact path sets, canonical manifest bytes, ancestry,
  and unresolved link checks all precede dynamic import.
- A raw reproducer must validate both pass and fail shards; otherwise a legitimate mechanical failure cannot be
  independently classified without inventing missing values.

## HYPOTHESIS

If the final integrated runner preserves these contracts and the engine-free reproducer validates the final raw
shape, then a mechanical qualification disposition can be reproduced without exposing or conditioning on pair
feeding outcomes.

## WHAT WOULD FALSIFY THIS?

- Any logged synthetic continuation differing from its unlogged clone.
- Any crossing, switch, merge, contact, below-24, or halo-touch fixture escaping its declared gate.
- Any diagnostic/tracker relabel changing geometry.
- Any nested forbidden outcome key reaching canonical output.
- Any malformed manifest importing the executor or creating output.
- Any forbidden-namespace decoy being opened or read.
- Any hole, plan mutation, shard tamper, or path escape accepted as a valid prefix.
- Any final raw failure shard that the standard-library reproducer cannot validate deterministically.

## Failures and dead ends

- `\.\.venv\Scripts\python.exe` does not exist in the isolated worktree. System Python compiled the files but lacked
  pytest. The existing project environment was then used as the read-only interpreter.
- First focused run: 31 pass, 2 fail. Both failures were genuine ordered-prefix contract defects, not fixture errors;
  after the integrating repair, 33 passed.
- New exact-path tests first wrote noncanonical JSON and therefore correctly stopped at the newly added canonical
  manifest gate. The fixture was corrected to compact sorted JSON with one LF.
- The code-path parametrization next reached missing synthetic input files before the code-path-set assertion. Its
  unrelated filesystem/hash helpers were isolated with mocks so the test now targets the exact set contract.
- Windows denied real symlink creation with WinError 1314. The fallback uses a regular decoy plus a mocked positive
  link detector; it still proves refusal occurs before `read_bytes`.

## Decisions

1. Keep all tests synthetic and outcome-blind; do not use an already-open DEV world merely for convenience.
2. Treat exact-24 distance and discrete halo touch as two independently asserted facts.
3. Encode ordered-prefix plan/path integrity as required behavior rather than documenting the initial defects.
4. Test the runner's import closure statically and its invalid preflight dynamically without invoking `main` or an
   executor.
5. Do not freeze tests against transient reproducer object-key sets while the dedicated agent is reconciling them.

## Unresolved risks

- The final runner/reproducer/schema changed concurrently after this agent began. The complete integrated suite must
  be rerun after those files and the final manifest are frozen.
- The combined-cut full-state own-replay comparison was selected during handoff but had not yet been rerun when this
  journal closed; final integrated tests/raw must prove all 80 hashes match.
- These tests prove logger passivity on exact synthetic `IOMState` fixtures, not full engine trajectory equivalence;
  the full integration validation remains required.
- No real Windows junction was created in this test run; the implementation checks `Path.is_junction` when available,
  but an environment-level junction fixture would be stronger.

## Handoff

Focused mechanics/preflight tests are ready and pass 36/36. Rerun this file after final runner/reproducer/schema
integration, then run the full mission-required suites. Do not classify the package mechanically qualified until the
engine-free reproducer accepts the final raw contract, including a legitimate failure-path payload.

Exact next action: freeze the final manifest/schema/reproducer shapes, rerun this focused file unchanged, and resolve
the combined-cut 80-step full-state replay evidence before executing any DEV world.
