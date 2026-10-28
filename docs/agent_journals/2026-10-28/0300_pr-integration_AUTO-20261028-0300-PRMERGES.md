# AUTO-20261028-0300-PRMERGES — journal

role: agent `claude` (Claude Code cloud session), integrator of test-only and
documentation-only pull requests under the owner's consent of 2026-10-28

run ID: `AUTO-20261028-0300-PRMERGES`

start/end: 2026-10-28 03:00Z / open; this part covers PRs #38 and #37, and the run
continues with PR #36

starting Git state: `main` at `f382dbf077699aa65c80328b6519035d1cda4a57`; open test-only or
documentation-only pull requests #38 (`auto/fix-stage-b-sampled-frames`), #37
(`auto/test-status`) and #36 (`auto/roadmap`)

ending Git state of this part: `main` at `8c08e9c` (merge of #38); `auto/test-status` tip
holds a merge of `8c08e9c` (`bb5afba`) and the corrections below, for merge as #37

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
  **1,472 passed, 23 failed, 22 skipped** (247.8 s). The 23 are the eight above plus 15 in
  `tests/test_scaffold.py` (7), `tests/test_multistable_phenotype.py` (5),
  `tests/test_chemotaxis.py` (2) and `tests/test_motile_polar.py` (1). Rerun of those 15 by
  node ID with `--tb=line`: 15 failed, all with `ModuleNotFoundError: No module named
  'scipy'`, raised at `edlab/substrates/chemotaxis/diagnostics.py:55` (14) and
  `edlab/substrates/motile_polar/observables.py:47` (1).
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

None in this part.

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

## Handoff

Continues in the PR #36 part of this run.
