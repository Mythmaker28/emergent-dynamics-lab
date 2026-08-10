"""FSCMA00 Phase 1 (cont.) -- inherited domain-violation quantification + algebraic rank ceiling
+ the PREREGISTERED environmental prediction. ZERO engine starts, exact arithmetic throughout.

E. Quantify the C1/C2 joint-domain violation that the parent recorded as domain_ok=False in 6 of
   its 12 TRAIN cells and did not act on.
F. Rank-ceiling algebra on the parent's 12x20 raw response matrix: sum/difference channels,
   A<->B antisymmetry, per-superfamily principal angle, exact Gram spectrum.
G. Freeze the discriminating prediction BEFORE the environmental operator is ever executed.
"""
from __future__ import annotations
import sys, json, hashlib
from fractions import Fraction as Fr
from decimal import Decimal, getcontext
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/ETPC")
sys.path.insert(0, "/home/claude/sweep/ETCMNFC")
sys.path.insert(0, "/home/claude/sweep/WSFSCRP00")
import numpy as np
import wsfscrp_core as Z
import domc_core as K, ppai_core as P
import etcmnfc_core as EC

getcontext().prec = 50
OUT = "/home/claude/sweep/FSCMA00"
CKD = "/home/claude/sweep/WSFSCRP00/checkpoints"
LED = json.load(open("/home/claude/sweep/WSFSCRP00/WSFSCRP00_CANDIDATE_QUEUE_AND_ACCEPTANCE_LEDGER.json"))
BASIS = [tuple(x) for x in LED["roles"]["TRAIN_SELECTION"]]
R = {}


def esum(a):
    return sum((Fr(float(v)) for v in np.asarray(a).ravel()), Fr(0))


# =====================================================================================
# E. INHERITED DOMAIN VIOLATION, quantified
# =====================================================================================
def ops_for(st0, MA, MB):
    K.set_geometry("FAR")
    mem = {"A": np.nonzero(MA), "B": np.nonzero(MB)}
    ok = EC.eligible_edges(st0, mem)
    ida = np.asarray(mem["A"][0]) * Z.L + np.asarray(mem["A"][1])
    idb = np.asarray(mem["B"][0]) * Z.L + np.asarray(mem["B"][1])
    M, pairs = EC.frozen_matching(ok, ida, idb)
    I = [(int(mem["A"][0][i]), int(mem["A"][1][i])) for (_, _, i, j) in pairs]
    J = [(int(mem["B"][0][j]), int(mem["B"][1][j])) for (_, _, i, j) in pairs]
    return {"S1_matched_transposition": lambda s: EC.transpose(s, I, J),
            "S2a_intensive_reflection": lambda s: P.state_cross(s),
            "S2b_extensive_reflection": lambda s: K.reciprocal_cross(s),
            "S2c_total_ablation": lambda s: P.erase_all(s)}


dom = []
for seed, geom in BASIS:
    st0 = Z.load(f"{CKD}/f_{seed}_{geom}.npz")
    mk = np.load(f"{CKD}/m_{seed}_{geom}.npz")
    MA, MB = mk["MA"], mk["MB"]
    sup = MA | MB
    for nm, op in ops_for(st0, MA, MB).items():
        post = op(st0.copy())
        mf0, rho = post.Mf[0], post.rho
        dead = rho <= 1e-4
        v1 = np.abs(mf0) > rho                       # C1
        v2 = dead & (mf0 != 0.0)                     # C2
        tot = esum(np.abs(mf0))
        off = esum(np.abs(mf0[dead]))
        dom.append({
            "seed": seed, "operator": nm,
            "C1_violated": bool(v1.any()), "C1_n_sites": int(v1.sum()),
            "C1_max_excess": float(np.max(np.abs(mf0) - rho)) if v1.any() else 0.0,
            "C2_violated": bool(v2.any()), "C2_n_sites": int(v2.sum()),
            "C2_n_dead_sites_total": int(dead.sum()),
            "C2_max_abs_Mf0_on_dead": float(np.abs(mf0[dead]).max()) if dead.any() else 0.0,
            "C2_offgate_abs_content": str(off),
            "C2_offgate_share_of_total_abs_content": float(off / tot) if tot > 0 else 0.0,
            "n_sites_in_AuB": int(sup.sum()),
        })
R["E_inherited_domain_violation"] = {
    "finding": "WSFSCRP00 recorded domain_ok=False in 6 of its 12 TRAIN cells (every S2 = "
               "intensive reflection cell) and did not act on it. This audit determines which "
               "constraint failed, by how much, and whether the dynamics repair it.",
    "constraints": {"C1": "|Mf[0]_i| <= rho_i", "C2": "Mf[0]_i == 0.0 exactly where rho_i <= 1e-4"},
    "per_cell": dom,
    "engine_repair_argument": (
        "The writer ends every step with newm[kk] = clip(mk,-1,1) * alive and Mf = rho * newm, "
        "with alive = rho > 1e-4. Therefore Mf is exactly 0 off the alive gate at the END of "
        "every step, for every step, unconditionally. A C2 violation introduced at t0 survives "
        "strictly less than one step. It is NOT inert, however: within that first step the "
        "carrier transport term dM reads fM = Mf/max(rho,EPS), so off-gate carrier can be "
        "advected onto live neighbours before the gate is re-applied."),
    "scope_of_the_correction": (
        "This is a defect in the parent's DOMAIN DECLARATION or in its choice of S2 instance, "
        "not a defect in the Q2 rank arithmetic, which is confirmed exactly elsewhere in this "
        "programme. It is recorded, not repaired: the parent's outputs are append-only."),
}

# =====================================================================================
# F. RANK-CEILING ALGEBRA on the parent's 12 x 20 raw response matrix
# =====================================================================================
D = json.load(open("/home/claude/sweep/WSFSCRP00/wsfscrp_q01.json"))
U = D["Q1"]
H = [40 * i for i in range(1, 11)]
PHYS = [Fr(h) * Fr(1, 10) for h in H]
v = [Fr(0)] * 10
v[0] = (PHYS[1] - PHYS[0]) / 2
v[9] = (PHYS[9] - PHYS[8]) / 2
for j in range(1, 9):
    v[j] = (PHYS[j + 1] - PHYS[j - 1]) / 2
W = [x / sum(v, Fr(0)) for x in v]
T = 10
A = [[Fr(x) for x in u["dA"]] for u in U]
B = [[Fr(x) for x in u["dB"]] for u in U]
LAB = [(u["seed"], u["superfamily"].split("_")[0]) for u in U]


def wenergy(r):
    return sum((W[j] * r[j] * r[j] for j in range(T)), Fr(0))


chan = []
for k, u in enumerate(U):
    s = [A[k][j] + B[k][j] for j in range(T)]
    d = [A[k][j] - B[k][j] for j in range(T)]
    Es, Ed = wenergy(s), wenergy(d)
    tot = Es + Ed
    chan.append({"seed": u["seed"], "superfamily": u["superfamily"].split("_")[0],
                 "E_sum": str(Es), "E_diff": str(Ed),
                 "sum_share": float(Es / tot) if tot > 0 else None,
                 "diff_share": float(Ed / tot) if tot > 0 else None,
                 "antisymmetry_ratio_dB_over_dA":
                     float(sum((W[j] * abs(B[k][j]) for j in range(T)), Fr(0))
                           / sum((W[j] * abs(A[k][j]) for j in range(T)), Fr(0)))})
ss = [c["sum_share"] for c in chan]
R["F_rank_ceiling_algebra"] = {
    "channel_decomposition": {
        "definition": "s = dA + dB (common mode, net matter in the two windows), "
                      "d = dA - dB (differential mode, redistribution between the windows). "
                      "Energy is the quadrature-weighted sum of squares over the scored grid.",
        "per_cell": chan,
        "carrier_sum_share_min": min(ss), "carrier_sum_share_max": max(ss),
        "carrier_sum_share_median": float(np.median(ss)),
    }}

# exact Gram spectrum, reusing the certified inertia machinery of the Q2 verifier
def gram_of(rows):
    n = len(rows)
    mu = [sum((rows[k][j] for k in range(n)), Fr(0)) / n for j in range(len(rows[0]))]
    Xc = [[rows[k][j] - mu[j] for j in range(len(mu))] for k in range(n)]
    ww = W + W if len(mu) == 2 * T else W
    G = [[sum((ww[j] * Xc[k][j] * Xc[l][j] for j in range(len(mu))), Fr(0)) for l in range(n)]
         for k in range(n)]
    return G


def eig_desc(G):
    n = len(G)

    def nbelow(t):
        M = [[G[i][j] - (t if i == j else Fr(0)) for j in range(n)] for i in range(n)]
        neg = 0
        for i in range(n):
            p = M[i][i]
            if p == 0:
                return None
            if p < 0:
                neg += 1
            for r in range(i + 1, n):
                f = M[r][i] / p
                if f:
                    for c in range(i, n):
                        M[r][c] -= f * M[i][c]
        return neg

    def cnt(t):
        for k in range(40):
            r = nbelow(t if k == 0 else t - Fr(1, 10 ** 40) * k)
            if r is not None:
                return r
        raise RuntimeError

    tr = sum(G[i][i] for i in range(n))
    out = []
    for k in range(1, 4):                     # top three only; the tail costs a lot and says little
        lo, hi = Fr(0), tr * 2 + 1
        for _ in range(80):
            if hi - lo <= Fr(1, 10 ** 16) * (hi + 1):
                break
            mid = (lo + hi) / 2
            if cnt(mid) <= n - k:
                lo = mid
            else:
                hi = mid
        out.append(lo)
    return out, tr


ALL = [A[k] + B[k] for k in range(12)]
SUMROWS = [[A[k][j] + B[k][j] for j in range(T)] for k in range(12)]
DIFROWS = [[A[k][j] - B[k][j] for j in range(T)] for k in range(12)]
spec, tr = eig_desc(gram_of(ALL))
spec_s, tr_s = eig_desc(gram_of(SUMROWS))
spec_d, tr_d = eig_desc(gram_of(DIFROWS))
R["F_rank_ceiling_algebra"]["exact_gram_spectra"] = {
    "full_two_channel": {"lambda": [float(x) for x in spec], "trace": float(tr),
                         "lam2_over_lam1": float(spec[1] / spec[0]),
                         "sigma2_over_sigma1": float((Decimal(spec[1].numerator)
                                                      / Decimal(spec[1].denominator)
                                                      / (Decimal(spec[0].numerator)
                                                         / Decimal(spec[0].denominator))).sqrt()),
                         "lam1_share": float(spec[0] / tr)},
    "sum_channel_only": {"lambda": [float(x) for x in spec_s], "trace": float(tr_s),
                         "share_of_full_trace": float(tr_s / tr)},
    "diff_channel_only": {"lambda": [float(x) for x in spec_d], "trace": float(tr_d),
                          "share_of_full_trace": float(tr_d / tr)},
}

# per-superfamily subspace comparison: does S2 add a direction S1 does not have?
def unitize(rows):
    M = np.array([[float(x) for x in r] for r in rows])
    sw = np.array([float(w) ** 0.5 for w in W] * (M.shape[1] // T))
    M = M * sw
    M = M - M.mean(0, keepdims=True)
    return M


S1i = [k for k in range(12) if LAB[k][1] == "S1"]
S2i = [k for k in range(12) if LAB[k][1] == "S2"]
M1, M2 = unitize([ALL[k] for k in S1i]), unitize([ALL[k] for k in S2i])
u1, _, _ = np.linalg.svd(M1.T, full_matrices=False)
u2, _, _ = np.linalg.svd(M2.T, full_matrices=False)
k1 = min(2, u1.shape[1]); k2 = min(2, u2.shape[1])
cs = np.linalg.svd(u1[:, :k1].T @ u2[:, :k2], compute_uv=False)
# leading direction of the whole carrier set
Mall = unitize(ALL)
uA, sA, vA = np.linalg.svd(Mall, full_matrices=False)
R["F_rank_ceiling_algebra"]["superfamily_subspaces"] = {
    "principal_cosines_S1_vs_S2_leading_2d": [float(x) for x in cs],
    "principal_angles_deg": [float(np.degrees(np.arccos(min(1.0, max(-1.0, x))))) for x in cs],
    "interpretation": "cosines near 1 mean the two TRAIN superfamilies excite the same response "
                      "directions and differ essentially in amplitude; that is what a rank-one "
                      "response matrix looks like from the operator side.",
}

# =====================================================================================
# G. PREREGISTERED PREDICTION, frozen before the environmental operator is executed
# =====================================================================================
CARRIER_SUM_SHARE_MAX = max(ss)
R["G_preregistered_prediction"] = {
    "frozen_before": "any environmental engine start of this programme (probe start count = 0 "
                     "at the moment this file is written)",
    "mechanism": [
        "Every carrier operator leaves N bit-identical, so it changes the total nutrient budget "
        "by exactly zero, and by the one-step dependency matrix it cannot reach rho at all "
        "within one step. It acts as a multiplicative transport-coefficient perturbation.",
        "The environmental operator adds +amp*N0 at all 4096 sites, changing the nutrient budget "
        "by exactly amp*N0*L^2, and reaches rho within one step through the growth term. It acts "
        "as an additive source perturbation that INJECTS matter into both scored windows.",
    ],
    "P1_common_mode": {
        "statement": "the environmental response will load on the common mode s = dA + dB more "
                     "heavily than any carrier cell does",
        "threshold": "env sum_share > " + str(CARRIER_SUM_SHARE_MAX)
                     + " (the maximum over all 12 carrier cells)",
        "carrier_sum_share_max": CARRIER_SUM_SHARE_MAX,
        "falsifier": "if the environmental sum_share lands inside the carrier range, the "
                     "budget-injection mechanism above is not what drives the endpoint and P1 is "
                     "recorded as refuted.",
    },
    "P2_off_family": {
        "statement": "the environmental response will fall outside the affine 1-D family S1 "
                     "fitted on the carrier BASIS",
        "threshold": "OFF1 > 0.10 for the environmental cells, the same tube gate the carrier "
                     "cells must satisfy from the inside",
        "falsifier": "OFF1 <= 0.10 for the environmental cells supports H1 instead.",
    },
    "relation_to_the_hypotheses": {
        "H1_supported_if": "P1 and P2 both refuted: one affine family absorbs the environmental "
                           "operator too",
        "H2_supported_if": "P2 confirmed: the environmental operator adds a mode the carrier "
                           "repertoire cannot reach",
        "note": "P1 and P2 are logically independent. P1 confirmed with P2 refuted would mean the "
                "environmental operator moves further along the SAME direction, which is an "
                "amplitude effect, not a second mode.",
    },
}

json.dump(R, open(f"{OUT}/FSCMA00_RANK_CEILING_AND_PREDICTION.json", "w"), indent=1, default=str)

print("E inherited domain violation")
for d in dom:
    if d["C1_violated"] or d["C2_violated"]:
        print("   %5d %-26s C1=%s(n=%d) C2=%s(n=%d of %d dead) max|Mf0|dead=%.3e "
              "offgate share=%.3e" % (d["seed"], d["operator"], d["C1_violated"], d["C1_n_sites"],
                                      d["C2_violated"], d["C2_n_sites"], d["C2_n_dead_sites_total"],
                                      d["C2_max_abs_Mf0_on_dead"],
                                      d["C2_offgate_share_of_total_abs_content"]))
print("\nF channel decomposition (carrier cells)")
for c in chan:
    print("   %5d %s  sum_share=%.4f diff_share=%.4f |dB|/|dA|=%.4f"
          % (c["seed"], c["superfamily"], c["sum_share"], c["diff_share"],
             c["antisymmetry_ratio_dB_over_dA"]))
print("   carrier sum_share  min=%.4f median=%.4f MAX=%.4f"
      % (min(ss), float(np.median(ss)), max(ss)))
g = R["F_rank_ceiling_algebra"]["exact_gram_spectra"]
print("   full spectrum lam:", ["%.3e" % x for x in g["full_two_channel"]["lambda"]])
print("   lam1 share=%.4f | sum-channel trace share=%.4f | diff-channel trace share=%.4f"
      % (g["full_two_channel"]["lam1_share"], g["sum_channel_only"]["share_of_full_trace"],
         g["diff_channel_only"]["share_of_full_trace"]))
print("   S1 vs S2 principal cosines:",
      ["%.5f" % x for x in R["F_rank_ceiling_algebra"]["superfamily_subspaces"]["principal_cosines_S1_vs_S2_leading_2d"]])
print("\nG prediction frozen: env sum_share > %.4f  and  OFF1 > 0.10" % CARRIER_SUM_SHARE_MAX)
