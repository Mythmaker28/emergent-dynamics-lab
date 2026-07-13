"""THE INDEPENDENT PHASE-NULL GENERATOR, V2 -- rebuilt because V1 was BIASED (D-058).

V1 did `sorted(set(lcg(...)))[:n]` -- it SORTED AND TRUNCATED, keeping only the smallest draws. The raw sequence
contained 31, 48, 33, 58; the generator returned [1,4,6,8,9,10,11,14,16,17,20,23], every one of them <= 23. The
strike phases at which the V3 probe misbehaves are 2, 3, 5, 32, 33, 35 -- and 32/33/35 were UNREACHABLE BY
CONSTRUCTION. A module whose entire purpose was independence from the estimator had a bias in its sampler.

That is the third time in this project that the test and the thing tested were not independent. So this generator
does not merely avoid the bug: it ASSERTS ITS OWN COVERAGE, and refuses to hand out a phase list that fails.

It imports NOTHING from any observer.
"""

from __future__ import annotations

import hashlib
import json

SEED = 20260715


def _lcg(seed, n):
    x, out = seed, []
    for _ in range(n):
        x = (1103515245 * x + 12345) % (2 ** 31)
        out.append(x)
    return out


def draw_phase_nulls(period: int, n: int = 12) -> list:
    """Uniform draws over the FULL cycle. No sorting-then-truncating: the draws are taken in sequence order and
    de-duplicated in place, so no part of the cycle can be preferentially discarded."""
    out = []
    for x in _lcg(SEED, n * 8):
        p = x % period
        if p not in out:
            out.append(p)
        if len(out) == n:
            break
    return out


def assert_null_coverage(period: int, phases, quantiles: int = 4) -> dict:
    """EXECUTABLE. A null that cannot reach part of the space it is testing is not a null.

    Split [0, T) into `quantiles` equal bins and require EVERY bin to contain at least one drawn phase. V1's list
    ([1,4,6,8,9,10,11,14,16,17,20,23], T=60) fails this instantly: bins 2, 3 and 4 are empty."""
    bins = [[] for _ in range(quantiles)]
    for p in phases:
        bins[min(quantiles - 1, p * quantiles // period)].append(p)
    empty = [i for i, b in enumerate(bins) if not b]
    if empty:
        raise AssertionError(
            f"NULL COVERAGE FAILURE: quantile bin(s) {empty} of [0,{period}) contain no drawn phase. "
            f"Drawn: {sorted(phases)}. A null that cannot reach part of the space is not a null (D-058).")
    return {"period": period, "phases": sorted(phases), "quantile_bins": [sorted(b) for b in bins],
            "coverage": "FULL CYCLE"}


def null_manifest(period: int) -> dict:
    ph = draw_phase_nulls(period)
    m = {"seed": SEED, "period": period, "phase_origins": ph,
         "coverage": assert_null_coverage(period, ph),
         "generator": "edlab/experiments/gt_nulls2.py -- imports NOTHING from any observer; no sort-and-truncate",
         "supersedes": "gt_nulls.py, which was BIASED toward small phases (D-058)"}
    m["hash"] = hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest()[:16]
    return m
