"""LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03E — deterministic power regenerator (red-team REPRO-01 / B5).

Regenerates the frozen family-size headline from committed code (previously only present as prose):

    p_eligible          ~ Beta(8.5, 2.5)              # 8/10 eligible DEV, Jeffreys prior
    p_feasible|eligible ~ Beta(4.5, 4.5)              # 4/8 feasible DEV, Jeffreys prior
    N_valid | N         ~ Binomial(N, p_eligible * p_feasible)
    headline            = P(N_valid >= 18 | N = 96)

Deterministic 2-D Gauss-Legendre quadrature (no RNG). Prints the exact expected values so a re-auditor can diff:
    mean_valid_probability          = 0.386363636363...
    P(N_valid >= 18 | N = 50)       = 0.570903754176
    P(N_valid >= 18 | N = 96)       = 0.924519023326
"""
from __future__ import annotations

import numpy as np
from scipy.stats import beta, binom

A_ELIG, B_ELIG = 8.5, 2.5
A_FEAS, B_FEAS = 4.5, 4.5
FLOOR = 18
NODES = 400  # Gauss-Legendre nodes per axis; convergence checked to 1e-9


def _nodes():
    x, w = np.polynomial.legendre.leggauss(NODES)   # on [-1, 1]
    p = 0.5 * (x + 1.0)                              # map to [0, 1]
    wp = 0.5 * w
    return p, wp


def prob_at_least(floor: int, n: int) -> float:
    p, wp = _nodes()
    pe = beta.pdf(p, A_ELIG, B_ELIG)
    pf = beta.pdf(p, A_FEAS, B_FEAS)
    # integrate over pe (rows) and pf (cols): sf(floor-1) = P(X >= floor)
    PE, PF = np.meshgrid(p, p, indexing="ij")
    surv = binom.sf(floor - 1, n, PE * PF)
    weight = (wp[:, None] * pe[:, None]) * (wp[None, :] * pf[None, :])
    return float(np.sum(surv * weight))


def mean_valid_probability() -> float:
    return float((A_ELIG / (A_ELIG + B_ELIG)) * (A_FEAS / (A_FEAS + B_FEAS)))


def main() -> None:
    out = {
        "model": "p_eligible~Beta(8.5,2.5), p_feasible|eligible~Beta(4.5,4.5), Binomial(N, p_eligible*p_feasible)",
        "method": f"deterministic 2-D Gauss-Legendre quadrature, {NODES}x{NODES} nodes",
        "mean_valid_probability": mean_valid_probability(),
        "probability_at_least_18_given_50": prob_at_least(FLOOR, 50),
        "probability_at_least_18_given_96": prob_at_least(FLOOR, 96),
        "floor": FLOOR,
        "expected_probability_at_least_18_given_96": 0.924519023326,
        "expected_probability_at_least_18_given_50": 0.570903754176,
    }
    import json
    print(json.dumps(out, indent=2))
    assert abs(out["probability_at_least_18_given_96"] - 0.924519023326) < 1e-6, "P>=18@96 mismatch"
    assert abs(out["probability_at_least_18_given_50"] - 0.570903754176) < 1e-6, "P>=18@50 mismatch"
    print("POWER REGENERATOR OK — matches audited 0.924519 and 0.570904")


if __name__ == "__main__":
    main()
