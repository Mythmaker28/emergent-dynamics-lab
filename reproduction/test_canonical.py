"""Automatic test of the four FROZEN canonical numbers and their tolerances.
Run:  python -m reproduction.test_canonical   (exit 0 = pass, 1 = fail)   [also importable by pytest]
"""
from __future__ import annotations
import sys

CANONICAL = {
    "h1_deep_point": (0.89, 0.06),
    "h1_deep_ci_lo": (0.84, 0.08),
    "h1_deep_ci_hi": (0.96, 0.08),
    "h2_deep_point": (-0.24, 0.06),
    "h2_deep_ci_lo": (-0.79, 0.10),
    "h2_deep_ci_hi": (0.32, 0.10),
    "survival": (36, 0),
    "switches": (0, 0),
}


def compute():
    from . import primary as P, decode as DEC
    import numpy as np
    recs = P.load_records()
    Xd, y1, g, _ = P.build_Xy(recs, P.DEEP_STEP, "h1")
    _, y2, _, _ = P.build_Xy(recs, P.DEEP_STEP, "h2")
    h1p = DEC.decode_r2(Xd, y1, g); h1lo, _, h1hi = DEC.bootstrap_ci(Xd, y1, g)
    h2p = DEC.decode_r2(Xd, y2, g); h2lo, _, h2hi = DEC.bootstrap_ci(Xd, y2, g)
    surv = len(recs) - sum(1 for r in recs if r.get("lost"))
    sw = sum(int(r.get("switch", 0)) for r in recs)
    return {"h1_deep_point": h1p, "h1_deep_ci_lo": h1lo, "h1_deep_ci_hi": h1hi,
            "h2_deep_point": h2p, "h2_deep_ci_lo": h2lo, "h2_deep_ci_hi": h2hi,
            "survival": surv, "switches": sw}


def run():
    got = compute()
    bad = []
    for k, (exp, tol) in CANONICAL.items():
        v = got[k]
        if abs(v - exp) > tol:
            bad.append("%s = %.4f, expected %.4f ± %.4f" % (k, v, exp, tol))
    for k in CANONICAL:
        print("  %-16s = %+.4f   (canonical %+.3f ± %.3f)" % (k, got[k], *CANONICAL[k]))
    if bad:
        print("CANONICAL TEST: FAIL\n  " + "\n  ".join(bad)); return 1
    print("CANONICAL TEST: PASS (4 frozen numbers within tolerance)."); return 0


def test_canonical_numbers():   # pytest entry point
    assert run() == 0


if __name__ == "__main__":
    sys.exit(run())
