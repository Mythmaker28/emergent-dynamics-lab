"""FTCTR01 (reconstruction) — exact functional-two-centre timescale rederivation.

ZERO engine runs. Part A is closed-form / linear algebra only. Parts B-E measure the
existing PQEC01 and OBTC02 records. Every value is recomputed here; none is copied.
"""
from __future__ import annotations
import json, glob, math, sys, hashlib
import numpy as np
import scipy, scipy.sparse, scipy.sparse.linalg

REPO = "/home/claude/edl"
RAW  = "/home/claude/PQEC01/raw"
OUT  = "/home/claude/FTCTR01/out"

# ---- frozen constants, read from the frozen protocol, never retyped from memory ----
import yaml
P = yaml.safe_load(open(f"{REPO}/OBTC02/code/obtc02_protocol.yaml"))
L      = int(P["point"]["L"])
P_HOP  = float(P["point"]["p_hop"])
MUX    = float(P["point"]["muX"])
A_X    = float(P["analytic"]["a_X"])
D_REL_FROZEN = float(P["analytic"]["D_relative"])
CORE_R = float(P["analytic"]["core_radius_cells"])
EFOLD_FROZEN = float(P["analytic"]["source_off_e_folding_steps"])
TAU_FROZEN = 125.0          # FLCR01 flcr01_science.py:17
STATES = ("E", "O", "C", "S", "P", "F")

# =========================== A. exact separation clock ==============================
q = P_HOP / 4.0
# one particle, one axis, per full step = two ordered sub-shifts (+1 then -1), each p_hop/4
P1 = {+1: q * (1 - q), -1: q * (1 - q), 0: q * q + (1 - q) ** 2}
assert abs(sum(P1.values()) - 1.0) < 1e-15
var_axis = sum(k * k * v for k, v in P1.items())          # == 2q(1-q)

# relative coordinate of two independent particles = P1 convolved with its reflection
PREL = {}
for a, pa in P1.items():
    for b, pb in P1.items():
        PREL[a - b] = PREL.get(a - b, 0.0) + pa * pb
var_rel = sum(k * k * v for k, v in PREL.items())
K = [(dy, dx, py * px) for dy, py in PREL.items() for dx, px in PREL.items() if py * px > 0]

# toroidal min-image distance of the relative coordinate on the L x L torus
ii = np.arange(L)
mi = np.minimum(ii, L - ii)
DIST = np.sqrt(mi[:, None] ** 2 + mi[None, :] ** 2)
ABS = DIST > CORE_R                                        # the classifier's own rule
TRANS = ~ABS
idx = -np.ones((L, L), dtype=np.int64)
idx[TRANS] = np.arange(TRANS.sum())
NT = int(TRANS.sum())

def _step_matrix():
    """Sub-stochastic transition matrix Q restricted to transient states."""
    rows, cols, vals = [], [], []
    ys, xs = np.nonzero(TRANS)
    for dy, dx, p in K:
        ny, nx = (ys + dy) % L, (xs + dx) % L
        keep = TRANS[ny, nx]
        rows.append(idx[ys[keep], xs[keep]])
        cols.append(idx[ny[keep], nx[keep]])
        vals.append(np.full(keep.sum(), p))
    return scipy.sparse.csr_matrix(
        (np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
        shape=(NT, NT))

Q = _step_matrix()
start = idx[0, 0]

# --- method A: linear solve (I - Q) t = 1 ---
I = scipy.sparse.identity(NT, format="csr")
tA = scipy.sparse.linalg.spsolve((I - Q).tocsc(), np.ones(NT))
EA = float(tA[start])

# --- method B: E[tau] = sum_{t>=0} P(tau > t), plus the full distribution ---
v = np.zeros(NT); v[start] = 1.0
surv, EB, t = [], 0.0, 0
while True:
    s = float(v.sum())
    surv.append(s)
    EB += s
    if s < 1e-14 or t > 400000:
        break
    v = Q.T @ v
    t += 1
pmf = -np.diff(np.array(surv))                 # P(tau = t+1)
supp = np.arange(1, len(pmf) + 1)
EB = float(EB)
AGREE = abs(EA - EB) <= 1e-6 * max(1.0, EA)
E2 = float((supp.astype(float) ** 2 * pmf).sum())
SD = math.sqrt(E2 - EB * EB)
cdf = np.cumsum(pmf)
def quant(p):  return float(supp[np.searchsorted(cdf, p)])

EXACT = {
    "q_per_substep": q, "P_one_axis_one_step": {str(k): v for k, v in P1.items()},
    "variance_one_axis_one_step": var_axis, "frozen_a_X": A_X,
    "variance_matches_frozen_a_X": abs(var_axis - A_X) < 1e-12,
    "variance_relative_coordinate": var_rel,
    "D_relative_derived": var_rel / 2.0, "frozen_D_relative": D_REL_FROZEN,
    "D_relative_matches_frozen": abs(var_rel / 2.0 - D_REL_FROZEN) < 1e-12,
    "n_transient_states": NT, "n_absorbing_states": int(ABS.sum()),
    "absorbing_rule": "toroidal min-image distance > CORE_R (the FLCR01 classifier rule)",
    "E_tau_method_A_linear_solve": EA,
    "E_tau_method_B_survival_sum": EB,
    "METHODS_AGREE": bool(AGREE),
    "abs_difference": abs(EA - EB),
    "E_tau": EB, "SD_tau": SD,
    "median_tau": quant(0.5), "q25_tau": quant(0.25), "q75_tau": quant(0.75),
    "TAU_SEP_frozen": TAU_FROZEN,
    "ratio_exact_over_frozen": EB / TAU_FROZEN,
    "frozen_understates_by_percent": 100.0 * (EB - TAU_FROZEN) / EB,
}
json.dump(EXACT, open(f"{OUT}/FTCTR01_FIRST_PASSAGE.json", "w"), indent=2)
print(json.dumps({k: EXACT[k] for k in
    ("variance_one_axis_one_step","variance_matches_frozen_a_X","D_relative_matches_frozen",
     "n_transient_states","E_tau_method_A_linear_solve","E_tau_method_B_survival_sum",
     "METHODS_AGREE","E_tau","SD_tau","median_tau","q25_tau","q75_tau",
     "ratio_exact_over_frozen","frozen_understates_by_percent")}, indent=2))
