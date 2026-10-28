# AUTO-20261028-0300-PRMERGES — journal

role: agent `claude` (Claude Code cloud session), integrator of test-only and
documentation-only pull requests under the owner's consent of 2026-10-28

run ID: `AUTO-20261028-0300-PRMERGES`

start/end: 2026-10-28 03:00Z / 2026-10-28 04:08Z; part 1 covers PRs #38 and #37, part 2
(below) PR #36

starting Git state: `main` at `f382dbf077699aa65c80328b6519035d1cda4a57`; open test-only or
documentation-only pull requests #38 (`auto/fix-stage-b-sampled-frames`), #37
(`auto/test-status`) and #36 (`auto/roadmap`)

ending Git state of part 1: `main` at `8c08e9c` (merge of #38); `auto/test-status` tip
holds a merge of `8c08e9c` (`bb5afba`) and the corrections below, for merge as #37 (merged as
`eb663c9`)

ending Git state of part 2: `main` at `eb663c9` (merge of #37); `auto/roadmap` tip holds a
merge of `eb663c9` (`9c93545`), the `ROADMAP.md` corrections and this part, for merge as #36

assigned scope: merge the open test-only and documentation-only pull requests in a safe
order after checking each one, and correct the factual errors found while checking. No code,
data, parameter, experiment, decision or scientific result changes.

## Authority

The repository owner asked on 2026-10-28, in the Claude Code session that ran this work, for
the open pull requests to be merged ("fusionner les PR ... t'as mon accord"). Pull requests
#31 to #35 carry scientific content or need the owner's review; they were not merged and not
modified.

## Lock

`AGENTS.md` requires the scheduled-run lock before a scheduled run changes files. This run is
not a heartbeat run and works in an ephemeral cloud clone, not in the owner's working copy,
so a lock taken here would protect nothing; it was not acquired. All writes go through
GitHub: a concurrent heartbeat push to `main` would be rejected as non-fast-forward, not
overwritten.

## Actions

1. Read `AGENTS.md`, `docs/RUN_INDEX.md`, and the diffs of #36, #37 and #38, including their
   journals, before merging #38. `docs/RESEARCH_CHARTER.md`, the top of
   `docs/PROJECT_STATE.md`, the end of `docs/DECISION_LOG.md` and `docs/EXPERIMENT_INDEX.md`
   were read only after the #38 merge, out of the required order; none bears on a test-only
   change.
2. PR #38: ran `tests/test_lattice_bond_stage_b.py` on `main` (`f382dbf`): 4 failed,
   28 passed; on the pull-request head (`41438ee`): 32 passed. Merged with a merge commit:
   `8c08e9c`, 2026-10-28 03:21:51Z.
3. Ran the complete suite on `8c08e9c`, with and without SciPy (commands below).
4. PR #37: merged `8c08e9c` into `auto/test-status` (`bb5afba`), resolving the
   `docs/RUN_INDEX.md` conflict by keeping both rows, newest first.
5. Corrected `docs/TEST_STATUS.md`: it said the 12 node IDs "match" the 2026-10-03 baseline
   of PR #36, but that baseline names only one of them by node ID (see Errata). Added the
   `8c08e9c` results and marked the Stage-B repair done.
6. Added this journal and one `docs/RUN_INDEX.md` row.

Important files read: those in action 1, `docs/TEST_STATUS.md`, `ROADMAP.md` (PR #36),
`pyproject.toml`, `tests/test_lattice_bond_stage_b.py`.

Changed: `docs/TEST_STATUS.md`, `docs/RUN_INDEX.md`, this journal. No code, data, experiment,
state, decision, parameter or scientific result changed.

## Reproducible commands

Environment: Linux, Python 3.11.17, numpy 2.4.6, scipy 1.15.3, pytest 8.4.2, matplotlib
3.11.2, complete checkout.

```bash
python3.11 -m venv /tmp/edlab-prmerges
/tmp/edlab-prmerges/bin/python -m pip install -e '.[dev]' 'scipy==1.15.3'
PYTHONPYCACHEPREFIX=/tmp/edlab-pycache-prmerges \
  /tmp/edlab-prmerges/bin/python -m pytest -q -p no:cacheprovider
```

Without SciPy, the same commands with `pip install -e '.[dev]'` only.

## OBSERVED

- `f382dbf`, Stage-B module: 4 failed, 28 passed. `41438ee` (#38 head): 32 passed.
- `8c08e9c`, complete suite with SciPy: **1,487 passed, 8 failed, 22 skipped** (153.7 s).
  The failing node IDs are items 1–2 and 7–12 of `docs/TEST_STATUS.md`. The seven Route E
  tests receive `configuration_error` ("no verifier supplied; PRB-6 requires a maintained
  verifier and there is no default, no fallback and no callback"); the scramble test raises
  "support overlaps its own translate: displacement would not conserve mass".
- The four Stage-B node IDs (items 3–6) pass when run by name: 4 passed.
- `8c08e9c` without SciPy (`pip install -e '.[dev]'` only; `scipy` absent from the venv):
  **1,472 passed, 23 failed, 22 skipped** (247.8 s). The 23 failing node IDs are the eight
  above plus 15 in `tests/test_scaffold.py` (7), `tests/test_multistable_phenotype.py` (5),
  `tests/test_chemotaxis.py` (2) and `tests/test_motile_polar.py` (1). Reruns by node ID with
  `--tb=line` in the same venv: the 15 fail with `ModuleNotFoundError: No module named
  'scipy'`, raised at `edlab/substrates/chemotaxis/diagnostics.py:55` (14) and
  `edlab/substrates/motile_polar/observables.py:47` (1). Of the eight, the seven Route E tests
  fail with `configuration_error` as above, and the scramble test fails with the same
  `ModuleNotFoundError` at `observables.py:47` instead of the conservation message. Sixteen of
  the 23 failures are therefore SciPy import errors.
- No Python, YAML or TOML file in the repository mentions `RUN_INDEX`, `agent_journals`,
  `TEST_STATUS` or `ROADMAP`, so these documentation files cannot change a test result.

## INFERRED

Taking the `f382dbf` record in `docs/TEST_STATUS.md` (1,483 passed, 12 failed) as the
reference, #38 removed exactly the four API-drift failures: the non-skipped total is
unchanged (1,495), and the other eight keep their node IDs and messages. The no-SciPy count
fell by the same four, from the 27 recorded at `f382dbf` to 23.

## HYPOTHESIS

The remaining eight failures have two independent causes: a pinned maintained verifier would
clear the seven Route E failures, and a disjoint, predeclared motile-polar geometry would
clear the scramble failure.

## WHAT WOULD FALSIFY THIS?

- A rerun at `8c08e9c` in the stated environment gives other counts or another failing set.
- One of the eight passes with no verifier or fixture change (flakiness or a hidden
  environment dependence).
- A valid pinned verifier leaves one of the seven Route E failures unchanged.

## Errata to other journals (not rewritten)

- `docs/agent_journals/2026-10-07/1834_test-status_AUTO-20261007-1834-TESTSTATUS.md`,
  OBSERVED: "The same 12 were recorded on 2026-10-03." The 2026-10-03 record (PR #36,
  `ROADMAP.md` §4) gives the same count, the same distribution by test module and the same
  messages, but names only the scramble test by node ID. "The same 12" is consistent with it,
  not established node by node.

## Failures and dead ends

- The first no-SciPy wording, pushed in `f1e97af`, read "the eight above plus 15 tests that
  raise `ModuleNotFoundError`", which implied 15 SciPy import errors. Rerunning the eight
  without SciPy showed 16, because the scramble test also fails at the import; corrected in
  the next commit of `auto/test-status`.

## Decisions

- Merge commits only; no rebase, no force-push; branch updates are fast-forward pushes.
- #37 is merged although the suite is red: it changes documentation only, cannot change a
  test result (see OBSERVED), and makes the failure list visible on `main`. The test-status
  agent's own "do not self-merge" decision concerned its authority; this merge rests on the
  owner's consent.
- Another agent's journal is never edited; corrections are recorded here.

## Unresolved risks

- `.github/workflows/nasi-ci.yml` does not run the suite, so `main` stays red (8 failures)
  with no CI signal.
- The Stage-B comparison and the complete runs used one editable install, made from the
  `8c08e9c` checkout. Production code is identical in all compared commits (#37 and #38
  change tests and documentation only), so the code under test was the same.

## Handoff (part 1)

Continued in part 2.

# Part 2: PR #36 (`auto/roadmap`)

## Actions

7. Checked the history facts in `ROADMAP.md` §6, and the H1 facts in §4, against Git and the
   GitHub API (commands below).
8. Corrected `ROADMAP.md` (`79850e1`, `87d286e`): the root commit and PR #11 in §6; H2 marked
   done by #38 and the H3 status at `8c08e9c` in §4; a dated correction note under the
   snapshot line; "the current `main`" in the merges table now reads "`main` at this
   snapshot".
9. Merged #37 with a merge commit after `nasi-ci` passed on `857226a`: `eb663c9`.
10. Merged `main` (`eb663c9`) into `auto/roadmap` (`9c93545`), resolving the
    `docs/RUN_INDEX.md` conflict by keeping all rows, newest first.
11. Wrote this part and set this run's `docs/RUN_INDEX.md` row to its final state.
12. Ran the complete suite on `c81ea31`, the pull-request head after action 11, with the
    part 1 commands from the `auto/roadmap` checkout (`edlab` imported from it), and listed
    the files that name `docs/RUN_INDEX.md` (commands below).

Changed in part 2: `ROADMAP.md`, `docs/RUN_INDEX.md`, this journal. No code, data,
experiment, state, decision, parameter or scientific result changed.

## Commands (part 2)

```bash
git rev-parse --is-shallow-repository          # false: complete history
git rev-list --max-parents=0 main
git log -1 --format='%h parents=%p %ad %s' --date=short b473ded
git log -1 --format='%h parents=%p %ad %s' --date=short d0f47b6
git show 5fa941b --stat --format= | grep DECISION_LOG
git log --first-parent --merges --format='%h %s' main | grep -E '#1[12]\b'
git merge-base --is-ancestor 44d91f0 6a958c6 && echo ancestor
git log -1 --format='%h %cI %s' 6a958c6
grep -rn --include=*.py -E '^\s*(import scipy|from scipy)' edlab
grep -n -i scipy requirements-lock.txt pyproject.toml
git grep -l RUN_INDEX -- ':!docs' ':!*.md'      # no output
git grep -l RUN_INDEX -- 'docs/individuation/*.json'
git grep -n 'docs/RUN_INDEX.md": "' -- 'docs/individuation/*.json'
git show HEAD:docs/RUN_INDEX.md | sha256sum
for f in $(git grep -l RUN_INDEX -- 'docs/individuation/*.json'); do
  git grep -l -F "$(basename "$f")" -- ':!docs'
done
grep -n -A15 'SOURCE_HASH_PATHS = ' edlab/substrates/lattice_bond/stage_b.py
```

PR #11 metadata: GitHub REST API, `GET /repos/Mythmaker28/emergent-dynamics-lab/pulls/11`.
The complete suite: the part 1 commands, run from this checkout. The two runs were compared
with `grep '^FAILED'` and `grep '^E '` on their outputs, after
`sed -E 's/0x[0-9a-f]+/0xADDR/g'` masked memory addresses.

## OBSERVED (part 2)

- The clone is complete (not shallow). `main` has a single root commit, `5fa941b` ("feat:
  establish falsifiable CORE V0 laboratory"), authored and committed on 2026-07-10. It adds
  `docs/DECISION_LOG.md` with D-001 to D-006, dated 2026-07-10.
- `b473ded` (2026-07-14, the CRD-03 freeze) has parent `68635f0`; `d0f47b6` (2026-07-15) has
  parent `a07b95b`. Neither is a root commit.
- PR #11 (API): `merged: true`, `merged_at` 2026-07-18T20:40:54Z, head `44d91f0`, base
  `88f9540`. No first-parent merge on `main` names #11; `44d91f0` is an ancestor of
  `6a958c6`, the merge of #12, committed at 2026-07-18T20:40:53Z, one second before that
  `merged_at`.
- `scipy` is imported at `edlab/substrates/chemotaxis/diagnostics.py:55`,
  `edlab/substrates/motile_polar/observables.py:47` and `edlab/experiments/sc_hsi/core.py:10`
  (the last at module level), pinned as `scipy==1.15.3` in `requirements-lock.txt`, and not
  mentioned in `pyproject.toml`, as `ROADMAP.md` H1 states.
- The roadmap journal records, on `f382dbf`, 1,468 passed, 27 failed and 22 skipped without
  SciPy, 16 of them SciPy import errors (`test_scaffold` 7, `test_multistable_phenotype` 5,
  `test_chemotaxis` 2, `test_motile_polar` 2), and 1,483 / 12 / 22 with it. Part 1 found the
  same 16 by module on `8c08e9c`.
- `c81ea31`, complete suite with SciPy, part 1 environment: **1,487 passed, 8 failed,
  22 skipped** (260.0 s). The eight failing node IDs are those of `8c08e9c`, and the 29 `E`
  lines of their failure reports are identical once memory addresses are masked.
- Outside `docs/`, no file other than Markdown names `RUN_INDEX`. Under
  `docs/individuation/`, seven JSON records name `docs/RUN_INDEX.md`: six source allowlists
  and `CAUSAL_ADDRESSABILITY_ARCHITECTURE_01_STAGE_A_QUALIFICATION.json`. Four allowlists
  give it a SHA-256 (`bac0b0fe…`, `92f55555…`, `2d8b8fc2…`, `f3e856d8…`); none equals that of
  the file at `c81ea31` (`f9c605dd…`).
- Outside `docs/`, three files name one of the seven records, and no test file does:
  `edlab/substrates/lattice_bond/stage_b.py` lists
  `INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_SOURCE_ALLOWLIST.json` in `SOURCE_HASH_PATHS`, the
  exact set of files whose manifest hashes it checks, which does not contain
  `docs/RUN_INDEX.md`; the two `analysis/interventional_individuality_stage_b_autopsy*.py`
  scripts read `INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_AUTOPSY_SOURCE_ALLOWLIST.json`.

## INFERRED (part 2)

Between `f382dbf` and `8c08e9c` only the four Stage-B outcomes changed, in both
environments; #38 did not touch the SciPy failures.

GitHub marked #11 merged when the merge of #12, which contains its head, reached `main`; the
two times differ by one second. `ROADMAP.md` §6 gives this as the reason.

## HYPOTHESIS (part 2)

None new. The `ROADMAP.md` corrections rest on the observations and the inference above.

## WHAT WOULD FALSIFY THIS? (part 2)

- A second root commit in a complete clone of `main`.
- A merge commit for #11 on the first-parent history of `main`, or `44d91f0` not reachable
  from `6a958c6`.
- A timeline of #11 that records its merge by another route than the push of `6a958c6`.

## Errata to other journals (part 2, not rewritten)

- `docs/agent_journals/2026-10-03/1615_roadmap_AUTO-20261003-1615-ROADMAP.md`, OBSERVED:
  "PR #11 is not among the merges into `main`. The Git history starts on 2026-07-14;
  `docs/DECISION_LOG.md` starts on 2026-07-10." The history starts on 2026-07-10, with the
  root commit that creates the log. #11 has no merge commit of its own, but its head is in
  `main` through the merge of #12, and GitHub records #11 as merged.
- Same journal, "Failures and dead ends": "the first decisions predate the history". They do
  not: D-001 to D-006 are in the root commit, of the same date. The other reason it gives,
  several PRs sharing a branch, was not checked here.

## Errata to part 1 (not rewritten)

- OBSERVED, last bullet: the search covered Python, YAML and TOML files only, and seven JSON
  records name `docs/RUN_INDEX.md` (OBSERVED, part 2), so the search alone does not show that
  these documentation files cannot change a test result. The direct check is the complete
  suite: the same counts and the same eight failures on `8c08e9c` and on `c81ea31`, which
  contains #37 and the #36 changes. The part 1 decision on #37 cites that bullet; its
  conclusion holds on this direct check.

## Decisions (part 2)

- `ROADMAP.md` keeps its 2026-10-03 snapshot: only facts found wrong and the status of the
  two hygiene steps touched by #38 were changed, and the change is dated in the file.
- `docs/PROJECT_STATE.md`, `docs/EXPERIMENT_INDEX.md` and `docs/DECISION_LOG.md` are not
  updated (end-of-run steps 5 to 7): no project state, experiment or decision changed. No
  experiment is active.

## Unresolved risks (part 2)

- The other claims of `ROADMAP.md` (its sections 1 to 3 and 5, the decision table, and the
  remaining hygiene steps) were not re-checked in this run.
- `docs/PROJECT_STATE.md` is still stale (ROADMAP H7); updating it records owner decisions and
  is left to the owner.

## Handoff

Run tests: the complete suite on `c81ea31`, with SciPy: 1,487 passed, 8 failed, 22 skipped,
the same eight failures as on `8c08e9c` (OBSERVED, part 2).

Next authorized action: ROADMAP §4 H1, which is also `docs/TEST_STATUS.md` repair step 4.
It is a packaging change with no scientific content, within the owner's consent of 2026-10-28
("t'as mon accord ... j'ai juste envie que ça fonctionne"). Declare `scipy` in `pyproject.toml` so
that a fresh `pip install -e '.[dev]'` installs it, using the `requirements-lock.txt` pin
(`scipy==1.15.3`) as the reference. Then rerun the complete suite in a fresh venv: the expected
result is 1,487 passed, 8 failed, 22 skipped, as recorded with SciPy at `8c08e9c`. It does not
cover the seven verifier failures or the motile-polar fixture, which need the owner (H3).
