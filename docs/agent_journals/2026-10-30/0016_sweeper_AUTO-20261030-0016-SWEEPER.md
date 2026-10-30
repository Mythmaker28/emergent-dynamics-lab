# AUTO-20261030-0016-SWEEPER — journal

role: agent `claude` (Claude Code cloud session), hygiene sweeper: proven bugs, tests,
documentation and reproducibility; no scientific content

run ID: `AUTO-20261030-0016-SWEEPER`

start/end: 2026-10-30 00:16Z (session start; lock acquired 00:25:07Z) / 00:51Z (journal
finalized; the commit, the suite on the pull-request head, the push, the draft pull request
and the lock release follow in that order)

starting Git state: `main` at `3e0e13b71c976d6dcf9602310084c908b8885541` (merge of PR #36),
clean working tree, shallow clone; branch `auto/sweeper-hygiene-20261030` created from it

ending Git state: `auto/sweeper-hygiene-20261030` = `3e0e13b` + `90cc652`, `c559c96`,
`165bcac`, `5e4aa51`, `0929831` and the commit that adds this journal; pushed for one draft
pull request to `main`, not merged

assigned scope: a scheduled task attributed to the repository owner ("Session crédit Sweeper
— backlog"): at most 8 useful, safe and verifiable tasks (fix a proven bug, add tests, repair
documentation or links, improve reproducibility) taken from `ROADMAP.md`, open issues or
defects found while reading; one commit per task, one draft pull request, no merge.
Results, numbers, claims and scientific conclusions are flagged, never changed. No paid API
call, no computation over 15 minutes outside the test suite, no secret, no release or
publication, no change to settings, scheduled tasks or GitHub Actions.

## Authority

The task text arrived as a scheduled instruction attributed to the owner. It was treated as
an assigned task, not as consent to merge: nothing was merged and no pull request other than
the draft opened by this run was modified.

## Lock

Acquired in this ephemeral clone before the first file change:
`python -m edlab.runtime_lock acquire --run-id AUTO-20261030-0016-SWEEPER --task-identity
emergent-dynamics-lab-sweeper-credit --starting-head 3e0e13b71c976d6dcf9602310084c908b8885541
--experiment NONE` (no lock existed). As the 2026-10-28 journal notes, a lock in a cloud
clone does not protect the owner's working copy. Released with the same run ID at the end.

## Actions

1. Read `AGENTS.md` first, then `docs/RESEARCH_CHARTER.md`, `ROADMAP.md`, `README.md`,
   `docs/PROJECT_STATE.md` (lines 1–120 and 631–694, all headings), `docs/RUN_INDEX.md`, the
   2026-10-28 journal, `docs/TEST_STATUS.md`, `docs/DECISION_LOG.md` (lines 215–254 and the
   D-021 entry) and `docs/EXPERIMENT_INDEX.md` (headings and lines 1–60). This is not exactly
   the order `AGENTS.md` gives. The manifest and summary of the last experiment were not read:
   no experiment was touched.
2. Ran the complete suite on `main` (`3e0e13b`) as the baseline.
3. Task 1, `90cc652` (test only): two tests drive `edlab.runtime_lock.main` as `AGENTS.md`
   invokes it (JSON output and exit 0; exit 2 on refusals; lock bytes unchanged).
4. Task 2, `c559c96` (proven bug): an existing but empty, truncated, non-UTF-8 or non-object
   lock file made `acquire`, `status` and `release` exit 1 with a `JSONDecodeError`
   traceback instead of the `SKIPPED_DUE_TO_ACTIVE_RUN` report. `read_lock` now raises
   `UnreadableLockError` (a subclass of `ActiveRunError`); the file is never modified or
   deleted.
5. Task 3, `165bcac` (`ROADMAP.md` H5): `README.md` says the pipeline it describes is the
   `CORE V0` substrate retired by D-021, points to the state files, and gives POSIX
   commands; both command blocks install `scipy==1.15.3`.
6. Task 4, `5e4aa51` (`ROADMAP.md` H8): the six rows after the `docs/RUN_INDEX.md` table were
   moved into it with their cell text unchanged, and a note above the table says so.
7. Task 5, `0929831` (proven bug): `_git_scope_clean` in `edlab/cli.py` read the source path
   of a rename or copy in `git status --porcelain=v1 -z` output as an entry and cut its first
   three characters. It now reads that field as the source path and requires both paths to
   lie inside the output directory.
8. Looked for further tasks and stopped at five (see Decisions).
9. Ran the complete suite on `0929831` in a detached worktree, then added this journal and
   one `docs/RUN_INDEX.md` row.
10. After the commit that adds this journal: the complete suite on the pull-request head,
    then push and draft pull request. The exact result on that head is in the pull-request
    description, not here, since this journal is part of that head.

Important files changed: `tests/test_runtime_lock.py`, `edlab/runtime_lock.py`,
`README.md`, `docs/RUN_INDEX.md`, `edlab/cli.py`, `tests/test_cli_git_scope.py` (new), this
journal. No data, result, manifest, experiment, state file (`docs/PROJECT_STATE.md`,
`docs/EXPERIMENT_INDEX.md`, `docs/DECISION_LOG.md`), parameter or scientific conclusion
changed.

Active experiment: none (`--experiment NONE`); this run produced no experiment output to
index.

## Reproducible commands

Environment: Linux, Python 3.11.17, numpy 2.4.6, scipy 1.15.3, pytest 8.4.2, matplotlib
3.11.2, black 24.10.0, git 2.43.0. The README check used Python 3.13.17 and a fresh venv.

```bash
python3.11 -m venv /tmp/edlab-venv
/tmp/edlab-venv/bin/python -m pip install -e '.[dev]' 'scipy==1.15.3' 'black==24.10.0'
PYTHONPYCACHEPREFIX=/tmp/edlab-pycache /tmp/edlab-venv/bin/python -m pytest -q -p no:cacheprovider
/tmp/edlab-venv/bin/python -m pytest -q -p no:cacheprovider tests/test_runtime_lock.py tests/test_cli_git_scope.py
/tmp/edlab-venv/bin/python -m black --check edlab/runtime_lock.py edlab/cli.py tests/test_runtime_lock.py tests/test_cli_git_scope.py
# fail-before checks: put back the previous module, run its test file, restore
git show 90cc652:edlab/runtime_lock.py > edlab/runtime_lock.py   # task 2: 10 failed
git show 5e4aa51:edlab/cli.py > edlab/cli.py                     # task 5: 4 failed, 3 passed
git checkout -- edlab/
# README (task 3): the five POSIX commands of README.md, one per line, in a clean worktree
# RUN_INDEX (task 4): no table row with other than 9 cells; prints nothing
awk -F'|' '/^\| / && NF != 11' docs/RUN_INDEX.md
```

## OBSERVED

- Baseline, `3e0e13b`: 8 failed, 1487 passed, 22 skipped in 184.81 s. The 8 node IDs are those
  of `docs/TEST_STATUS.md`: `test_round_03_a_neighbouring_round_is_refused_even_if_well_formed`
  `[-1]` and `[1]` (`tests/test_future_route_e_pre_run_integration_00.py`),
  `test_scramble_preserves_all_declared_invariants_and_destroys_organization`
  (`tests/test_motile_polar.py`), `test_outcome_06_a_response_that_does_not_match_the_pin_is_invalid`
  `[mutation0]` to `[mutation3]` and `test_outcome_07_unknown_or_missing_response_keys_are_invalid`
  (`tests/test_route_e_beacon_verifier.py`).
- Task 2, before the fix: on an empty and on a truncated lock file, `acquire`, `status` and
  `release` exited 1 with a traceback; the file was left in place. The 10 new parametrised
  cases fail 10/10 on the previous module; `tests/test_runtime_lock.py` passes 13/13 with the
  fix.
- Task 3: the five POSIX commands at `c559c96`, Python 3.13.17: venv exit 0, pip exit 0,
  pytest exit 1 (8 failed, 1499 passed, 22 skipped in 188.80 s, the same 8 node IDs as the
  baseline), `validate-forces` exit 0 (`"passed": true`), `nulls` exit 0. The PowerShell block
  was not run.
- Task 4: 83 table lines, each with 9 cells; a script checked that every cell of the six old
  rows is a substring of its new row.
- Task 5, `git status --porcelain=v1 --untracked-files=all -z` (git 2.43.0, global and system
  configuration ignored): staged rename `R  out/b\0out/a\0`; worktree rename of an
  intent-to-add file ` R out/b\0out/a\0`; copy with `status.renames=copies` and a modified
  source `M  out/a\0C  out/b\0out/a\0`; rename from outside `R  out/x\0tmpout/x\0`. The
  previous `_git_scope_clean(out)` returned False, False, False and True; the fixed one
  returns True, True, True and False. `tests/test_cli_git_scope.py`: 4 failed and 3 passed on
  the previous `edlab/cli.py`, 7 passed with the fix.
- The four `results/EXP02-COREV0-20260710-001/` artefacts that carry the flag
  (`manifest.json`, `stream_plan.json`, `analysis/analysis_manifest.json`,
  `analysis/exp02_analysis_summary.json`) record `true` and keep no status output.
- Complete suite on `0929831` (detached worktree, 00:44:42Z to 00:47:47Z): 8 failed, 1506
  passed, 22 skipped in 183.76 s. The sorted lists of failing node IDs of this run and of the
  baseline are identical (`diff` prints nothing). `tests/test_runtime_lock.py` and
  `tests/test_cli_git_scope.py` collect 20 tests; at `3e0e13b` the first file had one and the
  second did not exist, so 19 tests are new and 1487 + 19 = 1506.
- No open issue. Open pull requests: #31, #32, #33, #34 (draft), #35 and #39.
- No broken relative link in the 491 Markdown files outside `docs/agent_journals/`; the scan's
  two hits are a formula in an indented block of `docs/CRD02_PROTOCOL.md`.
- `black --check` passes on the four Python files changed.

## INFERRED

- Task 2: `AGENTS.md` tells a scheduled run to act on `SKIPPED_DUE_TO_ACTIVE_RUN`; a traceback
  gave it nothing to act on. An empty lock file is reachable: a concurrent acquirer sees it
  between the `O_EXCL` create and the JSON write, and a holder killed in that window leaves
  it. Whether a heartbeat ever hit this is unknown.
- Task 5: the false refusal hits any rename or copy whose source lies inside the output
  directory. The false clean needs a source path that, minus its first three characters,
  lies inside the output directory, a narrow case.
- Expected suite count: 1487 + 12 (tasks 1 and 2) + 7 (task 5) = 1506 passed, with the same
  8 failures and 22 skips.

## HYPOTHESIS

- The EXP02 `git_scope_clean: true` records were not produced in the false-clean state. The
  artefacts cannot show it either way.
- The PowerShell block of `README.md` works as the POSIX block does.

## WHAT WOULD FALSIFY THIS?

- A git version whose `-z` output orders a rename's paths differently, or adds a second path
  field to an entry without `R` or `C` in `XY`: `tests/test_cli_git_scope.py` would fail with
  it.
- A record of a staged rename into `results/EXP02-COREV0-20260710-001/` from a path of that
  shape when EXP02 ran.
- The PowerShell block failing on a Windows host.
- A failure on the pull-request head other than the 8 node IDs above.

## Failures and dead ends

- `black` reformatted a long `git -c ...` argument list in the new test; replaced by
  `git config` calls in the fixture.
- The first self-check of the RUN_INDEX script required the separator row to start with
  `"| "`; corrected before the script was used.
- A rewrite of `README.md` dropped its final blank line; restored.

## Decisions

No project decision; `docs/DECISION_LOG.md` is unchanged.

- Stopped after five tasks: no open issue; the remaining hygiene steps need the owner (H3,
  H4, H6, H7) or are in an open pull request (H1, #39); `AGENTS.md`: "Do not invent a
  direction merely to keep the automation busy."
- Flagged, not changed: the end of `docs/EXPERIMENT_INDEX.md` (a repair needs a table header
  the file does not define) and the stale `docs/PROJECT_STATE.md` (H7 waits on the owner's
  pilot decision).
- H5 and H8 are not marked done in `ROADMAP.md` §4 before a merge.

## Unresolved risks

- The 8 known failures remain (H3); CI does not run `pytest tests/` (H4), so the new tests
  run only locally.
- The description of PR #39 announces a second commit (journal, RUN_INDEX row,
  `docs/TEST_STATUS.md`, `ROADMAP.md`); the pull request has one commit that changes one
  file.
- `docs/RUN_INDEX.md` is newest-first at the top, while the six moved rows at the bottom are
  oldest-first; left as found.
- `docs/EXPERIMENT_INDEX.md`: the two 3-column rows (A1R4 and A1R5, "NOT AN EXPERIMENT")
  follow the EXP-GT-03 paragraph with no blank line and no header, so they do not render as
  a table; the pilot readiness entry is a bullet.
- H6: the research question quoted in `README.md`, the charter's "Current substrate and
  causal ladder" and the "Authorized sequence" of `AGENTS.md` still describe the CORE V0
  line.
- The clone is shallow: historical commits cited by older journals were not checked.

## Handoff

Next authorized action: the owner reviews the draft pull request from
`auto/sweeper-hygiene-20261030`. After a merge, record H5 and H8 as done in `ROADMAP.md` §4
with the merge commit, as was done for H2. No research step is authorized by this run; the
next research step remains the owner's decision in `ROADMAP.md` §3.
