"""GIMB00 Phase 1 -- certified gauge-invariant quotient rederivation. ZERO ENGINE STARTS.

Nothing in this file imports an engine, a substrate, a state or a checkpoint. It reads only the
committed exact-rational response rows bound in Phase 0.
"""
from __future__ import annotations
import json, hashlib, itertools, math, time, sys
from fractions import Fraction as Fr
import numpy as np

OUT = "/home/claude/sweep/GIMB00"
FZ = json.load(open(f"{OUT}/GIMB00_MASTER_FREEZE_HASHES.json"))
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
for f, h in FZ["hashes"].items():
    assert sha(f"{OUT}/{f}") == h, f"freeze mutated: {f}"
W = [Fr(x) for x in FZ["weights"]]
T = len(W)
HALF = Fr(1, 2)
WMIN = min(W)
INFL2 = 1 / WMIN                                   # ||z||^2 <= INFL2 * A_bu^2
ROWS = json.load(open(f"{OUT}/GIMB00_BOUND_ROWS.json"))
R = {"engine_starts_before": 0, "freeze_hashes": FZ["hashes"]}
t0 = time.time()


def uvec(r):
    return [Fr(x) + Fr(y) for x, y in zip(r["dA"], r["dB"])]


def vvec(r):
    return [Fr(x) - Fr(y) for x, y in zip(r["dA"], r["dB"])]


def ip(p, q):
    return sum((W[h] * p[h] * q[h] * HALF for h in range(T)), Fr(0))


for pan in ROWS:
    for r in ROWS[pan]:
        r["u"], r["v"] = uvec(r), vvec(r)
        r["zz"] = ip(r["u"], r["u"]) + ip(r["v"], r["v"])          # ||z||^2, exact

# =====================================================================================
# A. ABSOLUTE MATERIALITY -- propagation and the frozen compatibility test
# =====================================================================================
mat = {"constant_squared": str(INFL2), "constant": math.sqrt(float(INFL2)), "cells": []}
compat = True
for pan in ("CARRIER_BASIS", "CARRIER_LOCKED", "ENV_PROBE", "ENV_LOCKED"):
    for r in ROWS[pan]:
        A, E = Fr(r["A_bu"]), Fr(r["ETA_bu"])
        etaz2 = INFL2 * E * E
        material_parent = A > E
        material_z = r["zz"] > etaz2
        if material_parent and not material_z:
            compat = False
        mat["cells"].append({"panel": pan, "seed": r["seed"], "arm": r["arm"],
                             "A_bu": float(A), "ETA_bu": float(E), "A_over_ETA": float(A / E),
                             "z_norm": math.sqrt(float(r["zz"])),
                             "eta_z": math.sqrt(float(etaz2)),
                             "z_over_eta_z": math.sqrt(float(r["zz"] / etaz2)),
                             "parent_called_it_material": bool(material_parent),
                             "L2_bound_calls_it_material": bool(material_z)})
n_bad = sum(1 for c in mat["cells"] if c["parent_called_it_material"]
            and not c["L2_bound_calls_it_material"])
mat["n_cells"] = len(mat["cells"])
mat["n_parent_material"] = sum(1 for c in mat["cells"] if c["parent_called_it_material"])
mat["n_reversed_by_the_propagated_bound"] = n_bad
mat["COMPATIBLE"] = bool(compat)
mat["ABSOLUTE_MATERIALITY_STATUS"] = "AVAILABLE" if compat else "NOT_AVAILABLE"
mat["reasoning"] = (
    "The only rigorous L1->L2 propagation available is ||z|| <= A_bu / sqrt(min_h w_h) = "
    "sqrt(18)*A_bu, attained when the whole response sits on one endpoint of the scored grid. "
    "The frozen compatibility criterion asks whether that bound, applied to the parent's own "
    "accepted cells, reproduces their material status. It does not: it reverses "
    f"{n_bad} of {mat['n_parent_material']} cells the parents accepted as material. A bound that "
    "retrospectively unmakes the parents' own accepted responses is not a compatible restatement "
    "of the inherited threshold in L2 units, and no tighter constant may be improvised."
    if not compat else "the propagated bound reproduces every parent materiality decision.")
R["A_absolute_materiality"] = mat
print("A materiality: constant sqrt(%s)=%.4f | reversed %d of %d parent-material cells -> %s [%.0fs]"
      % (INFL2, math.sqrt(float(INFL2)), n_bad, mat["n_parent_material"],
         mat["ABSOLUTE_MATERIALITY_STATUS"], time.time() - t0))

# =====================================================================================
# B. EXACT QUOTIENT-AFFINE APPROXIMATION  R0, R1, R2  over all 2^(F-1) linked swaps
# =====================================================================================
def panel_arrays(pan):
    rs = sorted(ROWS[pan], key=lambda r: (r["seed"], r["arm"]))
    f = sorted({r["seed"] for r in rs})
    n = len(rs)
    U = [[ip(rs[i]["u"], rs[j]["u"]) for j in range(n)] for i in range(n)]
    V = [[ip(rs[i]["v"], rs[j]["v"]) for j in range(n)] for i in range(n)]
    return rs, f, U, V


def gram_centered(U, V, eps, seeds, alpha):
    """exact alpha-weighted centered Gram of z_i = (u_i, eps_{f(i)} v_i)."""
    n = len(U)
    e = [eps[s] for s in seeds]
    Z = [[U[i][j] + e[i] * e[j] * V[i][j] for j in range(n)] for i in range(n)]
    rowm = [sum((alpha[k] * Z[i][k] for k in range(n)), Fr(0)) for i in range(n)]
    tot = sum((alpha[i] * rowm[i] for i in range(n)), Fr(0))
    return [[Fr(alpha[i]).__mul__(1) * 0 + (Fr(1) * (alpha[i] * alpha[j]) ** 0) * 0
             + (Z[i][j] - rowm[i] - rowm[j] + tot) * alpha[i] if i == j else
             (Z[i][j] - rowm[i] - rowm[j] + tot) * alpha[i]
             for j in range(n)] for i in range(n)], Z


def gram_sym(U, V, eps, seeds, alpha):
    """symmetric version: G[i][j] = sqrt(a_i a_j)(...); all alpha equal so sqrt is rational."""
    n = len(U)
    a = alpha[0]
    assert all(x == a for x in alpha)
    e = [eps[s] for s in seeds]
    Z = [[U[i][j] + e[i] * e[j] * V[i][j] for j in range(n)] for i in range(n)]
    rowm = [sum((a * Z[i][k] for k in range(n)), Fr(0)) for i in range(n)]
    tot = sum((a * rowm[i] for i in range(n)), Fr(0))
    return [[a * (Z[i][j] - rowm[i] - rowm[j] + tot) for j in range(n)] for i in range(n)]


def inertia_below(G, t):
    n = len(G)
    M = [[G[i][j] - (t if i == j else Fr(0)) for j in range(n)] for i in range(n)]
    neg = 0
    for i in range(n):
        p = M[i][i]
        if p == 0:
            return None
        if p < 0:
            neg += 1
        for r_ in range(i + 1, n):
            f = M[r_][i] / p
            if f:
                for c in range(i, n):
                    M[r_][c] -= f * M[i][c]
    return neg


def cnt(G, t):
    for k in range(40):
        v = inertia_below(G, t if k == 0 else t - Fr(1, 10 ** 45) * k)
        if v is not None:
            return v
    raise RuntimeError("inertia")


def lam_bracket(G, k, iters=34):
    n = len(G)
    tr = sum(G[i][i] for i in range(n))
    lo, hi = Fr(0), tr + 1
    for _ in range(iters):
        mid = (lo + hi) / 2
        if cnt(G, mid) <= n - k:
            lo = mid
        else:
            hi = mid
    return lo, hi


rs_b, F_b, U_b, V_b = panel_arrays("CARRIER_BASIS")
n_b = len(rs_b)
ALPHA_B = [Fr(1, n_b)] * n_b
SEEDS_B = [r["seed"] for r in rs_b]
GAUGEF = F_b[0]
ASSIGN = []
for bits in itertools.product([0, 1], repeat=len(F_b) - 1):
    eps = {GAUGEF: 1}
    eps.update({f: (-1 if x else 1) for f, x in zip(F_b[1:], bits)})
    ASSIGN.append(eps)

cand = []
for a_i, eps in enumerate(ASSIGN):
    G = gram_sym(U_b, V_b, eps, SEEDS_B, ALPHA_B)
    tr = sum(G[i][i] for i in range(n_b))
    l1lo, l1hi = lam_bracket(G, 1)
    l2lo, l2hi = lam_bracket(G, 2)
    cand.append({"idx": a_i, "eps": {str(k): v for k, v in eps.items()},
                 "swapped": sorted(k for k, v in eps.items() if v < 0),
                 "trace": tr, "l1": (l1lo, l1hi), "l2": (l2lo, l2hi),
                 "R0": (tr, tr), "R1": (tr - l1hi, tr - l1lo),
                 "R2": (tr - l1hi - l2hi, tr - l1lo - l2lo)})
print("B enumerated %d linked-swap assignments with certified enclosures [%.0fs]"
      % (len(cand), time.time() - t0))


def min_over(key):
    lo = min(c[key][0] for c in cand)
    hi = min(c[key][1] for c in cand)
    return lo, hi


R0 = min_over("R0")
R1 = min_over("R1")
R2 = min_over("R2")
TOL = Fr(1, 10 ** 18)


def cooptimal(key):
    best_hi = min(c[key][1] for c in cand)
    return [c for c in cand if c[key][0] <= best_hi * (1 + TOL) + TOL]


CO1 = cooptimal("R1")
CO0 = cooptimal("R0")
CO2 = cooptimal("R2")
L1 = (R0[0] - R1[1], R0[1] - R1[0])
L2 = (R1[0] - R2[1], R1[1] - R2[0])
qq = {
    "n_assignments": len(cand), "gauge_founder_pinned": GAUGEF,
    "R0": [float(R0[0]), float(R0[1])], "R1": [float(R1[0]), float(R1[1])],
    "R2": [float(R2[0]), float(R2[1])],
    "L1": [float(L1[0]), float(L1[1])], "L2": [float(L2[0]), float(L2[1])],
    "R0_argmin_swapped": [c["swapped"] for c in CO0],
    "R1_argmin_swapped": [c["swapped"] for c in CO1],
    "R2_argmin_swapped": [c["swapped"] for c in CO2],
    "n_cooptimal_R0": len(CO0), "n_cooptimal_R1": len(CO1), "n_cooptimal_R2": len(CO2),
    "note": "R0, R1 and R2 are each minimised over the swaps independently, as specified. Their "
            "differences L1 and L2 are model-complexity gains, NOT singular values.",
}
# ---- gates ------------------------------------------------------------------------------
ETAZ2_B = sum((ALPHA_B[i] * INFL2 * Fr(rs_b[i]["ETA_bu"]) ** 2 for i in range(n_b)), Fr(0))
qq["FROZEN_BETWEEN_RESPONSE_MATERIALITY_ENERGY"] = float(ETAZ2_B)
qq["FROZEN_MODAL_MATERIALITY_AMPLITUDE"] = math.sqrt(float(ETAZ2_B))
qq["QDIM0_absolute"] = None if not compat else bool(R0[0] > ETAZ2_B)
qq["QDIM1_absolute"] = None if not compat else bool(L2[0] > ETAZ2_B)
ratio_lo = math.sqrt(float(L2[0] / L1[1])) if L1[1] > 0 and L2[0] > 0 else 0.0
ratio_hi = math.sqrt(float(L2[1] / L1[0])) if L1[0] > 0 else float("inf")
qq["QUOTIENT_INCREMENT_RATIO"] = [ratio_lo, ratio_hi]
qq["QUOTIENT_SECOND_SHARE"] = [float(L2[0] / R0[1]), float(L2[1] / R0[0])]
qq["QDIM2_ratio_gt_0.10"] = bool(ratio_lo > 0.10)
qq["QDIM3_energy_ge_0.05"] = bool(L2[0] / R0[1] >= Fr(1, 20))
qq["RELATIVE_AT_LEAST_TWO"] = qq["QDIM2_ratio_gt_0.10"] and qq["QDIM3_energy_ge_0.05"]
qq["ONE_FAMILY_AGGREGATE_RESIDUAL"] = [float(R1[0] / R0[1]), float(R1[1] / R0[0])]
qq["K2_AGGREGATE_RESIDUAL"] = [float(R2[0] / R0[1]), float(R2[1] / R0[0])]
R["B_quotient"] = qq
print("B R0=%.4e R1=[%.4e,%.4e] R2=[%.4e,%.4e]" % (float(R0[0]), *qq["R1"], *qq["R2"]))
print("  L1=%.4e L2=%.4e | ratio sqrt(L2/L1) in [%.4f,%.4f] | share L2/R0 in [%.4f,%.4f]"
      % (float(L1[0]), float(L2[0]), ratio_lo, ratio_hi, *qq["QUOTIENT_SECOND_SHARE"]))
print("  QDIM2 %s QDIM3 %s | one-family R1/R0 in [%.4f,%.4f] | k2 R2/R0 in [%.4f,%.4f]"
      % (qq["QDIM2_ratio_gt_0.10"], qq["QDIM3_energy_ge_0.05"],
         *qq["ONE_FAMILY_AGGREGATE_RESIDUAL"], *qq["K2_AGGREGATE_RESIDUAL"]))
print("  R0 argmin swaps:", qq["R0_argmin_swapped"], "| R1 argmin:", qq["R1_argmin_swapped"],
      "| R2 argmin:", qq["R2_argmin_swapped"], "[%.0fs]" % (time.time() - t0))

# =====================================================================================
# C. float working frame for cells, sectors, transfer and the environmental relation
# =====================================================================================
SW = np.array([float(w) ** 0.5 for w in W])
S2 = math.sqrt(2.0)


def zvec(r, e):
    a = np.array([float(Fr(x)) for x in r["dA"]])
    b = np.array([float(Fr(x)) for x in r["dB"]])
    return np.concatenate([SW * (a + b) / S2, e * SW * (a - b) / S2])


def panel_Z(pan, eps):
    rs = sorted(ROWS[pan], key=lambda r: (r["seed"], r["arm"]))
    return np.array([zvec(r, eps[r["seed"]]) for r in rs]), rs


def cellstats(Z, alpha, k, mu=None, B=None):
    if mu is None:
        mu = (alpha[:, None] * Z).sum(0) / alpha.sum()
    D = Z - mu
    if B is None:
        _, s, vt = np.linalg.svd((np.sqrt(alpha)[:, None]) * D, full_matrices=False)
        B = vt[:k]
    Rres = D - (D @ B.T) @ B
    num = (alpha * (Rres ** 2).sum(1)).sum()
    den = (alpha * (D ** 2).sum(1)).sum()
    cell = (Rres ** 2).sum(1) / np.maximum((D ** 2).sum(1), 1e-300)
    return mu, B, num / den, cell, Rres, D


EPS1 = {int(k): v for k, v in CO1[0]["eps"].items()}
ALPH = np.full(n_b, 1.0 / n_b)
ZB, rsB = panel_Z("CARRIER_BASIS", EPS1)
mu1, B1, agg1, cell1, res1, D1 = cellstats(ZB, ALPH, 1)
mu2, B2, agg2, cell2, res2, _ = cellstats(ZB, ALPH, 2)
one_fam = bool(agg1 < 0.05 and cell1.max() < 0.10)
k2_ok = bool(agg2 < 0.05 and cell2.max() < 0.10)
CARRIER_K = 1 if one_fam else (2 if (qq["RELATIVE_AT_LEAST_TWO"] and k2_ok) else "UNRESOLVED")
R["C_basis_family"] = {
    "eps_used": {str(k): v for k, v in EPS1.items()},
    "k1": {"aggregate_residual": float(agg1), "cell_max": float(cell1.max()),
           "cells": [{"seed": rsB[i]["seed"], "arm": rsB[i]["arm"], "resid": float(cell1[i])}
                     for i in range(n_b)], "GATE": one_fam},
    "k2": {"aggregate_residual": float(agg2), "cell_max": float(cell2.max()), "GATE": k2_ok},
    "CARRIER_MODEL_DIMENSION_USED_FOR_ENV_TEST": CARRIER_K}
print("C one-family: agg=%.4f cellmax=%.4f -> %s | k2: agg=%.4f cellmax=%.4f -> %s | K=%s"
      % (agg1, cell1.max(), one_fam, agg2, cell2.max(), k2_ok, CARRIER_K))

# ---- sector attribution via the NESTED extension -----------------------------------------
sect = {}
Bn = np.vstack([B1, np.linalg.svd((np.sqrt(ALPH)[:, None]) * (D1 - (D1 @ B1.T) @ B1),
                                  full_matrices=False)[2][:1]])
a_i = (D1 @ Bn.T) @ Bn - (D1 @ B1.T) @ B1
half = len(mu1) // 2
Pp = (ALPH * (a_i[:, :half] ** 2).sum(1)).sum()
Pm = (ALPH * (a_i[:, half:] ** 2).sum(1)).sum()
tot = Pp + Pm
sect["P_PLUS"] = float(Pp / tot) if tot > 0 else None
sect["P_MINUS"] = float(Pm / tot) if tot > 0 else None
sect["nested_extra_energy"] = float(tot)
sect["SECOND_DEGREE_SECTOR"] = (
    "COMMON" if sect["P_PLUS"] and sect["P_PLUS"] >= 0.95 else
    "DIFFERENTIAL_PROJECTIVE" if sect["P_MINUS"] and sect["P_MINUS"] >= 0.95 else
    "MIXED" if sect["P_PLUS"] and sect["P_PLUS"] >= 0.05 and sect["P_MINUS"] >= 0.05 else
    "SECTOR_ATTRIBUTION_UNRESOLVED")
# stability of the sector label across every co-optimal R1 representative
labels = set()
for c in CO1:
    e = {int(k): v for k, v in c["eps"].items()}
    Zc, _ = panel_Z("CARRIER_BASIS", e)
    m1, b1, _, _, _, Dc = cellstats(Zc, ALPH, 1)
    bn = np.vstack([b1, np.linalg.svd((np.sqrt(ALPH)[:, None]) * (Dc - (Dc @ b1.T) @ b1),
                                      full_matrices=False)[2][:1]])
    ai = (Dc @ bn.T) @ bn - (Dc @ b1.T) @ b1
    pp = (ALPH * (ai[:, :half] ** 2).sum(1)).sum()
    pm = (ALPH * (ai[:, half:] ** 2).sum(1)).sum()
    tt = pp + pm
    labels.add("COMMON" if pp / tt >= 0.95 else "DIFF" if pm / tt >= 0.95 else
               "MIXED" if min(pp, pm) / tt >= 0.05 else "UNRES")
sect["labels_over_cooptima"] = sorted(labels)
if len(labels) > 1:
    sect["SECOND_DEGREE_SECTOR"] = "SECTOR_ATTRIBUTION_UNRESOLVED"
if not compat:
    sect["absolute_materiality_of_the_nested_energy"] = "NOT_AVAILABLE"
R["C_sector"] = sect
print("C sector: P+=%.4f P-=%.4f -> %s (co-optima labels %s)"
      % (sect["P_PLUS"], sect["P_MINUS"], sect["SECOND_DEGREE_SECTOR"], sect["labels_over_cooptima"]))

# =====================================================================================
# D. TRANSFER to CARRIER_LOCKED, no refit; then the environmental relation
# =====================================================================================
def best_eps_for(pan, mu, Bm):
    """one linked swap per founder chosen to minimise that founder's whole-block residual."""
    rs = sorted(ROWS[pan], key=lambda r: (r["seed"], r["arm"]))
    eps = {}
    for s in sorted({r["seed"] for r in rs}):
        idx = [i for i, r in enumerate(rs) if r["seed"] == s]
        best, be = None, 1
        for e in (1, -1):
            Zs = np.array([zvec(rs[i], e) for i in idx])
            Dd = Zs - mu
            rr = ((Dd - (Dd @ Bm.T) @ Bm) ** 2).sum()
            if best is None or rr < best:
                best, be = rr, e
        eps[s] = be
    return eps, rs


def score_panel(pan, mu, Bm, alpha_per_founder=True):
    eps, rs = best_eps_for(pan, mu, Bm)
    Z = np.array([zvec(r, eps[r["seed"]]) for r in rs])
    D = Z - mu
    Rr = D - (D @ Bm.T) @ Bm
    nrows = len(rs)
    al = np.full(nrows, 1.0 / nrows)
    num = (al * (Rr ** 2).sum(1)).sum()
    den = (al * (D ** 2).sum(1)).sum()
    cell = (Rr ** 2).sum(1) / np.maximum((D ** 2).sum(1), 1e-300)
    return {"eps": eps, "rows": rs, "Z": Z, "D": D, "resid": Rr,
            "agg": float(num / den), "cells": cell, "abs_agg": float(num)}


TR = {}
for k, Bm in ((1, B1), (2, B2)):
    st = score_panel("CARRIER_LOCKED", mu1 if k == 1 else mu2, Bm)
    TR[k] = {"LOCKED_AGG_RESIDUAL": st["agg"], "cell_max": float(st["cells"].max()),
             "cells": [{"seed": st["rows"][i]["seed"], "arm": st["rows"][i]["arm"],
                        "resid": float(st["cells"][i])} for i in range(len(st["rows"]))],
             "GATE": bool(st["agg"] < 0.05 and st["cells"].max() < 0.10),
             "eps": {str(a): b for a, b in st["eps"].items()}}
R["D_carrier_transfer"] = TR
basis_gate = one_fam if CARRIER_K == 1 else (k2_ok if CARRIER_K == 2 else None)
locked_gate = TR[1]["GATE"] if CARRIER_K == 1 else (TR[2]["GATE"] if CARRIER_K == 2 else None)
R["D_carrier_transfer"]["CARRIER_QUOTIENT_TRANSFER_STATUS"] = (
    "SAME_GATE_STATUS_ON_CARRIER_LOCKED_WITHOUT_REFIT" if basis_gate == locked_gate
    else "DOES_NOT_TRANSFER_TO_CARRIER_LOCKED") if CARRIER_K != "UNRESOLVED" else "NUMERICALLY_UNRESOLVED"
print("D transfer k=1 agg=%.4f cellmax=%.4f | k=2 agg=%.4f cellmax=%.4f -> %s"
      % (TR[1]["LOCKED_AGG_RESIDUAL"], TR[1]["cell_max"], TR[2]["LOCKED_AGG_RESIDUAL"],
         TR[2]["cell_max"], R["D_carrier_transfer"]["CARRIER_QUOTIENT_TRANSFER_STATUS"]))

# ---- LOAO tube radius --------------------------------------------------------------------
loao = 0.0
for s in F_b:
    keep = [i for i, r in enumerate(rsB) if r["seed"] != s]
    drop = [i for i, r in enumerate(rsB) if r["seed"] == s]
    al = np.full(len(keep), 1.0 / len(keep))
    m, b, _, _, _, _ = cellstats(ZB[keep], al, 1 if CARRIER_K != 2 else 2)
    Dd = ZB[drop] - m
    rr = ((Dd - (Dd @ b.T) @ b) ** 2).sum(1) / (Dd ** 2).sum(1)
    loao = max(loao, float(rr.max()))
R["D_LOAO_TUBE_RADIUS"] = loao

# ---- environmental relation ---------------------------------------------------------------
KUSE = 1 if CARRIER_K == 1 else 2
MU, BM = (mu1, B1) if KUSE == 1 else (mu2, B2)
env = {}
for pan in ("ENV_PROBE", "ENV_LOCKED", "ENV_DOSE_SECONDARY"):
    st = score_panel(pan, MU, BM)
    ru, rv = st["resid"][:, :half], st["resid"][:, half:]
    fp = (ru ** 2).sum() / ((ru ** 2).sum() + (rv ** 2).sum())
    shares = (st["resid"] ** 2).sum(1) / (st["resid"] ** 2).sum()
    env[pan] = {"OFF_MODEL_FRAC_AGG": st["agg"], "cells": st["cells"].tolist(),
                "cells_ge_0.05": int((st["cells"] >= 0.05).sum()), "n_cells": len(st["cells"]),
                "min_cell": float(st["cells"].min()),
                "F_PLUS": float(fp), "F_MINUS": float(1 - fp),
                "max_single_founder_share": float(shares.max()),
                "abs_agg": st["abs_agg"],
                "mean_direction": (st["Z"].mean(0) / np.linalg.norm(st["Z"].mean(0))).tolist()}
dP = np.array(env["ENV_PROBE"]["mean_direction"])
dL = np.array(env["ENV_LOCKED"]["mean_direction"])
dD = np.array(env["ENV_DOSE_SECONDARY"]["mean_direction"])
env["stability_cos_probe_vs_locked"] = float(abs(dP @ dL))
env["stability_cos_dose"] = float(abs(dP @ dD))
sep_ok = all(env[p]["OFF_MODEL_FRAC_AGG"] >= 0.05 and env[p]["cells_ge_0.05"] >= 5
             and env[p]["min_cell"] > loao and env[p]["max_single_founder_share"] <= 1 / 3
             for p in ("ENV_PROBE", "ENV_LOCKED")) and env["stability_cos_probe_vs_locked"] >= 0.80
inside = all(env[p]["OFF_MODEL_FRAC_AGG"] < 0.05 and max(env[p]["cells"]) < 0.10
             for p in ("ENV_PROBE", "ENV_LOCKED"))
fpmin = min(env["ENV_PROBE"]["F_PLUS"], env["ENV_LOCKED"]["F_PLUS"])
fmmin = min(env["ENV_PROBE"]["F_MINUS"], env["ENV_LOCKED"]["F_MINUS"])
if inside:
    lab = "IN_CARRIER_QUOTIENT_FAMILY"
elif not sep_ok:
    lab = "OFF_FAMILY_EXTENSION_UNRESOLVED"
elif fpmin >= 0.95:
    lab = "ENVIRONMENTAL_COMMON_MODE_ONLY"
elif fmmin >= 0.95:
    lab = "OPERATOR_SPECIFIC_DIFFERENTIAL_EXTENSION"
elif fpmin >= 0.05 and fmmin >= 0.05:
    lab = "OPERATOR_SPECIFIC_MIXED_EXTENSION"
else:
    lab = "OFF_FAMILY_EXTENSION_UNRESOLVED"
if CARRIER_K == "UNRESOLVED":
    lab = "OFF_FROZEN_K2_CARRIER_APPROXIMATION"
env["separation_gates_pass"] = bool(sep_ok)
env["LOAO_TUBE_RADIUS"] = loao
env["ENVIRONMENTAL_QUOTIENT_RELATION_ON_EXPOSED_ROWS"] = lab
R["E_environment"] = env
print("E env: PROBE off=%.4f (min cell %.4f) LOCKED off=%.4f (min cell %.4f) | LOAO=%.4f"
      % (env["ENV_PROBE"]["OFF_MODEL_FRAC_AGG"], env["ENV_PROBE"]["min_cell"],
         env["ENV_LOCKED"]["OFF_MODEL_FRAC_AGG"], env["ENV_LOCKED"]["min_cell"], loao))
print("   F+ probe=%.4f locked=%.4f | stability=%.6f dose=%.6f -> %s"
      % (env["ENV_PROBE"]["F_PLUS"], env["ENV_LOCKED"]["F_PLUS"],
         env["stability_cos_probe_vs_locked"], env["stability_cos_dose"], lab))

# =====================================================================================
# F. THE PARENT-ALIASED FOUNDER STRATUM in the quotient
# =====================================================================================
QMAP = {s: (1 if s % 2 == 0 else -1) for s in sorted({r["seed"] for r in ROWS["CARRIER_BASIS"]}
                                                     | {r["seed"] for r in ROWS["CARRIER_LOCKED"]})}
str_ = {"partition_source": "committed construction code: make_founder assigns (HIST_H,HIST_L) on "
                            "even seeds and (HIST_L,HIST_H) on odd seeds; the frozen queue makes "
                            "even seeds FAR and odd NEAR. Named only PARENT_ALIASED_FOUNDER_STRATUM.",
        "q_map": {str(k): v for k, v in QMAP.items()},
        "support_BASIS": {str(v): sorted(s for s in F_b if QMAP[s] == v) for v in (-1, 1)},
        "support_LOCKED": {str(v): sorted(s for s in sorted({r["seed"] for r in ROWS["CARRIER_LOCKED"]})
                                          if QMAP[s] == v) for v in (-1, 1)}}
str_["support_3_plus_3_BASIS"] = all(len(v) == 3 for v in str_["support_BASIS"].values())
str_["support_3_plus_3_LOCKED"] = all(len(v) == 3 for v in str_["support_LOCKED"].values())


def stratum_residuals(eps):
    Z, rs = panel_Z("CARRIER_BASIS", eps)
    al = np.full(len(rs), 1.0 / len(rs))
    mu0 = Z.mean(0)
    r0 = (al * ((Z - mu0) ** 2).sum(1)).sum()
    q = np.array([QMAP[r["seed"]] for r in rs])
    r2 = 0.0
    cents = {}
    for lv in (-1, 1):
        m = q == lv
        cents[lv] = Z[m].mean(0)
        r2 += (al[m] * ((Z[m] - cents[lv]) ** 2).sum(1)).sum()
    return r0, r2, mu0, cents, Z, rs, q


best = None
for c in cand:
    e = {int(k): v for k, v in c["eps"].items()}
    r0, r2s, mu0, cents, Z, rs, q = stratum_residuals(e)
    if best is None or r0 < best[0]:
        best = (r0, r2s, mu0, cents, Z, rs, q, e)
r0s, r2s, mu0, cents, Zs, rss, qv, eps_s = best
E_STR = r0s - r2s
str_["R_STRATUM_0"] = float(r0s)
str_["R_STRATUM_2MEAN"] = float(r2s)
str_["E_STRATUM"] = float(E_STR)
str_["STRATUM_SHARE"] = float(E_STR / r0s) if r0s > 0 else None
a_str = np.array([cents[qv[i]] - mu0 for i in range(len(rss))])
al = np.full(len(rss), 1.0 / len(rss))
Ep = (al * (a_str[:, :half] ** 2).sum(1)).sum()
Em = (al * (a_str[:, half:] ** 2).sum(1)).sum()
str_["E_STRATUM_PLUS"] = float(Ep)
str_["E_STRATUM_MINUS"] = float(Em)
str_["P_STRATUM_PLUS"] = float(Ep / (Ep + Em))
str_["P_STRATUM_MINUS"] = float(Em / (Ep + Em))
str_["sector"] = ("COMMON" if str_["P_STRATUM_PLUS"] >= 0.95 else
                  "DIFFERENTIAL_PROJECTIVE" if str_["P_STRATUM_MINUS"] >= 0.95 else
                  "MIXED" if min(str_["P_STRATUM_PLUS"], str_["P_STRATUM_MINUS"]) >= 0.05
                  else "UNRESOLVED")
str_["relative_share_ge_0.05"] = bool(str_["STRATUM_SHARE"] >= 0.05)
str_["ABSOLUTE_MATERIALITY"] = "NOT_AVAILABLE" if not compat else (
    "PASS" if E_STR > float(ETAZ2_B) else "FAIL")
str_["FOUNDER_STRATUM_QUOTIENT_STATUS"] = (
    "SURVIVES_IN_QUOTIENT__ORIGIN_UNRESOLVED"
    if (str_["relative_share_ge_0.05"] and str_["ABSOLUTE_MATERIALITY"] == "PASS"
        and str_["support_3_plus_3_BASIS"] and str_["support_3_plus_3_LOCKED"])
    else "NUMERICALLY_UNRESOLVED" if not compat else "COLLAPSES_IN_QUOTIENT")
R["F_stratum"] = str_
print("F stratum: share=%.4f sector=%s (P+=%.4f) abs=%s -> %s"
      % (str_["STRATUM_SHARE"], str_["sector"], str_["P_STRATUM_PLUS"],
         str_["ABSOLUTE_MATERIALITY"], str_["FOUNDER_STRATUM_QUOTIENT_STATUS"]))

# =====================================================================================
# G. LOSSY-COORDINATE SENSITIVITY (never a vote)
# =====================================================================================
def rank_in(coord):
    rs = sorted(ROWS["CARRIER_BASIS"], key=lambda r: (r["seed"], r["arm"]))
    M = []
    for r in rs:
        a = np.array([float(Fr(x)) for x in r["dA"]])
        b = np.array([float(Fr(x)) for x in r["dB"]])
        if coord == "abs_v":
            M.append(np.abs(SW * (a - b)))
        elif coord == "elem_sym":
            M.append(np.concatenate([SW * (a + b), np.sign(a * b) * np.sqrt(np.abs(a * b)) * SW]))
        elif coord == "per_row_vvT":
            v = SW * (a - b) / S2
            M.append(np.concatenate([SW * (a + b) / S2, np.outer(v, v)[np.triu_indices(T)]]))
    M = np.array(M)
    Mc = M - M.mean(0)
    s = np.linalg.svd(Mc, compute_uv=False)
    return {"sigma2_over_sigma1": float(s[1] / s[0]),
            "second_share": float(s[1] ** 2 / (s ** 2).sum()),
            "one_family_residual": float(1 - s[0] ** 2 / (s ** 2).sum())}


R["G_lossy_sensitivity"] = {c: rank_in(c) for c in ("abs_v", "elem_sym", "per_row_vvT")}
R["G_lossy_sensitivity"]["status"] = ("SENSITIVITY_ONLY -- a disagreement here means the lossy or "
                                      "quadratic coordinate changed the question, not that a "
                                      "better answer was found. No coordinate is selected.")

# =====================================================================================
# H. PHASE 1 DISPOSITION
# =====================================================================================
if not compat:
    CQS = "RELATIVE_DIMENSION_ONLY__NO_COMPATIBLE_ABSOLUTE_BOUND"
elif qq["RELATIVE_AT_LEAST_TWO"]:
    CQS = "AT_LEAST_TWO__" + {"COMMON": "COMMON", "DIFFERENTIAL_PROJECTIVE": "DIFFERENTIAL_PROJECTIVE",
                              "MIXED": "MIXED"}.get(sect["SECOND_DEGREE_SECTOR"], "MODE_UNATTRIBUTED")
elif one_fam:
    CQS = "ONE_AFFINE_FAMILY_AT_5_PERCENT_GATE"
else:
    CQS = "NONAFFINE_OR_HIGHER_DIMENSION_STRUCTURE_UNRESOLVED"
R["H_disposition"] = {
    "OFFLINE_INVARIANT_STATUS": ("RELATIVE_ONLY_NO_ABSOLUTE_MATERIALITY" if not compat
                                 else "POST_HOC_GI_REDERIVATION_COMPLETE"),
    "CARRIER_QUOTIENT_STRUCTURE": CQS,
    "CARRIER_QUOTIENT_TRANSFER_STATUS": R["D_carrier_transfer"]["CARRIER_QUOTIENT_TRANSFER_STATUS"],
    "ENVIRONMENTAL_QUOTIENT_RELATION_ON_EXPOSED_ROWS": lab,
    "FOUNDER_STRATUM_QUOTIENT_STATUS": str_["FOUNDER_STRATUM_QUOTIENT_STATUS"],
    "PHASE2_LICENSE": ("YES" if (str_["FOUNDER_STRATUM_QUOTIENT_STATUS"]
                                 == "SURVIVES_IN_QUOTIENT__ORIGIN_UNRESOLVED" and compat)
                       else "NO"),
    "RELATIVE_AT_LEAST_TWO": qq["RELATIVE_AT_LEAST_TWO"],
    "engine_starts_phase1": 0,
}
R["engine_starts_after"] = 0
assert R["engine_starts_before"] == R["engine_starts_after"] == 0
json.dump(R, open(f"{OUT}/OFFLINE_GI_SCORES_AND_CERTIFIED_INTERVALS.json", "w"), indent=1, default=str)
print("\nH", json.dumps(R["H_disposition"], indent=1))
print("total %.0fs" % (time.time() - t0))
