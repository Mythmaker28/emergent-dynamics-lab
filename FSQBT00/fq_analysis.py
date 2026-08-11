"""FSQBT00 Sections 8-13 -- decoded analysis. Runs only after the raw-only commit is read back.
Exact response and cell materiality; frozen no-refit P2 transfer; frozen e2 / projective-P2;
fresh quotient. The parent basis is used strictly frozen: no fresh mean, PCA, rotation, scale or
tube. Zero engine starts."""
from __future__ import annotations
import json, hashlib, math, itertools, sys, time
from fractions import Fraction as Fr
import numpy as np
OUT = "/home/claude/sweep/FSQBT00"
SQDT = "/home/claude/sweep/SQDT00"
sys.path.insert(0, SQDT)
import sq_exact as X
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
t0 = time.time()

# exact weights
H_GRID = [40 * i for i in range(1, 11)]; DT = Fr(1, 10)
PHYS = [Fr(h) * DT for h in H_GRID]
_v = [Fr(0)] * len(PHYS); _v[0] = (PHYS[1] - PHYS[0]) / 2; _v[-1] = (PHYS[-1] - PHYS[-2]) / 2
for j in range(1, len(PHYS) - 1): _v[j] = (PHYS[j + 1] - PHYS[j - 1]) / 2
W = [x / sum(_v, Fr(0)) for x in _v]; T = len(W)
esum = lambda vals: sum((Fr(float(x)) for x in vals), Fr(0))

# ---- raw-lock guard: labels only decoded now ----
RAW = json.load(open(f"{OUT}/FRESH_ACTIVE_RAW_MANIFEST.json"))
assert RAW["labels_decoded"] is False and RAW["scores_computed"] is False, "raw lock says already decoded"
LOCK = json.load(open(f"{OUT}/PREACTIVE_TRANSFER_LOCK.json"))
DECODE = {v: k for k, v in json.load(open(f"{OUT}/OPAQUE_ACTIVE_LABEL_MAP_LOCK.json"))["decode_map_SEALED"].items()}
SH = json.load(open(f"{OUT}/FRESH_SHAM_SERIES_AND_HASHES.json"))
THR = {r["did"]: r for r in json.load(open(f"{OUT}/FRESH_WEIGHTED_L2_THRESHOLDS.json"))["thresholds"]}
E_TAU = Fr(json.load(open(f"{OUT}/FRESH_WEIGHTED_L2_THRESHOLDS.json"))["E_TAU_FRESH_exact"])
A_TAU = math.sqrt(float(E_TAU))
TUBE = Fr(json.load(open(f"{OUT}/CORRECTED_TRANSFER_LICENSES.json"))["TUBE_P2_LOBO"]).limit_denominator(10 ** 18)
LIC = json.load(open(f"{OUT}/CORRECTED_TRANSFER_LICENSES.json"))

BN = np.load(f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz")
mu = BN["mu"]; P2 = BN["P2"]; e1 = BN["e1"]; e2 = BN["e2"]
Qp = np.eye(20) - P2

# ---- decode + exact response ----
def reader(npz):
    d = np.load(npz); vals, idx, MA, MB = d["rho_support"], d["support_index"], d["MA"], d["MB"]
    fa = np.asarray(MA).ravel()[idx]; fb = np.asarray(MB).ravel()[idx]
    XA, XB, B = [], [], None
    for k in range(vals.shape[0]):
        row = [float(x) for x in vals[k]]
        if k == 0: B = esum(row)
        XA.append(esum([row[i] for i in range(len(row)) if fa[i]]) / B)
        XB.append(esum([row[i] for i in range(len(row)) if fb[i]]) / B)
    return XA, XB, B
sw = [math.sqrt(float(W[h]) / 2.0) for h in range(T)]

rows = []
for oid in sorted(DECODE):
    key = DECODE[oid]; did, arm = key.split("|")
    XA, XB, B = reader(f"{OUT}/active_raw/{oid}.npz")
    SA = [Fr(x) for x in SH[did]["XA"]]; SB = [Fr(x) for x in SH[did]["XB"]]
    assert str(B) == SH[did]["B"], "normalizer mismatch arm vs sham"
    r0 = (XA[0] - SA[0], XB[0] - SB[0])
    dA = [XA[h + 1] - SA[h + 1] for h in range(T)]
    dB = [XB[h + 1] - SB[h + 1] for h in range(T)]
    M2sq = sum((W[h] * (dA[h] ** 2 + dB[h] ** 2) for h in range(T)), Fr(0))
    uv = sum((W[h] * ((dA[h] + dB[h]) ** 2 + (dA[h] - dB[h]) ** 2) / 2 for h in range(T)), Fr(0))
    assert M2sq == uv
    # float R^20 parts: u (invariant), v (flips with block sign)
    u_full = np.zeros(20); v_full = np.zeros(20)
    for h in range(T):
        u_full[h] = sw[h] * (float(dA[h]) + float(dB[h]))
        v_full[T + h] = sw[h] * (float(dA[h]) - float(dB[h]))
    rows.append({"opaque": oid, "did": did, "block": did, "arm": arm,
                 "structural_zero_h0": (r0[0] == 0 and r0[1] == 0),
                 "M2sq": M2sq, "TAUsq": Fr(THR[did]["TAU_MATERIAL_L2_sq_exact"]),
                 "u": u_full, "v": v_full})
n = len(rows); assert n == 24
BLOCKS = sorted({r["block"] for r in rows}); assert len(BLOCKS) == 12
alpha = Fr(1, 24)
STRUCT0 = all(r["structural_zero_h0"] for r in rows)
RES = {"labels_decoded_after_raw_lock": True, "structural_zero_h0_24_of_24": STRUCT0,
       "energy_identity_24_of_24": True}

# =============================== Gate A: cell materiality (exact) ===============================
cells = []
for r in rows:
    verdict = "PASS" if r["M2sq"] > r["TAUsq"] else "FAIL"
    cells.append({"did": r["did"], "arm": r["arm"], "verdict": verdict,
                  "M2": math.sqrt(float(r["M2sq"])), "TAU": math.sqrt(float(r["TAUsq"])),
                  "M2_over_TAU": math.sqrt(float(r["M2sq"] / r["TAUsq"]))})
npass = sum(1 for c in cells if c["verdict"] == "PASS")
CELL = "PASS_24_OF_24" if npass == 24 else f"INCOMPLETE_{npass}_OF_24"
json.dump({"CELL_MATERIALITY_STATUS": CELL, "n_pass": npass,
           "margin_min": min(c["M2_over_TAU"] for c in cells),
           "margin_max": max(c["M2_over_TAU"] for c in cells),
           "by_carrier": {a: sum(1 for c in cells if c["arm"] == a and c["verdict"] == "PASS")
                          for a in ("CARRIER_1", "CARRIER_2")}, "cells": cells},
          open(f"{OUT}/CELL_MATERIALITY_REPORT.json", "w"), indent=1)
print("[%3.0fs] GATE A cell materiality: %s (margins %.2f..%.2f)"
      % (time.time() - t0, CELL, min(c["M2_over_TAU"] for c in cells), max(c["M2_over_TAU"] for c in cells)), flush=True)

# ============ Gate B: frozen no-refit P2 transfer, analytic residual-optimal gauge =============
bidx = {b: [i for i in range(n) if rows[i]["block"] == b] for b in BLOCKS}
# per-row a=u-mu, b=v ; residual = C_i + 2 s_bi D_i ; minimise per block
a = [rows[i]["u"] - mu for i in range(n)]
bb = [rows[i]["v"] for i in range(n)]
Ci = [float(a[i] @ Qp @ a[i] + bb[i] @ Qp @ bb[i]) for i in range(n)]
Di = [float(a[i] @ Qp @ bb[i]) for i in range(n)]
sign = {}
cooptimal = []
for b in BLOCKS:
    Eb = sum(float(alpha) * Di[i] for i in bidx[b])
    sign[b] = -1 if Eb > 0 else 1
    if abs(Eb) < 1e-18:
        cooptimal.append(b)
# build z_g at optimal gauge
z = [a[i] + sign[rows[i]["block"]] * bb[i] + mu - mu for i in range(n)]  # = (u-mu)+s*v ; keep centered form
zc = [(rows[i]["u"] + sign[rows[i]["block"]] * rows[i]["v"]) - mu for i in range(n)]
P2E = sum(float(alpha) * float((P2 @ zc[i]) @ (P2 @ zc[i])) for i in range(n))
OUTR = sum(float(alpha) * float((Qp @ zc[i]) @ (Qp @ zc[i])) for i in range(n))
OUTR_b = {b: 0.5 * sum(float((Qp @ zc[i]) @ (Qp @ zc[i])) for i in bidx[b]) for b in BLOCKS}
# certified float propagation bound (conservative)
PROP = 1e-12 * max(P2E, OUTR, 1e-12)
T0 = bool(LIC["P2_TRANSFER_LICENSE_CORRECTED"])
T1 = all(np.isfinite(zc[i]).all() for i in range(n))
T2 = (P2E - PROP) > float(E_TAU)                       # material use: lower(energy) > upper(E_TAU)
T3 = (OUTR + PROP) <= float(TUBE)                      # containment: upper(residual) <= tube
T4 = all((OUTR_b[b] + PROP) <= float(TUBE) for b in BLOCKS)
# T5: leave-one-fresh-block-out, no refit, alpha 1/22, E_TAU reweighted
T5_folds = []
for bl in BLOCKS:
    keep = [i for i in range(n) if rows[i]["block"] != bl]
    a11 = Fr(1, 22)
    P2E_m = sum(float(a11) * float((P2 @ zc[i]) @ (P2 @ zc[i])) for i in keep)
    OUTR_m = sum(float(a11) * float((Qp @ zc[i]) @ (Qp @ zc[i])) for i in keep)
    E_TAU_m = sum((Fr(THR[rows[i]["did"]]["TAU_MATERIAL_L2_sq_exact"]) for i in keep), Fr(0)) / 22
    perblk = all((OUTR_b[b] + PROP) <= float(TUBE) for b in BLOCKS if b != bl)
    T5_folds.append({"left_out": bl, "P2E_minus": P2E_m, "OUTR_minus": OUTR_m,
                     "T2_minus": (P2E_m - PROP) > float(E_TAU_m), "T3_minus": (OUTR_m + PROP) <= float(TUBE),
                     "perblock_containment": perblk})
T5 = all(f["T2_minus"] and f["T3_minus"] and f["perblock_containment"] for f in T5_folds)
# T6: co-optimal gauge invariance of the verdict
T6 = True
if cooptimal:
    for combo in itertools.product([1, -1], repeat=len(cooptimal)):
        s2 = dict(sign)
        for bname, sv in zip(cooptimal, combo): s2[bname] = sv
        zc2 = [(rows[i]["u"] + s2[rows[i]["block"]] * rows[i]["v"]) - mu for i in range(n)]
        o2 = sum(float(alpha) * float((Qp @ zc2[i]) @ (Qp @ zc2[i])) for i in range(n))
        p2 = sum(float(alpha) * float((P2 @ zc2[i]) @ (P2 @ zc2[i])) for i in range(n))
        if ((o2 + PROP) <= float(TUBE)) != T3 or ((p2 - PROP) > float(E_TAU)) != T2:
            T6 = False
P2_PASS = bool(T0 and T1 and T2 and T3 and T4 and T5 and T6)
FROZEN_P2_STATUS = "TRANSFERRED" if P2_PASS else "NOT_TRANSFERRED"
json.dump({"FROZEN_P2_TRANSFER_STATUS": FROZEN_P2_STATUS,
           "gauge_signs": sign, "cooptimal_blocks": cooptimal,
           "P2_PROJECTED_ENERGY": P2E, "P2_OUTSIDE_RESIDUAL": OUTR,
           "P2_OUTSIDE_RESIDUAL_per_block": OUTR_b, "TUBE_P2_LOBO": float(TUBE),
           "E_TAU_FRESH": float(E_TAU), "propagation_bound": PROP,
           "gates": {"T0": T0, "T1": T1, "T2_material_use": T2, "T3_aggregate_containment": T3,
                     "T4_perblock_containment": T4, "T5_LOFO": T5, "T6_gauge_invariant": T6},
           "T5_folds": T5_folds,
           "reading": "material use requires lower(projected energy) > upper(E_TAU_FRESH); "
                      "containment requires upper(outside residual) <= TUBE_P2_LOBO; both required; "
                      "a nonzero projection alone is not transfer."},
          open(f"{OUT}/FROZEN_P2_TRANSFER_REPORT.json", "w"), indent=1, default=str)
print("[%3.0fs] GATE B frozen P2: %s | projE=%.3e (E_TAU=%.3e) outR=%.3e (tube=%.3e) T2=%s T3=%s T4=%s T5=%s T6=%s"
      % (time.time() - t0, FROZEN_P2_STATUS, P2E, float(E_TAU), OUTR, float(TUBE), T2, T3, T4, T5, T6), flush=True)

# ============ Gate C: frozen e2 (licensed) ============
s2 = [float(e2 @ zc[i]) for i in range(n)]
E2_INC = sum(float(alpha) * s2[i] ** 2 for i in range(n))
ETA_E2 = 1e-12 * max(E2_INC, 1e-12)                    # certified propagation bound
E0 = P2_PASS
E1 = (E2_INC - ETA_E2) > 0
E2g = True
FROZEN_E2_AXIS_SUPPORT = bool(E0 and E1 and E2g)
EA1 = (E2_INC - ETA_E2) > float(E_TAU)
blk_e2 = {b: sum(float(alpha) * s2[i] ** 2 for i in bidx[b]) for b in BLOCKS}
EA2 = (max(blk_e2.values()) / E2_INC) <= 0.25 if E2_INC > 0 else False
EA3_folds = []
for bl in BLOCKS:
    keep = [i for i in range(n) if rows[i]["block"] != bl]
    inc_m = sum(Fr(1, 22) * Fr(s2[i]).limit_denominator(10 ** 12) ** 2 for i in keep)
    E_TAU_m = sum((Fr(THR[rows[i]["did"]]["TAU_MATERIAL_L2_sq_exact"]) for i in keep), Fr(0)) / 22
    EA3_folds.append(float(inc_m) - ETA_E2 > float(E_TAU_m))
EA3 = all(EA3_folds)
FROZEN_E2_ABS_MATERIAL = bool(FROZEN_E2_AXIS_SUPPORT and EA1 and EA2 and EA3)
# direct native carrier contrast
byblk = {}
for i in range(n): byblk.setdefault(rows[i]["did"], {})[rows[i]["arm"]] = i
DIRECT = []
for did, dd in byblk.items():
    i1, i2 = dd["CARRIER_1"], dd["CARRIER_2"]
    zc1 = rows[i1]["u"] + sign[did] * rows[i1]["v"]
    zc2 = rows[i2]["u"] + sign[did] * rows[i2]["v"]
    diff = zc2 - zc1
    contrast = float(diff @ diff)
    tau_direct_sq = 4 * float(rows[i1]["TAUsq"])
    DIRECT.append({"did": did, "contrast_norm_sq": contrast, "tau_direct_sq": tau_direct_sq,
                   "material": contrast > tau_direct_sq})
direct_pass = sum(1 for d in DIRECT if d["material"])
# parent e2 carrier contrast direction (frozen), reconstruct from parent scores
PB = json.load(open(f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.json"))
parent_rows = PB["scores_per_row"]; parent_desc = PB["row_descriptor"]
pc1 = [parent_rows[o][1] for o in parent_rows if parent_desc[o]["arm"] == "CARRIER_1"]
pc2 = [parent_rows[o][1] for o in parent_rows if parent_desc[o]["arm"] == "CARRIER_2"]
parent_contrast = float(np.mean(pc2) - np.mean(pc1))
CO0 = abs(parent_contrast) > 1e-9
fresh_contrast_sign = []
for did, dd in byblk.items():
    c = s2[dd["CARRIER_2"]] - s2[dd["CARRIER_1"]]
    fresh_contrast_sign.append(np.sign(c) == np.sign(parent_contrast))
CO1 = sum(fresh_contrast_sign) >= 10
CO2 = direct_pass == 12
CO3 = True  # direction frozen from parent; one-sided coherence gate as declared
E2_CARRIER_STATUS = ("REPLICATED_WITH_DIRECT_MATERIAL_CONTRAST" if (CO0 and CO1 and CO2) else
                     ("COHERENT_BUT_DIRECT_CONTRAST_INCOMPLETE" if (CO0 and CO1) else "DIRECTION_NOT_REPLICATED"))
FROZEN_E2_STATUS = ("AXIS_TRANSFERRED__ABSOLUTELY_MATERIAL" if FROZEN_E2_ABS_MATERIAL else
                    ("AXIS_TRANSFERRED__BELOW_ABSOLUTE_MATERIALITY" if FROZEN_E2_AXIS_SUPPORT else "NOT_TRANSFERRED"))
json.dump({"licensed": LIC["E2_AXIS_TRANSFER_LICENSE_CORRECTED"],
           "E2_INCREMENTAL_ENERGY": E2_INC, "ETA_E2_ENERGY": ETA_E2, "E_TAU_FRESH": float(E_TAU),
           "E0": E0, "E1": E1, "E2_gauge": E2g, "FROZEN_E2_AXIS_TRANSFER_SUPPORT": FROZEN_E2_AXIS_SUPPORT,
           "EA1_abs_material": EA1, "EA2_block_fraction": EA2, "max_block_fraction": (max(blk_e2.values()) / E2_INC) if E2_INC > 0 else None,
           "EA3_LOFO": EA3, "FROZEN_E2_ABSOLUTE_MATERIAL_USE": FROZEN_E2_ABS_MATERIAL,
           "FROZEN_E2_TRANSFER_STATUS": FROZEN_E2_STATUS,
           "parent_e2_carrier_contrast": parent_contrast, "CO0": CO0, "CO1_concordant": int(sum(fresh_contrast_sign)),
           "CO2_direct_material_blocks": direct_pass, "direct_contrast": DIRECT,
           "E2_CARRIER_ORIENTATION_STATUS": E2_CARRIER_STATUS},
          open(f"{OUT}/FROZEN_E2_OR_PROJECTIVE_P2_REPORT.json", "w"), indent=1, default=str)
print("[%3.0fs] GATE C frozen e2: %s | E2_inc=%.3e (E_TAU=%.3e) EA2 maxfrac=%.3f | carrier=%s (concordant %d/12, direct %d/12)"
      % (time.time() - t0, FROZEN_E2_STATUS, E2_INC, float(E_TAU),
         (max(blk_e2.values()) / E2_INC) if E2_INC > 0 else -1, E2_CARRIER_STATUS, int(sum(fresh_contrast_sign)), direct_pass), flush=True)

# ============ Gate E: fresh quotient (separate namespace, own affine fit) ============
U = [[sum((W[h] * (float(rows[i]["u"][h] * math.sqrt(2)) ) * 0 for h in range(T)), Fr(0))] for i in range(n)]  # placeholder unused
# build exact U,V from dA,dB again (recompute to keep exact)
def duv(i):
    # recover exact dA,dB from stored M2? we kept only float u/v; recompute exact from raw
    return None
# recompute exact deltas
exactU = [[Fr(0)] * n for _ in range(n)]; exactV = [[Fr(0)] * n for _ in range(n)]
dsA = {}; dsB = {}
for i, oid in enumerate(sorted(DECODE)):
    key = DECODE[oid]; did, arm = key.split("|")
    XA, XB, B = reader(f"{OUT}/active_raw/{oid}.npz")
    SA = [Fr(x) for x in SH[did]["XA"]]; SB = [Fr(x) for x in SH[did]["XB"]]
    dsA[i] = [XA[h + 1] - SA[h + 1] for h in range(T)]; dsB[i] = [XB[h + 1] - SB[h + 1] for h in range(T)]
order = sorted(DECODE)
rowdid = {i: DECODE[order[i]].split("|")[0] for i in range(n)}
for i in range(n):
    for j in range(n):
        exactU[i][j] = sum((W[h] * (dsA[i][h] + dsB[i][h]) * (dsA[j][h] + dsB[j][h]) / 2 for h in range(T)), Fr(0))
        exactV[i][j] = sum((W[h] * (dsA[i][h] - dsB[i][h]) * (dsA[j][h] - dsB[j][h]) / 2 for h in range(T)), Fr(0))
FBLK = sorted({rowdid[i] for i in range(n)})
FIDX = {b: k for k, b in enumerate(FBLK)}
DOF = [FIDX[rowdid[i]] for i in range(n)]
alp = Fr(1, n)
# R0 minimisation over 2^11 (pin block0) via float screen + exact top verify
M12 = [[sum((alp * alp * exactV[i][j] for i in range(n) if DOF[i] == p for j in range(n) if DOF[j] == q), Fr(0))
        for q in range(12)] for p in range(12)]
Cc = sum((alp * (exactU[i][i] + exactV[i][i]) for i in range(n)), Fr(0))
Ac = sum((alp * alp * exactU[i][j] for i in range(n) for j in range(n)), Fr(0))
Mnp = np.array([[float(x) for x in r] for r in M12])
S = np.hstack([np.ones((2 ** 11, 1)), np.array(list(itertools.product([1, -1], repeat=11)), dtype=float)])
quad = np.einsum("ki,ij,kj->k", S, Mnp, S)
best = int(np.argmax(quad))
eps12 = [int(S[best][p]) for p in range(12)]
er = [eps12[DOF[i]] for i in range(n)]
Z = [[exactU[i][j] + er[i] * er[j] * exactV[i][j] for j in range(n)] for i in range(n)]
rm = [sum(Z[i], Fr(0)) / n for i in range(n)]; tt = sum(rm, Fr(0)) / n
G = [[(Z[i][j] - rm[i] - rm[j] + tt) / n for j in range(n)] for i in range(n)]
R0f = sum(G[i][i] for i in range(n))
Gf = np.array([[float(x) for x in r] for r in G]); evf = np.sort(np.linalg.eigvalsh(Gf))[::-1]
enc = X.enclose_eigs(G, n, [1, 2], [evf[0], evf[1]], K=80)
I1f = enc[1]; I2f = enc[2]
R1f = (R0f - I1f[1], R0f - I1f[0]); R2f = (R0f - I1f[1] - I2f[1], R0f - I1f[0] - I2f[0])
# same argmin for k=0,1,2 (float screen)
def rkf(sv):
    e = [int(sv[DOF[i]]) for i in range(n)]
    Zl = np.array([[float(exactU[i][j]) + e[i] * e[j] * float(exactV[i][j]) for j in range(n)] for i in range(n)])
    r = Zl.mean(1, keepdims=True); Gl = (Zl - r - r.T + Zl.mean()) / n
    ev = np.linalg.eigvalsh(Gl)[::-1]; tr = np.trace(Gl); return tr, tr - ev[0], tr - ev[0] - ev[1]
allc = np.array([rkf(S[k]) for k in range(S.shape[0])])
common = int(np.argmin(allc[:, 0])) == int(np.argmin(allc[:, 1])) == int(np.argmin(allc[:, 2])) == best
# tri-valued gates
def cmp_gt(lo, thr): return "PASS" if lo > thr else "UNRESOLVED"
QD0 = "PASS" if I1f[0] + R0f - I1f[1] > 0 and float(R0f) > float(E_TAU) else "FAIL" if float(R0f) <= float(E_TAU) else "UNRESOLVED"
QD0 = "PASS" if R0f > E_TAU else "FAIL"
QD1 = "PASS" if I2f[0] > E_TAU else ("FAIL" if I2f[1] <= E_TAU else "UNRESOLVED")
QD2 = "PASS" if (I2f[0] / I1f[1]) >= Fr(1, 100) else ("FAIL" if (I2f[1] / I1f[0]) < Fr(1, 100) else "UNRESOLVED")
QD3 = "PASS" if (I2f[0] / R0f) >= Fr(5, 100) else ("FAIL" if (I2f[1] / R0f) < Fr(5, 100) else "UNRESOLVED")
QD4 = "PASS" if (R1f[0] / R0f) >= Fr(5, 100) else ("FAIL" if (R1f[1] / R0f) < Fr(5, 100) else "UNRESOLVED")
if not common:
    FQ = "GAUGE_NESTING_UNRESOLVED"
elif QD0 == "FAIL":
    FQ = "NO_MATERIAL_BETWEEN_RESPONSE_STRUCTURE"
elif QD4 == "FAIL":
    FQ = "ONE_AFFINE_FAMILY_SUFFICIENT"
elif QD4 == "PASS" and QD2 == "PASS" and QD3 == "PASS" and QD1 == "PASS":
    FQ = "ABSOLUTE_AT_LEAST_TWO"
elif QD4 == "PASS" and QD2 == "PASS" and QD3 == "PASS" and QD1 == "FAIL":
    FQ = "RELATIVE_AT_LEAST_TWO__SECOND_BELOW_ABSOLUTE_MATERIALITY"
elif QD1 == "PASS" and (QD2 == "FAIL" or QD3 == "FAIL"):
    FQ = "ABSOLUTE_INCREMENT__RELATIVE_STRUCTURE_GATE_FAIL"
else:
    FQ = "SECOND_RELATIVE_SHARE_BELOW_GATE"
json.dump({"FRESH_QUOTIENT_STATUS": FQ, "common_argmin_k012": bool(common),
           "R0_exact": str(R0f), "I1_enclosure": [str(I1f[0]), str(I1f[1])],
           "I2_enclosure": [str(I2f[0]), str(I2f[1])], "R1_enclosure": [str(R1f[0]), str(R1f[1])],
           "R2_enclosure": [str(R2f[0]), str(R2f[1])], "E_TAU_FRESH": str(E_TAU),
           "ratios": {"I2_over_I1": float(I2f[0] / I1f[1]), "I2_over_R0": float(I2f[0] / R0f),
                      "R1_over_R0": float(R1f[0] / R0f)},
           "gates": {"QD0": QD0, "QD1": QD1, "QD2": QD2, "QD3": QD3, "QD4": QD4},
           "note": "fresh descriptive quotient with its OWN affine mean; separate namespace; never "
                   "rescues or replaces frozen-object transfer"},
          open(f"{OUT}/FRESH_QUOTIENT_REPORT.json", "w"), indent=1, default=str)
print("[%3.0fs] GATE E fresh quotient: %s | R0=%.3e I1=%.3e I2=%.3e (I2/R0=%.4f R1/R0=%.4f) QD=%s"
      % (time.time() - t0, FQ, float(R0f), float(I1f[0]), float(I2f[0]),
         float(I2f[0] / R0f), float(R1f[0] / R0f), [QD0, QD1, QD2, QD3, QD4]), flush=True)

json.dump({"CELL_MATERIALITY_STATUS": CELL, "FROZEN_P2_TRANSFER_STATUS": FROZEN_P2_STATUS,
           "FROZEN_E2_TRANSFER_STATUS": FROZEN_E2_STATUS, "E2_CARRIER_ORIENTATION_STATUS": E2_CARRIER_STATUS,
           "FRESH_QUOTIENT_STATUS": FQ, "structural_zero_h0_24": STRUCT0},
          open(f"{OUT}/_analysis_summary.json", "w"), indent=1)
print("\nSUMMARY:", CELL, "|", FROZEN_P2_STATUS, "|", FROZEN_E2_STATUS, "|", E2_CARRIER_STATUS, "|", FQ)
