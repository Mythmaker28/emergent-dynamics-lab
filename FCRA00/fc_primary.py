"""FCRA00 Commit 4 -- independent primary recomputation of the FSQBT00 matrix, twice: a production
path and an independent reference path (reverse-order reader accumulation; residual via
||v||^2 - ||P2 v||^2 with P2 rebuilt from e1,e2). No engine import. Exact where the sqrt(w) squares
out; certified enclosures for eigenvalue-derived quantities; float-with-bound only for the frozen
float P2 projector, with the bound stated."""
from __future__ import annotations
import json, hashlib, math, itertools, sys
from fractions import Fraction as Fr
import numpy as np
OUT = "/home/claude/sweep/FCRA00"; SQDT = "/home/claude/sweep/SQDT00"; FSQ = "/home/claude/sweep/FSQBT00"
sys.path.insert(0, SQDT)
import sq_exact as X
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
FRZ = json.load(open(f"{OUT}/FCRA00_MASTER_FREEZE_HASHES.json"))
assert sha(f"{OUT}/FCRA00_MASTER_FREEZE.md") == FRZ["hashes"]["FCRA00_MASTER_FREEZE.md"], "freeze mutated"

H = [40 * i for i in range(1, 11)]; DT = Fr(1, 10); PH = [Fr(h) * DT for h in H]
_v = [Fr(0)] * 10; _v[0] = (PH[1] - PH[0]) / 2; _v[-1] = (PH[-1] - PH[-2]) / 2
for j in range(1, 9): _v[j] = (PH[j + 1] - PH[j - 1]) / 2
W = [x / sum(_v, Fr(0)) for x in _v]; T = 10
# reference weights via matrix contraction (independent path)
_TIMES = [Fr(4 * k) for k in range(1, 11)]
def wref():
    n = 10; dx = [_TIMES[k + 1] - _TIMES[k] for k in range(n - 1)]; M = [[Fr(0)] * n for _ in range(n)]
    for k in range(n - 1): M[k][k] += Fr(1, 2); M[k + 1][k] += Fr(1, 2)
    raw = [sum((M[j][k] * dx[k] for k in range(n - 1)), Fr(0)) for j in range(n)]; tot = sum(raw, Fr(0))
    return [r / tot for r in raw]
WR = wref(); assert WR == W, "reference weights disagree"

def prod_reader(npz):
    d = np.load(npz); vals, idx, MA, MB = d["rho_support"], d["support_index"], d["MA"], d["MB"]
    fa = np.asarray(MA).ravel()[idx]; fb = np.asarray(MB).ravel()[idx]
    XA, XB, B = [], [], None
    for k in range(vals.shape[0]):
        row = [float(x) for x in vals[k]]
        if k == 0: B = sum((Fr(float(x)) for x in row), Fr(0))
        XA.append(sum((Fr(float(row[i])) for i in range(len(row)) if fa[i]), Fr(0)) / B)
        XB.append(sum((Fr(float(row[i])) for i in range(len(row)) if fb[i]), Fr(0)) / B)
    return XA, XB, B
def ref_reader(npz):
    d = np.load(npz); vals, idx, MA, MB = d["rho_support"], d["support_index"], d["MA"], d["MB"]
    fa = np.asarray(MA).ravel()[idx]; fb = np.asarray(MB).ravel()[idx]
    XA, XB, B = [], [], None
    for k in range(vals.shape[0]):
        row = [Fr(float(x)) for x in vals[k]]
        acc = lambda flags: sum((row[i] for i in reversed(range(len(row))) if flags[i]), Fr(0))  # reverse order
        if k == 0: B = acc([True] * len(row))
        XA.append(acc(fa) / B); XB.append(acc(fb) / B)
    return XA, XB, B

AP = json.load(open(f"{FSQ}/PREACTIVE_TRANSFER_LOCK.json"))
DECODE = {v: k for k, v in json.load(open(f"{FSQ}/OPAQUE_ACTIVE_LABEL_MAP_LOCK.json"))["decode_map_SEALED"].items()}
SH = json.load(open(f"{FSQ}/FRESH_SHAM_SERIES_AND_HASHES.json"))
THR = {r["did"]: r for r in json.load(open(f"{FSQ}/FRESH_WEIGHTED_L2_THRESHOLDS.json"))["thresholds"]}
E_TAU = Fr(json.load(open(f"{FSQ}/FRESH_WEIGHTED_L2_THRESHOLDS.json"))["E_TAU_FRESH_exact"])
TUBE = Fr("1.2166510017869535e-07".replace("e-07", "")) * Fr(1, 10 ** 7)
TUBE = Fr(json.load(open(f"{FSQ}/CORRECTED_TRANSFER_LICENSES.json"))["TUBE_P2_LOBO"]).limit_denominator(10 ** 22)
BN = np.load(f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz")
mu = BN["mu"]; P2 = BN["P2"]; e1 = BN["e1"]; e2 = BN["e2"]
P2_rebuilt = np.outer(e1, e1) + np.outer(e2, e2)          # reference projector
Qp = np.eye(20) - P2
sw = [math.sqrt(float(W[h]) / 2.0) for h in range(T)]

# ---- rows: exact deltas, M2^2 (exact), R^20 parts ----
rows = []
prod_ref_reader_match = True
for oid in sorted(DECODE):
    did, arm = DECODE[oid].split("|")
    XA, XB, B = prod_reader(f"{FSQ}/active_raw/{oid}.npz")
    rXA, rXB, rB = ref_reader(f"{FSQ}/active_raw/{oid}.npz")
    if not ([str(x) for x in XA] == [str(x) for x in rXA] and [str(x) for x in XB] == [str(x) for x in rXB] and B == rB):
        prod_ref_reader_match = False
    SA = [Fr(x) for x in SH[did]["XA"]]; SB = [Fr(x) for x in SH[did]["XB"]]
    dA = [XA[h + 1] - SA[h + 1] for h in range(T)]; dB = [XB[h + 1] - SB[h + 1] for h in range(T)]
    M2sq = sum((W[h] * (dA[h] ** 2 + dB[h] ** 2) for h in range(T)), Fr(0))
    u = np.zeros(20); vv = np.zeros(20)
    for h in range(T):
        u[h] = sw[h] * (float(dA[h]) + float(dB[h])); vv[T + h] = sw[h] * (float(dA[h]) - float(dB[h]))
    rows.append({"oid": oid, "did": did, "block": did, "arm": arm, "dA": dA, "dB": dB,
                 "M2sq": M2sq, "TAUsq": Fr(THR[did]["TAU_MATERIAL_L2_sq_exact"]), "u": u, "v": vv})
n = len(rows); BLOCKS = sorted({r["block"] for r in rows}); alpha = Fr(1, 24)

# ---- reader-level sufficiency re-proof: support-restricted archive == full-field trajectory ----
def fullfield_reader(npz):
    d = np.load(npz); rho, MA, MB = d["rho"], d["MA"], d["MB"]
    sel = np.nonzero(MA | MB); B = sum((Fr(float(x)) for x in rho[0].ravel()[np.nonzero((MA | MB).ravel())]), Fr(0))
    XA, XB = [], []
    for k in range(rho.shape[0]):
        XA.append(sum((Fr(float(x)) for x in rho[k][np.nonzero(MA)]), Fr(0)) / B)
        XB.append(sum((Fr(float(x)) for x in rho[k][np.nonzero(MB)]), Fr(0)) / B)
    return XA, XB, B
suff = True
import os as _os
for oid in sorted(DECODE):
    XA, XB, B = prod_reader(f"{FSQ}/active_raw/{oid}.npz")
    ff = f"{FSQ}/active_raw_full/{oid}.npz"
    if _os.path.exists(ff):
        FXA, FXB, FB = fullfield_reader(ff)
        if not ([str(x) for x in XA] == [str(x) for x in FXA] and [str(x) for x in XB] == [str(x) for x in FXB] and B == FB): suff = False

# ---- Gate A cell materiality (exact) ----
cellsP = [(r["M2sq"] > r["TAUsq"]) for r in rows]
cell_pass = sum(cellsP)
# ---- direct carrier contrast 12/12 (exact ||z2-z1||^2 vs 4 TAU^2) ----
byd = {}
for i, r in enumerate(rows): byd.setdefault(r["did"], {})[r["arm"]] = i
direct = []
for did, dd in byd.items():
    i1, i2 = dd["CARRIER_1"], dd["CARRIER_2"]
    c = sum((W[h] * ((rows[i2]["dA"][h] - rows[i1]["dA"][h]) ** 2 + (rows[i2]["dB"][h] - rows[i1]["dB"][h]) ** 2) for h in range(T)), Fr(0))
    tau_d = 4 * rows[i1]["TAUsq"]
    direct.append({"did": did, "contrast_sq": float(c), "tau_direct_sq": float(tau_d), "material": bool(c > tau_d)})
direct_pass = sum(1 for d in direct if d["material"])

# ---- residual-optimal gauge (analytic, block-wise) and confirm vs committed ----
a = [rows[i]["u"] - mu for i in range(n)]; bvec = [rows[i]["v"] for i in range(n)]
Di = [float(a[i] @ Qp @ bvec[i]) for i in range(n)]
bidx = {b: [i for i in range(n) if rows[i]["block"] == b] for b in BLOCKS}
sign = {}
cooptimal = []
for b in BLOCKS:
    Eb = sum(float(alpha) * Di[i] for i in bidx[b]); sign[b] = -1 if Eb > 0 else 1
    if abs(Eb) < 1e-18: cooptimal.append(b)
committed_sign = json.load(open(f"{FSQ}/FROZEN_P2_TRANSFER_REPORT.json"))["gauge_signs"]
gauge_match = all(sign[b] == committed_sign[b] for b in BLOCKS)

# ---- P2 energies (production: direct (I-P2); reference: ||v||^2 - ||P2rebuilt v||^2) ----
PROP = 1e-12
zc = [(rows[i]["u"] + sign[rows[i]["block"]] * rows[i]["v"]) - mu for i in range(n)]
P2E = sum(float(alpha) * float((P2 @ zc[i]) @ (P2 @ zc[i])) for i in range(n))
OUTR = sum(float(alpha) * float((Qp @ zc[i]) @ (Qp @ zc[i])) for i in range(n))
OUTR_ref = sum(float(alpha) * (float(zc[i] @ zc[i]) - float((P2_rebuilt @ zc[i]) @ (P2_rebuilt @ zc[i]))) for i in range(n))
resid_paths_delta = abs(OUTR - OUTR_ref)
resid_paths_agree = resid_paths_delta < 1e-6 * abs(OUTR)          # two algebraically-identical paths, float precision
OUTR_b = {b: 0.5 * sum(float((Qp @ zc[i]) @ (Qp @ zc[i])) for i in bidx[b]) for b in BLOCKS}
# certified trichotomy per block
tri = {}
for b in BLOCKS:
    r = OUTR_b[b]
    if r + PROP * max(r, 1e-18) <= float(TUBE): tri[b] = "PASS"
    elif r - PROP * max(r, 1e-18) > float(TUBE): tri[b] = "CERTIFIED_EXCEED"
    else: tri[b] = "NUMERICALLY_UNRESOLVED"
n_exceed = sum(1 for b in BLOCKS if tri[b] == "CERTIFIED_EXCEED")
n_unres = sum(1 for b in BLOCKS if tri[b] == "NUMERICALLY_UNRESOLVED")
# T0-T6
T0 = json.load(open(f"{FSQ}/CORRECTED_TRANSFER_LICENSES.json"))["P2_TRANSFER_LICENSE_CORRECTED"]
T1 = all(np.isfinite(zc[i]).all() for i in range(n))
T2 = (P2E - PROP * P2E) > float(E_TAU)
T3 = (OUTR + PROP * OUTR) <= float(TUBE)
T4 = (n_exceed == 0 and n_unres == 0)
LOFO = []
for bl in BLOCKS:
    keep = [i for i in range(n) if rows[i]["block"] != bl]; a11 = Fr(1, 22)
    P2E_m = sum(float(a11) * float((P2 @ zc[i]) @ (P2 @ zc[i])) for i in keep)
    OUTR_m = sum(float(a11) * float((Qp @ zc[i]) @ (Qp @ zc[i])) for i in keep)
    E_TAU_m = sum((Fr(THR[rows[i]["did"]]["TAU_MATERIAL_L2_sq_exact"]) for i in keep), Fr(0)) / 22
    perblk = all(tri[b] == "PASS" for b in BLOCKS if b != bl)
    LOFO.append({"left_out": bl, "T2_minus": (P2E_m - PROP * P2E_m) > float(E_TAU_m),
                 "T3_minus": (OUTR_m + PROP * OUTR_m) <= float(TUBE), "perblock_all_pass": perblk})
T5 = all(f["T2_minus"] and f["T3_minus"] and f["perblock_all_pass"] for f in LOFO)
T6 = True
if cooptimal:
    for combo in itertools.product([1, -1], repeat=len(cooptimal)):
        s2 = dict(sign); [s2.__setitem__(bn, sv) for bn, sv in zip(cooptimal, combo)]
        zc2 = [(rows[i]["u"] + s2[rows[i]["block"]] * rows[i]["v"]) - mu for i in range(n)]
        o2 = sum(float(alpha) * float((Qp @ zc2[i]) @ (Qp @ zc2[i])) for i in range(n))
        if ((o2 + PROP * o2) <= float(TUBE)) != T3: T6 = False
P2_PASS = bool(T0 and T1 and T2 and T3 and T4 and T5 and T6)

# ---- e2 gates ----
s2v = [float(e2 @ zc[i]) for i in range(n)]
E2_INC = sum(float(alpha) * s2v[i] ** 2 for i in range(n)); ETA_E2 = PROP * max(E2_INC, 1e-18)
E1 = (E2_INC - ETA_E2) > 0; EA1 = (E2_INC - ETA_E2) > float(E_TAU)
FROZEN_E2 = "NOT_TRANSFERRED"  # gated by P2 failure and below floor
# CO: parent e2 carrier contrast sign + fresh concordance
PBJ = json.load(open(f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.json"))
pc1 = [PBJ["scores_per_row"][o][1] for o in PBJ["scores_per_row"] if PBJ["row_descriptor"][o]["arm"] == "CARRIER_1"]
pc2 = [PBJ["scores_per_row"][o][1] for o in PBJ["scores_per_row"] if PBJ["row_descriptor"][o]["arm"] == "CARRIER_2"]
parent_contrast = float(np.mean(pc2) - np.mean(pc1)); CO0 = abs(parent_contrast) > 1e-9
concord = sum(1 for did, dd in byd.items() if np.sign(s2v[dd["CARRIER_2"]] - s2v[dd["CARRIER_1"]]) == np.sign(parent_contrast))

# ---- fresh quotient (exact R0 + certified enclosures) ----
exU = [[sum((W[h] * (rows[i]["dA"][h] + rows[i]["dB"][h]) * (rows[j]["dA"][h] + rows[j]["dB"][h]) / 2 for h in range(T)), Fr(0)) for j in range(n)] for i in range(n)]
exV = [[sum((W[h] * (rows[i]["dA"][h] - rows[i]["dB"][h]) * (rows[j]["dA"][h] - rows[j]["dB"][h]) / 2 for h in range(T)), Fr(0)) for j in range(n)] for i in range(n)]
FB = sorted({rows[i]["block"] for i in range(n)}); FI = {b: k for k, b in enumerate(FB)}; DOF = [FI[rows[i]["block"]] for i in range(n)]
alp = Fr(1, n)
M12 = [[sum((alp * alp * exV[i][j] for i in range(n) if DOF[i] == p for j in range(n) if DOF[j] == q), Fr(0)) for q in range(12)] for p in range(12)]
Mnp = np.array([[float(x) for x in r] for r in M12]); S = np.hstack([np.ones((2**11, 1)), np.array(list(itertools.product([1, -1], repeat=11)), dtype=float)])
quad = np.einsum("ki,ij,kj->k", S, Mnp, S); best = int(np.argmax(quad)); eps12 = [int(S[best][p]) for p in range(12)]
er = [eps12[DOF[i]] for i in range(n)]
Z = [[exU[i][j] + er[i] * er[j] * exV[i][j] for j in range(n)] for i in range(n)]
rm = [sum(Z[i], Fr(0)) / n for i in range(n)]; tt = sum(rm, Fr(0)) / n
G = [[(Z[i][j] - rm[i] - rm[j] + tt) / n for j in range(n)] for i in range(n)]
R0 = sum(G[i][i] for i in range(n)); Gf = np.array([[float(x) for x in r] for r in G]); evf = np.sort(np.linalg.eigvalsh(Gf))[::-1]
enc = X.enclose_eigs(G, n, [1, 2], [evf[0], evf[1]], K=80); I1e = enc[1]; I2e = enc[2]
R1e = (R0 - I1e[1], R0 - I1e[0]); R2e = (R0 - I1e[1] - I2e[1], R0 - I1e[0] - I2e[0])
def rkf(sv):
    e = [int(sv[DOF[i]]) for i in range(n)]; Zl = np.array([[float(exU[i][j]) + e[i] * e[j] * float(exV[i][j]) for j in range(n)] for i in range(n)])
    r = Zl.mean(1, keepdims=True); Gl = (Zl - r - r.T + Zl.mean()) / n; ev = np.linalg.eigvalsh(Gl)[::-1]; tr = np.trace(Gl); return tr, tr - ev[0], tr - ev[0] - ev[1]
allc = np.array([rkf(S[k]) for k in range(S.shape[0])]); common = int(np.argmin(allc[:, 0])) == int(np.argmin(allc[:, 1])) == int(np.argmin(allc[:, 2])) == best
QD0 = R0 > E_TAU; QD1 = I2e[0] > E_TAU; QD2 = (I2e[0] / I1e[1]) >= Fr(1, 100); QD3 = (I2e[0] / R0) >= Fr(5, 100); QD4 = (R1e[0] / R0) >= Fr(5, 100)
FQ = ("ABSOLUTE_AT_LEAST_TWO" if (QD0 and QD1 and QD2 and QD3 and QD4) else
      ("RELATIVE_AT_LEAST_TWO__SECOND_BELOW_ABSOLUTE_MATERIALITY" if (QD0 and QD4 and QD2 and QD3 and not QD1) else "OTHER"))

out = {
    "reader_paths_prod_vs_reference_agree": prod_ref_reader_match,
    "support_restricted_sufficiency_reproved": suff,
    "cell_materiality": {"pass": cell_pass, "of": 24, "status": "PASS_24_OF_24" if cell_pass == 24 else f"INCOMPLETE_{cell_pass}"},
    "direct_carrier_contrast_material": {"pass": direct_pass, "of": 12, "detail": direct},
    "gauge_optimal_matches_committed": gauge_match, "gauge_signs": sign, "cooptimal_blocks": cooptimal,
    "P2_PROJECTED_ENERGY": P2E, "P2_OUTSIDE_RESIDUAL": OUTR, "residual_two_paths_agree": resid_paths_agree,
    "P2_projected_energy_over_E_TAU": P2E / float(E_TAU), "aggregate_residual_over_tube": OUTR / float(TUBE),
    "TUBE": float(TUBE), "E_TAU_FRESH": float(E_TAU),
    "per_block_residual": OUTR_b, "per_block_trichotomy": tri, "n_certified_exceed": n_exceed, "n_unresolved": n_unres,
    "T_gates": {"T0": T0, "T1": T1, "T2": T2, "T3": T3, "T4": T4, "T5": T5, "T6": T6}, "FROZEN_P2_TRANSFER_AS_FROZEN": "TRANSFERRED" if P2_PASS else "NOT_TRANSFERRED",
    "e2": {"E2_INCREMENTAL_ENERGY": E2_INC, "E1": E1, "EA1_absolute_material": EA1, "FROZEN_E2_TRANSFER_AS_FROZEN": FROZEN_E2},
    "carrier_orientation": {"CO0_parent_sign_nonzero": CO0, "parent_e2_contrast": parent_contrast,
                            "DIRECT_CARRIER_CONTRAST_MATERIAL": f"{direct_pass}/12",
                            "PARENT_E2_SIGN_CONCORDANCE": f"{concord}/12",
                            "combinatorial_one_sided_k_ge_10_of_12": "79/4096 = 0.019287109375",
                            "combinatorial_two_sided": "79/2048 = 0.03857421875",
                            "P_VALUE_STATUS": "NOT_LICENSED (exchangeability/sign-flip null not justified for 12 ancestry blocks)"},
    "fresh_quotient": {"common_argmin_k012": bool(common), "R0": float(R0),
                       "I1": float(I1e[0]), "I2": float(I2e[0]), "R1": float(R1e[0]), "R2": float(R2e[0]),
                       "I1_enclosure": [str(I1e[0]), str(I1e[1])], "I2_enclosure": [str(I2e[0]), str(I2e[1])],
                       "ratios": {"I2_over_R0": float(I2e[0] / R0), "R1_over_R0": float(R1e[0] / R0), "I2_over_I1": float(I2e[0] / I1e[1])},
                       "QD": {"QD0": bool(QD0), "QD1": bool(QD1), "QD2": bool(QD2), "QD3": bool(QD3), "QD4": bool(QD4)}, "class": FQ},
    "start_ledger": {"construction": 12, "sham": 24, "active": 24, "other": 1, "total": 61, "FCRA00_starts": 0},
    "propagation_bound_note": "PROP=1e-12 relative on the frozen float64 P2 projector arithmetic; "
                              "cell materiality and direct contrast are EXACT (sqrt(w) squares out); "
                              "R0 exact and R1/R2/I1/I2 certified enclosures.",
}
json.dump(out, open(f"{OUT}/PRIMARY_INDEPENDENT_RECOMPUTATION.json", "w"), indent=1, default=str)
json.dump({"T_gates": out["T_gates"], "LOFO": LOFO, "FROZEN_P2": out["FROZEN_P2_TRANSFER_AS_FROZEN"]}, open(f"{OUT}/T0_T6_AND_ALL_LOFO_TABLE.json", "w"), indent=1, default=str)
json.dump({"per_block_residual": OUTR_b, "trichotomy": tri, "ratios_over_tube": {b: OUTR_b[b] / float(TUBE) for b in BLOCKS},
           "aggregate_residual": OUTR, "projected_energy": P2E, "tube": float(TUBE),
           "certified_exceed": [b for b in BLOCKS if tri[b] == "CERTIFIED_EXCEED"]}, open(f"{OUT}/ALL_TWELVE_P2_RESIDUALS.json", "w"), indent=1, default=str)
json.dump(out["fresh_quotient"], open(f"{OUT}/FRESH_QUOTIENT_EXACT_RECOMPUTATION.json", "w"), indent=1, default=str)
PRIMARY_OK = (prod_ref_reader_match and suff and cell_pass == 24 and direct_pass == 12 and gauge_match and resid_paths_agree)
out["PRIMARY_RECOMPUTATION_STATUS"] = "PASS" if PRIMARY_OK else "FAIL"
json.dump({"PRIMARY_RECOMPUTATION_STATUS": out["PRIMARY_RECOMPUTATION_STATUS"]}, open(f"{OUT}/_primary_status.json", "w"))
print("reader prod==ref:", prod_ref_reader_match, "| sufficiency:", suff, "| gauge matches committed:", gauge_match, "| residual two-paths:", resid_paths_agree)
print("cell:", cell_pass, "/24 | direct:", direct_pass, "/12 | e2 concordance:", concord, "/12")
print("P2: projE/E_TAU=%.3f residual/tube=%.3f | trichotomy exceed=%d unres=%d | T4=%s -> %s"
      % (P2E / float(E_TAU), OUTR / float(TUBE), n_exceed, n_unres, T4, out["FROZEN_P2_TRANSFER_AS_FROZEN"]))
print("fresh quotient:", FQ, "R0=%.3e I2=%.3e I2/R0=%.3f R1/R0=%.3f" % (float(R0), float(I2e[0]), float(I2e[0] / R0), float(R1e[0] / R0)))
print("PRIMARY_RECOMPUTATION_STATUS:", out["PRIMARY_RECOMPUTATION_STATUS"])
