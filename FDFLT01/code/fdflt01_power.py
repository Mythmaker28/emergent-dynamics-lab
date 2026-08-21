"""FDFLT01 §2 + §13 — the frozen exact-binomial decision rule. Computed BEFORE any run."""
from __future__ import annotations
import json, math
from scipy.stats import binom, beta

N, P0, ALPHA = 192, 0.10, 0.05

def critical(n=N, p0=P0, alpha=ALPHA):
    """Smallest c with P_{p0}(X >= c) <= alpha. Exact, no normal approximation."""
    c = 0
    while binom.sf(c - 1, n, p0) > alpha: c += 1
    return c

def cp(k, n, conf=0.95, one_sided=False):
    if one_sided:
        return (0.0 if k == 0 else float(beta.ppf(1 - conf, k, n - k + 1)))
    a = (1 - conf) / 2
    lo = 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a, k + 1, n - k))
    return lo, hi

def power(p1, n=N, p0=P0, alpha=ALPHA):
    return float(binom.sf(critical(n, p0, alpha) - 1, n, p1))

if __name__ == "__main__":
    # developmental planning values RECOMPUTED from FLRS02 bytes, not copied
    A = json.load(open("/home/claude/edl/FLRS02/out/FLRS02_B1_DIRECT_ATLAS.json"))
    R = A["ATLAS"]["RATES"]["P_JOINT_FUNCTIONAL_SUCCESS_T_primary"]
    dev_k, dev_n = R["count"], R["n"]
    dev_p = dev_k / dev_n
    dev_lo = cp(dev_k, dev_n)[0]
    C = critical()
    J = {"SECTION": "FDFLT01 §2 — frozen decision rule, committed before any scientific world exists",
         "PRIMARY_N": N, "PRIMARY_NULL_RATE": P0, "PRIMARY_ALPHA": ALPHA,
         "TEST": "one-sided exact binomial, H0: p <= 0.10 against H1: p > 0.10",
         "PRIMARY_CRITICAL_SUCCESS_COUNT": C,
         "REJECT_H0_IF": "SUCCESS_COUNT >= %d" % C,
         "P_p0_X_ge_critical": float(binom.sf(C - 1, N, P0)),
         "P_p0_X_ge_critical_minus_1": float(binom.sf(C - 2, N, P0)),
         "SIZE_IS_AT_MOST_ALPHA": bool(binom.sf(C - 1, N, P0) <= ALPHA),
         "DEVELOPMENTAL_B1_SUCCESS": "%d / %d" % (dev_k, dev_n),
         "DEVELOPMENTAL_B1_RATE": dev_p,
         "DEVELOPMENTAL_B1_LOWER_95": dev_lo,
         "DEVELOPMENTAL_SOURCE": "recomputed from FLRS02_B1_DIRECT_ATLAS.json bytes; not copied from any launcher",
         "POWER_AT_DEVELOPMENTAL_LOWER_BOUND": power(dev_lo),
         "POWER_AT_DEVELOPMENTAL_POINT_ESTIMATE": power(dev_p),
         "PRIMARY_CLAIM_PASSES_IF": "the exact one-sided 95% lower confidence bound on the fresh rate exceeds 0.10",
         "EQUIVALENCE_OF_THE_TWO_STATEMENTS": {
             "note": "X >= critical and lower-bound > p0 are the same event for the Clopper-Pearson bound at this alpha",
             "smallest_X_with_one_sided_lower_bound_above_p0":
                 next(k for k in range(N + 1) if cp(k, N, 0.95, True) > P0)},
         "NO_NORMAL_APPROXIMATION_ANYWHERE": True,
         "FROZEN_BEFORE_ANY_RUN": True,
         "MAY_NOT_CHANGE_AFTER_OUTCOMES": True}
    json.dump(J, open("/home/claude/edl/FDFLT01/out/FDFLT01_POWER_ANALYSIS.json", "w"), indent=2)
    print(json.dumps(J, indent=2))
