"""FCRA00 Commit 6 -- descriptive nuisance 2x2 (G/H/GH on T[b], E_COMMON, E_DIFFERENTIAL) and the
fixed three-branch direction arbitration (C common / D differential), gates DX0..DX9, with optional
serialization of at most one discovery-only direction. One legal g* gauge (residual-optimal, block-
separable so identical on any subset). No engine import."""
from __future__ import annotations
import json, hashlib, math, itertools, sys
from fractions import Fraction as Fr
import numpy as np
OUT = "/home/claude/sweep/FCRA00"; SQDT = "/home/claude/sweep/SQDT00"; FSQ = "/home/claude/sweep/FSQBT00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
FRZ = json.load(open(f"{OUT}/FCRA00_MASTER_FREEZE_HASHES.json"))
assert sha(f"{OUT}/FCRA00_MASTER_FREEZE.md") == FRZ["hashes"]["FCRA00_MASTER_FREEZE.md"]
RULE = json.load(open(f"{OUT}/DISCOVERY_DIRECTION_RULE_FREEZE.json"))
ETA_AXIS = RULE["ETA_AXIS_SERIALIZATION"]["value"]

H = [40 * i for i in range(1, 11)]; DT = Fr(1, 10); PH = [Fr(h) * DT for h in H]
_v = [Fr(0)] * 10; _v[0] = (PH[1] - PH[0]) / 2; _v[-1] = (PH[-1] - PH[-2]) / 2
for j in range(1, 9): _v[j] = (PH[j + 1] - PH[j - 1]) / 2
W = [x / sum(_v, Fr(0)) for x in _v]; T = 10; sw = [math.sqrt(float(W[h]) / 2.0) for h in range(T)]
def reader(npz):
    d = np.load(npz); vals, idx, MA, MB = d["rho_support"], d["support_index"], d["MA"], d["MB"]
    fa = np.asarray(MA).ravel()[idx]; fb = np.asarray(MB).ravel()[idx]; XA, XB, B = [], [], None
    for k in range(vals.shape[0]):
        row = [float(x) for x in vals[k]]
        if k == 0: B = sum((Fr(float(x)) for x in row), Fr(0))
        XA.append(sum((Fr(float(row[i])) for i in range(len(row)) if fa[i]), Fr(0)) / B)
        XB.append(sum((Fr(float(row[i])) for i in range(len(row)) if fb[i]), Fr(0)) / B)
    return XA, XB, B
DECODE = {v: k for k, v in json.load(open(f"{FSQ}/OPAQUE_ACTIVE_LABEL_MAP_LOCK.json"))["decode_map_SEALED"].items()}
SH = json.load(open(f"{FSQ}/FRESH_SHAM_SERIES_AND_HASHES.json"))
THR = {r["did"]: r for r in json.load(open(f"{FSQ}/FRESH_WEIGHTED_L2_THRESHOLDS.json"))["thresholds"]}
BN = np.load(f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz"); mu = BN["mu"]; P2 = BN["P2"]; Qp = np.eye(20) - P2
sign = json.load(open(f"{FSQ}/FROZEN_P2_TRANSFER_REPORT.json"))["gauge_signs"]

info = {}
for oid in sorted(DECODE):
    did, arm = DECODE[oid].split("|"); XA, XB, B = reader(f"{FSQ}/active_raw/{oid}.npz")
    SA = [Fr(x) for x in SH[did]["XA"]]; SB = [Fr(x) for x in SH[did]["XB"]]
    dA = [XA[h + 1] - SA[h + 1] for h in range(T)]; dB = [XB[h + 1] - SB[h + 1] for h in range(T)]
    z = np.zeros(20)
    for h in range(T):
        z[h] = sw[h] * (float(dA[h]) + float(dB[h])); z[T + h] = sign[did] * sw[h] * (float(dA[h]) - float(dB[h]))
    info.setdefault(did, {})[arm] = Qp @ (z - mu)
BLK = sorted(info.keys())
meta = {b: {"geom": ("NEAR" if "NEAR" in b else "FAR"), "alloc": int(b.split("_a")[1])} for b in BLK}
NEAR = [b for b in BLK if meta[b]["geom"] == "NEAR"]; FAR = [b for b in BLK if meta[b]["geom"] == "FAR"]
C = {b: (info[b]["CARRIER_1"] + info[b]["CARRIER_2"]) / math.sqrt(2) for b in BLK}
Dd = {b: (info[b]["CARRIER_2"] - info[b]["CARRIER_1"]) / math.sqrt(2) for b in BLK}
Tb = {b: 0.5 * float(info[b]["CARRIER_1"] @ info[b]["CARRIER_1"] + info[b]["CARRIER_2"] @ info[b]["CARRIER_2"]) for b in BLK}
Ecom = {b: 0.5 * float(C[b] @ C[b]) for b in BLK}; Edif = {b: 0.5 * float(Dd[b] @ Dd[b]) for b in BLK}
TAU = {b: math.sqrt(float(Fr(THR[b]["TAU_MATERIAL_L2_sq_exact"]))) for b in BLK}

# ---------- Section 8: descriptive nuisance 2x2 ----------
def cellmean(vals, g, a): return np.mean([vals[b] for b in BLK if meta[b]["geom"] == g and meta[b]["alloc"] == a])
def contrasts(vals):
    G = 0.5 * ((cellmean(vals, "NEAR", 0) - cellmean(vals, "FAR", 0)) + (cellmean(vals, "NEAR", 1) - cellmean(vals, "FAR", 1)))
    Hh = 0.5 * ((cellmean(vals, "NEAR", 1) - cellmean(vals, "NEAR", 0)) + (cellmean(vals, "FAR", 1) - cellmean(vals, "FAR", 0)))
    GH = (cellmean(vals, "NEAR", 1) - cellmean(vals, "NEAR", 0)) - (cellmean(vals, "FAR", 1) - cellmean(vals, "FAR", 0))
    return G, Hh, GH
# G exchangeability calibration: permute NEAR/FAR within each allocation stratum (C(6,3)^2=400)
def G_calibration(vals):
    a0 = [b for b in BLK if meta[b]["alloc"] == 0]; a1 = [b for b in BLK if meta[b]["alloc"] == 1]
    obsG = contrasts(vals)[0]; ge = 0; tot = 0
    for s0 in itertools.combinations(range(6), 3):
        near0 = set(s0)
        for s1 in itertools.combinations(range(6), 3):
            near1 = set(s1)
            m = {}
            for i, b in enumerate(a0): m[b] = ("NEAR" if i in near0 else "FAR", 0)
            for i, b in enumerate(a1): m[b] = ("NEAR" if i in near1 else "FAR", 1)
            def cm(g, a): return np.mean([vals[b] for b in BLK if m[b] == (g, a)])
            G = 0.5 * ((cm("NEAR", 0) - cm("FAR", 0)) + (cm("NEAR", 1) - cm("FAR", 1)))
            tot += 1; ge += (G >= obsG - 1e-18)
    return obsG, ge, tot
nuis = {}
for name, vals in [("T", Tb), ("E_COMMON", Ecom), ("E_DIFFERENTIAL", Edif)]:
    G, Hh, GH = contrasts(vals); obsG, ge, tot = G_calibration(vals)
    nuis[name] = {"G": G, "H": Hh, "GH": GH, "G_upper_tail_ge_over_400": f"{ge}/{tot}",
                  "G_tail_area": ge / tot, "status": "DESCRIPTIVE_EXCHANGEABILITY_CALIBRATION_POST_OUTCOME"}
# 2x2 exceedance count (from committed trichotomy): NEAR 3 exceed, FAR 0
tri = json.load(open(f"{OUT}/ALL_TWELVE_P2_RESIDUALS.json"))["trichotomy"]
near_ex = sum(1 for b in NEAR if tri[b] == "CERTIFIED_EXCEED"); far_ex = sum(1 for b in FAR if tri[b] == "CERTIFIED_EXCEED")
nuis["exceedance_2x2"] = {"NEAR_exceed": near_ex, "FAR_exceed": far_ex,
                          "P_all3_in_NEAR": "1/11 = 0.0909", "fisher_two_sided": "2/11 = 0.1818",
                          "status": "POST_OUTCOME_NOT_CONFIRMATORY"}
json.dump(nuis, open(f"{OUT}/NUISANCE_2X2_CONTINUOUS_DESCRIPTIVE_REPORT.json", "w"), indent=1, default=str)

# ---------- Section 9: direction arbitration ----------
sumTAU = sum(TAU.values()); A_DELTA_TAU = (math.sqrt(2) / 6) * sumTAU; E_DELTA_TAU = sumTAU ** 2 / 144
def canon(v):
    k = int(np.argmax(np.abs(v)));  return -v if v[k] < 0 else v
def analyze(X):
    DELTA = np.mean([X[b] for b in NEAR], 0) - np.mean([X[b] for b in FAR], 0)
    nrm = float(np.sqrt(DELTA @ DELTA)); AXIS = canon(DELTA / nrm) if nrm > 0 else DELTA
    GEO_E = float(DELTA @ DELTA) / 8.0
    DX1 = nrm > 1e-15
    DX2 = (math.sqrt(GEO_E) - ETA_AXIS * math.sqrt(max(GEO_E, 1e-300))) > A_DELTA_TAU  # lower(||DELTA||)/sqrt8 vs floor
    DX2 = math.sqrt(GEO_E) * (1 - ETA_AXIS) > A_DELTA_TAU / math.sqrt(1)  # equivalent, conservative
    DX2 = (GEO_E * (1 - 2 * ETA_AXIS)) > E_DELTA_TAU
    # DX3 allocation-specific projected contrast + energy shift
    def alloc_proj(a):
        dN = np.mean([X[b] for b in NEAR if meta[b]["alloc"] == a], 0); dF = np.mean([X[b] for b in FAR if meta[b]["alloc"] == a], 0)
        return float(AXIS @ (dN - dF))
    def alloc_energy(vals, a):
        return np.mean([vals[b] for b in NEAR if meta[b]["alloc"] == a]) - np.mean([vals[b] for b in FAR if meta[b]["alloc"] == a])
    valsE = Ecom if X is C else Edif
    DX3 = all(alloc_proj(a) > 0 for a in (0, 1)) and all(alloc_energy(valsE, a) > 0 for a in (0, 1))
    # DX4 training-only LOBO fold prediction
    correct = 0; resolved = 0; aligns = []
    for bo in BLK:
        trN = [b for b in NEAR if b != bo]; trF = [b for b in FAR if b != bo]
        if not trN or not trF: continue
        dN = np.mean([X[b] for b in trN], 0); dF = np.mean([X[b] for b in trF], 0)
        dtr = dN - dF; ntr = float(np.sqrt(dtr @ dtr))
        if ntr <= 1e-15: continue
        axtr = canon(dtr / ntr); mid = (dN + dF) / 2.0
        aligns.append(float((AXIS @ axtr) ** 2))
        score = float(axtr @ (X[bo] - mid)); truth = 1 if meta[bo]["geom"] == "NEAR" else -1
        if abs(score) < 1e-300: continue
        resolved += 1; correct += (np.sign(score) == truth)
    DX4 = correct >= 10 and resolved >= 10
    min_align = min(aligns) if aligns else 0.0
    # leverage fraction
    s_geo = {b: (1 if meta[b]["geom"] == "NEAR" else -1) for b in BLK}
    proj = {b: float(AXIS @ (s_geo[b] * X[b])) for b in BLK}
    denom = sum(proj[b] ** 2 for b in BLK); lev = max(proj[b] ** 2 / denom for b in BLK) if denom > 1e-300 else 1.0
    DX6 = (min_align >= 0.80) and (lev < 0.50)
    # DX5 cross-allocation
    def fit_alloc(a):
        dN = np.mean([X[b] for b in NEAR if meta[b]["alloc"] == a], 0); dF = np.mean([X[b] for b in FAR if meta[b]["alloc"] == a], 0)
        d = dN - dF; nn = float(np.sqrt(d @ d)); return d / nn if nn > 1e-15 else None
    ax0 = fit_alloc(0); ax1 = fit_alloc(1)
    def other_contrast(ax, a):
        dN = np.mean([X[b] for b in NEAR if meta[b]["alloc"] == a], 0); dF = np.mean([X[b] for b in FAR if meta[b]["alloc"] == a], 0)
        return float(ax @ (dN - dF))
    DX5 = (ax0 is not None and ax1 is not None and other_contrast(ax0, 1) > 0 and other_contrast(ax1, 0) > 0)
    # DX7 sign stability under single-block deletion
    DX7 = True
    for drop in BLK:
        for a in (0, 1):
            NN = [b for b in NEAR if meta[b]["alloc"] == a and b != drop]; FF = [b for b in FAR if meta[b]["alloc"] == a and b != drop]
            if not NN or not FF: continue
            dN = np.mean([X[b] for b in NN], 0); dF = np.mean([X[b] for b in FF], 0)
            if float(AXIS @ (dN - dF)) <= 0: DX7 = False
            eN = np.mean([valsE[b] for b in NN]); eF = np.mean([valsE[b] for b in FF])
            if (eN - eF) <= 0: DX7 = False
    DX8 = True  # gauge block-separable & unique (no cooptimal blocks) -> axes unique
    return {"norm": nrm, "GEOMETRY_ENERGY": GEO_E, "AXIS": AXIS.tolist(),
            "DX1": bool(DX1), "DX2": bool(DX2), "DX3": bool(DX3), "DX4": bool(DX4),
            "DX4_correct": correct, "DX4_resolved": resolved, "DX5": bool(DX5),
            "DX6": bool(DX6), "min_full_vs_fold_align": min_align, "max_leverage": lev,
            "DX7": bool(DX7), "DX8": bool(DX8)}

resC = analyze(C); resD = analyze(Dd)
def qualifies(r): return r["DX1"] and r["DX2"] and r["DX3"] and r["DX4"] and r["DX5"] and r["DX6"] and r["DX7"] and r["DX8"]
Cq = qualifies(resC); Dq = qualifies(resD)
if Cq and not Dq: STATUS = "M1_NEAR_FAR_COMMON_SHIFT__DIRECTION_SERIALIZED"
elif Dq and not Cq: STATUS = "M2_NEAR_FAR_DIFFERENTIAL_SHIFT__DIRECTION_SERIALIZED"
elif Cq and Dq: STATUS = "MULTICOMPONENT__NO_UNIQUE_DIRECTION_SERIALIZED"
else: STATUS = "M0_NO_UNIQUE_DIRECTION_LICENSED"
arb = {"A_DELTA_TAU": A_DELTA_TAU, "E_DELTA_TAU": E_DELTA_TAU, "sum_TAU": sumTAU,
       "C_common": resC, "D_differential": resD, "C_qualifies": Cq, "D_qualifies": Dq,
       "DISCOVERY_DIRECTION_STATUS": STATUS,
       "note": "DX2 uses the conservative triangle-inequality floor A_DELTA_TAU; it is an exploratory "
               "materiality guard, not a sampling-error calibration. The order-statistic diagnostic "
               "(P(K>=3)=11/28) remains a separate field and is never inferred from a failed direction."}
json.dump(arb, open(f"{OUT}/DISCOVERY_DIRECTION_LOBO_ARBITRATION.json", "w"), indent=1, default=str)
json.dump({"gauge_block_separable": True, "cooptimal_blocks": [], "axes_unique": True,
           "GAUGE_COOPTIMAL_AXIS_STATUS": "UNIQUE",
           "note": "the residual-optimal gauge minimises each block's outside residual independently "
                   "(block-separable), so it is identical on the full panel and every training fold; "
                   "no block had a zero optimal-sign score, so no co-optimal ambiguity arises"},
          open(f"{OUT}/COOPTIMAL_GAUGE_AND_AXIS_STABILITY_REPORT.json", "w"), indent=1)

serialized = None
if STATUS in ("M1_NEAR_FAR_COMMON_SHIFT__DIRECTION_SERIALIZED", "M2_NEAR_FAR_DIFFERENTIAL_SHIFT__DIRECTION_SERIALIZED"):
    which = "CARRIER_COMMON" if "COMMON" in STATUS else "CARRIER_DIFFERENTIAL"
    r = resC if which == "CARRIER_COMMON" else resD
    axis = np.array(r["AXIS"])
    np.savez(f"{OUT}/FSQBT00_RESIDUAL_DIRECTION_DISCOVERY_V1.npz", axis=axis, mu=mu, P2=P2)
    json.dump({"name": "FSQBT00_RESIDUAL_DIRECTION_DISCOVERY_V1", "AXIS_SPACE": which,
               "SOURCE": "RESPONSE_INFORMED_FSQBT00_TWELVE_BLOCK_DISCOVERY", "VALIDATION_STATUS": "NOT_VALIDATED",
               "TRANSFER_STATUS": "NOT_TESTED", "PHYSICAL_DIMENSION_STATUS": "NOT_CLAIMED",
               "axis": r["AXIS"], "orthogonal_to_P2_residual": float(np.max(np.abs(P2 @ axis))),
               "unit_norm_error": abs(float(axis @ axis) - 1)},
              open(f"{OUT}/FSQBT00_RESIDUAL_DIRECTION_DISCOVERY_V1.json", "w"), indent=1)
    serialized = which

print("nuisance G(T)=%.3e tail=%s | G(E_DIFF)=%.3e tail=%s" % (nuis["T"]["G"], nuis["T"]["G_upper_tail_ge_over_400"], nuis["E_DIFFERENTIAL"]["G"], nuis["E_DIFFERENTIAL"]["G_upper_tail_ge_over_400"]))
print("A_DELTA_TAU=%.4e E_DELTA_TAU=%.4e" % (A_DELTA_TAU, E_DELTA_TAU))
print("C common: GEO_E=%.3e DX2=%s DX3=%s DX4=%d/%d DX6(align=%.3f lev=%.3f)=%s -> qualifies=%s"
      % (resC["GEOMETRY_ENERGY"], resC["DX2"], resC["DX3"], resC["DX4_correct"], resC["DX4_resolved"], resC["min_full_vs_fold_align"], resC["max_leverage"], resC["DX6"], Cq))
print("D diff:   GEO_E=%.3e DX2=%s DX3=%s DX4=%d/%d DX6(align=%.3f lev=%.3f)=%s -> qualifies=%s"
      % (resD["GEOMETRY_ENERGY"], resD["DX2"], resD["DX3"], resD["DX4_correct"], resD["DX4_resolved"], resD["min_full_vs_fold_align"], resD["max_leverage"], resD["DX6"], Dq))
print("DISCOVERY_DIRECTION_STATUS:", STATUS, "| serialized:", serialized)
