# AUTO-20261009-1829-STAGEBTESTS — journal

role: auto-backlog agent `codex`, test-only API-drift repair

run ID: `AUTO-20261009-1829-STAGEBTESTS`

start/end: 2026-10-09 18:29Z / 2026-10-09 18:36Z

starting Git state: clean `main` at `f382dbf077699aa65c80328b6519035d1cda4a57`

ending Git state: `auto/fix-stage-b-sampled-frames` tip, pending pull request review

assigned scope: adapt the four parameterized Stage-B tracker-parity cases to the mandatory
keyword-only `sampled_frames` argument of `track_components`.

## Actions

1. Read the repository contract and durable state in the required order, including the latest
   journal and the Route E pilot manifest/report.
2. Acquired the conservative scheduled-run lock with experiment `NONE` before changing files.
3. Created `auto/fix-stage-b-sampled-frames` from exact `main` SHA `f382dbf`.
4. Passed the detector frame schedule `tuple(range(len(frames)))` explicitly in the one stale
   production tracker call; production code remains unchanged.
5. Ran the four targeted cases, the complete Stage-B test module, and the complete suite in a
   fresh Python environment with `scipy==1.15.3`.

Important files read: `AGENTS.md`, `docs/RESEARCH_CHARTER.md`, `docs/PROJECT_STATE.md`,
`docs/DECISION_LOG.md`, `docs/EXPERIMENT_INDEX.md`, `docs/RUN_INDEX.md`, the latest journal,
the Route E pilot manifest/report, `tests/test_lattice_bond_stage_b.py`, and
`edlab/substrates/lattice_bond/instrumentation.py`.

Changed: `tests/test_lattice_bond_stage_b.py`, this journal, and `docs/RUN_INDEX.md`. No
production code, data, parameter, experiment, decision, or scientific result changed.

## Reproducible commands

```bash
PYTHONPYCACHEPREFIX=/tmp/edlab-pycache-20261009 \
  /tmp/edlab-stageb-20261009/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse

PYTHONPYCACHEPREFIX=/tmp/edlab-pycache-20261009 \
  /tmp/edlab-stageb-20261009/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_lattice_bond_stage_b.py

PYTHONPYCACHEPREFIX=/tmp/edlab-pycache-20261009 \
  /tmp/edlab-stageb-20261009/bin/python -m pytest -q -p no:cacheprovider
```

## OBSERVED

- Targeted parameterized tracker parity: 4 passed.
- Complete `tests/test_lattice_bond_stage_b.py`: 32 passed.
- Complete suite: 1,487 passed, 8 failed, 22 skipped in 146.40 s.
- The four previous Stage-B API-drift failures are absent. The remaining failures are the
  already classified 7 unavailable-verifier cases and 1 inadmissible motile-polar fixture.

## INFERRED

Supplying the declared sampled frame sequence repairs only the stale test/API boundary and
does not weaken the mandatory production contract.

## HYPOTHESIS

The same branch under CI or another Python environment will preserve tracker parity because
the schedule is derived directly from the detector-frame list used by the fixture.

## WHAT WOULD FALSIFY THIS?

- Any of the four targeted cases fails on the branch tip.
- The production and independent track/event projections differ after the schedule is supplied.
- The complete suite gains a failure outside the eight already classified cases.

## Failures and dead ends

The base cloud Python had no `pytest`; a fresh isolated environment was created from the
declared development dependencies plus the lockfile's `scipy==1.15.3`.

## Decisions

- Keep `sampled_frames` mandatory and keyword-only in production.
- Leave the PR open: the complete suite is not green, despite removing all four scoped failures.
- Do not update project, experiment, or decision state because no scientific state changed.

## Unresolved risks

- Seven verifier-dependent tests remain fail-closed until the pinned verifier is available.
- One motile-polar fixture remains inadmissible under the conservative swap assertion.

## Handoff

Next exact action: review this test-only PR; separately restore the pinned verifier before
changing the seven fail-closed Route E expectations.
