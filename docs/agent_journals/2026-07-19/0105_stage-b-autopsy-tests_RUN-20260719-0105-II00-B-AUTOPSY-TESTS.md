# Stage-B autopsy synthetic-test journal

- Role: independent code-only synthetic test author and adversarial reviewer
- Run ID: `RUN-20260719-0105-II00-B-AUTOPSY-TESTS`
- Start: 2026-07-19 01:05 CEST
- End: 2026-07-19 01:58 CEST
- Assigned scope: create deterministic synthetic tests for the frozen Stage-B raw-autopsy reconstruction and analysis APIs; no scientific execution and no inspection of outcome-bearing raw.
- Starting checkpoint: `168b86c83db22999025b34a5e93aad299529037d`
- Starting branch: `codex/interventional-individuality-00-stage-b-autopsy`
- Starting Git state observed: checkpoint `168b86c`; the independent reproducer journal was untracked. The shared worktree changed concurrently during this role.
- Ending checkpoint: `168b86c83db22999025b34a5e93aad299529037d` (no commit made by this role)
- Ending Git state observed:
  - modified by other roles: reconstruction protocol and source allowlist;
  - untracked shared implementation/reproducer artefacts: primary analysis module, reproducer module, reproducer journal;
  - untracked files created by this role: synthetic test module and this journal.

## Evidence firewall and source discipline

Read only the repository operating contract and allowlisted code/design materials needed for static qualification: `AGENTS.md`, the research charter and project/index records, the frozen Stage-B autopsy analysis plan, reconstruction protocol, source allowlist, the primary/reproducer journals, and the primary analysis module as it appeared in the shared worktree.

No `physics.npz`, Stage-B scientific world, checkpoint, result file, source-world state, engine seed, or forbidden outcome-bearing artefact was opened. All arrays, components, tracks, archives, observation rows, and analysis worlds used by the tests were deterministic hand-built fixtures or temporary files created by pytest.

## Actions and files changed

Created:

- `analysis/test_interventional_individuality_stage_b_autopsy.py`
- `docs/agent_journals/2026-07-19/0105_stage-b-autopsy-tests_RUN-20260719-0105-II00-B-AUTOPSY-TESTS.md`

No other file was edited by this role. No commit was created.

The 50-test synthetic suite covers:

- closed NPZ inventory acceptance and rejection of traversal, nested/backslash names, duplicate members, missing/extra members, object dtype, structured dtype, and non-native dtype;
- periodic seam connectivity, false-winding exclusion, true winding, minimum-component removal, and deterministic component indexing;
- exact association ties and ambiguity retention;
- tracker allocation ordering before appearances, many-to-many ambiguity, merge/split collapse, and unresolved propagation;
- exact cohort identity when `q == m`, conservation, tolerance-admissible values without clipping, matter-identity rejection, and cohort-bound rejection;
- frozen prefix candidate boundaries, observed-frame counting, gap sensitivity, and unresolved-track exclusion;
- all frozen world-classifier precedence paths and candidate-ID output;
- all autopsy outcome branches and the `RAW_INSUFFICIENT` default;
- canonical finite sorted UTF-8 JSON and negative-zero normalization;
- same-track developmental anti-stitching, numeric co-primary ordering, deterministic candidate representative selection, and non-union/non-summing of multi-candidate episodes;
- terminal freeze gaps, strict freeze thresholds, inclusive persistent-active thresholds, explicit dissolution, empty suffixes, administrative censoring, and fail-closed pre-horizon termination;
- formation/no-episode null output;
- zero initial cohort denominator and zero diagnostic-baseline unavailability, including routing to `RAW_INSUFFICIENT`.

## Reproducible command and final result

```powershell
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m pytest -q analysis/test_interventional_individuality_stage_b_autopsy.py
```

Final result at 2026-07-19 01:58 CEST:

```text
..................................................                       [100%]
50 passed in 0.27s
```

## OBSERVED

1. The first focused suite run exposed an object-array payload whose NumPy `ValueError` escaped instead of being normalized to the audit's fail-closed `AuditError`.
2. A terminal low-throughput suffix containing a missing detector frame was initially accepted as a 32-observation freeze run even though the frozen protocol says gaps break freeze runs.
3. Co-primary and reporting-representative track fingerprints were initially sorted lexically. This incorrectly placed `0:100,101,102` before `0:20,21,22`, contrary to numeric `(onset frame, ascending row-major onset-support tuple)` ordering.
4. The developmental summary API was absent during the earliest interface audit and appeared during concurrent primary implementation.
5. The primary role corrected all four integration points during this shared run. The unchanged 50-test adversarial suite now passes completely.

## INFERRED

- The current code-only implementation satisfies the exercised deterministic contracts for malicious archive rejection, periodic geometry, ambiguity-preserving tracking, cohort transport, developmental aggregation, terminal windows, classifier precedence, outcome routing, and canonical serialization.
- Passing these fixtures is synthetic qualification only. It does not validate any scientific world, reconstruct a scientific outcome, change the immutable Stage-B disposition, or authorize retrospective interpretation.
- The zero-baseline tests confirm that unavailable diagnostic denominators remain unavailable and route to `RAW_INSUFFICIENT`; they are not treated as negative evidence or silently excluded.

## HYPOTHESIS

Given the final primary implementation and frozen reconstruction protocol, any further deterministic fixture that differs only by arm/order, dictionary insertion order, or equivalent numeric track-label presentation should preserve the same detector/tracker/developmental classification and canonical bytes.

## WHAT WOULD FALSIFY THIS?

- Any deterministic reordering of equivalent synthetic inputs changes selected tracks, co-primary ordering, candidate episode aggregation, classifier output, or canonical serialization.
- Any object, structured, non-native, duplicate, nested, traversal-bearing, missing, or extra NPZ member reaches numerical analysis rather than failing closed.
- A detector-frame gap contributes to a candidate or freeze run.
- Milestones from different tracks are combined into a higher developmental pathway.
- A nonpositive required baseline is scored false, discarded from its denominator, or allowed to support an actionable mechanism instead of becoming unavailable.
- A cohort fixture satisfying the exact matter identity is clipped or creates/removes unexplained mass.

## Failures and dead ends

- One local pytest invocation initially omitted PowerShell's call operator for the Python path containing a space; it did not execute pytest. The corrected quoted `&` invocation is recorded above.
- No scientific or raw-data fallback was attempted when APIs were temporarily absent or fixtures failed.

## Decisions

- Retained each adversarial fixture after it exposed a defect; no fixture was weakened to match implementation output.
- Used numeric onset-support ordering as frozen, not lexical fingerprint ordering.
- Treated detector-frame gaps as run breaks and zero/nonpositive baselines as diagnostic unavailability.
- Stopped at code-only synthetic qualification. No raw reproduction, scientific execution, candidate promotion, threshold revision, or outcome reinterpretation was performed.

## Unresolved risks

- These fixtures do not exercise the allowlisted scientific archives and therefore cannot establish raw byte identity, the 64-world/candidate-set gates, or primary-versus-reproducer output equality.
- The zero-baseline analysis fixture deliberately isolates diagnostic availability and is not a physically generated population; it proves routing semantics, not empirical prevalence.
- The worktree is shared and remains dirty with coherent concurrent implementation artefacts. Attribution must be preserved when staging and committing.

## Handoff

The independent code-only synthetic gate is green: **50/50 PASS** at checkpoint `168b86c` plus the current uncommitted implementation. The parent role may review and intentionally stage the test module and this journal with the coherent Stage-B autopsy implementation. Preserve the source firewall and immutable `DEV_FEASIBILITY_FAIL`; raw access, if still authorized by the parent mission, must occur only after the full synthetic gate and source-binding checks remain green.

## APPENDED BLOCKER-REGRESSION AND CROSS-IMPLEMENTATION PASS — 2026-07-19 02:05–02:17 CEST

This append-only continuation remained code-only. I reread the current primary analyzer, frozen plan/protocol/allowlist and latest independent red-team journal, then opened the independent reproducer source only after the parent explicitly requested a primary-versus-independent canonical parity fixture. No physics/raw shard, scientific result, checkpoint or outcome-bearing world was opened.

Checkpoint remained `168b86c83db22999025b34a5e93aad299529037d`; no commit was made by this role. Exact inspected hashes at the final rerun were:

| File | SHA-256 |
|---|---|
| primary analyzer | `a7b0b409fdb956a60d466c1f3e781dc81e230009231c0d667f6472ddd0b04a92` |
| independent reproducer | `471d6eb411e0647ded462143ea4bc325470e302d2c299d03f1b80b8ad1712cf6` |
| expanded synthetic tests | `b4f6278ad96e6133840cacfbbcc855c29fc5f933b248f4b9e2dae0a3934ce698` |
| frozen analysis plan | `2b43da9ccd2a8ddb2fa6abc3b6f9e57b559a4546c99acb4d0076129b04006739` |
| reconstruction protocol | `ab47ac077924f146197e27b26f8bb5fa42d691460d5d72c945687942b4e6bbd0` |
| source allowlist | `96111e100b744d86bee70b47e7912f9f0497c4fe3763a0b04404a1897727c14e` |

### Added deterministic fixtures

- the exact nine-dissolution-world/three-law qualifying-support counterexample, with two high-exchange worlds from an unqualified subtype on two extra laws;
- post-authentication path substitution using two valid, distinct synthetic 46-array NPZ byte strings;
- allowlist casefold/backslash normalization, `..`, dot, empty segment, absolute/drive path rejection, unauthorized-casefold rejection and symlink/reparse rejection when the OS permits link creation;
- a fully neutral valid 46-array numerical fixture plus nonfinite, replay, scale, exact-zero, vector/reference, transport, matter-residual and energy-residual kill switches;
- exact seven-payload-plus-`COMPLETE.json` publication, file size/hash inventory, final/partial no-overwrite, missing/extra payload rejection;
- closed-package validation for lying `COMPLETE` hashes and extra/missing package members, plus qualification no-overwrite;
- arbitrary normal-run and compare-only root rejection before analyzer execution;
- a pytest-version mismatch driven through the otherwise-satisfied runtime gate;
- incomplete/gapped and complete/nonqualifying compact precursor windows;
- a fabricated complete 8-law × 2-IC × 4-replicate population with 11 synthetic candidate worlds, used to compare primary and independent atlas/analysis canonical bytes without scientific raw;
- the exact observational-signature interpretation literal, including `; never causal and never changes DEV_FEASIBILITY_FAIL`.

### OBSERVED during concurrent repair

The expanded fixtures initially reproduced the red-team blockers: the destructive law span used support from an unqualified subtype; `process_world` lacked a post-authentication binding; `write_package` accepted incomplete or extra payloads; package comparison did not validate a closed `COMPLETE` inventory; pytest was reported without being checked; compact precursor gaps did not make bond/heterogeneity windows unavailable; and the independent interpretation literal omitted the frozen non-causal suffix.

The primary/independent roles repaired those points concurrently without this role changing either analyzer. At the final rerun, every one of those blocker fixtures passed. The real symlink fixture was skipped because Windows returned `WinError 1314` (the test account lacks link-creation privilege); the normalized traversal/casefold path fixtures still ran.

### Final focused command and disposition

```powershell
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m pytest -q analysis/test_interventional_individuality_stage_b_autopsy.py
```

Final result at 02:17 CEST:

```text
2 failed, 81 passed, 1 skipped in 0.92s
```

The two failures are both binding cross-implementation canonical-parity failures on the complete fabricated population:

1. `trajectory_atlas.json` parity: 55 structural differences were observed. The independent atlas omits zero-valued frozen enum entries from `regime_counts`, `pathway_counts` and `terminal_counts`; it also emits a `group` key under `formation_funnel.all_worlds` that the primary atlas omits.
2. `analysis.json` parity: 10 structural differences were observed. `candidate_duration.worlds` is a list of candidate rows in the primary and integer `11` in the independent output. `IC_FORMATION_DEPENDENCE` differs in numerator (`3` versus `11`), denominator (`8` versus `32`) and direction type/value (frozen string versus integer sign). `COMPACT_PREMATURE_FREEZE` denominator differs (`8` versus `32`). The earlier five interpretation-literal differences were corrected concurrently and their dedicated exact-literal test now passes.

### INFERRED

- The primary implementation now closes the recorded authentication, runtime, precursor, publication and mechanism-support blockers under synthetic attack.
- The independent implementation is not yet capable of the required byte-identical `analysis.json` and `trajectory_atlas.json` output on a complete synthetic population. This is a code-only parity defect, not a scientific outcome.
- The remaining differences are schema/estimand serialization differences and must not be waived merely because real Stage-B values might make some zero-count keys inconspicuous.

### WHAT WOULD FALSIFY THIS APPENDED FINDING?

- The unchanged fabricated 64-world fixture produces byte-identical primary and independent atlas/analysis objects after independent-side corrections, while all blocker regression fixtures remain green.
- An equivalent independent test demonstrates that each currently differing field has one frozen schema-consistent encoding and both implementations emit it canonically.

### Risks and handoff

- **Do not open raw.** The code-only suite is not green while the two canonical parity fixtures fail.
- Correct only the independent reproducer's frozen schema/estimand encodings; do not copy primary output bytes, inspect scientific outcomes, change thresholds, alter `DEV_FEASIBILITY_FAIL`, or weaken the parity fixtures.
- Rerun the complete focused suite. A pre-raw code gate requires all 84 collected cases to pass; an OS-level symlink fixture may remain skipped only if the Windows privilege limitation is explicitly retained and reparse-aware implementation is independently reviewed.
- Preserve attribution in the dirty shared worktree: this role edited only the synthetic test module and this journal.

## APPENDED FINAL CODE-ONLY CONFORMANCE — 2026-07-19 02:24 CEST

The independent reproducer was corrected against the frozen output vocabularies and estimands. I kept the aggregate parity fixtures unchanged and reran them before adding the final end-to-end fixtures. Both `analysis.json` and `trajectory_atlas.json` fabricated-population canonical parity are now green.

I then added two complete, valid, hand-built 46-array reconstruction fixtures and passed each independently through the primary and reproducer detector, tracker, passive-cohort observation, developmental aggregation and classification paths:

- an empty world, requiring `EMPTY_OR_GAS`, no observations/events and `trajectory_class = null`;
- a persistent stationary 3×3 component with exact neutral transport and matter ledgers, requiring `STATIC_CRYSTAL_OR_SHELL` and `ACTIVATION_FAILURE|FROZEN|early|SPLIT_MERGE=0|CENSORED=1`.

For both worlds, one canonical object containing classification, public world transition, complete track observations and event rows is byte-identical between implementations. The initial static-fixture expectation incorrectly named `TURNOVER_FAILURE`; because the hand-built fixture has zero activity and zero work, the frozen ordered pathway is correctly `ACTIVATION_FAILURE`. Only that test expectation was corrected; neither analyzer was edited by this role.

The optional real Windows symlink attempt remains in the suite but no longer produces a skip when the test account lacks link privilege. A deterministic mocked `FILE_ATTRIBUTE_REPARSE_POINT` (`0x400`) fixture now directly exercises the primary `_has_reparse_or_symlink` and source-firewall rejection path on every platform.

Final exact command:

```powershell
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m pytest -q analysis/test_interventional_individuality_stage_b_autopsy.py
```

Final result:

```text
........................................................................ [ 82%]
...............                                                          [100%]
87 passed in 1.01s
```

Final source hashes at that rerun:

| File | SHA-256 |
|---|---|
| primary analyzer | `15c9b1195cb197774335f9dc233391096071f6b039959948346d892ed8bbfbc8` |
| independent reproducer | `fe6e72aa18d9b540220f9f3aae185a6c0baae2da88d5b0b1835dba46c3879667` |
| focused synthetic tests | `9aa429f3c1955b94736a42eec8e41fa64550e3c6eeae3d750123cfa384d96dcd` |

### Final OBSERVED / INFERRED / HANDOFF

- OBSERVED: all 87 code-only synthetic tests pass with zero skips and zero expected failures.
- OBSERVED: aggregate analysis/atlas and end-to-end reconstruction structures are canonically byte-identical between primary and independent implementations on the frozen fabricated fixtures.
- INFERRED: the previously binding code-only blockers recorded in this journal are closed at the exact hashes above.
- WHAT WOULD FALSIFY THIS?: any source/control change, parity regression, output-inventory drift, authenticated-byte substitution, runtime mismatch, path bypass or numerical-gate failure on the unchanged fixtures.
- HANDOFF: parent may stage this test module and journal with the coherent code-only package. This result does not itself authorize raw access; the parent must still enforce the separately frozen control hashes, exact source checkpoint, absent publication roots and independent pre-raw review. `DEV_FEASIBILITY_FAIL` remains immutable.
- Physics/raw access throughout this role: **none**.
- Commit created by this role: **none**.
