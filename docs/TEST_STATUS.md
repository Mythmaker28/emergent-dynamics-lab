# Test status on `main`

Snapshot: `f382dbf077699aa65c80328b6519035d1cda4a57` (2026-10-07).

This is a diagnostic record. It changes no code, data, parameter, scientific result, or
authorization. The backlog described 13 failures; the reproducible count is **12** when the
repository's pinned `scipy==1.15.3` is installed. A fresh `pip install -e '.[dev]'` omits SciPy
and produces 27 failures instead, so the environment must be stated with the count.

## Reproduction environment

- Linux, Python 3.11
- editable install of `.[dev]`
- `scipy==1.15.3`, matching `requirements-lock.txt`
- complete checkout (including `tools/`)

```bash
python3 -m venv /tmp/edlab-test-status
/tmp/edlab-test-status/bin/python -m pip install -e '.[dev]' 'scipy==1.15.3'
PYTHONPYCACHEPREFIX=/tmp/edlab-pycache \
  /tmp/edlab-test-status/bin/python -m pytest -q -p no:cacheprovider
```

Observed: **1,483 passed, 12 failed, 22 skipped**. The 12 node IDs and messages match the
2026-10-03 baseline recorded in PR #36. Two additional failures seen in an initial sparse
checkout were invalid environment artefacts: `tools/` was absent. After restoring it, both
affected tests passed (`2 passed`).

## Classification

| Class | Count | Cause | Disposition |
|---|---:|---|---|
| Environment / unavailable verifier | 7 | No verifier is supplied, so the fail-closed Route E path returns `configuration_error`; tests expect semantic `invalid` outcomes. | Keep fail-closed. Install and pin a maintained verifier before changing expectations. |
| API drift | 4 | `track_components` now requires keyword-only `sampled_frames`; these four tests still call the previous signature. | Update the tests with the exact sampled frame sequence; do not make the production argument optional. |
| Regression / stale fixture | 1 | The motile-polar support fills or overlaps its periodic translate, so `swap_support(..., 18, 18)` correctly rejects a non-bijective, mass-destroying swap. | Repair the fixture or censor this geometry; do not weaken the conservation assertion. |

No failure is evidence for or against the scientific hypotheses. The first group is an
environmental STOP, the second is test/API drift, and the last is a regression in fixture
admissibility.

## One reproduction command per failure

Run these after activating the environment above:

1. `python -m pytest -q 'tests/test_future_route_e_pre_run_integration_00.py::test_round_03_a_neighbouring_round_is_refused_even_if_well_formed[-1]'`
2. `python -m pytest -q 'tests/test_future_route_e_pre_run_integration_00.py::test_round_03_a_neighbouring_round_is_refused_even_if_well_formed[1]'`
3. `python -m pytest -q 'tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[split]'`
4. `python -m pytest -q 'tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[merge]'`
5. `python -m pytest -q 'tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[tie]'`
6. `python -m pytest -q 'tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[collapse]'`
7. `python -m pytest -q tests/test_motile_polar.py::test_scramble_preserves_all_declared_invariants_and_destroys_organization`
8. `python -m pytest -q 'tests/test_route_e_beacon_verifier.py::test_outcome_06_a_response_that_does_not_match_the_pin_is_invalid[mutation0]'`
9. `python -m pytest -q 'tests/test_route_e_beacon_verifier.py::test_outcome_06_a_response_that_does_not_match_the_pin_is_invalid[mutation1]'`
10. `python -m pytest -q 'tests/test_route_e_beacon_verifier.py::test_outcome_06_a_response_that_does_not_match_the_pin_is_invalid[mutation2]'`
11. `python -m pytest -q 'tests/test_route_e_beacon_verifier.py::test_outcome_06_a_response_that_does_not_match_the_pin_is_invalid[mutation3]'`
12. `python -m pytest -q tests/test_route_e_beacon_verifier.py::test_outcome_07_unknown_or_missing_response_keys_are_invalid`

## Repair order

1. Restore a pinned verifier and rerun the seven Route E failures.
2. Update the four Stage-B tests to pass `sampled_frames` explicitly.
3. Replace the inadmissible motile-polar displacement fixture with a disjoint, predeclared
   geometry, then rerun the complete suite.
4. Add `scipy` to an installable dependency group so `pip install -e '.[dev]'` reproduces the
   intended environment without a second manual install.

The GitHub workflow `.github/workflows/nasi-ci.yml` does not run `pytest tests/`; it therefore
cannot currently detect any of these failures.
