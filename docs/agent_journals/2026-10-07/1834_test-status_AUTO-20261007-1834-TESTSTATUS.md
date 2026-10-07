# AUTO-20261007-1834-TESTSTATUS — journal

role: auto-backlog agent `codex`, documentation-only test-status analyst

run ID: `AUTO-20261007-1834-TESTSTATUS`

start/end: 2026-10-07 18:34Z / 2026-10-07 18:50Z

starting Git state: clean `main` at `f382dbf077699aa65c80328b6519035d1cda4a57`

ending Git state: `auto/test-status` tip; documentation-only pull request pending owner review

assigned scope: classify the failing `pytest tests/` cases on `main` as API drift,
environment, or regression, with one reproduction command per failure.

## Actions

1. Read the repository contract and durable state in the required order, including the latest
   journal and the Route E pilot manifest/report.
2. Acquired the scheduled-run lock before changing tracked files.
3. Created `auto/test-status` from exact `main` SHA `f382dbf`.
4. Created a Python 3.11 environment outside the repository, installed `.[dev]` plus the
   lockfile's `scipy==1.15.3`, and ran the complete suite.
5. Corrected an invalid sparse-checkout artefact by restoring `tools/`; the two affected tests
   then passed.
6. Added `docs/TEST_STATUS.md`, this journal, and one `docs/RUN_INDEX.md` row.

Important files read: `AGENTS.md`, `docs/RESEARCH_CHARTER.md`, `docs/PROJECT_STATE.md`,
`docs/DECISION_LOG.md`, `docs/EXPERIMENT_INDEX.md`, `docs/RUN_INDEX.md`, the latest journal,
the Route E pilot manifest/report, `pyproject.toml`, `requirements-lock.txt`, and the failing
tests/code paths.

Changed: `docs/TEST_STATUS.md`, this journal, `docs/RUN_INDEX.md`. No code, data, experiment,
state, decision, parameter, or scientific result changed.

## Reproducible commands

```bash
python3 -m venv /tmp/edlab-teststatus-20261007
/tmp/edlab-teststatus-20261007/bin/python -m pip install -e '.[dev]' 'scipy==1.15.3'
PYTHONPYCACHEPREFIX=/tmp/edlab-pycache-20261007 \
  /tmp/edlab-teststatus-20261007/bin/python -m pytest -q -p no:cacheprovider
```

Per-node commands are in `docs/TEST_STATUS.md`.

## OBSERVED

- Complete checkout with SciPy: 1,483 passed, 12 failed, 22 skipped.
- Failures: 7 unavailable-verifier/environment, 4 `sampled_frames` API drift, 1 inadmissible
  motile-polar fixture.
- The backlog's count of 13 is not reproduced. The same 12 were recorded on 2026-10-03.
- A sparse checkout lacking `tools/` added two false failures. Restoring `tools/` made both pass.
- `.github/workflows/nasi-ci.yml` does not run `pytest tests/`.

## INFERRED

The stable 12-failure set is pre-existing on `main`; documentation does not create it. The
seven verifier failures are fail-closed environmental STOPs, not scientific regressions.

## HYPOTHESIS

Supplying the pinned maintained verifier will clear the seven environment failures. Updating
only the four test calls with correct sampled frames will clear the API-drift group.

## WHAT WOULD FALSIFY THIS?

- The same complete-checkout command at `f382dbf` yields a different failure set.
- A valid pinned verifier leaves one of the seven verifier failures unchanged.
- Passing correct `sampled_frames` leaves one of the four Stage-B tests failing for another
  reason.

## Failures and dead ends

The first full-suite run was from a sparse checkout without `tools/`, adding two invalid
environment failures. They were isolated and retested after restoring the directory.

## Decisions

- Document facts only; do not modify tests or production code in this task.
- Do not update project/experiment/decision state: no scientific state changed.
- Do not self-merge because the complete suite is not green.

## Unresolved risks

- The seven verifier cases cannot be semantically exercised until the pinned verifier exists.
- The complete suite remains red, and CI does not expose that state.

## Handoff

Next exact action: restore a pinned verifier or explicitly revise that STOP, then rerun the
seven Route E commands listed in `docs/TEST_STATUS.md`.
