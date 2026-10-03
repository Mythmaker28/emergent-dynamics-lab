# AUTO-20261003-1615-ROADMAP — journal

role: auto-backlog agent `claude`, roadmap writer, documentation only
run ID: `AUTO-20261003-1615-ROADMAP`
start: 2026-10-03 16:15Z (backlog reservation); run lock acquired 16:27:10Z
end: 2026-10-03 17:06Z (commit of this journal)
starting git state: `main` = `f382dbf077699aa65c80328b6519035d1cda4a57` (merge of PR #30), clean;
branch `auto/roadmap` created from it
ending git state: `auto/roadmap` = `f382dbf` + one commit (`ROADMAP.md`, this journal, one
`docs/RUN_INDEX.md` row), pushed; pull request to `main` opened for the owner, not merged
scope: one backlog task from the owner's `auto-backlog` list (`Mythmaker28/ai-credit-sweeper`,
`AUTONOMOUS_MODE.md` rules): "Rédiger un ROADMAP.md de projet à partir du README, d'AGENTS.md, des
PR ouvertes et de l'historique". Documentation only: no code, test, experiment, state file or
decision file changed.

## Actions

1. Read, in the `AGENTS.md` order: `AGENTS.md`, `docs/RESEARCH_CHARTER.md`,
   `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`, `docs/EXPERIMENT_INDEX.md`,
   `docs/RUN_INDEX.md`, the latest journal
   (`docs/agent_journals/2026-08-05/0030_route-e-pilot_ROUTE-E-PILOT-READINESS-00.md`) and the
   pilot's decision file and report; then `README.md` and the decision files cited in
   `ROADMAP.md`.
2. Inspected Git read-only: merges on `main`, root commits, the five open PRs (#31–#35:
   descriptions, branches, changed files), the merge bases of #31–#33 with `main`, and a trial
   merge of each with `git merge-tree` (no ref written, worktree untouched).
3. Ran the full suite on `f382dbf` from a virtual environment outside the repository, first after
   `pip install -e '.[dev]'` only, then with `scipy==1.15.3` added, the version pinned in
   `requirements-lock.txt`. For the second run, the uncommitted `ROADMAP.md` was moved out of the
   worktree so that the tree was clean, as for the first run.
4. Wrote `ROADMAP.md` and checked each statement against the source it cites.
5. Added this journal and the `docs/RUN_INDEX.md` row, committed, pushed `auto/roadmap`, opened
   the pull request, released the lock.

## Important files

Read: the eight `AGENTS.md` inputs above; `README.md`; `pyproject.toml`; `requirements-lock.txt`;
`.github/workflows/nasi-ci.yml`; in `docs/individuation/`:
`ROUTE_E_PILOT_READINESS_00_DECISION.json`, `ROUTE_E_PILOT_READINESS_00_REPORT.md`,
`FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_DECISION.json` and §9.3 of its `_REPORT.md`,
`FUTURE_ROUTE_E_EXECUTION_BOUNDARY_CORRECTION_00_DECISION.json` and `_REPORT.md`,
`A1R5_RNG_MAPPING_OWNER_DECISION.md`, the 01, 01R and 01S decision files;
`tests/test_future_route_e_execution_boundary_00.py` (`INHERITED_FAILURES`); on the #33 branch,
the audit's `NEXT_SCIENTIFIC_ROUTES_01R.md`.

Changed: `ROADMAP.md` (new), this journal (new), `docs/RUN_INDEX.md` (one row at the top of the
table).

## Commands

Linux, Python 3.11.15, numpy 2.4.6, pytest 8.4.2, matplotlib 3.11.2; `PYTHONPYCACHEPREFIX` set
outside the repository.

```bash
python3 -m venv <venv>                      # outside the repository
<venv>/bin/python -m pip install -e '.[dev]'
<venv>/bin/python -m pytest -q -p no:cacheprovider     # 16:20:48–16:23:59Z
<venv>/bin/python -m pip install 'scipy==1.15.3'
<venv>/bin/python -m pytest -q -p no:cacheprovider     # 16:49:42–16:52:50Z
<venv>/bin/python -m edlab.runtime_lock acquire --run-id AUTO-20261003-1615-ROADMAP \
  --task-identity auto-backlog-claude-roadmap \
  --starting-head f382dbf077699aa65c80328b6519035d1cda4a57 --experiment NONE
<venv>/bin/python -m edlab.runtime_lock release --run-id AUTO-20261003-1615-ROADMAP
git log --first-parent --merges --format='%h %ad %s' --date=short main
git merge-base f382dbf origin/<pr-branch>
git merge-tree --write-tree --name-only --no-messages f382dbf origin/<pr-branch>
```

## OBSERVED

- Suite on `f382dbf` after `pip install -e '.[dev]'` only: 1 517 collected, 1 468 passed,
  27 failed, 22 skipped, in 190 s:
  - 16 × `ModuleNotFoundError: No module named 'scipy'` (`test_chemotaxis` 2,
    `test_motile_polar` 2, `test_multistable_phenotype` 5, `test_scaffold` 7);
  - 7 × `configuration_error`, "no verifier supplied; PRB-6 requires a maintained verifier"
    (`test_route_e_beacon_verifier` 5, `test_future_route_e_pre_run_integration_00` 2);
  - 4 × `TypeError: track_components() missing 1 required keyword-only argument:
    'sampled_frames'` (`test_lattice_bond_stage_b`).
- Same commit with `scipy==1.15.3` added: 1 517 collected, 1 483 passed, 12 failed, 22 skipped,
  in 188 s. Fifteen of the 16 `scipy` failures pass.
  `test_motile_polar.py::test_scramble_preserves_all_declared_invariants_and_destroys_organization`
  then fails with `AssertionError: support overlaps its own translate: displacement would not
  conserve mass`, raised in `swap_support` at `edlab/experiments/exp_mo_00_gate0.py:62`. The other
  11 fail with the same messages as in the first run.
- The 12 include the 5 node IDs of `INHERITED_FAILURES` in
  `tests/test_future_route_e_execution_boundary_00.py`, with the messages recorded in §9.3 of
  `FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_REPORT.md`. The pilot decision counts 12 failures,
  7 `caused_by_stop_pinned_verifier_unavailable` and 5 `inherited_historical`, without node IDs.
  Its `suite.after` collected 1 510 tests; this run collected 7 more and counted 7 more passes.
  The difference was not investigated.
- `scipy` is imported by `edlab/substrates/chemotaxis/diagnostics.py`,
  `edlab/substrates/motile_polar/observables.py` and `edlab/experiments/sc_hsi/core.py`, pinned at
  line 5 of `requirements-lock.txt`, and absent from `pyproject.toml`.
- `.github/workflows/nasi-ci.yml` never runs `pytest tests/`.
- PRs #31, #32 and #33 (heads `7e6faeb`, `5e31527`, `cff7f26`) have merge base `199f29e`, the head
  of #29, with `main`. They are 4, 8 and 29 commits ahead of it, and none contains `e5049d0`,
  `2cb7a48`, `eccd46b` or `f19de81`, which reach `main` through #30. A trial merge into `main`
  conflicts in `edlab/substrates/lattice_bond/future_route_e_admission.py` and
  `future_route_e_execution.py`, and for #33 also in `docs/RUN_INDEX.md`.
- `docs/PROJECT_STATE.md` was last changed on 2026-08-04 and still reads
  `pilot_authorized = false`. `docs/DECISION_LOG.md` has no pilot entry.
  `A1R5_RNG_MAPPING_OWNER_DECISION.md` reads `PENDING`, while the pilot record shows
  `owner_decision = SELECT_OPTION_1_TOP_53_BITS` applied.
- `docs/RUN_INDEX.md` has six rows after its 9-column table, in 5- and 3-column formats.
- PR #11 is not among the merges into `main`. The Git history starts on 2026-07-14;
  `docs/DECISION_LOG.md` starts on 2026-07-10.
- The pilot decision concludes that "four focal components had over 99.8% of their matter
  replaced, two exactly complete". Its `residual_focal` list has five values below 0.002: 0.0,
  0.0, 2e-06, 8.4e-05 and 0.001799. Read as the fraction not replaced, that is five components
  above 99.8%. Not checked further; neither record was changed.

## INFERRED

- The pilot's environment most likely had `scipy`: with it, this run shows the pilot's
  12 failures by group and by message; without it, 15 more tests fail.
- CI never runs `tests/`, so a missing dependency or a changed signature does not turn CI red.
  That would explain how the 16 `scipy` failures and the 4 `sampled_frames` failures sit on
  `main`.
- The 4 `test_lattice_bond_stage_b` failures look like API drift: `track_components` requires
  `sampled_frames`, and the tests do not pass it.

## HYPOTHESIS

- PR #31, which installs a verifier and edits both verifier test files, fixes the 7 verifier
  failures. Not tested: its suite was not run.

## WHAT WOULD FALSIFY THIS?

- Any statement of `ROADMAP.md` contradicted by the source it cites. The source prevails, and
  `ROADMAP.md` must be corrected.
- The same commands on `f382dbf` giving other failures in another environment: the counts above
  would then depend on the environment as well as on the code.
- The suite on #31's head, with its verifier installed, still showing the 7 verifier failures.

## Failures and dead ends

- The system `python3` has no numpy. The suite was run from a virtual environment outside the
  repository.
- Mapping each D-number to a PR through Git ancestry gave inconsistent results: the first
  decisions predate the history, and several PRs share a branch. `ROADMAP.md` links groups of
  decisions to lines of work, and PRs to their branch names only.
- Checking `ROADMAP.md` against its sources led to these corrections before the commit:
  - ETCMNFC and the two route names appear in the audit's journals as well as its other files;
  - the history note was rephrased, because decision files start on 2026-08-02;
  - the #33 ordering was paraphrased closer to its text;
  - `ARCHITECTURE_02` and a PRB-5 precondition literal were left out, because later records may
    supersede them;
  - the pilot's test counts were completed with the five inherited node IDs;
  - the merge bases and trial merges of #31–#33 were added;
  - the 7 verifier failures are described by their message: only the 5 beacon tests show
    `BeaconOutcome.CONFIGURATION_ERROR`;
  - §4 was completed with the second run. The H2 and H3 criteria were tightened, since "a
    stated cause" was already met once the causes were known.
- The editable install created the gitignored `emergent_dynamics_lab.egg-info/` (16:20:31Z) and
  `edlab/__pycache__/` (16:20:41Z) before the lock was acquired at 16:27:10Z. No tracked file
  changed before the lock.

## Decisions

These are decisions about this run, not scientific decisions.

- Documentation only. `ROADMAP.md` describes and cites. It ranks nothing and authorizes nothing.
- `docs/PROJECT_STATE.md`, `docs/EXPERIMENT_INDEX.md` and `docs/DECISION_LOG.md` are unchanged:
  no state change, no experiment and no genuine decision.
- The `docs/RUN_INDEX.md` row goes at the top of the 9-column table (newest first), not after the
  six rows outside it.
- No self-merge. The suite is not green (failures that predate this run), so under
  `AUTONOMOUS_MODE.md` the pull request waits for the owner.

## Unresolved risks

- The lock lives in this clone's `.runtime/` only. It does not protect against another clone
  working at the same time.
- `ROADMAP.md` is a snapshot of 2026-10-03. It goes stale with the next merge or decision.
- What `ROADMAP.md` says about the open PRs comes from their descriptions, changed files and
  branch history. Their content was not verified, and their suites were not run.
- The test counts come from one environment (Linux, Python 3.11.15, numpy 2.4.6). CI uses
  Python 3.10 and 3.12, and does not run `tests/`.
- The pilot's count discrepancy (OBSERVED, last item) is reported, not resolved.

## Active experiment

None. The last experiment, `ROUTE-E-PILOT-READINESS-00`, is closed with
`PILOT_DESIGN_RISK_OBSERVED`. This run produced no experiment output to index.

## Handoff

Next authorized action, unchanged from the latest journal: *"ONE owner decision, on the two
observed design risks, before any preregistration mission. Nothing else is authorised."*

This run adds no authorization. The pull request that adds `ROADMAP.md` waits for the owner's
review.
