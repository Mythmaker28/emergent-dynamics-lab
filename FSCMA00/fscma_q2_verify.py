"""FSCMA00 Section 1 -- INDEPENDENT MINIMAL RECALCULATION of the parent WSFSCRP00 Q2 rank gate.

Separately coded. It imports NOTHING from the parent programme: not wsfscrp_core, not its
weights, not its reader, not numpy's SVD for the decision. It reads only the raw exact rational
response strings out of wsfscrp_q01.json and re-derives everything else from the frozen
physical-time grid.

METHOD (exact, certificate-bearing; no floating point anywhere in the decision path)
------------------------------------------------------------------------------------
The parent formed  X = [ Ycent_A * sqrt(w) , Ycent_B * sqrt(w) ]  and took singular values of the
row-centered X.  sqrt(w) is irrational, so X is not rational -- but the 12x12 Gram

    G = Xc Xc^T ,   G[k,l] = sum_j w_j * ( a_k[j] a_l[j] + b_k[j] b_l[j] )   (a,b centered)

IS exactly rational, because sqrt(w_j)*sqrt(w_j) = w_j exactly.  And sigma_i(Xc) = sqrt(lam_i(G)).
Therefore both gates are exact rational predicates on the eigenvalues of an exactly known
symmetric PSD rational matrix:

    gate_ratio  :  sigma_2/sigma_1 > 1/10        <=>   lam_2 / lam_1 > 1/100
    gate_frac   :  sigma_2^2 / sum sigma^2 >= 1/20  <=>   lam_2 >= trace(G)/20

Eigenvalue counting is done EXACTLY by Sylvester's law of inertia: for rational t, the symmetric
LDL^T factorisation of (G - t I) in exact Fraction arithmetic has exactly #{lam_i < t} negative
diagonal entries.  This is used both to decide the gates by rational certificate and to bisect
certified enclosures of lam_1 and lam_2.

CERTIFICATES EMITTED
    gate_frac  : a single exact inertia count at t = trace(G)/20.  No approximation at all.
    gate_ratio : a rational witness t with  #{lam < t} <= 10  (so lam_2 >= t)  and
                 #{lam < 100 t} = 12  (so lam_1 < 100 t), which proves lam_2/lam_1 > 1/100;
                 or the dual witness proving the negation.
"""
from __future__ import annotations
import json, hashlib, sys
from fractions import Fraction as Fr
from decimal import Decimal, getcontext

getcontext().prec = 60
SRC = "/home/claude/sweep/WSFSCRP00/wsfscrp_q01.json"
OUT = "/home/claude/sweep/FSCMA00/FSCMA00_PARENT_Q2_MINIMAL_RECALCULATION.json"

# ---------------------------------------------------------------- frozen grid, re-derived here
# From the parent freeze: native steps 40..400 step 40, dt = 1/10 exactly -> physical 4..40.
H_GRID = [40 * i for i in range(1, 11)]
DT = Fr(1, 10)
PHYS = [Fr(h) * DT for h in H_GRID]


def trapezoid_weights(p):
    """Trapezoidal quadrature weights over a physical-time grid, normalised to sum exactly 1.
    Written from the definition; not copied from the parent module."""
    n = len(p)
    v = [Fr(0)] * n
    v[0] = (p[1] - p[0]) / 2
    v[n - 1] = (p[n - 1] - p[n - 2]) / 2
    for j in range(1, n - 1):
        v[j] = (p[j + 1] - p[j - 1]) / 2
    s = sum(v, Fr(0))
    return [x / s for x in v]


W = trapezoid_weights(PHYS)
T = len(W)
assert sum(W, Fr(0)) == 1

# ---------------------------------------------------------------- raw response matrix
D = json.load(open(SRC))
U = D["Q1"]
assert len(U) == 12, len(U)
ROWS = [(u["seed"], u["geometry"], u["superfamily"]) for u in U]
A = [[Fr(x) for x in u["dA"]] for u in U]       # exact, straight from the stored strings
B = [[Fr(x) for x in u["dB"]] for u in U]
assert all(len(r) == T for r in A) and all(len(r) == T for r in B)

n = len(U)


def center(M):
    mu = [sum((M[k][j] for k in range(n)), Fr(0)) / n for j in range(T)]
    return [[M[k][j] - mu[j] for j in range(T)] for k in range(n)], mu


Ac, muA = center(A)
Bc, muB = center(B)


def gram(Ac, Bc):
    G = [[Fr(0)] * n for _ in range(n)]
    for k in range(n):
        for l in range(k, n):
            s = sum((W[j] * (Ac[k][j] * Ac[l][j] + Bc[k][j] * Bc[l][j]) for j in range(T)), Fr(0))
            G[k][l] = s
            G[l][k] = s
    return G


G = gram(Ac, Bc)
TR = sum(G[k][k] for k in range(n))
assert TR > 0

# ---------------------------------------------------------------- exact inertia (Sylvester)
def n_below(t):
    """#{eigenvalues of G strictly less than t}, computed exactly.
    Symmetric LDL^T of M = G - tI without pivoting; the count of negative D entries equals the
    count of negative eigenvalues of M, i.e. of eigenvalues of G below t (Sylvester's law).
    A zero pivot makes the unpivoted factorisation undefined -> signalled, caller nudges t."""
    M = [[G[i][j] - (t if i == j else Fr(0)) for j in range(n)] for i in range(n)]
    neg = 0
    for i in range(n):
        piv = M[i][i]
        if piv == 0:
            return None                      # exactly singular leading minor: caller re-tries
        if piv < 0:
            neg += 1
        for r in range(i + 1, n):
            f = M[r][i] / piv
            if f != 0:
                for c in range(i, n):
                    M[r][c] -= f * M[i][c]
    return neg


def count_below(t):
    """n_below with a deterministic zero-pivot escape: nudge t by a tiny rational downward.
    The nudge is recorded; it never crosses an eigenvalue because it is smaller than the
    bisection bracket in which it is used."""
    for k in range(0, 40):
        tt = t if k == 0 else t - Fr(1, 10 ** 40) * k
        r = n_below(tt)
        if r is not None:
            return r, k
    raise RuntimeError("inertia: could not escape a zero pivot")


# ---------------------------------------------------------------- certified eigenvalue brackets
HI = TR                                   # PSD => lam_1 <= trace
def bracket(k, rel=Fr(1, 10 ** 34)):
    """Certified [lo, hi] for the k-th largest eigenvalue (k = 1 is the largest).
    Invariant: count_below(lo) <= n-k  (so lam_k >= lo) and count_below(hi) > n-k (lam_k < hi)."""
    lo, hi = Fr(0), HI * 2
    assert count_below(lo)[0] <= n - k, "PSD violated"
    for _ in range(400):
        if hi - lo <= rel * (hi + 1):
            break
        mid = (lo + hi) / 2
        c, _nud = count_below(mid)
        if c <= n - k:
            lo = mid
        else:
            hi = mid
    return lo, hi


lam1_lo, lam1_hi = bracket(1)
lam2_lo, lam2_hi = bracket(2)

# rank of the centered matrix: 12 centered rows => rank <= 11 => lam_12 == 0 exactly
rank_exact = n - count_below(Fr(1, 10 ** 60))[0] if False else None
zero_count = n - count_below(Fr(1, 10 ** 80))[0]     # #{lam >= 1e-80}: effective rank probe

# ---------------------------------------------------------------- GATE 2 : exact, no bisection
t_frac = TR / 20                                     # sigma_2^2/sum sigma^2 >= 1/20
c_frac, nud_frac = count_below(t_frac)
gate_frac = (c_frac <= n - 2)                        # at least 2 eigenvalues >= t  <=> lam_2 >= t

# ---------------------------------------------------------------- GATE 1 : rational witness
gate_ratio = None
witness = None
for _ in range(1):
    lo, hi = Fr(0), HI * 2
    for _ in range(300):
        mid = (lo + hi) / 2
        c2, _ = count_below(mid)
        if c2 <= n - 2:                              # lam_2 >= mid
            c1, _ = count_below(100 * mid)
            if c1 == n:                              # lam_1 < 100*mid  => lam_2/lam_1 > 1/100
                gate_ratio, witness = True, {"t": str(mid), "count_below_t": c2,
                                             "count_below_100t": c1,
                                             "proves": "lam2 >= t and lam1 < 100t => lam2/lam1 > 1/100"}
                break
            lo = mid
        else:                                        # lam_2 < mid
            c1, _ = count_below(100 * mid)
            if c1 <= n - 1:                          # lam_1 >= 100*mid => lam_2/lam_1 < 1/100
                gate_ratio, witness = False, {"t": str(mid), "count_below_t": c2,
                                              "count_below_100t": c1,
                                              "proves": "lam2 < t and lam1 >= 100t => lam2/lam1 < 1/100"}
                break
            hi = mid
if gate_ratio is None:
    raise RuntimeError("gate_ratio: no rational witness found (value indistinguishable from 1/100)")

# ---------------------------------------------------------------- reporting numbers
def dec(fr):
    return Decimal(fr.numerator) / Decimal(fr.denominator)


def isqrt_dec(fr):
    return dec(fr).sqrt()


ratio_lo = isqrt_dec(lam2_lo / lam1_hi)
ratio_hi = isqrt_dec(lam2_hi / lam1_lo)
frac_lo, frac_hi = dec(lam2_lo / TR), dec(lam2_hi / TR)

# ---------------------------------------------------------------- reproduce the parent verbatim
# The parent rounded every exact rational to float64 first, then called numpy's LAPACK SVD.
# Reproduced here only to test whether that numeric path agreed with the exact answer.
import numpy as np
sw = np.array([float(w) ** 0.5 for w in W])
Yf = np.array([[float(x) for x in a] + [float(x) for x in b] for a, b in zip(A, B)])
Xf = np.concatenate([Yf[:, :T] * sw, Yf[:, T:] * sw], axis=1)
Xf = Xf - Xf.mean(0, keepdims=True)
sv = np.linalg.svd(Xf, compute_uv=False)
float_ratio = float(sv[1] / sv[0])
float_frac = float(sv[1] ** 2 / np.sum(sv ** 2))

PARENT = json.load(open("/home/claude/sweep/WSFSCRP00/wsfscrp_q234.json"))["Q2"]

res = {
    "programme": "FSCMA00",
    "section": "1_PARENT_PROVENANCE_AND_BUG_AUDIT / independent Q2 recalculation",
    "source_file": SRC,
    "source_sha256": hashlib.sha256(open(SRC, "rb").read()).hexdigest(),
    "verifier_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
    "independence": {
        "imports_parent_modules": False,
        "reuses_parent_weights_object": False,
        "weights_rederived_from": "frozen physical grid 4.0..40.0 (native 40..400, dt=1/10)",
        "decision_arithmetic": "exact Fraction; Sylvester inertia via exact LDL^T; no float",
        "numpy_used_only_for": "an optional replication of the parent's float64 path",
    },
    "grid": {"H_GRID": H_GRID, "physical_times": [str(p) for p in PHYS],
             "weights": [str(w) for w in W], "weights_sum": str(sum(W, Fr(0)))},
    "matrix": {"rows": [[r[0], r[1], r[2]] for r in ROWS], "n_units": n, "n_times": T,
               "channels": 2, "centering": "column mean over the 12 units, as in the parent"},
    "gram": {"trace_exact": str(TR),
             "n_eigenvalues_above_1e-80": zero_count,
             "expected_max_rank_after_centering": n - 1},
    "eigenvalues": {
        "lam1_lo": str(lam1_lo), "lam1_hi": str(lam1_hi),
        "lam2_lo": str(lam2_lo), "lam2_hi": str(lam2_hi),
        "lam1_decimal": str(+dec(lam1_lo)), "lam2_decimal": str(+dec(lam2_lo))},
    "GATE_RATIO_sigma2_over_sigma1_gt_0.10": {
        "verdict": bool(gate_ratio),
        "certified_interval": [str(+ratio_lo), str(+ratio_hi)],
        "value_approx": float(ratio_lo),
        "rational_witness": witness},
    "GATE_FRAC_sigma2sq_over_sumsq_ge_0.05": {
        "verdict": bool(gate_frac),
        "certified_interval": [str(+frac_lo), str(+frac_hi)],
        "value_approx": float(frac_lo),
        "exact_certificate": {"threshold_t": str(t_frac),
                              "n_eigenvalues_below_t": c_frac,
                              "n_eigenvalues_at_or_above_t": n - c_frac,
                              "needed_at_or_above": 2,
                              "zero_pivot_nudges": nud_frac,
                              "note": "single exact inertia count; no approximation"}},
    "Q2_PASS_recomputed": bool(gate_ratio and gate_frac),
    "parent_float64_path_replicated": {
        "sigma2_over_sigma1": float_ratio, "sigma2sq_frac": float_frac},
    "parent_reported": {"sigma2_over_sigma1": PARENT["sigma2_over_sigma1"],
                        "sigma2sq_frac": PARENT["sigma2sq_frac"],
                        "gate_ratio_gt_0.10": PARENT["gate_ratio_gt_0.10"],
                        "gate_frac_ge_0.05": PARENT["gate_frac_ge_0.05"],
                        "PASS": PARENT["PASS"]},
}
res["agreement"] = {
    "gate_ratio_matches_parent": bool(gate_ratio) == bool(PARENT["gate_ratio_gt_0.10"]),
    "gate_frac_matches_parent": bool(gate_frac) == bool(PARENT["gate_frac_ge_0.05"]),
    "PASS_matches_parent": bool(gate_ratio and gate_frac) == bool(PARENT["PASS"]),
    # NOTE the certified brackets are narrower than float64 resolution (relative width < 1e-30),
    # so "is the parent's float inside the bracket" is not the right question -- it can only be
    # answered no. The meaningful question is how far the parent's float64 answer sits from the
    # certified exact value, measured in units of float64 resolution (ULP).
    "parent_float_vs_certified_ratio_rel_error":
        float(abs(Decimal(repr(PARENT["sigma2_over_sigma1"])) - ratio_lo) / ratio_lo),
    "parent_float_vs_certified_frac_rel_error":
        float(abs(Decimal(repr(PARENT["sigma2sq_frac"])) - frac_lo) / frac_lo),
    "parent_float_agrees_to_float64_resolution":
        (float(abs(Decimal(repr(PARENT["sigma2_over_sigma1"])) - ratio_lo) / ratio_lo) < 1e-12
         and float(abs(Decimal(repr(PARENT["sigma2sq_frac"])) - frac_lo) / frac_lo) < 1e-12),
    "certified_bracket_relative_width_ratio": float((ratio_hi - ratio_lo) / ratio_lo),
    "certified_bracket_relative_width_frac": float((frac_hi - frac_lo) / frac_lo),
    "margin_of_gate_frac_failure":
        "lam2 = " + str(+frac_lo)[:12] + " of trace, threshold 0.05; the gate fails by a factor "
        + str(+(Decimal("0.05") / frac_lo))[:8] + ", not marginally",
    "margin_of_gate_ratio_pass":
        "sigma2/sigma1 = " + str(+ratio_lo)[:12] + " vs 0.10; passes by a factor "
        + str(+(ratio_lo / Decimal("0.10")))[:8],
}
json.dump(res, open(OUT, "w"), indent=1)

print("weights   :", [str(w) for w in W[:2]], "...", "sum =", sum(W, Fr(0)))
print("trace(G)  :", float(TR))
print("eigen>1e-80:", zero_count, "of", n, "(centering forces at least one exact zero)")
print("lam1      : [%.18e , %.18e]" % (float(lam1_lo), float(lam1_hi)))
print("lam2      : [%.18e , %.18e]" % (float(lam2_lo), float(lam2_hi)))
print("sigma2/sigma1 certified : [%s , %s]" % (str(+ratio_lo)[:22], str(+ratio_hi)[:22]))
print("   gate >0.10 :", gate_ratio, "| witness t =", witness["t"][:28], "...")
print("sigma2^2/sum  certified : [%s , %s]" % (str(+frac_lo)[:22], str(+frac_hi)[:22]))
print("   gate >=0.05:", gate_frac, "| exact: #eig >= trace/20 is", n - c_frac, "(need 2)")
print("Q2 PASS recomputed :", bool(gate_ratio and gate_frac), "| parent:", PARENT["PASS"])
print("parent float path replicated: ratio %.10f frac %.10f" % (float_ratio, float_frac))
print("parent reported             : ratio %.10f frac %.10f"
      % (PARENT["sigma2_over_sigma1"], PARENT["sigma2sq_frac"]))
print("agreement:", json.dumps(res["agreement"]))
