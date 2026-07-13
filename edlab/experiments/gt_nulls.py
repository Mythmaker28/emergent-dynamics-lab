"""THE INDEPENDENT PHASE-NULL GENERATOR (§3.2).

This module exists to be INDEPENDENT OF THE ESTIMATOR, and it is kept in a separate file for exactly that reason.
It imports NOTHING from `blind_a3`. It must be possible to read this file and see that no number in it was chosen
by looking at the observer.

WHY (D-056). V2's delay estimator struck at phases (0,15,30,45). V2's development phase-null tested phases
(0,15,30,45). The same four numbers. The null was drawn from the estimator's own grid, so it could not fire, and
the certificate measured the estimator's agreement with itself -- reporting a delay deviation of zero while the
head was in fact phase-sensitive. It took a held-out set to find out.

TWO INDEPENDENT DEFENCES ARE NOW IN PLACE, and the first is the real one:

  1. THE ESTIMATOR HAS NO FREE PHASE CHOICE. It strikes at EVERY phase 0..T-1 of the inferred fundamental period.
     `blind_a3.assert_exhaustive_phases` refuses to run on a subset. An estimator with nothing to select cannot
     have its null selected to match it. This is a STRUCTURAL fix, not a procedural one.

  2. THE NULL PHASES ARE DRAWN HERE, FROM A SEED, BEFORE THE OBSERVER SEES ANYTHING, and the manifest is hashed.
     `assert_null_independence` proves the drawn phases were not copied from any strike schedule the observer
     exposes -- and, more importantly, that the strike schedule is exhaustive, so "not copied" is guaranteed
     rather than merely checked.
"""

from __future__ import annotations

import hashlib
import json

SEED = 20260714          # fixed BEFORE any observer was run today; the number is arbitrary and that is the point
N_PHASE_NULLS = 12


def _lcg(seed, n, lo, hi):
    """A deliberately trivial, self-contained PRNG. No numpy, no shared state with the observer -- nothing about
    this sequence can depend on anything the estimator does."""
    x, out = seed, []
    for _ in range(n):
        x = (1103515245 * x + 12345) % (2 ** 31)
        out.append(lo + x % (hi - lo))
    return out


def draw_phase_nulls(period: int, n: int = N_PHASE_NULLS) -> list:
    """Random phase origins in [0, period). Drawn from SEED, never from the observer's schedule."""
    return sorted(set(_lcg(SEED, n * 3, 0, period)))[:n]


def null_manifest(period: int) -> dict:
    m = {"seed": SEED, "period": period, "phase_origins": draw_phase_nulls(period),
         "generator": "edlab/experiments/gt_nulls.py::draw_phase_nulls -- imports NOTHING from the observer",
         "contract": "phase origins are drawn from SEED before evaluation; the estimator's strike schedule is "
                     "EXHAUSTIVE over the inferred period, so no subset can be selected to match this list"}
    m["hash"] = hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest()[:16]
    return m


def assert_null_independence(period: int, strike_schedule) -> dict:
    """Executable §3.2. Two checks, and the second is the one with teeth."""
    nulls = draw_phase_nulls(period)
    if tuple(strike_schedule) != tuple(range(period)):
        raise AssertionError(
            f"the estimator's strike schedule is a SUBSET ({len(strike_schedule)} of {period} phases). "
            f"That is the V2 loophole: a selected grid whose null can be drawn from the same grid. "
            f"Coverage must be exhaustive.")
    if set(nulls) - set(range(period)):
        raise AssertionError("null phases outside the period")
    return {"null_phase_origins": nulls, "strike_schedule": "EXHAUSTIVE (0..T-1)",
            "independence": "STRUCTURAL -- the estimator has no free phase parameter to select",
            "manifest_hash": null_manifest(period)["hash"]}
